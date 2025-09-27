# Developer Quickstart

Make your first API request in minutes. Learn the basics of the ASI:One platform.

## Prerequisites

- ASI:One API key
- Basic knowledge of HTTP requests
- Your preferred programming language

## Getting Your API Key

1. Sign up for an ASI:One account
2. Navigate to the API Keys section in your dashboard
3. Click "Generate New API Key"
4. Copy and securely store your API key

## Making Your First Request

### cURL Example

```bash
curl -X POST https://api.asi1.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ASI_ONE_API_KEY" \
  -d '{
    "model": "asi1-mini",
    "messages": [
      {"role": "user", "content": "What is agentic AI?"}
    ]
  }'
```

### Python Example

```python
import openai

client = openai.OpenAI(
    api_key="your-api-key",
    base_url="https://api.asi1.ai/v1"
)

response = client.chat.completions.create(
    model="asi1-mini",
    messages=[
        {"role": "user", "content": "What is agentic AI?"}
    ]
)

print(response.choices[0].message.content)
```

### JavaScript Example

```javascript
const response = await fetch('https://api.asi1.ai/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    model: 'asi1-mini',
    messages: [
      { role: 'user', content: 'What is agentic AI?' }
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

## Understanding the Response

The API returns a response in the following format:

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "asi1-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Agentic AI refers to AI systems that can..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  }
}
```

## Next Steps

- Explore different models and their capabilities
- Learn about tool calling and function usage
- Integrate with your applications
- Build agentic AI systems
