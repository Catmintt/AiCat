import redis.asyncio as redis
from .config import settings

# 用于保存 Redis 连接池的全局变量
redis_pool = None

async def get_redis_pool():
    """获取 Redis 连接池"""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            decode_responses=True  # 自动将 Redis 的 bytes 响应解码为字符串
        )
    return redis.Redis(connection_pool=redis_pool)

async def close_redis_pool():
    """关闭 Redis 连接池"""
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None