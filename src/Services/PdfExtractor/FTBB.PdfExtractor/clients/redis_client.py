"""
Redis client wrapper for data storage operations
"""
import json
import logging
from typing import Dict, Any, Optional, List
import redis

from config.redis_config import RedisConfig

logger = logging.getLogger(__name__)


class RedisClient:
    """Wrapper for Redis operations with type safety and error handling"""
    
    def __init__(self):
        """Initialize Redis connection pool"""
        try:
            self.redis_client = redis.Redis(
                host=RedisConfig.HOST,
                port=RedisConfig.PORT,
                db=RedisConfig.DB,
                password=RedisConfig.PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def store_team_data(self, team_data: Dict[str, Any], team_abbr: str, 
                       event_id: Optional[str] = None, 
                       expiry: Optional[int] = None) -> bool:
        """Store team data in Redis"""
        try:
            key = RedisConfig.get_team_key(team_abbr, event_id)
            value = json.dumps(team_data, ensure_ascii=False)
            expiry_time = expiry or RedisConfig.DEFAULT_EXPIRY
            
            self.redis_client.setex(key, expiry_time, value)
            return True
        except Exception as e:
            logger.error(f"Failed to store team data: {e}")
            return False
    
    def store_extraction_result(self, extraction_result: Dict[str, Any], 
                               event_id: str, pdf_name: str,
                               expiry: Optional[int] = None) -> bool:
        """Store complete extraction result (all teams from a PDF)"""
        try:
            key = RedisConfig.get_extraction_key(event_id, pdf_name)
            value = json.dumps(extraction_result, ensure_ascii=False)
            expiry_time = expiry or RedisConfig.DEFAULT_EXPIRY
            
            self.redis_client.setex(key, expiry_time, value)
            return True
        except Exception as e:
            logger.error(f"Failed to store extraction result: {e}")
            return False
    
    def get_team_data(self, team_abbr: str, event_id: Optional[str] = None) -> Optional[Dict]:
        """Retrieve team data from Redis"""
        try:
            key = RedisConfig.get_team_key(team_abbr, event_id)
            value = self.redis_client.get(key)
            
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve team data: {e}")
            return None
    
    def get_extraction_result(self, event_id: str, pdf_name: str) -> Optional[Dict]:
        """Retrieve extraction result from Redis"""
        try:
            key = RedisConfig.get_extraction_key(event_id, pdf_name)
            value = self.redis_client.get(key)
            
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve extraction result: {e}")
            return None
    
    def store_event_metadata(self, event_id: str, metadata: Dict[str, Any],
                            expiry: Optional[int] = None) -> bool:
        """Store event metadata"""
        try:
            key = RedisConfig.get_event_key(event_id)
            value = json.dumps(metadata, ensure_ascii=False)
            expiry_time = expiry or RedisConfig.DEFAULT_EXPIRY
            
            self.redis_client.setex(key, expiry_time, value)
            return True
        except Exception as e:
            logger.error(f"Failed to store event metadata: {e}")
            return False
    
    def get_event_metadata(self, event_id: str) -> Optional[Dict]:
        """Retrieve event metadata from Redis"""
        try:
            key = RedisConfig.get_event_key(event_id)
            value = self.redis_client.get(key)
            
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve event metadata: {e}")
            return None
    
    def get_all_event_teams(self, event_id: str) -> List[Dict]:
        """Retrieve all team data for an event"""
        try:
            pattern = RedisConfig.get_team_key('*', event_id)
            keys = self.redis_client.keys(pattern)
            teams = []
            
            for key in keys:
                value = self.redis_client.get(key)
                if value:
                    teams.append(json.loads(value))
            
            return teams
        except Exception as e:
            logger.error(f"Failed to retrieve all event teams: {e}")
            return []
    
    def delete_team_data(self, team_abbr: str, event_id: Optional[str] = None) -> bool:
        """Delete team data from Redis"""
        try:
            key = RedisConfig.get_team_key(team_abbr, event_id)
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete team data: {e}")
            return False
    
    def delete_event_data(self, event_id: str) -> bool:
        """Delete all data related to an event"""
        try:
            pattern = RedisConfig.get_team_key('*', event_id)
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
            
            # Also delete event metadata
            event_key = RedisConfig.get_event_key(event_id)
            self.redis_client.delete(event_key)
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete event data: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        try:
            self.redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
