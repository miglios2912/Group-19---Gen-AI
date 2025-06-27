# TUM Chatbot Backend - Logging Guide

This guide covers the logging system, monitoring, troubleshooting, and chat session logging for the TUM Chatbot Backend.

## 📊 Logging System Overview

The TUM Chatbot uses structured logging with multiple handlers for comprehensive monitoring and debugging.

### Log Structure

The application uses structured logging with multiple handlers:

- **Console Handler**: INFO level and above (for development)
- **File Handler**: DEBUG level and above with rotation (for production)
- **Error Handler**: ERROR level and above (separate file)

### Log Format

```
2024-01-01T12:00:00.123Z - tum_chatbot - INFO - [user123:session456:req789] - Request completed in 1.234s
```

**Format Components:**

- **Timestamp**: ISO 8601 format with timezone
- **Logger Name**: `tum_chatbot`
- **Log Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context**: `[user_id:session_id:request_id]`
- **Message**: Human-readable log message

## 📁 Log Files

### Log File Locations

#### Docker Environment

- **Main log**: `/app/logs/tum_chatbot.log` (mounted to `./logs/tum_chatbot.log`)
- **Error log**: `/app/logs/tum_chatbot_error.log` (mounted to `./logs/tum_chatbot_error.log`)
- **Chat sessions**: `/app/logs/chat_sessions.log` (mounted to `./logs/chat_sessions.log`)

#### Development Environment

- **Main log**: `./logs/tum_chatbot.log`
- **Error log**: `./logs/tum_chatbot_error.log`
- **Chat sessions**: `./logs/chat_sessions.log`

### Log Rotation

Log files are automatically rotated to prevent disk space issues:

- **Maximum size**: 10MB (configurable via `MAX_LOG_SIZE`)
- **Backup count**: 5 files (configurable via `LOG_BACKUP_COUNT`)
- **Rotation**: When size limit is reached

## 🔍 Accessing Logs

### Docker Commands

```bash
# View real-time logs
docker-compose logs -f tum-chatbot-backend

# View recent logs
docker-compose logs --tail=100 tum-chatbot-backend

# View logs since specific time
docker-compose logs --since="2024-01-01T10:00:00" tum-chatbot-backend

# View error logs only
docker-compose logs tum-chatbot-backend | grep ERROR

# Access log files directly
docker exec tum-chatbot-backend cat /app/logs/tum_chatbot.log
docker exec tum-chatbot-backend cat /app/logs/tum_chatbot_error.log
```

### Direct File Access

```bash
# View main log file
tail -f logs/tum_chatbot.log

# View error log file
tail -f logs/tum_chatbot_error.log

# View chat session log
tail -f logs/chat_sessions.log

# Search logs
grep "ERROR" logs/tum_chatbot.log
grep "user123" logs/tum_chatbot.log
grep "session456" logs/tum_chatbot.log

# View last 100 lines
tail -n 100 logs/tum_chatbot.log

# View logs from specific time
grep "2024-01-01T12:" logs/tum_chatbot.log
```

## 💬 Chat Session Logging

### Overview

Chat session logging records complete conversations for debugging and analysis. This feature is **automatically enabled in development** and **automatically disabled in production** for security.

### Configuration

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

### Chat Session Log Format

```
2024-01-01 12:00:00 - === Chat Session: session123 [professor at Heilbronn] ===
2024-01-01 12:00:00 - USER (user123): Hello, I am a professor at the Heilbronn campus looking for places to engage with students.
2024-01-01 12:00:00 - BOT: As a professor at TUM Heilbronn, you can find students engaging in various activities...
2024-01-01 12:00:00 - ---
```

**Format Components:**

- **Session header**: Session ID and user context
- **User messages**: Timestamp, user ID, and message content
- **Bot responses**: Timestamp and AI-generated response
- **Session separator**: `---` between sessions

### Accessing Chat Session Logs

```bash
# View recent chat sessions
tail -f logs/chat_sessions.log

# Search for specific user
grep "user123" logs/chat_sessions.log

# Search for specific session
grep "session456" logs/chat_sessions.log

# View sessions from today
grep "$(date +%Y-%m-%d)" logs/chat_sessions.log

# Count total sessions
grep "=== Chat Session:" logs/chat_sessions.log | wc -l
```

### Security Considerations

**⚠️ Security Note**: Chat session logs contain user queries and are automatically disabled in production for security.

- **Development**: Enabled for debugging conversation issues
- **Production**: Disabled by default to protect user privacy
- **Manual override**: Can be enabled in production if needed for debugging

## 📈 Log Analysis

### Common Log Patterns

#### Request Processing

