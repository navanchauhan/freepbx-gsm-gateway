from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import mimetypes
from pathlib import Path
import quopri
import re

from sms_api.pdu import decode_well_known_content_type, read_uintvar, read_value_length


TEXT_MIN = 32
TEXT_MAX = 127
QUOTE = 127
QUOTED_STRING_FLAG = 34

P_CHARSET = 0x81
P_TYPE = 0x83
P_DEP_NAME = 0x85
P_CT_MR_TYPE = 0x89
P_DEP_START = 0x8A
P_CONTENT_LOCATION = 0x8E
P_CONTENT_TYPE = 0x91
P_NAME = 0x97
P_FILENAME = 0x98
P_START = 0x99
P_CONTENT_ID = 0xC0
P_DEP_CONTENT_DISPOSITION = 0xAE
P_CONTENT_DISPOSITION = 0xC5

P_DISPOSITION_FROM_DATA = 0x80
P_DISPOSITION_ATTACHMENT = 0x81
P_DISPOSITION_INLINE = 0x82

HEADER_MESSAGE_TYPE = 0x8C
HEADER_TRANSACTION_ID = 0x98
HEADER_CONTENT_TYPE = 0x84
HEADER_SUBJECT = 0x96
HEADER_DATE = 0x85
HEADER_FROM = 0x89
HEADER_MESSAGE_ID = 0x8B

MESSAGE_TYPE_RETRIEVE_CONF = 0x84

TRANSFER_ENCODING_HEADER = "content-transfer-encoding"
SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
MIB_TO_PYTHON_ENCODING = {
    3: "ascii",
    4: "latin-1",
    106: "utf-8",
}


@dataclass(frozen=True)
class ParsedMmsPart:
    content_type: str
    data: bytes
    name: str | None = None
    filename: str | None = None
    content_id: str | None = None
    content_location: str | None = None
    charset: int | None = None


@dataclass(frozen=True)
class ParsedMmsRetrieveConf:
    content_type: str
    subject: str | None
    transaction_id: str | None
    message_id: str | None
    message_date: str | None
    parts: list[ParsedMmsPart]


