from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import hmac
import json
from pathlib import Path
import queue
import re
import uuid
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, Query, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from sms_api.ami import AmiClient, AmiError
from sms_api.config import Settings, load_settings
from sms_api.events import EventBroker, MessageEvent, WebhookDispatcher
from sms_api.modem import ModemPoller
from sms_api.phone_numbers import PHONE_DIGITS_RE, normalize_phone_number as normalize_phone_number_value
from sms_api.storage import SmsStore


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")
SUPPORTED_EVENT_TYPES = ("message.inbound", "message.outbound")


class ApiError(Exception):
    def __init__(self, status_code: int, message: str, *, code: int) -> None:
        self.status_code = status_code
        self.message = message
        self.code = code


class ErrorDetail(BaseModel):
    status: int
    code: int
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    trace_id: str


class TextPartRequest(BaseModel):
    type: Literal["text"]
    value: str = Field(min_length=1, max_length=1600)


class TextPartResponse(BaseModel):
    type: Literal["text"] = "text"
    value: str


class MediaPartResponse(BaseModel):
    type: Literal["image", "file"]
    url: str
    mime_type: str
    filename: str | None = None
    size_bytes: int | None = None


class MessageContentRequest(BaseModel):
    parts: list[TextPartRequest] = Field(min_length=1, max_length=1)
    idempotency_key: str | None = Field(default=None, max_length=255)
    preferred_service: Literal["SMS"] | None = None


class CreateChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")
    to: list[str] = Field(min_length=1, max_length=1)
    message: MessageContentRequest


class SendMessageToChatRequest(BaseModel):
    message: MessageContentRequest


class ChatHandle(BaseModel):
    id: str
    handle: str
    service: Literal["SMS", "MMS"] = "SMS"
    status: str | None = "active"
    joined_at: str
    left_at: str | None = None
    is_me: bool | None = None


class Chat(BaseModel):
    id: str
    display_name: str | None
    service: Literal["SMS", "MMS"] = "SMS"
    handles: list[ChatHandle]
    is_archived: bool = False
    is_group: bool = False
    created_at: str
    updated_at: str


class SentMessage(BaseModel):
    id: str
    service: Literal["SMS", "MMS"] | None = "SMS"
    preferred_service: Literal["SMS"] | None = None
    parts: list[TextPartResponse | MediaPartResponse]
    sent_at: str
    delivered_at: str | None = None
    delivery_status: Literal["pending", "queued", "sent", "delivered", "failed"]
    is_read: bool = False
    from_handle: ChatHandle | None = None


class ChatWithMessage(Chat):
    message: SentMessage


class CreateChatResult(BaseModel):
    chat: ChatWithMessage


class Message(BaseModel):
    id: str
    chat_id: str
    service: Literal["SMS", "MMS"] | None = "SMS"
    preferred_service: Literal["SMS"] | None = None
    from_handle: ChatHandle | None = None
    parts: list[TextPartResponse | MediaPartResponse] | None = None
    is_from_me: bool
    is_delivered: bool
    is_read: bool
    created_at: str
    updated_at: str
    sent_at: str | None = None
    delivered_at: str | None = None
    read_at: str | None = None


class SendMessageResponse(BaseModel):
    chat_id: str
    message: SentMessage


class ListChatsResult(BaseModel):
    chats: list[Chat]
    next_cursor: str | None = None


class GetMessagesResult(BaseModel):
    messages: list[Message]
    next_cursor: str | None = None


class PhoneNumberCapabilities(BaseModel):
    sms: bool = True
    mms: bool = False
    voice: bool = True


class PhoneNumberInfo(BaseModel):
    id: str
    phone_number: str
    device: str
    state: str | None = None
    provider_name: str | None = None
    capabilities: PhoneNumberCapabilities = Field(default_factory=PhoneNumberCapabilities)


class ListPhoneNumbersResult(BaseModel):
    phone_numbers: list[PhoneNumberInfo]


class InboundSmsResult(BaseModel):
    stored: bool = True
    chat_id: str
    message_id: str


class CreateWebhookSubscriptionRequest(BaseModel):
    target_url: AnyHttpUrl
    event_types: list[str] | None = Field(default=None, min_length=1, max_length=16)
    secret: str | None = Field(default=None, max_length=255)


