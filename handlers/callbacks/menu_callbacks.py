"""Menu and cancel callbacks."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils.decorators import authenticated, error_handler

logger = logging.getLogger(__name__)


@error_handler
@authenticated
async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle cancel callback."""
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("❌ Dibatalkan.")
    context.user_data.clear()


@error_handler
@authenticated
async def handle_menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle main menu callbacks (saldo, report, categories, budget, recurring, history, help)."""
    query = update.callback_query
    await query.answer()

    from utils.formatters import Formatter
    from utils.keyboards import Keyboards
    from services.category_service import CategoryService
    from services.transaction_service import TransactionService

    action = query.data.replace("menu_", "")

    if action == "saldo":
        balance_data = TransactionService.get_balance(user.id)
        balance_icon = "✅" if balance_data["balance"] >= 0 else "⚠️"
        message = "SALDO SEKARANG\n\n"
        message += f"Total Pemasukan: {Formatter.format_currency(balance_data['income'])}\n"
        message += f"Total Pengeluaran: {Formatter.format_currency(balance_data['expense'])}\n"
        message += f"{balance_icon} Saldo: {Formatter.format_currency(balance_data['balance'])}"
        await query.message.edit_text(message)
    elif action == "report":
        await query.message.edit_text(
            "Pilih periode laporan:",
            reply_markup=Keyboards.report_period_selection(),
        )
    elif action == "categories":
        categories = CategoryService.get_categories(user.id)
        if not categories:
            await query.message.edit_text("Tidak ada kategori.")
            return
        income_cats = [c for c in categories if c.type == "income"]
        expense_cats = [c for c in categories if c.type == "expense"]
        message = "KATEGORI ANDA\n\n"
        message += "PEMASUKAN:\n"
        for cat in income_cats:
            message += f"  {cat.name}\n"
        message += "\nPENGELUARAN:\n"
        for cat in expense_cats:
            message += f"  {cat.name}\n"
        message += "\nGunakan /addcategory untuk menambah kategori baru."
        await query.message.edit_text(message)
    elif action == "budget":
        await query.message.edit_text(
            "BUDGET MANAGEMENT\n\n"
            "Gunakan:\n"
            "• /budget - Lihat semua budget\n"
            "• /setbudget - Atur budget baru\n"
            "• /budgetstatus - Status budget"
        )
    elif action == "recurring":
        await query.message.edit_text(
            "TRANSAKSI BERULANG\n\n"
            "Gunakan:\n"
            "• /recurring - Lihat transaksi berulang\n"
            "• /addrecurring - Tambah transaksi berulang"
        )
    elif action == "history":
        await query.message.edit_text(
            "Pilih periode untuk melihat riwayat:",
            reply_markup=Keyboards.report_period_selection(),
        )
    elif action == "help":
        await query.message.reply_text("📚 Panduan akan ditampilkan...")
