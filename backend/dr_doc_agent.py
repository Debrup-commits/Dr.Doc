#!/usr/bin/env python3
"""
Dr.Doc uAgent

uAgent implementation using MCP server adapter for ASI:One integration.
This converts the MCP server into a uAgent that can be deployed on Agentverse.

Author: Dr.Doc Team
"""

import os
import logging
from dotenv import load_dotenv

# uAgent imports
from uagents import Agent

# Try to import the adapter, handle gracefully if not available
try:
    from uagents_adapter import MCPServerAdapter
    ADAPTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ uagents-adapter not available: {e}")
    print("   The uAgent will be created without MCP adapter integration")
    ADAPTER_AVAILABLE = False

# Local imports
from server import mcp, server
from rag_initializer import initialize_rag_system, auto_process_documents_if_needed, get_rag_system, get_metta_kb

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dr_doc_agent():
    """Create and configure the Dr.Doc uAgent"""
    
    # Get ASI:One API key
    asi1_api_key = os.getenv("ASI_ONE_API_KEY")
    if not asi1_api_key:
        raise ValueError("ASI_ONE_API_KEY not found in environment variables")
    
    print("🤖 Creating Dr.Doc uAgent...")
    logger.info("🤖 Creating Dr.Doc uAgent...")
    
    # Initialize RAG system for the agent
    print("🔄 Initializing RAG system for uAgent...")
    rag_system = initialize_rag_system()
    
    # Update the global RAG system in mcp_server
    import mcp_server
    mcp_server.rag_system = rag_system
    mcp_server.metta_kb = get_metta_kb()
    
    # Create the uAgent with proper configuration
    print("🚀 Creating uAgent...")
    agent = Agent(
        name="Dr.Doc Agent",
        seed="Dr.Doc Agent Seed for deterministic address generation",
        port=8000,
        endpoint=["http://127.0.0.1:8000/submit"]
    )
    
    print("✅ Agent configured for basic operation")
    
    # Add periodic heartbeat to keep agent active
    @agent.on_interval(period=30.0)
    async def heartbeat(ctx):
        """Send periodic heartbeat to keep agent active on Agentverse"""
        try:
            print("💓 Agent heartbeat - staying active on Agentverse")
            # You can add any periodic maintenance tasks here
        except Exception as e:
            print(f"❌ Heartbeat error: {e}")
    
    print("✅ Heartbeat configured for Agentverse activity")
    
    print("✅ Agent ready for Agentverse deployment")
    
    mcp_adapter = None
    
    if ADAPTER_AVAILABLE:
        # Create MCP adapter with the MCP server
        print("🔗 Creating MCP adapter...")
        try:
            mcp_adapter = MCPServerAdapter(
                mcp_server=mcp,                     # Our MCP server instance
                asi1_api_key=asi1_api_key,          # ASI:One API key
                model="asi1-mini"                   # Model to use
            )
            
            # Include protocols from the adapter
            print("📋 Including MCP protocols in uAgent...")
            for protocol in mcp_adapter.protocols:
                agent.include(protocol, publish_manifest=True)
                logger.info(f"Included protocol: {protocol}")
                
            print("✅ MCP adapter integrated successfully!")
            
        except Exception as e:
            print(f"⚠️ MCP adapter creation failed: {e}")
            print("   Creating uAgent without MCP adapter integration")
            mcp_adapter = None
    else:
        print("⚠️ Creating uAgent without MCP adapter integration")
    
    print("✅ Dr.Doc uAgent created successfully!")
    logger.info("✅ Dr.Doc uAgent created successfully!")
    
    return agent, mcp_adapter

def main():
    """Main function to run the Dr.Doc uAgent"""
    try:
        print("🚀 Starting Dr.Doc uAgent System")
        print("=" * 50)
        
        # Check environment
        asi1_api_key = os.getenv("ASI_ONE_API_KEY")
        if not asi1_api_key:
            print("❌ ASI_ONE_API_KEY not found in environment variables")
            print("   Please set ASI_ONE_API_KEY in your .env file")
            return 1
        
        print("✅ ASI:One API key found")
        
        # Create agent and adapter
        agent, mcp_adapter = create_dr_doc_agent()
        
        print("\n🎯 Dr.Doc uAgent Configuration:")
        print(f"   📍 Agent Name: {agent.name}")
        print(f"   🔑 Agent Address: {agent.address}")
        print(f"   🌐 Endpoint: http://127.0.0.1:8000/submit")
        print(f"   🤖 Model: asi1-mini")
        if mcp_adapter:
            print(f"   📋 Protocols: {len(mcp_adapter.protocols)} included")
        else:
            print(f"   📋 Protocols: MCP adapter not available")
        
        print("\n🚀 Starting uAgent...")
        print("📍 Agent will be available on Agentverse")
        print("🌐 Agent Inspector will be available")
        print("🛑 Press Ctrl+C to stop")
        
        if mcp_adapter:
            # Run the MCP adapter with the agent
            mcp_adapter.run(agent)
        else:
            # Run the agent directly without adapter
            print("⚠️ Running agent without MCP adapter")
            agent.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Dr.Doc uAgent stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Dr.Doc uAgent failed: {e}")
        logger.error(f"Dr.Doc uAgent failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