class WebhookSubscription(BaseModel):
    id: str
    target_url: str
    event_types: list[str]
    is_active: bool
    created_at: str
    updated_at: str
    has_secret: bool
    last_success_at: str | None = None
    last_failure_at: str | None = None
    last_failure_status: int | None = None
    last_failure_message: str | None = None


class ListWebhooksResult(BaseModel):
    webhooks: list[WebhookSubscription]


settings: Settings = load_settings()
store = SmsStore(settings.db_path)
ami_client = AmiClient(
    host=settings.ami_host,
    port=settings.ami_port,
    username=settings.ami_username,
    password=settings.ami_password,
    timeout_seconds=settings.ami_timeout_seconds,
)
event_broker = EventBroker()
webhook_dispatcher = WebhookDispatcher(store=store)
partner_security = HTTPBearer(auto_error=False)
modem_poller = ModemPoller(store=store, settings=settings) if settings.modem_port else None
Path(settings.media_root).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="SIM7600 SMS API",
    version="1.0.0",
    description=(
        "Chat-centric HTTP API for the SIM7600 Asterisk gateway. "
        "Outbound is still SMS-only today; inbound MMS capture is handled through a sidecar modem poller."
    ),
    openapi_tags=[
        {"name": "Chats", "description": "Create and list SMS chats."},
        {"name": "Messages", "description": "Send and retrieve SMS messages."},
        {"name": "Events", "description": "Stream live message events over SSE or WebSocket."},
        {"name": "Phone Numbers", "description": "Inspect the modem-backed sending number(s)."},
        {"name": "Webhooks", "description": "Manage outbound webhook subscriptions for message events."},
        {"name": "Internal", "description": "Inbound hooks used by the dialplan."},
    ],
)
app.mount("/media", StaticFiles(directory=settings.media_root), name="media")


@app.middleware("http")
async def attach_trace_id(request: Request, call_next):
    trace_id = f"trace_{uuid.uuid4().hex}"
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.on_event("startup")
def startup() -> None:
    webhook_dispatcher.start()
    if modem_poller is not None and not modem_poller.is_alive():
        modem_poller.start()


@app.on_event("shutdown")
def shutdown() -> None:
    webhook_dispatcher.stop()
    if modem_poller is not None:
        modem_poller.stop()
        if modem_poller.is_alive():
            modem_poller.join(timeout=2.0)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", f"trace_{uuid.uuid4().hex}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                status=exc.status_code,
                code=exc.code,
                message=exc.message,
            ),
            trace_id=trace_id,
        ).model_dump(),
    )


@app.exception_handler(AmiError)
async def ami_error_handler(request: Request, exc: AmiError) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", f"trace_{uuid.uuid4().hex}")
    return JSONResponse(
        status_code=502,
        content=ErrorResponse(
            error=ErrorDetail(
                status=502,
                code=5020,
                message=str(exc) or "Asterisk AMI command failed",
            ),
            trace_id=trace_id,
        ).model_dump(),
    )


def require_partner_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(partner_security)],
) -> None:
    token = None
    if credentials is not None:
        if credentials.scheme.lower() != "bearer":
            raise ApiError(401, "Invalid bearer token.", code=4011)
        token = credentials.credentials
    verify_partner_token(token)


def verify_partner_token(token: str | None) -> None:
    if not settings.api_bearer_token:
        return

    if token is None:
        raise ApiError(401, "Missing bearer token.", code=4010)

    if not hmac.compare_digest(token, settings.api_bearer_token):
        raise ApiError(401, "Invalid bearer token.", code=4011)


def parse_bearer_token_header(authorization: str | None) -> str | None:
    if authorization is None:
        return None

    scheme, separator, value = authorization.partition(" ")
    if separator == "" or scheme.lower() != "bearer" or not value.strip():
        raise ApiError(401, "Invalid bearer token.", code=4011)
    return value.strip()


def require_stream_auth(
    authorization: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Query()] = None,
) -> None:
    token = access_token or parse_bearer_token_header(authorization)
    verify_partner_token(token)


def require_internal_auth(x_internal_token: Annotated[str | None, Header()] = None) -> None:
    if not settings.internal_token:
        return

    if x_internal_token is None:
        raise ApiError(401, "Missing internal token.", code=4012)

    if not hmac.compare_digest(x_internal_token, settings.internal_token):
        raise ApiError(401, "Invalid internal token.", code=4013)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_cursor(cursor: str | None) -> int:
    if cursor is None:
        return 0
    if not cursor.isdigit():
        raise ApiError(400, "Cursor must be a non-negative integer offset.", code=4003)
    return int(cursor)


