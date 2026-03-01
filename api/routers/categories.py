"""Categories router."""

from fastapi import APIRouter, Depends, Query

from api.auth import get_current_user
from services.category_service import CategoryService

router = APIRouter(prefix="/api", tags=["categories"])


@router.get("/categories")
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
