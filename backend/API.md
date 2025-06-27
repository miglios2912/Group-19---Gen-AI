# TUM Chatbot Backend - API Reference

Complete API reference for the TUM Chatbot Backend with examples and usage patterns.

## 📡 API Overview

The TUM Chatbot Backend provides a RESTful API for:

- **Chat interactions** - Send messages and receive AI responses
- **Session management** - Start, manage, and end user sessions
- **Health monitoring** - Check system status and configuration
- **Statistics** - Access usage and performance metrics

### Base URL

- **Development**: `http://localhost:8080`
- **Production**: `https://yourdomain.com`

### Authentication

The API uses header-based authentication:

- `X-User-ID`: Unique identifier for the user
- `X-Session-ID`: Session identifier (optional for some endpoints)

### Response Format

All API responses follow this structure:

```json
{
	"data": {
		// Response data
	},
	"request_id": "abc123",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "success"
}
```

## 🔗 Core Endpoints

### POST /api/chat

Send a message and receive an AI response.

#### Request

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -H "X-Session-ID: session456" \
  -d '{
    "message": "Where is the library?",
    "user_role": "student",
    "user_campus": "Munich"
  }'
```

#### Request Body

| Field         | Type   | Required | Description                            |
| ------------- | ------ | -------- | -------------------------------------- |
| `message`     | string | ✅       | User's question or message             |
| `user_role`   | string | ❌       | User role (student, employee, visitor) |
| `user_campus` | string | ❌       | Campus (Munich, Heilbronn, Singapore)  |

#### Response

```json
{
	"data": {
		"response": "The main library is located in the Arcisstraße 21 building...",
		"search_method": "hybrid",
		"search_time": 0.234,
		"results_count": 3,
		"similarity_scores": [0.85, 0.72, 0.68],
		"session_id": "session456"
	},
	"request_id": "req789",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "success"
}
```

#### Response Fields

| Field               | Type    | Description                                    |
| ------------------- | ------- | ---------------------------------------------- |
| `response`          | string  | AI-generated response                          |
| `search_method`     | string  | Search method used (hybrid, semantic, keyword) |
| `search_time`       | float   | Search execution time in seconds               |
| `results_count`     | integer | Number of relevant results found               |
| `similarity_scores` | array   | Similarity scores of top results               |
| `session_id`        | string  | Session identifier                             |

### POST /api/session/start

Start a new user session.

#### Request

```bash
curl -X POST http://localhost:8080/api/session/start \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{
    "user_role": "student",
    "user_campus": "Munich"
  }'
```

#### Request Body

| Field         | Type   | Required | Description                            |
| ------------- | ------ | -------- | -------------------------------------- |
| `user_role`   | string | ❌       | User role (student, employee, visitor) |
| `user_campus` | string | ❌       | Campus (Munich, Heilbronn, Singapore)  |

#### Response

```json
{
	"data": {
		"session_id": "session789",
		"user_id": "user123",
		"start_time": "2024-01-01T12:00:00.000Z",
		"user_role": "student",
		"user_campus": "Munich"
	},
	"request_id": "req456",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "success"
}
```

### POST /api/session/{id}/end

End a user session.

#### Request

```bash
curl -X POST http://localhost:8080/api/session/session789/end \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123"
```

#### Response

```json
{
	"data": {
		"session_id": "session789",
		"end_time": "2024-01-01T12:30:00.000Z",
		"duration": 1800,
		"interaction_count": 5
	},
	"request_id": "req789",
	"timestamp": "2024-01-01T12:30:00.000Z",
	"status": "success"
}
```

### GET /api/session/{id}

Get session information.

#### Request

```bash
curl -X GET http://localhost:8080/api/session/session789 \
  -H "X-User-ID: user123"
```

#### Response

```json
{
	"data": {
		"session_id": "session789",
		"user_id": "user123",
		"start_time": "2024-01-01T12:00:00.000Z",
		"end_time": null,
		"user_role": "student",
		"user_campus": "Munich",
		"interaction_count": 3,
		"is_active": true
	},
	"request_id": "req123",
	"timestamp": "2024-01-01T12:15:00.000Z",
	"status": "success"
}
```

### GET /api/health

Check system health and configuration.

#### Request

```bash
curl -X GET http://localhost:8080/api/health
```

#### Response

```json
{
	"data": {
		"status": "healthy",
		"timestamp": "2024-01-01T12:00:00.000Z",
		"version": "1.0.0",
		"uptime": 3600,
		"config": {
			"environment": "production",
			"log_level": "WARNING",
			"similarity_threshold": 0.3
		},
		"services": {
			"vector_database": "connected",
			"statistics_database": "connected",
			"gemini_api": "connected"
		}
	},
	"request_id": "health123",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "success"
}
```

## 📊 Analytics Endpoints

### GET /api/statistics

Get usage statistics for a specified time period.

#### Request

```bash
curl -X GET "http://localhost:8080/api/statistics?days=30"
```

#### Query Parameters

| Parameter | Type    | Default | Description                             |
| --------- | ------- | ------- | --------------------------------------- |
| `days`    | integer | 30      | Number of days to include in statistics |

#### Response

```json
{
	"data": {
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
		}
	},
	"request_id": "stats123",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "success"
}
```

### GET /api/statistics/performance

Get performance metrics for a specified time period.

#### Request

```bash
curl -X GET "http://localhost:8080/api/statistics/performance?days=7"
```

#### Response

```json
{
	"data": {
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
		}
	},
	"request_id": "perf123",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "success"
}
```

## 🔧 Testing Endpoints

### POST /api/search

Test search functionality directly.

#### Request

```bash
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "library hours",
    "method": "hybrid",
    "top_k": 5
  }'
