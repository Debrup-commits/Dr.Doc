# Authentication & Security

## API Key Management

### Obtaining API Keys

1. Register at [https://dashboard.tokenswap.io](https://dashboard.tokenswap.io)
2. Navigate to API Keys section
3. Generate a new API key with appropriate permissions
4. Store the key securely - it cannot be retrieved once generated

### Key Types

| Type | Permissions | Rate Limit |
|------|-------------|------------|
| **Read** | GET endpoints only | 100 req/min |
| **Trade** | All endpoints | 1,000 req/min |
| **Admin** | All endpoints + management | 10,000 req/min |

### Key Rotation

- Keys expire after 90 days by default
- Set up key rotation before expiration
- Old keys remain valid for 24 hours after rotation

## Request Signing

For enhanced security, all requests can be signed using EIP-712:

```javascript
const signature = await signTypedData({
  domain: {
    name: 'TokenSwap API',
    version: '1',
    chainId: 1
  },
  types: {
    SwapRequest: [
      { name: 'fromToken', type: 'address' },
      { name: 'toToken', type: 'address' },
      { name: 'amount', type: 'uint256' },
      { name: 'nonce', type: 'uint256' }
    ]
  },
  primaryType: 'SwapRequest',
  message: swapData
});
```

## IP Whitelisting

Enterprise customers can whitelist specific IP addresses:

1. Go to Security Settings in dashboard
2. Add IP addresses or CIDR blocks
3. API requests from non-whitelisted IPs will be rejected

## Rate Limiting

### Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
X-RateLimit-Retry-After: 60
```

### Handling Rate Limits

When rate limited (HTTP 429):

1. Check `X-RateLimit-Reset` header for reset time
2. Implement exponential backoff
3. Consider upgrading your plan

### Example Implementation

```python
import time
import requests

def make_request_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('X-RateLimit-Retry-After', 60))
            time.sleep(retry_after)
            continue
            
        return response
    
    raise Exception("Max retries exceeded")
```

## Security Best Practices

### API Key Storage

- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly
- Use different keys for different environments

### Request Validation

- Always validate responses from the API
- Check transaction hashes on-chain
- Implement proper error handling
- Use HTTPS only

### Example Secure Implementation

```python
import os
import hmac
import hashlib
import time

class TokenSwapClient:
    def __init__(self, api_key, secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.tokenswap.io/v1"
    
    def _sign_request(self, method, path, body=""):
        if not self.secret_key:
            return {}
            
        timestamp = str(int(time.time()))
        message = f"{method}{path}{body}{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'X-Timestamp': timestamp,
            'X-Signature': signature
        }
    
    def swap_tokens(self, from_token, to_token, amount):
        path = "/swap"
        body = {
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            **self._sign_request('POST', path, json.dumps(body))
        }
        
        response = requests.post(
            f"{self.base_url}{path}",
            json=body,
            headers=headers
        )
        
        return response.json()
```

## Error Handling

### Common Error Scenarios

1. **Invalid API Key**: Check key format and permissions
2. **Rate Limited**: Implement backoff strategy
3. **Network Issues**: Retry with exponential backoff
4. **Invalid Parameters**: Validate input before sending

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_TOKEN_ADDRESS",
    "message": "The provided token address is not valid",
    "details": {
      "field": "from_token",
      "value": "0xinvalid",
      "expected_format": "Ethereum address (0x...)"
    },
    "request_id": "req_123456789"
  }
}
```

## Monitoring & Logging

### API Usage Dashboard

Monitor your API usage in real-time:
- Request volume and patterns
- Error rates and types
- Rate limit utilization
- Response times

### Webhook Monitoring

Set up webhooks for:
- Failed authentication attempts
- Rate limit violations
- Unusual usage patterns
- System maintenance notifications

## Compliance

### Data Protection

- All data is encrypted in transit (TLS 1.3)
- Sensitive data is encrypted at rest
- API keys are hashed and salted
- Personal data is handled per GDPR guidelines

### Audit Logging

- All API requests are logged
- Logs include timestamp, IP, endpoint, and response
- Logs are retained for 1 year
- Available for compliance audits
