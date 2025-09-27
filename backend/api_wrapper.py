#!/usr/bin/env python3
"""
Dr.Doc API Wrapper

Clean HTTP API wrapper that exposes MCP server endpoints for frontend integration.
Provides RESTful endpoints for document processing and Q&A functionality.

Author: Dr.Doc Team
"""

import os
import logging
import asyncio
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Local imports
from mcp_server import process_documents, ask_dr_doc

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask application
app = Flask(__name__)
CORS(app)

# Initialize RAG system at server startup
def initialize_rag_at_startup():
    """Initialize RAG system when server starts up"""
    try:
        from mcp_server import rag_system
        if rag_system is None:
            print("🔄 Initializing RAG pipeline at server startup...")
            print("📡 Loading BGE embeddings and preparing the system for fast responses")
            
            from simple_rag import SimpleRAG
            import mcp_server
            mcp_server.rag_system = SimpleRAG()
            
            print("✅ RAG pipeline is ready to use!")
            print("🚀 Ask endpoint will respond faster now")
            logger.info("✅ RAG system initialized at server startup")
        else:
            print("ℹ️ RAG system was already initialized")
    except Exception as e:
        print(f"⚠️ Could not initialize RAG system at startup: {e}")
        logger.warning(f"Could not initialize RAG system at startup: {e}")

def auto_process_documents_if_needed():
    """Auto-process documents if system status indicates they're needed"""
    try:
        print("🔍 Checking if documents need to be processed...")
        status = check_system_status()
        
        # Check if any critical status fields are False
        needs_processing = not status.get("docs_processed", False) or not status.get("system_initialized", False)
        
        if needs_processing:
            print("📚 System needs document processing. Auto-processing documents...")
            
            # Default docs directory
            docs_dir = "../docs"
            docs_path = Path(docs_dir)
            if docs_path.exists() and docs_path.is_dir():
                print(f"🔄 Processing documents from: {docs_dir}")
                
                # Call the MCP server function to process documents
                result = asyncio.run(process_documents(docs_dir))
                print(f"✅ Auto-processing result: {result}")
                logger.info(f"Auto-processed documents: {result}")
            else:
                print(f"⚠️ Docs directory not found or invalid: {docs_dir}")
                print("   Please create the docs directory and add documents, then call /api/process-documents")
                print("   System will be ready once documents are processed")
        else:
            print("✅ System is already fully initialized - no processing needed")
            
    except Exception as e:
        print(f"⚠️ Could not auto-process documents: {e}")
        logger.warning(f"Auto-processing failed: {e}")

# Initialize RAG system and auto-process documents if needed
initialize_rag_at_startup()
auto_process_documents_if_needed()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "system": "Dr.Doc MCP API Wrapper",
        "version": "1.0.0"
    }), 200

@app.route('/api/process-documents', methods=['POST'])
def process_docs_endpoint():
    """
    Frontend endpoint for document processing
    Idempotent - only processes if not already done
    """
    try:
        data = request.get_json()
        if not data or 'docs_dir_path' not in data:
            return jsonify({
                "success": False,
                "error": "Missing docs_dir_path in request body"
            }), 400
        
        docs_dir_path = data['docs_dir_path'].strip()
        if not docs_dir_path:
            return jsonify({
                "success": False,
                "error": "docs_dir_path cannot be empty"
            }), 400
        
        # Call the MCP server function
        result = asyncio.run(process_documents(docs_dir_path))
        
        return jsonify({
            "success": True,
            "result": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in process_docs_endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/ask', methods=['POST'])
def ask_dr_doc_endpoint():
    """
    Frontend endpoint for Dr.Doc agent
    Takes user prompt and returns ASI:One response
    """
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                "success": False,
                "error": "Missing question in request body"
            }), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({
                "success": False,
                "error": "Question cannot be empty"
            }), 400
        
        # Optional session ID
        session_id = data.get('session_id')
        
        # Call the MCP server function
        result = asyncio.run(ask_dr_doc(question, session_id))
        
        return jsonify({
            "success": True,
            "answer": result,
            "question": question,
            "session_id": session_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in ask_dr_doc_endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def check_system_status():
    """Check if MeTTa files and RAG pipelines are properly set up"""
    try:
        # Check if MeTTa knowledge base exists
        metta_file = Path("api_facts.metta")
        metta_available = metta_file.exists() and metta_file.stat().st_size > 0
        
        # Check if RAG pipeline has documents
        rag_available = False
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost", port="5532", database="ai", 
                user="ai", password="ai"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            rag_available = doc_count > 0
        except Exception as e:
            logger.warning(f"Could not check database status: {e}")
        
        return {
            "docs_processed": metta_available and rag_available,
            "system_initialized": metta_available and rag_available,
            "metta_available": metta_available,
            "rag_available": rag_available
        }
        
    except Exception as e:
        logger.error(f"Error checking system status: {e}")
        return {
            "docs_processed": False,
            "system_initialized": False,
            "metta_available": False,
            "rag_available": False
        }

@app.route('/api/status', methods=['GET'])
def system_status():
    """Get comprehensive system status"""
    try:
        status_info = check_system_status()
        
        return jsonify({
            "success": True,
            "status": {
                "system_initialized": status_info["system_initialized"],
                "docs_processed": status_info["docs_processed"],
                "asi_one_configured": bool(os.getenv("ASI_ONE_API_KEY")),
                "metta_available": status_info["metta_available"],
                "rag_available": status_info["rag_available"]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in system_status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Dr.Doc MCP API Wrapper...")
    print("📍 API will be available at: http://localhost:5003")
    print("📋 Available endpoints:")
    print("   POST /api/process-documents - Process documents (idempotent)")
    print("   POST /api/ask - Ask questions to Dr.Doc agent")
    print("   GET /api/status - Get system status")
    print("   GET /api/health - Health check")
    
    app.run(host='0.0.0.0', port=5003, debug=True)
