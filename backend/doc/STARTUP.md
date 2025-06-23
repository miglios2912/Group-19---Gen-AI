# TUM Chatbot Backend - Startup Procedure Documentation

This document provides a comprehensive overview of the TUM Chatbot backend startup procedure, including configuration validation, vector database initialization, and all startup steps.

## Table of Contents

1. [Overview](#overview)
2. [Startup Sequence](#startup-sequence)
3. [Configuration Validation](#configuration-validation)
4. [Vector Database Initialization](#vector-database-initialization)
5. [Statistics Database Setup](#statistics-database-setup)
6. [Logging System Initialization](#logging-system-initialization)
7. [API Server Startup](#api-server-startup)
8. [Error Handling and Recovery](#error-handling-and-recovery)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

## Overview

The TUM Chatbot backend follows a structured startup procedure that ensures all components are properly initialized before accepting requests. The startup process is designed to be robust, with comprehensive error handling and graceful degradation.

### Key Components

- **Configuration Management**: Environment-based configuration with validation
- **Vector Database**: ChromaDB with sentence transformers for semantic search
- **Statistics Database**: SQLite for analytics and performance tracking
- **Logging System**: Structured logging with file rotation
- **API Server**: Flask-based REST API with CORS and rate limiting

## Startup Sequence

The startup sequence follows this order:

```
1. Signal Handler Setup
2. Logging System Initialization
3. Configuration Validation
4. Statistics Database Initialization
5. Vector Database Initialization
6. API Server Startup
7. Health Check Endpoint Activation
```

### Detailed Flow

```python
# Entry point: app.py -> main()
def main():
    # 1. Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 2. Setup logging
    logger = setup_logger("tum_chatbot")

    # 3. Validate configuration
    validate_config()

    # 4. Create and run API
    api = TUMChatbotAPI()  # This initializes everything
    api.run()
```

## Configuration Validation

### Configuration Loading Process

1. **Environment File Loading**: Uses `python-dotenv` to load `.env` file
2. **Environment Variable Processing**: Converts string values to appropriate types
3. **Validation**: Checks for required fields and valid value ranges

### Configuration Structure

```python
@dataclass
class AppConfig:
    # Core application settings
    app_name: str
    app_version: str
    environment: str

    # Sub-configurations
    database: DatabaseConfig      # ChromaDB settings
    api: APIConfig               # Gemini API settings
    search: SearchConfig         # Search parameters
    server: ServerConfig         # Flask server settings
    logging: LoggingConfig       # Logging configuration
    statistics: StatisticsConfig # Analytics settings
    security: SecurityConfig     # Security settings
    knowledge_base: KnowledgeBaseConfig # Knowledge base settings
```

### Validation Rules

```python
def validate(self) -> list[str]:
    errors = []

    # Required API key
    if not self.api.gemini_api_key:
        errors.append("GEMINI_API_KEY is required")

    # Knowledge base file existence
    if not os.path.exists(self.knowledge_base.knowledge_base_path):
        errors.append(f"Knowledge base file not found: {self.knowledge_base.knowledge_base_path}")

    # Value range validation
    if self.api.temperature < 0 or self.api.temperature > 1:
        errors.append("GEMINI_TEMPERATURE must be between 0 and 1")

    if self.search.similarity_threshold < 0 or self.search.similarity_threshold > 1:
        errors.append("SIMILARITY_THRESHOLD must be between 0 and 1")

    return errors
```

### Environment Variables

Key environment variables that must be set:

```bash
# Required
GEMINI_API_KEY=your_actual_api_key

# Optional (with defaults)
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MAX_TOKENS=4096
GEMINI_TEMPERATURE=0.7
CHROMA_DB_PATH=./chroma_db
KNOWLEDGE_BASE_PATH=./TUM_QA.json
LOG_LEVEL=INFO
ENABLE_STATISTICS=True
```

## Vector Database Initialization

### ChromaDB Setup Process

The vector database initialization is handled in the `TUMChatbotEngine.__init__()` method:

```python
def __init__(self):
    # 1. Initialize Gemini API
    genai.configure(api_key=self.config.api.gemini_api_key)
    self.model = genai.GenerativeModel(...)

    # 2. Initialize sentence transformer
    self.embedding_model = SentenceTransformer(self.config.search.embedding_model)

    # 3. Initialize ChromaDB client
    self.chroma_client = chromadb.PersistentClient(path=self.config.database.chroma_db_path)

    # 4. Load knowledge base
    self.knowledge_base = self._load_knowledge_base()

    # 5. Setup vector database
    self._setup_vector_database()
```

### Vector Database Decision Logic

The system determines whether to create a new vector database or use an existing one:

```python
def _setup_vector_database(self):
    """Setup ChromaDB collection with embeddings"""
    try:
        # Try to get existing collection
        self.collection = self.chroma_client.get_collection(self.collection_name)
        self.logger.info(f"Using existing vector database with {self.collection.count()} documents")
    except:
        # Create new collection if it doesn't exist
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"description": "TUM Q&A Knowledge Base"}
        )

        # Prepare and add documents
        self._add_documents_to_collection()
        self.logger.info(f"Created vector database with {len(documents)} documents")
```

### Decision Criteria

The system creates a new vector database when:

1. **Collection doesn't exist**: First-time startup or collection was deleted
2. **ChromaDB client fails**: Database corruption or permission issues
3. **Collection access fails**: Any exception during `get_collection()`

The system reuses existing vector database when:

1. **Collection exists**: `get_collection()` succeeds
2. **Collection has documents**: `collection.count()` returns > 0
3. **No exceptions**: Clean access to existing collection

### Document Processing

When creating a new vector database, documents are processed as follows:

```python
def _add_documents_to_collection(self):
    documents = []
    metadatas = []
    ids = []

    for doc in self.knowledge_base:
        # Create searchable text combining all fields
        searchable_text = f"{doc['question']} {doc['answer']} {' '.join(doc['keywords'])} {doc['category']} {doc['role']}"

        documents.append(searchable_text)
        metadatas.append({
            'id': doc['id'],
            'category': doc['category'],
            'role': doc['role'],
            'question': doc['question'],
            'answer': doc['answer'],
            'keywords': ','.join(doc['keywords']),
            'source': doc.get('source', '')
        })
        ids.append(doc['id'])

    # Add to ChromaDB collection
    self.collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
```

### Vector Database Storage

The vector database is stored persistently:

- **Development**: `./chroma_db/` (relative to backend directory)
- **Docker**: `/app/chroma_db/` (inside container)
- **Files**:
  - `chroma.sqlite3` - Metadata and indexes
  - Binary vector data files
  - Collection metadata

## Statistics Database Setup

### Database Initialization

The statistics database is initialized in the `StatisticsManager`:

```python
def initialize_database(self):
    """Initialize the statistics database with required tables"""
    try:
        # Ensure database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        with sqlite3.connect(self.db_path, timeout=30) as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL;")

            # Create tables
            self._create_chat_interactions_table(conn)
            self._create_search_performance_table(conn)
            self._create_user_sessions_table(conn)
            self._create_query_analytics_table(conn)

            # Create indexes
            self._create_indexes(conn)

            conn.commit()
            logger.info("Statistics database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize statistics database: {e}")
        raise
```

### Database Schema

The statistics database contains four main tables:

1. **chat_interactions**: Records of all chat exchanges
2. **search_performance**: Search method performance metrics
3. **user_sessions**: User session tracking
4. **query_analytics**: Query frequency and performance analysis

### WAL Mode Configuration

The database uses WAL (Write-Ahead Logging) mode for better concurrency:

```python
conn.execute("PRAGMA journal_mode=WAL;")
```

This prevents "database is locked" errors during concurrent access.

## Logging System Initialization

### Logger Setup

The logging system is initialized with multiple handlers:

```python
def setup_logger(name: str = "tum_chatbot") -> logging.Logger:
    config = get_config()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.logging.log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (INFO level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation (DEBUG level)
    if config.logging.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.logging.log_file,
            maxBytes=config.logging.max_log_size,
            backupCount=config.logging.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    # Error file handler (ERROR level)
    error_log_file = config.logging.log_file.replace('.log', '_error.log')
    error_handler = logging.handlers.RotatingFileHandler(...)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
```

### Log Levels

- **Console**: INFO and above (for development visibility)
- **File**: DEBUG and above (for detailed debugging)
- **Error File**: ERROR and above (for error tracking)

### Chat Session Logging

Optional plain text chat session logging for development:

```python
def log_chat_session(user_id: str, session_id: str, query: str, response: str,
                    user_role: Optional[str] = None, user_campus: Optional[str] = None):
    """Log plain text chat sessions for development debugging"""
    config = get_config()

    if not config.logging.log_chat_sessions:
        return

    # Create separate logger for chat sessions
    chat_logger = logging.getLogger("chat_sessions")
    # ... logging implementation
```

## API Server Startup

### Flask Application Initialization

The API server is initialized in the `TUMChatbotAPI` class:

```python
def __init__(self):
    self.config = get_config()
    self.app = Flask(__name__)
    self.chatbot = TUMChatbotEngine()  # This initializes everything

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

    # Setup routes and error handlers
    self._setup_routes()
    self._setup_error_handlers()
```

### Route Setup

The API provides these endpoints:

- `GET /api/health` - Health check
- `POST /api/chat` - Main chat endpoint
- `POST /api/session/start` - Start session
- `POST /api/session/{id}/end` - End session
- `GET /api/session/{id}` - Get session info
- `GET /api/statistics` - Get usage statistics
- `GET /api/statistics/performance` - Get performance metrics
- `POST /api/search` - Test search functionality

### Server Startup

```python
def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
    """Start the Flask development server"""
    host = host or self.config.server.host
    port = port or self.config.server.port
    debug = debug if debug is not None else self.config.server.debug

    logger.info(f"Starting Flask server on {host}:{port} (debug={debug})")
    self.app.run(host=host, port=port, debug=debug)
```

## Error Handling and Recovery

### Graceful Shutdown

Signal handlers ensure graceful shutdown:

```python
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger = get_logger(__name__)
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Docker stop
```

### Error Recovery

The system implements multiple layers of error recovery:

1. **Configuration Validation**: Fails fast if configuration is invalid
2. **Database Connection Retry**: SQLite with timeout and WAL mode
3. **Vector Database Fallback**: Falls back to keyword search if semantic search fails
4. **API Error Handling**: Comprehensive error responses with request IDs

### Error Response Format

```python
def _error_response(self, message: str, status_code: int, request_id: Optional[str] = None) -> tuple:
    """Generate standardized error response"""
    response_data = {
        'error': message,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat()
    }

    if request_id:
        response_data['request_id'] = request_id

    return jsonify(response_data), status_code
```

## Performance Considerations

### Startup Time Optimization

1. **Lazy Loading**: Sentence transformer is loaded only when needed
2. **Connection Reuse**: SQLite connections are reused within operations
3. **WAL Mode**: Prevents database locks during concurrent access
4. **Efficient Logging**: Asynchronous file operations

### Memory Usage

- **Sentence Transformer**: ~100MB (all-MiniLM-L6-v2)
- **ChromaDB**: ~50-100MB for 2400 documents
- **Statistics Database**: ~1-5MB depending on usage
- **Flask Application**: ~20-50MB

### Disk Usage

- **Vector Database**: ~50-100MB
- **Statistics Database**: ~1-10MB
- **Log Files**: ~10-50MB (with rotation)

## Troubleshooting

### Common Startup Issues

#### 1. Configuration Errors

**Problem**: `Configuration errors: GEMINI_API_KEY is required`

**Solution**:

```bash
# Set the API key in .env file
echo "GEMINI_API_KEY=your_actual_api_key" >> .env
```

#### 2. Knowledge Base Not Found

**Problem**: `Knowledge base file not found: ./TUM_QA.json`

**Solution**:

```bash
# Ensure TUM_QA.json exists in the correct location
ls -la backend/TUM_QA.json

# Or update the path in .env
echo "KNOWLEDGE_BASE_PATH=/path/to/TUM_QA.json" >> .env
```

#### 3. Database Permission Issues

**Problem**: `Failed to initialize statistics database: [Errno 13] Permission denied`

**Solution**:

```bash
# Fix directory permissions
chmod 755 backend/
chmod 755 backend/data/

# Or run with appropriate permissions
sudo chown -R $USER:$USER backend/
```

#### 4. Vector Database Corruption

**Problem**: ChromaDB collection access fails

**Solution**:

```bash
# Remove corrupted database
rm -rf backend/chroma_db/

# Restart application (will recreate database)
python backend/app.py
```

#### 5. Memory Issues

**Problem**: Out of memory during startup

**Solution**:

```bash
# Reduce memory usage
export GEMINI_MAX_TOKENS=2048
export SEMANTIC_SEARCH_TOP_K=3

# Or use smaller embedding model
export EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set debug environment variables
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
export LOG_CHAT_SESSIONS=True

# Start application
python backend/app.py
```

### Health Check

Verify the application is running correctly:

```bash
# Check health endpoint
curl http://localhost:8080/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "1.0.0",
  "environment": "development"
}
```

### Log Analysis

Check logs for startup issues:

```bash
# View application logs
tail -f backend/logs/tum_chatbot.log

# View error logs
tail -f backend/logs/tum_chatbot_error.log

# View chat sessions (if enabled)
tail -f backend/logs/chat_sessions.log
```

### Database Verification

Verify database integrity:

```bash
# Check statistics database
sqlite3 backend/statistics.db "SELECT COUNT(*) FROM chat_interactions;"

# Check vector database
ls -la backend/chroma_db/
```

## Startup Time Benchmarks

Typical startup times on different systems:

| System              | Startup Time | Notes                            |
| ------------------- | ------------ | -------------------------------- |
| Development (SSD)   | 3-5 seconds  | Fast disk, good CPU              |
| Development (HDD)   | 5-8 seconds  | Slower disk access               |
| Docker (first run)  | 8-12 seconds | Image building, downloads        |
| Docker (subsequent) | 4-6 seconds  | Cached layers                    |
| Production server   | 6-10 seconds | Network latency, larger datasets |

### Optimization Tips

1. **Use SSD storage** for faster database access
2. **Pre-build Docker images** for production deployment
3. **Use smaller embedding models** if memory is constrained
4. **Disable debug logging** in production
5. **Use connection pooling** for high-traffic deployments

## Conclusion

The TUM Chatbot backend startup procedure is designed to be robust, efficient, and maintainable. The system automatically handles vector database creation, configuration validation, and graceful error recovery. The modular design allows for easy troubleshooting and performance optimization.

For production deployments, ensure proper monitoring of startup times and resource usage, and consider implementing health checks and automated recovery procedures.
