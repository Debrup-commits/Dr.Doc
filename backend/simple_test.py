#!/usr/bin/env python3
"""
Simple test script to interact with the ASI:One uAgent
This script demonstrates how to send messages and receive responses
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from uuid import uuid4

# Configuration
AGENT_ADDRESS = "agent1qdfnj0vck9d33a8gvsy7uhsz904h66spy45nz2prvpwdn6f8tlf92gzlqzz"
AGENT_URL = "http://127.0.0.1:8001"

async def test_agent_connection():
    """
    Test if the agent is running and accessible
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{AGENT_URL}/health") as response:
                if response.status == 200:
                    print("✅ Agent is running and accessible")
                    return True
                else:
                    print(f"❌ Agent returned status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Cannot connect to agent: {e}")
        print("💡 Make sure the uAgent is running with: python app.py")
        return False

async def send_test_message(message: str):
    """
    Send a test message to the agent
    """
    print(f"\n📤 Sending message: '{message}'")
    
    # Create message payload
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "msg_id": str(uuid4()),
        "content": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AGENT_URL}/message",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Message sent successfully!")
                    print(f"📥 Response: {result}")
                    return result
                else:
                    print(f"❌ Failed to send message. Status: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return None

async def run_interactive_test():
    """
    Run an interactive test session
    """
    print("🤖 ASI:One uAgent Interactive Test")
    print("=" * 40)
    
    # Test connection first
    if not await test_agent_connection():
        return
    
    print("\n💬 Interactive chat mode")
    print("Type your messages (type 'quit' to exit)")
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
            
            await send_test_message(message)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def run_predefined_tests():
    """
    Run predefined test messages
    """
    print("🧪 Running predefined tests")
    print("=" * 30)
    
    # Test connection first
    if not await test_agent_connection():
        return
    
    test_messages = [
        "Hello! What is ASI:One?",
        "How do I build an AI agent?",
        "What are the key features of ASI:One?",
        "Can you explain agentic AI?",
        "How do I deploy an agent on Agentverse?",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}/{len(test_messages)}")
        await send_test_message(message)
        await asyncio.sleep(1)  # Wait between messages
    
    print("\n✅ All tests completed!")

def main():
    """
    Main function
    """
    print("🚀 ASI:One uAgent Test Client")
    print("=" * 40)
    print("1. Interactive chat")
    print("2. Run predefined tests")
    print("3. Test connection only")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect an option (1-4): ").strip()
            
            if choice == "1":
                asyncio.run(run_interactive_test())
                break
            elif choice == "2":
                asyncio.run(run_predefined_tests())
                break
            elif choice == "3":
                asyncio.run(test_agent_connection())
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