def next_cursor(current_offset: int, limit: int, returned_count: int) -> str | None:
    if returned_count < limit:
        return None
    return str(current_offset + returned_count)


def normalize_event_types(value: str | list[str] | None, *, field_name: str) -> list[str]:
    if value is None:
        return list(SUPPORTED_EVENT_TYPES)

    raw_values = value.split(",") if isinstance(value, str) else value
    normalized: list[str] = []
    seen: set[str] = set()

    for raw_value in raw_values:
        event_type = raw_value.strip()
        if not event_type:
            continue
        if event_type not in SUPPORTED_EVENT_TYPES:
            supported = ", ".join(SUPPORTED_EVENT_TYPES)
            raise ApiError(
                400,
                f"{field_name} includes unsupported value {event_type!r}; supported values are {supported}.",
                code=40010,
            )
        if event_type not in seen:
            normalized.append(event_type)
            seen.add(event_type)

    if not normalized:
        raise ApiError(400, f"{field_name} must include at least one event type.", code=40011)

    return normalized


def normalize_phone_number(value: str, *, field_name: str) -> str:
    if not value.strip():
        raise ApiError(400, f"{field_name} is required.", code=4001)
    try:
        return normalize_phone_number_value(value)
    except ValueError as exc:
        message = str(exc)
        if field_name != "phone number":
            message = message.replace("phone number", field_name)
        raise ApiError(400, message + ".", code=4002) from exc


def build_handle(chat_row: dict, handle: str, *, is_me: bool) -> ChatHandle:
    return ChatHandle(
        id=str(uuid.uuid5(uuid.UUID(chat_row["id"]), f"{handle}:{int(is_me)}")),
        handle=handle,
        service=chat_row.get("service", "SMS"),
        joined_at=chat_row["created_at"],
        is_me=is_me,
    )


def build_chat(chat_row: dict) -> Chat:
    handles = [
        build_handle(chat_row, chat_row["from_number"], is_me=True),
        build_handle(chat_row, chat_row["to_number"], is_me=False),
    ]
    return Chat(
        id=chat_row["id"],
        display_name=chat_row["display_name"],
        service=chat_row.get("service", "SMS"),
        handles=handles,
        created_at=chat_row["created_at"],
        updated_at=chat_row["updated_at"],
    )


def build_message_parts(message_row: dict, attachments_by_message_id: dict[str, list[dict]]) -> list[TextPartResponse | MediaPartResponse]:
    parts: list[TextPartResponse | MediaPartResponse] = []
    if message_row["body"]:
        parts.append(TextPartResponse(value=message_row["body"]))

    for attachment in attachments_by_message_id.get(message_row["id"], []):
        mime_type = attachment["mime_type"]
        parts.append(
            MediaPartResponse(
                type="image" if mime_type.startswith("image/") else "file",
                url=f"/media/{attachment['relative_path']}",
                mime_type=mime_type,
                filename=attachment["filename"],
                size_bytes=attachment["size_bytes"],
            )
        )

    return parts


def build_sent_message(
    chat_row: dict,
    message_row: dict,
    attachments_by_message_id: dict[str, list[dict]] | None = None,
) -> SentMessage:
    is_from_me = message_row["direction"] == "outbound"
    sender_handle = build_handle(chat_row, message_row["sender_handle"], is_me=is_from_me)
    attachment_map = attachments_by_message_id or {}

    return SentMessage(
        id=message_row["id"],
        service=message_row.get("service", "SMS"),
        preferred_service=message_row["preferred_service"],
        parts=build_message_parts(message_row, attachment_map),
        sent_at=message_row["sent_at"] or message_row["created_at"],
        delivered_at=message_row["delivered_at"],
        delivery_status=message_row["delivery_status"],
        is_read=bool(message_row["is_read"]),
        from_handle=sender_handle,
    )


def build_message(
    chat_row: dict,
    message_row: dict,
    attachments_by_message_id: dict[str, list[dict]],
) -> Message:
    is_from_me = message_row["direction"] == "outbound"
    sender_handle = build_handle(chat_row, message_row["sender_handle"], is_me=is_from_me)

    return Message(
        id=message_row["id"],
        chat_id=message_row["chat_id"],
        service=message_row.get("service", "SMS"),
        preferred_service=message_row["preferred_service"],
        from_handle=sender_handle,
        parts=build_message_parts(message_row, attachments_by_message_id),
        is_from_me=is_from_me,
        is_delivered=bool(message_row["is_delivered"]),
        is_read=bool(message_row["is_read"]),
        created_at=message_row["created_at"],
        updated_at=message_row["updated_at"],
        sent_at=message_row["sent_at"],
        delivered_at=message_row["delivered_at"],
        read_at=message_row["read_at"],
    )


def build_webhook_subscription(subscription_row: dict) -> WebhookSubscription:
    return WebhookSubscription(
        id=subscription_row["id"],
        target_url=subscription_row["target_url"],
        event_types=subscription_row["event_types"],
        is_active=bool(subscription_row["is_active"]),
        created_at=subscription_row["created_at"],
        updated_at=subscription_row["updated_at"],
        has_secret=bool(subscription_row.get("secret")),
        last_success_at=subscription_row["last_success_at"],
        last_failure_at=subscription_row["last_failure_at"],
        last_failure_status=subscription_row["last_failure_status"],
        last_failure_message=subscription_row["last_failure_message"],
    )


def build_message_event(chat_row: dict, message_row: dict) -> MessageEvent:
    attachments_by_message_id = store.list_attachments_for_message_ids([message_row["id"]])
    direction = message_row["direction"]
    event_type = "message.outbound" if direction == "outbound" else "message.inbound"
    return MessageEvent(
        id=str(uuid.uuid4()),
        type=event_type,
        occurred_at=message_row["created_at"],
        payload={
            "chat": build_chat(chat_row).model_dump(),
            "message": build_message(chat_row, message_row, attachments_by_message_id).model_dump(),
        },
    )


def publish_message_event(chat_row: dict, message_row: dict) -> None:
    event = build_message_event(chat_row, message_row)
    event_broker.publish(event)
    webhook_dispatcher.enqueue(event)


if modem_poller is not None:
    modem_poller.on_message_created = publish_message_event


def validate_outbound_message(message: MessageContentRequest) -> tuple[str, Literal["SMS"] | None]:
    if len(message.parts) != 1 or message.parts[0].type != "text":
        raise ApiError(400, "Only a single text part is supported for SMS.", code=4004)

    body = message.parts[0].value
    if not body.strip():
        raise ApiError(400, "Message body cannot be empty.", code=4005)

    if "\r" in body or "\n" in body:
        raise ApiError(400, "Outbound SMS currently supports single-line text only.", code=4006)

    if message.preferred_service not in {None, "SMS"}:
        raise ApiError(400, "Only SMS is supported on this gateway.", code=4007)

    return body, message.preferred_service or "SMS"


def escape_cli_message(body: str) -> str:
    return body.replace("\\", "\\\\").replace('"', '\\"')


def parse_quectel_devices(raw_output: str) -> list[dict]:
    devices: list[dict] = []

    for raw_line in raw_output.splitlines():
        line = ANSI_ESCAPE_RE.sub("", raw_line).strip()
        if not line or line.startswith("ID") or line.startswith("Name") or set(line) == {"-"}:
            continue

        tokens = line.split()
        if len(tokens) < 2:
            continue

        device = tokens[0]
        if device.lower() == "command":
            continue

        number = None
        for token in reversed(tokens):
            cleaned = PHONE_DIGITS_RE.sub("", token)
            if not cleaned:
                continue
            try:
                number = normalize_phone_number(cleaned, field_name="phone number")
                break
            except ApiError:
                continue

        if number is None:
            continue

        devices.append(
            {
                "device": device,
                "phone_number": number,
                "state": tokens[2] if len(tokens) > 2 else None,
                "provider_name": tokens[6] if len(tokens) > 6 else None,
            }
        )

    return devices


def get_available_phone_numbers(*, allow_fallback: bool = True) -> list[dict]:
    try:
        output = ami_client.command("quectel show devices")
        devices = parse_quectel_devices(output)
        if devices:
            return devices
    except AmiError:
        if not allow_fallback:
            raise

    if settings.sms_from_number:
        return [
            {
                "device": settings.sms_device,
                "phone_number": normalize_phone_number(settings.sms_from_number, field_name="SMS_FROM_NUMBER"),
                "state": None,
                "provider_name": None,
            }
        ]

    return []


