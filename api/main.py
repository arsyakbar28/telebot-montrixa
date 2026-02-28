"""FastAPI app for Montrixa Telegram Mini App."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.auth import get_current_user
from api.schemas import TransactionCreateRequest
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from utils.validators import Validator


app = FastAPI(title="Montrixa Mini App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
def get_balance(user=Depends(get_current_user)):
    return TransactionService.get_balance(user.id)


@app.get("/api/transactions")
def get_transactions(
    period: str = Query(default="30d", pattern="^(today|7d|30d|this_month|last_month)$"),
    user=Depends(get_current_user),
):
    transactions = TransactionService.get_transactions_by_period(user.id, period)
    return {
        "period": period,
        "transactions": [t.to_dict() for t in transactions],
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


# Serve Mini App static files (optional, for same-origin hosting)
_miniapp_dir = Path(__file__).resolve().parents[1] / "miniapp"
if _miniapp_dir.exists():
    app.mount("/", StaticFiles(directory=str(_miniapp_dir), html=True), name="miniapp")

