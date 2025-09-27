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
from rag_initializer import initialize_rag_system, auto_process_documents_if_needed, get_rag_system, get_metta_kb, get_processing_status

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask application
app = Flask(__name__)
CORS(app)

# Initialize RAG system at server startup using the independent initializer
def initialize_system_at_startup():
    """Initialize RAG system and documents when server starts up"""
    try:
        print("🚀 Starting RAG system initialization...")
        logger.info("🚀 Starting RAG system initialization...")
        
        # Initialize RAG system
        rag_system = initialize_rag_system()
        
        # Update the global RAG system in mcp_server
        import mcp_server
        mcp_server.rag_system = rag_system
        mcp_server.metta_kb = get_metta_kb()
        mcp_server.processing_status = get_processing_status()
        
        print("✅ RAG system initialization completed!")
        logger.info("✅ RAG system initialization completed")
        
        # Auto-process documents if needed
        print("🔍 Checking document processing status...")
        docs_success = asyncio.run(auto_process_documents_if_needed())
        
        if docs_success:
            print("🎯 System is fully ready for requests!")
            logger.info("🎯 System is fully ready for requests")
        else:
            print("⚠️ System ready with warnings - check document processing")
            logger.warning("System ready with warnings")
            
    except Exception as e:
        print(f"⚠️ Could not initialize system at startup: {e}")
        logger.warning(f"Could not initialize system at startup: {e}")

# Initialize RAG system and documents
initialize_system_at_startup()

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
        # Use the status from the RAG initializer
        return get_processing_status()
        
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
