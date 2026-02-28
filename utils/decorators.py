"""Decorators for bot handlers."""

from functools import wraps
from services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


def authenticated(func):
    """Decorator to ensure user is authenticated.
    
    Automatically registers new users or gets existing user.
    Injects user object as first parameter after update and context.
    """
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        telegram_user = update.effective_user
        
        if not telegram_user:
            logger.warning("No telegram user in update")
            return
        
        # Get or register user
        user = UserService.get_or_register(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language_code=telegram_user.language_code or 'id'
        )
        
        if not user:
            await update.message.reply_text(
                "❌ Terjadi kesalahan saat mendaftar. Silakan coba lagi."
            )
            return
        
        # Call original function with user parameter
        return await func(update, context, user, *args, **kwargs)
    
    return wrapper


def error_handler(func):
    """Decorator to handle errors in bot handlers."""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            
            # Try to send error message to user
            try:
                if update.message:
                    await update.message.reply_text(
                        "❌ Terjadi kesalahan. Silakan coba lagi atau hubungi admin."
                    )
                elif update.callback_query:
                    await update.callback_query.message.reply_text(
                        "❌ Terjadi kesalahan. Silakan coba lagi atau hubungi admin."
                    )
            except:
                pass
    
    return wrapper


def admin_only(func):
    """Decorator to restrict access to admin users only.
    
    Note: Requires ADMIN_USER_IDS to be set in settings.
    """
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        telegram_user = update.effective_user
        
        # Check if user is admin (you can define admin IDs in settings)
        # For now, allow all users
        # TODO: Implement admin check if needed
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper
