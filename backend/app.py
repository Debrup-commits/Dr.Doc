"""
ASI:One uAgent - A Fetch.ai uAgent that integrates with ASI:One API
Deployable on Agentverse via Render
"""

from datetime import datetime
from uuid import uuid4
import os
from dotenv import load_dotenv
from openai import OpenAI
from uagents import Context, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Load environment variables
load_dotenv()

# Initialize ASI:One client
client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key=os.getenv("ASI_API_KEY"),  
)

# Create the agent
agent = Agent(
    name=os.getenv("AGENT_NAME", "ASI-One-Agent"),
    seed=os.getenv("AGENT_SEED", "asi-one-agent-seed"),
    port=int(os.getenv("AGENT_PORT", "8001")),
    mailbox=True,
)

# Create the chat protocol
protocol = Protocol(spec=chat_protocol_spec)

@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle incoming chat messages and respond using ASI:One API
    """
    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    
    # Extract text content from message
    text = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text

    # Default response
    response = "Sorry, I wasn't able to process that request."
    
    try:
        # Query ASI:One API
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are ASI:One, an advanced AI assistant specialized in agentic AI and multi-agent systems. You help users build, deploy, and manage AI agents. Be helpful, clear, and provide practical guidance for agent development and ASI:One platform usage."
                },
                {
                    "role": "user", 
                    "content": text
                },
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        response = str(r.choices[0].message.content)
        
        # Log successful response
        ctx.logger.info(f"Successfully processed message from {sender}")
        
    except Exception as e:
        ctx.logger.exception(f"Error querying ASI:One API: {e}")
        response = "I'm experiencing technical difficulties. Please try again later."

    # Send response back to sender
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
    """
    Handle chat acknowledgements
    """
    ctx.logger.info(f"Received acknowledgement from {sender}")

# Include the protocol in the agent
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    print(f"Starting {agent.name}...")
    print(f"Agent address: {agent.address}")
    print("Mailbox enabled: True")
    print("Connecting to ASI:One API...")
    
    # Verify API key is set
    if not os.getenv("ASI_API_KEY"):
        print("WARNING: ASI_API_KEY not set in environment variables!")
        print("Please set your ASI API key in the .env file or environment variables.")
    else:
        print("✅ ASI API key found")
    
    print("\n🚀 Starting agent...")
    print("📡 Agent will be available via Agentverse mailbox")
    print("🔗 Check logs for Agent Inspector link")
    
    agent.run()
