# TUM Chatbot Backend - Deployment Guide

This guide covers production deployment, scaling, monitoring, and maintenance for the TUM Chatbot Backend.

## 🚀 Production Deployment Overview

The TUM Chatbot Backend is designed for production deployment with Docker, providing:

- **Containerized deployment** for consistency and portability
- **Environment-based configuration** for different deployment stages
- **Health monitoring** and automated recovery
- **Scalability** through horizontal scaling
- **Security** with proper isolation and access controls

## 🐳 Docker Production Deployment

### Prerequisites

- **Docker Engine** 20.10+
- **Docker Compose** 2.0+
- **4GB+ RAM** for vector database operations
- **10GB+ disk space** for logs and data
- **Google Gemini API key** for AI responses

### Step-by-Step Deployment

#### 1. Prepare Environment

```bash
# Clone the repository
git clone <repository-url>
cd "TUM Chatbot"

# Create production environment file
cp backend/docker.env.example .env

# Edit environment configuration
nano .env
```

#### 2. Configure Production Environment

**Required Configuration:**

```bash
# Set environment
ENVIRONMENT=production

# Set your actual Gemini API key
GEMINI_API_KEY=your_actual_api_key_here

# Production-specific settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=3600
```

**Optional Production Settings:**

```bash
# Performance tuning
SIMILARITY_THRESHOLD=0.4
GEMINI_TEMPERATURE=0.6
MAX_LOG_SIZE=5242880  # 5MB
LOG_BACKUP_COUNT=3

# Security settings
ANONYMIZE_DATA=True
LOG_CHAT_SESSIONS=False
```

#### 3. Deploy with Docker Compose

```bash
# Navigate to backend directory
cd backend

# Create necessary directories
mkdir -p logs data

# Set proper permissions
chmod 755 logs data

# Build and start the backend
docker-compose up -d

# Check deployment status
docker-compose ps

# View logs
docker-compose logs -f tum-chatbot-backend
```

#### 4. Verify Deployment

```bash
# Check health endpoint
curl http://localhost:8080/api/health

# Test chat functionality
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test" \
  -H "X-Session-ID: test" \
  -d '{"message": "Hello"}'

# Check logs
docker-compose logs tum-chatbot-backend
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

## 📊 Monitoring and Alerting

### Health Monitoring

#### Automated Health Checks

```bash
#!/bin/bash
# Health check script

HEALTH_URL="https://yourdomain.com/health"
ALERT_EMAIL="admin@yourdomain.com"

# Check health endpoint
HEALTH_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/health.json $HEALTH_URL)
HTTP_CODE="${HEALTH_RESPONSE: -3}"

if [ "$HTTP_CODE" != "200" ]; then
    echo "Health check failed: HTTP $HTTP_CODE" | mail -s "TUM Chatbot Health Alert" $ALERT_EMAIL
    exit 1
fi

# Check response time
RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null $HEALTH_URL)
if (( $(echo "$RESPONSE_TIME > 5" | bc -l) )); then
    echo "Slow response time: ${RESPONSE_TIME}s" | mail -s "TUM Chatbot Performance Alert" $ALERT_EMAIL
fi

echo "Health check passed"
```

#### System Monitoring

```bash
#!/bin/bash
# System monitoring script

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "High disk usage: ${DISK_USAGE}%" | mail -s "TUM Chatbot Disk Alert" admin@yourdomain.com
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "High memory usage: ${MEMORY_USAGE}%" | mail -s "TUM Chatbot Memory Alert" admin@yourdomain.com
fi

# Check Docker container status
if ! docker-compose ps | grep -q "Up"; then
    echo "Docker container is down" | mail -s "TUM Chatbot Container Alert" admin@yourdomain.com
fi
```

### Log Monitoring

```bash
#!/bin/bash
# Log monitoring script

LOG_FILE="logs/tum_chatbot.log"
ERROR_THRESHOLD=10

# Count errors in last hour
ERROR_COUNT=$(grep "$(date -d '1 hour ago' '+%Y-%m-%dT%H')" $LOG_FILE | grep -c "ERROR")

if [ $ERROR_COUNT -gt $ERROR_THRESHOLD ]; then
    echo "High error rate: $ERROR_COUNT errors in last hour" | mail -s "TUM Chatbot Error Alert" admin@yourdomain.com
fi

# Check for specific error patterns
if grep -q "Gemini API error" $LOG_FILE; then
    echo "API errors detected" | mail -s "TUM Chatbot API Alert" admin@yourdomain.com
fi
```

## 📚 Related Documentation

- **[SETUP.md](SETUP.md)** - Installation and setup instructions
- **[CONFIGURATION.md](CONFIGURATION.md)** - Environment configuration
- **[API.md](API.md)** - API endpoints and usage
- **[LOGGING.md](LOGGING.md)** - Logging system and monitoring
- **[METRICS.md](METRICS.md)** - Performance metrics and analytics
