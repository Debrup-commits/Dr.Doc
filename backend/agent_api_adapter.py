#!/usr/bin/env python3
"""
Flask API Adapter for Document Q&A uAgent
Provides REST API endpoints that communicate with the uAgent
"""

import os
import time
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from agent_client import SyncDocumentQAClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the agent client
AGENT_ADDRESS = os.getenv("AGENT_ADDRESS", "agent1q...")  # Replace with actual agent address
agent_client = SyncDocumentQAClient(AGENT_ADDRESS)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        health = agent_client.health_check()
        return jsonify(health)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a question to the Document Q&A agent"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Question is required',
                'success': False
            }), 400
        
        question = data['question']
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        # Ask the agent
        response = agent_client.ask_question(question, user_id, session_id)
        
        if response.get('success', False):
            return jsonify(response)
        else:
            return jsonify(response), 500
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/ask/stream', methods=['POST'])
def ask_question_stream():
    """Streaming endpoint for questions (simulated streaming)"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Question is required',
                'success': False
            }), 400
        
        question = data['question']
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        def generate_stream():
            # Send initial status
            yield f"data: {jsonify({'status': 'thinking', 'message': 'Processing your question...'}).data.decode()}\n\n"
            
            # Ask the agent
            response = agent_client.ask_question(question, user_id, session_id)
            
            if response.get('success', False):
                # Send the response
                yield f"data: {jsonify(response).data.decode()}\n\n"
            else:
                # Send error
                yield f"data: {jsonify(response).data.decode()}\n\n"
            
            # Send completion
            yield f"data: {jsonify({'status': 'complete'}).data.decode()}\n\n"
        
        return Response(generate_stream(), mimetype='text/plain')
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    """Get detailed agent status"""
    try:
        health = agent_client.health_check()
        
        status = {
            'agent_address': AGENT_ADDRESS,
            'agent_type': 'Document Q&A uAgent',
            'framework': 'Fetch.ai uAgents',
            'capabilities': [
                'MeTTa Knowledge Base Query',
                'RAG Document Retrieval',
                'Hybrid Response Generation',
                'Fetch.ai ASI:One Integration',
                'Agentverse Communication'
            ],
            'health': health
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/agent/info', methods=['GET'])
def agent_info():
    """Get agent information"""
    return jsonify({
        'name': 'Document Q&A Agent',
        'version': '1.0.0',
        'description': 'Intelligent Document Question Answering Agent using Fetch.ai uAgents framework',
        'features': [
            'MeTTa symbolic reasoning',
            'RAG document retrieval',
            'Hybrid response generation',
            'Fetch.ai ASI:One LLM integration',
            'Agentverse ecosystem integration',
            'Autonomous operation',
            'Health monitoring',
            'Error recovery'
        ],
        'technology_stack': [
            'Fetch.ai uAgents Framework',
            'MeTTa Knowledge Base',
            'Agno RAG System',
            'Fetch.ai ASI:One Models',
            'BGE Embeddings',
            'PostgreSQL with pgvector',
            'Python asyncio'
        ],
        'agent_address': AGENT_ADDRESS,
        'inspector_url': f"https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8001&address={AGENT_ADDRESS}"
    })

if __name__ == '__main__':
    print("🚀 Starting Document Q&A Agent API Adapter...")
    print(f"📍 API will be available at: http://localhost:5003")
    print(f"🤖 Agent address: {AGENT_ADDRESS}")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=False)
