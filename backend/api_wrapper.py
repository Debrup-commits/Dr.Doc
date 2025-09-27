#!/usr/bin/env python3
"""
MCP API Wrapper for Frontend
Simple HTTP API that wraps the MCP server endpoints for frontend access
"""

import os
import logging
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import our MCP server functions
from mcp_server import process_documents, ask_dr_doc

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

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

@app.route('/api/status', methods=['GET'])
def system_status():
    """Get system status"""
    try:
        from mcp_server import processing_status
        
        return jsonify({
            "success": True,
            "status": {
                "system_initialized": processing_status["initialized"],
                "asi_one_configured": bool(os.getenv("ASI_ONE_API_KEY")),
                "docs_processed": processing_status["initialized"]
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
