# ASI:One uAgent Testing Guide

This guide explains how to test and interact with the ASI:One uAgent locally.

## Prerequisites

1. **Running uAgent**: Make sure the uAgent is running with `python app.py`
2. **ASI API Key**: Set in `.env` file
3. **Dependencies**: All Python packages installed

## Test Scripts Available

### 1. Direct Test (Recommended)
```bash
python3 direct_test.py
```
- Uses uAgents protocol directly
- Most reliable method
- Interactive chat mode
- Predefined test messages

### 2. Simple HTTP Test
```bash
python3 simple_test.py
```
- Uses HTTP requests
- Tests connection first
- Interactive and predefined modes

### 3. Curl Test
```bash
./curl_test.sh
```
- Uses curl commands
- Simple and direct
- Good for quick tests

### 4. Full Test Client
```bash
python3 test_client.py
```
- Comprehensive testing
- Multiple interaction modes
- Advanced features

## Quick Start

1. **Start the uAgent**:
   ```bash
   python3 app.py
   ```

2. **In another terminal, run a test**:
   ```bash
   python3 direct_test.py
   ```

3. **Choose option 1 for interactive chat**

4. **Type your message and see the response in the uAgent logs**

## Expected Behavior

### uAgent Logs
When you send a message, you should see:
```
INFO: [ASI-One-Agent]: Received message from test-client
INFO: [ASI-One-Agent]: Successfully processed message from test-client
```

### Test Client
You should see:
```
📤 Sending: Hello! What is ASI:One?
✅ Message sent successfully!
💡 Check the uAgent logs for the response
```

## Test Messages

Try these sample messages:
- "Hello! What is ASI:One?"
- "How do I build an AI agent?"
- "What are the key features of ASI:One?"
- "Can you explain agentic AI?"
- "How do I deploy an agent on Agentverse?"

## Troubleshooting

### Common Issues

1. **"Cannot connect to agent"**
   - Make sure uAgent is running on port 8001
   - Check if port is available

2. **"Message send failed"**
   - Verify agent address is correct
   - Check uAgent logs for errors

3. **"No response from agent"**
   - Check ASI API key in `.env`
   - Verify internet connection
   - Check uAgent logs for API errors

### Debug Steps

1. **Check uAgent status**:
   ```bash
   curl http://127.0.0.1:8001/health
   ```

2. **Check agent logs** for errors

3. **Verify environment**:
   ```bash
   python3 deploy.py
   ```

## Agent Inspector

For advanced testing, use the Agent Inspector:
```
https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8001&address=agent1qdfnj0vck9d33a8gvsy7uhsz904h66spy45nz2prvpwdn6f8tlf92gzlqzz
```

## Next Steps

1. **Test locally** with the scripts above
2. **Deploy to Render** when ready
3. **Connect to Agentverse** for production testing
4. **Integrate with frontend** for full-stack testing

## Support

- Check uAgent logs for detailed error messages
- Verify ASI API key and credits
- Ensure all dependencies are installed
- Test with simple messages first
