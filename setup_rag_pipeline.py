#!/usr/bin/env python3
"""
RAG Pipeline Setup Script
Sets up the complete RAG pipeline with BGE embeddings and Fetch.ai ASI:One
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    # Create .env file from example
    env_file = Path(".env")
    example_file = Path("env-fetchai-only.example")
    
    if not env_file.exists() and example_file.exists():
        print("📝 Creating .env file from example...")
        with open(example_file, 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual API key if available
        if "ASI_ONE_API_KEY" in os.environ:
            content = content.replace("your_asi_one_api_key_here", os.environ["ASI_ONE_API_KEY"])
        
        with open(env_file, 'w') as f:
            f.write(content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is configured
    api_key = os.getenv("ASI_ONE_API_KEY", "")
    if not api_key or api_key.startswith("your_"):
        print("⚠️  ASI_ONE_API_KEY not configured or using placeholder")
        print("💡 Please set your Fetch.ai ASI:One API key in the .env file")
        return False
    
    print("✅ Environment configured")
    return True

def start_database():
    """Start the PostgreSQL database with pgvector"""
    print("🗄️  Starting PostgreSQL database with pgvector...")
    
    try:
        # Check if docker-compose is available
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ docker-compose not found. Please install Docker Compose")
            return False
        
        # Start the database
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database started successfully")
            
            # Wait for database to be ready
            print("⏳ Waiting for database to be ready...")
            time.sleep(10)
            
            return True
        else:
            print(f"❌ Failed to start database: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting database: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port="5532",
            database="ai",
            user="ai",
            password="ai"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection successful: {version}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure PostgreSQL is running on port 5532")
        return False

def run_ingestion():
    """Run document ingestion using the Agno RAG system"""
    print("📚 Running document ingestion...")
    
    try:
        # Import and run the Agno RAG system
        sys.path.append('backend')
        from fetchai_agno_rag import FetchAIAgnoRAG
        
        # Initialize RAG system
        print("🔄 Initializing Agno RAG system...")
        rag = FetchAIAgnoRAG(use_fetchai=True, require_openai_fallback=False)
        
        # Ingest documents
        print("📄 Ingesting documents from docs/ directory...")
        rag.ingest_documents("../docs")
        
        # Test the system
        print("🧪 Testing the RAG system...")
        result = rag.query("What is ASI:One?")
        
        if result and 'answer' in result:
            print("✅ RAG system working correctly")
            print(f"📝 Sample answer: {result['answer'][:100]}...")
            return True
        else:
            print("❌ RAG system test failed")
            return False
            
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return False

def run_metta_ingestion():
    """Run MeTTa fact extraction"""
    print("🧠 Running MeTTa fact extraction...")
    
    try:
        sys.path.append('backend')
        from metta_ingest import main as metta_main
        
        # Run MeTTa ingestion
        metta_main()
        print("✅ MeTTa fact extraction completed")
        return True
        
    except Exception as e:
        print(f"⚠️  MeTTa ingestion failed: {e}")
        print("💡 MeTTa is optional - continuing without it")
        return False

def start_services():
    """Start the main services"""
    print("🚀 Starting services...")
    
    services = [
        {
            'name': 'Main Hybrid System',
            'command': ['python3', 'backend/app_agno_hybrid.py'],
            'port': 5003
        },
        {
            'name': 'Agent API Adapter',
            'command': ['python3', 'backend/agent_api_adapter.py'],
            'port': 5001
        },
        {
            'name': 'Document Q&A Agent',
            'command': ['python3', 'backend/doc_qa_agent.py'],
            'port': 8001
        }
    ]
    
    processes = []
    
    for service in services:
        print(f"🔄 Starting {service['name']}...")
        try:
            process = subprocess.Popen(
                service['command'],
                cwd=Path.cwd()
            )
            processes.append((service['name'], process))
            print(f"✅ {service['name']} started (PID: {process.pid})")
            
            # Wait a bit between starting services
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")
    
    return processes

def main():
    """Main setup function"""
    print("🚀 Setting up RAG Pipeline with BGE Embeddings and Fetch.ai ASI:One")
    print("=" * 70)
    
    # Step 1: Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return False
    
    # Step 2: Start database
    if not start_database():
        print("❌ Database setup failed")
        return False
    
    # Step 3: Test database connection
    if not test_database_connection():
        print("❌ Database connection test failed")
        return False
    
    # Step 4: Run document ingestion
    if not run_ingestion():
        print("❌ Document ingestion failed")
        return False
    
    # Step 5: Run MeTTa ingestion (optional)
    run_metta_ingestion()
    
    # Step 6: Start services
    processes = start_services()
    
    print("\n🎉 RAG Pipeline Setup Complete!")
    print("=" * 70)
    print("📍 Services running:")
    print("  • Main Hybrid System: http://localhost:5003")
    print("  • Agent API Adapter: http://localhost:5001")
    print("  • Document Q&A Agent: http://localhost:8001")
    print("\n💡 Test the system by visiting: http://localhost:5003")
    print("🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for name, process in processes:
            print(f"🛑 Stopping {name}...")
            process.terminate()
            process.wait()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()

