#!/usr/bin/env python3
"""
Dr.Doc uAgent
MCP server wrapped as a uAgent for Agentverse integration
"""

import os
import logging
from dotenv import load_dotenv

# uAgents imports
from uagents import Agent

# MCP adapter imports
from uagents_adapter import MCPServerAdapter

# Import our MCP server
from mcp_server import mcp

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dr_doc_agent():
    """Create the Dr.Doc uAgent with MCP server integration"""
    
    # Get ASI:One API key
    asi1_api_key = os.getenv("ASI_ONE_API_KEY")
    if not asi1_api_key:
        logger.error("❌ ASI_ONE_API_KEY environment variable not set")
        raise ValueError("ASI_ONE_API_KEY environment variable not set")
    
    # Create MCP adapter with your MCP server
    logger.info("🔧 Creating MCP Server Adapter...")
    mcp_adapter = MCPServerAdapter(
        mcp_server=mcp,                     # Your MCP server instance
        asi1_api_key=asi1_api_key,          # Your ASI:One API key
        model="asi1-mini"                   # Model to use
    )
    
    # Create a uAgent
    logger.info("🤖 Creating Dr.Doc uAgent...")
    agent = Agent(
        name="dr_doc_agent",
        seed=os.getenv("AGENTVERSE_API_KEY", "dr-doc-agent-seed"),
        port=8002,
        mailbox=True
    )
    
    # Include protocols from the adapter
    logger.info("📋 Including MCP protocols in uAgent...")
    for protocol in mcp_adapter.protocols:
        agent.include(protocol, publish_manifest=True)
    
    logger.info("✅ Dr.Doc uAgent created successfully")
    return agent, mcp_adapter

def main():
    """Main function to run the Dr.Doc uAgent"""
    try:
        logger.info("🚀 Starting Dr.Doc uAgent with MCP Server...")
        
        # Create agent and adapter
        agent, mcp_adapter = create_dr_doc_agent()
        
        logger.info("📍 Dr.Doc uAgent Address: " + agent.address)
        logger.info("🌐 Agent Inspector: https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8002&address=" + agent.address)
        logger.info("📋 Available MCP Tools:")
        logger.info("   1. process_documents(docs_dir_path) - Initialize system with documents")
        logger.info("   2. ask_dr_doc(question, session_id) - Ask questions about documents")
        
        # Run the MCP adapter with the agent
        logger.info("🎯 Starting agent...")
        mcp_adapter.run(agent)
        
    except Exception as e:
        logger.error(f"❌ Failed to start Dr.Doc uAgent: {e}")
        raise e

if __name__ == "__main__":
    main()

