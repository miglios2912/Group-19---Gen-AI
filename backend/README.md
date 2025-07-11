# TUM Chatbot Backend

We built the backend to handle chat requests and search through university information using Python Flask and Google Gemini.

## How It Works

Our backend processes user questions through several steps:

1. **Context Detection**: Figures out if we need to know the user's role or campus
2. **Smart Search**: Expands keywords and searches through our knowledge base
3. **Response Generation**: Uses Google Gemini to create helpful, contextual answers
4. **Session Management**: Remembers conversation context for follow-up questions

## Key Files

- `chatbot_v2.py` - Main chatbot logic and search system
- `api_v2.py` - Flask API endpoints for the frontend
- `config.py` - Configuration and settings management
- `TUM_QA.json` - University knowledge base (270 Q&As)
- `requirements.txt` - Python dependencies

## Features

**Smart Context System**

- Only asks for role/campus when actually needed
- Remembers context throughout the conversation
- Handles campus-specific and role-dependent questions

**Keyword Search**

- Expands common student terms (e.g., "liv" → "library")
- Scores results based on keyword matches
- Fast and predictable search results

**Production Ready**

- Comprehensive logging and error handling
- Session management and analytics
- Rate limiting and CORS support
- Health check endpoints

## Architecture

**Development Mode:**

- Direct Flask development server (`python api_v2.py`)
- Runs on port 8083
- Auto-reload on code changes
- Debug mode enabled

**Production Mode:**

- Gunicorn WSGI server (`gunicorn api_v2:app`)
- Multiple worker processes for concurrent requests
- Production-optimized settings (no debug, request limits)
- Graceful worker restarts

## Configuration

Set these environment variables:

- `GEMINI_API_KEY` - Your Google Gemini API key
- `ENVIRONMENT` - Set to "production" for deployment
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)
- `WORKERS` - Number of Gunicorn workers (default: 4)

## API Endpoints

- `POST /api/v2/chat` - Send chat message and get AI response
- `POST /api/v2/session/start` - Start new user session
- `DELETE /api/v2/session/{id}` - End user session
- `GET /api/v2/health` - Health check for Cloud Run
- `GET /api/v2/statistics` - Comprehensive usage statistics (default: 30 days)
- `GET /api/v2/statistics/performance` - Performance metrics (default: 7 days)
- `GET /api/v2/stats` - Simple stats endpoint (alias for /api/v2/statistics)

## Deployment Features

- **Session Management**: In-memory session storage with automatic cleanup
- **Rate Limiting**: Configurable per-IP request limits
- **CORS Support**: Cross-origin requests for frontend integration
- **Health Checks**: Kubernetes-compatible health endpoints
- **Logging**: Structured logging with request tracing
- **Error Handling**: Graceful error responses with proper HTTP status codes

The backend is designed to be stateless except for session data, making it easy to scale horizontally on Google Cloud Run.
