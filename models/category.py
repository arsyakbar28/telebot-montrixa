"""Category model and database operations."""

from typing import Optional, Dict, Any, List
from config.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class Category:
    """Category model for income and expense categorization."""
    
    def __init__(self, category_data: Dict[str, Any]):
        """Initialize Category from database row."""
        self.id = category_data.get('id')
        self.user_id = category_data.get('user_id')
        self.name = category_data.get('name')
        self.type = category_data.get('type')  # 'income' or 'expense'
        self.icon = category_data.get('icon', '📦')
        self.is_default = category_data.get('is_default', False)
        self.is_active = category_data.get('is_active', True)
        self.created_at = category_data.get('created_at')
        self.updated_at = category_data.get('updated_at')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'icon': self.icon,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @property
    def display_name(self) -> str:
        """Get category display name with icon."""
        return f"{self.icon} {self.name}" if self.icon else self.name
    
    @staticmethod
    def create(user_id: int, name: str, cat_type: str, icon: str = '📦',
               is_default: bool = False) -> Optional['Category']:
        """Create a new category.
        
        Args:
            user_id: User ID
            name: Category name
            cat_type: Category type ('income' or 'expense')
            icon: Emoji icon for category
            is_default: Whether this is a default category
            
        Returns:
            Category instance or None if creation failed
        """
        query = """
            INSERT INTO categories (user_id, name, type, icon, is_default)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query, (user_id, name, cat_type, icon, is_default))
                category_id = cursor.lastrowid
            
            logger.info(f"Created category: {name} for user {user_id}")
            return Category.get_by_id(category_id)
        except Exception as e:
            logger.error(f"Failed to create category: {e}")
            return None
    
    @staticmethod
    def get_by_id(category_id: int) -> Optional['Category']:
        """Get category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category instance or None if not found
        """
        query = "SELECT * FROM categories WHERE id = %s"
        result = DatabaseConnection.execute_query(query, (category_id,), fetch_one=True, commit=False)
        
        if result:
            return Category(result)
        return None
    
    @staticmethod
    def get_by_user(user_id: int, cat_type: Optional[str] = None,
                    include_inactive: bool = False) -> List['Category']:
        """Get all categories for a user.
        
        Args:
            user_id: User ID
            cat_type: Filter by type ('income' or 'expense'), None for all
            include_inactive: Include inactive categories
            
        Returns:
            List of Category instances
        """
        query = "SELECT * FROM categories WHERE user_id = %s"
        params = [user_id]
        
        if cat_type:
            query += " AND type = %s"
            params.append(cat_type)
        
        if not include_inactive:
            query += " AND is_active = TRUE"
        
        query += " ORDER BY is_default DESC, name ASC"
        
        results = DatabaseConnection.execute_query(query, tuple(params), commit=False)
        return [Category(row) for row in results]
    
    @staticmethod
    def get_by_name(user_id: int, name: str, cat_type: str) -> Optional['Category']:
        """Get category by name and type.
        
        Args:
            user_id: User ID
            name: Category name
            cat_type: Category type
            
        Returns:
            Category instance or None if not found
        """
        query = """
            SELECT * FROM categories 
            WHERE user_id = %s AND name = %s AND type = %s AND is_active = TRUE
        """
        result = DatabaseConnection.execute_query(
            query, (user_id, name, cat_type), fetch_one=True, commit=False
        )
        
        if result:
            return Category(result)
        return None
    
    def update(self, **kwargs) -> bool:
        """Update category information.
        
        Args:
            **kwargs: Fields to update (name, icon, is_active)
            
        Returns:
            True if update successful, False otherwise
        """
        allowed_fields = ['name', 'icon', 'is_active']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            return False
        
        values.append(self.id)
        query = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(values))
            
            # Update instance
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(self, field, value)
            
            logger.info(f"Updated category: {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update category: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete category (soft delete).
        
        Returns:
            True if deletion successful, False otherwise
        """
        if self.is_default:
            logger.warning(f"Cannot delete default category: {self.id}")
            return False
        
        return self.update(is_active=False)
    
    @staticmethod
    def create_default_categories(user_id: int, categories: List[tuple]) -> bool:
        """Create default categories for a new user.
        
        Args:
            user_id: User ID
            categories: List of tuples (name, type)
            
        Returns:
            True if all categories created successfully
        """
        try:
            query = """
                INSERT INTO categories (user_id, name, type, icon, is_default)
                VALUES (%s, %s, %s, %s, TRUE)
            """
            
            params_list = []
            for name_with_icon, cat_type in categories:
                # Extract icon from name (first character if emoji)
                parts = name_with_icon.split(' ', 1)
                if len(parts) == 2:
                    icon, name = parts
                else:
                    icon, name = '📦', parts[0]
                
                params_list.append((user_id, name, cat_type, icon))
            
            DatabaseConnection.execute_many(query, params_list)
            logger.info(f"Created {len(params_list)} default categories for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create default categories: {e}")
            return False
