"""Caching service with Redis support and in-memory fallback."""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Callable, TypeVar
from functools import wraps

from .logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheService:
    """Caching service with Redis backend and in-memory fallback."""

    def __init__(self):
        self._redis = None
        self._memory_cache: dict[str, tuple[Any, datetime]] = {}
        self._use_redis = False
        self._hits = 0
        self._misses = 0

    async def initialize(self) -> None:
        """Initialize cache backend."""
        try:
            import redis.asyncio as redis
            from ..config import Settings

            settings = Settings()
            if hasattr(settings, "redis_url") and settings.redis_url:
                self._redis = redis.from_url(settings.redis_url)
                await self._redis.ping()
                self._use_redis = True
                logger.info("Cache initialized with Redis")
            else:
                logger.info("Cache initialized with in-memory store")
        except ImportError:
            logger.info("Redis not available, using in-memory cache")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")

    def _generate_key(self, prefix: str, **kwargs: Any) -> str:
        """Generate a cache key from prefix and parameters."""
        if not kwargs:
            return prefix

        # Sort kwargs for consistent hashing
        params = json.dumps(kwargs, sort_keys=True, default=str)
        hash_key = hashlib.md5(params.encode()).hexdigest()[:8]
        return f"{prefix}:{hash_key}"

    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        if self._use_redis and self._redis:
            try:
                value = await self._redis.get(key)
                if value:
                    self._hits += 1
                    return json.loads(value)
                self._misses += 1
                return None
            except Exception as e:
                logger.error("Redis get failed", key=key, error=str(e))
                return self._memory_get(key)
        else:
            return self._memory_get(key)

    def _memory_get(self, key: str) -> Any | None:
        """Get from in-memory cache."""
        if key in self._memory_cache:
            value, expiry = self._memory_cache[key]
            if datetime.utcnow() < expiry:
                self._hits += 1
                return value
            else:
                del self._memory_cache[key]
        self._misses += 1
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        """Set a value in cache with TTL in seconds."""
        if self._use_redis and self._redis:
            try:
                await self._redis.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str),
                )
                return
            except Exception as e:
                logger.error("Redis set failed", key=key, error=str(e))

        # Fallback to memory
        self._memory_set(key, value, ttl)

    def _memory_set(self, key: str, value: Any, ttl: int) -> None:
        """Set in memory cache."""
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._memory_cache[key] = (value, expiry)

    async def delete(self, key: str) -> None:
        """Delete a key from cache."""
        if self._use_redis and self._redis:
            try:
                await self._redis.delete(key)
                return
            except Exception as e:
                logger.error("Redis delete failed", key=key, error=str(e))

        self._memory_cache.pop(key, None)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if self._use_redis and self._redis:
            try:
                keys = []
                async for key in self._redis.scan_iter(match=pattern):
                    keys.append(key)
                if keys:
                    await self._redis.delete(*keys)
                return len(keys)
            except Exception as e:
                logger.error(
                    "Redis delete_pattern failed", pattern=pattern, error=str(e)
                )

        # Memory fallback - simple prefix match
        count = 0
        keys_to_delete = [
            k
            for k in self._memory_cache.keys()
            if k.startswith(pattern.replace("*", ""))
        ]
        for key in keys_to_delete:
            del self._memory_cache[key]
            count += 1
        return count

    async def clear(self) -> None:
        """Clear all cache entries."""
        if self._use_redis and self._redis:
            try:
                await self._redis.flushdb()
                return
            except Exception as e:
                logger.error("Redis clear failed", error=str(e))

        self._memory_cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "backend": "redis" if self._use_redis else "memory",
            "memory_entries": len(self._memory_cache),
        }

    def reset_stats(self) -> None:
        """Reset hit/miss counters."""
        self._hits = 0
        self._misses = 0


# Global cache instance
cache_service = CacheService()


def cached(key_prefix: str, ttl: int = 300):
    """Decorator for caching function results."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            cache_key = cache_service._generate_key(
                f"{key_prefix}:{func.__name__}",
                args=str(args),
                kwargs=kwargs,
            )

            # Try to get from cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            return result

        # Attach cache utilities to function
        wrapper.cache_clear = lambda: cache_service.clear()
        wrapper.cache_key = lambda *args, **kwargs: cache_service._generate_key(
            f"{key_prefix}:{func.__name__}",
            args=str(args),
            kwargs=kwargs,
        )

        return wrapper

    return decorator
