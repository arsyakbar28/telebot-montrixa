"""Main bot application entry point."""

import logging
import sys
from telegram import Update, MenuButtonWebApp, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Import config
from config.settings import Settings
from config.database import DatabaseConnection

# Import handlers
from handlers.start_handler import start_command, help_command, menu_command
from handlers.transaction_handler import (
    income_command,
    expense_command,
    list_command,
    balance_command,
    history_command,
    delete_command,
    undo_command,
)
from handlers.category_handler import categories_command, add_category_command
from handlers.budget_handler import (
    budget_command,
    budget_status_command,
    set_budget_command,
)
from handlers.recurring_handler import recurring_command, add_recurring_command
from handlers.report_handler import summary_command, report_command, export_command
from handlers.callbacks import (
    handle_category_selection,
    handle_cancel,
    handle_menu_callbacks,
    handle_report_period,
    handle_delete_transaction,
    menu_income_expense_start,
    receive_amount_from_menu,
    category_selection_conversation_end,
    cancel_conversation,
    WAITING_AMOUNT,
    SELECTING_CATEGORY,
)

# Import jobs
from jobs.recurring_job import schedule_recurring_job
from jobs.budget_alert_job import schedule_budget_alert_job

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Settings.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('montrixa.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


async def error_callback(update: Update, context) -> None:
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


async def post_init_set_menu_button(application: Application) -> None:
    """Set chat menu button to open Mini App (tombol 'Open' di samping lampiran)."""
    if not Settings.MINIAPP_URL:
        logger.warning("MINIAPP_URL kosong - Menu Button tidak diset. Isi .env lalu restart bot.")
        return
    url = Settings.MINIAPP_URL.strip()
    if not url.startswith("https://"):
        logger.warning("MINIAPP_URL harus HTTPS. Menu Button tidak diset.")
        return
    try:
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open", web_app=WebAppInfo(url=url))
        )
        logger.info("Menu button (Open) set ke Mini App: %s", url)
    except Exception as e:
        logger.error("Gagal set Menu Button: %s", e, exc_info=True)


def main():
    """Start the bot."""
    # Validate settings
    try:
        Settings.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file")
        sys.exit(1)
    
    logger.info("Starting Montrixa Bot...")
    
    # Create application (post_init = set Menu Button "Open" seperti BotFather)
    application = (
        Application.builder()
        .token(Settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init_set_menu_button)
        .build()
    )
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Transaction commands
    application.add_handler(CommandHandler("income", income_command))
    application.add_handler(CommandHandler("expense", expense_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("delete", delete_command))
    application.add_handler(CommandHandler("undo", undo_command))
    
    # Category commands
    application.add_handler(CommandHandler("categories", categories_command))
    application.add_handler(CommandHandler("addcategory", add_category_command))
    
    # Budget commands
    application.add_handler(CommandHandler("budget", budget_command))
    application.add_handler(CommandHandler("budgetstatus", budget_status_command))
    application.add_handler(CommandHandler("setbudget", set_budget_command))
    
    # Recurring commands
    application.add_handler(CommandHandler("recurring", recurring_command))
    application.add_handler(CommandHandler("addrecurring", add_recurring_command))
    
    # Report commands
    application.add_handler(CommandHandler("summary", summary_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("export", export_command))
    
    # Conversation: klik Pemasukan/Pengeluaran -> ketik nominal -> klik kategori
    conv_transaction = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(menu_income_expense_start, pattern="^menu_(income|expense)$"),
        ],
        states={
            WAITING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount_from_menu),
                CallbackQueryHandler(cancel_conversation, pattern="^cancel$"),
            ],
            SELECTING_CATEGORY: [
                CallbackQueryHandler(category_selection_conversation_end, pattern="^(income|expense)_cat_"),
                CallbackQueryHandler(cancel_conversation, pattern="^cancel$"),
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel_conversation, pattern="^cancel$")],
    )
    application.add_handler(conv_transaction)

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(handle_cancel, pattern="^cancel$"))
    application.add_handler(CallbackQueryHandler(handle_category_selection, pattern="^(income|expense)_cat_"))
    application.add_handler(CallbackQueryHandler(handle_menu_callbacks, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(handle_report_period, pattern="^report_(today|7d|30d|this_month|last_month)$"))
    application.add_handler(CallbackQueryHandler(handle_delete_transaction, pattern="^(delete_trans_|confirm_delete_)"))
    
    # Error handler
    application.add_error_handler(error_callback)
    
    # Setup scheduler for background jobs
    scheduler = AsyncIOScheduler()
    
    # Get bot instance for jobs
    bot = application.bot
    
    # Schedule jobs
    schedule_recurring_job(scheduler, bot)
    schedule_budget_alert_job(scheduler, bot)
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started with recurring and budget alert jobs")
    
    # Start bot
    logger.info("Bot started successfully! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # Cleanup on shutdown
    scheduler.shutdown()
    DatabaseConnection.close_all_connections()
    logger.info("Bot stopped")


if __name__ == '__main__':
    main()
