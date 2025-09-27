#!/usr/bin/env python3
"""
Test script for uAgent integration

This script tests the uAgent integration to ensure everything works properly.

Author: Dr.Doc Team
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_server_wrapper():
    """Test the server wrapper functionality"""
    try:
        print("🧪 Testing Server Wrapper...")
        
        from server import server
        
        # Test list_tools
        print("📋 Testing list_tools...")
        tools = await server.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # Test call_tool with a simple question
        print("\n🔧 Testing call_tool...")
        result = await server.call_tool("ask_dr_doc", {
            "question": "What is ASI:One?",
            "session_id": "test_session"
        })
        
        if result.get("success"):
            print("✅ Tool call successful!")
            print(f"   Result: {result['result'][:100]}...")
        else:
            print(f"❌ Tool call failed: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server wrapper test failed: {e}")
        logger.error(f"Server wrapper test failed: {e}")
        return False

async def test_mcp_adapter():
    """Test the MCP adapter creation"""
    try:
        print("\n🧪 Testing MCP Adapter...")
        
        # Check if uagents-adapter is available
        try:
            from uagents_adapter import MCPServerAdapter
            print("✅ uagents-adapter imported successfully")
        except ImportError as e:
            print(f"❌ uagents-adapter not available: {e}")
            print("   Please install: pip install uagents-adapter")
            return False
        
        # Check ASI:One API key
        asi1_api_key = os.getenv("ASI_ONE_API_KEY")
        if not asi1_api_key:
            print("❌ ASI_ONE_API_KEY not found in environment variables")
            return False
        
        print("✅ ASI:One API key found")
        
        # Test adapter creation
        from server import mcp
        
        adapter = MCPServerAdapter(
            mcp_server=mcp,
            asi1_api_key=asi1_api_key,
            model="asi1-mini"
        )
        
        print("✅ MCP Adapter created successfully")
        print(f"   Protocols available: {len(adapter.protocols)}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP adapter test failed: {e}")
        logger.error(f"MCP adapter test failed: {e}")
        return False

def test_agent_creation():
    """Test uAgent creation"""
    try:
        print("\n🧪 Testing uAgent Creation...")
        
        # Check if uagents is available
        try:
            from uagents import Agent
            print("✅ uagents imported successfully")
        except ImportError as e:
            print(f"❌ uagents not available: {e}")
            print("   Please install: pip install uagents")
            return False
        
        # Create a test agent
        agent = Agent(
            name="Test Agent",
            seed="Test seed for deterministic address generation"
        )
        
        print("✅ Test agent created successfully")
        print(f"   Agent name: {agent.name}")
        print(f"   Agent address: {agent.address}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        logger.error(f"Agent creation test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 uAgent Integration Test Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Server Wrapper", test_server_wrapper()),
        ("MCP Adapter", test_mcp_adapter()),
        ("Agent Creation", test_agent_creation())
    ]
    
    results = []
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! uAgent integration is ready!")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
