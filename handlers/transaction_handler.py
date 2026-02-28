"""Transaction command handlers."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import authenticated, error_handler
from utils.keyboards import Keyboards
from utils.formatters import Formatter
from utils.validators import Validator
from services.transaction_service import TransactionService
from services.category_service import CategoryService
from services.budget_service import BudgetService
import logging

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_CATEGORY, ENTERING_NOTES = range(2)


@error_handler
@authenticated
async def income_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /income command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    args = Validator.parse_command_args(update.message.text)
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Format salah\n\n"
            "Gunakan: /income [jumlah] [keterangan]\n"
            "Contoh: /income 5000000 gaji bulanan"
        )
        return
    
    # Parse amount
    amount_str = args[0]
    is_valid, amount, error = Validator.validate_amount(amount_str)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Get description (remaining args)
    description = ' '.join(args[1:])
    is_valid, description, error = Validator.validate_description(description)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Get income categories
    categories = CategoryService.get_income_categories(user.id)
    
    if not categories:
        await update.message.reply_text(
            "❌ Tidak ada kategori pemasukan. Hubungi admin."
        )
        return
    
    # Store data in context for later
    context.user_data['pending_transaction'] = {
        'amount': amount,
        'description': description,
        'type': 'income'
    }
    
    # Show category selection
    await update.message.reply_text(
        f"Pilih kategori untuk pemasukan {Formatter.format_currency(amount)}:",
        reply_markup=Keyboards.category_selection(categories, 'income', 'income')
    )
    
    return SELECTING_CATEGORY


@error_handler
@authenticated
async def expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /expense command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    args = Validator.parse_command_args(update.message.text)
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Format salah\n\n"
            "Gunakan: /expense [jumlah] [keterangan]\n"
            "Contoh: /expense 50000 makan siang"
        )
        return
    
    # Parse amount
    amount_str = args[0]
    is_valid, amount, error = Validator.validate_amount(amount_str)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Get description
    description = ' '.join(args[1:])
    is_valid, description, error = Validator.validate_description(description)
    
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Get expense categories
    categories = CategoryService.get_expense_categories(user.id)
    
    if not categories:
        await update.message.reply_text(
            "❌ Tidak ada kategori pengeluaran. Hubungi admin."
        )
        return
    
    # Store data in context
    context.user_data['pending_transaction'] = {
        'amount': amount,
        'description': description,
        'type': 'expense'
    }
    
    # Show category selection
    await update.message.reply_text(
        f"Pilih kategori untuk pengeluaran {Formatter.format_currency(amount)}:",
        reply_markup=Keyboards.category_selection(categories, 'expense', 'expense')
    )
    
    return SELECTING_CATEGORY


@error_handler
@authenticated
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /list command - show today's transactions.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    transactions = TransactionService.get_today_transactions(user.id)
    
    if not transactions:
        await update.message.reply_text(
            "Belum ada transaksi hari ini."
        )
        return
    
    # Format message
    message = "TRANSAKSI HARI INI\n\n"
    
    income_total = 0
    expense_total = 0
    
    for trans in transactions:
        message += Formatter.format_transaction_message(trans) + "\n"
        message += "─" * 30 + "\n"
        
        if trans.type == 'income':
            income_total += trans.amount
        else:
            expense_total += trans.amount
    
    # Add summary
    message += f"\nRINGKASAN:\n"
    message += f"Pemasukan: {Formatter.format_currency(income_total)}\n"
    message += f"Pengeluaran: {Formatter.format_currency(expense_total)}\n"
    message += f"Net: {Formatter.format_currency(income_total - expense_total)}"
    
    await update.message.reply_text(message)


@error_handler
@authenticated
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /balance command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    balance_data = TransactionService.get_balance(user.id)
    
    balance_icon = '✅' if balance_data['balance'] >= 0 else '⚠️'
    
    message = "SALDO TOTAL\n\n"
    message += f"Total Pemasukan: {Formatter.format_currency(balance_data['income'])}\n"
    message += f"Total Pengeluaran: {Formatter.format_currency(balance_data['expense'])}\n"
    message += f"{balance_icon} Saldo: {Formatter.format_currency(balance_data['balance'])}"
    
    await update.message.reply_text(message)


@error_handler
@authenticated
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /history command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    await update.message.reply_text(
        "Pilih periode untuk melihat riwayat:",
        reply_markup=Keyboards.report_period_selection()
    )


@error_handler
@authenticated
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /delete command - show recent transactions with delete buttons.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    # Get last 10 transactions
    transactions = TransactionService.get_user_transactions(user.id, limit=10)
    
    if not transactions:
        await update.message.reply_text(
            "Belum ada transaksi untuk dihapus."
        )
        return
    
    message = "Pilih transaksi yang ingin dihapus:\n\n"
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = []
    
    for trans in transactions:
        # Format transaction info
        sign = '+' if trans.type == 'income' else '-'
        amount = Formatter.format_currency(trans.amount)
        date_str = Formatter.format_date_relative(trans.transaction_date)
        category = trans.category_name
        
        trans_text = f"{sign}{amount} - {trans.description[:20]}"
        trans_detail = f"{category} • {date_str}"
        
        # Add button for each transaction
        keyboard.append([
            InlineKeyboardButton(
                f"{trans_text}\n{trans_detail}",
                callback_data=f"delete_trans_{trans.id}"
            )
        ])
    
    # Add cancel button
    keyboard.append([InlineKeyboardButton("❌ Batal", callback_data="cancel")])
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@error_handler
@authenticated
async def undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /undo command - delete last transaction.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    # Get last transaction
    transactions = TransactionService.get_user_transactions(user.id, limit=1)
    
    if not transactions:
        await update.message.reply_text(
            "Tidak ada transaksi untuk di-undo."
        )
        return
    
    last_trans = transactions[0]
    
    # Show confirmation
    message = "⚠️ Hapus transaksi terakhir?\n\n"
    message += Formatter.format_transaction_message(last_trans)
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"confirm_delete_{last_trans.id}"),
            InlineKeyboardButton("❌ Batal", callback_data="cancel")
        ]
    ]
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
