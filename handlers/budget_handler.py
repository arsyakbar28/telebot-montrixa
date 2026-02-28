"""Budget management handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import authenticated, error_handler
from utils.formatters import Formatter
from utils.validators import Validator
from services.budget_service import BudgetService
from services.category_service import CategoryService
import logging

logger = logging.getLogger(__name__)


@error_handler
@authenticated
async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /budget command - show all budgets.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    budgets = BudgetService.get_user_budgets(user.id)
    
    if not budgets:
        await update.message.reply_text(
            "Belum ada budget.\n\n"
            "Gunakan /setbudget untuk mengatur budget."
        )
        return
    
    message = "BUDGET ANDA\n\n"
    
    for budget in budgets:
        message += f"{budget.category_name}\n"
        message += f"  {Formatter.format_currency(budget.amount)}\n"
        message += f"  {Formatter.format_period(budget.period)}\n"
        message += "─" * 30 + "\n"
    
    message += "\nGunakan /budgetstatus untuk melihat status penggunaan budget."
    
    await update.message.reply_text(message)


@error_handler
@authenticated
async def budget_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /budgetstatus command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    status_list = BudgetService.get_budget_status(user.id)
    
    if not status_list:
        await update.message.reply_text(
            "Belum ada budget.\n\n"
            "Gunakan /setbudget untuk mengatur budget."
        )
        return
    
    message = "STATUS BUDGET\n\n"
    
    for status in status_list:
        message += Formatter.format_budget_status(status) + "\n"
        message += "─" * 30 + "\n"
    
    await update.message.reply_text(message)


@error_handler
@authenticated
async def set_budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /setbudget command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    args = Validator.parse_command_args(update.message.text)
    
    if len(args) < 3:
        await update.message.reply_text(
            "❌ Format salah\n\n"
            "Gunakan: /setbudget [kategori] [jumlah] [periode]\n"
            "Periode: harian/mingguan/bulanan\n\n"
            "Contoh:\n"
            "• /setbudget Makanan 1000000 bulanan\n"
            "• /setbudget Transport 500000 mingguan"
        )
        return
    
    # Parse arguments
    cat_name = ' '.join(args[:-2])
    amount_str = args[-2]
    period_str = args[-1]
    
    # Validate amount
    is_valid, amount, error = Validator.validate_amount(amount_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Validate period
    is_valid, period, error = Validator.validate_period(period_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Find category
    categories = CategoryService.get_expense_categories(user.id)
    category = None
    
    for cat in categories:
        if cat.name.lower() == cat_name.lower():
            category = cat
            break
    
    if not category:
        await update.message.reply_text(
            f"❌ Kategori '{cat_name}' tidak ditemukan.\n\n"
            f"Gunakan /categories untuk melihat kategori yang tersedia."
        )
        return
    
    # Create budget
    budget = BudgetService.create_budget(user.id, category.id, amount, period)
    
    if not budget:
        await update.message.reply_text("❌ Gagal mengatur budget. Silakan coba lagi.")
        return
    
    await update.message.reply_text(
        f"✅ Budget berhasil diatur\n\n"
        f"{category.display_name}\n"
        f"{Formatter.format_currency(amount)}\n"
        f"{Formatter.format_period(period)}\n\n"
        f"Anda akan menerima notifikasi ketika budget mencapai 75%, 90%, dan 100%."
    )
