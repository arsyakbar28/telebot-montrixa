"""Database migration script runner."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from config.settings import Settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the database migration from init_db.sql."""
    try:
        # Connect without selecting database first
        connection = pymysql.connect(
            host=Settings.DB_HOST,
            port=Settings.DB_PORT,
            user=Settings.DB_USER,
            password=Settings.DB_PASSWORD,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Read SQL file
        sql_file = os.path.join(os.path.dirname(__file__), 'init_db.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        for statement in statements:
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    logger.info(f"Executed: {statement[:50]}...")
                except Exception as e:
                    logger.warning(f"Statement failed (might already exist): {str(e)[:100]}")
        
        connection.commit()
        logger.info("✅ Database migration completed successfully!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 60)
    print("Montrixa Database Migration")
    print("=" * 60)
    run_migration()
