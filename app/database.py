# backend_server/app/database.py
import pymysql
from . import config

def get_db_connection():
    """创建并返回一个数据库连接"""
    try:
        conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            port=config.MYSQL_PORT,
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        return conn
    except pymysql.Error as e:
        print(f"Database connection failed: {e}")
        return None
