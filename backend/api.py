"""
Flask API for TUM Chatbot Backend
Provides REST API endpoints with CORS, rate limiting, and comprehensive error handling
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import traceback

# Handle imports for both module and direct execution
try:
    from .config import get_config, validate_config
    from .logger import get_logger, RequestLogger, log_error
    from .chatbot import TUMChatbotEngine
    from .statistics import stats_manager
except ImportError:
    from config import get_config, validate_config
    from logger import get_logger, RequestLogger, log_error
    from chatbot import TUMChatbotEngine
    from statistics import stats_manager

logger = get_logger(__name__)

class TUMChatbotAPI:
    """Flask API for TUM Chatbot"""
    
    def __init__(self):
        self.config = get_config()
        self.app = Flask(__name__)
        self.chatbot = TUMChatbotEngine()
        
        # Setup CORS
        if self.config.security.enable_cors:
            CORS(self.app, origins=self.config.get_cors_origins_list())
        
        # Setup rate limiting
        if self.config.security.enable_rate_limiting:
            self.limiter = Limiter(
                app=self.app,
                key_func=get_remote_address,
                default_limits=[f"{self.config.security.rate_limit_requests} per {self.config.security.rate_limit_window} seconds"]
            )
        
        # Setup routes
        self._setup_routes()
        
        # Error handlers
        self._setup_error_handlers()
        
        logger.info("TUM Chatbot API initialized successfully")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': self.config.app_version,
                'environment': self.config.environment
            })
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Main chat endpoint"""
            request_id = str(uuid.uuid4())
            user_id = request.headers.get('X-User-ID', 'anonymous')
            session_id = request.headers.get('X-Session-ID', str(uuid.uuid4()))
            
            with RequestLogger(logger, user_id, session_id, request_id):
                try:
                    # Validate request
                    if not request.is_json:
                        return self._error_response("Request must be JSON", 400, request_id)
                    
                    data = request.get_json()
                    message = data.get('message', '').strip()
                    
                    if not message:
                        return self._error_response("Message is required", 400, request_id)
                    
                    # Check message length
                    if len(message) > 1000:
                        return self._error_response("Message too long (max 1000 characters)", 400, request_id)
                    
                    # Start session if needed
                    if session_id not in self.chatbot.user_sessions:
                        self.chatbot.start_session(session_id, user_id)
                    
                    # Generate response
                    response = self.chatbot.generate_response(message, session_id, user_id)
                    
                    return jsonify({
                        'response': response,
                        'session_id': session_id,
                        'request_id': request_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    log_error(e, "chat endpoint", user_id, session_id)
                    return self._error_response("Internal server error", 500, request_id)
        
        @self.app.route('/api/session/start', methods=['POST'])
        def start_session():
            """Start a new session"""
            request_id = str(uuid.uuid4())
            user_id = request.headers.get('X-User-ID', 'anonymous')
            
            with RequestLogger(logger, user_id, "session_start", request_id):
                try:
                    session_id = str(uuid.uuid4())
                    self.chatbot.start_session(session_id, user_id)
                    
                    return jsonify({
                        'session_id': session_id,
                        'request_id': request_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    log_error(e, "start_session endpoint", user_id, "session_start")
                    return self._error_response("Internal server error", 500, request_id)
        
        @self.app.route('/api/session/<session_id>/end', methods=['POST'])
        def end_session(session_id):
            """End a session"""
            request_id = str(uuid.uuid4())
            user_id = request.headers.get('X-User-ID', 'anonymous')
            
            with RequestLogger(logger, user_id, session_id, request_id):
                try:
                    self.chatbot.end_session(session_id)
                    
                    return jsonify({
                        'session_id': session_id,
                        'status': 'ended',
                        'request_id': request_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    log_error(e, "end_session endpoint", user_id, session_id)
                    return self._error_response("Internal server error", 500, request_id)
        
        @self.app.route('/api/session/<session_id>', methods=['GET'])
        def get_session_info(session_id):
            """Get session information"""
            request_id = str(uuid.uuid4())
            user_id = request.headers.get('X-User-ID', 'anonymous')
            
            with RequestLogger(logger, user_id, session_id, request_id):
                try:
                    session_info = self.chatbot.get_session_info(session_id)
                    
                    if session_info:
                        return jsonify({
                            'session_info': session_info,
                            'request_id': request_id,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    else:
                        return self._error_response("Session not found", 404, request_id)
                    
                except Exception as e:
                    log_error(e, "get_session_info endpoint", user_id, session_id)
                    return self._error_response("Internal server error", 500, request_id)
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """Get usage statistics"""
            request_id = str(uuid.uuid4())
            user_id = request.headers.get('X-User-ID', 'anonymous')
            
            with RequestLogger(logger, user_id, "statistics", request_id):
                try:
                    days = request.args.get('days', 30, type=int)
                    if days < 1 or days > 365:
                        return self._error_response("Days must be between 1 and 365", 400, request_id)
                    
                    stats = stats_manager.get_statistics(days)
                    
                    return jsonify({
                        'statistics': stats,
                        'request_id': request_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    log_error(e, "get_statistics endpoint", user_id, "statistics")
                    return self._error_response("Internal server error", 500, request_id)
        
        @self.app.route('/api/statistics/performance', methods=['GET'])
        def get_performance_metrics():
            """Get performance metrics"""
            request_id = str(uuid.uuid4())
            user_id = request.headers.get('X-User-ID', 'anonymous')
            
            with RequestLogger(logger, user_id, "performance", request_id):
                try:
                    days = request.args.get('days', 7, type=int)
                    if days < 1 or days > 30:
                        return self._error_response("Days must be between 1 and 30", 400, request_id)
                    
                    metrics = stats_manager.get_performance_metrics(days)
                    
                    return jsonify({
                        'performance_metrics': metrics,
                        'request_id': request_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    log_error(e, "get_performance_metrics endpoint", user_id, "performance")
                    return self._error_response("Internal server error", 500, request_id)
        
        @self.app.route('/api/search', methods=['POST'])
        def search():
            """Search endpoint for testing search functionality"""
            request_id = str(uuid.uuid4())
            user_id = request.headers.get('X-User-ID', 'anonymous')
            
            with RequestLogger(logger, user_id, "search", request_id):
                try:
                    if not request.is_json:
                        return self._error_response("Request must be JSON", 400, request_id)
                    
                    data = request.get_json()
                    query = data.get('query', '').strip()
                    method = data.get('method', 'hybrid')
                    top_k = data.get('top_k', 5)
                    
                    if not query:
                        return self._error_response("Query is required", 400, request_id)
                    
                    if method not in ['semantic', 'keyword', 'hybrid']:
                        return self._error_response("Method must be semantic, keyword, or hybrid", 400, request_id)
                    
                    if top_k < 1 or top_k > 20:
                        return self._error_response("Top_k must be between 1 and 20", 400, request_id)
                    
                    # Perform search
                    if method == 'semantic':
                        results = self.chatbot.semantic_search(query, top_k)
                    elif method == 'keyword':
                        results = self.chatbot.keyword_search(query, top_k)
                    else:
                        results = self.chatbot.hybrid_search(query, top_k)
                    
                    return jsonify({
                        'query': query,
                        'method': method,
                        'results': results,
                        'count': len(results),
                        'request_id': request_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    log_error(e, "search endpoint", user_id, "search")
                    return self._error_response("Internal server error", 500, request_id)
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return self._error_response("Endpoint not found", 404)
        
        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return self._error_response("Method not allowed", 405)
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return self._error_response("Internal server error", 500)
        
        @self.app.errorhandler(Exception)
        def handle_exception(error):
            logger.error(f"Unhandled exception: {error}")
            logger.error(traceback.format_exc())
            return self._error_response("Internal server error", 500)
    
    def _error_response(self, message: str, status_code: int, request_id: Optional[str] = None) -> tuple:
        """Create standardized error response"""
        response_data = {
            'error': message,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if request_id:
            response_data['request_id'] = request_id
        
        response = make_response(jsonify(response_data), status_code)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
        """Run the Flask application"""
        host = host or self.config.server.host
        port = port or self.config.server.port
        debug = debug if debug is not None else self.config.server.debug
        
        logger.info(f"Starting TUM Chatbot API on {host}:{port} (debug={debug})")
        self.app.run(host=host, port=port, debug=debug)

def create_app():
    """Factory function to create Flask app"""
    # Validate configuration
    validate_config()
    
    # Create API instance
    api = TUMChatbotAPI()
    return api.app

# For direct execution
if __name__ == '__main__':
    api = TUMChatbotAPI()
    api.run() 