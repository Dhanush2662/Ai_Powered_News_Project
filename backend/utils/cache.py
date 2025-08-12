import os
import json
from typing import Any, Optional, Callable, TypeVar, Dict
from functools import wraps
import redis
import fakeredis
from config import Config

# Type variable for generic function return type
T = TypeVar('T')

# Determine if we should use real Redis or FakeRedis (for testing/development)
use_real_redis = os.getenv("USE_REAL_REDIS", "False").lower() == "true"

# Redis connection parameters
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_password = os.getenv("REDIS_PASSWORD", None)
redis_db = int(os.getenv("REDIS_DB", 0))

# Create Redis client
if use_real_redis:
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=redis_db,
        decode_responses=True
    )
else:
    # Use FakeRedis for development/testing
    redis_client = fakeredis.FakeRedis(decode_responses=True)


def cache_key_builder(*args, **kwargs) -> str:
    """Build a cache key from function arguments"""
    # Convert args and kwargs to strings and join them
    args_str = "_".join([str(arg) for arg in args])
    kwargs_str = "_".join([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    
    # Combine args and kwargs strings
    if args_str and kwargs_str:
        return f"{args_str}_{kwargs_str}"
    elif args_str:
        return args_str
    elif kwargs_str:
        return kwargs_str
    else:
        return "default"


def cache(prefix: str, ttl: Optional[int] = None):
    """Cache decorator for functions
    
    Args:
        prefix: Prefix for the cache key
        ttl: Time to live in seconds, defaults to CACHE_TTL_SECONDS from config
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Get TTL from config if not provided
            cache_ttl = ttl if ttl is not None else Config.CACHE_TTL_SECONDS
            
            # Build cache key
            key_suffix = cache_key_builder(*args, **kwargs)
            cache_key = f"{prefix}:{func.__name__}:{key_suffix}"
            
            # Try to get from cache
            cached_value = redis_client.get(cache_key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    # If not JSON, return as is
                    return cached_value
            
            # If not in cache, call the function
            result = await func(*args, **kwargs)
            
            # Cache the result
            try:
                redis_client.setex(
                    cache_key,
                    cache_ttl,
                    json.dumps(result) if not isinstance(result, str) else result
                )
            except (TypeError, json.JSONDecodeError) as e:
                # Log the error but don't fail the function call
                print(f"Error caching result: {e}")
            
            return result
        return wrapper
    return decorator


def clear_cache(prefix: Optional[str] = None) -> int:
    """Clear cache with the given prefix or all cache if no prefix
    
    Args:
        prefix: Prefix for the cache keys to clear
        
    Returns:
        Number of keys deleted
    """
    if prefix:
        # Get all keys with the prefix
        keys = redis_client.keys(f"{prefix}:*")
        if keys:
            return redis_client.delete(*keys)
        return 0
    else:
        # Clear all cache
        return redis_client.flushdb()