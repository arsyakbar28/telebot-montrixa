"""Recurring transaction model and database operations."""

from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta
from config.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class RecurringTransaction:
    """Recurring transaction model for automated transaction creation."""
    
    def __init__(self, recurring_data: Dict[str, Any]):
        """Initialize RecurringTransaction from database row."""
        self.id = recurring_data.get('id')
        self.user_id = recurring_data.get('user_id')
        self.category_id = recurring_data.get('category_id')
        self.amount = float(recurring_data.get('amount', 0))
        self.description = recurring_data.get('description')
        self.type = recurring_data.get('type')  # 'income' or 'expense'
        self.frequency = recurring_data.get('frequency')  # 'daily', 'weekly', 'monthly'
        self.start_date = recurring_data.get('start_date')
        self.next_run_date = recurring_data.get('next_run_date')
        self.last_run_date = recurring_data.get('last_run_date')
        self.end_date = recurring_data.get('end_date')
        self.is_active = recurring_data.get('is_active', True)
        self.created_at = recurring_data.get('created_at')
        self.updated_at = recurring_data.get('updated_at')
        
        # Extra fields from joins
        self.category_name = recurring_data.get('category_name')
        self.category_icon = recurring_data.get('category_icon')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recurring transaction to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'description': self.description,
            'type': self.type,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            'next_run_date': self.next_run_date.isoformat() if isinstance(self.next_run_date, date) else self.next_run_date,
            'last_run_date': self.last_run_date.isoformat() if isinstance(self.last_run_date, date) else self.last_run_date if self.last_run_date else None,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'category_name': self.category_name,
            'category_icon': self.category_icon,
        }
    
    @staticmethod
    def create(user_id: int, category_id: int, amount: float, description: str,
               trans_type: str, frequency: str, start_date: Optional[date] = None) -> Optional['RecurringTransaction']:
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
        if start_date is None:
            start_date = date.today()
        
        query = """
            INSERT INTO recurring_transactions 
            (user_id, category_id, amount, description, type, frequency, start_date, next_run_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query, (
                    user_id, category_id, amount, description, trans_type,
                    frequency, start_date, start_date
                ))
                recurring_id = cursor.lastrowid
            
            logger.info(f"Created recurring transaction: {trans_type} {amount} for user {user_id}")
            return RecurringTransaction.get_by_id(recurring_id)
        except Exception as e:
            logger.error(f"Failed to create recurring transaction: {e}")
            return None
    
    @staticmethod
    def get_by_id(recurring_id: int) -> Optional['RecurringTransaction']:
        """Get recurring transaction by ID with category info.
        
        Args:
            recurring_id: Recurring transaction ID
            
        Returns:
            RecurringTransaction instance or None if not found
        """
        query = """
            SELECT r.*, c.name as category_name, c.icon as category_icon
            FROM recurring_transactions r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE r.id = %s
        """
        result = DatabaseConnection.execute_query(query, (recurring_id,), fetch_one=True, commit=False)
        
        if result:
            return RecurringTransaction(result)
        return None
    
    @staticmethod
    def get_by_user(user_id: int, include_inactive: bool = False) -> List['RecurringTransaction']:
        """Get all recurring transactions for a user.
        
        Args:
            user_id: User ID
            include_inactive: Include inactive recurring transactions
            
        Returns:
            List of RecurringTransaction instances
        """
        query = """
            SELECT r.*, c.name as category_name, c.icon as category_icon
            FROM recurring_transactions r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE r.user_id = %s
        """
        params = [user_id]
        
        if not include_inactive:
            query += " AND r.is_active = TRUE"
        
        query += " ORDER BY r.next_run_date ASC"
        
        results = DatabaseConnection.execute_query(query, tuple(params), commit=False)
        return [RecurringTransaction(row) for row in results]
    
    @staticmethod
    def get_due_transactions(current_date: Optional[date] = None) -> List['RecurringTransaction']:
        """Get all recurring transactions that are due to run.
        
        Args:
            current_date: Date to check against (defaults to today)
            
        Returns:
            List of RecurringTransaction instances
        """
        if current_date is None:
            current_date = date.today()
        
        query = """
            SELECT r.*, c.name as category_name, c.icon as category_icon
            FROM recurring_transactions r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE r.is_active = TRUE 
            AND r.next_run_date <= %s
            AND (r.end_date IS NULL OR r.end_date >= %s)
            ORDER BY r.next_run_date ASC
        """
        results = DatabaseConnection.execute_query(query, (current_date, current_date), commit=False)
        return [RecurringTransaction(row) for row in results]
    
    def calculate_next_run_date(self, from_date: Optional[date] = None) -> date:
        """Calculate the next run date based on frequency.
        
        Args:
            from_date: Date to calculate from (defaults to next_run_date)
            
        Returns:
            Next run date
        """
        if from_date is None:
            from_date = self.next_run_date if self.next_run_date else date.today()
        
        if self.frequency == 'daily':
            return from_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return from_date + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            # Add one month (handle month overflow)
            month = from_date.month
            year = from_date.year
            
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            
            # Handle day overflow (e.g., Jan 31 -> Feb 28)
            day = min(from_date.day, 28 if month == 2 else 30 if month in [4, 6, 9, 11] else 31)
            
            return date(year, month, day)
        
        return from_date
    
    def update_next_run_date(self) -> bool:
        """Update next_run_date to the next occurrence.
        
        Returns:
            True if update successful, False otherwise
        """
        next_date = self.calculate_next_run_date()
        
        query = """
            UPDATE recurring_transactions 
            SET next_run_date = %s, last_run_date = %s 
            WHERE id = %s
        """
        try:
            DatabaseConnection.execute_query(query, (next_date, date.today(), self.id))
            self.next_run_date = next_date
            self.last_run_date = date.today()
            logger.info(f"Updated next run date for recurring transaction {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update next run date: {e}")
            return False
    
    def update(self, **kwargs) -> bool:
        """Update recurring transaction information.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        allowed_fields = ['amount', 'description', 'frequency', 'is_active', 'end_date']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            return False
        
        values.append(self.id)
        query = f"UPDATE recurring_transactions SET {', '.join(update_fields)} WHERE id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(values))
            
            # Update instance
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(self, field, value)
            
            logger.info(f"Updated recurring transaction: {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update recurring transaction: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause recurring transaction.
        
        Returns:
            True if pause successful, False otherwise
        """
        return self.update(is_active=False)
    
    def resume(self) -> bool:
        """Resume recurring transaction.
        
        Returns:
            True if resume successful, False otherwise
        """
        return self.update(is_active=True)
    
    def delete(self) -> bool:
        """Delete recurring transaction.
        
        Returns:
            True if deletion successful, False otherwise
        """
        query = "DELETE FROM recurring_transactions WHERE id = %s"
        try:
            DatabaseConnection.execute_query(query, (self.id,))
            logger.info(f"Deleted recurring transaction: {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete recurring transaction: {e}")
            return False
