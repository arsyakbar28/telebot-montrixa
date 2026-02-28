"""User service for user management and initialization."""

from typing import Optional
from models.user import User
from models.category import Category
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations."""
    
    @staticmethod
    def register_user(telegram_id: int, username: Optional[str] = None,
                     first_name: Optional[str] = None, last_name: Optional[str] = None,
                     language_code: str = 'id') -> Optional[User]:
        """Register a new user and create default categories.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            language_code: User's language code
            
        Returns:
            User instance or None if registration failed
        """
        # Check if user already exists
        user = User.get_by_telegram_id(telegram_id)
        if user:
            logger.info(f"User already exists: {telegram_id}")
            return user
        
        # Create new user
        user = User.create(telegram_id, username, first_name, last_name, language_code)
        if not user:
            logger.error(f"Failed to create user: {telegram_id}")
            return None
        
        # Create default categories
        all_categories = Settings.DEFAULT_INCOME_CATEGORIES + Settings.DEFAULT_EXPENSE_CATEGORIES
        success = Category.create_default_categories(user.id, all_categories)
        
        if success:
            logger.info(f"Successfully registered user and created default categories: {telegram_id}")
        else:
            logger.warning(f"User created but failed to create default categories: {telegram_id}")
        
        return user
    
    @staticmethod
    def get_user(telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User instance or None if not found
        """
        return User.get_by_telegram_id(telegram_id)
    
    @staticmethod
    def get_or_register(telegram_id: int, username: Optional[str] = None,
                       first_name: Optional[str] = None, last_name: Optional[str] = None,
                       language_code: str = 'id') -> Optional[User]:
        """Get existing user or register new one.
        
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
        return UserService.register_user(telegram_id, username, first_name, last_name, language_code)
