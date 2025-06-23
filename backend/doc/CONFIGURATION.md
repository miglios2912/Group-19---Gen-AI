# TUM Chatbot Backend - Configuration Guide

This guide covers all configuration options and environment variables for the TUM Chatbot Backend.

## 🔧 Environment Configuration Overview

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

## 📋 Environment Variables Reference

### Required Variables

| Variable         | Description           | Example                       | Required |
| ---------------- | --------------------- | ----------------------------- | -------- |
| `ENVIRONMENT`    | Environment mode      | `development` or `production` | ✅       |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSyC...`                  | ✅       |

### Server Configuration

| Variable      | Description        | Default         | Override |
| ------------- | ------------------ | --------------- | -------- |
| `FLASK_HOST`  | Flask host address | `0.0.0.0`       | ✅       |
| `FLASK_PORT`  | Flask port         | `8080`          | ✅       |
| `FLASK_DEBUG` | Flask debug mode   | Auto-configured | ✅       |

### API Configuration

| Variable             | Description                   | Default      | Override |
| -------------------- | ----------------------------- | ------------ | -------- |
| `GEMINI_MODEL`       | Gemini model to use           | `gemini-pro` | ✅       |
| `GEMINI_MAX_TOKENS`  | Maximum tokens for responses  | `1000`       | ✅       |
| `GEMINI_TEMPERATURE` | Response creativity (0.0-1.0) | `0.7`        | ✅       |

### Search Configuration

| Variable                | Description                | Default            | Override |
| ----------------------- | -------------------------- | ------------------ | -------- |
| `SIMILARITY_THRESHOLD`  | Minimum similarity score   | `0.3`              | ✅       |
| `SEMANTIC_SEARCH_TOP_K` | Number of semantic results | `5`                | ✅       |
| `KEYWORD_SEARCH_TOP_K`  | Number of keyword results  | `5`                | ✅       |
| `HYBRID_SEARCH_TOP_K`   | Number of hybrid results   | `8`                | ✅       |
| `EMBEDDING_MODEL`       | Sentence transformer model | `all-MiniLM-L6-v2` | ✅       |

### Database Configuration

| Variable             | Description              | Default           | Override |
| -------------------- | ------------------------ | ----------------- | -------- |
| `CHROMA_DB_PATH`     | ChromaDB storage path    | `./chroma_db`     | ✅       |
| `STATISTICS_DB_PATH` | Statistics database path | `./statistics.db` | ✅       |

### Logging Configuration

| Variable              | Description                   | Default                        | Override |
| --------------------- | ----------------------------- | ------------------------------ | -------- |
| `LOG_LEVEL`           | Logging level                 | Auto-configured                | ✅       |
| `LOG_FILE_PATH`       | Main log file path            | `./logs/tum_chatbot.log`       | ✅       |
| `LOG_ERROR_FILE_PATH` | Error log file path           | `./logs/tum_chatbot_error.log` | ✅       |
| `LOG_CHAT_SESSIONS`   | Enable chat session logging   | Auto-configured                | ✅       |
| `MAX_LOG_SIZE`        | Maximum log file size (bytes) | `10485760` (10MB)              | ✅       |
| `LOG_BACKUP_COUNT`    | Number of log backups         | `5`                            | ✅       |

### Security Configuration

| Variable              | Description                    | Default         | Override |
| --------------------- | ------------------------------ | --------------- | -------- |
| `CORS_ORIGINS`        | Allowed CORS origins           | Auto-configured | ✅       |
| `RATE_LIMIT_REQUESTS` | Rate limit requests per window | `100`           | ✅       |
| `RATE_LIMIT_WINDOW`   | Rate limit window in seconds   | `3600`          | ✅       |
| `ANONYMIZE_DATA`      | Anonymize user data            | `True`          | ✅       |

### Statistics Configuration

| Variable                    | Description                | Default | Override |
| --------------------------- | -------------------------- | ------- | -------- |
| `ENABLE_STATISTICS`         | Enable statistics tracking | `True`  | ✅       |
| `TRACK_QUERY_ANALYTICS`     | Track query analytics      | `True`  | ✅       |
| `TRACK_USER_SESSIONS`       | Track user sessions        | `True`  | ✅       |
| `STATISTICS_RETENTION_DAYS` | Data retention period      | `90`    | ✅       |

## 📝 Configuration Examples

### Development Environment (`.env`)

```bash
# Set environment
ENVIRONMENT=development

# Required API key
GEMINI_API_KEY=your_actual_api_key

# Optional overrides (will use development defaults if not set)
# FLASK_DEBUG=True          # Automatically True in development
# LOG_LEVEL=DEBUG           # Automatically DEBUG in development
# LOG_CHAT_SESSIONS=True    # Automatically True in development

# Custom settings for development
FLASK_PORT=8080
GEMINI_TEMPERATURE=0.8
SIMILARITY_THRESHOLD=0.2
LOG_LEVEL=DEBUG
```

### Production Environment (`.env`)

```bash
# Set environment
ENVIRONMENT=production

# Required API key
GEMINI_API_KEY=your_actual_api_key

# Production-specific settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=3600

# Optional overrides (will use production defaults if not set)
# FLASK_DEBUG=False         # Automatically False in production
# LOG_LEVEL=WARNING         # Automatically WARNING in production
# LOG_CHAT_SESSIONS=False   # Automatically False in production

