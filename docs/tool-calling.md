# Tool Calling

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

```json
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
```

## Example Implementation

### Python Example

```python
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
```

### JavaScript Example

```javascript
const tools = [
  {
    type: "function",
    function: {
      name: "get_weather",
      description: "Get the current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "The city and state"
          }
        },
        required: ["location"]
      }
    }
  }
];

const response = await fetch('https://api.asi1.ai/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    model: 'asi1-mini',
    messages: [
      { role: 'user', content: 'What\'s the weather like in New York?' }
    ],
    tools: tools,
    tool_choice: 'auto'
  })
});

const data = await response.json();

// Handle tool calls
if (data.choices[0].message.tool_calls) {
  const toolCall = data.choices[0].message.tool_calls[0];
  
  if (toolCall.function.name === 'get_weather') {
    const args = JSON.parse(toolCall.function.arguments);
    const weatherData = await getWeather(args.location);
    
    // Send tool result back
    const finalResponse = await fetch('https://api.asi1.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-api-key'
      },
      body: JSON.stringify({
        model: 'asi1-mini',
        messages: [
          { role: 'user', content: 'What\'s the weather like in New York?' },
          { role: 'assistant', content: null, tool_calls: [toolCall] },
          { role: 'tool', content: weatherData, tool_call_id: toolCall.id }
        ],
        tools: tools
      })
    });
    
    const finalData = await finalResponse.json();
    console.log(finalData.choices[0].message.content);
  }
}
```

## Tool Choice Options

### auto
Let the model decide whether to use tools (default)

### none
Disable tool calling

### specific
Force the model to use a specific tool

```json
{
  "type": "function",
  "function": {
    "name": "get_weather"
  }
}
```

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
- **Real-time Information**: Access current data or status

## Limitations

- Tools must be defined in JSON Schema format
- Tool execution happens outside the model
- Tool results are limited by API response size
- Some tools may have rate limits or costs
