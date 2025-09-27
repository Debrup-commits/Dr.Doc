#!/usr/bin/env python3
"""
Startup script for ethNewDelhi2025 Metta+RAG system
This script sets up and starts the complete system with document ingestion
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_docker():
    """Check if Docker is running and PostgreSQL container is up"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'ethNewDelhi2025-pgvector' in result.stdout:
            print("✅ PostgreSQL container is running")
            return True
        else:
            print("⚠️  PostgreSQL container not found")
            return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker first.")
        return False

def start_database():
    """Start PostgreSQL database with PgVector"""
    print("🔄 Starting PostgreSQL database...")
    try:
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print("✅ Database started successfully")
        time.sleep(5)  # Wait for database to be ready
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start database: {e}")
        return False

def check_env_file():
    """Check if .env file exists and is configured"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("💡 Please copy one of the example files:")
        print("   cp env-fetchai-only.example .env")
        print("   # Then edit .env with your API keys")
        return False
    
    # Check if API key is configured
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_asi_one_api_key_here' in content:
            print("⚠️  Please configure your ASI_ONE_API_KEY in .env file")
            return False
    
    print("✅ Environment file configured")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("🔄 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-agno-minimal.txt'], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def ingest_documents():
    """Ingest documents into the knowledge base"""
    print("🔄 Ingesting documents...")
    try:
        # Check if docs directory exists
        docs_dir = Path('docs')
        if not docs_dir.exists():
            print("⚠️  docs directory not found")
            print("💡 Please create docs directory and add your documentation files")
            return False
        
        # Check if there are markdown files
        md_files = list(docs_dir.glob('*.md'))
        if not md_files:
            print("⚠️  No markdown files found in docs directory")
            print("💡 Please add .md documentation files")
            return False
        
        print(f"📄 Found {len(md_files)} markdown files")
        
        # Run MeTTa ingestion if enabled
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if 'ENABLE_METTA=true' in content:
                    print("🧠 Running MeTTa fact extraction...")
                    subprocess.run([sys.executable, 'backend/metta_ingest.py'], check=True)
                    print("✅ MeTTa facts extracted")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to ingest documents: {e}")
        return False

def start_server():
    """Start the main server"""
    print("🚀 Starting ethNewDelhi2025 Metta+RAG server...")
    try:
        subprocess.run([sys.executable, 'backend/app_agno_hybrid.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True

def test_system():
    """Test the system components"""
    print("🧪 Testing system components...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'test_agent_system.py', '--quick'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ System test passed")
            return True
        else:
            print("⚠️  System test failed, but continuing...")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"⚠️  Could not run system test: {e}")
        return False

def main():
    """Main startup sequence"""
    print("🚀 Starting ethNewDelhi2025 Metta+RAG System")
    print("=" * 50)
    
    # Step 1: Check environment
    if not check_env_file():
        return False
    
    # Step 2: Install dependencies
    if not install_dependencies():
        return False
    
    # Step 3: Check/start database
    if not check_docker():
        if not start_database():
            return False
    else:
        print("✅ Database is already running")
    
    # Step 4: Test system components
    if not test_system():
        print("⚠️  System test failed, but continuing...")
    
    # Step 5: Ingest documents
    if not ingest_documents():
        print("⚠️  Document ingestion failed, but continuing...")
    
    # Step 6: Start server
    print("\n🎉 System ready! Starting server...")
    print("📱 Open your browser to http://localhost:5003")
    print("🤖 Agent API available at http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    return start_server()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Startup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ System shutdown complete.")