def parse_mms_retrieve_conf(payload: bytes) -> ParsedMmsRetrieveConf | None:
    offset = 0
    message_type = None
    transaction_id = None
    subject = None
    message_id = None
    message_date = None
    content_type = None

    while offset < len(payload):
        field = payload[offset]
        offset += 1

        if field == HEADER_MESSAGE_TYPE:
            if offset >= len(payload):
                return None
            message_type = payload[offset]
            offset += 1
        elif field == HEADER_TRANSACTION_ID:
            transaction_id, offset = read_wap_string(payload, offset)
        elif field == HEADER_SUBJECT:
            subject, _, offset = read_encoded_string_value(payload, offset)
        elif field == HEADER_MESSAGE_ID:
            message_id, offset = read_wap_string(payload, offset)
        elif field == HEADER_DATE:
            date_value, offset = parse_integer_value(payload, offset)
            message_date = datetime.fromtimestamp(date_value, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        elif field == HEADER_FROM:
            offset = skip_length_value(payload, offset)
        elif field == HEADER_CONTENT_TYPE:
            content_type, _, offset = parse_content_type(payload, offset)
            break
        else:
            offset = skip_mms_header_value(payload, offset)

    if message_type != MESSAGE_TYPE_RETRIEVE_CONF or content_type is None:
        return None

    try:
        parts, final_offset = parse_parts(payload, offset)
    except ValueError:
        return None

    if final_offset > len(payload):
        return None

    return ParsedMmsRetrieveConf(
        content_type=content_type,
        subject=subject,
        transaction_id=transaction_id,
        message_id=message_id,
        message_date=message_date,
        parts=parts,
    )


def extract_mms_text(parsed: ParsedMmsRetrieveConf) -> str | None:
    for part in parsed.parts:
        normalized = part.content_type.lower()
        if normalized.startswith("text/plain"):
            text = decode_text_part(part)
            if text:
                return text
    if parsed.subject:
        return parsed.subject
    return None


def build_mms_attachments(
    *,
    parsed: ParsedMmsRetrieveConf,
    media_root: str,
    transport_key: str,
) -> list[dict]:
    attachments: list[dict] = []
    root = Path(media_root) / "mms" / transport_key[:16]
    root.mkdir(parents=True, exist_ok=True)

    attachment_index = 0
    for part in parsed.parts:
        normalized = part.content_type.lower()
        if normalized.startswith("text/plain") or normalized == "application/smil":
            continue

        attachment_index += 1
        filename = select_filename(part, attachment_index)
        safe_name = SAFE_FILENAME_RE.sub("_", filename).strip("._") or f"part-{attachment_index}.bin"
        destination = root / safe_name
        if destination.exists():
            destination = root / f"{attachment_index}-{safe_name}"
        destination.write_bytes(part.data)
        attachments.append(
            {
                "kind": "image" if normalized.startswith("image/") else "file",
                "mime_type": part.content_type,
                "filename": destination.name,
                "relative_path": str(Path("mms") / transport_key[:16] / destination.name),
                "size_bytes": destination.stat().st_size,
            }
        )

    return attachments


def build_raw_mms_attachment(
    *,
    payload: bytes,
    media_root: str,
    transport_key: str,
) -> list[dict]:
    root = Path(media_root) / "mms" / transport_key[:16]
    root.mkdir(parents=True, exist_ok=True)
    destination = root / "raw.mms"
    destination.write_bytes(payload)
    return [
        {
            "kind": "file",
            "mime_type": "application/vnd.wap.mms-message",
            "filename": destination.name,
            "relative_path": str(Path("mms") / transport_key[:16] / destination.name),
            "size_bytes": destination.stat().st_size,
        }
    ]


def read_wap_string(data: bytes, offset: int, *, quoted: bool = False) -> tuple[str | None, int]:
    if offset >= len(data):
        return None, offset
    if quoted:
        if data[offset] == QUOTED_STRING_FLAG:
            offset += 1
    elif data[offset] == QUOTE:
        offset += 1

    start = offset
    while offset < len(data) and data[offset] != 0:
        offset += 1

    value = data[start:offset].decode("utf-8", errors="replace") if offset >= start else ""
    if offset < len(data) and data[offset] == 0:
        offset += 1
    return value or None, offset


def read_encoded_string_value(data: bytes, offset: int) -> tuple[str | None, int | None, int]:
    if offset >= len(data):
        return None, None, offset

    charset = None
    first = data[offset]
    if first == 0:
        return "", None, offset + 1

    if first < TEXT_MIN:
        _, offset = read_value_length(data, offset)
        charset_value, offset = parse_short_integer(data, offset)
        charset = charset_value

    text, offset = read_wap_string(data, offset)
    return text, charset, offset


def parse_short_integer(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError("missing short integer")
    return data[offset] & 0x7F, offset + 1


def parse_long_integer(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError("missing long integer length")
    length = data[offset]
    offset += 1
    if offset + length > len(data):
        raise ValueError("truncated long integer")
    value = 0
    for _ in range(length):
        value = (value << 8) | data[offset]
        offset += 1
    return value, offset


def parse_integer_value(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError("missing integer value")
    if data[offset] > TEXT_MAX:
        return parse_short_integer(data, offset)
    return parse_long_integer(data, offset)


def parse_content_type(data: bytes, offset: int) -> tuple[str, dict, int]:
    if offset >= len(data):
        raise ValueError("missing content type")

    params: dict[str, object] = {}
    first = data[offset]
    if first < TEXT_MIN:
        length, offset = read_value_length(data, offset)
        start_offset = offset
        if offset >= len(data):
            raise ValueError("truncated content type")
        first = data[offset]
        if TEXT_MIN <= first <= TEXT_MAX:
            content_type, offset = read_wap_string(data, offset)
        elif first > TEXT_MAX:
            index, offset = parse_short_integer(data, offset)
            content_type = decode_well_known_content_type(index)
        else:
            raise ValueError("invalid content type")

        parameter_length = length - (offset - start_offset)
        if parameter_length > 0:
            params, offset = parse_content_type_params(data, offset, parameter_length)
        elif parameter_length < 0:
            raise ValueError("invalid content type parameter length")
    elif first <= TEXT_MAX:
        content_type, offset = read_wap_string(data, offset)
    else:
        index, offset = parse_short_integer(data, offset)
        content_type = decode_well_known_content_type(index)

    if not content_type:
        raise ValueError("empty content type")
    return content_type, params, offset


def parse_content_type_params(data: bytes, offset: int, length: int) -> tuple[dict, int]:
    params: dict[str, object] = {}
    end = offset + length

    while offset < end:
        param = data[offset]
        offset += 1

        if param in {P_TYPE, P_CT_MR_TYPE}:
            if offset >= len(data):
                break
            if data[offset] > TEXT_MAX:
                index, offset = parse_short_integer(data, offset)
                params["type"] = decode_well_known_content_type(index)
            else:
                params["type"], offset = read_wap_string(data, offset)
        elif param in {P_START, P_DEP_START}:
            params["start"], offset = read_wap_string(data, offset)
        elif param == P_CHARSET:
            if offset >= len(data):
                break
            current = data[offset]
            if (TEXT_MIN < current < TEXT_MAX) or current == 0:
                charset_name, offset = read_wap_string(data, offset)
                params["charset"] = charset_name
            else:
                charset_value, offset = parse_integer_value(data, offset)
                params["charset"] = charset_value
        elif param in {P_DEP_NAME, P_NAME}:
            params["name"], offset = read_wap_string(data, offset)
        else:
            offset = end

    return params, min(offset, end)


def parse_parts(data: bytes, offset: int) -> tuple[list[ParsedMmsPart], int]:
    count, offset = read_uintvar(data, offset)
    parts: list[ParsedMmsPart] = []

    for _ in range(count):
        header_length, offset = read_uintvar(data, offset)
        data_length, offset = read_uintvar(data, offset)
        header_start = offset

        content_type, params, offset = parse_content_type(data, offset)
        part_header_length = header_length - (offset - header_start)
        if part_header_length < 0:
            raise ValueError("invalid part header length")

        header_values, offset = parse_part_headers(data, offset, part_header_length)
        if offset + data_length > len(data):
            raise ValueError("truncated part data")

        part_data = data[offset : offset + data_length]
        offset += data_length
        part_data = decode_transfer_encoded_part(part_data, header_values.get("content_transfer_encoding"))

        if content_type.lower() == "application/vnd.wap.multipart.alternative":
            nested_parts, _ = parse_parts(part_data, 0)
            if nested_parts:
                parts.append(nested_parts[0])
            continue

        parts.append(
            ParsedMmsPart(
                content_type=content_type,
                data=part_data,
                name=_string_or_none(params.get("name")),
                filename=_string_or_none(header_values.get("filename")),
                content_id=_string_or_none(header_values.get("content_id")),
                content_location=_string_or_none(header_values.get("content_location")),
                charset=_coerce_charset(params.get("charset")),
            )
        )

    return parts, offset


def parse_part_headers(data: bytes, offset: int, length: int) -> tuple[dict[str, object], int]:
    end = offset + length
    values: dict[str, object] = {}

    while offset < end:
        header = data[offset]
        offset += 1

        if header > TEXT_MAX:
            if header == P_CONTENT_LOCATION:
                values["content_location"], offset = read_wap_string(data, offset)
            elif header == P_CONTENT_ID:
                values["content_id"], offset = read_wap_string(data, offset, quoted=True)
            elif header in {P_DEP_CONTENT_DISPOSITION, P_CONTENT_DISPOSITION}:
                disposition_length, offset = read_value_length(data, offset)
                disposition_end = offset + disposition_length
                if offset < len(data):
                    disposition_value = data[offset]
                    offset += 1
                    if disposition_value not in {
                        P_DISPOSITION_FROM_DATA,
                        P_DISPOSITION_ATTACHMENT,
                        P_DISPOSITION_INLINE,
                    }:
                        offset -= 1
                        _, offset = read_wap_string(data, offset)
                if offset < disposition_end:
                    parameter = data[offset]
                    offset += 1
                    if parameter == P_FILENAME:
                        values["filename"], offset = read_wap_string(data, offset)
                offset = max(offset, disposition_end)
            else:
                offset = end
        elif TEXT_MIN <= header <= TEXT_MAX:
            header_name, offset = read_wap_string(data, offset - 1)
            header_value, offset = read_wap_string(data, offset)
            if header_name and header_value and header_name.lower() == TRANSFER_ENCODING_HEADER:
                values["content_transfer_encoding"] = header_value
        else:
            offset = end

    return values, min(offset, end)


def decode_transfer_encoded_part(data: bytes, transfer_encoding: object) -> bytes:
    encoding = _string_or_none(transfer_encoding)
    if encoding is None:
        return data
    normalized = encoding.lower()
    if normalized == "base64":
        return base64.b64decode(data)
    if normalized == "quoted-printable":
        return quopri.decodestring(data)
    return data


def decode_text_part(part: ParsedMmsPart) -> str | None:
    encoding = MIB_TO_PYTHON_ENCODING.get(part.charset or 0, "utf-8")
    try:
        return part.data.decode(encoding, errors="replace").strip() or None
    except LookupError:
        return part.data.decode("utf-8", errors="replace").strip() or None


def skip_length_value(data: bytes, offset: int) -> int:
    length, offset = read_value_length(data, offset)
    return min(offset + length, len(data))


def skip_mms_header_value(data: bytes, offset: int) -> int:
    if offset >= len(data):
        return offset

    first = data[offset]
    if first < TEXT_MIN:
        return skip_length_value(data, offset)
    if first > TEXT_MAX:
        try:
            _, offset = parse_integer_value(data, offset)
            return offset
        except ValueError:
            return len(data)
    if first == QUOTED_STRING_FLAG or first == QUOTE or TEXT_MIN <= first <= TEXT_MAX:
        _, offset = read_wap_string(data, offset, quoted=first == QUOTED_STRING_FLAG)
        return offset
    return len(data)


def select_filename(part: ParsedMmsPart, attachment_index: int) -> str:
    candidate = part.filename or part.name or part.content_location or f"part-{attachment_index}"
    suffix = mimetypes.guess_extension(part.content_type) or ".bin"
    if "." not in Path(candidate).name:
        candidate = f"{candidate}{suffix}"
    return Path(candidate).name


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _coerce_charset(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        normalized = value.lower()
        if normalized == "utf-8":
            return 106
        if normalized in {"us-ascii", "ascii"}:
            return 3
        if normalized in {"iso-8859-1", "latin-1"}:
            return 4
    return None


def normalize_mms_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
