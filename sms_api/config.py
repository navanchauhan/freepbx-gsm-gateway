from __future__ import annotations

from dataclasses import dataclass
import os


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return int(value)


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return float(value)


@dataclass(frozen=True)
class Settings:
    api_host: str
    api_port: int
    api_bearer_token: str
    internal_token: str
    db_path: str
    ami_host: str
    ami_port: int
    ami_username: str
    ami_password: str
    ami_timeout_seconds: float
    sms_device: str
    sms_from_number: str | None
    media_root: str
    modem_port: str | None
    modem_poll_interval_seconds: float
    mms_http_apn: str
    mms_http_pdp_context_id: int
    mms_http_read_chunk_size: int


def load_settings() -> Settings:
    raw_from_number = os.getenv("SMS_FROM_NUMBER")

    return Settings(
        api_host=os.getenv("SMS_API_HOST", "0.0.0.0"),
        api_port=_int_env("SMS_API_PORT", 8080),
        api_bearer_token=os.getenv("SMS_API_BEARER_TOKEN", "change-me"),
        internal_token=os.getenv("SMS_API_INTERNAL_TOKEN", "change-me-internal"),
        db_path=os.getenv("SMS_DB_PATH", "/app/data/sms_api.db"),
        ami_host=os.getenv("AMI_HOST", "asterisk"),
        ami_port=_int_env("AMI_PORT", 5038),
        ami_username=os.getenv("AMI_USERNAME", "admin"),
        ami_password=os.getenv("AMI_PASSWORD", "asterisk123"),
        ami_timeout_seconds=_float_env("AMI_TIMEOUT_SECONDS", 5.0),
        sms_device=os.getenv("SMS_DEVICE", "quectel0"),
        sms_from_number=raw_from_number.strip() if raw_from_number and raw_from_number.strip() else None,
        media_root=os.getenv("SMS_MEDIA_ROOT", "/app/data/media"),
        modem_port=(os.getenv("MMS_MODEM_PORT") or "").strip() or None,
        modem_poll_interval_seconds=_float_env("MMS_POLL_INTERVAL_SECONDS", 5.0),
        mms_http_apn=os.getenv("MMS_APN", "fast.t-mobile.com"),
        mms_http_pdp_context_id=_int_env("MMS_HTTP_PDP_CONTEXT_ID", 5),
        mms_http_read_chunk_size=_int_env("MMS_HTTP_READ_CHUNK_SIZE", 4096),
    )
