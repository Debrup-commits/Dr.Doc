#!/usr/bin/env python3
"""
Deployment helper script for ASI:One uAgent
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("📝 Please copy env.example to .env and fill in your ASI_API_KEY")
        return False
    
    # Check if ASI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("ASI_API_KEY"):
        print("❌ ASI_API_KEY not set in .env file!")
        return False
    
    print("✅ Requirements check passed!")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def test_agent():
    """Test the agent locally"""
    print("🧪 Testing agent...")
    try:
        # Import and test basic functionality
        from app import agent, client
        
        print(f"✅ Agent created: {agent.name}")
        print(f"✅ Agent address: {agent.address}")
        print(f"✅ ASI client initialized")
        print("✅ Agent test passed!")
        return True
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 ASI:One uAgent Deployment Helper")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test agent
    if not test_agent():
        sys.exit(1)
    
    print("\n🎉 All checks passed!")
    print("\n📋 Next steps:")
    print("1. Run locally: python app.py")
    print("2. Check the Agent Inspector link in the logs")
    print("3. Connect to Agentverse using the link")
    print("4. Deploy to Render when ready")
    
    print("\n🔗 Useful links:")
    print("- Agentverse: https://agentverse.ai")
    print("- Render: https://render.com")
    print("- ASI:One API: https://api.asi1.ai")

if __name__ == "__main__":
    main()
