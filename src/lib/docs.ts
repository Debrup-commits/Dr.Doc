// Documentation data structure
export interface DocSection {
  id: string;
  title: string;
  content: string;
  order: number;
}

export interface DocCategory {
  id: string;
  title: string;
  sections: DocSection[];
  order: number;
}

// Documentation content
export const documentation: DocCategory[] = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    order: 1,
    sections: [
      {
        id: 'overview',
        title: 'Overview',
        order: 1,
        content: `# ASI:One Developer Platform

ASI:One is an intelligent AI platform built by Fetch.ai. ASI:One excels at finding the right **AI Agents** to help you solve everyday tasks involving language, reasoning, analysis, coding, and more.

## Key Features

### Agentic Reasoning

ASI1 can autonomously plan, execute, and adapt its approach based on evolving inputs and goals.

### Natural Language Understanding

ASI1 is highly proficient in understanding and generating human-like text across multiple domains.

### Multi-Step Task Execution

Handle complex, goal-oriented tasks without constant user intervention.

### Contextual Memory

Retains and utilizes context for longer, more coherent interactions.

### API-Driven Integration

Easily embed ASI1 into your applications through a simple, powerful API.

### Web3 Native

Designed from the ground up for decentralized environments and blockchain interactions.

## Meet the Models

### asi1-mini
Balanced performance and speed

### asi1-fast
Optimized for quick responses

### asi1-extended
Enhanced capabilities for complex tasks

### asi1-agentic
Specialized for agent interactions

### asi1-graph
Optimized for data analytics and graphs

## Start Building

- **Chat Completion**: Use the API to prompt a model and generate text
- **Tool Calling**: Enable models to use external tools and APIs
- **Image Generation**: Create images from text descriptions
- **Agent Chat Protocol**: Enable agents to communicate with each other
- **Agentic LLM**: Call agents from Agentverse for complex tasks
- **Structured Data**: Get model responses that adhere to a JSON schema
- **OpenAI Compatibility**: Use OpenAI SDK with ASI:One`
      },
      {
        id: 'quickstart',
        title: 'Developer Quickstart',
        order: 2,
        content: `# Developer Quickstart

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

\`\`\`bash
curl -X POST https://api.asi1.ai/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $ASI_ONE_API_KEY" \\
  -d '{
    "model": "asi1-mini",
    "messages": [
      {"role": "user", "content": "What is agentic AI?"}
    ]
  }'
\`\`\`

### Python Example

\`\`\`python
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
\`\`\`

### JavaScript Example

\`\`\`javascript
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
\`\`\`

## Understanding the Response

The API returns a response in the following format:

\`\`\`json
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
\`\`\`

## Next Steps

- Explore different models and their capabilities
- Learn about tool calling and function usage
- Integrate with your applications
- Build agentic AI systems`
      },
      {
        id: 'models',
        title: 'Model Selection',
        order: 3,
        content: `# Model Selection

ASI:One offers a variety of models optimized for different use cases. Choose the right model for your specific needs.

## Available Models

### asi1-mini
**Balanced performance and speed**

- **Best for**: General-purpose tasks, development, testing
- **Strengths**: Fast responses, cost-effective, good for most use cases
- **Use cases**: Chat applications, content generation, basic reasoning

### asi1-fast
**Optimized for quick responses**

- **Best for**: Real-time applications, high-throughput scenarios
- **Strengths**: Ultra-fast response times, low latency
- **Use cases**: Live chat, real-time assistance, high-frequency requests

### asi1-extended
**Enhanced capabilities for complex tasks**

- **Best for**: Complex reasoning, detailed analysis, multi-step tasks
- **Strengths**: Advanced reasoning, better context understanding
- **Use cases**: Research, analysis, complex problem-solving

### asi1-agentic
**Specialized for agent interactions**

- **Best for**: Multi-agent systems, autonomous agents, agent communication
- **Strengths**: Agent-specific optimizations, better agent reasoning
- **Use cases**: Agent development, multi-agent coordination, autonomous systems

### asi1-graph
**Optimized for data analytics and graphs**

- **Best for**: Data analysis, graph processing, analytical tasks
- **Strengths**: Data processing, analytical reasoning, graph operations
- **Use cases**: Data analysis, business intelligence, graph-based applications

## Model Comparison

| Model | Speed | Capability | Cost | Best For |
|-------|-------|------------|------|----------|
| asi1-mini | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | General use |
| asi1-fast | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Real-time apps |
| asi1-extended | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Complex tasks |
| asi1-agentic | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Agent systems |
| asi1-graph | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Data analysis |

## Choosing the Right Model

### For Development and Testing
- Use **asi1-mini** for cost-effective development and testing

### For Production Applications
- Use **asi1-fast** for real-time user interactions
- Use **asi1-extended** for complex reasoning tasks
- Use **asi1-agentic** for agent-based applications
- Use **asi1-graph** for data analysis applications

## Best Practices

1. **Start with asi1-mini** for development and testing
2. **Profile your application** to understand performance requirements
3. **Test different models** to find the best fit for your use case
4. **Monitor usage and costs** to optimize your model selection
5. **Use streaming** for real-time applications`
      }
    ]
  },
  {
    id: 'build-with-asi-one',
    title: 'Build with ASI:One',
    order: 2,
    sections: [
      {
        id: 'tool-calling',
        title: 'Tool Calling',
        order: 1,
        content: `# Tool Calling

Enable models to use external tools and APIs to extend their capabilities beyond text generation.

## Overview

Tool calling allows ASI:One models to interact with external systems, APIs, and services. This enables the models to:

- Access real-time data
- Perform actions in external systems
- Retrieve information from databases
- Integrate with third-party services

## How Tool Calling Works

1. **Define Tools**: Specify available tools and their schemas
2. **Model Decision**: The model decides which tools to use
3. **Tool Execution**: Execute the selected tools with provided parameters
4. **Response Generation**: Generate a response based on tool results

## Tool Definition

Tools are defined using JSON Schema format:

\`\`\`json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get the current weather for a location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city and state, e.g. San Francisco, CA"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"],
          "description": "The temperature unit"
        }
      },
      "required": ["location"]
    }
  }
}
\`\`\`

## Example Implementation

### Python Example

\`\`\`python
import openai
import json

client = openai.OpenAI(
    api_key="your-api-key",
    base_url="https://api.asi1.ai/v1"
)

# Define available tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Make a request with tool calling
response = client.chat.completions.create(
    model="asi1-mini",
    messages=[
        {"role": "user", "content": "What's the weather like in New York?"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    
    if tool_call.function.name == "get_weather":
        # Execute the tool
        args = json.loads(tool_call.function.arguments)
        weather_data = get_weather(args["location"])
        
        # Send tool result back to the model
        response = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "user", "content": "What's the weather like in New York?"},
                {"role": "assistant", "content": None, "tool_calls": [tool_call]},
                {"role": "tool", "content": weather_data, "tool_call_id": tool_call.id}
            ],
            tools=tools
        )
        
        print(response.choices[0].message.content)
\`\`\`

## Best Practices

1. **Clear Descriptions**: Provide clear, concise descriptions for tools
2. **Parameter Validation**: Validate tool parameters before execution
3. **Error Handling**: Handle tool execution errors gracefully
4. **Security**: Validate and sanitize tool inputs
5. **Performance**: Consider tool execution time and costs
6. **Testing**: Test tools thoroughly before production use

## Common Use Cases

- **Data Retrieval**: Fetch data from databases or APIs
- **Calculations**: Perform complex calculations or analysis
- **File Operations**: Read, write, or manipulate files
- **External Services**: Integrate with third-party services
- **Real-time Information**: Access current data or status`
      },
      {
        id: 'agent-chat-protocol',
        title: 'Agent Chat Protocol',
        order: 2,
        content: `# Agent Chat Protocol

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

\`\`\`json
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
\`\`\`

#### ChatAcknowledgement
Confirmation that a message was received.

\`\`\`json
{
  "timestamp": "2024-01-01T12:00:01Z",
  "acknowledged_msg_id": "unique-message-id"
}
\`\`\`

## Implementation Example

### Python Implementation

\`\`\`python
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

# Include protocol in agent
agent.include(protocol, publish_manifest=True)

def process_message(text: str) -> str:
    # Your message processing logic here
    return f"Processed: {text}"

if __name__ == "__main__":
    agent.run()
\`\`\`

## Message Flow

1. **Message Sent**: Agent A sends a ChatMessage to Agent B
2. **Acknowledgement**: Agent B sends ChatAcknowledgement back to Agent A
3. **Processing**: Agent B processes the message content
4. **Response**: Agent B sends a response ChatMessage to Agent A
5. **Session End**: Agent B includes EndSessionContent to close the session

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
- **Fault Tolerance**: Implement redundancy and failover mechanisms`
      }
    ]
  }
];

// Helper functions
export function getDocCategory(categoryId: string): DocCategory | undefined {
  return documentation.find(cat => cat.id === categoryId);
}

export function getDocSection(categoryId: string, sectionId: string): DocSection | undefined {
  const category = getDocCategory(categoryId);
  return category?.sections.find(sec => sec.id === sectionId);
}

export function getAllCategories(): DocCategory[] {
  return documentation.sort((a, b) => a.order - b.order);
}

export function getCategorySections(categoryId: string): DocSection[] {
  const category = getDocCategory(categoryId);
  return category?.sections.sort((a, b) => a.order - b.order) || [];
}
