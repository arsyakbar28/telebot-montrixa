"""Transactions CRUD router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth import get_current_user
from api.helpers import default_date_range, parse_date
from api.schemas import TransactionCreateRequest, TransactionUpdateRequest
from models.transaction import Transaction
from services.transaction_service import TransactionService
from utils.validators import Validator

router = APIRouter(prefix="/api", tags=["transactions"])


def _get_owned_transaction(transaction_id: int, user_id: int):
    """Return transaction if found and owned by user; else raise 404/403."""
    transaction = Transaction.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    if transaction.user_id != user_id:
        raise HTTPException(status_code=403, detail="Tidak punya akses ke transaksi ini")
    return transaction


@router.get("/transactions")
def get_transactions(
    start: Optional[str] = Query(default=None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(default=None, description="End date YYYY-MM-DD"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user=Depends(get_current_user),
):
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date is None or end_date is None:
        start_date, end_date = default_date_range()
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


@router.get("/transactions/meta")
def get_transactions_meta(user=Depends(get_current_user)):
    bounds = Transaction.get_date_bounds(user.id)
    oldest = bounds.get("oldest_date")
    newest = bounds.get("newest_date")
    return {
        "oldest_date": oldest.isoformat() if hasattr(oldest, "isoformat") and oldest else None,
        "newest_date": newest.isoformat() if hasattr(newest, "isoformat") and newest else None,
    }


@router.post("/transaction")
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


@router.patch("/transaction/{transaction_id}")
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


@router.delete("/transaction/{transaction_id}")
def delete_transaction(transaction_id: int, user=Depends(get_current_user)):
    _get_owned_transaction(transaction_id, user.id)
    ok = TransactionService.delete_transaction(transaction_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Gagal menghapus transaksi")
    return {"deleted": True}
