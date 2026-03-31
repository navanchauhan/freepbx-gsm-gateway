from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import re
import threading
import time
from typing import Callable

import serial

from sms_api.mms import (
    build_mms_attachments,
    build_raw_mms_attachment,
    extract_mms_text,
    parse_mms_retrieve_conf,
)
from sms_api.pdu import ParsedInboundPdu, parse_inbound_pdu
from sms_api.phone_numbers import normalize_phone_number


HEADER_RE = re.compile(r"^\+CMGL:\s*(\d+),([^,]+),,(\d+)$")
HEX_RE = re.compile(r"^[0-9A-Fa-f]+$")
HTTP_ACTION_RE = re.compile(r"\+HTTPACTION:\s*(\d+),(\d+),(\d+)")
HTTP_READ_LEN_RE = re.compile(r"\+HTTPREAD:\s*LEN,(\d+)")
HTTP_READ_DATA_RE = re.compile(br"\+HTTPREAD:\s*DATA,(\d+)\r\n")


@dataclass(frozen=True)
class ModemStoredMessage:
    storage: str
    index: int
    status: str
    tpdu_length: int
    pdu_hex: str


class ModemError(RuntimeError):
    pass


class AtSerialClient:
    def __init__(self, port: str, *, baudrate: int = 115200, timeout_seconds: float = 0.5) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout_seconds = timeout_seconds
        self._serial: serial.Serial | None = None

    def __enter__(self) -> AtSerialClient:
        self._serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout_seconds)
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()
        self.command("ATE0", timeout_seconds=2.0)
        self.command("AT+CMGF=0", timeout_seconds=2.0)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def command(self, command: str, *, timeout_seconds: float = 5.0) -> str:
        if self._serial is None:
            raise ModemError("serial port is not open")

        self._write_command(command)
        return self._read_text_response(command=command, timeout_seconds=timeout_seconds)

    def set_storage(self, storage: str) -> None:
        self.command(f'AT+CPMS="{storage}","{storage}","{storage}"', timeout_seconds=5.0)

    def list_messages(self, *, storage: str | None = None) -> list[ModemStoredMessage]:
        if storage is not None:
            self.set_storage(storage)
        response = self.command("AT+CMGL=4", timeout_seconds=8.0)
        messages: list[ModemStoredMessage] = []
        lines = [line.strip() for line in response.replace("\r", "\n").split("\n") if line.strip()]
        current_header: tuple[int, str, int] | None = None
        active_storage = storage or "SM"

        for line in lines:
            header_match = HEADER_RE.match(line)
            if header_match:
                current_header = (
                    int(header_match.group(1)),
                    header_match.group(2),
                    int(header_match.group(3)),
                )
                continue

            if current_header and HEX_RE.match(line):
                messages.append(
                    ModemStoredMessage(
                        storage=active_storage,
                        index=current_header[0],
                        status=current_header[1],
                        tpdu_length=current_header[2],
                        pdu_hex=line.upper(),
                    )
                )
                current_header = None

        return messages

    def delete_message(self, index: int, *, storage: str | None = None) -> None:
        if storage is not None:
            self.set_storage(storage)
        self.command(f"AT+CMGD={index}", timeout_seconds=3.0)

    def fetch_http(
        self,
        *,
        url: str,
        apn: str,
        pdp_context_id: int,
        chunk_size: int,
    ) -> bytes:
        self.command("AT+CMEE=2", timeout_seconds=2.0)
        self.command(f'AT+CGDCONT={pdp_context_id},"IP","{apn}"', timeout_seconds=5.0)
        self.command(f"AT+CSOCKSETPN={pdp_context_id}", timeout_seconds=5.0)
        self.command(f"AT+CGACT=1,{pdp_context_id}", timeout_seconds=20.0)
        try:
            self.command("AT+HTTPTERM", timeout_seconds=5.0)
        except ModemError:
            pass
        self.command("AT+HTTPINIT", timeout_seconds=20.0)
        self.command(f'AT+HTTPPARA="URL","{url}"', timeout_seconds=10.0)
        _, status_code, total_length = self.http_action(method=0, timeout_seconds=60.0)
        if status_code < 200 or status_code >= 300:
            raise ModemError(f"HTTP fetch failed with status {status_code} for {url!r}")

        try:
            return self.http_read_all(total_length=total_length, chunk_size=chunk_size)
        finally:
            try:
                self.command("AT+HTTPTERM", timeout_seconds=10.0)
            except ModemError:
                pass

    def http_action(self, *, method: int, timeout_seconds: float) -> tuple[int, int, int]:
        response = self.command(f"AT+HTTPACTION={method}", timeout_seconds=10.0)
        if "+HTTPACTION:" not in response:
            response += self._read_until_pattern(
                command=f"AT+HTTPACTION={method}",
                pattern=HTTP_ACTION_RE,
                timeout_seconds=timeout_seconds,
            )

        match = HTTP_ACTION_RE.search(response)
        if match is None:
            raise ModemError(f"missing +HTTPACTION URC after AT+HTTPACTION={method}")
        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def http_read_all(self, *, total_length: int, chunk_size: int) -> bytes:
        data = bytearray()
        offset = 0
        while offset < total_length:
            current_length = min(chunk_size, total_length - offset)
            data.extend(self.http_read_chunk(offset=offset, size=current_length))
            offset = len(data)
        return bytes(data)

    def http_read_chunk(self, *, offset: int, size: int, timeout_seconds: float = 20.0) -> bytes:
        if self._serial is None:
            raise ModemError("serial port is not open")

        self._write_command(f"AT+HTTPREAD={offset},{size}")
        deadline = time.monotonic() + timeout_seconds
        buffer = bytearray()
        data_start = None
        data_length = None
        expected_end = None

        while time.monotonic() < deadline:
            chunk = self._serial.read(self._serial.in_waiting or 1)
            if chunk:
                buffer.extend(chunk)

                if data_start is None:
                    match = HTTP_READ_DATA_RE.search(buffer)
                    if match is not None:
                        data_start = match.end()
                        data_length = int(match.group(1))
                        expected_end = data_start + data_length

                if data_start is not None and data_length is not None and expected_end is not None:
                    if len(buffer) < expected_end:
                        continue
                    trailer = buffer[expected_end:]
                    if b"+HTTPREAD: 0" in trailer:
                        return bytes(buffer[data_start:expected_end])
            else:
                time.sleep(0.05)

        text = buffer.decode("utf-8", errors="replace")
        raise ModemError(f"timeout waiting for response to 'AT+HTTPREAD={offset},{size}': {text[-400:]}")

    def _write_command(self, command: str) -> None:
        if self._serial is None:
            raise ModemError("serial port is not open")
        self._serial.reset_input_buffer()
        self._serial.write((command + "\r").encode("ascii"))
        self._serial.flush()

    def _read_text_response(self, *, command: str, timeout_seconds: float) -> str:
        deadline = time.monotonic() + timeout_seconds
        chunks: list[bytes] = []
        while time.monotonic() < deadline:
            chunk = self._serial.read(self._serial.in_waiting or 1)
            if chunk:
                chunks.append(chunk)
                text = b"".join(chunks).decode("utf-8", errors="replace")
                if self._is_complete_response(text):
                    return text
            else:
                time.sleep(0.05)

        text = b"".join(chunks).decode("utf-8", errors="replace")
        raise ModemError(f"timeout waiting for response to {command!r}: {text[-200:]}")

    def _read_until_pattern(self, *, command: str, pattern: re.Pattern[str], timeout_seconds: float) -> str:
        deadline = time.monotonic() + timeout_seconds
        chunks: list[bytes] = []
        while time.monotonic() < deadline:
            chunk = self._serial.read(self._serial.in_waiting or 1)
            if chunk:
                chunks.append(chunk)
                text = b"".join(chunks).decode("utf-8", errors="replace")
                if pattern.search(text):
                    return text
            else:
                time.sleep(0.05)

        text = b"".join(chunks).decode("utf-8", errors="replace")
        raise ModemError(f"timeout waiting for URC after {command!r}: {text[-200:]}")

    @staticmethod
    def _is_complete_response(text: str) -> bool:
        lines = [line.strip() for line in text.replace("\r", "\n").split("\n") if line.strip()]
        if not lines:
            return False
        last = lines[-1]
        return last == "OK" or last == "ERROR" or last.startswith("+CME ERROR") or last.startswith("+CMS ERROR")


