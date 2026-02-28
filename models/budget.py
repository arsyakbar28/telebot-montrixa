"""Budget model and database operations."""

from typing import Optional, Dict, Any, List
from datetime import date, datetime
from config.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class Budget:
    """Budget model for expense tracking and alerts."""
    
    def __init__(self, budget_data: Dict[str, Any]):
        """Initialize Budget from database row."""
        self.id = budget_data.get('id')
        self.user_id = budget_data.get('user_id')
        self.category_id = budget_data.get('category_id')
        self.amount = float(budget_data.get('amount', 0))
        self.period = budget_data.get('period')  # 'daily', 'weekly', 'monthly'
        self.start_date = budget_data.get('start_date')
        self.end_date = budget_data.get('end_date')
        self.is_active = budget_data.get('is_active', True)
        self.alert_at_75 = budget_data.get('alert_at_75', True)
        self.alert_at_90 = budget_data.get('alert_at_90', True)
        self.alert_at_100 = budget_data.get('alert_at_100', True)
        self.created_at = budget_data.get('created_at')
        self.updated_at = budget_data.get('updated_at')
        
        # Extra fields from joins
        self.category_name = budget_data.get('category_name')
        self.category_icon = budget_data.get('category_icon')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert budget to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'period': self.period,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date if self.end_date else None,
            'is_active': self.is_active,
            'alert_at_75': self.alert_at_75,
            'alert_at_90': self.alert_at_90,
            'alert_at_100': self.alert_at_100,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'category_name': self.category_name,
            'category_icon': self.category_icon,
        }
    
    @staticmethod
    def create(user_id: int, category_id: int, amount: float, period: str,
               start_date: Optional[date] = None) -> Optional['Budget']:
        """Create a new budget.
        
        Args:
            user_id: User ID
            category_id: Category ID
            amount: Budget amount
            period: Budget period ('daily', 'weekly', 'monthly')
            start_date: Start date (defaults to today)
            
        Returns:
            Budget instance or None if creation failed
        """
        if start_date is None:
            start_date = date.today()
        
        query = """
            INSERT INTO budgets (user_id, category_id, amount, period, start_date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE amount = %s, is_active = TRUE, updated_at = CURRENT_TIMESTAMP
        """
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query, (user_id, category_id, amount, period, start_date, amount))
                budget_id = cursor.lastrowid
            
            logger.info(f"Created/Updated budget for user {user_id}, category {category_id}")
            return Budget.get_by_user_category(user_id, category_id, period)
        except Exception as e:
            logger.error(f"Failed to create budget: {e}")
            return None
    
    @staticmethod
    def get_by_id(budget_id: int) -> Optional['Budget']:
        """Get budget by ID with category info.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Budget instance or None if not found
        """
        query = """
            SELECT b.*, c.name as category_name, c.icon as category_icon
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.id = %s
        """
        result = DatabaseConnection.execute_query(query, (budget_id,), fetch_one=True, commit=False)
        
        if result:
            return Budget(result)
        return None
    
    @staticmethod
    def get_by_user(user_id: int, include_inactive: bool = False) -> List['Budget']:
        """Get all budgets for a user.
        
        Args:
            user_id: User ID
            include_inactive: Include inactive budgets
            
        Returns:
            List of Budget instances
        """
        query = """
            SELECT b.*, c.name as category_name, c.icon as category_icon
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = %s
        """
        params = [user_id]
        
        if not include_inactive:
            query += " AND b.is_active = TRUE"
        
        query += " ORDER BY b.period, c.name"
        
        results = DatabaseConnection.execute_query(query, tuple(params), commit=False)
        return [Budget(row) for row in results]
    
    @staticmethod
    def get_by_user_category(user_id: int, category_id: int, period: str) -> Optional['Budget']:
        """Get budget for specific user, category, and period.
        
        Args:
            user_id: User ID
            category_id: Category ID
            period: Budget period
            
        Returns:
            Budget instance or None if not found
        """
        query = """
            SELECT b.*, c.name as category_name, c.icon as category_icon
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = %s AND b.category_id = %s AND b.period = %s AND b.is_active = TRUE
            ORDER BY b.start_date DESC
            LIMIT 1
        """
        result = DatabaseConnection.execute_query(
            query, (user_id, category_id, period), fetch_one=True, commit=False
        )
        
        if result:
            return Budget(result)
        return None
    
    def get_spent_amount(self, current_date: Optional[date] = None) -> float:
        """Calculate total spent for this budget in current period.
        
        Args:
            current_date: Date to calculate from (defaults to today)
            
        Returns:
            Total spent amount
        """
        if current_date is None:
            current_date = date.today()
        
        # Calculate period start date
        from datetime import timedelta
        
        if self.period == 'daily':
            period_start = current_date
        elif self.period == 'weekly':
            # Start of week (Monday)
            period_start = current_date - timedelta(days=current_date.weekday())
        else:  # monthly
            period_start = current_date.replace(day=1)
        
        query = """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE user_id = %s 
            AND category_id = %s 
            AND type = 'expense'
            AND transaction_date >= %s 
            AND transaction_date <= %s
        """
        
        result = DatabaseConnection.execute_query(
            query, (self.user_id, self.category_id, period_start, current_date),
            fetch_one=True, commit=False
        )
        
        return float(result['total']) if result else 0.0
    
    def get_percentage_used(self, current_date: Optional[date] = None) -> float:
        """Calculate percentage of budget used.
        
        Args:
            current_date: Date to calculate from (defaults to today)
            
        Returns:
            Percentage used (0-100+)
        """
        spent = self.get_spent_amount(current_date)
        if self.amount == 0:
            return 0.0
        return (spent / self.amount) * 100
    
    def update(self, **kwargs) -> bool:
        """Update budget information.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        allowed_fields = ['amount', 'is_active', 'alert_at_75', 'alert_at_90', 'alert_at_100']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            return False
        
        values.append(self.id)
        query = f"UPDATE budgets SET {', '.join(update_fields)} WHERE id = %s"
        
        try:
            DatabaseConnection.execute_query(query, tuple(values))
            
            # Update instance
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(self, field, value)
            
            logger.info(f"Updated budget: {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update budget: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete budget (soft delete).
        
        Returns:
            True if deletion successful, False otherwise
        """
        return self.update(is_active=False)
    
    @staticmethod
    def get_all_active() -> List['Budget']:
        """Get all active budgets across all users.
        
        Returns:
            List of Budget instances
        """
        query = """
            SELECT b.*, c.name as category_name, c.icon as category_icon
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.is_active = TRUE
            ORDER BY b.user_id, b.period
        """
        results = DatabaseConnection.execute_query(query, commit=False)
        return [Budget(row) for row in results]
