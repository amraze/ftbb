"""
Redis configuration module
"""
import os
from dotenv import load_dotenv

load_dotenv()


class RedisConfig:
    """Redis connection and storage configuration"""
    
    HOST = os.getenv('REDIS_HOST', 'localhost')
    PORT = int(os.getenv('REDIS_PORT', 6379))
    DB = int(os.getenv('REDIS_DB', 0))
    PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # Key naming patterns
    TEAM_KEY_PREFIX = 'team:'
    EVENT_KEY_PREFIX = 'event:'
    EXTRACTION_KEY_PREFIX = 'extraction:'
    
    # Expiration times (in seconds)
    DEFAULT_EXPIRY = int(os.getenv('REDIS_DEFAULT_EXPIRY', 86400))  # 24 hours
    
    @staticmethod
    def get_team_key(team_abbr: str, event_id: str = None) -> str:
        """Generate Redis key for team data"""
        if event_id:
            return f"{RedisConfig.TEAM_KEY_PREFIX}{event_id}:{team_abbr}"
        return f"{RedisConfig.TEAM_KEY_PREFIX}{team_abbr}"
    
    @staticmethod
    def get_event_key(event_id: str) -> str:
        """Generate Redis key for event metadata"""
        return f"{RedisConfig.EVENT_KEY_PREFIX}{event_id}"
    
    @staticmethod
    def get_extraction_key(event_id: str, pdf_name: str) -> str:
        """Generate Redis key for extraction results"""
        return f"{RedisConfig.EXTRACTION_KEY_PREFIX}{event_id}:{pdf_name}"
