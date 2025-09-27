#!/bin/bash

# Simple curl test script for ASI:One uAgent
# Make sure the uAgent is running on port 8001

echo "🤖 ASI:One uAgent Curl Test"
echo "=========================="
echo "Target: http://127.0.0.1:8001"
echo ""

# Test 1: Health check
echo "📋 Test 1: Health check"
curl -s http://127.0.0.1:8001/health || echo "❌ Health check failed"
echo ""

# Test 2: Send a simple message
echo "📋 Test 2: Send message"
curl -X POST http://127.0.0.1:8001/message \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "msg_id": "'$(uuidgen)'",
    "content": [
      {
        "type": "text",
        "text": "Hello! What is ASI:One?"
      }
    ]
  }' || echo "❌ Message send failed"
echo ""

# Test 3: Interactive mode
echo "📋 Test 3: Interactive mode"
echo "Type your message (or 'quit' to exit):"
while true; do
    read -p "👤 You: " message
    if [ "$message" = "quit" ] || [ "$message" = "exit" ]; then
        echo "👋 Goodbye!"
        break
    fi
    
    if [ -n "$message" ]; then
        echo "📤 Sending: $message"
        curl -X POST http://127.0.0.1:8001/message \
          -H "Content-Type: application/json" \
          -d "{
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",
            \"msg_id\": \"$(uuidgen)\",
            \"content\": [
              {
                \"type\": \"text\",
                \"text\": \"$message\"
              }
            ]
          }"
        echo ""
    fi
done
