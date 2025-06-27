"""
TUM Chatbot Backend Package
Production-ready backend with vector database, comprehensive logging, and statistics
"""

__version__ = "1.0.0"
__author__ = "TUM Chatbot Team"

from .config import get_config, validate_config
from .logger import get_logger, setup_logger
from .chatbot import TUMChatbotEngine
from .statistics import stats_manager
from .api import TUMChatbotAPI, create_app

__all__ = [
    'get_config',
    'validate_config', 
    'get_logger',
    'setup_logger',
    'TUMChatbotEngine',
    'stats_manager',
    'TUMChatbotAPI',
    'create_app'
] 