```

#### Request Body

| Field    | Type    | Required | Description                               |
| -------- | ------- | -------- | ----------------------------------------- |
| `query`  | string  | ✅       | Search query                              |
| `method` | string  | ❌       | Search method (hybrid, semantic, keyword) |
| `top_k`  | integer | ❌       | Number of results to return               |

#### Response

```json
{
	"data": {
		"query": "library hours",
		"method": "hybrid",
		"results": [
			{
				"content": "The library is open Monday to Friday...",
				"metadata": {
					"source": "library_info",
					"category": "services"
				},
				"similarity_score": 0.85
			}
		],
		"search_time": 0.123,
		"total_results": 1
	},
	"request_id": "search123",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "success"
}
```

## 📝 Usage Examples

### Complete Chat Flow

```bash
# 1. Start a session
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8080/api/session/start \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"user_role": "student", "user_campus": "Munich"}')

SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.data.session_id')

# 2. Send a message
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -H "X-Session-ID: $SESSION_ID" \
  -d '{"message": "Where is the library?"}'

# 3. Send follow-up message
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -H "X-Session-ID: $SESSION_ID" \
  -d '{"message": "What are the opening hours?"}'

# 4. End the session
curl -X POST http://localhost:8080/api/session/$SESSION_ID/end \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123"
```

### Monitoring Script

```bash
#!/bin/bash
# Monitor TUM Chatbot performance

echo "=== TUM Chatbot Performance Monitor ==="
echo "Timestamp: $(date)"
echo

# Health check
echo "Health Status:"
curl -s http://localhost:8080/api/health | jq -r '.data.status'
echo

# Today's statistics
echo "Today's Usage:"
curl -s "http://localhost:8080/api/statistics?days=1" | jq '.data.statistics | {total_interactions, avg_response_time, active_sessions}'
echo

# Performance metrics
echo "Performance (7 days):"
curl -s "http://localhost:8080/api/statistics/performance?days=7" | jq '.data.performance_metrics.response_time_percentiles'
echo
```

### Automated Testing

```bash
#!/bin/bash
# Test API endpoints

BASE_URL="http://localhost:8080"
USER_ID="test_user_$(date +%s)"
SESSION_ID="test_session_$(date +%s)"

echo "Testing TUM Chatbot API..."

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$BASE_URL/api/health" | jq '.data.status'

# Test session start
echo "2. Testing session start..."
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/session/start" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{"user_role": "student", "user_campus": "Munich"}')

echo $SESSION_RESPONSE | jq '.data.session_id'

# Test chat endpoint
echo "3. Testing chat endpoint..."
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -H "X-Session-ID: $SESSION_ID" \
  -d '{"message": "Hello, this is a test"}')

echo $CHAT_RESPONSE | jq '.data.response'

# Test statistics
echo "4. Testing statistics endpoint..."
curl -s "$BASE_URL/api/statistics?days=1" | jq '.data.statistics.total_interactions'

echo "API testing completed!"
```

## ⚠️ Error Handling

### Error Response Format

```json
{
	"error": {
		"code": "VALIDATION_ERROR",
		"message": "Invalid request parameters",
		"details": {
			"field": "message",
			"issue": "Message cannot be empty"
		}
	},
	"request_id": "req123",
	"timestamp": "2024-01-01T12:00:00.000Z",
	"status": "error"
}
```

### Common Error Codes

| Code                   | Description                  | HTTP Status |
| ---------------------- | ---------------------------- | ----------- |
| `VALIDATION_ERROR`     | Invalid request parameters   | 400         |
| `AUTHENTICATION_ERROR` | Missing or invalid headers   | 401         |
| `RATE_LIMIT_EXCEEDED`  | Too many requests            | 429         |
| `INTERNAL_ERROR`       | Server error                 | 500         |
| `SERVICE_UNAVAILABLE`  | External service unavailable | 503         |

### Rate Limiting

The API implements rate limiting:

- **Default**: 100 requests per hour per IP
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Response**: 429 status code when limit exceeded

## 🔍 Debugging

### Enable Debug Mode

Set `FLASK_DEBUG=True` in your environment for detailed error messages.

### Request Logging

All requests are logged with:

- Request ID for tracing
- User ID and session ID
- Request timing
- Response status

### Common Issues

**CORS Errors:**

```bash
# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS http://localhost:8080/api/chat
```

**Session Issues:**

```bash
# Check session status
curl -X GET http://localhost:8080/api/session/YOUR_SESSION_ID \
  -H "X-User-ID: YOUR_USER_ID"
```

## 📚 Related Documentation

- **[doc/SETUP.md](doc/SETUP.md)** - Installation and setup instructions
- **[doc/CONFIGURATION.md](doc/CONFIGURATION.md)** - Environment configuration
- **[doc/LOGGING.md](doc/LOGGING.md)** - Logging system and monitoring
- **[doc/METRICS.md](doc/METRICS.md)** - Performance metrics and analytics
- **[doc/DEPLOYMENT.md](doc/DEPLOYMENT.md)** - Production deployment guide
