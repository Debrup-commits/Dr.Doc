# Advanced API Patterns and Design Principles

## Complex Authentication Flows

### OAuth 2.0 with PKCE Implementation

The TokenSwap API implements OAuth 2.0 with Proof Key for Code Exchange (PKCE) for enhanced security in public clients.

#### Authorization Code Flow with PKCE

```javascript
// Step 1: Generate code verifier and challenge
const codeVerifier = generateCodeVerifier();
const codeChallenge = await generateCodeChallenge(codeVerifier);

// Step 2: Redirect user to authorization server
const authUrl = `https://auth.tokenswap.io/oauth/authorize?` +
  `client_id=${clientId}&` +
  `redirect_uri=${redirectUri}&` +
  `response_type=code&` +
  `code_challenge=${codeChallenge}&` +
  `code_challenge_method=S256&` +
  `scope=read:trades write:swaps`;

// Step 3: Exchange authorization code for tokens
const tokenResponse = await fetch('https://auth.tokenswap.io/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: clientId,
    code: authorizationCode,
    redirect_uri: redirectUri,
    code_verifier: codeVerifier
  })
});
```

#### Token Refresh Pattern

```javascript
class TokenManager {
  constructor() {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiry = null;
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch('https://auth.tokenswap.io/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: this.refreshToken,
        client_id: this.clientId
      })
    });

    const tokens = await response.json();
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
    this.tokenExpiry = Date.now() + (tokens.expires_in * 1000);
  }

  async getValidToken() {
    if (!this.accessToken || Date.now() >= this.tokenExpiry) {
      await this.refreshAccessToken();
    }
    return this.accessToken;
  }
}
```

## Advanced Rate Limiting Strategies

### Tiered Rate Limiting System

The API implements a sophisticated multi-tier rate limiting system:

#### Rate Limit Tiers

| Tier | Requests/Minute | Burst Limit | Monthly Quota | Features |
|------|----------------|-------------|---------------|----------|
| **Free** | 100 | 10/sec | 10,000/month | Basic endpoints only |
| **Pro** | 1,000 | 50/sec | 100,000/month | All endpoints, webhooks |
| **Enterprise** | 10,000 | 200/sec | 1,000,000/month | Custom limits, priority support |

#### Adaptive Rate Limiting

```python
class AdaptiveRateLimiter:
    def __init__(self, base_limit=100, burst_multiplier=2):
        self.base_limit = base_limit
        self.burst_limit = base_limit * burst_multiplier
        self.current_limit = base_limit
        self.request_history = []
        
    def can_make_request(self, user_id: str) -> bool:
        now = time.time()
        # Clean old requests
        self.request_history = [
            req_time for req_time in self.request_history 
            if now - req_time < 60
        ]
        
        # Check if under limit
        if len(self.request_history) < self.current_limit:
            self.request_history.append(now)
            return True
            
        return False
    
    def adjust_limit(self, success_rate: float):
        """Dynamically adjust rate limits based on success rate"""
        if success_rate > 0.95:
            self.current_limit = min(self.burst_limit, self.current_limit * 1.1)
        elif success_rate < 0.8:
            self.current_limit = max(self.base_limit, self.current_limit * 0.9)
```

### Circuit Breaker Pattern

```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.threshold = threshold;
    this.timeout = timeout;
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
  }

  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.threshold) {
      this.state = 'OPEN';
    }
  }
}
```

## Complex Error Handling Patterns

### Hierarchical Error Codes

The API uses a hierarchical error code system:

```
4xx - Client Errors
├── 400 - Bad Request
│   ├── 4001 - Invalid JSON format
│   ├── 4002 - Missing required field
│   ├── 4003 - Invalid field value
│   └── 4004 - Field validation failed
├── 401 - Unauthorized
│   ├── 4011 - Invalid API key
│   ├── 4012 - Expired token
│   ├── 4013 - Insufficient permissions
│   └── 4014 - Token refresh required
├── 403 - Forbidden
│   ├── 4031 - Rate limit exceeded
│   ├── 4032 - Quota exceeded
│   ├── 4033 - Account suspended
│   └── 4034 - Feature not available
└── 404 - Not Found
    ├── 4041 - Endpoint not found
    ├── 4042 - Resource not found
    ├── 4043 - Token not supported
    └── 4044 - Pool not found

