#!/usr/bin/env python3
"""
Startup script for the Dr.Doc MCP-based system
Provides options to run the MCP server standalone or as a uAgent
"""

import os
import sys
import argparse
import asyncio
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "mcp",
        "fastmcp", 
        "openai",
        "hyperon"
    ]
    
    optional_packages = [
        "uagents_adapter"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Missing")
            missing_packages.append(package)
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ⚠️ {package} - Missing (optional)")
    
    if missing_packages:
        print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required dependencies are installed")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
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

def run_mcp_server_standalone():
    """Run the MCP server in standalone mode"""
    print("\n🚀 Starting MCP Server in standalone mode...")
    print("📍 Server will be available via stdio transport")
    print("📋 Available tools:")
    print("   1. process_documents(docs_dir_path)")
    print("   2. ask_dr_doc(question, session_id)")
    print("   3. get_system_status()")
    
    try:
        from mcp_server import mcp
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("\n🛑 MCP Server stopped by user")
    except Exception as e:
        print(f"\n❌ MCP Server failed: {e}")

def run_mcp_agent():
    """Run the MCP server as a uAgent"""
    print("\n🤖 Starting Dr.Doc uAgent with MCP Server...")
    print("📍 Agent will be available on Agentverse")
    print("🌐 Agent Inspector will be available")
    
    try:
        # Check if uagents_adapter is available
        try:
            import uagents_adapter
            from dr_doc_agent import main
            main()
        except ImportError:
            print("❌ uagents_adapter not available. Cannot run as uAgent.")
            print("💡 Run in 'server' mode instead for standalone MCP server")
            print("   Or install missing dependencies: pip install uagents_adapter")
    except KeyboardInterrupt:
        print("\n🛑 Dr.Doc uAgent stopped by user")
    except Exception as e:
        print(f"\n❌ Dr.Doc uAgent failed: {e}")

def test_mcp_system():
    """Test the MCP system"""
    print("\n🧪 Testing MCP system...")
    
    try:
        from test_mcp_server import test_mcp_tools, test_mcp_server
        test_mcp_tools()
        asyncio.run(test_mcp_server())
        print("✅ MCP system test completed successfully")
    except Exception as e:
        print(f"❌ MCP system test failed: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Dr.Doc MCP System Startup")
    parser.add_argument(
        "mode", 
        choices=["server", "agent", "test"], 
        help="Mode to run: 'server' (standalone MCP), 'agent' (uAgent), or 'test'"
    )
    parser.add_argument(
        "--skip-checks", 
        action="store_true", 
        help="Skip dependency and environment checks"
    )
    
    args = parser.parse_args()
    
    print("🚀 Dr.Doc MCP System")
    print("=" * 50)
    
    # Run checks unless skipped
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)
        check_environment()
    
    # Run in requested mode
    if args.mode == "server":
        run_mcp_server_standalone()
    elif args.mode == "agent":
        run_mcp_agent()
    elif args.mode == "test":
        test_mcp_system()

if __name__ == "__main__":
    main()
