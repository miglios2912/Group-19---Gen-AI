# TUM Chatbot Backend

Production-ready backend for the TUM Chatbot with vector database integration, comprehensive logging, and analytics.

## 🚀 Features

- **Vector Database Integration**: ChromaDB with sentence transformers for semantic search
- **Hybrid Search**: Combines semantic and keyword-based search for optimal results
- **Comprehensive Logging**: Structured logging with file rotation and multiple handlers
- **Statistics & Analytics**: Track usage, performance, and user interactions
- **Production Ready**: CORS, rate limiting, error handling, and graceful shutdown
- **Environment Configuration**: Fully configurable via environment variables
- **RESTful API**: Clean REST API with comprehensive endpoints
- **Session Management**: User session tracking and management

## 📋 Requirements

- Python 3.8+
- Google Gemini API key
- 4GB+ RAM (for vector database operations)

## 🛠️ Installation

1. **Clone the repository and navigate to backend:**

   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

5. **Configure your Gemini API key:**
   ```bash
   # In .env file
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## ⚙️ Configuration

The backend is fully configurable via environment variables. See `env_example.txt` for all available options.

### Key Configuration Sections:

- **API Configuration**: Gemini API settings
- **Server Configuration**: Host, port, CORS, rate limiting
- **Database Configuration**: ChromaDB settings
- **Search Configuration**: Search parameters and thresholds
- **Logging Configuration**: Log levels, file paths, rotation
- **Statistics Configuration**: Analytics and tracking options

## 🚀 Running the Application

### Development Mode

```bash
python app.py
```

### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:8080 backend.api:create_app()
```

### Using Docker

```bash
docker build -t tum-chatbot-backend .
docker run -p 8080:8080 --env-file .env tum-chatbot-backend
```

## 📡 API Endpoints

### Core Endpoints

#### `POST /api/chat`

Main chat endpoint for generating responses.

**Headers:**

- `X-User-ID`: User identifier (optional, defaults to "anonymous")
- `X-Session-ID`: Session identifier (optional, auto-generated if not provided)

**Request Body:**

```json
{
	"message": "Where is the library?"
}
```

**Response:**

```json
{
	"response": "The library is located in Building 1, Room 101...",
	"session_id": "uuid-session-id",
	"request_id": "uuid-request-id",
	"timestamp": "2024-01-01T12:00:00Z"
}
```

#### `POST /api/session/start`

Start a new user session.

**Response:**

```json
{
	"session_id": "uuid-session-id",
	"request_id": "uuid-request-id",
	"timestamp": "2024-01-01T12:00:00Z"
}
```

#### `POST /api/session/{session_id}/end`

End a user session.

**Response:**

```json
{
	"session_id": "uuid-session-id",
	"status": "ended",
	"request_id": "uuid-request-id",
	"timestamp": "2024-01-01T12:00:00Z"
}
```

#### `GET /api/session/{session_id}`

Get session information.

**Response:**

```json
{
	"session_info": {
		"session_id": "uuid-session-id",
		"user_context": {
			"role": "student",
			"campus": "Munich"
		},
		"conversation_count": 5
	},
	"request_id": "uuid-request-id",
	"timestamp": "2024-01-01T12:00:00Z"
}
```

### Analytics Endpoints

#### `GET /api/statistics?days=30`

Get usage statistics for the specified period.

**Response:**

```json
{
	"statistics": {
		"period_days": 30,
		"total_interactions": 1250,
		"avg_response_time": 1.234,
		"search_methods": {
			"hybrid": 800,
			"semantic": 300,
			"keyword": 150
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
			["How to set up email?", 32]
		],
		"active_sessions": 25
	},
	"request_id": "uuid-request-id",
	"timestamp": "2024-01-01T12:00:00Z"
}
```

#### `GET /api/statistics/performance?days=7`

Get performance metrics.

**Response:**

```json
{
	"performance_metrics": {
		"period_days": 7,
		"search_performance": [
			["hybrid", 0.5, 4.2, 0.75, 800],
			["semantic", 0.3, 3.8, 0.82, 300]
		],
		"response_time_percentiles": {
			"p50": 1.2,
			"p95": 2.8,
			"p99": 4.5
		},
		"generated_at": "2024-01-01T12:00:00Z"
	},
	"request_id": "uuid-request-id",
	"timestamp": "2024-01-01T12:00:00Z"
}
```

### Utility Endpoints

#### `GET /api/health`

Health check endpoint.

**Response:**

```json
{
	"status": "healthy",
	"timestamp": "2024-01-01T12:00:00Z",
	"version": "1.0.0",
	"environment": "production"
}
```

#### `POST /api/search`

Test search functionality.

**Request Body:**

```json
{
	"query": "library location",
	"method": "hybrid",
	"top_k": 5
}
```

## 📊 Logging

The backend uses structured logging with multiple handlers:

- **Console Handler**: INFO level and above
- **File Handler**: DEBUG level and above with rotation
- **Error Handler**: ERROR level and above (separate file)

### Log Format

```
2024-01-01T12:00:00.123Z - tum_chatbot - INFO - [user123:session456:req789] - Request completed in 1.234s
```

### Log Files

- Main log: `./logs/tum_chatbot.log`
- Error log: `./logs/tum_chatbot_error.log`

## 📈 Statistics and Analytics

The backend tracks comprehensive statistics:

- **Chat Interactions**: Query, response, timing, search method
- **Search Performance**: Method, results count, similarity scores
- **User Sessions**: Duration, interaction count, user context
- **Query Analytics**: Frequency, average response time

### Data Privacy

- User IDs are anonymized by default (configurable)
- No personal information is stored
- All data is stored locally in SQLite

## 🔧 Development

### Project Structure

```
backend/
├── __init__.py          # Package initialization
├── app.py              # Main application entry point
├── api.py              # Flask API implementation
├── chatbot.py          # Core chatbot engine
├── config.py           # Configuration management
├── logger.py           # Logging setup
├── statistics.py       # Analytics and statistics
├── requirements.txt    # Python dependencies
├── env_example.txt     # Environment variables template
└── README.md          # This file
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black backend/
flake8 backend/
mypy backend/
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Configure logging paths
- [ ] Set up monitoring and alerting
- [ ] Configure backup for statistics database

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "backend.api:create_app()"]
```

### Environment Variables for Production

```bash
ENVIRONMENT=production
FLASK_DEBUG=False
LOG_LEVEL=WARNING
ENABLE_STATISTICS=True
ANONYMIZE_DATA=True
ENABLE_RATE_LIMITING=True
ENABLE_CORS=True
```

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

## 🛡️ Security

- **Rate Limiting**: Configurable per-IP rate limits
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: No sensitive information in error responses
- **Data Anonymization**: User data is anonymized by default

## 📞 Support

For issues and questions:

- Check the logs in `./logs/`
- Review the configuration in `.env`
- Test the health endpoint: `GET /api/health`
- Contact the development team

## 📄 License

This project is part of the TUM Chatbot initiative.
