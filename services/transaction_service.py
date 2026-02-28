"""Transaction service for transaction management."""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from models.transaction import Transaction
from models.category import Category
import logging

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction-related operations."""
    
    @staticmethod
    def create_transaction(user_id: int, category_id: int, amount: float,
                          description: str, trans_type: str,
                          transaction_date: Optional[date] = None,
                          notes: Optional[str] = None) -> Optional[Transaction]:
        """Create a new transaction.
        
        Args:
            user_id: User ID
            category_id: Category ID
            amount: Transaction amount
            description: Transaction description
            trans_type: Transaction type ('income' or 'expense')
            transaction_date: Date of transaction (defaults to today)
            notes: Additional notes
            
        Returns:
            Transaction instance or None if creation failed
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
        
        return Transaction.create(
            user_id, category_id, amount, description, trans_type,
            transaction_date, notes
        )
    
    @staticmethod
    def get_transaction(transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction instance or None if not found
        """
        return Transaction.get_by_id(transaction_id)
    
    @staticmethod
    def get_user_transactions(user_id: int, limit: int = 10, offset: int = 0,
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             trans_type: Optional[str] = None) -> List[Transaction]:
        """Get transactions for a user with filters.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination
            start_date: Filter by start date
            end_date: Filter by end date
            trans_type: Filter by type ('income' or 'expense')
            
        Returns:
            List of Transaction instances
        """
        return Transaction.get_by_user(user_id, limit, offset, start_date, end_date, trans_type)
    
    @staticmethod
    def get_today_transactions(user_id: int) -> List[Transaction]:
        """Get today's transactions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Transaction instances
        """
        return Transaction.get_today(user_id)
    
    @staticmethod
    def get_transactions_by_period(user_id: int, period: str) -> List[Transaction]:
        """Get transactions for a specific period.
        
        Args:
            user_id: User ID
            period: Period ('today', '7d', '30d', 'this_month', 'last_month')
            
        Returns:
            List of Transaction instances
        """
        today = date.today()
        
        if period == 'today':
            start_date = today
            end_date = today
        elif period == '7d':
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == '30d':
            start_date = today - timedelta(days=30)
            end_date = today
        elif period == 'this_month':
            start_date = today.replace(day=1)
            end_date = today
        elif period == 'last_month':
            # First day of last month
            first_of_month = today.replace(day=1)
            end_date = first_of_month - timedelta(days=1)
            start_date = end_date.replace(day=1)
        else:
            # Default to last 30 days
            start_date = today - timedelta(days=30)
            end_date = today
        
        return Transaction.get_by_date_range(user_id, start_date, end_date)
    
    @staticmethod
    def update_transaction(transaction_id: int, **kwargs) -> bool:
        """Update a transaction.
        
        Args:
            transaction_id: Transaction ID
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        transaction = Transaction.get_by_id(transaction_id)
        if not transaction:
            logger.error(f"Transaction not found: {transaction_id}")
            return False
        
        return transaction.update(**kwargs)
    
    @staticmethod
    def delete_transaction(transaction_id: int) -> bool:
        """Delete a transaction.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        transaction = Transaction.get_by_id(transaction_id)
        if not transaction:
            logger.error(f"Transaction not found: {transaction_id}")
            return False
        
        return transaction.delete()
    
    @staticmethod
    def get_balance(user_id: int, start_date: Optional[date] = None,
                   end_date: Optional[date] = None) -> Dict[str, float]:
        """Get balance for a user.
        
        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with income, expense, and balance
        """
        return Transaction.get_balance(user_id, start_date, end_date)
    
    @staticmethod
    def parse_date_string(date_str: str) -> Optional[date]:
        """Parse natural language date string to date object.
        
        Args:
            date_str: Date string ('today', 'yesterday', 'kemarin', etc.)
            
        Returns:
            Date object or None if parsing failed
        """
        today = date.today()
        date_str = date_str.lower().strip()
        
        if date_str in ['today', 'hari ini', 'sekarang']:
            return today
        elif date_str in ['yesterday', 'kemarin']:
            return today - timedelta(days=1)
        elif date_str in ['2 days ago', '2 hari lalu']:
            return today - timedelta(days=2)
        elif date_str in ['3 days ago', '3 hari lalu']:
            return today - timedelta(days=3)
        elif date_str in ['last week', 'minggu lalu']:
            return today - timedelta(weeks=1)
        
        # Try to parse as date
        try:
            # Try DD/MM/YYYY format
            parts = date_str.split('/')
            if len(parts) == 3:
                day, month, year = map(int, parts)
                return date(year, month, day)
        except:
            pass
        
        return None
    
    @staticmethod
    def search_transactions(user_id: int, keyword: str, limit: int = 50) -> List[Transaction]:
        """Search transactions by keyword in description.
        
        Args:
            user_id: User ID
            keyword: Search keyword
            limit: Maximum number of results
            
        Returns:
            List of Transaction instances
        """
        from config.database import DatabaseConnection
        
        query = """
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s AND (t.description LIKE %s OR t.notes LIKE %s)
            ORDER BY t.transaction_date DESC, t.created_at DESC
            LIMIT %s
        """
        
        keyword_pattern = f"%{keyword}%"
        results = DatabaseConnection.execute_query(
            query, (user_id, keyword_pattern, keyword_pattern, limit), commit=False
        )
        
        return [Transaction(row) for row in results]
