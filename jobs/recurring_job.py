"""Recurring transaction processing job."""

from services.recurring_service import RecurringService
from telegram import Bot
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)


async def process_recurring_transactions(bot: Bot):
    """Process all due recurring transactions.
    
    Args:
        bot: Telegram Bot instance
    """
    logger.info("Starting recurring transaction processing...")
    
    try:
        count = RecurringService.process_due_recurring()
        
        if count > 0:
            logger.info(f"Successfully processed {count} recurring transactions")
        else:
            logger.info("No recurring transactions due")
            
    except Exception as e:
        logger.error(f"Error processing recurring transactions: {e}", exc_info=True)


def schedule_recurring_job(scheduler, bot: Bot):
    """Schedule recurring transaction processing job.
    
    Args:
        scheduler: APScheduler instance
        bot: Telegram Bot instance
    """
    # Run every hour
    scheduler.add_job(
        process_recurring_transactions,
        'interval',
        hours=1,
        args=[bot],
        id='recurring_transactions',
        name='Process Recurring Transactions',
        replace_existing=True
    )
    
    logger.info("Scheduled recurring transaction job (every hour)")
