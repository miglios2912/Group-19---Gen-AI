# TUM Chatbot Backend - Setup Guide

This guide covers the complete setup process for the TUM Chatbot Backend in both development and production environments.

## 📋 Prerequisites

### System Requirements

- **Python 3.11+** (for compatibility with scientific packages)
- **Google Gemini API key** (required for AI responses)
- **4GB+ RAM** (for vector database operations)
- **Docker & Docker Compose** (for production deployment)

### API Key Setup

1. **Get a Google Gemini API key**:

   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key for use in configuration

2. **Test your API key**:
   ```bash
   curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
   ```

## 🐳 Docker Setup (Recommended)

### Quick Start with Docker

```bash
# 1. Clone the repository
git clone <repository-url>
cd "TUM Chatbot"

# 2. Configure environment
cp backend/docker.env.example .env

# 3. Edit .env with your settings
nano .env
```

**Required Configuration:**

```bash
ENVIRONMENT=production
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

### Start the Backend

```bash
# Navigate to backend directory
cd backend

# Build and start the backend
docker-compose up -d

# Check logs
docker-compose logs -f tum-chatbot-backend

# Check health
curl http://localhost:8080/api/health
```

### Docker Commands Reference

```bash
# Start the service
docker-compose up -d

# Stop the service
docker-compose down

# View logs
docker-compose logs -f tum-chatbot-backend

# Restart the service
docker-compose restart tum-chatbot-backend

# Rebuild the image
docker-compose build --no-cache

# Access the container shell
docker exec -it tum-chatbot-backend /bin/bash

# Check container status
docker-compose ps
```

## 🛠️ Development Setup

### Step-by-Step Development Installation

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

### Development Environment Verification

```bash
# Check Python version
python --version  # Should be 3.11+

# Check installed packages
pip list

# Test the application
curl http://localhost:8080/api/health

# Check logs
tail -f logs/tum_chatbot.log
```

### Virtual Environment Management

```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Update dependencies
pip install -r requirements.txt --upgrade

# Install development dependencies
pip install pytest black flake8

# Create requirements from current environment
pip freeze > requirements.txt
```

## 🔧 Environment Configuration

### Environment Variables

The system uses a **single environment setting** that automatically configures all environment-specific behavior.

#### Required Variables

| Variable         | Description           | Example                       |
| ---------------- | --------------------- | ----------------------------- |
| `ENVIRONMENT`    | Environment mode      | `development` or `production` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSyC...`                  |

#### Optional Variables

| Variable              | Description                    | Default         |
| --------------------- | ------------------------------ | --------------- |
| `FLASK_HOST`          | Flask host address             | `0.0.0.0`       |
| `FLASK_PORT`          | Flask port                     | `8080`          |
| `LOG_LEVEL`           | Logging level                  | Auto-configured |
| `CORS_ORIGINS`        | Allowed CORS origins           | Auto-configured |
| `RATE_LIMIT_REQUESTS` | Rate limit requests per window | `100`           |
| `RATE_LIMIT_WINDOW`   | Rate limit window in seconds   | `3600`          |

### Configuration Files

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

## 🔍 Troubleshooting

### Common Issues

#### Docker Issues

**Container won't start:**

```bash
# Check Docker logs
docker-compose logs tum-chatbot-backend

# Check if port is in use
netstat -tulpn | grep 8080

# Restart Docker service
sudo systemctl restart docker
```

**Permission issues:**

```bash
# Fix log directory permissions
sudo mkdir -p logs
sudo chown -R $USER:$USER logs

# Fix data directory permissions
sudo mkdir -p data
sudo chown -R $USER:$USER data
```

#### Python Issues

**Import errors:**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"

# Verify virtual environment
which python
```

**Memory issues:**

```bash
# Check available memory
free -h

# Increase swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### API Key Issues

**Invalid API key:**

```bash
# Test API key directly
curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'

# Check environment variable
echo $GEMINI_API_KEY
```

### Verification Steps

1. **Check system requirements:**

   ```bash
   python --version  # Should be 3.11+
   docker --version  # Should be installed
   docker-compose --version  # Should be installed
   ```

2. **Verify API key:**

   ```bash
   curl http://localhost:8080/api/health
   ```

3. **Check logs:**

   ```bash
   # Docker
   docker-compose logs tum-chatbot-backend

   # Development
   tail -f logs/tum_chatbot.log
   ```

4. **Test functionality:**
   ```bash
   curl -X POST http://localhost:8080/api/chat \
     -H "Content-Type: application/json" \
     -H "X-User-ID: test" \
     -H "X-Session-ID: test" \
     -d '{"message": "Hello"}'
   ```

## 📚 Next Steps

After successful setup:

1. **Configure your frontend** to connect to the backend
2. **Set up monitoring** using the **[LOGGING.md](LOGGING.md)** guide
3. **Deploy to production** using the **[DEPLOYMENT.md](DEPLOYMENT.md)** guide
4. **Monitor performance** using the **[METRICS.md](METRICS.md)** guide

## 📞 Support

If you encounter issues:

1. Check the **[LOGGING.md](LOGGING.md)** for troubleshooting
2. Review the **[CONFIGURATION.md](CONFIGURATION.md)** for settings
3. Test the health endpoint: `GET /api/health`
4. Contact the development team
