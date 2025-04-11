import json
import os
from redis import Redis
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

class CacheService:
    DEFAULT_TTL = 300  # 5 minutes in seconds
    PRICE_TTL = 1800   # 30 minutes in seconds
    COINS_TTL = 86400  # 24 hours in seconds
    
    def __init__(self):
        """Initialize Redis connection"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = Redis.from_url(redis_url, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from Redis cache"""
        cached_data = self.redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    def set(self, key: str, data: Any, ttl: int = None) -> None:
        """Set data in Redis cache"""
        if ttl is None:
            ttl = self.DEFAULT_TTL
        self.redis.setex(key, ttl, json.dumps(data))
    
    def delete(self, key: str) -> None:
        """Delete a key from the cache"""
        self.redis.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        return self.redis.exists(key) > 0