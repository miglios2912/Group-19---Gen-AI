"""
Configuration module for TUM Chatbot Backend
Handles all environment variables and configuration settings
"""

import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def _get_environment_specific_value(env_var: str, dev_default: str, prod_default: str) -> str:
    """Get environment-specific value based on ENVIRONMENT setting"""
    environment = os.getenv("ENVIRONMENT", "development")
    
    # If explicitly set, use that value
    if os.getenv(env_var) is not None:
        return os.getenv(env_var)
    
    # Otherwise use environment-specific default
    if environment.lower() == "production":
        return prod_default
    else:
        return dev_default

def _get_environment_specific_bool(env_var: str, dev_default: bool, prod_default: bool) -> bool:
    """Get environment-specific boolean value based on ENVIRONMENT setting"""
    environment = os.getenv("ENVIRONMENT", "development")
    
    # If explicitly set, use that value
    if os.getenv(env_var) is not None:
        return os.getenv(env_var, "False").lower() == "true"
    
    # Otherwise use environment-specific default
    if environment.lower() == "production":
        return prod_default
    else:
        return dev_default

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "/app/data/chroma_db")
    collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "tum_qa_collection")
    persist_directory: str = os.getenv("CHROMA_PERSIST_DIR", "/app/data/chroma_db")

@dataclass
class APIConfig:
    """API configuration settings"""
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_tokens: int = int(os.getenv("GEMINI_MAX_TOKENS", "4096"))
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))

@dataclass
class SearchConfig:
    """Search configuration settings"""
    semantic_search_top_k: int = int(os.getenv("SEMANTIC_SEARCH_TOP_K", "5"))
    keyword_search_top_k: int = int(os.getenv("KEYWORD_SEARCH_TOP_K", "5"))
    hybrid_search_top_k: int = int(os.getenv("HYBRID_SEARCH_TOP_K", "5"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

@dataclass
class ServerConfig:
    """Server configuration settings"""
    host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    port: int = int(os.getenv("SERVER_PORT", "8080"))
    debug: bool = _get_environment_specific_bool("FLASK_DEBUG", True, False)
    workers: int = int(os.getenv("GUNICORN_WORKERS", "4"))
    timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    log_level: str = _get_environment_specific_value("LOG_LEVEL", "DEBUG", "WARNING")
    log_file: str = os.getenv("LOG_FILE", "/app/logs/tum_chatbot.log")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    max_log_size: int = int(os.getenv("MAX_LOG_SIZE", "10485760"))  # 10MB
    backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    log_chat_sessions: bool = _get_environment_specific_bool("LOG_CHAT_SESSIONS", True, False)
    chat_session_file: str = os.getenv("CHAT_SESSION_FILE", "/app/logs/chat_sessions.log")

@dataclass
class StatisticsConfig:
    """Statistics and analytics configuration"""
    enable_statistics: bool = os.getenv("ENABLE_STATISTICS", "True").lower() == "true"
    stats_db_path: str = os.getenv("STATS_DB_PATH", "/app/data/statistics.db")
    track_user_sessions: bool = os.getenv("TRACK_USER_SESSIONS", "True").lower() == "true"
    track_query_analytics: bool = os.getenv("TRACK_QUERY_ANALYTICS", "True").lower() == "true"
    anonymize_data: bool = os.getenv("ANONYMIZE_DATA", "True").lower() == "true"

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    enable_rate_limiting: bool = os.getenv("ENABLE_RATE_LIMITING", "True").lower() == "true"
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    enable_cors: bool = os.getenv("ENABLE_CORS", "True").lower() == "true"
    session_timeout: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour

@dataclass
class KnowledgeBaseConfig:
    """Knowledge base configuration"""
    knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "/app/TUM_QA.json")
    max_context_length: int = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    conversation_history_limit: int = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "12"))

@dataclass
class AppConfig:
    """Main application configuration"""
    app_name: str = os.getenv("APP_NAME", "TUM Chatbot")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Sub-configurations - using default_factory to avoid mutable default issues
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    statistics: StatisticsConfig = field(default_factory=StatisticsConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    knowledge_base: KnowledgeBaseConfig = field(default_factory=KnowledgeBaseConfig)

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.api.gemini_api_key:
            errors.append("GEMINI_API_KEY is required")
        
        if not os.path.exists(self.knowledge_base.knowledge_base_path):
            errors.append(f"Knowledge base file not found: {self.knowledge_base.knowledge_base_path}")
        
        if self.api.temperature < 0 or self.api.temperature > 1:
            errors.append("GEMINI_TEMPERATURE must be between 0 and 1")
        
        if self.search.similarity_threshold < 0 or self.search.similarity_threshold > 1:
            errors.append("SIMILARITY_THRESHOLD must be between 0 and 1")
        
        return errors

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.server.cors_origins.split(",")]

# Global configuration instance
config = AppConfig()

def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config

def validate_config() -> None:
    """Validate configuration and raise errors if invalid"""
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}") 