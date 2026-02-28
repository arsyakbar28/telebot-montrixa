"""Recurring transaction service."""

from typing import Optional, List
from datetime import date
from models.recurring import RecurringTransaction
from models.category import Category
from services.transaction_service import TransactionService
import logging

logger = logging.getLogger(__name__)


class RecurringService:
    """Service for recurring transaction operations."""
    
    @staticmethod
    def create_recurring(user_id: int, category_id: int, amount: float,
                        description: str, trans_type: str, frequency: str,
                        start_date: Optional[date] = None) -> Optional[RecurringTransaction]:
        """Create a new recurring transaction.
        
        Args:
            user_id: User ID
            category_id: Category ID
            amount: Transaction amount
            description: Transaction description
            trans_type: Transaction type ('income' or 'expense')
            frequency: Frequency ('daily', 'weekly', 'monthly')
            start_date: Start date (defaults to today)
            
        Returns:
            RecurringTransaction instance or None if creation failed
        """
        # Validate category belongs to user
        category = Category.get_by_id(category_id)
        if not category or category.user_id != user_id:
            logger.error(f"Invalid category {category_id} for user {user_id}")
            return None
        
        # Validate category type matches transaction type
        if category.type != trans_type:
            logger.error(f"Category type {category.type} doesn't match transaction type {trans_type}")
            return None
        
        return RecurringTransaction.create(
            user_id, category_id, amount, description, trans_type, frequency, start_date
        )
    
    @staticmethod
    def get_recurring(recurring_id: int) -> Optional[RecurringTransaction]:
        """Get recurring transaction by ID.
        
        Args:
            recurring_id: Recurring transaction ID
            
        Returns:
            RecurringTransaction instance or None if not found
        """
        return RecurringTransaction.get_by_id(recurring_id)
    
    @staticmethod
    def get_user_recurring(user_id: int) -> List[RecurringTransaction]:
        """Get all recurring transactions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of RecurringTransaction instances
        """
        return RecurringTransaction.get_by_user(user_id)
    
    @staticmethod
    def update_recurring(recurring_id: int, **kwargs) -> bool:
        """Update a recurring transaction.
        
        Args:
            recurring_id: Recurring transaction ID
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        recurring = RecurringTransaction.get_by_id(recurring_id)
        if not recurring:
            logger.error(f"Recurring transaction not found: {recurring_id}")
            return False
        
        return recurring.update(**kwargs)
    
    @staticmethod
    def pause_recurring(recurring_id: int) -> bool:
        """Pause a recurring transaction.
        
        Args:
            recurring_id: Recurring transaction ID
            
        Returns:
            True if pause successful, False otherwise
        """
        recurring = RecurringTransaction.get_by_id(recurring_id)
        if not recurring:
            logger.error(f"Recurring transaction not found: {recurring_id}")
            return False
        
        return recurring.pause()
    
    @staticmethod
    def resume_recurring(recurring_id: int) -> bool:
        """Resume a recurring transaction.
        
        Args:
            recurring_id: Recurring transaction ID
            
        Returns:
            True if resume successful, False otherwise
        """
        recurring = RecurringTransaction.get_by_id(recurring_id)
        if not recurring:
            logger.error(f"Recurring transaction not found: {recurring_id}")
            return False
        
        return recurring.resume()
    
    @staticmethod
    def delete_recurring(recurring_id: int) -> bool:
        """Delete a recurring transaction.
        
        Args:
            recurring_id: Recurring transaction ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        recurring = RecurringTransaction.get_by_id(recurring_id)
        if not recurring:
            logger.error(f"Recurring transaction not found: {recurring_id}")
            return False
        
        return recurring.delete()
    
    @staticmethod
    def process_due_recurring() -> int:
        """Process all due recurring transactions.
        
        Returns:
            Number of transactions created
        """
        due_recurring = RecurringTransaction.get_due_transactions()
        count = 0
        
        for recurring in due_recurring:
            # Create transaction
            transaction = TransactionService.create_transaction(
                user_id=recurring.user_id,
                category_id=recurring.category_id,
                amount=recurring.amount,
                description=recurring.description,
                trans_type=recurring.type,
                transaction_date=recurring.next_run_date,
                notes=f"Recurring transaction (ID: {recurring.id})"
            )
            
            if transaction:
                # Update next run date
                recurring.update_next_run_date()
                count += 1
                logger.info(f"Processed recurring transaction {recurring.id}")
            else:
                logger.error(f"Failed to create transaction for recurring {recurring.id}")
        
        if count > 0:
            logger.info(f"Processed {count} recurring transactions")
        
        return count