def assert_owned_from_number(from_number: str) -> None:
    available_numbers = get_available_phone_numbers()
    if not available_numbers:
        return

    if from_number not in {entry["phone_number"] for entry in available_numbers}:
        raise ApiError(400, f"from number {from_number} is not available on this gateway.", code=4008)


def resolve_local_number_for_device(device_name: str) -> str:
    available_numbers = get_available_phone_numbers()
    for entry in available_numbers:
        if entry["device"] == device_name:
            return entry["phone_number"]

    if len(available_numbers) == 1:
        return available_numbers[0]["phone_number"]

    if settings.sms_from_number:
        return normalize_phone_number(settings.sms_from_number, field_name="SMS_FROM_NUMBER")

    raise ApiError(502, f"Could not resolve a local phone number for device {device_name}.", code=5021)


def send_sms_via_ami(*, device_name: str, to_number: str, body: str) -> None:
    cli_command = f'quectel sms {device_name} {to_number.lstrip("+")} "{escape_cli_message(body)}"'
    output = ami_client.command(cli_command)
    lowered = output.lower()

    if "error" in lowered or "fail" in lowered:
        raise AmiError(output or "Asterisk rejected the SMS command")

    if "queued" not in lowered and "sent" not in lowered:
        raise AmiError(output or "Unexpected response from Asterisk SMS command")


def websocket_close_code_for_error(exc: ApiError) -> int:
    if exc.status_code == 401:
        return 4401
    if exc.status_code == 403:
        return 4403
    return 4400


@app.get("/healthz")
def healthz():
    try:
        phone_numbers = get_available_phone_numbers(allow_fallback=False)
        return {
            "status": "ok",
            "database": "ok",
            "ami": "ok",
            "phone_numbers": phone_numbers,
        }
    except AmiError as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "database": "ok",
                "ami": "error",
                "error": str(exc),
            },
        )


@app.get(
    "/v3/phone_numbers",
    tags=["Phone Numbers"],
    response_model=ListPhoneNumbersResult,
    dependencies=[Depends(require_partner_auth)],
)
def list_phone_numbers() -> ListPhoneNumbersResult:
    phone_numbers = [
        PhoneNumberInfo(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{entry["device"]}:{entry["phone_number"]}')),
            phone_number=entry["phone_number"],
            device=entry["device"],
            state=entry["state"],
            provider_name=entry["provider_name"],
            capabilities=PhoneNumberCapabilities(mms=bool(settings.modem_port)),
        )
        for entry in get_available_phone_numbers()
    ]

    if not phone_numbers:
        raise ApiError(502, "No modem-backed phone numbers are currently available.", code=5022)

    return ListPhoneNumbersResult(phone_numbers=phone_numbers)


@app.get(
    "/v3/chats",
    tags=["Chats"],
    response_model=ListChatsResult,
    dependencies=[Depends(require_partner_auth)],
)
def list_chats(
    from_number: Annotated[str | None, Query(alias="from")] = None,
    to_number: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: Annotated[str | None, Query()] = None,
) -> ListChatsResult:
    normalized_from = normalize_phone_number(from_number, field_name="from") if from_number else None
    normalized_to = normalize_phone_number(to_number, field_name="to") if to_number else None
    offset = parse_cursor(cursor)

    chats = store.list_chats(
        from_number=normalized_from,
        to_number=normalized_to,
        limit=limit,
        offset=offset,
    )

    return ListChatsResult(
        chats=[build_chat(chat_row) for chat_row in chats],
        next_cursor=next_cursor(offset, limit, len(chats)),
    )


@app.get(
    "/v3/chats/{chat_id}",
    tags=["Chats"],
    response_model=Chat,
    dependencies=[Depends(require_partner_auth)],
)
def get_chat(chat_id: str) -> Chat:
    chat_row = store.get_chat(chat_id)
    if chat_row is None:
        raise ApiError(404, f"Chat {chat_id} was not found.", code=4040)
    return build_chat(chat_row)


@app.get(
    "/v3/webhooks",
    tags=["Webhooks"],
    response_model=ListWebhooksResult,
    dependencies=[Depends(require_partner_auth)],
)
def list_webhooks() -> ListWebhooksResult:
    subscriptions = store.list_webhook_subscriptions()
    return ListWebhooksResult(
        webhooks=[build_webhook_subscription(subscription) for subscription in subscriptions]
    )


