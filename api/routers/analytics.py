"""Analytics router."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.auth import get_current_user
from api.helpers import default_date_range, parse_date
from services.report_service import ReportService

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics")
def get_analytics(
    start: Optional[str] = Query(default=None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(default=None, description="End date YYYY-MM-DD"),
    type: str = Query(default="expense", pattern="^(income|expense)$"),
    user=Depends(get_current_user),
):
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date is None or end_date is None:
        start_date, end_date = default_date_range()
    summary = ReportService.get_summary(user.id, start_date, end_date)
    by_category = (
        ReportService.get_income_by_category(user.id, start_date, end_date)
        if type == "income"
        else ReportService.get_expense_by_category(user.id, start_date, end_date)
    )
    by_day = ReportService.get_daily_trend(user.id, start_date, end_date)
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "type": type,
        "summary": {
            "total_income": summary["total_income"],
            "total_expense": summary["total_expense"],
            "balance": summary["balance"],
            "transaction_count": summary["transaction_count"],
        },
        "by_category": [
            {
                "category_name": r["category_name"],
                "category_icon": r["category_icon"],
                "total_amount": r["total_amount"],
                "percentage": round(r["percentage"], 2),
            }
            for r in by_category
        ],
        "by_day": [
            {
                "date": (d["date"].isoformat() if hasattr(d["date"], "isoformat") else str(d["date"])),
                "income": d["income"],
                "expense": d["expense"],
            }
            for d in by_day
        ],
    }
