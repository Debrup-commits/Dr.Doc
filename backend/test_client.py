#!/usr/bin/env python3
"""
Test client for ASI:One uAgent
This script allows you to send messages to the running uAgent and receive responses
"""

import asyncio
import json
from datetime import datetime
from uuid import uuid4
from uagents import Agent
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    TextContent,
    EndSessionContent,
)

# Agent address from the running uAgent
AGENT_ADDRESS = "agent1qdfnj0vck9d33a8gvsy7uhsz904h66spy45nz2prvpwdn6f8tlf92gzlqzz"

# Create a test client agent
test_client = Agent(
    name="test-client",
    seed="test-client-seed",
    port=8002,  # Different port to avoid conflict
)

async def send_message_to_agent(message: str):
    """
    Send a message to the ASI:One uAgent and wait for response
    """
    print(f"\n📤 Sending message: {message}")
    print("⏳ Waiting for response...")
    
    # Create the message
    chat_message = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=message)]
    )
    
    # Send message to the agent
    await test_client.send(AGENT_ADDRESS, chat_message)
    
    # Wait for response (this is a simplified approach)
    # In a real implementation, you'd need to handle the response properly
    print("✅ Message sent successfully!")
    print("💡 Check the uAgent logs for the response")

async def interactive_chat():
    """
    Interactive chat interface with the uAgent
    """
    print("🤖 ASI:One uAgent Test Client")
    print("=" * 40)
    print(f"🎯 Target Agent: {AGENT_ADDRESS}")
    print("💬 Type your messages (type 'quit' to exit)")
    print("=" * 40)
    
    while True:
        try:
            # Get user input
            message = input("\n👤 You: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not message:
                print("⚠️  Please enter a message")
                continue
            
            # Send message to agent
            await send_message_to_agent(message)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_predefined_messages():
    """
    Test the agent with predefined messages
    """
    test_messages = [
        "Hello! Can you help me understand what ASI:One is?",
        "How do I build an AI agent?",
        "What are the key features of ASI:One?",
        "Can you explain agentic AI?",
        "How do I deploy an agent on Agentverse?",
    ]
    
    print("🧪 Testing uAgent with predefined messages")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}/{len(test_messages)}")
        await send_message_to_agent(message)
        
        # Wait a bit between messages
        await asyncio.sleep(2)
    
    print("\n✅ All test messages sent!")

def main():
    """
    Main function to run the test client
    """
    print("🚀 ASI:One uAgent Test Client")
    print("=" * 40)
    print("1. Interactive chat")
    print("2. Test predefined messages")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nSelect an option (1-3): ").strip()
            
            if choice == "1":
                print("\n🔄 Starting interactive chat...")
                print("⚠️  Make sure the uAgent is running on port 8001")
                asyncio.run(interactive_chat())
                break
                
            elif choice == "2":
                print("\n🔄 Running predefined tests...")
                print("⚠️  Make sure the uAgent is running on port 8001")
                asyncio.run(test_predefined_messages())
                break
                
            elif choice == "3":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