```
2024-01-01T12:00:00.123Z - tum_chatbot - INFO - [user123:session456:req789] - Request started
2024-01-01T12:00:00.234Z - tum_chatbot - DEBUG - [user123:session456:req789] - Search method: hybrid
2024-01-01T12:00:00.345Z - tum_chatbot - DEBUG - [user123:session456:req789] - Found 3 results
2024-01-01T12:00:00.456Z - tum_chatbot - INFO - [user123:session456:req789] - Request completed in 0.333s
```

#### Error Patterns

```
2024-01-01T12:00:00.123Z - tum_chatbot - ERROR - [user123:session456:req789] - Gemini API error: Invalid API key
2024-01-01T12:00:00.234Z - tum_chatbot - WARNING - [user123:session456:req789] - No results found for query
2024-01-01T12:00:00.345Z - tum_chatbot - ERROR - [user123:session456:req789] - Database connection failed
```

### Useful Log Queries

```bash
# Find all errors
grep "ERROR" logs/tum_chatbot.log

# Find slow requests (>5 seconds)
grep "Request completed in" logs/tum_chatbot.log | awk '$NF > 5'

# Find API errors
grep "Gemini API error" logs/tum_chatbot.log

# Find database errors
grep "Database" logs/tum_chatbot.log | grep "ERROR"

# Find rate limit violations
grep "Rate limit" logs/tum_chatbot.log

# Find search method distribution
grep "Search method:" logs/tum_chatbot.log | awk '{print $NF}' | sort | uniq -c

# Find user activity
grep "user123" logs/tum_chatbot.log | tail -20

# Find session activity
grep "session456" logs/tum_chatbot.log | tail -20
```

### Performance Analysis

```bash
# Extract response times
grep "Request completed in" logs/tum_chatbot.log | awk '{print $NF}' | sed 's/s//'

# Calculate average response time
grep "Request completed in" logs/tum_chatbot.log | awk '{sum+=$NF; count++} END {print "Average:", sum/count "s"}'

# Find slowest requests
grep "Request completed in" logs/tum_chatbot.log | sort -k10 -n | tail -10

# Count requests per hour
grep "Request started" logs/tum_chatbot.log | awk '{print substr($1,1,13)}' | sort | uniq -c
```

## 🔧 Log Configuration

### Environment Variables

| Variable              | Description                   | Default                        | Override |
| --------------------- | ----------------------------- | ------------------------------ | -------- |
| `LOG_LEVEL`           | Logging level                 | Auto-configured                | ✅       |
| `LOG_FILE_PATH`       | Main log file path            | `./logs/tum_chatbot.log`       | ✅       |
| `LOG_ERROR_FILE_PATH` | Error log file path           | `./logs/tum_chatbot_error.log` | ✅       |
| `LOG_CHAT_SESSIONS`   | Enable chat session logging   | Auto-configured                | ✅       |
| `MAX_LOG_SIZE`        | Maximum log file size (bytes) | `10485760` (10MB)              | ✅       |
| `LOG_BACKUP_COUNT`    | Number of log backups         | `5`                            | ✅       |

### Log Levels

| Level      | Description                                         | Use Case                    |
| ---------- | --------------------------------------------------- | --------------------------- |
| `DEBUG`    | Detailed debugging information                      | Development troubleshooting |
| `INFO`     | General information about program execution         | Normal operation monitoring |
| `WARNING`  | Warning messages for potentially harmful situations | Production monitoring       |
| `ERROR`    | Error messages for serious problems                 | Error tracking              |
| `CRITICAL` | Critical errors that may prevent program execution  | Emergency situations        |

### Configuration Examples

#### Development Logging

```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_CHAT_SESSIONS=True
MAX_LOG_SIZE=5242880  # 5MB
LOG_BACKUP_COUNT=3
```

#### Production Logging

```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
LOG_CHAT_SESSIONS=False
MAX_LOG_SIZE=20971520  # 20MB
LOG_BACKUP_COUNT=10
```

#### High-Volume Logging

```bash
ENVIRONMENT=production
LOG_LEVEL=ERROR
LOG_CHAT_SESSIONS=False
MAX_LOG_SIZE=52428800  # 50MB
LOG_BACKUP_COUNT=5
```

## 🛠️ Troubleshooting

### Common Log Issues

#### Log File Not Found

```bash
# Check if log directory exists
ls -la logs/

# Create log directory if missing
mkdir -p logs
chmod 755 logs

# Check permissions
ls -la logs/tum_chatbot.log
chmod 644 logs/tum_chatbot.log
```

#### Log File Too Large

