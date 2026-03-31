from __future__ import annotations

import re


PHONE_DIGITS_RE = re.compile(r"[^\d+]")


def normalize_phone_number(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise ValueError("phone number is required")

    if candidate.startswith("+"):
        digits = PHONE_DIGITS_RE.sub("", candidate)
        if not re.fullmatch(r"\+[1-9]\d{1,14}", digits):
            raise ValueError("phone number must be in E.164 format or a 10/11 digit US number")
        return digits

    digits = re.sub(r"\D", "", candidate)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    if 1 < len(digits) <= 15 and not digits.startswith("0"):
        return f"+{digits}"

    raise ValueError("phone number must be in E.164 format or a 10/11 digit US number")
