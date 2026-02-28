"""Telegram Mini App init_data validation and user dependency."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException

from config.settings import Settings
from services.user_service import UserService


@dataclass(frozen=True)
class TelegramInitData:
    raw: str
    data: Dict[str, str]
    user: Dict[str, Any]


def _parse_init_data(raw: str) -> Dict[str, str]:
    # raw is a querystring: "query_id=...&user=...&auth_date=...&hash=..."
    return dict(parse_qsl(raw, keep_blank_values=True, strict_parsing=False))


def validate_init_data(raw: str, bot_token: str, max_age_seconds: int) -> TelegramInitData:
    if not raw:
        raise HTTPException(status_code=401, detail="Missing init_data")

    data = _parse_init_data(raw)
    received_hash = data.get("hash")
    auth_date = data.get("auth_date")
    user_raw = data.get("user")

    if not received_hash or not auth_date or not user_raw:
        raise HTTPException(status_code=401, detail="Invalid init_data payload")

    try:
        auth_date_int = int(auth_date)
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid auth_date") from e

    now = int(time.time())
    if max_age_seconds > 0 and (now - auth_date_int) > max_age_seconds:
        raise HTTPException(status_code=401, detail="init_data expired")

    # Build the data_check_string
    check_pairs = []
    for k, v in data.items():
        if k == "hash":
            continue
        check_pairs.append(f"{k}={v}")
    check_pairs.sort()
    data_check_string = "\n".join(check_pairs)

    # secret_key = HMAC_SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=401, detail="init_data signature mismatch")

    try:
        user_obj = json.loads(user_raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=401, detail="Invalid user JSON") from e

    return TelegramInitData(raw=raw, data=data, user=user_obj)


def _extract_init_data(
    authorization: Optional[str],
    x_telegram_init_data: Optional[str],
    init_data: Optional[str],
) -> str:
    if x_telegram_init_data:
        return x_telegram_init_data.strip()

    if authorization:
        auth = authorization.strip()
        if auth.lower().startswith("tma "):
            return auth[4:].strip()

    if init_data:
        return init_data.strip()

    return ""


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    x_telegram_init_data: Optional[str] = Header(default=None, alias="X-Telegram-Init-Data"),
    init_data: Optional[str] = Header(default=None, alias="X-Init-Data"),
):
    """FastAPI dependency to authenticate user using Telegram init_data."""
    raw = _extract_init_data(authorization, x_telegram_init_data, init_data)
    init = validate_init_data(
        raw=raw,
        bot_token=Settings.TELEGRAM_BOT_TOKEN or "",
        max_age_seconds=Settings.MINIAPP_INITDATA_MAX_AGE_SECONDS,
    )

    u = init.user or {}
    telegram_id = u.get("id")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Missing user id in init_data")

    user = UserService.get_or_register(
        telegram_id=int(telegram_id),
        username=u.get("username"),
        first_name=u.get("first_name"),
        last_name=u.get("last_name"),
        language_code=u.get("language_code") or "id",
    )
    if not user:
        raise HTTPException(status_code=500, detail="Failed to initialize user")
    return user

