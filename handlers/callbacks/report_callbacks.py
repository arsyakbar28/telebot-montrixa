"""Report period selection callbacks."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils.decorators import authenticated, error_handler
from utils.formatters import Formatter
from services.report_service import ReportService
from services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


@error_handler
@authenticated
async def handle_report_period(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle report period selection callback."""
    query = update.callback_query
    await query.answer()

    period_map = {
        "report_today": "today",
        "report_7d": "7d",
        "report_30d": "30d",
        "report_this_month": "this_month",
        "report_last_month": "last_month",
    }

    period = period_map.get(query.data)
    if not period:
        await query.message.edit_text("❌ Periode tidak valid.")
        return

    transactions = TransactionService.get_transactions_by_period(user.id, period)
    if not transactions:
        await query.message.edit_text("Tidak ada transaksi untuk periode ini.")
        return

    start_date = min(t.transaction_date for t in transactions)
    end_date = max(t.transaction_date for t in transactions)
    summary = ReportService.get_summary(user.id, start_date, end_date)
    expense_by_cat = ReportService.get_expense_by_category(user.id, start_date, end_date)
    income_by_cat = ReportService.get_income_by_category(user.id, start_date, end_date)

    message = "LAPORAN KEUANGAN\n"
    message += f"{Formatter.format_date(start_date)} - {Formatter.format_date(end_date)}\n\n"
    message += f"Pemasukan: {Formatter.format_currency(summary['total_income'])}\n"
    message += f"Pengeluaran: {Formatter.format_currency(summary['total_expense'])}\n"
    balance_icon = "✅" if summary["balance"] >= 0 else "⚠️"
    message += f"{balance_icon} Saldo: {Formatter.format_currency(summary['balance'])}\n"
    message += f"\nTotal: {summary['transaction_count']} transaksi\n"

    if expense_by_cat:
        message += "\nPENGELUARAN PER KATEGORI:\n"
        for cat in expense_by_cat[:10]:
            message += f"  {cat['category_name']}: "
            message += f"{Formatter.format_currency(cat['total_amount'])} "
            message += f"({Formatter.format_percentage(cat['percentage'])})\n"
    if income_by_cat:
        message += "\nPEMASUKAN PER KATEGORI:\n"
        for cat in income_by_cat[:10]:
            message += f"  {cat['category_name']}: "
            message += f"{Formatter.format_currency(cat['total_amount'])} "
            message += f"({Formatter.format_percentage(cat['percentage'])})\n"

    await query.message.edit_text(message)
