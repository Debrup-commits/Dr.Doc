# Model Selection

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

### Performance Considerations

- **Response Time**: asi1-fast > asi1-mini > asi1-agentic > asi1-graph > asi1-extended
- **Capability**: asi1-extended > asi1-agentic > asi1-graph > asi1-mini > asi1-fast
- **Cost**: asi1-mini < asi1-fast < asi1-agentic < asi1-graph < asi1-extended

## Model Parameters

All models support the following parameters:

- `temperature`: Controls randomness (0.0 to 2.0)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Controls diversity (0.0 to 1.0)
- `stream`: Enable streaming responses

## Best Practices

1. **Start with asi1-mini** for development and testing
2. **Profile your application** to understand performance requirements
3. **Test different models** to find the best fit for your use case
4. **Monitor usage and costs** to optimize your model selection
5. **Use streaming** for real-time applications
