# TokenSwap API Documentation

## Overview

The TokenSwap API provides a comprehensive interface for decentralized token exchange operations on the Ethereum blockchain. This RESTful API enables users to swap tokens, check balances, and manage liquidity positions with built-in rate limiting and error handling.

## Base URL

```
https://api.tokenswap.io/v1
```

## Authentication

All API requests require authentication using an API key in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits

- **Free Tier**: 100 requests per minute
- **Pro Tier**: 1,000 requests per minute
- **Enterprise**: 10,000 requests per minute

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error |

## Endpoints

### POST /swap

Execute a token swap operation between two supported tokens.

**Request Body:**
```json
{
  "from_token": "string",
  "to_token": "string", 
  "amount": "string",
  "slippage_tolerance": "number",
  "recipient": "string"
}
```

**Parameters:**
- `from_token` (required): Contract address of the source token
- `to_token` (required): Contract address of the destination token
- `amount` (required): Amount to swap (in wei)
- `slippage_tolerance` (optional): Maximum acceptable slippage (default: 0.5%)
- `recipient` (optional): Address to receive swapped tokens (defaults to sender)

**Response:**
```json
{
  "transaction_hash": "0x...",
  "from_token": "0x...",
  "to_token": "0x...",
  "amount_in": "1000000000000000000",
  "amount_out": "950000000000000000",
  "slippage": "0.05",
  "gas_used": "150000",
  "status": "pending"
}
```

**Error Responses:**
- `400`: Invalid token addresses or amount format
- `403`: Insufficient token balance
- `429`: Rate limit exceeded

### GET /balance

Retrieve the token balance for a specific address.

**Query Parameters:**
- `address` (required): Ethereum address to check balance for
- `token` (optional): Specific token contract address (defaults to ETH)

**Response:**
```json
{
  "address": "0x...",
  "token": "0x...",
  "balance": "1000000000000000000",
  "balance_formatted": "1.0",
  "decimals": 18,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400`: Invalid address format
- `404`: Token not found

### GET /pools

List available liquidity pools for token swapping.

**Query Parameters:**
- `token_a` (optional): Filter pools containing this token
- `token_b` (optional): Filter pools containing this token
- `limit` (optional): Maximum number of pools to return (default: 50)
- `offset` (optional): Number of pools to skip (default: 0)

**Response:**
```json
{
  "pools": [
    {
      "pool_id": "0x...",
      "token_a": "0x...",
      "token_b": "0x...",
      "reserve_a": "1000000000000000000",
      "reserve_b": "2000000000000000000",
      "liquidity": "1414213562373095048",
      "fee": "0.003",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

## Webhooks

The API supports webhooks for real-time notifications of swap events.

### Webhook Events

- `swap.completed`: Swap transaction confirmed
- `swap.failed`: Swap transaction failed
- `balance.updated`: Token balance changed

### Webhook Payload

```json
{
  "event": "swap.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "transaction_hash": "0x...",
    "user_address": "0x...",
    "amount_in": "1000000000000000000",
    "amount_out": "950000000000000000"
  }
}
```

## SDKs

Official SDKs are available for:
- JavaScript/TypeScript
- Python
- Go
- Rust

## Support

For technical support and questions:
- Email: support@tokenswap.io
- Discord: https://discord.gg/tokenswap
- Documentation: https://docs.tokenswap.io
