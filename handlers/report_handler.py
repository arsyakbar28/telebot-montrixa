"""Report and analytics handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import authenticated, error_handler
from utils.formatters import Formatter
from services.report_service import ReportService
from services.transaction_service import TransactionService
from datetime import date
import logging

logger = logging.getLogger(__name__)


@error_handler
@authenticated
async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /summary command - show current month summary.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    summary = ReportService.get_current_month_summary(user.id)
    
    message = f"RINGKASAN {summary['month']}/{summary['year']}\n\n"
    message += f"Pemasukan: {Formatter.format_currency(summary['total_income'])}\n"
    message += f"Pengeluaran: {Formatter.format_currency(summary['total_expense'])}\n"
    
    balance_icon = '✅' if summary['balance'] >= 0 else '⚠️'
    message += f"{balance_icon} Saldo: {Formatter.format_currency(summary['balance'])}\n"
    message += f"\nTransaksi: {summary['transaction_count']}\n"
    
    # Top spending categories
    if summary['expense_by_category']:
        message += "\nTOP PENGELUARAN:\n"
        for i, cat in enumerate(summary['expense_by_category'][:5], 1):
            message += f"{i}. {cat['category_name']} - "
            message += f"{Formatter.format_currency(cat['total_amount'])} "
            message += f"({Formatter.format_percentage(cat['percentage'])})\n"
    
    message += "\nGunakan /report untuk laporan lengkap."
    
    await update.message.reply_text(message)


@error_handler
@authenticated
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /report command - generate detailed report.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    from utils.keyboards import Keyboards
    
    await update.message.reply_text(
        "Pilih periode untuk laporan:",
        reply_markup=Keyboards.report_period_selection()
    )


@error_handler
@authenticated
async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /export command - export data to CSV.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    from utils.keyboards import Keyboards
    
    await update.message.reply_text(
        "Pilih periode untuk export:",
        reply_markup=Keyboards.report_period_selection()
    )


@error_handler
@authenticated
async def handle_report_period(update: Update, context: ContextTypes.DEFAULT_TYPE, user, period: str):
    """Generate report for specified period.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
        period: Period string ('today', '7d', '30d', 'this_month', 'last_month')
    """
    # Calculate date range
    transactions = TransactionService.get_transactions_by_period(user.id, period)
    
    if not transactions:
        await update.callback_query.message.edit_text(
            f"Tidak ada transaksi untuk periode ini."
        )
        return
    
    # Get first and last transaction dates
    start_date = min(t.transaction_date for t in transactions)
    end_date = max(t.transaction_date for t in transactions)
    
    # Get summary
    summary = ReportService.get_summary(user.id, start_date, end_date)
    
    # Get category breakdown
    expense_by_cat = ReportService.get_expense_by_category(user.id, start_date, end_date)
    income_by_cat = ReportService.get_income_by_category(user.id, start_date, end_date)
    
    # Format message
    message = f"LAPORAN KEUANGAN\n"
    message += f"{Formatter.format_date(start_date)} - {Formatter.format_date(end_date)}\n\n"
    
    message += f"Pemasukan: {Formatter.format_currency(summary['total_income'])}\n"
    message += f"Pengeluaran: {Formatter.format_currency(summary['total_expense'])}\n"
    
    balance_icon = '✅' if summary['balance'] >= 0 else '⚠️'
    message += f"{balance_icon} Saldo: {Formatter.format_currency(summary['balance'])}\n"
    message += f"\nTotal: {summary['transaction_count']} transaksi\n"
    
    # Expense breakdown
    if expense_by_cat:
        message += "\nPENGELUARAN PER KATEGORI:\n"
        for cat in expense_by_cat[:10]:  # Top 10
            message += f"  {cat['category_name']}: "
            message += f"{Formatter.format_currency(cat['total_amount'])} "
            message += f"({Formatter.format_percentage(cat['percentage'])})\n"
    
    # Income breakdown
    if income_by_cat:
        message += "\nPEMASUKAN PER KATEGORI:\n"
        for cat in income_by_cat[:10]:  # Top 10
            message += f"  {cat['category_name']}: "
            message += f"{Formatter.format_currency(cat['total_amount'])} "
            message += f"({Formatter.format_percentage(cat['percentage'])})\n"
    
    await update.callback_query.message.edit_text(message)
