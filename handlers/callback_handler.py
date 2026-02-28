"""Callback query handlers for inline keyboards."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import authenticated, error_handler
from utils.formatters import Formatter
from utils.keyboards import Keyboards
from utils.validators import Validator
from services.transaction_service import TransactionService
from services.budget_service import BudgetService
from services.category_service import CategoryService
from services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

# Conversation states for "klik menu -> ketik nominal -> klik kategori"
WAITING_AMOUNT, SELECTING_CATEGORY = 0, 1


async def _do_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Core logic for category selection (shared by command flow and conversation flow)."""
    query = update.callback_query
    await query.answer()
    pending = context.user_data.get('pending_transaction')
    if not pending:
        await query.message.edit_text("❌ Data transaksi tidak ditemukan. Silakan coba lagi.")
        return
    callback_parts = query.data.split('_')
    if len(callback_parts) != 3:
        await query.message.edit_text("❌ Data tidak valid.")
        return
    trans_type = callback_parts[0]
    category_id = int(callback_parts[2])
    transaction = TransactionService.create_transaction(
        user_id=user.id,
        category_id=category_id,
        amount=pending['amount'],
        description=pending['description'],
        trans_type=pending['type']
    )
    if not transaction:
        await query.message.edit_text("❌ Gagal menyimpan transaksi. Silakan coba lagi.")
        return
    message = "✅ Transaksi berhasil dicatat!\n\n"
    message += Formatter.format_transaction_message(transaction)
    if transaction.type == 'expense':
        alert = BudgetService.check_budget_alerts(user.id, category_id)
        if alert:
            message += f"\n\n⚠️ PERINGATAN BUDGET\n"
            message += f"{alert['category_name']}\n"
            message += f"{Formatter.format_currency(alert['spent_amount'])} / "
            message += f"{Formatter.format_currency(alert['budget_amount'])} "
            message += f"({Formatter.format_percentage(alert['percentage'])})\n"
            if alert['alert_type'] == 'critical':
                message += "Budget sudah melampaui batas!"
            elif alert['alert_type'] == 'danger':
                message += "Budget hampir habis!"
            else:
                message += "Hati-hati, budget mulai menipis!"
            BudgetService.log_alert(
                user.id, alert['budget_id'], alert['alert_type'],
                alert['percentage'], alert['spent_amount'], alert['budget_amount']
            )
    await query.message.edit_text(message)
    context.user_data.pop('pending_transaction', None)


