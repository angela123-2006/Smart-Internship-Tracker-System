"""
==============================================================
Smart Internship Tracker System — Database Connection
==============================================================
Provides a reusable function to obtain a MySQL connection using
connection pooling for better performance and resource management.
==============================================================
"""

import mysql.connector
from mysql.connector import pooling, Error
from config import Config

# ---------------------------------------------------------------
# Connection Pool (created once when the module is first imported)
# ---------------------------------------------------------------
# A pool keeps a fixed number of connections open and reuses them,
# which is much faster than opening a new connection per request.
# ---------------------------------------------------------------
CONNECTION_POOL_SIZE = 5
CONNECTION_POOL_NAME = "internship_pool"

try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name=CONNECTION_POOL_NAME,
        pool_size=CONNECTION_POOL_SIZE,
        pool_reset_session=True,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )
except Error as err:
    # If the pool can't be created (e.g., MySQL not running),
    # we log the error and set the pool to None so the app can
    # still start and return a helpful error message.
    print(f"[DB ERROR] Could not create connection pool: {err}")
    connection_pool = None


def get_db_connection():
    """
    Get a connection from the pool.

    Returns:
        mysql.connector.connection.MySQLConnection | None:
            A database connection, or None if the pool is unavailable.
    """
    if connection_pool is None:
        print("[DB ERROR] Connection pool is not available.")
        return None

    try:
        connection = connection_pool.get_connection()
        return connection
    except Error as err:
        print(f"[DB ERROR] Failed to get connection from pool: {err}")
        return None
