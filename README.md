# TUM Chatbot - Production-Ready RAG-Powered University Assistant

A sophisticated, production-ready chatbot for the Technical University of Munich (TUM) that uses Retrieval-Augmented Generation (RAG) with vector database integration to provide accurate, contextual answers to student and staff questions.

## 🚀 Features

### Core Functionality

- **Vector Database Integration**: ChromaDB with sentence transformers for semantic search
- **Hybrid Search**: Combines semantic and keyword-based search for optimal results
- **Context-Aware**: Remembers user role (student/employee) and campus location
- **Comprehensive Knowledge Base**: 2400+ Q&A entries covering all aspects of university life
- **Multi-Campus Support**: Munich, Heilbronn, and Singapore campuses
- **Conversation Memory**: Maintains context across multiple interactions

### Production Features

- **Comprehensive Logging**: Structured logging with file rotation and multiple handlers
- **Statistics & Analytics**: Track usage, performance, and user interactions
- **RESTful API**: Clean REST API with comprehensive endpoints
- **Session Management**: User session tracking and management
- **Rate Limiting**: Configurable per-IP rate limits
- **CORS Support**: Configurable cross-origin resource sharing
- **Error Handling**: Comprehensive error handling and graceful degradation
- **Environment Configuration**: Fully configurable via environment variables
- **Docker Support**: Production-ready containerization

### Frontend Features

- **Modern React Interface**: Clean, responsive UI with Tailwind CSS
- **Real-time Chat**: Live chat interface with loading states
- **Session Management**: Automatic session handling
- **Error Handling**: User-friendly error messages
- **Copy to Clipboard**: Easy response copying

## 📋 Requirements

- **Python 3.11+** (for compatibility with scientific packages)
- **Node.js 16+** (for frontend)
- **Google Gemini API key**
- **4GB+ RAM** (for vector database operations)
- **Docker & Docker Compose** (for production deployment)

## 🔧 Environment Configuration

### Overview

The TUM Chatbot uses a **single environment setting** that automatically configures all environment-specific behavior. This eliminates confusion and ensures consistent configuration.

### Environment Setting

Set `ENVIRONMENT` in your `.env` file to either:

- `ENVIRONMENT=development` - For local development
- `ENVIRONMENT=production` - For production deployment

### Automatic Configuration

Based on the `ENVIRONMENT` setting, the system automatically configures:

| Setting             | Development          | Production | Override                           |
| ------------------- | -------------------- | ---------- | ---------------------------------- |
| `FLASK_DEBUG`       | `True`               | `False`    | Set `FLASK_DEBUG=True/False`       |
| `LOG_LEVEL`         | `DEBUG`              | `WARNING`  | Set `LOG_LEVEL=DEBUG/INFO/WARNING` |
| `LOG_CHAT_SESSIONS` | `True`               | `False`    | Set `LOG_CHAT_SESSIONS=True/False` |
| Error Messages      | Verbose              | Minimal    | N/A                                |
| CORS Origins        | Development-friendly | Strict     | Set `CORS_ORIGINS`                 |
| Security            | Development          | Enhanced   | N/A                                |

### Configuration Priority

1. **Explicit Environment Variables** - If you set a value in `.env`, it takes precedence
2. **Environment-Based Defaults** - If not set, uses development/production defaults
3. **System Defaults** - Fallback values for all environments

### Example Configurations

#### Development Environment (`.env`)

```bash
# Set environment
ENVIRONMENT=development

# Required API key
GEMINI_API_KEY=your_actual_api_key

# Optional overrides (will use development defaults if not set)
# FLASK_DEBUG=True          # Automatically True in development
# LOG_LEVEL=DEBUG           # Automatically DEBUG in development
# LOG_CHAT_SESSIONS=True    # Automatically True in development
```

#### Production Environment (`.env`)

```bash
# Set environment
ENVIRONMENT=production

# Required API key
GEMINI_API_KEY=your_actual_api_key

# Production-specific settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional overrides (will use production defaults if not set)
# FLASK_DEBUG=False         # Automatically False in production
# LOG_LEVEL=WARNING         # Automatically WARNING in production
# LOG_CHAT_SESSIONS=False   # Automatically False in production
```

