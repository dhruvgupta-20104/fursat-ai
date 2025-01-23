# config/config_manager.py

import os
from typing import Dict, Any
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    OPENAI_API_KEY: str
    MONGODB_CONNECTION_STRING: str
    TELEGRAM_BOT_TOKEN: str
    YOUTUBE_API_KEY: str
    
    # Application Settings
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Fursat.fun AI Multi-Agent"
    
    # Content Processing
    MAX_VIDEO_DURATION: int = 60  # seconds
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    SUPPORTED_VIDEO_FORMATS: list = ["mp4", "mov", "avi"]
    
    # MongoDB Collections
    TOURS_COLLECTION: str = "tours"
    CUSTOMIZED_TOURS_COLLECTION: str = "customized_tours"
    CONTENT_COLLECTION: str = "content"
    
    # Cache Settings
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()

class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self):
        self.settings = get_settings()
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        required_vars = [
            "OPENAI_API_KEY",
            "MONGODB_CONNECTION_STRING",
            "TELEGRAM_BOT_TOKEN",
            "YOUTUBE_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self.settings, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def get_mongodb_config(self) -> Dict[str, Any]:
        """Get MongoDB configuration"""
        return {
            "connection_string": self.settings.MONGODB_CONNECTION_STRING,
            "tours_collection": self.settings.TOURS_COLLECTION,
            "customized_tours_collection": self.settings.CUSTOMIZED_TOURS_COLLECTION,
            "content_collection": self.settings.CONTENT_COLLECTION
        }
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get API keys"""
        return {
            "openai": self.settings.OPENAI_API_KEY,
            "youtube": self.settings.YOUTUBE_API_KEY,
            "telegram": self.settings.TELEGRAM_BOT_TOKEN
        }
    
    def get_content_settings(self) -> Dict[str, Any]:
        """Get content processing settings"""
        return {
            "max_duration": self.settings.MAX_VIDEO_DURATION,
            "max_size": self.settings.MAX_UPLOAD_SIZE,
            "supported_formats": self.settings.SUPPORTED_VIDEO_FORMATS
        }
    
    def get_cache_settings(self) -> Dict[str, Any]:
        """Get cache settings"""
        return {
            "redis_url": self.settings.REDIS_URL,
            "ttl": self.settings.CACHE_TTL
        }
    
    def get_rate_limit_settings(self) -> Dict[str, int]:
        """Get rate limiting settings"""
        return {
            "calls": self.settings.RATE_LIMIT_CALLS,
            "period": self.settings.RATE_LIMIT_PERIOD
        }