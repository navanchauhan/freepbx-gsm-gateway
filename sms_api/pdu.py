from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import UTC
import hashlib
from io import StringIO
from typing import Literal

from smspdudecoder.fields import SMSDeliver


WSP_CONTENT_TYPES: tuple[str, ...] = (
    "*/*",
    "text/*",
    "text/html",
    "text/plain",
    "text/x-hdml",
    "text/x-ttml",
    "text/x-vCalendar",
    "text/x-vCard",
    "text/vnd.wap.wml",
    "text/vnd.wap.wmlscript",
    "text/vnd.wap.wta-event",
    "multipart/*",
    "multipart/mixed",
    "multipart/form-data",
    "multipart/byterantes",
    "multipart/alternative",
    "application/*",
    "application/java-vm",
    "application/x-www-form-urlencoded",
    "application/x-hdmlc",
    "application/vnd.wap.wmlc",
    "application/vnd.wap.wmlscriptc",
    "application/vnd.wap.wta-eventc",
    "application/vnd.wap.uaprof",
    "application/vnd.wap.wtls-ca-certificate",
    "application/vnd.wap.wtls-user-certificate",
    "application/x-x509-ca-cert",
    "application/x-x509-user-cert",
    "image/*",
    "image/gif",
    "image/jpeg",
    "image/tiff",
    "image/png",
    "image/vnd.wap.wbmp",
    "application/vnd.wap.multipart.*",
    "application/vnd.wap.multipart.mixed",
    "application/vnd.wap.multipart.form-data",
    "application/vnd.wap.multipart.byteranges",
    "application/vnd.wap.multipart.alternative",
    "application/xml",
    "text/xml",
    "application/vnd.wap.wbxml",
    "application/x-x968-cross-cert",
    "application/x-x968-ca-cert",
    "application/x-x968-user-cert",
    "text/vnd.wap.si",
    "application/vnd.wap.sic",
    "text/vnd.wap.sl",
    "application/vnd.wap.slc",
    "text/vnd.wap.co",
    "application/vnd.wap.coc",
    "application/vnd.wap.multipart.related",
    "application/vnd.wap.sia",
    "text/vnd.wap.connectivity-xml",
    "application/vnd.wap.connectivity-wbxml",
    "application/pkcs7-mime",
    "application/vnd.wap.hashed-certificate",
    "application/vnd.wap.signed-certificate",
    "application/vnd.wap.cert-response",
    "application/xhtml+xml",
    "application/wml+xml",
    "text/css",
    "application/vnd.wap.mms-message",
    "application/vnd.wap.rollover-certificate",
    "application/vnd.wap.locc+wbxml",
    "application/vnd.wap.loc+xml",
    "application/vnd.syncml.dm+wbxml",
    "application/vnd.syncml.dm+xml",
    "application/vnd.syncml.notification",
    "application/vnd.wap.xhtml+xml",
    "application/vnd.wv.csp.cir",
    "application/vnd.oma.dd+xml",
    "application/vnd.oma.drm.message",
    "application/vnd.oma.drm.content",
    "application/vnd.oma.drm.rights+xml",
    "application/vnd.oma.drm.rights+wbxml",
    "application/vnd.wv.csp+xml",
    "application/vnd.wv.csp+wbxml",
    "application/vnd.syncml.ds.notification",
    "audio/*",
    "video/*",
    "application/vnd.oma.dd2+xml",
    "application/mikey",
)

MMS_MESSAGE_CLASS = {
    0x80: "personal",
    0x81: "advertisement",
    0x82: "informational",
    0x83: "auto",
}


@dataclass(frozen=True)
class ParsedMmsNotification:
    transaction_id: str | None
    content_location: str | None
    message_size: int | None
    message_class: str | None
    mms_version: int | None


@dataclass(frozen=True)
class ParsedInboundPdu:
    transport_key: str
    sender: str
    received_at: str
    encoding: Literal["gsm", "ucs2", "binary"]
    service: Literal["SMS", "MMS", "BINARY"]
    text_body: str
    raw_pdu_hex: str
    payload_base64: str | None
    source_port: int | None
    dest_port: int | None
    is_wap_push: bool
    mms_notification: ParsedMmsNotification | None


def parse_inbound_pdu(pdu_hex: str) -> ParsedInboundPdu:
    sms = SMSDeliver.decode(StringIO(pdu_hex))
    sender = sms["sender"]["number"]
    if sms["sender"]["toa"]["ton"] == "international":
        sender = f"+{sender}"

    received_at = sms["scts"].astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    encoding = sms["dcs"]["encoding"]
    user_data = sms["user_data"]["data"]
    header = sms["user_data"].get("header") or {}
    source_port, dest_port = extract_ports(header.get("elements") or [])

    text_body = user_data if isinstance(user_data, str) else ""
    payload_base64 = None
    if isinstance(user_data, bytes):
        payload_base64 = base64.b64encode(user_data).decode("ascii")

    transport_key = hashlib.sha256(pdu_hex.upper().encode("ascii")).hexdigest()
    wap_push = parse_wap_push(user_data, dest_port=dest_port) if isinstance(user_data, bytes) else None
    mms_notification = wap_push if wap_push and wap_push.content_location else None
    service: Literal["SMS", "MMS", "BINARY"] = "SMS"
    if mms_notification is not None:
        service = "MMS"
    elif isinstance(user_data, bytes):
        service = "BINARY"

    return ParsedInboundPdu(
        transport_key=transport_key,
        sender=sender,
        received_at=received_at,
        encoding=encoding,
        service=service,
        text_body=text_body,
        raw_pdu_hex=pdu_hex.upper(),
        payload_base64=payload_base64,
        source_port=source_port,
        dest_port=dest_port,
        is_wap_push=wap_push is not None,
        mms_notification=mms_notification,
    )


