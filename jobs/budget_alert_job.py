"""Budget alert checking job."""

from models.budget import Budget
from services.budget_service import BudgetService
from telegram import Bot
from utils.formatters import Formatter
import logging

logger = logging.getLogger(__name__)


async def check_budget_alerts(bot: Bot):
    """Check all budgets and send alerts if needed.
    
    Args:
        bot: Telegram Bot instance
    """
    logger.info("Checking budget alerts...")
    
    try:
        # Get all active budgets
        budgets = Budget.get_all_active()
        
        alert_count = 0
        
        for budget in budgets:
            # Check if alert needed
            percentage = budget.get_percentage_used()
            
            # Determine alert type
            alert_type = None
            should_send = False
            
            if percentage >= 100 and budget.alert_at_100:
                alert_type = 'critical'
                should_send = True
            elif percentage >= 90 and budget.alert_at_90:
                alert_type = 'danger'
                should_send = True
            elif percentage >= 75 and budget.alert_at_75:
                alert_type = 'warning'
                should_send = True
            
            if should_send:
                # Check if alert already sent today
                if not BudgetService._alert_sent_today(budget.id, alert_type):
                    # Send alert to user
                    from models.user import User
                    user = User.get_by_id(budget.user_id)
                    
                    if user:
                        spent = budget.get_spent_amount()
                        
                        message = "⚠️ PERINGATAN BUDGET\n\n"
                        message += f"{budget.category_name}\n"
                        message += f"{Formatter.format_currency(spent)} / "
                        message += f"{Formatter.format_currency(budget.amount)} "
                        message += f"({Formatter.format_percentage(percentage)})\n"
                        message += f"{Formatter.format_period(budget.period)}\n\n"
                        
                        if alert_type == 'critical':
                            message += "Budget sudah melampaui batas!"
                        elif alert_type == 'danger':
                            message += "Budget hampir habis! (90%+)"
                        else:
                            message += "Perhatian: Budget sudah terpakai 75%"
                        
                        try:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=message
                            )
                            
                            # Log alert
                            BudgetService.log_alert(
                                user.id, budget.id, alert_type,
                                percentage, spent, budget.amount
                            )
                            
                            alert_count += 1
                            logger.info(f"Sent {alert_type} alert for budget {budget.id} to user {user.telegram_id}")
                            
                        except Exception as e:
                            logger.error(f"Failed to send alert to user {user.telegram_id}: {e}")
        
        if alert_count > 0:
            logger.info(f"Sent {alert_count} budget alerts")
        else:
            logger.info("No budget alerts needed")
            
    except Exception as e:
        logger.error(f"Error checking budget alerts: {e}", exc_info=True)


def schedule_budget_alert_job(scheduler, bot: Bot):
    """Schedule budget alert checking job.
    
    Args:
        scheduler: APScheduler instance
        bot: Telegram Bot instance
    """
    # Run every 6 hours
    scheduler.add_job(
        check_budget_alerts,
        'interval',
        hours=6,
        args=[bot],
        id='budget_alerts',
        name='Check Budget Alerts',
        replace_existing=True
    )
    
    logger.info("Scheduled budget alert job (every 6 hours)")