# Custom production settings
GEMINI_TEMPERATURE=0.6
SIMILARITY_THRESHOLD=0.4
MAX_LOG_SIZE=5242880  # 5MB
LOG_BACKUP_COUNT=3
```

### High-Performance Configuration

```bash
ENVIRONMENT=production
GEMINI_API_KEY=your_actual_api_key

# Performance optimizations
SEMANTIC_SEARCH_TOP_K=3
HYBRID_SEARCH_TOP_K=5
SIMILARITY_THRESHOLD=0.5
GEMINI_MAX_TOKENS=500

# Security settings
RATE_LIMIT_REQUESTS=500
RATE_LIMIT_WINDOW=3600
CORS_ORIGINS=https://yourdomain.com

# Logging optimization
LOG_LEVEL=WARNING
MAX_LOG_SIZE=5242880
LOG_BACKUP_COUNT=3
```

### Memory-Constrained Configuration

```bash
ENVIRONMENT=production
GEMINI_API_KEY=your_actual_api_key

# Memory optimizations
SEMANTIC_SEARCH_TOP_K=2
KEYWORD_SEARCH_TOP_K=2
HYBRID_SEARCH_TOP_K=3
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Reduced logging
LOG_LEVEL=ERROR
MAX_LOG_SIZE=2097152  # 2MB
LOG_BACKUP_COUNT=2

# Reduced statistics
TRACK_QUERY_ANALYTICS=False
STATISTICS_RETENTION_DAYS=30
```

## 🔍 Configuration Validation

### Validation Rules

The system validates configuration values:

| Variable               | Validation Rule                       | Error Message                |
| ---------------------- | ------------------------------------- | ---------------------------- |
| `ENVIRONMENT`          | Must be `development` or `production` | Invalid environment setting  |
| `GEMINI_API_KEY`       | Must not be empty                     | Gemini API key is required   |
| `FLASK_PORT`           | Must be 1-65535                       | Invalid port number          |
| `SIMILARITY_THRESHOLD` | Must be 0.0-1.0                       | Invalid similarity threshold |
| `GEMINI_TEMPERATURE`   | Must be 0.0-1.0                       | Invalid temperature value    |
| `RATE_LIMIT_REQUESTS`  | Must be > 0                           | Invalid rate limit requests  |
| `RATE_LIMIT_WINDOW`    | Must be > 0                           | Invalid rate limit window    |

### Configuration Testing

```bash
# Test configuration validation
python -c "
from config import Config
try:
    config = Config()
    print('Configuration is valid')
except Exception as e:
    print(f'Configuration error: {e}')
"

# Test environment-specific settings
python -c "
import os
os.environ['ENVIRONMENT'] = 'development'
from config import Config
config = Config()
print(f'Debug mode: {config.FLASK_DEBUG}')
print(f'Log level: {config.LOG_LEVEL}')
print(f'Chat sessions: {config.LOG_CHAT_SESSIONS}')
"
```

## 🔧 Advanced Configuration

### Custom Logging Configuration

```bash
# Custom log paths
LOG_FILE_PATH=/var/log/tum_chatbot/app.log
LOG_ERROR_FILE_PATH=/var/log/tum_chatbot/error.log

# Custom log rotation
MAX_LOG_SIZE=20971520  # 20MB
LOG_BACKUP_COUNT=10
```

### Custom Search Configuration

```bash
# Aggressive search settings
SIMILARITY_THRESHOLD=0.1
SEMANTIC_SEARCH_TOP_K=10
HYBRID_SEARCH_TOP_K=15

# Conservative search settings
SIMILARITY_THRESHOLD=0.7
SEMANTIC_SEARCH_TOP_K=3
HYBRID_SEARCH_TOP_K=5
```

### Custom Security Configuration

```bash
# Strict CORS
CORS_ORIGINS=https://app.yourdomain.com,https://admin.yourdomain.com

# Aggressive rate limiting
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=3600

# Lenient rate limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
```

## 📊 Configuration Monitoring

### Check Current Configuration

```bash
# View all configuration values
curl http://localhost:8080/api/health | jq '.config'

# Check environment variables
docker exec tum-chatbot-backend env | grep -E "(ENVIRONMENT|GEMINI|LOG_)"

# Check configuration in logs
grep "Configuration" logs/tum_chatbot.log
```

### Configuration Changes

```bash
# Reload configuration (requires restart)
docker-compose restart tum-chatbot-backend

# Check if changes took effect
curl http://localhost:8080/api/health
```

## 🔍 Troubleshooting Configuration

### Common Configuration Issues

**Invalid API key:**

```bash
# Check API key format
echo $GEMINI_API_KEY | wc -c  # Should be > 20

# Test API key directly
curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GEMINI_API_KEY" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

**Port conflicts:**

```bash
# Check if port is in use
netstat -tulpn | grep 8080

# Change port in configuration
FLASK_PORT=8081
```

**Permission issues:**

```bash
# Fix log directory permissions
sudo mkdir -p /var/log/tum_chatbot
sudo chown -R $USER:$USER /var/log/tum_chatbot

# Fix data directory permissions
sudo mkdir -p /var/lib/tum_chatbot
sudo chown -R $USER:$USER /var/lib/tum_chatbot
```

## 📚 Related Documentation

- **[SETUP.md](SETUP.md)** - Installation and setup instructions
- **[API.md](API.md)** - API endpoints and usage
- **[LOGGING.md](LOGGING.md)** - Logging system and monitoring
- **[METRICS.md](METRICS.md)** - Performance metrics and analytics
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
