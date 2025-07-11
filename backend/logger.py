"""
Logging module for TUM Chatbot Backend
Provides structured logging with file rotation and multiple handlers
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

# Handle imports for both module and direct execution
try:
    from .config import get_config
except ImportError:
    from config import get_config

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add structured fields
        if not hasattr(record, 'user_id'):
            record.user_id = 'anonymous'
        if not hasattr(record, 'session_id'):
            record.session_id = 'none'
        if not hasattr(record, 'request_id'):
            record.request_id = 'none'
        
        return super().format(record)

def setup_logger(name: str = "tum_chatbot") -> logging.Logger:
    """Setup and configure the application logger"""
    config = get_config()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.logging.log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = StructuredFormatter(
        fmt='%(timestamp)s - %(name)s - %(levelname)s - [%(user_id)s:%(session_id)s:%(request_id)s] - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (only if log file is specified and directory is writable)
    if config.logging.log_file:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(config.logging.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=config.logging.log_file,
                maxBytes=config.logging.max_log_size,
                backupCount=config.logging.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
            
            # Error file handler (separate file for errors)
            error_log_file = config.logging.log_file.replace('.log', '_error.log')
            error_handler = logging.handlers.RotatingFileHandler(
                filename=error_log_file,
                maxBytes=config.logging.max_log_size,
                backupCount=config.logging.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            logger.addHandler(error_handler)
            
        except (OSError, PermissionError) as e:
            # If we can't write to log files, just log to console
            logger.warning(f"Could not setup file logging: {e}. Using console logging only.")
    
    return logger

def get_logger(name: str = "tum_chatbot") -> logging.Logger:
    """Get a logger instance"""
    logger = logging.getLogger(name)
    
    # If this is not the main logger, ensure it has the same handlers
    if name != "tum_chatbot":
        # Get the main logger to inherit its handlers
        main_logger = logging.getLogger("tum_chatbot")
        if main_logger.handlers:
            # Clear any existing handlers and copy from main logger
            logger.handlers.clear()
            for handler in main_logger.handlers:
                logger.addHandler(handler)
            logger.setLevel(main_logger.level)
    
    return logger

class RequestLogger:
    """Context manager for request logging"""
    
    def __init__(self, logger: logging.Logger, user_id: str = "anonymous", 
                 session_id: str = "none", request_id: str = "none"):
        self.logger = logger
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(
            "Request started",
            extra={
                'user_id': self.user_id,
                'session_id': self.session_id,
                'request_id': self.request_id
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                f"Request failed after {duration:.3f}s: {exc_val}",
                extra={
                    'user_id': self.user_id,
                    'session_id': self.session_id,
                    'request_id': self.request_id,
                    'duration': duration,
                    'error_type': exc_type.__name__
                }
            )
        else:
            self.logger.info(
                f"Request completed in {duration:.3f}s",
                extra={
                    'user_id': self.user_id,
                    'session_id': self.session_id,
                    'request_id': self.request_id,
                    'duration': duration
                }
            )

def log_function_call(logger: logging.Logger, function_name: str, **kwargs):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            logger.debug(
                f"Calling {function_name}",
                extra={
                    'function': function_name,
                    'args_count': len(args),
                    'kwargs_count': len(func_kwargs)
                }
            )
            try:
                result = func(*args, **func_kwargs)
                logger.debug(
                    f"Function {function_name} completed successfully",
                    extra={'function': function_name}
                )
                return result
            except Exception as e:
                logger.error(
                    f"Function {function_name} failed: {str(e)}",
                    extra={
                        'function': function_name,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
                raise
        return wrapper
    return decorator

# Global logger instance
logger = setup_logger()

def log_chat_interaction(user_id: str, session_id: str, query: str, response: str, 
                        search_results_count: int, response_time: float, 
                        search_method: str = "hybrid"):
    """Log chat interaction details"""
    logger.info(
        "Chat interaction",
        extra={
            'user_id': user_id,
            'session_id': session_id,
            'query_length': len(query),
            'response_length': len(response),
            'search_results_count': search_results_count,
            'response_time': response_time,
            'search_method': search_method,
            'interaction_type': 'chat'
        }
    )

def log_search_performance(query: str, search_method: str, results_count: int, 
                          search_time: float, similarity_scores: Optional[list] = None):
    """Log search performance metrics"""
    logger.info(
        "Search performance",
        extra={
            'query_length': len(query),
            'search_method': search_method,
            'results_count': results_count,
            'search_time': search_time,
            'avg_similarity': sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
            'max_similarity': max(similarity_scores) if similarity_scores else 0,
            'min_similarity': min(similarity_scores) if similarity_scores else 0
        }
    )

def log_error(error: Exception, context: str = "", user_id: str = "anonymous", 
              session_id: str = "none"):
    """Log errors with context"""
    logger.error(
        f"Error in {context}: {str(error)}",
        extra={
            'user_id': user_id,
            'session_id': session_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
    )

def log_chat_session(user_id: str, session_id: str, query: str, response: str, 
                    user_role: Optional[str] = None, user_campus: Optional[str] = None):
    """Log plain text chat sessions for development debugging"""
    config = get_config()
    
    if not config.logging.log_chat_sessions:
        return
    
    # Strong warning for development mode chat session logging
    if config.environment.lower() == "development":
        print("\n" + "="*80)
        print("⚠️  DEVELOPMENT MODE WARNING ⚠️")
        print("="*80)
        print("🔒 CHAT SESSION LOGGING IS ENABLED")
        print("📝 All user conversations are being logged to:")
        print(f"   {config.logging.chat_session_file}")
        print("⚠️  This includes sensitive user data and should NEVER be enabled in production!")
        print("🔧 To disable: set LOG_CHAT_SESSIONS=False in your .env file")
        print("="*80 + "\n")
    else:
        # Production warning if somehow enabled
        print("\n" + "="*80)
        print("🚨 PRODUCTION SECURITY WARNING 🚨")
        print("="*80)
        print("❌ CHAT SESSION LOGGING IS ENABLED IN PRODUCTION!")
        print("🔒 This is a security risk - user conversations are being logged!")
        print("🛑 IMMEDIATELY DISABLE by setting LOG_CHAT_SESSIONS=False")
        print("="*80 + "\n")
    
    try:
        # Ensure chat session log directory exists
        chat_log_dir = os.path.dirname(config.logging.chat_session_file)
        if chat_log_dir and not os.path.exists(chat_log_dir):
            os.makedirs(chat_log_dir, exist_ok=True)
        
        # Create chat session logger
        chat_logger = logging.getLogger("chat_sessions")
        chat_logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        chat_logger.handlers.clear()
        
        # File handler for chat sessions
        chat_handler = logging.handlers.RotatingFileHandler(
            filename=config.logging.chat_session_file,
            maxBytes=config.logging.max_log_size,
            backupCount=config.logging.backup_count,
            encoding='utf-8'
        )
        chat_handler.setLevel(logging.INFO)
        
        # Simple formatter for chat sessions
        chat_formatter = logging.Formatter(
            fmt='%(asctime)s - %(message)s'
        )
        chat_handler.setFormatter(chat_formatter)
        chat_logger.addHandler(chat_handler)
        
        # Log the chat interaction
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        user_info = f"[{user_role or 'unknown'} at {user_campus or 'unknown campus'}]" if user_role or user_campus else ""
        
        chat_logger.info(f"=== Chat Session: {session_id} {user_info} ===")
        chat_logger.info(f"USER ({user_id}): {query}")
        chat_logger.info(f"BOT: {response}")
        chat_logger.info("---")
        
    except Exception as e:
        # If chat session logging fails, log the error but don't break the application
        logger.warning(f"Failed to log chat session: {e}") 