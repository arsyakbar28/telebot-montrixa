"""Application settings and configuration."""

import os
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()


class Settings:
    """Application configuration settings."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # Telegram Mini App (Web App)
    MINIAPP_URL = os.getenv('MINIAPP_URL', '').strip()
    MINIAPP_INITDATA_MAX_AGE_SECONDS = int(os.getenv('MINIAPP_INITDATA_MAX_AGE_SECONDS', 86400))

    # Mini App API server (optional, for local run commands)
    API_HOST = os.getenv('API_HOST', '127.0.0.1')
    API_PORT = int(os.getenv('API_PORT', 8000))
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'montrixa')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Application Settings
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Jakarta')
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'IDR')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Bot Settings
    MAX_TRANSACTIONS_PER_PAGE = int(os.getenv('MAX_TRANSACTIONS_PER_PAGE', 10))
    CHART_DPI = int(os.getenv('CHART_DPI', 100))
    EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'csv')
    
    # Timezone object
    TZ = pytz.timezone(TIMEZONE)
    
    # Default Categories
    DEFAULT_INCOME_CATEGORIES = [
        ('Gaji', 'income'),
        ('Bonus', 'income'),
        ('Investasi', 'income'),
        ('Lainnya', 'income'),
    ]
    
    DEFAULT_EXPENSE_CATEGORIES = [
        ('Makanan', 'expense'),
        ('Transport', 'expense'),
        ('Belanja', 'expense'),
        ('Tagihan', 'expense'),
        ('Hiburan', 'expense'),
        ('Kesehatan', 'expense'),
        ('Langganan', 'expense'),
        ('Lainnya', 'expense'),
    ]
    
    # Budget Alert Thresholds
    BUDGET_WARNING_THRESHOLD = 75  # 75%
    BUDGET_DANGER_THRESHOLD = 90   # 90%
    BUDGET_CRITICAL_THRESHOLD = 100  # 100%
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required in .env file")
        # DB_PASSWORD can be empty for local development
        return True