@app.post(
    "/v3/webhooks",
    tags=["Webhooks"],
    response_model=WebhookSubscription,
    status_code=201,
    dependencies=[Depends(require_partner_auth)],
)
def create_webhook(payload: CreateWebhookSubscriptionRequest) -> WebhookSubscription:
    created_at = utc_now()
    subscription_row = store.create_webhook_subscription(
        target_url=str(payload.target_url),
        secret=payload.secret,
        event_types=normalize_event_types(payload.event_types, field_name="event_types"),
        created_at=created_at,
    )
    return build_webhook_subscription(subscription_row)


@app.delete(
    "/v3/webhooks/{webhook_id}",
    tags=["Webhooks"],
    status_code=204,
    dependencies=[Depends(require_partner_auth)],
)
def delete_webhook(webhook_id: str) -> Response:
    if not store.delete_webhook_subscription(webhook_id):
        raise ApiError(404, f"Webhook {webhook_id} was not found.", code=4041)
    return Response(status_code=204)


@app.post(
    "/v3/chats",
    tags=["Chats"],
    response_model=CreateChatResult,
    dependencies=[Depends(require_partner_auth)],
)
def create_chat(payload: CreateChatRequest, response: Response) -> CreateChatResult:
    from_number = normalize_phone_number(payload.from_, field_name="from")
    assert_owned_from_number(from_number)

    if len(payload.to) != 1:
        raise ApiError(400, "Only one recipient is supported for SMS chats.", code=4009)

    to_number = normalize_phone_number(payload.to[0], field_name="to")
    body, preferred_service = validate_outbound_message(payload.message)

    if payload.message.idempotency_key:
        existing_message = store.get_message_by_idempotency_key(payload.message.idempotency_key)
        if existing_message is not None:
            chat_row = store.get_chat(existing_message["chat_id"])
            if chat_row is None:
                raise ApiError(409, "Idempotent message exists but its chat record is missing.", code=4091)
            if chat_row["from_number"] != from_number or chat_row["to_number"] != to_number:
                raise ApiError(409, "Idempotency key is already associated with a different chat.", code=4090)
            response.status_code = 200
            return CreateChatResult(
                chat=ChatWithMessage(
                    **build_chat(chat_row).model_dump(),
                    message=build_sent_message(chat_row, existing_message),
                )
            )

    send_sms_via_ami(device_name=settings.sms_device, to_number=to_number, body=body)

    timestamp = utc_now()
    chat_row, created = store.get_or_create_chat(
        from_number=from_number,
        to_number=to_number,
        created_at=timestamp,
    )
    message_row = store.create_outbound_message(
        chat_id=chat_row["id"],
        sender_handle=from_number,
        body=body,
        preferred_service=preferred_service,
        idempotency_key=payload.message.idempotency_key,
        created_at=timestamp,
    )
    chat_row = store.get_chat(chat_row["id"]) or chat_row
    publish_message_event(chat_row, message_row)

    response.status_code = 201 if created else 200
    return CreateChatResult(
        chat=ChatWithMessage(
            **build_chat(chat_row).model_dump(),
            message=build_sent_message(chat_row, message_row),
        )
    )


@app.get(
    "/v3/chats/{chat_id}/messages",
    tags=["Messages"],
    response_model=GetMessagesResult,
    dependencies=[Depends(require_partner_auth)],
)
def get_messages(
    chat_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query()] = None,
) -> GetMessagesResult:
    chat_row = store.get_chat(chat_id)
    if chat_row is None:
        raise ApiError(404, f"Chat {chat_id} was not found.", code=4040)

    offset = parse_cursor(cursor)
    messages = store.list_messages(chat_id=chat_id, limit=limit, offset=offset)
    attachments_by_message_id = store.list_attachments_for_message_ids([message["id"] for message in messages])

    return GetMessagesResult(
        messages=[build_message(chat_row, message_row, attachments_by_message_id) for message_row in messages],
        next_cursor=next_cursor(offset, limit, len(messages)),
    )


