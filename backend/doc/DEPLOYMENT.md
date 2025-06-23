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

## 🌐 Web Server Configuration

### Nginx Configuration

Create an Nginx configuration file for reverse proxy:

```nginx
# /etc/nginx/sites-available/tum-chatbot
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # API endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;

        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8080/api/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend (if serving from same domain)
    location / {
        root /var/www/tum-chatbot-frontend;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### Apache Configuration

Create an Apache virtual host configuration:

```apache
# /etc/apache2/sites-available/tum-chatbot.conf
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com

    # Redirect to HTTPS
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /path/to/your/certificate.crt
    SSLCertificateKeyFile /path/to/your/private.key

    # Security headers
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

    # Rate limiting
    <Location "/api/">
        SetEnvIf X-Forwarded-For "^(\d{1,3}\.){3}\d{1,3}$" CLIENT_IP=$1
        SetEnvIf X-Real-IP "^(\d{1,3}\.){3}\d{1,3}$" CLIENT_IP=$1
        SetEnvIf Remote_Addr "^(\d{1,3}\.){3}\d{1,3}$" CLIENT_IP=$1

        # Use mod_ratelimit if available
        # RateLimitWindow 3600
        # RateLimitRequests 100
    </Location>

    # Proxy to backend
    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:8080/api/
    ProxyPassReverse /api/ http://localhost:8080/api/

    # Health check
    ProxyPass /health http://localhost:8080/api/health
    ProxyPassReverse /health http://localhost:8080/api/health

    # Frontend (if serving from same domain)
    DocumentRoot /var/www/tum-chatbot-frontend

    <Directory /var/www/tum-chatbot-frontend>
        AllowOverride All
        Require all granted

        # Cache static assets
        <FilesMatch "\.(js|css|png|jpg|jpeg|gif|ico|svg)$">
            ExpiresActive On
            ExpiresDefault "access plus 1 year"
            Header set Cache-Control "public, immutable"
        </FilesMatch>
    </Directory>
</VirtualHost>
```

## 🔧 SSL/TLS Configuration

### Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Certificate

```bash
# Generate private key
openssl genrsa -out private.key 2048

# Generate certificate signing request
openssl req -new -key private.key -out certificate.csr

# Generate self-signed certificate (for testing)
openssl x509 -req -days 365 -in certificate.csr -signkey private.key -out certificate.crt
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
