"""Category management handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import authenticated, error_handler
from utils.validators import Validator
from services.category_service import CategoryService
import logging

logger = logging.getLogger(__name__)


@error_handler
@authenticated
async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /categories command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    categories = CategoryService.get_categories(user.id)
    
    if not categories:
        await update.message.reply_text("Tidak ada kategori.")
        return
    
    income_cats = [c for c in categories if c.type == 'income']
    expense_cats = [c for c in categories if c.type == 'expense']
    
    message = "KATEGORI ANDA\n\n"
    
    message += "PEMASUKAN:\n"
    for cat in income_cats:
        default_mark = " (default)" if cat.is_default else ""
        message += f"  {cat.name}{default_mark}\n"
    
    message += "\nPENGELUARAN:\n"
    for cat in expense_cats:
        default_mark = " (default)" if cat.is_default else ""
        message += f"  {cat.name}{default_mark}\n"
    
    message += "\nTips:\n"
    message += "• /addcategory [nama] [tipe] - Tambah kategori\n"
    message += "  Contoh: /addcategory Hobby expense"
    
    await update.message.reply_text(message)


@error_handler
@authenticated
async def add_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Handle /addcategory command.
    
    Args:
        update: Telegram update object
        context: Telegram context
        user: Authenticated user object
    """
    args = Validator.parse_command_args(update.message.text)
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Format salah\n\n"
            "Gunakan: /addcategory [nama] [tipe]\n"
            "Tipe: income/expense (pemasukan/pengeluaran)\n\n"
            "Contoh:\n"
            "• /addcategory Hobby expense\n"
            "• /addcategory Freelance income"
        )
        return
    
    # Get category name (all args except last)
    cat_name = ' '.join(args[:-1])
    cat_type_str = args[-1]
    
    # Validate name
    is_valid, cat_name, error = Validator.validate_category_name(cat_name)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # Validate type
    is_valid, cat_type, error = Validator.validate_transaction_type(cat_type_str)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return
    
    # No icon for simplified version
    icon = ''
    
    # Create category
    category = CategoryService.create_category(user.id, cat_name, cat_type, icon)
    
    if not category:
        await update.message.reply_text("❌ Gagal membuat kategori. Mungkin sudah ada.")
        return
    
    type_name = "pemasukan" if cat_type == "income" else "pengeluaran"
    await update.message.reply_text(
        f"✅ Kategori {type_name} berhasil ditambahkan\n\n"
        f"{category.name}\n\n"
        f"Sekarang Anda bisa menggunakan kategori ini untuk transaksi."
    )
