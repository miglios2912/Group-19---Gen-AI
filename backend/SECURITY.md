# TUM Chatbot Security System

## Overview

The TUM Chatbot implements a comprehensive security system designed to protect against prompt injection attacks and malicious users. The system includes IP blacklisting, real-time validation, and multi-layer protection.

## Security Features

### 1. IP Blacklisting System

**Purpose**: Permanently block IP addresses that attempt prompt injection attacks.

**Components**:

- `IPBlacklistManager`: Manages blacklist storage and queries
- `SecurityManager`: Coordinates detection and blacklisting
- SQLite database: Persistent storage for blacklisted IPs

**Storage**: `data/security.db`

### 2. Prompt Injection Detection

**Method**: LLM-based detection using a specialized prompt to analyze user input.

**Detection Types**:

- Role manipulation
- Instruction override
- System prompt injection
- Context confusion
- Code injection attempts

**Fallback**: No fallback - if detection fails, request is blocked with error message.

### 3. Frontend Security Guard

**Purpose**: Prevent access to the application for blacklisted IPs.

**Features**:

- Real-time IP validation on page load
- Complete API call blocking for blacklisted IPs
- Response integrity verification
- Security token validation

### 4. Backend IP Validation

**Middleware**: Validates IP on ALL API requests (except security endpoints).

**Client IP Detection**:

1. `X-Client-IP` header (frontend-provided)
2. `X-Forwarded-For` header (proxy-provided)
3. `X-Real-IP` header
4. `CF-Connecting-IP` header (Cloudflare)
5. `request.remote_addr` (fallback)

### 5. Security Token System

**Purpose**: Prevent response tampering and ensure request authenticity.

**Implementation**:

- Base64-encoded tokens with timestamp and user agent
- Token validation on IP validation requests
- Automatic rejection of invalid tokens

## API Endpoints

### Security Endpoints

#### `GET /api/v2/security/validate-ip`

Validates if the requesting IP is blacklisted.

**Headers**:

- `X-Client-IP`: Client's real IP address
- `X-Validation-Token`: Security token

**Response**:

```json
{
  "blocked": true/false,
  "reason": "IP blacklisted: [reason]",
  "attack_type": "role_manipulation",
  "confidence": 0.9,
  "first_detected": "2025-07-11 11:18:30.561074",
  "request_id": "uuid",
  "timestamp": "2025-07-11T11:33:46.462989"
}
```

#### `GET /api/v2/security/client-ip`

Returns the detected client IP address.

**Response**:

```json
{
	"client_ip": "192.168.1.1",
	"request_id": "uuid",
	"timestamp": "2025-07-11T11:33:46.462989"
}
```

#### `GET /api/v2/security/stats`

Returns security statistics and blacklisted IPs list.

**Response**:

```json
{
	"security_stats": {
		"total_blacklisted": 1,
		"attack_breakdown": { "role_manipulation": 1 },
		"recent_events_24h": 5,
		"blacklisted_ips": [
			{
				"ip_address": "192.168.1.1",
				"attack_type": "role_manipulation",
				"reason": "Attempted role manipulation",
				"confidence": 0.9,
				"first_detected": "2025-07-11 11:18:30.561074",
				"total_attempts": 3
			}
		]
	}
}
```

## Security Flow

### 1. Frontend Access

1. User accesses frontend
2. SecurityGuard component loads
3. IP validation request sent to backend
4. If blocked: Show blocking screen, block all API calls
5. If allowed: Render normal application

### 2. API Request Processing

1. Request received by backend
2. IP validation middleware checks client IP
3. If blacklisted: Return 403 error immediately
4. If allowed: Process request normally

### 3. Chat Request Security

1. User sends chat message
2. Security analysis performed on message
3. If attack detected: Block request, blacklist IP
4. If clean: Process chat request

## Production Security Considerations

### 1. Client IP Detection

**Challenge**: Frontend cannot directly access client IP due to browser security.

**Solution**:

- Use proxy headers (X-Forwarded-For, X-Real-IP)
- Configure reverse proxy to pass real client IP
- Implement additional validation layers

### 2. Response Tampering Prevention

**Measures**:

- Security tokens with timestamp validation
- Response integrity checks
- HTTPS enforcement
- Server-side validation on all requests

### 3. Bypass Prevention

**Measures**:

- Middleware validation on ALL endpoints
- No fallback detection (block on failure)
- Complete frontend lockdown for blacklisted IPs
- API call blocking at JavaScript level

### 4. Production Deployment

**Requirements**:

- Reverse proxy (nginx/Apache) with proper IP forwarding
- HTTPS enforcement
- Rate limiting
- Log monitoring
- Regular security audits

## Configuration

### Environment Variables

```bash
# Security Settings
ENABLE_SECURITY=true
ENABLE_PROMPT_INJECTION_DETECTION=true
ENABLE_IP_BLACKLISTING=true
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS Settings
ENABLE_CORS=true
CORS_ORIGINS=http://localhost:5173,https://yourdomain.com

# Logging
LOG_SECURITY_EVENTS=true
```

### Database Schema

```sql
-- IP Blacklist Table
CREATE TABLE ip_blacklist (
    ip_address TEXT PRIMARY KEY,
    attack_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    confidence REAL NOT NULL,
    first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_attempts INTEGER DEFAULT 1,
    blacklisted_by TEXT DEFAULT 'system'
);

-- Security Events Table
CREATE TABLE security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    event_type TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Monitoring and Logging

### Log Files

- `logs/tum_chatbot.log`: General application logs
- `logs/security.log`: Security-specific events
- `data/security.db`: Blacklist and security events database

### Key Metrics

- Total blacklisted IPs
- Attack type breakdown
- Recent security events (24h)
- Detection confidence scores
- False positive rates

## Security Testing

### Test Cases

1. **Direct API Access**: Attempt to bypass frontend
2. **IP Spoofing**: Try to fake client IP
3. **Response Tampering**: Modify validation responses
4. **Token Manipulation**: Use invalid security tokens
5. **Bypass Attempts**: Try to access blocked endpoints

### Attack Vectors Tested

- Role manipulation attacks
- Instruction override attempts
- System prompt injection
- Context confusion attacks
- Code injection attempts

## Incident Response

### When Attack Detected

1. IP automatically blacklisted
2. User immediately blocked from frontend
3. All API calls blocked for that IP
4. Security event logged with full details
5. Admin notification (if configured)

### Recovery Process

1. Review security logs
2. Verify attack was legitimate
3. Remove IP from blacklist if false positive
4. Update detection rules if needed
5. Monitor for similar attacks

## Compliance and Best Practices

### Security Standards

- OWASP Top 10 compliance
- Input validation and sanitization
- Defense in depth
- Fail secure principle
- Comprehensive logging

### Privacy Considerations

- IP addresses logged for security purposes
- No personal data stored in blacklist
- Logs retained for security monitoring only
- GDPR compliance for EU users

## Future Enhancements

### Planned Features

1. **JWT-based Security Tokens**: Replace simple base64 tokens
2. **Machine Learning Detection**: Improve attack detection accuracy
3. **Geographic Blocking**: Block by country/region
4. **Behavioral Analysis**: Detect suspicious patterns
5. **Admin Dashboard**: Web interface for security management
6. **Alert System**: Real-time notifications for attacks
7. **Whitelist System**: Allow trusted IPs to bypass some checks

### Advanced Security

1. **Rate Limiting per IP**: Prevent brute force attacks
2. **Session-based Validation**: Track user sessions
3. **Multi-factor Validation**: Additional security layers
4. **Threat Intelligence**: Integration with security feeds
5. **Automated Response**: Automatic countermeasures