class ModemPoller(threading.Thread):
    def __init__(
        self,
        *,
        store,
        settings,
        on_message_created: Callable[[dict, dict], None] | None = None,
    ) -> None:
        super().__init__(name="mms-modem-poller", daemon=True)
        self.store = store
        self.settings = settings
        self.on_message_created = on_message_created
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.poll_once()
            except Exception as exc:
                print(f"[mms-poller] poll failed: {exc}")
            self._stop_event.wait(self.settings.modem_poll_interval_seconds)

    def poll_once(self) -> None:
        if not self.settings.modem_port or not self.settings.sms_from_number:
            return

        local_number = normalize_phone_number(self.settings.sms_from_number)

        with AtSerialClient(self.settings.modem_port) as client:
            for storage in ("SM", "ME"):
                try:
                    messages = client.list_messages(storage=storage)
                except ModemError as exc:
                    print(f"[mms-poller] unable to scan {storage}: {exc}")
                    continue

                for message in messages:
                    parsed = parse_inbound_pdu(message.pdu_hex)
                    if parsed.service == "SMS":
                        continue

                    if self.store.get_message_by_transport_key(parsed.transport_key) is not None:
                        client.delete_message(message.index, storage=message.storage)
                        continue

                    try:
                        remote_number = normalize_phone_number(parsed.sender)
                    except ValueError:
                        print(f"[mms-poller] skipping unsupported sender {parsed.sender!r} from {message.storage}")
                        client.delete_message(message.index, storage=message.storage)
                        continue

                    body = self._build_placeholder_body(parsed)
                    attachments: list[dict] | None = None
                    if parsed.service == "MMS" and parsed.mms_notification and parsed.mms_notification.content_location:
                        try:
                            body, attachments = self._download_mms_content(
                                client=client,
                                parsed=parsed,
                            )
                        except ModemError as exc:
                            print(f"[mms-poller] MMS fetch failed for {parsed.transport_key}: {exc}")
                            continue

                    chat_row, message_row = self.store.create_inbound_message(
                        local_number=local_number,
                        remote_number=remote_number,
                        body=body,
                        created_at=self._timestamp_for_store(parsed),
                        service=parsed.service,
                        transport_key=parsed.transport_key,
                        raw_pdu_hex=parsed.raw_pdu_hex,
                        content_location=parsed.mms_notification.content_location if parsed.mms_notification else None,
                        attachments=attachments or [],
                    )
                    if self.on_message_created is not None:
                        self.on_message_created(chat_row, message_row)
                    print(
                        "[mms-poller] captured "
                        f"{parsed.service} from {remote_number} in {message.storage}"
                    )
                    client.delete_message(message.index, storage=message.storage)

    @staticmethod
    def _build_placeholder_body(parsed: ParsedInboundPdu) -> str:
        if parsed.service == "MMS":
            return "Incoming MMS"
        return "Incoming binary SMS"

    def _download_mms_content(
        self,
        *,
        client: AtSerialClient,
        parsed: ParsedInboundPdu,
    ) -> tuple[str, list[dict]]:
        if parsed.mms_notification is None or not parsed.mms_notification.content_location:
            return self._build_placeholder_body(parsed), []

        payload = client.fetch_http(
            url=parsed.mms_notification.content_location,
            apn=self.settings.mms_http_apn,
            pdp_context_id=self.settings.mms_http_pdp_context_id,
            chunk_size=self.settings.mms_http_read_chunk_size,
        )
        retrieved = parse_mms_retrieve_conf(payload)
        if retrieved is None:
            body = "Incoming MMS (raw download attached)"
            attachments = build_raw_mms_attachment(
                payload=payload,
                media_root=self.settings.media_root,
                transport_key=parsed.transport_key,
            )
            return body, attachments

        body = extract_mms_text(retrieved) or retrieved.subject or self._build_placeholder_body(parsed)
        attachments = build_mms_attachments(
            parsed=retrieved,
            media_root=self.settings.media_root,
            transport_key=parsed.transport_key,
        )

        if not attachments:
            attachments = build_raw_mms_attachment(
                payload=payload,
                media_root=self.settings.media_root,
                transport_key=parsed.transport_key,
            )
            if body == self._build_placeholder_body(parsed):
                body = "Incoming MMS (raw download attached)"

        return body, attachments

    @staticmethod
    def _timestamp_for_store(parsed: ParsedInboundPdu) -> str:
        try:
            parsed_dt = datetime.fromisoformat(parsed.received_at.replace("Z", "+00:00"))
            return parsed_dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except ValueError:
            return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
