"""Recurring transaction handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import authenticated, error_handler
from utils.formatters import Formatter
from utils.validators import Validator
from services.recurring_service import RecurringService
from services.category_service import CategoryService
import logging

logger = logging.getLogger(__name__)


@error_handler
@authenticated
async def recurring_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /recurring command - show all recurring transactions.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    recurring_list = RecurringService.get_user_recurring(user.id)
    
    if not recurring_list:
        await update.message.reply_text(
            "Belum ada transaksi berulang.\n\n"
            "Gunakan /addrecurring untuk menambah transaksi berulang."
        )
        return
    
    message = "TRANSAKSI BERULANG\n\n"
    
    for recurring in recurring_list:
        status_icon = "✅" if recurring.is_active else "⏸"
        sign = "+" if recurring.type == "income" else "-"
        
        message += f"{status_icon} {sign}{Formatter.format_currency(recurring.amount)}\n"
        message += f"{recurring.category_name}\n"
        message += f"{recurring.description}\n"
        message += f"Frekuensi: {Formatter.format_period(recurring.frequency)}\n"
        message += f"Berikutnya: {Formatter.format_date(recurring.next_run_date)}\n"
        message += "─" * 30 + "\n"
    
    message += "\nGunakan /pauserecurring [id] atau /deleterecurring [id]"
    
    await update.message.reply_text(message)


@error_handler
@authenticated
async def add_recurring_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /addrecurring command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    args = Validator.parse_command_args(update.message.text)
    
    if len(args) < 4:
        await update.message.reply_text(
            "❌ Format salah\n\n"
            "Gunakan: /addrecurring [tipe] [jumlah] [keterangan] [frekuensi]\n"
            "Tipe: income/expense (pemasukan/pengeluaran)\n"
            "Frekuensi: harian/mingguan/bulanan\n\n"
            "Contoh:\n"
            "• /addrecurring expense 1000000 \"Sewa kost\" bulanan\n"
            "• /addrecurring income 5000000 \"Gaji\" bulanan"
        )
        return
    
    # Parse arguments
    type_str = args[0]
    amount_str = args[1]
    frequency_str = args[-1]
    description = ' '.join(args[2:-1])
    
    # Validate type
    is_valid, trans_type, error = Validator.validate_transaction_type(type_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Validate amount
    is_valid, amount, error = Validator.validate_amount(amount_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Validate description
    is_valid, description, error = Validator.validate_description(description)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Validate frequency
    is_valid, frequency, error = Validator.validate_frequency(frequency_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Get categories and let user choose
    if trans_type == 'income':
        categories = CategoryService.get_income_categories(user.id)
    else:
        categories = CategoryService.get_expense_categories(user.id)
    
    if not categories:
        await update.message.reply_text("❌ Tidak ada kategori. Hubungi admin.")
        return
    
    # For now, use first category (TODO: add category selection)
    category = categories[0]
    
    # Create recurring transaction
    recurring = RecurringService.create_recurring(
        user.id, category.id, amount, description, trans_type, frequency
    )
    
    if not recurring:
        await update.message.reply_text("❌ Gagal membuat transaksi berulang. Silakan coba lagi.")
        return
    
    type_name = "pemasukan" if trans_type == "income" else "pengeluaran"
    sign = "+" if trans_type == "income" else "-"
    
    await update.message.reply_text(
        f"✅ Transaksi berulang berhasil dibuat\n\n"
        f"{sign}{Formatter.format_currency(amount)}\n"
        f"{category.name}\n"
        f"{description}\n"
        f"Frekuensi: {Formatter.format_period(frequency)}\n"
        f"Mulai: {Formatter.format_date(recurring.start_date)}\n\n"
        f"Transaksi akan otomatis dicatat setiap {Formatter.format_period(frequency).lower()}."
    )
