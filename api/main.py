"""FastAPI app for Montrixa Telegram Mini App."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.auth import get_current_user
from api.schemas import TransactionCreateRequest, TransactionUpdateRequest
from models.transaction import Transaction
from services.category_service import CategoryService
from services.report_service import ReportService
from services.transaction_service import TransactionService
from utils.datetime_utils import today_jakarta
from utils.validators import Validator


app = FastAPI(title="Montrixa Mini App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NoCacheStaticFiles(StaticFiles):
    """Static files with no-store headers to avoid stale Telegram WebView cache."""

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/categories")
def get_categories(
    type: str = Query(default="expense", pattern="^(income|expense)$"),
    user=Depends(get_current_user),
):
    categories = (
        CategoryService.get_income_categories(user.id)
        if type == "income"
        else CategoryService.get_expense_categories(user.id)
    )
    return {
        "type": type,
        "categories": [
            {"id": c.id, "name": c.name, "icon": c.icon, "type": c.type} for c in categories
        ],
    }


@app.get("/api/balance")
def get_balance(
    start: Optional[str] = Query(default=None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(default=None, description="End date YYYY-MM-DD"),
    user=Depends(get_current_user),
):
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    return TransactionService.get_balance(user.id, start_date=start_date, end_date=end_date)


@app.get("/api/analytics")
def get_analytics(
    start: Optional[str] = Query(default=None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(default=None, description="End date YYYY-MM-DD"),
    type: str = Query(default="expense", pattern="^(income|expense)$"),
    user=Depends(get_current_user),
):
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    if start_date is None or end_date is None:
        start_date, end_date = _default_date_range()
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


def _parse_date(d: Optional[str]) -> Optional[date]:
    if not d:
        return None
    try:
        return date.fromisoformat(d)
    except ValueError:
        return None


def _default_date_range():
    end = today_jakarta()
    start = end - timedelta(days=30)
    return start, end


@app.get("/api/transactions")
def get_transactions(
    start: Optional[str] = Query(default=None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(default=None, description="End date YYYY-MM-DD"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user=Depends(get_current_user),
):
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    if start_date is None or end_date is None:
        start_date, end_date = _default_date_range()
    transactions = TransactionService.get_user_transactions(
        user.id, limit=limit, offset=offset, start_date=start_date, end_date=end_date
    )
    total = Transaction.get_count(user.id, start_date=start_date, end_date=end_date)
    return {
        "transactions": [t.to_dict() for t in transactions],
        "total": total,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


@app.post("/api/transaction")
def create_transaction(payload: TransactionCreateRequest, user=Depends(get_current_user)):
    is_valid, amount, err = Validator.validate_amount(payload.amount)
    if not is_valid or amount is None:
        raise HTTPException(status_code=400, detail=err or "Invalid amount")

    desc = (payload.description or "-").strip() or "-"
    if desc != "-":
        is_valid_desc, desc2, err_desc = Validator.validate_description(desc)
        if not is_valid_desc or desc2 is None:
            raise HTTPException(status_code=400, detail=err_desc or "Invalid description")
        desc = desc2

    transaction = TransactionService.create_transaction(
        user_id=user.id,
        category_id=payload.category_id,
        amount=amount,
        description=desc,
        trans_type=payload.type,
    )
    if not transaction:
        raise HTTPException(status_code=400, detail="Failed to create transaction")

    return {"transaction": transaction.to_dict()}


def _get_owned_transaction(transaction_id: int, user_id: int):
    """Return transaction if found and owned by user; else raise 404/403."""
    transaction = Transaction.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    if transaction.user_id != user_id:
        raise HTTPException(status_code=403, detail="Tidak punya akses ke transaksi ini")
    return transaction


@app.patch("/api/transaction/{transaction_id}")
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdateRequest,
    user=Depends(get_current_user),
):
    transaction = _get_owned_transaction(transaction_id, user.id)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return {"transaction": transaction.to_dict()}

    if "amount" in updates and updates["amount"] is not None:
        is_valid, amount_val, err = Validator.validate_amount(updates["amount"])
        if not is_valid or amount_val is None:
            raise HTTPException(status_code=400, detail=err or "Invalid amount")
        updates["amount"] = amount_val
    if "description" in updates and updates["description"] is not None:
        desc = (updates["description"] or "-").strip() or "-"
        if desc != "-":
            is_valid_desc, desc2, err_desc = Validator.validate_description(desc)
            if not is_valid_desc or desc2 is None:
                raise HTTPException(status_code=400, detail=err_desc or "Invalid description")
            desc = desc2
        updates["description"] = desc

    ok = TransactionService.update_transaction(transaction_id, **updates)
    if not ok:
        raise HTTPException(status_code=400, detail="Gagal memperbarui transaksi")
    updated = Transaction.get_by_id(transaction_id)
    return {"transaction": updated.to_dict()}


@app.delete("/api/transaction/{transaction_id}")
def delete_transaction(transaction_id: int, user=Depends(get_current_user)):
    _get_owned_transaction(transaction_id, user.id)
    ok = TransactionService.delete_transaction(transaction_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Gagal menghapus transaksi")
    return {"deleted": True}


# Serve Mini App static files (optional, for same-origin hosting)
_miniapp_dir = Path(__file__).resolve().parents[1] / "miniapp"
if _miniapp_dir.exists():
    app.mount("/", NoCacheStaticFiles(directory=str(_miniapp_dir), html=True), name="miniapp")
