# TUM Chatbot - Performance Metrics and Analytics Guide

This document provides detailed information about the performance metrics, search analytics, and configuration parameters used in the TUM Chatbot system.

## Table of Contents

1. [Overview](#overview)
2. [Search Performance Metrics](#search-performance-metrics)
3. [Similarity Threshold Configuration](#similarity-threshold-configuration)
4. [Response Time Metrics](#response-time-metrics)
5. [Database Performance](#database-performance)
6. [Memory Usage Metrics](#memory-usage-metrics)
7. [Monitoring and Alerting](#monitoring-and-alerting)
8. [Performance Optimization](#performance-optimization)

## Overview

The TUM Chatbot tracks comprehensive performance metrics to ensure optimal operation and provide insights for optimization. These metrics are stored in SQLite databases and accessible via API endpoints.

### Metrics Categories

- **Search Performance**: Effectiveness of different search methods
- **Response Times**: API endpoint performance
- **Database Performance**: Query execution and storage efficiency
- **Memory Usage**: Resource consumption patterns
- **User Analytics**: Usage patterns and session data

## Search Performance Metrics

### Search Methods

The system uses three search methods, each tracked separately:

1. **Semantic Search**: Vector similarity using ChromaDB
2. **Keyword Search**: Text-based matching with expansions
3. **Hybrid Search**: Combination of semantic and keyword search

### Search Metrics Explained

#### Similarity Scores

**What they measure**: How relevant the search results are to the user's query.

**Range**: -1.0 to 1.0 (higher = more relevant)

**Calculation**:

- For semantic search: `1 - distance` where distance is ChromaDB's cosine distance
- For keyword search: Based on word overlap and scoring algorithm
- For hybrid search: Weighted combination of both methods

**Interpretation**:

- **0.8-1.0**: Very relevant results
- **0.6-0.8**: Relevant results
- **0.4-0.6**: Somewhat relevant results
- **0.0-0.4**: Low relevance results
- **Negative**: Very low relevance (rare)

#### Search Time

**What it measures**: How long each search method takes to execute.

**Unit**: Seconds

**Typical ranges**:

- **Semantic Search**: 0.1-0.5 seconds
- **Keyword Search**: 0.01-0.1 seconds
- **Hybrid Search**: 0.2-0.8 seconds

**Performance indicators**:

- **Good**: < 0.3 seconds
- **Acceptable**: 0.3-0.8 seconds
- **Needs attention**: > 0.8 seconds

#### Results Count

**What it measures**: Number of documents returned by each search method.

**Typical ranges**:

- **Semantic Search**: 3-10 documents
- **Keyword Search**: 2-8 documents
- **Hybrid Search**: 3-12 documents

**Optimization targets**:

- **Too few results**: May indicate narrow search parameters
- **Too many results**: May indicate broad search parameters
- **Optimal**: 5-8 results for most queries

### Search Performance API Response

```json
{
	"performance_metrics": {
		"period_days": 7,
		"search_performance": [
			["hybrid", 0.592, 16.67, -0.222, 15],
			["semantic", 0.143, 10.0, -0.222, 15]
		],
		"generated_at": "2024-01-01T12:00:00.000Z"
	}
}
```

**Search performance array format**: `[method, avg_search_time, avg_results_count, avg_similarity, total_searches]`

## Similarity Threshold Configuration

### Configuration Parameter

**Environment Variable**: `SIMILARITY_THRESHOLD`

**Default Value**: `0.3`

**Range**: `0.0` to `1.0`

### What It Controls

The similarity threshold determines the minimum relevance score required for search results to be considered valid.

#### How It Works

1. **Search Execution**: All search methods return results with similarity scores
2. **Threshold Filtering**: Only results with scores ≥ threshold are included
3. **Fallback Logic**: If no results meet the threshold, lower-scoring results are included

#### Configuration Examples

**Strict Matching (0.7)**:

```bash
SIMILARITY_THRESHOLD=0.7
```

- Only very relevant results
- Higher precision, lower recall
- May return fewer results

**Balanced Matching (0.3)**:

```bash
SIMILARITY_THRESHOLD=0.3
```

- Good balance of precision and recall
- Default setting for most use cases
- Returns relevant results with some flexibility

**Loose Matching (0.1)**:

```bash
SIMILARITY_THRESHOLD=0.1
```

- Includes more results
- Higher recall, lower precision
- Useful for exploratory queries

### Impact on Search Methods

#### Semantic Search

- **High threshold (0.7+)**: Only very similar vector embeddings
- **Low threshold (0.1-0.3)**: Includes conceptually related content

#### Keyword Search

- **High threshold**: Requires exact or near-exact matches
- **Low threshold**: Includes partial matches and expansions

#### Hybrid Search

- **Combines both methods** with threshold applied to final scores
- **More robust** than individual methods
- **Better balance** of precision and recall

### Optimization Guidelines

#### For High-Quality Results

```bash
SIMILARITY_THRESHOLD=0.6
```

- Use when accuracy is critical
- May reduce result count
- Better for specific technical queries

#### For Comprehensive Results

```bash
SIMILARITY_THRESHOLD=0.2
```

- Use when coverage is important
- Includes more diverse results
- Better for general inquiries

#### For Balanced Performance

```bash
SIMILARITY_THRESHOLD=0.3
```

- Default setting
- Good balance for most use cases
- Recommended starting point

## Response Time Metrics

### Response Time Percentiles

**What they measure**: Distribution of response times across all API requests.

**Calculation**: Sort all response times, then take the value at the specified percentile position.

#### Percentile Explanation

- **P50 (Median)**: 50% of requests complete within this time
- **P95**: 95% of requests complete within this time
- **P99**: 99% of requests complete within this time

#### Performance Targets

| Percentile | Target | Good     | Needs Attention |
| ---------- | ------ | -------- | --------------- |
| P50        | < 1.0s | 1.0-2.0s | > 2.0s          |
| P95        | < 3.0s | 3.0-5.0s | > 5.0s          |
| P99        | < 5.0s | 5.0-8.0s | > 8.0s          |

#### Example Response

```json
{
	"performance_metrics": {
		"response_time_percentiles": {
			"p50": 1.234,
			"p95": 3.456,
			"p99": 4.789
		}
	}
}
```

**Interpretation**:

- 50% of requests complete in ≤1.234 seconds
- 95% of requests complete in ≤3.456 seconds
- 99% of requests complete in ≤4.789 seconds

### Response Time Components

#### Breakdown by Operation

1. **Search Time**: 40-60% of total response time
2. **LLM Generation**: 30-50% of total response time
3. **Database Operations**: 5-10% of total response time
4. **Logging and Analytics**: 1-5% of total response time

#### Optimization Opportunities

- **High search time**: Optimize vector database or reduce search scope
- **High LLM time**: Consider model optimization or caching
- **High database time**: Optimize queries or add indexes
- **High logging time**: Reduce log verbosity in production

## Database Performance

### SQLite Performance Metrics

#### WAL Mode Benefits

- **Concurrent Access**: Multiple readers, single writer
- **Better Performance**: Reduced lock contention
- **Crash Recovery**: Automatic recovery from incomplete transactions

#### Database Size Metrics

| Table              | Size per 1000 records | Growth rate |
| ------------------ | --------------------- | ----------- |
| chat_interactions  | ~2MB                  | Linear      |
| search_performance | ~1MB                  | Linear      |
| user_sessions      | ~0.5MB                | Linear      |
| query_analytics    | ~0.2MB                | Logarithmic |

#### Query Performance

**Optimized Queries**:

- Indexed lookups: < 1ms
- Range queries: 1-5ms
- Aggregation queries: 5-20ms

**Performance Monitoring**:

```sql
-- Check query performance
SELECT COUNT(*) as total_interactions,
       AVG(response_time) as avg_response_time
FROM chat_interactions
WHERE timestamp >= datetime('now', '-7 days');
```

### Database Maintenance

#### Regular Maintenance

```bash
# Optimize database
sqlite3 backend/statistics.db "VACUUM; ANALYZE;"

# Archive old data (older than 90 days)
sqlite3 backend/statistics.db "DELETE FROM chat_interactions WHERE timestamp < datetime('now', '-90 days');"

# Monitor database size
ls -lh backend/statistics.db
```

#### Performance Monitoring

```sql
-- Check table sizes
SELECT 'chat_interactions' as table_name, COUNT(*) as row_count,
       COUNT(*) * 2048 as estimated_bytes
FROM chat_interactions
UNION ALL
SELECT 'search_performance', COUNT(*), COUNT(*) * 1024
FROM search_performance;
```

## Memory Usage Metrics

### Component Memory Usage

#### Typical Memory Consumption

- **Sentence Transformer**: ~100MB (all-MiniLM-L6-v2)
- **ChromaDB**: ~50-100MB for 2400 documents
- **Flask Application**: ~20-50MB
- **Statistics Database**: ~1-5MB
- **Logging System**: ~5-10MB

#### Memory Optimization

**For Memory-Constrained Environments**:

```bash
# Use smaller embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Reduce search scope
SEMANTIC_SEARCH_TOP_K=3
HYBRID_SEARCH_TOP_K=3

# Optimize logging
LOG_LEVEL=WARNING
MAX_LOG_SIZE=5242880  # 5MB
```

### Memory Monitoring

```bash
# Monitor container memory
docker stats tum-chatbot-backend

# Check memory usage in container
docker exec tum-chatbot-backend ps aux --sort=-%mem
```

## Monitoring and Alerting

### Key Performance Indicators (KPIs)

#### Response Time KPIs

- **Average Response Time**: Target < 2.0 seconds
- **P95 Response Time**: Target < 5.0 seconds
- **Error Rate**: Target < 1%

#### Search Performance KPIs

- **Average Similarity Score**: Target > 0.5
- **Search Success Rate**: Target > 95%
- **Hybrid Search Usage**: Target > 70%

#### System Health KPIs

- **Database Size**: Monitor growth rate
- **Memory Usage**: Target < 80% of available
- **Disk Usage**: Target < 80% of available

### Monitoring Commands

#### Real-time Monitoring

```bash
# Health check
curl http://localhost:8080/api/health

# Performance metrics
curl "http://localhost:8080/api/statistics/performance?days=1"

# Usage statistics
curl "http://localhost:8080/api/statistics?days=7"
```

#### Database Monitoring

```bash
# Check database size
ls -lh backend/statistics.db

# Monitor query performance
sqlite3 backend/statistics.db "SELECT COUNT(*) FROM chat_interactions WHERE timestamp >= datetime('now', '-1 hour');"

# Check search method distribution
sqlite3 backend/statistics.db "SELECT search_method, COUNT(*) FROM chat_interactions GROUP BY search_method;"
```

### Alerting Thresholds

#### Critical Alerts

- **Response Time P95 > 10 seconds**
- **Error Rate > 5%**
- **Database Size > 1GB**
- **Memory Usage > 90%**

#### Warning Alerts

- **Response Time P95 > 5 seconds**
- **Error Rate > 1%**
- **Search Success Rate < 90%**
- **Memory Usage > 80%**

## Performance Optimization

### Search Optimization

#### Vector Database Optimization

```bash
# Optimize ChromaDB
# (ChromaDB handles optimization automatically)

# Monitor vector database size
ls -lh backend/chroma_db/
```

#### Search Parameter Tuning

```bash
# For faster searches (less accurate)
SEMANTIC_SEARCH_TOP_K=3
HYBRID_SEARCH_TOP_K=3
SIMILARITY_THRESHOLD=0.2

# For more accurate searches (slower)
SEMANTIC_SEARCH_TOP_K=8
HYBRID_SEARCH_TOP_K=8
SIMILARITY_THRESHOLD=0.5
```

### Database Optimization

#### Index Optimization

```sql
-- Create additional indexes if needed
CREATE INDEX IF NOT EXISTS idx_chat_user_role ON chat_interactions(user_role);
CREATE INDEX IF NOT EXISTS idx_chat_campus ON chat_interactions(user_campus);
```

#### Query Optimization

```sql
-- Use efficient date queries
SELECT COUNT(*) FROM chat_interactions
WHERE timestamp >= datetime('now', '-7 days');

-- Avoid expensive operations
SELECT search_method, COUNT(*)
FROM chat_interactions
GROUP BY search_method;
```

### Logging Optimization

#### Production Logging

```bash
# Reduce log verbosity
LOG_LEVEL=WARNING

# Optimize log rotation
MAX_LOG_SIZE=5242880  # 5MB
LOG_BACKUP_COUNT=3

# Disable chat session logging
LOG_CHAT_SESSIONS=False
```

### Memory Optimization

#### Container Memory Limits

```yaml
# In docker-compose.yml
services:
  tum-chatbot-backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

#### Application Memory Optimization

```bash
# Use smaller embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Reduce search scope
SEMANTIC_SEARCH_TOP_K=3
KEYWORD_SEARCH_TOP_K=3
HYBRID_SEARCH_TOP_K=3
```

### Performance Testing

#### Load Testing

```bash
# Simple load test
for i in {1..100}; do
  curl -X POST http://localhost:8080/api/chat \
    -H "Content-Type: application/json" \
    -H "X-User-ID: test$i" \
    -H "X-Session-ID: test$i" \
    -d '{"message": "test message"}' &
done
wait
```

#### Performance Benchmarking

```bash
# Test response times
curl -w "@curl-format.txt" -o /dev/null -s \
  -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-User-ID: perf_test" \
  -H "X-Session-ID: perf_test" \
  -d '{"message": "test message"}'
```

## Troubleshooting Performance Issues

### Common Performance Problems

#### High Response Times

**Symptoms**: P95 > 5 seconds, P99 > 10 seconds

**Causes**:

- Large knowledge base
- Complex queries
- Resource constraints
- Network latency

**Solutions**:

- Reduce search scope
- Optimize embedding model
- Increase resources
- Add caching

#### Low Similarity Scores

**Symptoms**: Average similarity < 0.3

**Causes**:

- Poor query matching
- Inadequate knowledge base
- Incorrect threshold setting

**Solutions**:

- Adjust similarity threshold
- Improve knowledge base
- Enhance search algorithms

#### High Memory Usage

**Symptoms**: Memory usage > 80%

**Causes**:

- Large embedding model
- Too many concurrent requests
- Memory leaks

**Solutions**:

- Use smaller embedding model
- Limit concurrent requests
- Monitor for memory leaks

### Performance Debugging

#### Enable Debug Logging

```bash
# Set debug environment
LOG_LEVEL=DEBUG
FLASK_DEBUG=True

# Monitor logs
tail -f backend/logs/tum_chatbot.log | grep "search\|performance"
```

#### Database Performance Analysis

```sql
-- Check slow queries
SELECT query, AVG(response_time) as avg_time, COUNT(*) as count
FROM chat_interactions
GROUP BY query
ORDER BY avg_time DESC
LIMIT 10;
```

#### Search Performance Analysis

```sql
-- Analyze search method effectiveness
SELECT search_method,
       COUNT(*) as total_searches,
       AVG(search_time) as avg_search_time,
       AVG(avg_similarity) as avg_similarity
FROM search_performance
GROUP BY search_method;
```

This comprehensive metrics guide provides all the information needed to understand, monitor, and optimize the TUM Chatbot's performance.
