"""Pydantic schemas for Mini App API."""

from __future__ import annotations

from typing import Optional, Literal

from pydantic import BaseModel, Field


class TransactionCreateRequest(BaseModel):
    amount: str = Field(..., description="Transaction amount, digits with optional separators")
    description: Optional[str] = Field(default="-", max_length=500)
    category_id: int
    type: Literal["income", "expense"]


class TransactionUpdateRequest(BaseModel):
    """Optional fields for PATCH; only sent fields are updated."""
    amount: Optional[str] = Field(default=None, description="Transaction amount")
    description: Optional[str] = Field(default=None, max_length=500)
    category_id: Optional[int] = None
    type: Optional[Literal["income", "expense"]] = None


class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    type: str
    transaction_date: str
    category_id: int
    category_name: Optional[str] = None
    category_icon: Optional[str] = None