## 🐳 Quick Start with Docker (Recommended)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd "TUM Chatbot"
```

### 2. Configure Environment

```bash
# Copy environment template
cp backend/docker.env.example .env

# Edit .env and set your Gemini API key
nano .env
```

**Required Configuration:**

```bash
# Set environment (development or production)
ENVIRONMENT=production

# Set your actual Gemini API key
GEMINI_API_KEY=your_actual_api_key_here
```

**Optional Production Settings:**

```bash
# Update CORS origins for your frontend domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Adjust rate limiting for your traffic
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### 3. Start with Docker Compose

```bash
# Build and start the backend
docker-compose up -d tum-chatbot-backend

# Check logs
docker-compose logs -f tum-chatbot-backend

# Check health
curl http://localhost:8080/api/health
```

### 4. Access the Application

- **Backend API**: http://localhost:8080
- **Health Check**: http://localhost:8080/api/health
- **API Documentation**: See API Endpoints section below

## 🛠️ Development Setup

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Create virtual environment:**

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**

   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

   **Required for development:**

   ```bash
   ENVIRONMENT=development
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Start the backend:**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Configure environment:**

   ```bash
   echo "VITE_API_BASE_URL=http://localhost:8080" > .env
   ```

4. **Start the frontend:**
   ```bash
   npm run dev
   ```

## 📊 Logging and Monitoring

### Log Structure

The application uses structured logging with multiple handlers:

- **Console Handler**: INFO level and above (for development)
- **File Handler**: DEBUG level and above with rotation (for production)
- **Error Handler**: ERROR level and above (separate file)

### Log Format

```
2024-01-01T12:00:00.123Z - tum_chatbot - INFO - [user123:session456:req789] - Request completed in 1.234s
```

### Log Files (Docker)

- **Main log**: `/app/logs/tum_chatbot.log` (mounted to `./logs/tum_chatbot.log`)
- **Error log**: `/app/logs/tum_chatbot_error.log` (mounted to `./logs/tum_chatbot_error.log`)

### Accessing Logs

```bash
# View logs in Docker
docker-compose logs -f tum-chatbot-backend

# View log files directly
tail -f logs/tum_chatbot.log
tail -f logs/tum_chatbot_error.log

# Search logs
grep "ERROR" logs/tum_chatbot.log
```

### Chat Session Logging (Development)

For debugging conversation issues, chat session logging is **automatically enabled in development** and **automatically disabled in production**.

**Development (automatic):**

```bash
ENVIRONMENT=development
# LOG_CHAT_SESSIONS=True  # Automatically True
```

**Production (automatic):**

```bash
ENVIRONMENT=production
# LOG_CHAT_SESSIONS=False  # Automatically False
```

**Manual override (if needed):**

```bash
ENVIRONMENT=development
LOG_CHAT_SESSIONS=False  # Override to disable
```

**Example chat session log**:

```
2024-01-01 12:00:00 - === Chat Session: session123 [professor at Heilbronn] ===
2024-01-01 12:00:00 - USER (user123): Hello, I am a professor at the Heilbronn campus looking for places to engage with students.
2024-01-01 12:00:00 - BOT: As a professor at TUM Heilbronn, you can find students engaging in various activities...
2024-01-01 12:00:00 - ---
```

**⚠️ Security Note**: Chat session logs contain user queries and are automatically disabled in production for security.

## 📈 Statistics and Analytics

### What's Tracked

The backend tracks comprehensive statistics in SQLite:

- **Chat Interactions**: Query, response, timing, search method
- **Search Performance**: Method, results count, similarity scores
- **User Sessions**: Duration, interaction count, user context
- **Query Analytics**: Frequency, average response time

### Accessing Statistics

#### Via API

```bash
# Get usage statistics (last 30 days)
curl "http://localhost:8080/api/statistics?days=30"

# Get performance metrics (last 7 days)
curl "http://localhost:8080/api/statistics/performance?days=7"

# Get statistics for specific time periods
curl "http://localhost:8080/api/statistics?days=1"    # Last 24 hours
curl "http://localhost:8080/api/statistics?days=7"    # Last week
curl "http://localhost:8080/api/statistics?days=30"   # Last month
curl "http://localhost:8080/api/statistics?days=90"   # Last quarter

