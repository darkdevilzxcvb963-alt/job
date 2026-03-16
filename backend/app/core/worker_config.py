"""
Async Worker Configuration
Defines background task workers using arq for Redis-backed async processing.
Falls back to in-process execution if Redis is unavailable.
"""
import os
from loguru import logger

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}")

# Try to connect to Redis, fall back gracefully
_redis_available = False
_redis_pool = None

def get_redis_pool():
    """Get or create a Redis connection pool (lazy)"""
    global _redis_available, _redis_pool
    if _redis_pool is not None:
        return _redis_pool
    
    try:
        import redis
        pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
        client = redis.Redis(connection_pool=pool)
        client.ping()
        _redis_pool = pool
        _redis_available = True
        logger.info(f"Redis connected at {REDIS_URL}")
        return pool
    except Exception as e:
        logger.warning(f"Redis not available ({e}). Using in-memory fallback.")
        _redis_available = False
        return None

def is_redis_available():
    """Check if Redis is available"""
    if _redis_pool is None:
        get_redis_pool()
    return _redis_available

def get_redis_client():
    """Get a Redis client instance"""
    pool = get_redis_pool()
    if pool is None:
        return None
    import redis
    return redis.Redis(connection_pool=pool)