@app.post(
    "/v3/chats/{chat_id}/messages",
    tags=["Messages"],
    response_model=SendMessageResponse,
    status_code=202,
    dependencies=[Depends(require_partner_auth)],
)
def send_message_to_chat(
    chat_id: str,
    payload: SendMessageToChatRequest,
    response: Response,
) -> SendMessageResponse:
    chat_row = store.get_chat(chat_id)
    if chat_row is None:
        raise ApiError(404, f"Chat {chat_id} was not found.", code=4040)

    body, preferred_service = validate_outbound_message(payload.message)

    if payload.message.idempotency_key:
        existing_message = store.get_message_by_idempotency_key(payload.message.idempotency_key)
        if existing_message is not None:
            if existing_message["chat_id"] != chat_id:
                raise ApiError(409, "Idempotency key is already associated with a different chat.", code=4090)
            response.status_code = 200
            return SendMessageResponse(
                chat_id=chat_id,
                message=build_sent_message(chat_row, existing_message),
            )

    send_sms_via_ami(device_name=settings.sms_device, to_number=chat_row["to_number"], body=body)

    timestamp = utc_now()
    message_row = store.create_outbound_message(
        chat_id=chat_id,
        sender_handle=chat_row["from_number"],
        body=body,
        preferred_service=preferred_service,
        idempotency_key=payload.message.idempotency_key,
        created_at=timestamp,
    )
    chat_row = store.get_chat(chat_id) or chat_row
    publish_message_event(chat_row, message_row)

    return SendMessageResponse(
        chat_id=chat_id,
        message=build_sent_message(chat_row, message_row),
    )


@app.get(
    "/v3/events/stream",
    tags=["Events"],
    dependencies=[Depends(require_stream_auth)],
)
async def stream_events(
    events: Annotated[str | None, Query(description="Comma-separated event types to include.")] = None,
) -> StreamingResponse:
    event_types = normalize_event_types(events, field_name="events")

    async def event_generator():
        subscription_id, subscriber_queue = event_broker.subscribe(event_types=event_types)
        try:
            while True:
                try:
                    event = await asyncio.to_thread(subscriber_queue.get, True, 15.0)
                except queue.Empty:
                    yield f": keepalive {utc_now()}\n\n"
                    continue

                payload = json.dumps(event.as_dict(), separators=(",", ":"), sort_keys=True)
                yield f"id: {event.id}\nevent: {event.type}\ndata: {payload}\n\n"
        except asyncio.CancelledError:
            raise
        finally:
            event_broker.unsubscribe(subscription_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.websocket("/v3/events/ws")
async def websocket_events(websocket: WebSocket) -> None:
    try:
        event_types = normalize_event_types(websocket.query_params.get("events"), field_name="events")
        token = websocket.query_params.get("access_token") or parse_bearer_token_header(
            websocket.headers.get("authorization")
        )
        verify_partner_token(token)
    except ApiError as exc:
        await websocket.close(code=websocket_close_code_for_error(exc), reason=exc.message)
        return

    await websocket.accept()
    subscription_id, subscriber_queue = event_broker.subscribe(event_types=event_types)
    try:
        while True:
            try:
                event = await asyncio.to_thread(subscriber_queue.get, True, 15.0)
                await websocket.send_json(event.as_dict())
            except queue.Empty:
                await websocket.send_json(
                    {
                        "id": f"keepalive_{uuid.uuid4().hex}",
                        "type": "system.keepalive",
                        "occurred_at": utc_now(),
                    }
                )
    except WebSocketDisconnect:
        pass
    finally:
        event_broker.unsubscribe(subscription_id)


@app.post(
    "/internal/inbound-sms",
    tags=["Internal"],
    response_model=InboundSmsResult,
    dependencies=[Depends(require_internal_auth)],
)
def ingest_inbound_sms(
    device: Annotated[str, Query(min_length=1)] = settings.sms_device,
    from_number: Annotated[str, Query(alias="from", min_length=1)] = ...,
    body: Annotated[str, Query()] = ...,
) -> InboundSmsResult:
    remote_number = normalize_phone_number(from_number, field_name="from")
    local_number = resolve_local_number_for_device(device)
    timestamp = utc_now()

    chat_row, message_row = store.create_inbound_message(
        local_number=local_number,
        remote_number=remote_number,
        body=body,
        created_at=timestamp,
    )
    publish_message_event(chat_row, message_row)

    return InboundSmsResult(chat_id=chat_row["id"], message_id=message_row["id"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
