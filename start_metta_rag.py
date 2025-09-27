#!/usr/bin/env python3
"""
Startup script for Metta+RAG Agent System
Simplified startup for the ethNewDelhi2025 project
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import uagents
        import agno
        import flask
        import sentence_transformers
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment configuration"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy .env.example to .env and configure your API keys")
        return False
    
    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["ASI_ONE_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or placeholder environment variables: {missing_vars}")
        print("Please update your .env file with valid API keys")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def start_system():
    """Start the Metta+RAG agent system"""
    print("🚀 Starting Metta+RAG Agent System...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check environment
    if not check_environment():
        return False
    
    # Start the agentic system
    try:
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return False
        
        print("🤖 Starting agentic system...")
        process = subprocess.Popen([
            sys.executable, "start_agentic_system.py"
        ], cwd=backend_dir)
        
        print("✅ System started successfully!")
        print("📍 API available at: http://localhost:5003")
        print("🤖 Agent running on port: 8001")
        print("🛑 Press Ctrl+C to stop the system")
        print("=" * 50)
        
        # Wait for the process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping system...")
            process.terminate()
            process.wait()
            print("✅ System stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start system: {e}")
        return False

def main():
    """Main function"""
    print("Metta+RAG Agent System Startup")
    print("=" * 50)
    
    if start_system():
        print("🎉 System completed successfully")
    else:
        print("❌ System failed to start")
        sys.exit(1)

if __name__ == "__main__":
    main()

