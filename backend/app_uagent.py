#!/usr/bin/env python3
"""
Flask API adapter for the ASI:One RAG uAgent
Maintains compatibility with the existing frontend
"""

import os
import json
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

# Import the agent client
from agent_client import get_client, set_agent_address

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASI:One RAG Agent</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status.healthy {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.unhealthy {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }
        .response {
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
        .error {
            border-left-color: #dc3545;
            background-color: #f8d7da;
            color: #721c24;
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 2s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 ASI:One RAG Agent</h1>
        
        <div id="status" class="status">
            <span id="status-text">Checking agent status...</span>
        </div>
        
        <form id="question-form">
            <div class="form-group">
                <label for="question">Ask a question:</label>
                <textarea id="question" name="question" placeholder="Enter your question here..." required></textarea>
            </div>
            <button type="submit" id="submit-btn">Ask Question</button>
        </form>
        
        <div id="response" style="display: none;"></div>
    </div>

    <script>
        let agentAddress = null;
        
        // Check agent status on page load
        async function checkStatus() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                
                const statusDiv = document.getElementById('status');
                const statusText = document.getElementById('status-text');
                
                if (data.status === 'healthy') {
                    statusDiv.className = 'status healthy';
                    statusText.textContent = `✅ Agent is healthy - System: ${data.system}, Embedder: ${data.embedder}, Database: ${data.database}, MeTTa: ${data.metta_enabled ? 'Enabled' : 'Disabled'}`;
                } else {
                    statusDiv.className = 'status unhealthy';
                    statusText.textContent = `❌ Agent is unhealthy: ${data.error || 'Unknown error'}`;
                }
            } catch (error) {
                const statusDiv = document.getElementById('status');
                const statusText = document.getElementById('status-text');
                statusDiv.className = 'status unhealthy';
                statusText.textContent = `❌ Failed to check agent status: ${error.message}`;
            }
        }
        
        // Handle form submission
        document.getElementById('question-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const question = document.getElementById('question').value;
            const submitBtn = document.getElementById('submit-btn');
            const responseDiv = document.getElementById('response');
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            responseDiv.style.display = 'block';
            responseDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Processing your question...</p></div>';
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    responseDiv.className = 'response';
                    responseDiv.innerHTML = `
                        <h3>Answer:</h3>
                        <div style="white-space: pre-wrap;">${data.answer}</div>
                        ${data.sources ? `<h4>Sources:</h4><ul>${data.sources.map(s => `<li>${s}</li>`).join('')}</ul>` : ''}
                        ${data.metta_reasoning ? `<h4>MeTTa Reasoning:</h4><div style="white-space: pre-wrap;">${data.metta_reasoning}</div>` : ''}
                    `;
                } else {
                    responseDiv.className = 'response error';
                    responseDiv.innerHTML = `<h3>Error:</h3><p>${data.answer}</p>`;
                }
            } catch (error) {
                responseDiv.className = 'response error';
                responseDiv.innerHTML = `<h3>Error:</h3><p>Failed to process question: ${error.message}</p>`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Ask Question';
            }
        });
        
        // Check status on page load
        checkStatus();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check the actual uAgent health
        client = get_client()
        result = client.health_check()
        
        if result.get('status') == 'healthy':
            return jsonify({
                "status": "healthy",
                "system": result.get('system', 'asi_one_rag_agent'),
                "embedder": result.get('embedder', 'bge'),
                "database": result.get('database', 'postgresql_pgvector'),
                "metta_enabled": result.get('metta_enabled', False)
            }), 200
        else:
            return jsonify({
                "status": "unhealthy",
                "error": result.get('error', 'Unknown error')
            }), 503
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a question to the ASI:One RAG agent"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                "answer": "Please provide a question in the request body.",
                "success": False,
                "error": "Missing question field"
            }), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({
                "answer": "Please provide a non-empty question.",
                "success": False,
                "error": "Empty question"
            }), 400
        
        # Get session ID if provided
        session_id = data.get('session_id')
        
        # Use the uAgent client to communicate with the actual agent
        client = get_client()
        result = client.ask_question(question, session_id)
        
        if result.get('success', False):
            return jsonify({
                "answer": result.get('answer', ''),
                "sources": result.get('sources', []),
                "metta_reasoning": result.get('metta_reasoning'),
                "success": True
            }), 200
        else:
            return jsonify({
                "answer": result.get('answer', 'An error occurred'),
                "success": False,
                "error": result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({
            "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/ask/stream', methods=['POST'])
def ask_question_stream():
    """Streaming endpoint for questions (for future use)"""
    # For now, just redirect to the regular ask endpoint
    return ask_question()

@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    """Get agent status information"""
    try:
        client = get_client()
        result = client.health_check()
        
        return jsonify({
            "status": result.get('status', 'unknown'),
            "system": result.get('system', 'asi_one_rag_agent'),
            "embedder": result.get('embedder', 'bge'),
            "database": result.get('database', 'postgresql_pgvector'),
            "metta_enabled": result.get('metta_enabled', False),
            "agent_address": getattr(client.client, 'agent_address', 'Not set')
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/agent/info', methods=['GET'])
def agent_info():
    """Get agent information"""
    return jsonify({
        "name": "ASI:One RAG Agent",
        "description": "AI agent powered by ASI:One Mini with MeTTa and RAG integration",
        "version": "1.0.0",
        "capabilities": [
            "Question answering with RAG",
            "MeTTa symbolic reasoning",
            "Document retrieval and citation",
            "ASI:One Mini LLM integration"
        ]
    }), 200

if __name__ == '__main__':
    print("🚀 Starting ASI:One RAG Agent API...")
    print("📍 API will be available at: http://localhost:5003")
    print("⚠️  Make sure the ASI:One RAG uAgent is running on port 8001")
    print("⚠️  Set the ASI_ONE_API_KEY environment variable")
    
    # You can set the agent address here if known
    # set_agent_address("agent1q...")
    
    app.run(host='0.0.0.0', port=5003, debug=True)
