# TUM Chatbot Backend

Production-ready backend for the TUM Chatbot with vector database integration, comprehensive logging, and analytics.

## 🚀 Overview

The TUM Chatbot Backend is a sophisticated AI-powered system that provides intelligent responses to university-related questions using:

- **Vector Database Integration**: ChromaDB with sentence transformers for semantic search
- **Hybrid Search**: Combines semantic and keyword-based search for optimal results
- **Comprehensive Logging**: Structured logging with file rotation and multiple handlers
- **Statistics & Analytics**: Track usage, performance, and user interactions
- **Production Ready**: CORS, rate limiting, error handling, and graceful shutdown
- **Environment Configuration**: Fully configurable via environment variables
- **RESTful API**: Clean REST API with comprehensive endpoints
- **Session Management**: User session tracking and management

## 📋 Requirements

- **Python 3.11+** (for compatibility with scientific packages)
- **Google Gemini API key**
- **4GB+ RAM** (for vector database operations)
- **Docker & Docker Compose** (for production deployment)

## 🏗️ Project Structure

```
backend/
├── __init__.py         # Package initialization
├── app.py              # Main application entry point
├── api.py              # Flask API implementation
├── chatbot.py          # Core chatbot engine
├── config.py           # Configuration management
├── logger.py           # Logging setup
├── statistics.py       # Analytics and statistics
├── requirements.txt    # Python dependencies
├── env_example.txt     # Development environment template
├── docker.env.example  # Docker environment template
├── Dockerfile          # Backend Docker image
├── docker-compose.yml  # Backend service configuration
├── .dockerignore       # Docker build exclusions
├── README.md           # This file - general overview
├── doc/                # Documentation directory
│   ├── SETUP.md        # Detailed setup and installation guide
│   ├── CONFIGURATION.md # Environment configuration and settings
│   ├── API.md          # API endpoints and usage
│   ├── LOGGING.md      # Logging system and monitoring
│   ├── METRICS.md      # Performance metrics and analytics
│   ├── DEPLOYMENT.md   # Production deployment guide
│   └── STARTUP.md      # Startup procedure documentation
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd "TUM Chatbot"

# 2. Configure environment
cp backend/docker.env.example .env
# Edit .env and add your Google Gemini API key

# 3. Start the backend
cd backend
docker-compose up -d

# 4. Check health
curl http://localhost:8080/api/health
```

### Option 2: Development Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp env_example.txt .env
# Edit .env with your API key

# 5. Start the backend
python app.py
```

## 📚 Documentation

### Setup and Installation

- **[doc/SETUP.md](doc/SETUP.md)** - Detailed setup instructions for development and production
- **[doc/CONFIGURATION.md](doc/CONFIGURATION.md)** - Environment configuration and settings

### API and Usage

- **[doc/API.md](doc/API.md)** - Complete API reference with examples
- **[doc/LOGGING.md](doc/LOGGING.md)** - Logging system, monitoring, and troubleshooting

### Performance and Deployment

- **[doc/METRICS.md](doc/METRICS.md)** - Performance metrics, analytics, and optimization
- **[doc/DEPLOYMENT.md](doc/DEPLOYMENT.md)** - Production deployment and scaling
- **[doc/STARTUP.md](doc/STARTUP.md)** - Startup procedure and initialization

## 🔧 Development

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
```

## 🛡️ Security Features

- **Rate Limiting**: Configurable per-IP rate limits
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: No sensitive information in error responses
- **Data Anonymization**: User data is anonymized by default
- **Non-root User**: Docker container runs as non-root user

## 📞 Support

For issues and questions:

- Check the **[doc/LOGGING.md](doc/LOGGING.md)** for troubleshooting
- Review the **[doc/CONFIGURATION.md](doc/CONFIGURATION.md)** for settings
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
