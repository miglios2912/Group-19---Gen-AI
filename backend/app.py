#!/usr/bin/env python3
"""
TUM Chatbot Backend - Main Application Entry Point
Production-ready server with comprehensive logging and monitoring
"""

import os
import sys
import signal
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from config import get_config, validate_config
from logger import setup_logger, get_logger
from api import TUMChatbotAPI

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger = get_logger(__name__)
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main application entry point"""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Setup logging
    logger = setup_logger("tum_chatbot")
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_config()
        logger.info("Configuration validation successful")
        
        # Get configuration
        config = get_config()
        logger.info(f"Starting {config.app_name} v{config.app_version} in {config.environment} mode")
        
        # Create and run API
        api = TUMChatbotAPI()
        api.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 