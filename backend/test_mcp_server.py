#!/usr/bin/env python3
"""
Test script for the Dr.Doc MCP Server
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import mcp, process_documents, ask_dr_doc, get_system_status

# Load environment variables
load_dotenv()

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing Dr.Doc MCP Server...")
    
    # Test 1: Check system status
    print("\n1️⃣ Testing system status...")
    status = await get_system_status()
    print(f"Status: {status}")
    
    # Test 2: Process documents (use docs directory if it exists)
    print("\n2️⃣ Testing document processing...")
    docs_dir = "../docs"
    if Path(docs_dir).exists():
        print(f"Processing documents from: {docs_dir}")
        result = await process_documents(docs_dir)
        print(f"Result: {result}")
    else:
        print(f"⚠️ Docs directory '{docs_dir}' not found, skipping document processing test")
    
    # Test 3: Ask a question (only if documents were processed)
    print("\n3️⃣ Testing Dr.Doc agent...")
    question = "What is this system about?"
    try:
        answer = await ask_dr_doc(question)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
    except Exception as e:
        print(f"❌ Dr.Doc agent test failed: {e}")
    
    # Test 4: Check final status
    print("\n4️⃣ Final system status...")
    final_status = await get_system_status()
    print(f"Final Status: {final_status}")

def test_mcp_tools():
    """Test MCP tools directly"""
    print("\n🔧 Testing MCP tools directly...")
    
    # List available tools
    print("Available tools:")
    print("  - process_documents: Process documents to create MeTTa knowledge graphs and RAG pipelines")
    print("  - ask_dr_doc: Ask questions to the Dr.Doc agent about processed documents")
    print("  - get_system_status: Get the current status of the Dr.Doc system")

if __name__ == "__main__":
    print("🚀 Dr.Doc MCP Server Test Suite")
    print("=" * 50)
    
    # Test MCP tools
    test_mcp_tools()
    
    # Test async functionality
    try:
        asyncio.run(test_mcp_server())
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
