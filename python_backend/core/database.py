import aiomysql
from .config import settings

# 用于保存连接池的全局变量
pool = None

async def get_db_pool():
    """获取数据库连接池"""
    global pool
    if pool is None:
        pool = await aiomysql.create_pool(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            db=settings.DB_DATABASE,
            autocommit=True  # 我们的场景下使用自动提交更方便
        )
    return pool

async def close_db_pool():
    """关闭数据库连接池"""
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        pool = None