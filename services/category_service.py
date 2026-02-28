"""Category service for category management."""

from typing import Optional, List
from models.category import Category
import logging

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for category-related operations."""
    
    @staticmethod
    def get_categories(user_id: int, cat_type: Optional[str] = None) -> List[Category]:
        """Get categories for a user.
        
        Args:
            user_id: User ID
            cat_type: Filter by type ('income' or 'expense')
            
        Returns:
            List of Category instances
        """
        return Category.get_by_user(user_id, cat_type)
    
    @staticmethod
    def get_income_categories(user_id: int) -> List[Category]:
        """Get income categories for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Category instances
        """
        return Category.get_by_user(user_id, 'income')
    
    @staticmethod
    def get_expense_categories(user_id: int) -> List[Category]:
        """Get expense categories for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Category instances
        """
        return Category.get_by_user(user_id, 'expense')
    
    @staticmethod
    def create_category(user_id: int, name: str, cat_type: str, icon: str = '📦') -> Optional[Category]:
        """Create a new category.
        
        Args:
            user_id: User ID
            name: Category name
            cat_type: Category type ('income' or 'expense')
            icon: Category icon (emoji)
            
        Returns:
            Category instance or None if creation failed
        """
        # Check if category already exists
        existing = Category.get_by_name(user_id, name, cat_type)
        if existing:
            logger.warning(f"Category already exists: {name}")
            return existing
        
        return Category.create(user_id, name, cat_type, icon)
    
    @staticmethod
    def update_category(category_id: int, **kwargs) -> bool:
        """Update a category.
        
        Args:
            category_id: Category ID
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        category = Category.get_by_id(category_id)
        if not category:
            logger.error(f"Category not found: {category_id}")
            return False
        
        return category.update(**kwargs)
    
    @staticmethod
    def delete_category(category_id: int) -> bool:
        """Delete a category.
        
        Args:
            category_id: Category ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        category = Category.get_by_id(category_id)
        if not category:
            logger.error(f"Category not found: {category_id}")
            return False
        
        if category.is_default:
            logger.warning(f"Cannot delete default category: {category_id}")
            return False
        
        return category.delete()
    
    @staticmethod
    def get_category_by_id(category_id: int) -> Optional[Category]:
        """Get category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category instance or None if not found
        """
        return Category.get_by_id(category_id)
