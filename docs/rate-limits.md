# Rate Limits & Quotas

## Overview

TokenSwap API implements rate limiting to ensure fair usage and system stability. Rate limits are applied per API key and reset on a rolling window basis.

## Rate Limit Tiers

### Free Tier
- **Rate Limit**: 100 requests per minute
- **Burst Limit**: 10 requests per second
- **Monthly Quota**: 10,000 requests
- **Cost**: Free

### Pro Tier
- **Rate Limit**: 1,000 requests per minute
- **Burst Limit**: 50 requests per second
- **Monthly Quota**: 100,000 requests
- **Cost**: $99/month

### Enterprise Tier
- **Rate Limit**: 10,000 requests per minute
- **Burst Limit**: 200 requests per second
- **Monthly Quota**: 1,000,000 requests
- **Cost**: Custom pricing

## Endpoint-Specific Limits

### High-Frequency Endpoints
These endpoints have stricter limits due to computational complexity:

| Endpoint | Free | Pro | Enterprise |
|----------|------|-----|------------|
| `POST /swap` | 10/min | 100/min | 1,000/min |
| `GET /pools` | 50/min | 500/min | 5,000/min |
| `POST /quote` | 20/min | 200/min | 2,000/min |

### Read-Only Endpoints
These endpoints have more lenient limits:

| Endpoint | Free | Pro | Enterprise |
|----------|------|-----|------------|
| `GET /balance` | 100/min | 1,000/min | 10,000/min |
| `GET /tokens` | 100/min | 1,000/min | 10,000/min |
| `GET /health` | 200/min | 2,000/min | 20,000/min |

## Rate Limit Headers

Every API response includes rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
X-RateLimit-Retry-After: 60
X-RateLimit-Window: 60
```

### Header Descriptions

- `X-RateLimit-Limit`: Maximum requests allowed in the current window
- `X-RateLimit-Remaining`: Number of requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets
- `X-RateLimit-Retry-After`: Seconds to wait before retrying (only present on 429)
- `X-RateLimit-Window`: Length of the rate limit window in seconds

## Handling Rate Limits

### HTTP 429 Response

When rate limited, you'll receive:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 60,
    "limit": 1000,
    "remaining": 0,
    "reset_time": "2024-01-15T10:31:00Z"
  }
}
```

### Retry Strategies

#### Exponential Backoff
```python
import time
import random

def exponential_backoff(attempt, base_delay=1, max_delay=60):
    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
    time.sleep(delay)
```

#### Jittered Backoff
```python
def jittered_backoff(retry_after):
    jitter = random.uniform(0.1, 0.5) * retry_after
    time.sleep(retry_after + jitter)
```

### Best Practices

1. **Respect Retry-After**: Always use the `X-RateLimit-Retry-After` header
2. **Implement Backoff**: Use exponential backoff for retries
3. **Monitor Headers**: Track remaining requests to avoid limits
4. **Batch Requests**: Combine multiple operations when possible
5. **Cache Responses**: Cache data that doesn't change frequently

## Quota Management

### Monthly Quotas

Each tier has a monthly request quota that resets on the 1st of each month:

- **Free**: 10,000 requests/month
- **Pro**: 100,000 requests/month  
- **Enterprise**: 1,000,000 requests/month

### Quota Headers

Quota information is included in responses:

```
X-Quota-Limit: 100000
X-Quota-Remaining: 95000
X-Quota-Reset: 1640995200
```

### Quota Exhaustion

When monthly quota is exceeded:

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly quota exceeded. Upgrade your plan or wait for reset.",
    "quota_limit": 100000,
    "quota_remaining": 0,
    "quota_reset": "2024-02-01T00:00:00Z"
  }
}
```

## Rate Limit Bypass

### Priority Requests

Enterprise customers can use priority headers for urgent requests:

```
X-Priority: high
X-Priority-Reason: emergency-swap
```

Priority requests bypass normal rate limits but count against monthly quota.

### Webhook Exemptions

Webhook delivery attempts don't count against rate limits but have their own limits:
- **Free**: 100 webhook deliveries/hour
- **Pro**: 1,000 webhook deliveries/hour
- **Enterprise**: 10,000 webhook deliveries/hour

## Monitoring & Alerts

### Usage Dashboard

Monitor your API usage in real-time:
- Current rate limit utilization
- Monthly quota consumption
- Error rates and types
- Response time trends

### Alert Configuration

Set up alerts for:
- 80% rate limit utilization
- 90% monthly quota consumption
- High error rates (>5%)
- Unusual usage patterns

### Example Monitoring Code

```python
import time
from collections import defaultdict

class RateLimitMonitor:
    def __init__(self):
        self.requests = defaultdict(list)
        self.errors = defaultdict(int)
    
    def track_request(self, endpoint, response):
        now = time.time()
        self.requests[endpoint].append(now)
        
        # Clean old requests (older than 1 minute)
        self.requests[endpoint] = [
            req_time for req_time in self.requests[endpoint]
            if now - req_time < 60
        ]
        
        if response.status_code == 429:
            self.errors[endpoint] += 1
    
    def get_utilization(self, endpoint):
        recent_requests = len(self.requests[endpoint])
        # Assuming 100 requests per minute limit
        return recent_requests / 100.0
    
    def should_backoff(self, endpoint):
        return self.get_utilization(endpoint) > 0.8
```

## Upgrading Limits

### Automatic Upgrades

Temporarily increase limits during high-traffic periods:
- **Free → Pro**: 24-hour upgrade for $10
- **Pro → Enterprise**: 7-day upgrade for $50

### Permanent Upgrades

Contact support for permanent tier upgrades:
- Email: billing@tokenswap.io
- Include: Current usage patterns and expected growth
- Processing time: 1-2 business days

## Fair Use Policy

### Acceptable Use

- Normal trading operations
- Portfolio monitoring
- Data analysis and research
- Third-party integrations

### Prohibited Use

- Automated trading without proper rate limiting
- Scraping or data harvesting
- Attempting to circumvent rate limits
- Sharing API keys across multiple applications

### Enforcement

Violations may result in:
- Temporary rate limit reduction
- API key suspension
- Account termination (for severe violations)

## Support

For rate limit questions or issues:
- Email: support@tokenswap.io
- Include: API key (masked), error logs, and usage patterns
- Response time: < 24 hours
