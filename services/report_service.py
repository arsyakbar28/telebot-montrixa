"""Report service for generating statistics and analytics."""

from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from models.transaction import Transaction
from config.database import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating reports and analytics."""
    
    @staticmethod
    def get_summary(user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get financial summary for a date range.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with summary data
        """
        # Get balance
        balance_data = Transaction.get_balance(user_id, start_date, end_date)
        
        # Get transaction count
        transactions = Transaction.get_by_date_range(user_id, start_date, end_date)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_income': balance_data['income'],
            'total_expense': balance_data['expense'],
            'balance': balance_data['balance'],
            'transaction_count': len(transactions),
            'income_count': len([t for t in transactions if t.type == 'income']),
            'expense_count': len([t for t in transactions if t.type == 'expense']),
        }
    
    @staticmethod
    def get_monthly_summary(user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Get monthly summary.
        
        Args:
            user_id: User ID
            year: Year
            month: Month
            
        Returns:
            Dictionary with monthly summary
        """
        start_date = date(year, month, 1)
        
        # Calculate last day of month
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        summary = ReportService.get_summary(user_id, start_date, end_date)
        summary['month'] = month
        summary['year'] = year
        
        # Add category breakdown
        summary['expense_by_category'] = ReportService.get_expense_by_category(
            user_id, start_date, end_date
        )
        summary['income_by_category'] = ReportService.get_income_by_category(
            user_id, start_date, end_date
        )
        
        return summary
    
    @staticmethod
    def get_current_month_summary(user_id: int) -> Dict[str, Any]:
        """Get current month summary.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with current month summary
        """
        today = date.today()
        return ReportService.get_monthly_summary(user_id, today.year, today.month)
    
    @staticmethod
    def get_expense_by_category(user_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get expense breakdown by category.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of category breakdowns
        """
        query = """
            SELECT 
                c.id as category_id,
                c.name as category_name,
                c.icon as category_icon,
                SUM(t.amount) as total_amount,
                COUNT(t.id) as transaction_count
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s 
            AND t.type = 'expense'
            AND t.transaction_date >= %s 
            AND t.transaction_date <= %s
            GROUP BY c.id, c.name, c.icon
            ORDER BY total_amount DESC
        """
        
        results = DatabaseConnection.execute_query(
            query, (user_id, start_date, end_date), commit=False
        )
        
        # Calculate total for percentage
        total_expense = float(sum(float(row['total_amount']) for row in results))
        
        breakdown = []
        for row in results:
            amount = float(row['total_amount'])
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            
            breakdown.append({
                'category_id': row['category_id'],
                'category_name': row['category_name'],
                'category_icon': row['category_icon'],
                'total_amount': amount,
                'transaction_count': row['transaction_count'],
                'percentage': percentage,
            })
        
        return breakdown
    
    @staticmethod
    def get_income_by_category(user_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get income breakdown by category.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of category breakdowns
        """
        query = """
            SELECT 
                c.id as category_id,
                c.name as category_name,
                c.icon as category_icon,
                SUM(t.amount) as total_amount,
                COUNT(t.id) as transaction_count
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s 
            AND t.type = 'income'
            AND t.transaction_date >= %s 
            AND t.transaction_date <= %s
            GROUP BY c.id, c.name, c.icon
            ORDER BY total_amount DESC
        """
        
        results = DatabaseConnection.execute_query(
            query, (user_id, start_date, end_date), commit=False
        )
        
        # Calculate total for percentage
        total_income = float(sum(float(row['total_amount']) for row in results))
        
        breakdown = []
        for row in results:
            amount = float(row['total_amount'])
            percentage = (amount / total_income * 100) if total_income > 0 else 0
            
            breakdown.append({
                'category_id': row['category_id'],
                'category_name': row['category_name'],
                'category_icon': row['category_icon'],
                'total_amount': amount,
                'transaction_count': row['transaction_count'],
                'percentage': percentage,
            })
        
        return breakdown
    
    @staticmethod
    def get_daily_trend(user_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get daily income/expense trend.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of daily data
        """
        query = """
            SELECT 
                transaction_date,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE user_id = %s 
            AND transaction_date >= %s 
            AND transaction_date <= %s
            GROUP BY transaction_date
            ORDER BY transaction_date ASC
        """
        
        results = DatabaseConnection.execute_query(
            query, (user_id, start_date, end_date), commit=False
        )
        
        return [
            {
                'date': row['transaction_date'],
                'income': float(row['income']),
                'expense': float(row['expense']),
                'net': float(row['income']) - float(row['expense']),
            }
            for row in results
        ]
    
    @staticmethod
    def export_to_csv(user_id: int, start_date: date, end_date: date) -> str:
        """Export transactions to CSV format.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            CSV string
        """
        transactions = Transaction.get_by_date_range(user_id, start_date, end_date)
        
        # Build CSV
        csv_lines = [
            "Date,Type,Category,Amount,Description,Notes"
        ]
        
        for trans in transactions:
            date_str = trans.transaction_date.strftime('%Y-%m-%d') if isinstance(trans.transaction_date, date) else str(trans.transaction_date)
            category_name = trans.category_name or 'Unknown'
            description = (trans.description or '').replace(',', ';').replace('\n', ' ')
            notes = (trans.notes or '').replace(',', ';').replace('\n', ' ')
            
            csv_lines.append(
                f"{date_str},{trans.type},{category_name},{trans.amount},{description},{notes}"
            )
        
        return '\n'.join(csv_lines)
