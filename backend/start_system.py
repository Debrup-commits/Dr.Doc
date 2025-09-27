#!/usr/bin/env python3
"""
Clean Dr.Doc System Startup
Minimal system with MCP server and HTTP API wrapper
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment configuration...")
    
    # Check ASI:One API key
    asi1_key = os.getenv("ASI_ONE_API_KEY")
    if asi1_key:
        print("  ✅ ASI_ONE_API_KEY is set")
    else:
        print("  ⚠️ ASI_ONE_API_KEY is not set")
        print("     Set it in .env file or environment variable")
    
    # Check docs directory
    docs_dir = Path("../docs")
    if docs_dir.exists():
        print(f"  ✅ Docs directory found: {docs_dir}")
        doc_count = len(list(docs_dir.glob("*")))
        print(f"     Contains {doc_count} files")
    else:
        print(f"  ⚠️ Docs directory not found: {docs_dir}")
        print("     Create it and add your documents for processing")
    
    return True

def run_mcp_server():
    """Run the MCP server in standalone mode"""
    print("\n🚀 Starting Clean MCP Server...")
    print("📍 Server will be available via stdio transport")
    print("📋 Available tools:")
    print("   1. process_documents(docs_dir_path) - Idempotent document processing")
    print("   2. ask_dr_doc(question, session_id) - ASI:One agent for document Q&A")
    
    try:
        from mcp_server import mcp
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n🛑 MCP Server stopped by user")
    except Exception as e:
        print(f"\n❌ MCP Server failed: {e}")

def run_api_wrapper():
    """Run the HTTP API wrapper"""
    print("\n🌐 Starting MCP API Wrapper...")
    print("📍 API will be available at: http://localhost:5003")
    print("📋 Available endpoints:")
    print("   POST /api/process-documents - Process documents (idempotent)")
    print("   POST /api/ask - Ask questions to Dr.Doc agent")
    print("   GET /api/status - Get system status")
    print("   GET /api/health - Health check")
    
    try:
        from api_wrapper import app
        app.run(host='0.0.0.0', port=5003, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 API Wrapper stopped by user")
    except Exception as e:
        print(f"\n❌ API Wrapper failed: {e}")

def run_uagent():
    """Run the uAgent with MCP integration"""
    print("\n🤖 Starting Dr.Doc uAgent...")
    print("📍 Agent will be available on Agentverse")
    print("🌐 Agent Inspector will be available")
    
    try:
        from dr_doc_agent import main as uagent_main
        uagent_main()
    except KeyboardInterrupt:
        print("\n🛑 Dr.Doc uAgent stopped by user")
    except Exception as e:
        print(f"\n❌ Dr.Doc uAgent failed: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Dr.Doc System")
    parser.add_argument(
        "mode", 
        choices=["mcp", "api", "uagent"], 
        help="Mode to run: 'mcp' (standalone MCP server), 'api' (HTTP API wrapper), or 'uagent' (uAgent with MCP)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Clean Dr.Doc System")
    print("=" * 40)
    
    # Run environment checks
    check_environment()
    
    # Run in requested mode
    if args.mode == "mcp":
        run_mcp_server()
    elif args.mode == "api":
        run_api_wrapper()
    elif args.mode == "uagent":
        run_uagent()

if __name__ == "__main__":
    main()
