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

## 🔄 Scaling and Load Balancing

### Horizontal Scaling

#### Multiple Instances

```yaml
# docker-compose.scale.yml
version: "3.8"
services:
  tum-chatbot-backend:
    build: .
    environment:
      - ENVIRONMENT=production
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    ports:
      - "8080"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
        reservations:
          memory: 1G
          cpus: "0.5"
```

#### Load Balancer Configuration

```nginx
# Nginx load balancer configuration
upstream tum_chatbot_backend {
    least_conn;  # Least connections algorithm
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
    server 127.0.0.1:8083;

    # Health checks
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://tum_chatbot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Connection pooling
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

### Database Scaling

#### Shared Database

For multiple instances, use a shared database:

```bash
# Use external database
docker run -d \
  --name tum-chatbot-db \
  -v tum_chatbot_data:/var/lib/postgresql/data \
  -e POSTGRES_DB=tum_chatbot \
  -e POSTGRES_USER=tum_chatbot \
  -e POSTGRES_PASSWORD=secure_password \
  postgres:13
```

#### Redis for Session Storage

```yaml
# Add Redis for session storage
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  tum-chatbot-backend:
    # ... existing configuration
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
```

## 🔒 Security Hardening

### Container Security

```dockerfile
# Security-hardened Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r tum_chatbot && useradd -r -g tum_chatbot tum_chatbot

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R tum_chatbot:tum_chatbot /app
RUN chmod -R 755 /app

# Switch to non-root user
USER tum_chatbot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "app.py"]
```

### Network Security

```bash
# Configure firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8080/tcp   # Block direct access to backend
sudo ufw enable

# Configure Docker network
docker network create --driver bridge --subnet=172.20.0.0/16 tum_chatbot_network
```

### Environment Security

```bash
# Secure environment file
chmod 600 .env

# Use secrets management
echo $GEMINI_API_KEY | docker secret create gemini_api_key -

# Rotate API keys regularly
# Set up automated key rotation
```

## 🛠️ Maintenance and Updates

### Backup Strategy

```bash
#!/bin/bash
# Backup script

BACKUP_DIR="/backups/tum_chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec tum-chatbot-backend sqlite3 /app/data/statistics.db ".backup /tmp/statistics_backup.db"
docker cp tum-chatbot-backend:/tmp/statistics_backup.db $BACKUP_DIR/statistics_$DATE.db

# Backup vector database
docker exec tum-chatbot-backend tar -czf /tmp/chroma_backup.tar.gz -C /app/chroma_db .
docker cp tum-chatbot-backend:/tmp/chroma_backup.tar.gz $BACKUP_DIR/chroma_$DATE.tar.gz

# Backup logs
docker exec tum-chatbot-backend tar -czf /tmp/logs_backup.tar.gz -C /app/logs .
docker cp tum-chatbot-backend:/tmp/logs_backup.tar.gz $BACKUP_DIR/logs_$DATE.tar.gz

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Update Procedure

```bash
#!/bin/bash
# Update script

echo "Starting TUM Chatbot update..."

# Backup current deployment
./backup.sh

# Pull latest code
git pull origin main

# Rebuild and restart
cd backend
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for health check
sleep 30

# Verify deployment
if curl -f http://localhost:8080/api/health; then
    echo "Update successful"
else
    echo "Update failed, rolling back..."
    docker-compose down
    # Restore from backup
    echo "Please restore from backup manually"
    exit 1
fi
```

### Performance Optimization

```bash
# Monitor resource usage
docker stats tum-chatbot-backend

# Optimize database
docker exec tum-chatbot-backend sqlite3 /app/data/statistics.db "VACUUM; ANALYZE;"

# Clean up old logs
find logs/ -name "*.log.*" -mtime +7 -delete

# Monitor disk usage
du -sh data/ logs/
```

## 📚 Related Documentation

- **[SETUP.md](SETUP.md)** - Installation and setup instructions
- **[CONFIGURATION.md](CONFIGURATION.md)** - Environment configuration
- **[API.md](API.md)** - API endpoints and usage
- **[LOGGING.md](LOGGING.md)** - Logging system and monitoring
- **[METRICS.md](METRICS.md)** - Performance metrics and analytics