```bash
# Check log file sizes
ls -lh logs/

# Rotate logs manually
mv logs/tum_chatbot.log logs/tum_chatbot.log.old
touch logs/tum_chatbot.log

# Compress old logs
gzip logs/tum_chatbot.log.old
```

#### No Logs Being Written

```bash
# Check if application is running
docker-compose ps

# Check log level configuration
grep "LOG_LEVEL" .env

# Test logging manually
docker exec tum-chatbot-backend python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
logging.info('Test log message')
"
```

### Log Analysis Tools

#### Simple Analysis Script

```bash
#!/bin/bash
# Analyze TUM Chatbot logs

LOG_FILE="logs/tum_chatbot.log"

echo "=== TUM Chatbot Log Analysis ==="
echo "Log file: $LOG_FILE"
echo "Timestamp: $(date)"
echo

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file not found"
    exit 1
fi

# Basic statistics
echo "1. Basic Statistics:"
echo "   Total lines: $(wc -l < $LOG_FILE)"
echo "   File size: $(du -h $LOG_FILE | cut -f1)"
echo "   Last modified: $(stat -c %y $LOG_FILE)"
echo

# Error analysis
echo "2. Error Analysis:"
echo "   Total errors: $(grep -c "ERROR" $LOG_FILE)"
echo "   Total warnings: $(grep -c "WARNING" $LOG_FILE)"
echo "   Recent errors (last 100 lines):"
grep "ERROR" $LOG_FILE | tail -5
echo

# Performance analysis
echo "3. Performance Analysis:"
echo "   Average response time: $(grep "Request completed in" $LOG_FILE | awk '{sum+=$NF; count++} END {if(count>0) print sum/count "s"; else print "No data"}')"
echo "   Slowest requests (>5s): $(grep "Request completed in" $LOG_FILE | awk '$NF > 5' | wc -l)"
echo

# User activity
echo "4. User Activity:"
echo "   Unique users: $(grep -o '\[[^:]*:' $LOG_FILE | sort | uniq | wc -l)"
echo "   Active sessions: $(grep -c "session" $LOG_FILE)"
echo

# Search method distribution
echo "5. Search Method Distribution:"
grep "Search method:" $LOG_FILE | awk '{print $NF}' | sort | uniq -c | sort -nr
echo
```

#### Real-time Monitoring Script

```bash
#!/bin/bash
# Real-time log monitoring

LOG_FILE="logs/tum_chatbot.log"

echo "=== TUM Chatbot Real-time Monitor ==="
echo "Monitoring: $LOG_FILE"
echo "Press Ctrl+C to stop"
echo

# Monitor logs in real-time
tail -f $LOG_FILE | while read line; do
    # Color code different log levels
    if echo "$line" | grep -q "ERROR"; then
        echo -e "\033[31m$line\033[0m"  # Red for errors
    elif echo "$line" | grep -q "WARNING"; then
        echo -e "\033[33m$line\033[0m"  # Yellow for warnings
    elif echo "$line" | grep -q "Request completed in"; then
        # Highlight slow requests
        response_time=$(echo "$line" | awk '{print $NF}' | sed 's/s//')
        if (( $(echo "$response_time > 5" | bc -l) )); then
            echo -e "\033[35m$line\033[0m"  # Magenta for slow requests
        else
            echo "$line"
        fi
    else
        echo "$line"
    fi
done
```

## 📊 Monitoring and Alerting

### Health Check Monitoring

```bash
# Check application health
curl -s http://localhost:8080/api/health | jq '.data.status'

# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s \
  -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: monitor" \
  -H "X-Session-ID: monitor" \
  -d '{"message": "health check"}'
```

### Log-based Monitoring

```bash
# Monitor error rate
ERROR_COUNT=$(grep -c "ERROR" logs/tum_chatbot.log)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "High error rate detected: $ERROR_COUNT errors"
fi

# Monitor response times
SLOW_REQUESTS=$(grep "Request completed in" logs/tum_chatbot.log | awk '$NF > 5' | wc -l)
if [ $SLOW_REQUESTS -gt 5 ]; then
    echo "Slow requests detected: $SLOW_REQUESTS requests > 5s"
fi

# Monitor API errors
API_ERRORS=$(grep -c "Gemini API error" logs/tum_chatbot.log)
if [ $API_ERRORS -gt 0 ]; then
    echo "API errors detected: $API_ERRORS errors"
fi
```

## 📚 Related Documentation

- **[SETUP.md](SETUP.md)** - Installation and setup instructions
- **[CONFIGURATION.md](CONFIGURATION.md)** - Environment configuration
- **[API.md](API.md)** - API endpoints and usage
- **[METRICS.md](METRICS.md)** - Performance metrics and analytics
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