# Get performance metrics for different periods
curl "http://localhost:8080/api/statistics/performance?days=1"   # Last 24 hours
curl "http://localhost:8080/api/statistics/performance?days=7"   # Last week
curl "http://localhost:8080/api/statistics/performance?days=30"  # Last month
```

#### Example API Responses

**Usage Statistics Response:**

```json
{
	"statistics": {
		"period_days": 30,
		"total_interactions": 1250,
		"avg_response_time": 1.234,
		"search_methods": {
			"hybrid": 850,
			"semantic": 300,
			"keyword": 100
		},
		"user_roles": {
			"student": 900,
			"employee": 300,
			"visitor": 50
		},
		"campuses": {
			"Munich": 800,
			"Heilbronn": 300,
			"Singapore": 150
		},
		"top_queries": [
			["Where is the library?", 45],
			["How do I set up email?", 32],
			["Library opening hours", 28]
		],
		"active_sessions": 15,
		"generated_at": "2024-01-01T12:00:00.000Z"
	},
	"request_id": "abc123",
	"timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Performance Metrics Response:**

```json
{
	"performance_metrics": {
		"period_days": 7,
		"search_performance": [
			["hybrid", 0.592, 16.67, -0.222, 15],
			["semantic", 0.143, 10.0, -0.222, 15]
		],
		"response_time_percentiles": {
			"p50": 3.193,
			"p95": 4.768,
			"p99": 4.768
		},
		"generated_at": "2024-01-01T12:00:00.000Z"
	},
	"request_id": "def456",
	"timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### Direct Database Access

```bash
# Access the SQLite database
docker exec -it tum-chatbot-backend sqlite3 /app/data/statistics.db

# Example queries
SELECT COUNT(*) FROM chat_interactions WHERE timestamp >= datetime('now', '-7 days');
SELECT search_method, COUNT(*) FROM chat_interactions GROUP BY search_method;
```

### Data Privacy

- **User IDs are anonymized** by default (configurable)
- **No personal information** is stored
- **All data is stored locally** in SQLite
- **Data retention** can be configured

## 🗑️ Clearing Statistics and Performance Data

### Clear All Statistics

**⚠️ Warning**: This will permanently delete all statistics and performance data.

```bash
# Development environment
rm backend/statistics.db

# Production environment (Docker)
docker exec tum-chatbot-backend rm /app/data/statistics.db

# The database will be automatically recreated on next startup
```

### Clear Specific Data Types

```bash
# Access the database
sqlite3 backend/statistics.db

# Clear chat interactions only
DELETE FROM chat_interactions;

# Clear search performance data only
DELETE FROM search_performance;

# Clear user sessions only
DELETE FROM user_sessions;

# Clear query analytics only
DELETE FROM query_analytics;

# Clear data older than 30 days
DELETE FROM chat_interactions WHERE timestamp < datetime('now', '-30 days');
DELETE FROM search_performance WHERE timestamp < datetime('now', '-30 days');
DELETE FROM user_sessions WHERE start_time < datetime('now', '-30 days');

# Reset auto-increment counters
DELETE FROM sqlite_sequence WHERE name IN ('chat_interactions', 'search_performance', 'user_sessions', 'query_analytics');

# Optimize database after deletions
VACUUM;
ANALYZE;
```

### Backup Before Clearing

```bash
# Create backup
cp backend/statistics.db backend/statistics_backup_$(date +%Y%m%d_%H%M%S).db

# Or compress backup
sqlite3 backend/statistics.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore from backup
cp backup_20241201_143022.db backend/statistics.db
```

### Automated Cleanup Script

Create a cleanup script (`cleanup_stats.sh`):

```bash
#!/bin/bash
# Cleanup statistics data

echo "=== TUM Chatbot Statistics Cleanup ==="
echo "Timestamp: $(date)"
echo

# Backup current data
BACKUP_FILE="statistics_backup_$(date +%Y%m%d_%H%M%S).db"
echo "Creating backup: $BACKUP_FILE"
cp backend/statistics.db "backend/$BACKUP_FILE"

# Show current data counts
echo "Current data counts:"
sqlite3 backend/statistics.db "SELECT 'chat_interactions' as table_name, COUNT(*) as count FROM chat_interactions UNION ALL SELECT 'search_performance', COUNT(*) FROM search_performance UNION ALL SELECT 'user_sessions', COUNT(*) FROM user_sessions UNION ALL SELECT 'query_analytics', COUNT(*) FROM query_analytics;"

echo
read -p "Do you want to clear all statistics? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Clearing all statistics..."
    sqlite3 backend/statistics.db "DELETE FROM chat_interactions; DELETE FROM search_performance; DELETE FROM user_sessions; DELETE FROM query_analytics; DELETE FROM sqlite_sequence; VACUUM; ANALYZE;"
    echo "Statistics cleared successfully!"
else
    echo "Operation cancelled."
fi
```

Make it executable: `chmod +x cleanup_stats.sh`

## 📊 Performance Metrics Explained

### Response Time Percentiles

**What they measure**: Distribution of response times across all chat interactions.

**Calculation**:

- **P50 (Median)**: 50% of requests complete within this time
- **P95**: 95% of requests complete within this time
- **P99**: 99% of requests complete within this time

**Example**: P50=1.2s, P95=3.5s means:

- 50% of requests complete in ≤1.2 seconds
- 95% of requests complete in ≤3.5 seconds
- 5% of requests take >3.5 seconds

**Formula**: Sort all response times, then take the value at the specified percentile position.

### Search Performance Metrics

**What they measure**: Effectiveness and efficiency of different search methods.

**Metrics per search method**:

1. **Average Search Time** (seconds): Mean time to execute search
2. **Average Results Count**: Mean number of documents returned
3. **Average Similarity Score**: Mean relevance score of returned documents
4. **Total Searches**: Number of searches performed

**Similarity Score Calculation**:

- **Range**: -1.0 to 1.0 (higher = more relevant)
- **Formula**: `1 - distance` where distance is ChromaDB's cosine distance
- **Interpretation**:
  - 0.8-1.0: Very relevant
  - 0.6-0.8: Relevant
  - 0.4-0.6: Somewhat relevant
  - 0.0-0.4: Low relevance
  - Negative: Very low relevance

### Search Method Distribution

**What it measures**: How often each search method is used and its effectiveness.

**Methods**:

- **Hybrid**: Combines semantic + keyword search (most comprehensive)
- **Semantic**: Vector similarity search (best for conceptual queries)
- **Keyword**: Text matching search (fallback method)

**Usage Patterns**:

- High hybrid usage = Good system performance
- High keyword usage = May indicate semantic search issues
- High semantic usage = Good for conceptual queries

### User Interaction Analytics

**What they measure**: User behavior and system usage patterns.

**Metrics**:

- **Total Interactions**: Total number of chat exchanges
- **Average Response Time**: Mean time from query to response
- **Active Sessions**: Number of ongoing user sessions
- **User Role Distribution**: Breakdown by student/employee/visitor
- **Campus Distribution**: Usage across Munich/Heilbronn/Singapore

### Query Analytics

**What they measure**: Most common queries and their performance.

**Metrics per query**:

- **Frequency**: How often this query appears
- **Average Response Time**: Mean time to answer this query
- **Success Rate**: Percentage of successful responses (default 1.0)
- **First Seen**: When this query was first encountered
- **Last Seen**: When this query was last encountered

**Query Hashing**: Queries are hashed (SHA-256) for privacy and efficiency.

### Performance Impact Analysis

**Database Operations**:

- **Chat Interaction Recording**: ~1-2ms per request
- **Query Analytics Update**: ~1ms per request
- **Search Performance Logging**: ~0.5ms per search
- **Session Management**: ~0.5ms per session

**Memory Usage**:

- **Statistics Database**: ~50-100KB per 1000 interactions
- **Query Analytics**: ~10-20KB per 100 unique queries
- **Session Data**: ~1KB per active session

**Storage Growth**:

- **Chat Interactions**: ~2KB per interaction
- **Search Performance**: ~1KB per search
- **User Sessions**: ~500 bytes per session
- **Query Analytics**: ~200 bytes per unique query

### Performance Optimization

**For High-Traffic Deployments**:

```bash
# Regular database maintenance
sqlite3 backend/statistics.db "VACUUM; ANALYZE;"

# Archive old data (older than 90 days)
sqlite3 backend/statistics.db "DELETE FROM chat_interactions WHERE timestamp < datetime('now', '-90 days');"

# Monitor database size
ls -lh backend/statistics.db

# Check query performance
sqlite3 backend/statistics.db "SELECT COUNT(*) as total_interactions, AVG(response_time) as avg_response_time FROM chat_interactions WHERE timestamp >= datetime('now', '-7 days');"
```

## ⚡ Performance Considerations

### Logging Performance Impact

The logging system is designed to be **minimal impact** on performance:

- **Asynchronous Logging**: File operations are non-blocking
- **Log Rotation**: Prevents disk space issues
- **Configurable Levels**: Can reduce logging in production
- **Efficient Formatting**: Minimal string operations

**Performance Impact**: < 1ms per request

**Recommendations**:

```bash
# For high-traffic production
LOG_LEVEL=WARNING          # Reduce log volume
MAX_LOG_SIZE=5242880       # 5MB rotation
LOG_BACKUP_COUNT=3         # Keep fewer backups
```

### Statistics Performance Impact

Statistics tracking is **optimized for minimal overhead**:

- **Single Database Connection**: Reuses connections to avoid locks
- **Batch Operations**: Efficient SQLite operations
- **Configurable Tracking**: Can disable specific features
- **Non-blocking**: Database operations don't block responses

**Performance Impact**: < 2ms per request

**Recommendations**:

```bash
# For maximum performance
ENABLE_STATISTICS=True     # Keep enabled for insights
TRACK_QUERY_ANALYTICS=True # Valuable for optimization
TRACK_USER_SESSIONS=True   # Useful for user behavior
ANONYMIZE_DATA=True        # Privacy compliance
```

### Performance Monitoring

Monitor the impact with these commands:

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8080/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test" \
  -H "X-Session-ID: test" \
  -d '{"message": "test"}'

# Monitor database size
ls -lh backend/statistics.db

# Check log file sizes
ls -lh backend/logs/

# Performance metrics
curl "http://localhost:8080/api/statistics/performance?days=1"
```

### Scaling Considerations

For high-traffic deployments:

1. **Database Optimization**:

   ```bash
   # Regular maintenance
   sqlite3 backend/statistics.db "VACUUM;"
   sqlite3 backend/statistics.db "ANALYZE;"
   ```

2. **Log Management**:

   ```bash
   # Log rotation and cleanup
   find backend/logs/ -name "*.log.*" -mtime +7 -delete
   ```

3. **Resource Monitoring**:

   ```bash
   # Monitor memory usage
   docker stats tum-chatbot-backend

   # Check disk usage
   du -sh backend/data/ backend/logs/
   ```

## 📡 API Endpoints

### Core Endpoints

- `POST /api/chat` - Main chat endpoint
- `POST /api/session/start` - Start a new session
- `POST /api/session/{id}/end` - End a session
- `GET /api/session/{id}` - Get session information
- `GET /api/health` - Health check

### Analytics Endpoints

- `GET /api/statistics?days=30` - Get usage statistics
- `GET /api/statistics/performance?days=7` - Get performance metrics
- `POST /api/search` - Test search functionality

### Example Usage

```bash
# Start a session
curl -X POST http://localhost:8080/api/session/start \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123"

# Send a message
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -H "X-Session-ID: session456" \
  -d '{"message": "Where is the library?"}'

# Get statistics
curl http://localhost:8080/api/statistics?days=7
```

### Practical Statistics Examples

```bash
# Monitor daily usage
curl "http://localhost:8080/api/statistics?days=1" | jq '.statistics.total_interactions'

# Check response time performance
curl "http://localhost:8080/api/statistics/performance?days=7" | jq '.performance_metrics.response_time_percentiles'

# Monitor search method effectiveness
curl "http://localhost:8080/api/statistics?days=30" | jq '.statistics.search_methods'

# Get top queries for optimization
curl "http://localhost:8080/api/statistics?days=30" | jq '.statistics.top_queries'

# Check user distribution
curl "http://localhost:8080/api/statistics?days=30" | jq '.statistics.user_roles'

# Monitor campus usage
curl "http://localhost:8080/api/statistics?days=30" | jq '.statistics.campuses'

# Performance testing with timing
curl -w "@curl-format.txt" -o /dev/null -s \
  -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: perf_test" \
  -H "X-Session-ID: perf_test" \
  -d '{"message": "test message"}'
```

### Automated Monitoring Script

Create a monitoring script (`monitor.sh`):

```bash
#!/bin/bash
# Monitor TUM Chatbot performance

echo "=== TUM Chatbot Performance Monitor ==="
echo "Timestamp: $(date)"
echo

# Health check
echo "Health Status:"
curl -s http://localhost:8080/api/health | jq -r '.status'
echo

# Today's statistics
echo "Today's Usage:"
curl -s "http://localhost:8080/api/statistics?days=1" | jq '.statistics | {total_interactions, avg_response_time, active_sessions}'
echo

# Performance metrics
echo "Performance (7 days):"
curl -s "http://localhost:8080/api/statistics/performance?days=7" | jq '.performance_metrics.response_time_percentiles'
echo

# Database size
echo "Database Size:"
ls -lh backend/statistics.db
echo

# Log file sizes
echo "Log File Sizes:"
ls -lh backend/logs/
echo
```

Make it executable: `chmod +x monitor.sh`

## 🚀 Production Deployment

### Docker Production Deployment

```bash
# 1. Create production .env file
cp backend/docker.env.example .env

# 2. Edit .env for production
nano .env
# Set: ENVIRONMENT=production
# Set: GEMINI_API_KEY=your_actual_key
# Set: CORS_ORIGINS=https://yourdomain.com

# 3. Navigate to backend directory
cd backend

# 4. Deploy with Docker Compose
docker-compose up -d

# 5. Check deployment
docker-compose logs -f tum-chatbot-backend
curl http://localhost:8080/api/health
```

### Docker Environment Configuration

The `docker-compose.yml` file uses environment variables with sensible defaults:

- **Required**: `ENVIRONMENT`, `GEMINI_API_KEY`
- **Optional**: All other settings with defaults
- **Automatic**: Environment-specific settings based on `ENVIRONMENT`

**Example minimal `.env` for production:**

```bash
ENVIRONMENT=production
GEMINI_API_KEY=your_actual_api_key_here
CORS_ORIGINS=https://yourdomain.com
```

**Example minimal `.env` for development:**

```bash
ENVIRONMENT=development
GEMINI_API_KEY=your_actual_api_key_here
```

## 🔧 Development

### Project Structure

```
TUM Chatbot/
├── backend/                 # Production-ready backend
│   ├── __init__.py         # Package initialization
│   ├── app.py              # Main application entry point
│   ├── api.py              # Flask API implementation
│   ├── chatbot.py          # Core chatbot engine
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging setup
│   ├── statistics.py       # Analytics and statistics
│   ├── requirements.txt    # Python dependencies
│   ├── env_example.txt     # Development environment template
│   ├── docker.env.example  # Docker environment template
│   ├── Dockerfile          # Backend Docker image
│   ├── docker-compose.yml  # Backend service configuration
│   └── .dockerignore       # Docker build exclusions
├── frontend/               # React frontend
├── TUM_QA.json            # Knowledge base
└── README.md              # This file
```

### Running Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

### Code Formatting

```bash
cd backend
source venv/bin/activate
black .
flake8 .
cd ../frontend
npm run lint
```

## 🛡️ Security

- **Rate Limiting**: Configurable per-IP rate limits
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: No sensitive information in error responses
- **Data Anonymization**: User data is anonymized by default
- **Non-root User**: Docker container runs as non-root user

## 🔍 Monitoring

### Health Checks

- Use `/api/health` endpoint for load balancer health checks
- Monitor log files for errors and performance issues
- Track response times and error rates

### Key Metrics

- Response time percentiles (P50, P95, P99)
- Search method distribution
- User interaction patterns
- Error rates by endpoint

### Monitoring Commands

```bash
# Navigate to backend directory first
cd backend

# Check health
curl http://localhost:8080/api/health

# Monitor logs
docker-compose logs -f tum-chatbot-backend | grep ERROR

# Check performance
curl "http://localhost:8080/api/statistics/performance?days=1"

# Monitor resource usage
docker stats tum-chatbot-backend
```

### Useful SQL Queries for Analysis

```bash
# Access the database
sqlite3 backend/statistics.db

# Most common queries (top 10)
SELECT query_text, frequency FROM query_analytics ORDER BY frequency DESC LIMIT 10;

# Search method effectiveness
SELECT search_method,
       COUNT(*) as total_searches,
       AVG(search_time) as avg_search_time,
       AVG(avg_similarity) as avg_similarity
FROM search_performance
GROUP BY search_method;

# Response time distribution
SELECT
    CASE
        WHEN response_time < 1 THEN 'Under 1s'
        WHEN response_time < 2 THEN '1-2s'
        WHEN response_time < 3 THEN '2-3s'
        WHEN response_time < 5 THEN '3-5s'
        ELSE 'Over 5s'
    END as time_range,
    COUNT(*) as count
FROM chat_interactions
GROUP BY time_range
ORDER BY count DESC;

# User session analysis
SELECT
    COUNT(*) as total_sessions,
    AVG(interaction_count) as avg_interactions_per_session,
    AVG(total_time) as avg_session_duration
FROM user_sessions
WHERE end_time IS NOT NULL;

# Campus usage breakdown
SELECT user_campus, COUNT(*) as interactions
FROM chat_interactions
WHERE user_campus IS NOT NULL
GROUP BY user_campus
ORDER BY interactions DESC;

# Role distribution
SELECT user_role, COUNT(*) as interactions
FROM chat_interactions
WHERE user_role IS NOT NULL
GROUP BY user_role
ORDER BY interactions DESC;

# Daily usage trends (last 7 days)
SELECT
    DATE(timestamp) as date,
    COUNT(*) as interactions,
    AVG(response_time) as avg_response_time
FROM chat_interactions
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY DATE(timestamp)
ORDER BY date DESC;

# Database size analysis
SELECT
    'chat_interactions' as table_name,
    COUNT(*) as row_count,
    COUNT(*) * 2048 as estimated_bytes
FROM chat_interactions
UNION ALL
SELECT 'search_performance', COUNT(*), COUNT(*) * 1024
FROM search_performance
UNION ALL
SELECT 'user_sessions', COUNT(*), COUNT(*) * 512
FROM user_sessions
UNION ALL
SELECT 'query_analytics', COUNT(*), COUNT(*) * 256
FROM query_analytics;
```

### Quick Reference - Most Common Commands

```bash
# Check current statistics
curl "http://localhost:8080/api/statistics?days=1" | jq '.statistics.total_interactions'

# Check performance
curl "http://localhost:8080/api/statistics/performance?days=7" | jq '.performance_metrics.response_time_percentiles'

# Clear all statistics (with backup)
./cleanup_stats.sh

# Monitor database size
ls -lh backend/statistics.db

# Check most common queries
sqlite3 backend/statistics.db "SELECT query_text, frequency FROM query_analytics ORDER BY frequency DESC LIMIT 5;"

# Check search method usage
sqlite3 backend/statistics.db "SELECT search_method, COUNT(*) FROM chat_interactions GROUP BY search_method;"

# Backup statistics
cp backend/statistics.db backend/statistics_backup_$(date +%Y%m%d_%H%M%S).db

# Restore from backup
cp backend/statistics_backup_20241201_143022.db backend/statistics.db
```

## 📞 Support

For issues and questions:

- Check the logs in `./logs/` or `cd backend && docker-compose logs`
- Review the configuration in `.env`
- Test the health endpoint: `GET /api/health`
- Contact the development team

## 📄 License

This project is part of the TUM Chatbot initiative.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## 📝 Changelog

### Version 1.0.0

- Production-ready backend with comprehensive logging
- Vector database integration with ChromaDB
- Statistics and analytics tracking
- Modern React frontend
- Docker containerization
- Comprehensive documentation