5xx - Server Errors
├── 500 - Internal Server Error
│   ├── 5001 - Database connection failed
│   ├── 5002 - External service unavailable
│   ├── 5003 - Processing timeout
│   └── 5004 - Unexpected error
├── 502 - Bad Gateway
│   ├── 5021 - Blockchain node unreachable
│   ├── 5022 - Price oracle failure
│   └── 5023 - External API timeout
└── 503 - Service Unavailable
    ├── 5031 - Maintenance mode
    ├── 5032 - High load
    └── 5033 - Feature temporarily disabled
```

### Error Response Format

```json
{
  "error": {
    "code": "4003",
    "type": "INVALID_FIELD_VALUE",
    "message": "The amount field must be a positive number",
    "details": {
      "field": "amount",
      "value": "-100",
      "constraints": {
        "min": 0,
        "type": "number"
      },
      "suggestion": "Please provide a positive number for the amount"
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z",
    "documentation_url": "https://docs.tokenswap.io/errors/4003",
    "support_url": "https://support.tokenswap.io/contact"
  }
}
```

## Advanced Query Patterns

### Complex Filtering and Pagination

```javascript
// Multi-dimensional filtering
const complexQuery = {
  filters: {
    tokens: {
      from: ['0x1234...', '0x5678...'],
      to: { exclude: ['0x9999...'] }
    },
    timeRange: {
      start: '2024-01-01T00:00:00Z',
      end: '2024-01-31T23:59:59Z'
    },
    amounts: {
      min: '1000000000000000000', // 1 ETH in wei
      max: '100000000000000000000' // 100 ETH in wei
    },
    status: ['completed', 'pending'],
    gasPrice: {
      gte: '20000000000' // 20 gwei
    }
  },
  pagination: {
    page: 1,
    limit: 50,
    cursor: 'eyJpZCI6MTIzNDU2Nzg5fQ==',
    sort: [
      { field: 'timestamp', order: 'desc' },
      { field: 'amount', order: 'desc' }
    ]
  },
  aggregations: {
    groupBy: ['from_token', 'to_token'],
    metrics: ['count', 'sum_amount', 'avg_gas_used'],
    timeBuckets: '1d'
  }
};
```

### GraphQL-style Field Selection

```javascript
// Request specific fields to optimize response size
const fieldSelection = {
  fields: {
    swap: ['id', 'timestamp', 'amount_in', 'amount_out', 'status'],
    tokens: {
      from: ['symbol', 'name', 'decimals'],
      to: ['symbol', 'name', 'decimals']
    },
    metadata: {
      gas_used: true,
      gas_price: true,
      block_number: false // Exclude this field
    }
  },
  include: ['sources', 'fees'],
  exclude: ['raw_transaction_data']
};
```

## Webhook System Architecture

### Event-Driven Architecture

```javascript
class WebhookManager {
  constructor() {
    this.eventTypes = new Map();
    this.subscriptions = new Map();
    this.retryQueue = [];
  }

  registerEventType(type, schema) {
    this.eventTypes.set(type, schema);
  }

  subscribe(userId, endpoint, events, options = {}) {
    const subscription = {
      id: generateId(),
      userId,
      endpoint,
      events,
      secret: generateSecret(),
      retryPolicy: {
        maxRetries: options.maxRetries || 3,
        backoffMultiplier: options.backoffMultiplier || 2,
        initialDelay: options.initialDelay || 1000
      },
      filters: options.filters || {},
      createdAt: new Date(),
      status: 'active'
    };

    this.subscriptions.set(subscription.id, subscription);
    return subscription;
  }

  async deliverEvent(event, subscription) {
    const payload = {
      id: event.id,
      type: event.type,
      data: event.data,
      timestamp: event.timestamp,
      version: '1.0'
    };

    const signature = this.generateSignature(payload, subscription.secret);
    
    try {
      const response = await fetch(subscription.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-TokenSwap-Signature': signature,
          'X-TokenSwap-Event-Type': event.type,
          'X-TokenSwap-Event-ID': event.id
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Webhook delivery failed: ${response.status}`);
      }

      return { success: true, response };
    } catch (error) {
      await this.handleDeliveryFailure(event, subscription, error);
      throw error;
    }
  }

  async handleDeliveryFailure(event, subscription, error) {
    const retryAttempt = {
      eventId: event.id,
      subscriptionId: subscription.id,
      attempt: 1,
      nextRetry: Date.now() + subscription.retryPolicy.initialDelay,
      error: error.message
    };

    this.retryQueue.push(retryAttempt);
  }
}
```

### Webhook Security

```javascript
class WebhookSecurity {
  static generateSignature(payload, secret) {
    const hmac = crypto.createHmac('sha256', secret);
    hmac.update(JSON.stringify(payload));
    return `sha256=${hmac.digest('hex')}`;
  }

  static verifySignature(payload, signature, secret) {
    const expectedSignature = this.generateSignature(payload, secret);
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  }

  static validateTimestamp(timestamp, toleranceSeconds = 300) {
    const eventTime = new Date(timestamp).getTime();
    const now = Date.now();
    const diff = Math.abs(now - eventTime) / 1000;
    
    return diff <= toleranceSeconds;
  }
}
```

## Performance Optimization Patterns

### Caching Strategies

```javascript
class CacheManager {
  constructor() {
    this.memoryCache = new Map();
    this.redisClient = null;
    this.cacheLayers = ['memory', 'redis', 'database'];
  }

  async get(key, options = {}) {
    // Try memory cache first
    if (this.memoryCache.has(key)) {
      const item = this.memoryCache.get(key);
      if (item.expiry > Date.now()) {
        return item.data;
      }
      this.memoryCache.delete(key);
    }

    // Try Redis cache
    if (this.redisClient) {
      try {
        const data = await this.redisClient.get(key);
        if (data) {
          const parsed = JSON.parse(data);
          // Store in memory cache for faster access
          this.setMemoryCache(key, parsed, options.ttl);
          return parsed;
        }
      } catch (error) {
        console.warn('Redis cache error:', error);
      }
    }

    return null;
  }

  async set(key, data, options = {}) {
    const ttl = options.ttl || 3600; // Default 1 hour

    // Set in memory cache
    this.setMemoryCache(key, data, ttl);

    // Set in Redis cache
    if (this.redisClient) {
      try {
        await this.redisClient.setex(key, ttl, JSON.stringify(data));
      } catch (error) {
        console.warn('Redis cache set error:', error);
      }
    }
  }

  setMemoryCache(key, data, ttl) {
    this.memoryCache.set(key, {
      data,
      expiry: Date.now() + (ttl * 1000)
    });
  }
}
```

### Database Query Optimization

```sql
-- Optimized query with proper indexing
EXPLAIN ANALYZE
SELECT 
    s.id,
    s.amount_in,
    s.amount_out,
    s.status,
    s.timestamp,
    ft.symbol as from_symbol,
    tt.symbol as to_symbol
FROM swaps s
JOIN tokens ft ON s.from_token_id = ft.id
JOIN tokens tt ON s.to_token_id = tt.id
WHERE s.user_id = $1
    AND s.timestamp >= $2
    AND s.timestamp <= $3
    AND s.status IN ('completed', 'pending')
ORDER BY s.timestamp DESC
LIMIT 50;

-- Composite index for optimal performance
CREATE INDEX CONCURRENTLY idx_swaps_user_time_status 
ON swaps (user_id, timestamp DESC, status) 
WHERE status IN ('completed', 'pending');
```

## Security Best Practices

### Input Validation and Sanitization

```javascript
class InputValidator {
  static validateSwapRequest(data) {
    const schema = {
      from_token: {
        required: true,
        type: 'string',
        pattern: /^0x[a-fA-F0-9]{40}$/,
        message: 'Must be a valid Ethereum address'
      },
      to_token: {
        required: true,
        type: 'string',
        pattern: /^0x[a-fA-F0-9]{40}$/,
        message: 'Must be a valid Ethereum address'
      },
      amount: {
        required: true,
        type: 'string',
        pattern: /^\d+$/,
        validate: (value) => BigInt(value) > 0,
        message: 'Must be a positive integer'
      },
      slippage_tolerance: {
        required: false,
        type: 'number',
        min: 0.1,
        max: 50,
        default: 0.5,
        message: 'Must be between 0.1 and 50 percent'
      }
    };

    return this.validateAgainstSchema(data, schema);
  }

  static sanitizeString(input) {
    return input
      .trim()
      .replace(/[<>\"']/g, '') // Remove potentially dangerous characters
      .substring(0, 1000); // Limit length
  }
}
```

### API Key Management

```javascript
class APIKeyManager {
  static generateKey() {
    const randomBytes = crypto.randomBytes(32);
    const prefix = 'tsk_';
    const key = randomBytes.toString('base64url');
    return prefix + key;
  }

  static hashKey(key) {
    return crypto.createHash('sha256').update(key).digest('hex');
  }

  static validateKeyFormat(key) {
    return /^tsk_[A-Za-z0-9_-]{43}$/.test(key);
  }

  static async rotateKey(oldKey, newKey) {
    // Implement key rotation logic
    // 1. Validate new key format
    // 2. Hash and store new key
    // 3. Mark old key as deprecated
    // 4. Set grace period for old key
    // 5. Notify user of rotation
  }
}
```

## Monitoring and Observability

### Comprehensive Logging

```javascript
class Logger {
  constructor(service = 'tokenswap-api') {
    this.service = service;
    this.logLevel = process.env.LOG_LEVEL || 'info';
  }

  log(level, message, metadata = {}) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      service: this.service,
      message,
      ...metadata
    };

    // Console output for development
    if (process.env.NODE_ENV === 'development') {
      console.log(JSON.stringify(logEntry, null, 2));
    }

    // Send to logging service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToLoggingService(logEntry);
    }
  }

  info(message, metadata) {
    this.log('info', message, metadata);
  }

  error(message, error, metadata = {}) {
    this.log('error', message, {
      ...metadata,
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name
      }
    });
  }
}
```

### Performance Metrics

```javascript
class MetricsCollector {
  constructor() {
    this.counters = new Map();
    this.gauges = new Map();
    this.histograms = new Map();
  }

  incrementCounter(name, labels = {}, value = 1) {
    const key = this.createKey(name, labels);
    this.counters.set(key, (this.counters.get(key) || 0) + value);
  }

  setGauge(name, labels = {}, value) {
    const key = this.createKey(name, labels);
    this.gauges.set(key, value);
  }

  recordHistogram(name, labels = {}, value) {
    const key = this.createKey(name, labels);
    if (!this.histograms.has(key)) {
      this.histograms.set(key, []);
    }
    this.histograms.get(key).push(value);
  }

  createKey(name, labels) {
    const sortedLabels = Object.keys(labels)
      .sort()
      .map(key => `${key}=${labels[key]}`)
      .join(',');
    return `${name}{${sortedLabels}}`;
  }
}
```

This documentation demonstrates complex API patterns that require sophisticated reasoning capabilities, making it perfect for MeTTa integration to provide precise, structured answers about these advanced concepts.




