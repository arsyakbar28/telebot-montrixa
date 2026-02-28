"""Budget service for budget management and alerts."""

from typing import Optional, List, Dict, Any
from datetime import date
from models.budget import Budget
from models.category import Category
from config.settings import Settings
from config.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class BudgetService:
    """Service for budget-related operations."""
    
    @staticmethod
    def create_budget(user_id: int, category_id: int, amount: float,
                     period: str, start_date: Optional[date] = None) -> Optional[Budget]:
        """Create or update a budget.
        
        Args:
            user_id: User ID
            category_id: Category ID
            amount: Budget amount
            period: Budget period ('daily', 'weekly', 'monthly')
            start_date: Start date (defaults to today)
            
        Returns:
            Budget instance or None if creation failed
        """
        # Validate category belongs to user and is expense type
        category = Category.get_by_id(category_id)
        if not category or category.user_id != user_id:
            logger.error(f"Invalid category {category_id} for user {user_id}")
            return None
        
        if category.type != 'expense':
            logger.error(f"Budget can only be set for expense categories")
            return None
        
        return Budget.create(user_id, category_id, amount, period, start_date)
    
    @staticmethod
    def get_budget(budget_id: int) -> Optional[Budget]:
        """Get budget by ID.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Budget instance or None if not found
        """
        return Budget.get_by_id(budget_id)
    
    @staticmethod
    def get_user_budgets(user_id: int) -> List[Budget]:
        """Get all budgets for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Budget instances
        """
        return Budget.get_by_user(user_id)
    
    @staticmethod
    def get_budget_status(user_id: int) -> List[Dict[str, Any]]:
        """Get budget status with spending information.
        
        Args:
            user_id: User ID
            
        Returns:
            List of budget status dictionaries
        """
        budgets = Budget.get_by_user(user_id)
        status_list = []
        
        for budget in budgets:
            spent = budget.get_spent_amount()
            percentage = budget.get_percentage_used()
            remaining = budget.amount - spent
            
            # Determine status level
            if percentage >= Settings.BUDGET_CRITICAL_THRESHOLD:
                status = 'critical'
                icon = '🔴'
            elif percentage >= Settings.BUDGET_DANGER_THRESHOLD:
                status = 'danger'
                icon = '🟠'
            elif percentage >= Settings.BUDGET_WARNING_THRESHOLD:
                status = 'warning'
                icon = '🟡'
            else:
                status = 'ok'
                icon = '🟢'
            
            status_list.append({
                'budget_id': budget.id,
                'category_id': budget.category_id,
                'category_name': budget.category_name,
                'category_icon': budget.category_icon,
                'period': budget.period,
                'budget_amount': budget.amount,
                'spent_amount': spent,
                'remaining_amount': remaining,
                'percentage': percentage,
                'status': status,
                'status_icon': icon,
            })
        
        return status_list
    
    @staticmethod
    def update_budget(budget_id: int, **kwargs) -> bool:
        """Update a budget.
        
        Args:
            budget_id: Budget ID
            **kwargs: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        budget = Budget.get_by_id(budget_id)
        if not budget:
            logger.error(f"Budget not found: {budget_id}")
            return False
        
        return budget.update(**kwargs)
    
    @staticmethod
    def delete_budget(budget_id: int) -> bool:
        """Delete a budget.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        budget = Budget.get_by_id(budget_id)
        if not budget:
            logger.error(f"Budget not found: {budget_id}")
            return False
        
        return budget.delete()
    
    @staticmethod
    def check_budget_alerts(user_id: int, category_id: int) -> Optional[Dict[str, Any]]:
        """Check if budget alert should be sent for a category.
        
        Args:
            user_id: User ID
            category_id: Category ID
            
        Returns:
            Alert dictionary or None if no alert needed
        """
        # Get all active budgets for this category
        budgets = Budget.get_by_user(user_id)
        
        for budget in budgets:
            if budget.category_id != category_id:
                continue
            
            percentage = budget.get_percentage_used()
            spent = budget.get_spent_amount()
            
            # Check if alert should be sent
            alert_type = None
            
            if percentage >= Settings.BUDGET_CRITICAL_THRESHOLD and budget.alert_at_100:
                alert_type = 'critical'
            elif percentage >= Settings.BUDGET_DANGER_THRESHOLD and budget.alert_at_90:
                alert_type = 'danger'
            elif percentage >= Settings.BUDGET_WARNING_THRESHOLD and budget.alert_at_75:
                alert_type = 'warning'
            
            if alert_type:
                # Check if alert already sent today
                if not BudgetService._alert_sent_today(budget.id, alert_type):
                    return {
                        'budget_id': budget.id,
                        'category_name': budget.category_name,
                        'category_icon': budget.category_icon,
                        'period': budget.period,
                        'budget_amount': budget.amount,
                        'spent_amount': spent,
                        'percentage': percentage,
                        'alert_type': alert_type,
                    }
        
        return None
    
    @staticmethod
    def _alert_sent_today(budget_id: int, alert_type: str) -> bool:
        """Check if alert was already sent today.
        
        Args:
            budget_id: Budget ID
            alert_type: Alert type ('warning', 'danger', 'critical')
            
        Returns:
            True if alert already sent, False otherwise
        """
        query = """
            SELECT COUNT(*) as count
            FROM budget_alerts
            WHERE budget_id = %s AND alert_type = %s AND alert_date = %s
        """
        result = DatabaseConnection.execute_query(
            query, (budget_id, alert_type, date.today()),
            fetch_one=True, commit=False
        )
        
        return result['count'] > 0 if result else False
    
    @staticmethod
    def log_alert(user_id: int, budget_id: int, alert_type: str,
                 percentage: float, amount_spent: float, budget_amount: float) -> bool:
        """Log that an alert was sent.
        
        Args:
            user_id: User ID
            budget_id: Budget ID
            alert_type: Alert type
            percentage: Percentage used
            amount_spent: Amount spent
            budget_amount: Budget amount
            
        Returns:
            True if logging successful, False otherwise
        """
        query = """
            INSERT INTO budget_alerts 
            (user_id, budget_id, alert_type, percentage, amount_spent, budget_amount, alert_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            DatabaseConnection.execute_query(
                query, (user_id, budget_id, alert_type, percentage, amount_spent, budget_amount, date.today())
            )
            logger.info(f"Logged budget alert: {alert_type} for budget {budget_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to log budget alert: {e}")
            return False
