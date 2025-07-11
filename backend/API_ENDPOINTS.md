# TUM Chatbot V2 API Documentation

## Base URL

- **Development**: `http://localhost:8083`
- **Production**: `https://your-domain.com`

## Authentication

All endpoints support optional user identification via headers:

- `X-User-ID`: User identifier (defaults to "anonymous")
- `X-Session-ID`: Session identifier (can also be passed in request body)

## Endpoints

### 1. Health Check

**GET** `/api/v2/health`

Check if the API is running and healthy.

**Response:**

```json
{
	"status": "healthy",
	"version": "v2-smart-context",
	"timestamp": "2024-01-15T10:30:00.000Z",
	"environment": "development"
}
```

### 2. Chat

**POST** `/api/v2/chat`

Send a message and get an AI response with smart context management.

**Headers:**

```
Content-Type: application/json
X-User-ID: user123 (optional)
X-Session-ID: session456 (optional)
```

**Request Body:**

```json
{
  "message": "Where is the library?",
  "session_id": "session456" (optional, can be in headers)
}
```

**Response:**

```json
{
	"response": "The main library is located in the Arcisstraße 21 building...",
	"session_id": "session456",
	"request_id": "uuid-here",
	"version": "v2",
	"timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 3. Session Management

#### Start Session

**POST** `/api/v2/session/start`

Start a new chat session.

**Headers:**

```
X-User-ID: user123 (optional)
```

**Response:**

```json
{
	"session_id": "new-session-uuid",
	"message": "Session started successfully"
}
```

#### End Session

**DELETE** `/api/v2/session/{session_id}`

End a specific chat session.

**Response:**

```json
{
	"message": "Session ended successfully"
}
```

### 4. Statistics

#### Get Statistics

**GET** `/api/v2/statistics`

Get comprehensive usage statistics.

**Query Parameters:**

- `days` (optional): Number of days to analyze (1-365, default: 30)

**Headers:**

```
X-User-ID: user123 (optional)
```

**Response:**

```json
{
	"statistics": {
		"total_interactions": 150,
		"unique_users": 45,
		"average_response_time": 2.3,
		"popular_queries": ["library", "cafeteria", "exam"],
		"user_roles": {
			"student": 80,
			"staff": 15,
			"visitor": 5
		},
		"campuses": {
			"Munich": 60,
			"Garching": 25,
			"Weihenstephan": 15
		}
	},
	"request_id": "uuid-here",
	"timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Get Performance Metrics

**GET** `/api/v2/statistics/performance`

Get detailed performance metrics.

**Query Parameters:**

- `days` (optional): Number of days to analyze (1-30, default: 7)

**Headers:**

```
X-User-ID: user123 (optional)
```

**Response:**

```json
{
	"performance_metrics": {
		"average_response_time": 2.1,
		"response_time_percentiles": {
			"50th": 1.8,
			"90th": 3.2,
			"95th": 4.1
		},
		"search_performance": {
			"average_results": 3.5,
			"success_rate": 0.92
		},
		"error_rates": {
			"total_errors": 5,
			"error_rate": 0.03
		}
	},
	"request_id": "uuid-here",
	"timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Simple Stats (Alias)

**GET** `/api/v2/stats`

Simple alias for `/api/v2/statistics` with simplified response format.

**Query Parameters:**

- `days` (optional): Number of days to analyze (1-365, default: 30)

**Response:**

```json
{
	"stats": {
		"total_interactions": 150,
		"unique_users": 45,
		"average_response_time": 2.3
	},
	"request_id": "uuid-here",
	"timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 5. Security

#### Security Statistics

**GET** `/api/v2/security/stats`

Get security statistics and blacklist information.

**Response:**

```json
{
	"security_stats": {
		"total_blacklisted": 5,
		"attack_breakdown": {
			"prompt_injection": 2,
			"role_manipulation": 1,
			"code_injection": 1,
			"jailbreak_attempt": 1
		},
		"recent_events_24h": 12
	},
	"request_id": "uuid-here",
	"timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": "Error message here",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "request_id": "uuid-here" (optional)
}
```

## Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Endpoint not found
- `405` - Method not allowed
- `500` - Internal server error

## Rate Limiting

When enabled, the API implements rate limiting:

- Default: 100 requests per 15 minutes per IP
- Configurable via environment variables

## CORS Support

Cross-Origin Resource Sharing is enabled for frontend integration:

- Configurable origins via environment variables
- Default: Allows all origins in development

## Development vs Production

### Development Mode

- Debug mode enabled
- Detailed error messages
- Chat session logging (with warnings)
- Console logging

### Production Mode

- Debug mode disabled
- Minimal error messages
- No chat session logging
- Structured logging only

## Configuration

All endpoints respect the configuration in `config.py` and environment variables:

- `ENVIRONMENT`: Controls debug mode and logging
- `ENABLE_STATISTICS`: Enables/disables statistics collection
- `LOG_CHAT_SESSIONS`: Enables chat session logging (development only)
- `ENABLE_RATE_LIMITING`: Enables rate limiting
- `ENABLE_CORS`: Enables CORS support
- `ENABLE_SECURITY`: Enables prompt injection detection and IP blacklisting
- `ENABLE_PROMPT_INJECTION_DETECTION`: Enables LLM-based attack detection
- `DETECTION_CONFIDENCE_THRESHOLD`: Confidence threshold for attack detection (0.0-1.0)

## Security Behavior

### Detection Errors

When the detection LLM encounters problems (JSON parsing errors, API failures, etc.), the system will:

- Block the request immediately
- Return: "We are having trouble verifying your question at the moment, please try again later."
- Not pass the message to the main chatbot
- Log the detection error for monitoring

### Attack Detection

When prompt injection attacks are detected:

- Block the request with a security reason
- Permanently blacklist the IP address
- Log the attack details for analysis
