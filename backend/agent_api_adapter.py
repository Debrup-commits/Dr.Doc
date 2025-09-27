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
from agent_rag_interface import get_agent_interface, query_for_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the agent client
AGENT_ADDRESS = os.getenv("AGENT_ADDRESS", "agent1q...")  # Replace with actual agent address
agent_client = SyncDocumentQAClient(AGENT_ADDRESS)

# Initialize the RAG interface for direct queries
rag_interface = None

def initialize_rag_interface():
    """Initialize the RAG interface"""
    global rag_interface
    try:
        rag_interface = get_agent_interface()
        print("✅ RAG interface initialized for API adapter")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize RAG interface: {e}")
        return False

# Initialize on startup
initialize_rag_interface()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Try agent health check first
        try:
            health = agent_client.health_check()
            return jsonify(health)
        except Exception as agent_error:
            # Fallback to direct RAG interface health check
            if rag_interface:
                status = rag_interface.get_system_status()
                return jsonify({
                    'status': 'healthy' if status['initialized'] else 'error',
                    'rag_available': status.get('rag_available', False),
                    'metta_available': status.get('metta_available', False),
                    'model_source': status.get('rag_model_source', 'unknown'),
                    'success': status['initialized'],
                    'error': None if status['initialized'] else 'RAG system not fully initialized'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'error': 'Both agent and RAG interface unavailable',
                    'success': False
                }), 500
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
        context = data.get('context')
        query_type = data.get('query_type', 'auto')  # "rag", "metta", "hybrid", "auto"
        
        # Try agent first, fallback to direct RAG interface
        try:
            # Use agent client
            response = agent_client.ask_question(
                question=question,
                user_id=user_id,
                session_id=session_id,
                context=context,
                query_type=query_type
            )
            return jsonify(response)
        except Exception as agent_error:
            # Fallback to direct RAG interface
            if rag_interface:
                print(f"⚠️  Agent unavailable, using direct RAG interface: {agent_error}")
                result = query_for_agent(
                    question=question,
                    query_type=query_type,
                    context=context,
                    user_id=user_id
                )
                return jsonify(result)
            else:
                return jsonify({
                    'error': f'Both agent and RAG interface unavailable: {agent_error}',
                    'success': False
                }), 500
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/ask/stream', methods=['POST'])
def ask_question_stream():
    """Streaming endpoint for questions"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        query_type = data.get('query_type', 'auto')
        context = data.get('context')
        user_id = data.get('user_id')
        
        def generate_stream():
            try:
                # Get the answer
                if rag_interface:
                    result = query_for_agent(
                        question=question,
                        query_type=query_type,
                        context=context,
                        user_id=user_id
                    )
                    answer = result.get('answer', 'No answer available')
                else:
                    answer = "RAG system not available"
                
                # Stream the answer word by word
                words = answer.split(' ')
                current_text = ""
                
                for i, word in enumerate(words):
                    current_text += word + " "
                    
                    stream_data = {
                        'type': 'content',
                        'content': current_text,
                        'isComplete': False,
                        'metadata': {
                            'word_count': i + 1,
                            'total_words': len(words)
                        }
                    }
                    
                    yield f"data: {json.dumps(stream_data)}\n\n"
                    
                    # Add typing delay
                    if word.endswith(('.', '!', '?')):
                        time.sleep(0.1)
                    else:
                        time.sleep(0.02)
                
                # Send completion
                final_data = {
                    'type': 'complete',
                    'content': answer,
                    'isComplete': True,
                    'metadata': {
                        'total_words': len(words),
                        'response_time': result.get('response_time', 0) if rag_interface else 0
                    }
                }
                
                yield f"data: {json.dumps(final_data)}\n\n"
                
            except Exception as e:
                error_data = {
                    'type': 'error',
                    'error': str(e),
                    'isComplete': True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ingest', methods=['POST'])
def ingest_documents():
    """Ingest documents into the knowledge base"""
    try:
        data = request.get_json() or {}
        docs_dir = data.get('docs_dir', '../docs')
        force_refresh = data.get('force_refresh', False)
        
        if not rag_interface:
            return jsonify({
                'error': 'RAG system not available',
                'success': False
            }), 500
        
        # Ingest documents
        success = rag_interface.ingest_documents(docs_dir)
        
        if success:
            return jsonify({
                'message': f'Documents ingested successfully from {docs_dir}',
                'success': True
            })
        else:
            return jsonify({
                'error': 'Document ingestion failed',
                'success': False
            }), 500
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/extract-facts', methods=['POST'])
def extract_metta_facts():
    """Extract MeTTa facts from documents"""
    try:
        data = request.get_json() or {}
        docs_dir = data.get('docs_dir', '../docs')
        
        if not rag_interface:
            return jsonify({
                'error': 'RAG system not available',
                'success': False
            }), 500
        
        # Extract MeTTa facts
        success = rag_interface.extract_metta_facts(docs_dir)
        
        if success:
            facts_count = len(rag_interface.metta_kb.atoms) if rag_interface.metta_kb else 0
            return jsonify({
                'message': f'Extracted {facts_count} MeTTa facts from {docs_dir}',
                'facts_count': facts_count,
                'success': True
            })
        else:
            return jsonify({
                'error': 'MeTTa fact extraction failed',
                'success': False
            }), 500
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get detailed system status"""
    try:
        if not rag_interface:
            return jsonify({
                'status': 'error',
                'error': 'RAG system not available',
                'success': False
            }), 500
        
        status = rag_interface.get_system_status()
        
        return jsonify({
            'status': 'healthy' if status['initialized'] else 'error',
            'rag_available': status.get('rag_available', False),
            'metta_available': status.get('metta_available', False),
            'use_fetchai': status.get('use_fetchai', False),
            'rag_model_source': status.get('rag_model_source', 'unknown'),
            'rag_knowledge_ready': status.get('rag_knowledge_ready', False),
            'metta_atoms_loaded': status.get('metta_atoms_loaded', 0),
            'success': status['initialized']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/query-types', methods=['GET'])
def get_query_types():
    """Get available query types"""
    return jsonify({
        'query_types': [
            {
                'type': 'auto',
                'description': 'Automatically detect best query type',
                'recommended': True
            },
            {
                'type': 'rag',
                'description': 'Use RAG system for comprehensive answers',
                'recommended': False
            },
            {
                'type': 'metta',
                'description': 'Use MeTTa for precise facts',
                'recommended': False
            },
            {
                'type': 'hybrid',
                'description': 'Combine RAG and MeTTa for best results',
                'recommended': True
            }
        ]
    })

@app.route('/api/examples', methods=['GET'])
def get_example_questions():
    """Get example questions for testing"""
    return jsonify({
        'examples': [
            {
                'question': 'What OAuth flows are supported?',
                'query_type': 'hybrid',
                'description': 'Security patterns and authentication'
            },
            {
                'question': 'What are the rate limits for the free tier?',
                'query_type': 'metta',
                'description': 'Precise rate limit information'
            },
            {
                'question': 'How do I authenticate with the API?',
                'query_type': 'rag',
                'description': 'General authentication guidance'
            },
            {
                'question': 'What error codes can the /swap endpoint return?',
                'query_type': 'metta',
                'description': 'Specific error code information'
            },
            {
                'question': 'Explain the API architecture and design patterns',
                'query_type': 'rag',
                'description': 'Comprehensive architectural overview'
            }
        ]
    })

@app.route('/')
def index():
    """API documentation endpoint"""
    return jsonify({
        'name': 'Document Q&A Agent API',
        'version': '1.0.0',
        'description': 'REST API for querying documents using RAG and MeTTa systems',
        'endpoints': {
            'POST /api/ask': 'Ask a question',
            'POST /api/ask/stream': 'Streaming question endpoint',
            'GET /api/health': 'Health check',
            'GET /api/status': 'Detailed system status',
            'POST /api/ingest': 'Ingest documents',
            'POST /api/extract-facts': 'Extract MeTTa facts',
            'GET /api/query-types': 'Available query types',
            'GET /api/examples': 'Example questions'
        },
        'query_types': ['auto', 'rag', 'metta', 'hybrid']
    })

if __name__ == '__main__':
    print("🚀 Starting Document Q&A Agent API Adapter...")
    print("📡 API will be available at http://localhost:5001")
    print("🔗 Agent endpoint:", AGENT_ADDRESS)
    
    # Check if RAG interface is available
    if rag_interface:
        print("✅ RAG interface available")
    else:
        print("⚠️  RAG interface not available - some features may not work")
    
    app.run(debug=True, host='0.0.0.0', port=5001)