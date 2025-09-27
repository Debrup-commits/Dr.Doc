#!/usr/bin/env python3
"""
Direct test script to interact with the ASI:One uAgent
This script uses the uAgents protocol to send messages directly
"""

import asyncio
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
    port=8003,  # Different port to avoid conflict
)

async def send_message(message: str):
    """
    Send a message to the ASI:One uAgent
    """
    print(f"\n📤 Sending: {message}")
    
    # Create the message
    chat_message = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=message)]
    )
    
    try:
        # Send message to the agent using the correct method
        await test_client._ctx.send(AGENT_ADDRESS, chat_message)
        print("✅ Message sent successfully!")
        print("💡 Check the uAgent logs for the response")
        return True
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

async def interactive_chat():
    """
    Interactive chat with the uAgent
    """
    print("🤖 ASI:One uAgent Direct Test")
    print("=" * 40)
    print(f"🎯 Target Agent: {AGENT_ADDRESS}")
    print("💬 Type your messages (type 'quit' to exit)")
    print("=" * 40)
    
    while True:
        try:
            message = input("\n👤 You: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not message:
                print("⚠️  Please enter a message")
                continue
            
            await send_message(message)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def run_tests():
    """
    Run predefined test messages
    """
    print("🧪 Running predefined tests")
    print("=" * 30)
    
    test_messages = [
        "Hello! What is ASI:One?",
        "How do I build an AI agent?",
        "What are the key features of ASI:One?",
        "Can you explain agentic AI?",
        "How do I deploy an agent on Agentverse?",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}/{len(test_messages)}")
        await send_message(message)
        await asyncio.sleep(2)  # Wait between messages
    
    print("\n✅ All tests completed!")

def main():
    """
    Main function
    """
    print("🚀 ASI:One uAgent Direct Test Client")
    print("=" * 40)
    print("1. Interactive chat")
    print("2. Run predefined tests")
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
                asyncio.run(run_tests())
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
