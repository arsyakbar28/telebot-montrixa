"""Shared helpers for API routes."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, Tuple

from utils.datetime_utils import today_jakarta


def parse_date(d: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD string to date or None."""
    if not d:
        return None
    try:
        return date.fromisoformat(d)
    except ValueError:
        return None


def default_date_range() -> Tuple[date, date]:
    """Return (start, end) for last 30 days."""
    end = today_jakarta()
    start = end - timedelta(days=30)
    return start, end
