"""Caching layer for frequently accessed database data"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import lru_cache

LOG = logging.getLogger(__name__)


class CategoryCache:
    """Cache for Category objects with TTL"""
    
    def __init__(self, ttl: int = 300):
        """
        Args:
            ttl: Time to live in seconds (default 5 minutes)
        """
        self.cache: Dict[int, tuple] = {}  # {category_id: (data, timestamp)}
        self.ttl = timedelta(seconds=ttl)
    
    def get(self, category_id: int) -> Optional[Any]:
        """Get cached category data if still valid"""
        if category_id in self.cache:
            data, timestamp = self.cache[category_id]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                # Expired, remove from cache
                del self.cache[category_id]
        return None
    
    def set(self, category_id: int, data: Any) -> None:
        """Cache category data with current timestamp"""
        self.cache[category_id] = (data, datetime.now())
    
    def invalidate(self, category_id: int) -> None:
        """Remove category from cache"""
        self.cache.pop(category_id, None)
    
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()


class ChannelListCache:
    """Cache for channel ID lists per category"""
    
    def __init__(self, ttl: int = 180):
        """
        Args:
            ttl: Time to live in seconds (default 3 minutes)
        """
        self.cache: Dict[int, tuple] = {}  # {category_id: (channel_ids, timestamp)}
        self.ttl = timedelta(seconds=ttl)
    
    def get(self, category_id: int) -> Optional[list]:
        """Get cached channel ID list if still valid"""
        if category_id in self.cache:
            data, timestamp = self.cache[category_id]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[category_id]
        return None
    
    def set(self, category_id: int, channel_ids: list) -> None:
        """Cache channel ID list"""
        self.cache[category_id] = (channel_ids, datetime.now())
    
    def invalidate(self, category_id: int) -> None:
        """Remove category's channel list from cache"""
        self.cache.pop(category_id, None)
    
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()


# Global cache instances
category_cache = CategoryCache(ttl=300)  # 5 minutes
channel_list_cache = ChannelListCache(ttl=180)  # 3 minutes
