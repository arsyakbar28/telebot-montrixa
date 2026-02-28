"""Formatting utilities for numbers, dates, and messages."""

from datetime import date, datetime
from typing import Any, Optional
import locale


class Formatter:
    """Utility class for formatting data."""
    
    @staticmethod
    def format_currency(amount: float, currency: str = 'IDR') -> str:
        """Format amount as currency.
        
        Args:
            amount: Amount to format
            currency: Currency code (default: IDR)
            
        Returns:
            Formatted currency string
        """
        if currency == 'IDR':
            # Indonesian Rupiah format: Rp 1.500.000
            formatted = f"{amount:,.0f}".replace(',', '.')
            return f"Rp {formatted}"
        else:
            # Default format
            return f"{currency} {amount:,.2f}"
    
    @staticmethod
    def format_date(date_obj: date, format_str: str = '%d/%m/%Y') -> str:
        """Format date object.
        
        Args:
            date_obj: Date object to format
            format_str: Format string
            
        Returns:
            Formatted date string
        """
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime(format_str)
    
    @staticmethod
    def format_date_relative(date_obj: date) -> str:
        """Format date relative to today.
        
        Args:
            date_obj: Date object
            
        Returns:
            Relative date string
        """
        today = date.today()
        
        if date_obj == today:
            return "Hari ini"
        elif date_obj == today - timedelta(days=1):
            return "Kemarin"
        elif date_obj == today + timedelta(days=1):
            return "Besok"
        elif date_obj.year == today.year:
            # Same year, show day and month
            return date_obj.strftime('%d %b')
        else:
            return date_obj.strftime('%d %b %Y')
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage value.
        
        Args:
            value: Percentage value
            decimals: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_transaction_message(transaction: Any) -> str:
        """Format transaction for display.
        
        Args:
            transaction: Transaction object
            
        Returns:
            Formatted message string
        """
        sign = '+' if transaction.type == 'income' else '-'
        amount_str = Formatter.format_currency(transaction.amount)
        category = transaction.category_name
        date_str = Formatter.format_date_relative(transaction.transaction_date)
        
        msg = f"{sign}{amount_str}\n"
        msg += f"{category} • {transaction.description} • {date_str}"
        
        if transaction.notes:
            msg += f"\nCatatan: {transaction.notes}"
        
        return msg
    
    @staticmethod
    def format_budget_status(budget_data: dict) -> str:
        """Format budget status for display.
        
        Args:
            budget_data: Budget status dictionary
            
        Returns:
            Formatted budget status string
        """
        icon = budget_data['status_icon']
        category = budget_data['category_name']
        spent = Formatter.format_currency(budget_data['spent_amount'])
        budget = Formatter.format_currency(budget_data['budget_amount'])
        percentage = Formatter.format_percentage(budget_data['percentage'])
        remaining = Formatter.format_currency(budget_data['remaining_amount'])
        
        msg = f"{icon} {category}\n"
        msg += f"{spent} / {budget} ({percentage})\n"
        msg += f"Sisa: {remaining}"
        
        return msg
    
    @staticmethod
    def format_period(period: str) -> str:
        """Format period name in Indonesian.
        
        Args:
            period: Period code ('daily', 'weekly', 'monthly')
            
        Returns:
            Indonesian period name
        """
        period_map = {
            'daily': 'Harian',
            'weekly': 'Mingguan',
            'monthly': 'Bulanan',
        }
        return period_map.get(period, period)
    
    @staticmethod
    def format_summary(summary: dict) -> str:
        """Format financial summary for display.
        
        Args:
            summary: Summary dictionary
            
        Returns:
            Formatted summary string
        """
        income = Formatter.format_currency(summary['total_income'])
        expense = Formatter.format_currency(summary['total_expense'])
        balance = Formatter.format_currency(summary['balance'])
        
        balance_icon = '✅' if summary['balance'] >= 0 else '⚠️'
        
        msg = "RINGKASAN KEUANGAN\n\n"
        msg += f"Pemasukan: {income}\n"
        msg += f"Pengeluaran: {expense}\n"
        msg += f"{balance_icon} Saldo: {balance}\n"
        msg += f"\nTotal: {summary['transaction_count']} transaksi"
        
        return msg


# Import timedelta for relative date formatting
from datetime import timedelta
