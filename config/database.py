"""Database connection pool and management."""

import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import logging
from .settings import Settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager with connection pooling."""
    
    _connection_pool = []
    _pool_size = 5
    
    @classmethod
    def get_connection(cls):
        """Get a database connection from the pool or create a new one."""
        if cls._connection_pool:
            conn = cls._connection_pool.pop()
            try:
                conn.ping(reconnect=True)
                return conn
            except:
                pass
        
        return cls._create_connection()
    
    @classmethod
    def _create_connection(cls):
        """Create a new database connection."""
        try:
            connection = pymysql.connect(
                host=Settings.DB_HOST,
                port=Settings.DB_PORT,
                user=Settings.DB_USER,
                password=Settings.DB_PASSWORD,
                database=Settings.DB_NAME,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=False
            )
            logger.info("Database connection established")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    @classmethod
    def release_connection(cls, conn):
        """Return a connection to the pool."""
        if conn and len(cls._connection_pool) < cls._pool_size:
            try:
                conn.ping(reconnect=True)
                cls._connection_pool.append(conn)
            except:
                try:
                    conn.close()
                except:
                    pass
        else:
            try:
                conn.close()
            except:
                pass
    
    @classmethod
    @contextmanager
    def get_cursor(cls, commit=True):
        """Context manager for database operations.
        
        Args:
            commit: Whether to commit the transaction (default: True)
            
        Usage:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            cls.release_connection(conn)
    
    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, commit=True):
        """Execute a query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
            fetch_one: Return single row instead of all rows
            commit: Whether to commit the transaction
            
        Returns:
            Query results or None
        """
        with cls.get_cursor(commit=commit) as cursor:
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    
    @classmethod
    def execute_many(cls, query, params_list):
        """Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with cls.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    @classmethod
    def close_all_connections(cls):
        """Close all connections in the pool."""
        while cls._connection_pool:
            conn = cls._connection_pool.pop()
            try:
                conn.close()
            except:
                pass
        logger.info("All database connections closed")