@error_handler
@authenticated
async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle category selection callback."""
    await _do_category_selection(update, context, user)


@error_handler
@authenticated
async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle cancel callback.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    query = update.callback_query
    await query.answer()
    
    await query.message.edit_text("❌ Dibatalkan.")
    
    # Clear any pending data
    context.user_data.clear()


@error_handler
@authenticated
async def handle_menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle main menu callbacks.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    query = update.callback_query
    await query.answer()
    
    action = query.data.replace('menu_', '')
    
    if action == 'saldo':
        balance_data = TransactionService.get_balance(user.id)
        balance_icon = '✅' if balance_data['balance'] >= 0 else '⚠️'
        message = "SALDO SEKARANG\n\n"
        message += f"Total Pemasukan: {Formatter.format_currency(balance_data['income'])}\n"
        message += f"Total Pengeluaran: {Formatter.format_currency(balance_data['expense'])}\n"
        message += f"{balance_icon} Saldo: {Formatter.format_currency(balance_data['balance'])}"
        await query.message.edit_text(message)
    # menu_income / menu_expense ditangani ConversationHandler (klik -> ketik nominal -> klik kategori)
    elif action == 'report':
        from utils.keyboards import Keyboards
        await query.message.edit_text(
            "Pilih periode laporan:",
            reply_markup=Keyboards.report_period_selection()
        )
    elif action == 'categories':
        from services.category_service import CategoryService
        categories = CategoryService.get_categories(user.id)
        
        if not categories:
            await query.message.edit_text("Tidak ada kategori.")
            return
        
        income_cats = [c for c in categories if c.type == 'income']
        expense_cats = [c for c in categories if c.type == 'expense']
        
        message = "KATEGORI ANDA\n\n"
        message += "PEMASUKAN:\n"
        for cat in income_cats:
            message += f"  {cat.name}\n"
        
        message += "\nPENGELUARAN:\n"
        for cat in expense_cats:
            message += f"  {cat.name}\n"
        
        message += "\nGunakan /addcategory untuk menambah kategori baru."
        
        await query.message.edit_text(message)
    elif action == 'budget':
        await query.message.edit_text(
            "BUDGET MANAGEMENT\n\n"
            "Gunakan:\n"
            "• /budget - Lihat semua budget\n"
            "• /setbudget - Atur budget baru\n"
            "• /budgetstatus - Status budget"
        )
    elif action == 'recurring':
        await query.message.edit_text(
            "TRANSAKSI BERULANG\n\n"
            "Gunakan:\n"
            "• /recurring - Lihat transaksi berulang\n"
            "• /addrecurring - Tambah transaksi berulang"
        )
    elif action == 'history':
        from utils.keyboards import Keyboards
        await query.message.edit_text(
            "Pilih periode untuk melihat riwayat:",
            reply_markup=Keyboards.report_period_selection()
        )
    elif action == 'help':
        from handlers.start_handler import help_command
        # Send help as new message
        await query.message.reply_text(
            "📚 Panduan akan ditampilkan..."
        )
        # Note: help_command will need to be modified to work without message.text


@error_handler
@authenticated
async def handle_report_period(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle report period selection callback.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    query = update.callback_query
    await query.answer()
    
    # Parse period from callback data: "report_today", "report_7d", etc
    period_map = {
        'report_today': 'today',
        'report_7d': '7d',
        'report_30d': '30d',
        'report_this_month': 'this_month',
        'report_last_month': 'last_month',
    }
    
    period = period_map.get(query.data)
    if not period:
        await query.message.edit_text("❌ Periode tidak valid.")
        return
    
    # Get transactions for period
    transactions = TransactionService.get_transactions_by_period(user.id, period)
    
    if not transactions:
        await query.message.edit_text(
            f"Tidak ada transaksi untuk periode ini."
        )
        return
    
    # Get first and last transaction dates
    start_date = min(t.transaction_date for t in transactions)
    end_date = max(t.transaction_date for t in transactions)
    
    # Get summary
    from services.report_service import ReportService
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
    
    await query.message.edit_text(message)


@error_handler
@authenticated
async def handle_delete_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle delete transaction callback.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    query = update.callback_query
    await query.answer()
    
    # Parse transaction ID from callback data
    if query.data.startswith('delete_trans_'):
        transaction_id = int(query.data.replace('delete_trans_', ''))
        
        # Get transaction details
        transaction = TransactionService.get_transaction(transaction_id)
        
        if not transaction or transaction.user_id != user.id:
            await query.message.edit_text("❌ Transaksi tidak ditemukan atau bukan milik Anda.")
            return
        
        # Show confirmation
        message = "⚠️ Yakin ingin menghapus transaksi ini?\n\n"
        message += Formatter.format_transaction_message(transaction)
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"confirm_delete_{transaction_id}"),
                InlineKeyboardButton("❌ Batal", callback_data="cancel")
            ]
        ]
        
        await query.message.edit_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data.startswith('confirm_delete_'):
        transaction_id = int(query.data.replace('confirm_delete_', ''))
        
        # Get transaction for details before deleting
        transaction = TransactionService.get_transaction(transaction_id)
        
        if not transaction or transaction.user_id != user.id:
            await query.message.edit_text("❌ Transaksi tidak ditemukan atau bukan milik Anda.")
            return
        
        # Delete the transaction
        success = TransactionService.delete_transaction(transaction_id)
        
        if success:
            sign = '+' if transaction.type == 'income' else '-'
            message = "✅ Transaksi berhasil dihapus\n\n"
            message += f"{sign}{Formatter.format_currency(transaction.amount)}\n"
            message += f"{transaction.category_name}\n"
            message += f"{transaction.description}\n"
            message += f"{Formatter.format_date_relative(transaction.transaction_date)}"
            
            await query.message.edit_text(message)
        else:
            await query.message.edit_text("❌ Gagal menghapus transaksi. Silakan coba lagi.")


# --- Alur "full klik": menu -> ketik nominal dan keterangan -> klik kategori ---

@error_handler
async def menu_income_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: user klik Pemasukan atau Pengeluaran di menu."""
    query = update.callback_query
    await query.answer()
    trans_type = 'income' if query.data == 'menu_income' else 'expense'
    context.user_data['pending_transaction'] = {'type': trans_type}
    label = "pemasukan" if trans_type == 'income' else "pengeluaran"
    keyboard = [[InlineKeyboardButton("❌ Batal", callback_data="cancel")]]
    await query.edit_message_text(
        f"📝 Catat {label}\n\nKetik nominal dan keterangan.\nContoh: 10000 makan siang",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_AMOUNT


def _get_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get or register user from update (for use inside conversation)."""
    telegram_user = update.effective_user
    if not telegram_user:
        return None
    return UserService.get_or_register(
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        language_code=telegram_user.language_code or 'id'
    )


@error_handler
async def receive_amount_from_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima nominal dan keterangan dari user (state WAITING_AMOUNT). Format: 10000 makan siang"""
    user = _get_user(update, context)
    if not user:
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END
    text = (update.message.text or "").strip()
    parts = text.split(maxsplit=1)
    amount_str = parts[0] if parts else ""
    description_str = (parts[1].strip() if len(parts) > 1 else "") or "-"
    is_valid, amount, error = Validator.validate_amount(amount_str)
    if not is_valid:
        await update.message.reply_text(
            f"❌ {error}\n\nKetik nominal dan keterangan.\nContoh: 10000 makan siang"
        )
        return WAITING_AMOUNT
    if description_str != "-":
        is_valid_desc, description_str, err_desc = Validator.validate_description(description_str)
        if not is_valid_desc:
            await update.message.reply_text(f"❌ {err_desc}\n\nContoh: 10000 makan siang")
            return WAITING_AMOUNT
    trans_type = context.user_data['pending_transaction']['type']
    categories = CategoryService.get_income_categories(user.id) if trans_type == 'income' else CategoryService.get_expense_categories(user.id)
    if not categories:
        await update.message.reply_text("❌ Tidak ada kategori. Gunakan /addcategory untuk menambah.")
        return ConversationHandler.END
    context.user_data['pending_transaction'] = {
        'amount': amount,
        'description': description_str,
        'type': trans_type
    }
    label = "pemasukan" if trans_type == 'income' else "pengeluaran"
    await update.message.reply_text(
        f"Pilih kategori untuk {label} {Formatter.format_currency(amount)} - {description_str}:",
        reply_markup=Keyboards.category_selection(categories, trans_type, trans_type)
    )
    return SELECTING_CATEGORY


@error_handler
async def category_selection_conversation_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Setelah user klik kategori, simpan transaksi dan akhiri conversation."""
    user = _get_user(update, context)
    if not user:
        await update.callback_query.message.edit_text("❌ Terjadi kesalahan.")
        return ConversationHandler.END
    await _do_category_selection(update, context, user)
    return ConversationHandler.END


@error_handler
async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batal di dalam alur conversation."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Dibatalkan.")
    context.user_data.clear()
    return ConversationHandler.END