def extract_ports(elements: list[dict]) -> tuple[int | None, int | None]:
    for element in elements:
        iei = element.get("iei")
        raw = element.get("data")
        if not isinstance(raw, str):
            continue
        if iei == 0x05 and len(raw) == 8:
            return int(raw[4:8], 16), int(raw[0:4], 16)
        if iei == 0x04 and len(raw) == 4:
            return int(raw[2:4], 16), int(raw[0:2], 16)
    return None, None


def parse_wap_push(payload: bytes, *, dest_port: int | None) -> ParsedMmsNotification | None:
    if not payload or dest_port not in {2948, 9200, 9201}:
        return None

    if len(payload) < 3:
        return None

    offset = 0
    offset += 1  # transaction id
    pdu_type = payload[offset]
    offset += 1
    if pdu_type not in {0x06, 0x07}:
        return None

    try:
        headers_length, offset = read_uintvar(payload, offset)
        content_type, offset_after_ct = read_wsp_content_type(payload, offset)
    except ValueError:
        return None

    headers_end = offset + headers_length
    body = payload[headers_end:]
    if content_type != "application/vnd.wap.mms-message" or not body:
        return None

    return parse_mms_notification(body)


def parse_mms_notification(payload: bytes) -> ParsedMmsNotification | None:
    offset = 0
    message_type = None
    transaction_id = None
    content_location = None
    message_size = None
    message_class = None
    mms_version = None

    while offset < len(payload):
        field = payload[offset]
        offset += 1

        if field == 0x8C:  # X-Mms-Message-Type
            if offset >= len(payload):
                break
            message_type = payload[offset]
            offset += 1
        elif field == 0x98:  # X-Mms-Transaction-ID
            transaction_id, offset = read_text_string(payload, offset)
        elif field == 0x83:  # X-Mms-Content-Location
            content_location, offset = read_text_string(payload, offset)
        elif field == 0x8E:  # X-Mms-Message-Size
            message_size, offset = read_uintvar(payload, offset)
        elif field == 0x8A:  # X-Mms-Message-Class
            if offset >= len(payload):
                break
            token = payload[offset]
            if token in MMS_MESSAGE_CLASS:
                message_class = MMS_MESSAGE_CLASS[token]
                offset += 1
            else:
                message_class, offset = read_text_string(payload, offset)
        elif field == 0x8D:  # X-Mms-MMS-Version
            if offset >= len(payload):
                break
            mms_version = payload[offset] & 0x7F
            offset += 1
        elif field == 0x89:  # From
            _, offset = skip_length_quoted_value(payload, offset)
        elif field == 0x88:  # Expiry
            _, offset = skip_length_quoted_value(payload, offset)
        elif field == 0x96:  # Subject
            _, offset = skip_length_quoted_value(payload, offset)
        elif field in {0x86, 0x8F, 0x90, 0x91, 0x95}:  # octet-valued fields
            offset += 1
        else:
            break

        if message_type == 0x82 and content_location:
            return ParsedMmsNotification(
                transaction_id=transaction_id,
                content_location=content_location,
                message_size=message_size,
                message_class=message_class,
                mms_version=mms_version,
            )

    if message_type != 0x82:
        return None

    return ParsedMmsNotification(
        transaction_id=transaction_id,
        content_location=content_location,
        message_size=message_size,
        message_class=message_class,
        mms_version=mms_version,
    )


def read_uintvar(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    while offset < len(data):
        current = data[offset]
        offset += 1
        value = (value << 7) | (current & 0x7F)
        if current & 0x80 == 0:
            return value, offset
    raise ValueError("unterminated uintvar")


def read_text_string(data: bytes, offset: int) -> tuple[str, int]:
    if offset >= len(data):
        return "", offset
    if data[offset] == 0x7F:
        offset += 1
    start = offset
    while offset < len(data) and data[offset] != 0x00:
        offset += 1
    text = data[start:offset].decode("utf-8", errors="replace")
    if offset < len(data) and data[offset] == 0x00:
        offset += 1
    return text, offset


def read_value_length(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError("missing value length")
    first = data[offset]
    if first <= 30:
        return first, offset + 1
    if first == 31:
        return read_uintvar(data, offset + 1)
    raise ValueError("invalid value length")


def skip_length_quoted_value(data: bytes, offset: int) -> tuple[bytes, int]:
    length, offset = read_value_length(data, offset)
    value = data[offset : offset + length]
    return value, offset + length


def read_wsp_content_type(data: bytes, offset: int) -> tuple[str, int]:
    if offset >= len(data):
        raise ValueError("missing content type")

    first = data[offset]
    if first <= 30 or first == 31:
        length, offset = read_value_length(data, offset)
        end = offset + length
        if offset >= len(data):
            raise ValueError("truncated content type")
        field = data[offset]
        if field & 0x80:
            return decode_well_known_content_type(field & 0x7F), end
        text, _ = read_text_string(data, offset)
        return text, end

    if first & 0x80:
        return decode_well_known_content_type(first & 0x7F), offset + 1

    return read_text_string(data, offset)


def decode_well_known_content_type(index: int) -> str:
    if 0 <= index < len(WSP_CONTENT_TYPES):
        return WSP_CONTENT_TYPES[index]
    return f"well-known/{index}"
