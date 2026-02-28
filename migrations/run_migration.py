"""Database migration script runner."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
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
        
        # Use configured DB_NAME instead of hardcoded name in SQL
        sql_script = re.sub(
            r'CREATE\s+DATABASE\s+IF\s+NOT\s+EXISTS\s+`?montrixa`?',
            f"CREATE DATABASE IF NOT EXISTS `{Settings.DB_NAME}`",
            sql_script,
            flags=re.IGNORECASE
        )
        sql_script = re.sub(
            r'USE\s+`?montrixa`?',
            f"USE `{Settings.DB_NAME}`",
            sql_script,
            flags=re.IGNORECASE
        )
        
        # Remove single-line comments so CREATE TABLE etc. are not skipped
        cleaned_lines = []
        for line in sql_script.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('--'):
                continue
            cleaned_lines.append(line)
        
        cleaned_script = '\n'.join(cleaned_lines)
        statements = [s.strip() for s in cleaned_script.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, start=1):
            cursor.execute(statement)
            preview = ' '.join(statement.split())[:80]
            logger.info(f"[{i}/{len(statements)}] Executed: {preview}...")
        
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
