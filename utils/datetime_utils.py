"""Timezone-aware date/time helpers."""

from __future__ import annotations

from datetime import date, datetime

from config.settings import Settings


def now_jakarta() -> datetime:
    """Return current datetime in configured app timezone (default: Asia/Jakarta)."""
    return datetime.now(Settings.TZ)


def today_jakarta() -> date:
    """Return current date in configured app timezone (default: Asia/Jakarta)."""
    return now_jakarta().date()

