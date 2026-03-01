"""Balance router."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.auth import get_current_user
from api.helpers import parse_date
from services.transaction_service import TransactionService

router = APIRouter(prefix="/api", tags=["balance"])


@router.get("/balance")
def get_balance(
    start: Optional[str] = Query(default=None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(default=None, description="End date YYYY-MM-DD"),
    user=Depends(get_current_user),
):
    start_date = parse_date(start)
    end_date = parse_date(end)
    return TransactionService.get_balance(user.id, start_date=start_date, end_date=end_date)
