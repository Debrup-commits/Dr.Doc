# Agent Chat Protocol

Enable agents to communicate with each other using a standardized protocol for seamless multi-agent interactions.

## Overview

The Agent Chat Protocol is a standardized communication framework that allows AI agents to interact with each other in a structured, reliable manner. This protocol enables:

- **Inter-agent Communication**: Agents can send messages to each other
- **Protocol Compliance**: Standardized message formats and behaviors
- **Error Handling**: Robust error handling and acknowledgments
- **Session Management**: Proper session lifecycle management

## Protocol Specification

### Message Types

#### ChatMessage
Primary message type for agent communication.

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "msg_id": "unique-message-id",
  "content": [
    {
      "type": "text",
      "text": "Hello, how can you help me?"
    }
  ]
}
```

#### ChatAcknowledgement
Confirmation that a message was received.

```json
{
  "timestamp": "2024-01-01T12:00:01Z",
  "acknowledged_msg_id": "unique-message-id"
}
```

#### EndSessionContent
Indicates the end of a conversation session.

```json
{
  "type": "end-session"
}
```

### Content Types

#### TextContent
Standard text content for messages.

```json
{
  "type": "text",
  "text": "Your message content here"
}
```

#### StructuredContent
For structured data exchange.

```json
{
  "type": "structured",
  "data": {
    "key": "value",
    "nested": {
      "property": "value"
    }
  }
}
```

## Implementation Example

### Python Implementation

```python
from datetime import datetime
from uuid import uuid4
from uagents import Context, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Create agent
agent = Agent(
    name="chat-agent",
    seed="chat-agent-seed",
    port=8001,
    mailbox=True,
)

# Create protocol
protocol = Protocol(spec=chat_protocol_spec)

@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(), 
            acknowledged_msg_id=msg.msg_id
        ),
    )
    
    # Extract text content
    text = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text
    
    # Process the message
    response = process_message(text)
    
    # Send response
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=response),
            EndSessionContent(type="end-session"),
        ]
    ))

@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender}")

# Include protocol in agent
agent.include(protocol, publish_manifest=True)

def process_message(text: str) -> str:
    # Your message processing logic here
    return f"Processed: {text}"

if __name__ == "__main__":
    agent.run()
```

### JavaScript Implementation

```javascript
class ChatAgent {
  constructor(name, seed, port) {
    this.name = name;
    this.seed = seed;
    this.port = port;
    this.mailbox = true;
  }

  async handleMessage(sender, message) {
    // Send acknowledgement
    await this.sendAcknowledgement(sender, message.msg_id);
    
    // Extract text content
    let text = '';
    for (const item of message.content) {
      if (item.type === 'text') {
        text += item.text;
      }
    }
    
    // Process the message
    const response = this.processMessage(text);
    
    // Send response
    await this.sendResponse(sender, response);
  }

  async sendAcknowledgement(sender, msgId) {
    const ack = {
      timestamp: new Date().toISOString(),
      acknowledged_msg_id: msgId
    };
    
    await this.send(sender, ack);
  }

  async sendResponse(sender, response) {
    const message = {
      timestamp: new Date().toISOString(),
      msg_id: this.generateId(),
      content: [
        { type: 'text', text: response },
        { type: 'end-session' }
      ]
    };
    
    await this.send(sender, message);
  }

  processMessage(text) {
    // Your message processing logic here
    return `Processed: ${text}`;
  }

  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }
}
```

## Message Flow

1. **Message Sent**: Agent A sends a ChatMessage to Agent B
2. **Acknowledgement**: Agent B sends ChatAcknowledgement back to Agent A
3. **Processing**: Agent B processes the message content
4. **Response**: Agent B sends a response ChatMessage to Agent A
5. **Session End**: Agent B includes EndSessionContent to close the session

## Error Handling

### Timeout Handling
```python
import asyncio

async def send_with_timeout(ctx, recipient, message, timeout=30):
    try:
        await asyncio.wait_for(
            ctx.send(recipient, message),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        ctx.logger.error(f"Timeout sending message to {recipient}")
```

### Retry Logic
```python
async def send_with_retry(ctx, recipient, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            await ctx.send(recipient, message)
            return
        except Exception as e:
            if attempt == max_retries - 1:
                ctx.logger.error(f"Failed to send message after {max_retries} attempts: {e}")
            else:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Best Practices

1. **Always Acknowledge**: Send acknowledgements for received messages
2. **Handle Errors**: Implement proper error handling and retry logic
3. **Validate Content**: Validate message content before processing
4. **Manage Sessions**: Properly manage session lifecycle
5. **Log Interactions**: Log all agent interactions for debugging
6. **Secure Communication**: Use secure channels for sensitive communications

## Use Cases

- **Multi-Agent Systems**: Coordinate multiple agents for complex tasks
- **Agent Orchestration**: Manage workflows across different agents
- **Service Discovery**: Agents can discover and communicate with each other
- **Load Balancing**: Distribute tasks across multiple agent instances
- **Fault Tolerance**: Implement redundancy and failover mechanisms

## Integration with ASI:One

The Agent Chat Protocol integrates seamlessly with ASI:One models:

```python
from openai import OpenAI

client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key=os.getenv("ASI_API_KEY")
)

async def process_with_asi_one(text: str) -> str:
    response = client.chat.completions.create(
        model="asi1-agentic",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
```

This enables agents to leverage ASI:One's powerful language models while maintaining standardized communication protocols.
