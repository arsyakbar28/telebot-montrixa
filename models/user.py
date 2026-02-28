"""User model and database operations."""

from datetime import datetime
from typing import Optional, Dict, Any
from config.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class User:
    """User model representing a Telegram user."""
    
    def __init__(self, user_data: Dict[str, Any]):
        """Initialize User from database row."""
        self.id = user_data.get('id')
        self.telegram_id = user_data.get('telegram_id')
        self.username = user_data.get('username')
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.timezone = user_data.get('timezone', 'Asia/Jakarta')
        self.language_code = user_data.get('language_code', 'id')
        self.is_active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or str(self.telegram_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'timezone': self.timezone,
            'language_code': self.language_code,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @staticmethod
    def create(telegram_id: int, username: Optional[str] = None, 
               first_name: Optional[str] = None, last_name: Optional[str] = None,
               language_code: str = 'id') -> Optional['User']:
        """Create a new user.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            language_code: User's language code
            
        Returns:
            User instance or None if creation failed
        """
        query = """
            INSERT INTO users (telegram_id, username, first_name, last_name, language_code)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query, (telegram_id, username, first_name, last_name, language_code))
                user_id = cursor.lastrowid
            
            logger.info(f"Created user: {telegram_id} - {first_name}")
            return User.get_by_telegram_id(telegram_id)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    @staticmethod
    def get_by_telegram_id(telegram_id: int) -> Optional['User']:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User instance or None if not found
        """
        query = "SELECT * FROM users WHERE telegram_id = %s"
        result = DatabaseConnection.execute_query(query, (telegram_id,), fetch_one=True, commit=False)
        
        if result:
            return User(result)
        return None
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """Get user by internal ID.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            User instance or None if not found
        """
        query = "SELECT * FROM users WHERE id = %s"
        result = DatabaseConnection.execute_query(query, (user_id,), fetch_one=True, commit=False)
        
        if result:
            return User(result)
        return None
    
    @staticmethod
    def get_or_create(telegram_id: int, username: Optional[str] = None,
                     first_name: Optional[str] = None, last_name: Optional[str] = None,
                     language_code: str = 'id') -> Optional['User']:
        """Get existing user or create new one.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            language_code: User's language code
            
        Returns:
            User instance or None
        """
        user = User.get_by_telegram_id(telegram_id)
        if user:
            return user
        return User.create(telegram_id, username, first_name, last_name, language_code)
    
    def update(self, **kwargs) -> bool:
        """Update user information.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        allowed_fields = ['username', 'first_name', 'last_name', 'timezone', 
                         'language_code', 'is_active']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            return False
        
        values.append(self.telegram_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE telegram_id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(values))
            
            # Update instance
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(self, field, value)
            
            logger.info(f"Updated user: {self.telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete user (soft delete by setting is_active to False).
        
        Returns:
            True if deletion successful, False otherwise
        """
        return self.update(is_active=False)
    
    @staticmethod
    def get_all_active() -> list['User']:
        """Get all active users.
        
        Returns:
            List of User instances
        """
        query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC"
        results = DatabaseConnection.execute_query(query, commit=False)
        
        return [User(row) for row in results]
    
    @staticmethod
    def count() -> int:
        """Get total number of active users.
        
        Returns:
            Count of active users
        """
        query = "SELECT COUNT(*) as count FROM users WHERE is_active = TRUE"
        result = DatabaseConnection.execute_query(query, fetch_one=True, commit=False)
        
        return result['count'] if result else 0
