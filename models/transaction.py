"""Transaction model and database operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from config.database import DatabaseConnection
from utils.datetime_utils import today_jakarta
import logging

logger = logging.getLogger(__name__)


class Transaction:
    """Transaction model for income and expense tracking."""
    
    def __init__(self, transaction_data: Dict[str, Any]):
        """Initialize Transaction from database row."""
        self.id = transaction_data.get('id')
        self.user_id = transaction_data.get('user_id')
        self.category_id = transaction_data.get('category_id')
        self.amount = float(transaction_data.get('amount', 0))
        self.description = transaction_data.get('description')
        self.transaction_date = transaction_data.get('transaction_date')
        self.type = transaction_data.get('type')  # 'income' or 'expense'
        self.notes = transaction_data.get('notes')
        self.is_recurring = transaction_data.get('is_recurring', False)
        self.recurring_id = transaction_data.get('recurring_id')
        self.created_at = transaction_data.get('created_at')
        self.updated_at = transaction_data.get('updated_at')
        
        # Extra fields from joins
        self.category_name = transaction_data.get('category_name')
        self.category_icon = transaction_data.get('category_icon')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat() if isinstance(self.transaction_date, date) else self.transaction_date,
            'type': self.type,
            'notes': self.notes,
            'is_recurring': self.is_recurring,
            'recurring_id': self.recurring_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'category_name': self.category_name,
            'category_icon': self.category_icon,
        }
    
    @staticmethod
    def create(user_id: int, category_id: int, amount: float, description: str,
               trans_type: str, transaction_date: Optional[date] = None,
               notes: Optional[str] = None, is_recurring: bool = False,
               recurring_id: Optional[int] = None) -> Optional['Transaction']:
        """Create a new transaction.
        
        Args:
            user_id: User ID
            category_id: Category ID
            amount: Transaction amount
            description: Transaction description
            trans_type: Transaction type ('income' or 'expense')
            transaction_date: Date of transaction (defaults to today)
            notes: Additional notes
            is_recurring: Whether this is from recurring transaction
            recurring_id: ID of recurring transaction if applicable
            
        Returns:
            Transaction instance or None if creation failed
        """
        if transaction_date is None:
            transaction_date = today_jakarta()
        
        query = """
            INSERT INTO transactions 
            (user_id, category_id, amount, description, transaction_date, type, notes, is_recurring, recurring_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query, (
                    user_id, category_id, amount, description, transaction_date,
                    trans_type, notes, is_recurring, recurring_id
                ))
                transaction_id = cursor.lastrowid
            
            logger.info(f"Created transaction: {trans_type} {amount} for user {user_id}")
            return Transaction.get_by_id(transaction_id)
        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            return None
    
    @staticmethod
    def get_by_id(transaction_id: int) -> Optional['Transaction']:
        """Get transaction by ID with category info.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction instance or None if not found
        """
        query = """
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = %s
        """
        result = DatabaseConnection.execute_query(query, (transaction_id,), fetch_one=True, commit=False)
        
        if result:
            return Transaction(result)
        return None
    
    @staticmethod
    def get_by_user(user_id: int, limit: int = 10, offset: int = 0,
                   start_date: Optional[date] = None, end_date: Optional[date] = None,
                   trans_type: Optional[str] = None) -> List['Transaction']:
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
        query = """
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND t.transaction_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND t.transaction_date <= %s"
            params.append(end_date)
        
        if trans_type:
            query += " AND t.type = %s"
            params.append(trans_type)
        
        query += " ORDER BY t.transaction_date DESC, t.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = DatabaseConnection.execute_query(query, tuple(params), commit=False)
        return [Transaction(row) for row in results]
    
    @staticmethod
    def get_count(user_id: int, start_date: Optional[date] = None,
                  end_date: Optional[date] = None, trans_type: Optional[str] = None) -> int:
        """Get total count of transactions for a user with optional filters."""
        query = "SELECT COUNT(*) as cnt FROM transactions t WHERE t.user_id = %s"
        params: List[Any] = [user_id]
        if start_date:
            query += " AND t.transaction_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND t.transaction_date <= %s"
            params.append(end_date)
        if trans_type:
            query += " AND t.type = %s"
            params.append(trans_type)
        result = DatabaseConnection.execute_query(query, tuple(params), fetch_one=True, commit=False)
        return int(result['cnt']) if result else 0
    
    @staticmethod
    def get_today(user_id: int) -> List['Transaction']:
        """Get today's transactions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Transaction instances
        """
        today = today_jakarta()
        return Transaction.get_by_user(user_id, start_date=today, end_date=today, limit=100)
    
    @staticmethod
    def get_by_date_range(user_id: int, start_date: date, end_date: date) -> List['Transaction']:
        """Get transactions within date range.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of Transaction instances
        """
        return Transaction.get_by_user(user_id, start_date=start_date, end_date=end_date, limit=1000)
    
    @staticmethod
    def get_by_category(user_id: int, category_id: int, start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> List['Transaction']:
        """Get transactions for a specific category.
        
        Args:
            user_id: User ID
            category_id: Category ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of Transaction instances
        """
        query = """
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s AND t.category_id = %s
        """
        params = [user_id, category_id]
        
        if start_date:
            query += " AND t.transaction_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND t.transaction_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY t.transaction_date DESC"
        
        results = DatabaseConnection.execute_query(query, tuple(params), commit=False)
        return [Transaction(row) for row in results]
    
    def update(self, **kwargs) -> bool:
        """Update transaction information.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        allowed_fields = ['category_id', 'amount', 'description', 'transaction_date', 'notes', 'type']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            return False
        
        values.append(self.id)
        query = f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(values))
            
            # Update instance
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(self, field, value)
            
            logger.info(f"Updated transaction: {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update transaction: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete transaction.
        
        Returns:
            True if deletion successful, False otherwise
        """
        query = "DELETE FROM transactions WHERE id = %s"
        try:
            DatabaseConnection.execute_query(query, (self.id,))
            logger.info(f"Deleted transaction: {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete transaction: {e}")
            return False
    
    @staticmethod
    def get_balance(user_id: int, start_date: Optional[date] = None,
                   end_date: Optional[date] = None) -> Dict[str, float]:
        """Calculate balance for a user.
        
        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with income, expense, and balance
        """
        query = """
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
            FROM transactions
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND transaction_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND transaction_date <= %s"
            params.append(end_date)
        
        result = DatabaseConnection.execute_query(query, tuple(params), fetch_one=True, commit=False)
        
        income = float(result['total_income'] or 0)
        expense = float(result['total_expense'] or 0)
        
        return {
            'income': income,
            'expense': expense,
            'balance': income - expense
        }
    
    @staticmethod
    def count(user_id: int) -> int:
        """Get total number of transactions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Count of transactions
        """
        query = "SELECT COUNT(*) as count FROM transactions WHERE user_id = %s"
        result = DatabaseConnection.execute_query(query, (user_id,), fetch_one=True, commit=False)
        
        return result['count'] if result else 0

    @staticmethod
    def get_date_bounds(user_id: int) -> Dict[str, Optional[date]]:
        """Get oldest and newest transaction dates for a user."""
        query = """
            SELECT
                MIN(transaction_date) AS oldest_date,
                MAX(transaction_date) AS newest_date
            FROM transactions
            WHERE user_id = %s
        """
        result = DatabaseConnection.execute_query(query, (user_id,), fetch_one=True, commit=False) or {}
        return {
            "oldest_date": result.get("oldest_date"),
            "newest_date": result.get("newest_date"),
        }
