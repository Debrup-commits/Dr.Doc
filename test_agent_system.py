#!/usr/bin/env python3
"""
Comprehensive Test Script for Agent RAG/MeTTa System
Tests all components and integration points
"""

import os
import sys
import time
import requests
import asyncio
from typing import List, Dict, Any
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from backend.agent_rag_interface import get_agent_interface, QueryType
        print("✅ Agent RAG Interface imported")
    except Exception as e:
        print(f"❌ Agent RAG Interface import failed: {e}")
        return False
    
    try:
        from backend.fetchai_agno_rag import FetchAIAgnoRAG
        print("✅ FetchAI Agno RAG imported")
    except Exception as e:
        print(f"❌ FetchAI Agno RAG import failed: {e}")
        return False
    
    try:
        from backend.metta_ingest import MeTTaKnowledgeBase
        print("✅ MeTTa Knowledge Base imported")
    except Exception as e:
        print(f"⚠️  MeTTa import failed (optional): {e}")
    
    try:
        from backend.bge_embedder import BGEEmbedder
        print("✅ BGE Embedder imported")
    except Exception as e:
        print(f"❌ BGE Embedder import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🧪 Testing environment...")
    
    # Check for .env file
    if not Path('.env').exists():
        print("⚠️  .env file not found")
        print("💡 Please copy env-fetchai-only.example to .env and configure")
        return False
    
    # Check API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    fetchai_key = os.getenv("ASI_ONE_API_KEY", "")
    if not fetchai_key or fetchai_key.startswith("your_"):
        print("⚠️  ASI_ONE_API_KEY not configured")
        print("💡 Please set your Fetch.ai API key in .env")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def test_database():
    """Test database connection"""
    print("\n🧪 Testing database...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5532",
            database="ai",
            user="ai",
            password="ai"
        )
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Please start the database: docker-compose up -d")
        return False

def test_bge_embedder():
    """Test BGE embedder"""
    print("\n🧪 Testing BGE Embedder...")
    
    try:
        from backend.bge_embedder import BGEEmbedder
        
        embedder = BGEEmbedder()
        
        # Test document embeddings
        test_docs = [
            "This is a test document about authentication.",
            "Rate limits are important for API security."
        ]
        
        doc_embeddings = embedder.embed_documents(test_docs)
        print(f"✅ Document embeddings: {len(doc_embeddings)} x {len(doc_embeddings[0])}")
        
        # Test query embedding
        query_embedding = embedder.embed_query("How do I authenticate?")
        print(f"✅ Query embedding: {len(query_embedding)} dimensions")
        
        return True
    except Exception as e:
        print(f"❌ BGE Embedder test failed: {e}")
        return False

def test_metta_system():
    """Test MeTTa system"""
    print("\n🧪 Testing MeTTa System...")
    
    try:
        from backend.metta_ingest import MeTTaKnowledgeBase
        
        # Check if atoms file exists
        if not Path("api_facts.metta").exists():
            print("⚠️  api_facts.metta not found")
            print("💡 Run: python backend/metta_ingest.py")
            return False
        
        # Load knowledge base
        kb = MeTTaKnowledgeBase()
        kb.load_atoms_from_file("api_facts.metta")
        
        print(f"✅ MeTTa knowledge base loaded: {len(kb.atoms)} atoms")
        
        # Test queries
        endpoints = kb.query_endpoints()
        print(f"✅ Found {len(endpoints)} endpoints")
        
        error_codes = kb.query_error_codes()
        print(f"✅ Found {len(error_codes)} error codes")
        
        return True
    except Exception as e:
        print(f"❌ MeTTa system test failed: {e}")
        return False

def test_agno_rag():
    """Test Agno RAG system"""
    print("\n🧪 Testing Agno RAG System...")
    
    try:
        from backend.fetchai_agno_rag import FetchAIAgnoRAG
        
        # Initialize with lazy loading
        rag = FetchAIAgnoRAG(use_fetchai=True, require_openai_fallback=True, lazy_init=True)
        
        print("✅ Agno RAG system initialized")
        
        # Test knowledge base loading
        knowledge_loaded = rag.load_knowledge()
        if knowledge_loaded:
            print("✅ Knowledge base loaded")
        else:
            print("⚠️  Knowledge base not loaded (may need document ingestion)")
        
        return True
    except Exception as e:
        print(f"❌ Agno RAG test failed: {e}")
        return False

def test_agent_interface():
    """Test agent interface"""
    print("\n🧪 Testing Agent Interface...")
    
    try:
        from backend.agent_rag_interface import get_agent_interface, QueryType
        
        interface = get_agent_interface()
        
        # Test system status
        status = interface.get_system_status()
        print(f"✅ System status: {status}")
        
        # Test queries
        test_questions = [
            "What OAuth flows are supported?",
            "What are the rate limits?",
            "How do I authenticate with the API?"
        ]
        
        for question in test_questions:
            print(f"🔍 Testing: {question}")
            result = interface.query(question, QueryType.AUTO)
            print(f"  Answer: {result.answer[:100]}...")
            print(f"  Type: {result.query_type.value}, Confidence: {result.confidence:.2f}")
            print(f"  Facts: {len(result.facts)}, Sources: {len(result.sources)}")
        
        return True
    except Exception as e:
        print(f"❌ Agent interface test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    
    base_url = "http://localhost:5001"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  API endpoints not available: {e}")
        print("💡 Start the API adapter: python backend/agent_api_adapter.py")
        return False
    
    try:
        # Test ask endpoint
        response = requests.post(f"{base_url}/api/ask", json={
            "question": "What OAuth flows are supported?",
            "query_type": "hybrid"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ask endpoint working: {result.get('answer', '')[:100]}...")
        else:
            print(f"⚠️  Ask endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  Ask endpoint test failed: {e}")
    
    return True

def test_hybrid_system():
    """Test hybrid system"""
    print("\n🧪 Testing Hybrid System...")
    
    base_url = "http://localhost:5003"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Hybrid system health endpoint working")
        else:
            print(f"⚠️  Hybrid system health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  Hybrid system not available: {e}")
        print("💡 Start the hybrid system: python backend/app_agno_hybrid.py")
        return False
    
    try:
        # Test ask endpoint
        response = requests.post(f"{base_url}/api/ask", json={
            "question": "What OAuth flows are supported?"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hybrid system ask endpoint working: {result.get('answer', '')[:100]}...")
        else:
            print(f"⚠️  Hybrid system ask endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  Hybrid system ask endpoint test failed: {e}")
    
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive Agent System Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Database", test_database),
        ("BGE Embedder", test_bge_embedder),
        ("MeTTa System", test_metta_system),
        ("Agno RAG", test_agno_rag),
        ("Agent Interface", test_agent_interface),
        ("API Endpoints", test_api_endpoints),
        ("Hybrid System", test_hybrid_system)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. System is mostly functional.")
    else:
        print("❌ Many tests failed. Please check the issues above.")
    
    return passed == total

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test - just imports and basic functionality
        print("🚀 Running Quick Test...")
        success = test_imports() and test_environment()
        if success:
            print("✅ Quick test passed!")
        else:
            print("❌ Quick test failed!")
        return success
    else:
        # Comprehensive test
        return run_comprehensive_test()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

