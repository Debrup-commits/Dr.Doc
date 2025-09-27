#!/usr/bin/env python3
"""
Fetch.ai Agno RAG Hybrid QA Application
Uses Agno RAG framework from fetchai/innovation-lab-examples
"""

import os
import sys
import json
import re
import time
from typing import List, Dict, Any, Tuple, Optional
from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
from dotenv import load_dotenv
from fetchai_agno_rag import FetchAIAgnoRAG

# Conditional MeTTa import - completely optional
METTA_AVAILABLE = False
MeTTaKnowledgeBase = None

ENABLE_METTA = os.getenv("ENABLE_METTA", "false").lower() in ('true', '1', 'yes', 'on')

if ENABLE_METTA:
    try:
        from metta_ingest import MeTTaKnowledgeBase
        METTA_AVAILABLE = True
        print("✅ MeTTa integration enabled and available")
    except ImportError as e:
        print(f"⚠️  MeTTa import failed: {e}")
        print("⚠️  Continuing without MeTTa integration")
        METTA_AVAILABLE = False
        ENABLE_METTA = False
else:
    print("⚠️  MeTTa integration disabled in configuration")

# Load environment variables
load_dotenv()

class AgnoHybridQASystem:
    """Hybrid QA system using Fetch.ai Agno RAG with optional MeTTa"""
    
    def __init__(self, use_fetchai: bool = True, require_openai_fallback: bool = False):
        self.metta_enabled = ENABLE_METTA and METTA_AVAILABLE
        self.use_fetchai = use_fetchai
        self.require_openai_fallback = require_openai_fallback
        
        # Initialize Agno RAG system with lazy loading
        print("🔄 Setting up Agno RAG system (lazy initialization)...")
        self.agno_rag = FetchAIAgnoRAG(
            use_fetchai=use_fetchai, 
            require_openai_fallback=require_openai_fallback,
            lazy_init=True  # Use lazy initialization to avoid startup issues
        )
        
        # Skip knowledge base loading during startup (will be loaded on first query)
        print("📚 Knowledge base will be loaded on first query (lazy loading)")
        # self._initialize_knowledge_base()  # Commented out to avoid startup delays
        
        # Initialize MeTTa knowledge base (if available)
        self.metta_kb = None
        if self.metta_enabled:
            try:
                self.metta_kb = MeTTaKnowledgeBase()
                self.metta_kb.load_atoms_from_file("api_facts.metta")
                print("✅ MeTTa knowledge base loaded successfully")
            except Exception as e:
                print(f"⚠️  Failed to load MeTTa knowledge base: {e}")
                self.metta_enabled = False
        
        print(f"✅ Agno Hybrid QA system fully loaded (MeTTa: {'ENABLED' if self.metta_enabled else 'DISABLED'})")
    
    def _initialize_knowledge_base(self):
        """Initialize and load the knowledge base with automatic ingestion if needed"""
        try:
            # First, try to load existing knowledge base
            knowledge_loaded = self.agno_rag.load_knowledge()
            if knowledge_loaded:
                print("✅ Knowledge base initialized successfully")
            else:
                print("⚠️  Knowledge base not initialized, attempting document ingestion...")
                self._attempt_automatic_ingestion()
            
        except Exception as load_error:
            print(f"⚠️  Knowledge base initialization failed: {load_error}")
            print("🔄 Attempting automatic document ingestion...")
            self._attempt_automatic_ingestion()
    
    def _attempt_automatic_ingestion(self):
        """Attempt automatic document ingestion"""
        try:
            # Check if docs directory exists
            import os
            docs_dir = "../docs"
            if not os.path.exists(docs_dir):
                print(f"❌ Documents directory {docs_dir} not found")
                print("💡 Please create the docs directory and add your documentation files")
                return
            
            # Check if there are any markdown files
            from pathlib import Path
            docs_path = Path(docs_dir)
            md_files = list(docs_path.glob("*.md"))
            
            if not md_files:
                print(f"⚠️  No markdown files found in {docs_dir}")
                print("💡 Please add .md documentation files to the docs directory")
                return
            
            print(f"📄 Found {len(md_files)} markdown files, starting ingestion...")
            
            # Ingest documents automatically
            self.agno_rag.ingest_documents(docs_dir)
            
            # Check if knowledge base is now ready
            if self.agno_rag.load_knowledge():
                print("✅ Knowledge base created and loaded successfully from documents")
            else:
                print("⚠️  Knowledge base created but may need manual verification")
                
        except Exception as ingest_error:
            print(f"❌ Automatic ingestion failed: {ingest_error}")
            print("💡 Please run manual ingestion or check your setup:")
            print("   python backend/fetchai_agno_rag.py")
            print("   or")
            print("   python backend/ingest.py")
    
    def detect_query_type(self, question: str) -> str:
        """Detect if question is suitable for MeTTa or RAG"""
        question_lower = question.lower()
        
        # If MeTTa is disabled, always use RAG
        if not self.metta_enabled:
            return 'rag'
        
        # MeTTa-suitable patterns
        metta_patterns = [
            r'what.*error.*code',
            r'what.*rate.*limit',
            r'what.*parameters',
            r'list.*endpoints',
            r'what.*tier',
            r'how.*many.*requests',
            r'what.*authentication',
            r'what.*endpoint.*supports',
            r'what.*status.*code',
            r'what.*slippage',
            r'what.*gas',
            r'what.*fee',
        ]
        
        for pattern in metta_patterns:
            if re.search(pattern, question_lower):
                return 'metta'
        
        # Default to RAG for general questions
        return 'rag'
    
    def query_metta(self, question: str) -> Dict[str, Any]:
        """Query MeTTa knowledge base for precise facts"""
        if not self.metta_enabled or not METTA_AVAILABLE or self.metta_kb is None:
            reason = "disabled in configuration" if not ENABLE_METTA else "not available"
            return {
                'answer': f'MeTTa knowledge base is not available ({reason})',
                'facts': [],
                'source': 'metta',
                'confidence': 0.0
            }
        
        try:
            # Try advanced pattern queries first
            advanced_results = self.metta_kb.query_advanced_patterns(question)
            if advanced_results:
                return self._format_metta_response(advanced_results, question, 'advanced_patterns')
            
            # Try specific MeTTa queries based on question content
            question_lower = question.lower()
            
            # Security-related queries
            if any(word in question_lower for word in ['oauth', 'authentication', 'security', 'auth']):
                security_patterns = self.metta_kb.query_security_patterns()
                if security_patterns:
                    return self._format_metta_response(security_patterns, question, 'security')
            
            # Performance-related queries
            if any(word in question_lower for word in ['performance', 'cache', 'optimization', 'speed']):
                performance_patterns = self.metta_kb.query_performance_patterns()
                if performance_patterns:
                    return self._format_metta_response(performance_patterns, question, 'performance')
            
            # Monitoring-related queries
            if any(word in question_lower for word in ['monitoring', 'logging', 'metrics', 'observability']):
                monitoring_concepts = self.metta_kb.query_monitoring_concepts()
                if monitoring_concepts:
                    return self._format_metta_response(monitoring_concepts, question, 'monitoring')
            
            # Error handling queries
            if any(word in question_lower for word in ['error', 'exception', 'failure', 'handling']):
                error_codes = self.metta_kb.query_error_codes()
                if error_codes:
                    return self._format_metta_response(error_codes, question, 'errors')
            
            # Rate limiting queries
            if any(word in question_lower for word in ['rate', 'limit', 'quota', 'throttle']):
                rate_limits = self.metta_kb.query_rate_limits()
                if rate_limits:
                    return self._format_metta_response(rate_limits, question, 'rate_limits')
            
            # Endpoint queries
            if any(word in question_lower for word in ['endpoint', 'api', 'url', 'route']):
                endpoints = self.metta_kb.query_endpoints()
                if endpoints:
                    return self._format_metta_response(endpoints, question, 'endpoints')
            
            return {
                'answer': 'No specific MeTTa facts found for this question. Try asking about security patterns, performance optimization, monitoring, error codes, rate limits, or API endpoints.',
                'facts': [],
                'source': 'metta',
                'confidence': 0.0
            }
        
        except Exception as e:
            print(f"Error in MeTTa query: {e}")
            return {
                'answer': f'MeTTa query failed: {str(e)}',
                'facts': [],
                'source': 'metta',
                'confidence': 0.0
            }
    
    def _format_metta_response(self, results: List[Dict[str, Any]], question: str, category: str) -> Dict[str, Any]:
        """Format MeTTa query results into a structured response."""
        if not results:
            return {
                'answer': f'No {category} information found in MeTTa knowledge base.',
                'facts': [],
                'source': 'metta',
                'confidence': 0.0
            }
        
        # Create a comprehensive answer based on the results
        answer_parts = []
        
        if category == 'security':
            answer_parts.append("## Security Patterns and Authentication")
            for result in results:
                if 'pattern' in result and 'flow_type' in result:
                    answer_parts.append(f"• **{result['pattern']}**: {result['flow_type']}")
        
        elif category == 'performance':
            answer_parts.append("## Performance Optimization Patterns")
            for result in results:
                if 'category' in result and 'pattern' in result:
                    answer_parts.append(f"• **{result['category']}**: {result['pattern']}")
        
        elif category == 'monitoring':
            answer_parts.append("## Monitoring and Observability")
            for result in results:
                if 'type' in result and 'concept' in result:
                    answer_parts.append(f"• **{result['type']}**: {result['concept']}")
        
        elif category == 'errors':
            answer_parts.append("## Error Codes and Handling")
            for result in results:
                if 'code' in result and 'description' in result:
                    answer_parts.append(f"• **{result['code']}**: {result['description']}")
        
        elif category == 'rate_limits':
            answer_parts.append("## Rate Limiting Information")
            for result in results:
                if 'tier' in result and 'limit' in result:
                    answer_parts.append(f"• **{result['tier']}**: {result['limit']}")
        
        elif category == 'endpoints':
            answer_parts.append("## Available API Endpoints")
            for endpoint in results:
                answer_parts.append(f"• **{endpoint}**")
        
        elif category == 'advanced_patterns':
            # Check if this is an OAuth/security query
            if any('oauth' in str(result.get('pattern', '')).lower() or 'security' in str(result.get('category', '')).lower() for result in results):
                answer_parts.append("## OAuth Authentication Flows")
                answer_parts.append("The following OAuth 2.0 authentication flows are supported:")
                answer_parts.append("")
                
                for result in results:
                    if result.get('category') == 'security' and result.get('flow_type'):
                        flow_type = result['flow_type']
                        if flow_type == 'authorization_code':
                            answer_parts.append("• **Authorization Code Flow**: Standard OAuth 2.0 flow for web applications")
                        elif flow_type == 'pkce':
                            answer_parts.append("• **PKCE (Proof Key for Code Exchange)**: Enhanced security for public clients")
                        elif flow_type == 'client_credentials':
                            answer_parts.append("• **Client Credentials Flow**: For server-to-server authentication")
                        elif flow_type == 'token_refresh':
                            answer_parts.append("• **Token Refresh Flow**: For refreshing expired access tokens")
                        else:
                            answer_parts.append(f"• **{flow_type}**: OAuth 2.0 authentication flow")
                
                answer_parts.append("")
                answer_parts.append("Each flow provides different security characteristics and is suitable for different client types (web apps, mobile apps, servers).")
            else:
                answer_parts.append("## Advanced API Patterns")
                for result in results:
                    if 'pattern' in result:
                        answer_parts.append(f"• **{result['pattern']}**")
                    elif 'concept' in result:
                        answer_parts.append(f"• **{result['concept']}**")
        
        answer = "\n".join(answer_parts) if answer_parts else "Found relevant information in MeTTa knowledge base."
        
        return {
            'answer': answer,
            'facts': results,
            'source': 'metta',
            'confidence': 0.9,
            'reasoning': f'Used MeTTa knowledge base for {category} information'
        }
    
    def query_rag(self, question: str) -> Dict[str, Any]:
        """Query Agno RAG system"""
        return self.agno_rag.query(question)
    
    def query(self, question: str) -> Dict[str, Any]:
        """Main query method that decides between MeTTa and RAG"""
        print(f"Processing question: {question}")
        
        # Detect query type
        query_type = self.detect_query_type(question)
        print(f"Detected query type: {query_type}")
        
        # Always try MeTTa first if available, then supplement with RAG
        metta_result = None
        if self.metta_enabled:
            metta_result = self.query_metta(question)
        
        # Always get RAG context for comprehensive information
        rag_result = self.query_rag(question)
        
        # Create hybrid response combining MeTTa facts with RAG context
        if metta_result and metta_result['confidence'] > 0.5 and metta_result['facts']:
            # MeTTa found good results - create hybrid response
            hybrid_answer = self._create_hybrid_response(metta_result, rag_result)
            
            return {
                'answer': hybrid_answer,
                'facts': metta_result['facts'],
                'sources': rag_result.get('sources', []),
                'source': 'hybrid',
                'confidence': metta_result['confidence'],
                'reasoning': f"Combined MeTTa facts (confidence: {metta_result['confidence']:.2f}) with RAG context for comprehensive answer",
                'model_source': self.agno_rag.model_source,
                'context_used': rag_result.get('context_used', 0),
                'metta_details': {
                    'facts_found': len(metta_result['facts']),
                    'confidence': metta_result['confidence']
                },
                'rag_details': {
                    'sources_found': len(rag_result.get('sources', [])),
                    'context_used': rag_result.get('context_used', 0)
                }
            }
        else:
            # MeTTa didn't find relevant facts, use RAG with MeTTa fallback info
            if metta_result:
                rag_result['reasoning'] = f"MeTTa found limited results (confidence: {metta_result['confidence']:.2f}), used RAG for comprehensive answer"
                rag_result['metta_fallback'] = metta_result
            else:
                rag_result['reasoning'] = "Used RAG system for comprehensive answer (MeTTa not available)"
            
            return rag_result
    
    def _create_hybrid_response(self, metta_result: Dict[str, Any], rag_result: Dict[str, Any]) -> str:
        """Create a hybrid response combining MeTTa facts with RAG context"""
        response_parts = []
        
        # Start with MeTTa facts (precise information)
        if metta_result.get('answer'):
            response_parts.append(metta_result['answer'])
        
        # Add RAG context only if it's complementary and not contradictory
        rag_content = rag_result.get('answer', '').strip()
        if rag_content and len(rag_content) > 100:
            # Check if RAG content contradicts MeTTa facts
            rag_lower = rag_content.lower()
            metta_answer = metta_result.get('answer', '').lower()
            
            # Only skip RAG content if it's clearly contradictory to MeTTa facts
            # Be more lenient - only block if RAG explicitly denies what MeTTa states
            contradictory_phrases = [
                'does not support oauth', 'oauth is not supported', 'no oauth flows',
                'does not have oauth', 'oauth is not available', 'does not mention oauth at all'
            ]
            
            is_contradictory = any(phrase in rag_lower for phrase in contradictory_phrases)
            
            # Only block if RAG explicitly contradicts the specific MeTTa topic
            if 'oauth' in metta_answer and any(phrase in rag_lower for phrase in [
                'no oauth', 'doesn\'t support oauth', 'oauth not supported'
            ]):
                is_contradictory = True
            
            if not is_contradictory:
                response_parts.append("\n---\n")
                response_parts.append("## Additional Context")
                response_parts.append(rag_content)
            else:
                # Instead of contradictory content, add a note about MeTTa being the authoritative source
                response_parts.append("\n---\n")
                response_parts.append("## Information Source")
                response_parts.append("The above information is based on structured knowledge base facts. For additional context or implementation details, please refer to the official documentation.")
        
        # Always add sources section if RAG found documents, regardless of contradiction
        if rag_result.get('sources'):
            response_parts.append("\n---\n")
            response_parts.append("## Documentation Sources")
            response_parts.append("The following documentation files were consulted:")
            for i, source in enumerate(rag_result['sources'][:5], 1):  # Show top 5 sources
                source_name = source.get('file_path', '').split('/')[-1] if source.get('file_path') else 'Unknown'
                relevance_score = (source.get('score', 0) * 100)
                response_parts.append(f"**{i}. {source_name}** (relevance: {relevance_score:.1f}%)")
                if source.get('heading'):
                    response_parts.append(f"   📄 Section: {source['heading']}")
            response_parts.append("")
            response_parts.append("*These sources provide additional context and implementation details for the topics covered above.*")
        
        return "\n".join(response_parts)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize Agno hybrid QA system
use_fetchai = os.getenv("USE_FETCHAI", "true").lower() in ('true', '1', 'yes', 'on')
require_openai_fallback = os.getenv("REQUIRE_OPENAI_FALLBACK", "false").lower() in ('true', '1', 'yes', 'on')

print("🚀 Initializing Fetch.ai Agno RAG Hybrid QA System...")

# Check if API keys are configured
fetchai_key = os.getenv("ASI_ONE_API_KEY", "")
openai_key = os.getenv("OPENAI_API_KEY", "")

if not fetchai_key or fetchai_key.startswith("your_"):
    print("⚠️  Fetch.ai API key not configured or using placeholder value")
    print("💡 Please set ASI_ONE_API_KEY in your .env file")

if not openai_key or openai_key.startswith("your_"):
    print("⚠️  OpenAI API key not configured or using placeholder value")
    print("💡 Please set OPENAI_API_KEY in your .env file")

agno_hybrid_qa = AgnoHybridQASystem(use_fetchai=use_fetchai, require_openai_fallback=require_openai_fallback)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fetch.ai Agno RAG Hybrid Q&A</title>
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
        .search-form {
            margin-bottom: 30px;
        }
        .search-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .search-input:focus {
            outline: none;
            border-color: #007bff;
        }
        .search-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        .search-button:hover {
            background: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }
        .answer {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .reasoning {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 14px;
            color: #1976d2;
        }
        .facts {
            background: #f3e5f5;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .fact {
            background: white;
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
            font-family: monospace;
            font-size: 14px;
        }
        .sources {
            margin-top: 20px;
        }
        .source {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .source-header {
            font-weight: bold;
            color: #333;
        }
        .source-details {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #f5c6cb;
        }
        .system-info {
            background: #e8f5e8;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 14px;
            color: #2e7d32;
        }
        .agno-badge {
            background: #6c5ce7;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Fetch.ai Agno RAG Hybrid Q&A <span class="agno-badge">AGNO</span></h1>
        <div class="system-info">
            <strong>Fetch.ai Agno RAG System:</strong> This system uses the Agno RAG framework from fetchai/innovation-lab-examples 
            with PgVector database and hybrid search capabilities, powered by Fetch.ai ASI:One models.
        </div>
        
        <form class="search-form" onsubmit="askQuestion(event)">
            <input type="text" id="question" class="search-input" 
                   placeholder="Ask about API documentation using Agno RAG..." 
                   required>
            <button type="submit" class="search-button">Ask Question</button>
        </form>
        
        <div id="result"></div>
    </div>

    <script>
        async function askQuestion(event) {
            event.preventDefault();
            
            const question = document.getElementById('question').value;
            const resultDiv = document.getElementById('result');
            
            if (!question.trim()) return;
            
            // Show loading state
            resultDiv.innerHTML = '<div class="loading">Analyzing question and querying Agno RAG system...</div>';
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    displayResult(data);
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        function displayResult(data) {
            const resultDiv = document.getElementById('result');
            
            let factsHtml = '';
            if (data.facts && data.facts.length > 0) {
                factsHtml = '<div class="facts"><h3>MeTTa Facts:</h3>';
                data.facts.forEach((fact, index) => {
                    factsHtml += `<div class="fact">${JSON.stringify(fact, null, 2)}</div>`;
                });
                factsHtml += '</div>';
            }
            
            let sourcesHtml = '';
            if (data.sources && data.sources.length > 0) {
                sourcesHtml = '<div class="sources"><h3>Agno RAG Sources:</h3>';
                data.sources.forEach((source, index) => {
                    sourcesHtml += `
                        <div class="source">
                            <div class="source-header">Source ${index + 1}</div>
                            <div class="source-details">
                                Source: ${source.source || 'Unknown'}<br>
                                Content: ${source.content || 'N/A'}<br>
                                Score: ${(source.score || 0).toFixed(3)}
                            </div>
                        </div>
                    `;
                });
                sourcesHtml += '</div>';
            }
            
            let reasoningHtml = '';
            if (data.reasoning) {
                reasoningHtml = `<div class="reasoning"><strong>System Reasoning:</strong> ${data.reasoning}</div>`;
            }
            
            let modelSourceHtml = '';
            if (data.model_source) {
                modelSourceHtml = `<div class="reasoning"><strong>Model Source:</strong> ${data.model_source.toUpperCase()}</div>`;
            }
            
            resultDiv.innerHTML = `
                <div class="result">
                    <div class="answer">${data.answer}</div>
                    ${reasoningHtml}
                    ${modelSourceHtml}
                    ${factsHtml}
                    ${sourcesHtml}
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint for asking questions."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Process the question using Agno hybrid system
        result = agno_hybrid_qa.query(question)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask/stream', methods=['POST'])
def ask_question_stream():
    """Streaming API endpoint for asking questions."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        def generate_stream():
            try:
                # Process the question using Agno hybrid system
                result = agno_hybrid_qa.query(question)
                
                # Get the full answer
                full_answer = result.get('answer', '')
                
                # Stream the answer word by word with typing effect
                words = full_answer.split(' ')
                current_text = ""
                
                for i, word in enumerate(words):
                    current_text += word + " "
                    
                    # Create streaming response
                    stream_data = {
                        'type': 'content',
                        'content': current_text,
                        'isComplete': False,
                        'metadata': {
                            'source': result.get('source', 'agno_rag'),
                            'reasoning': result.get('reasoning', ''),
                            'context_used': result.get('context_used', 0)
                        }
                    }
                    
                    yield f"data: {json.dumps(stream_data)}\n\n"
                    
                    # Add typing delay (faster for punctuation, slower for regular words)
                    if word.endswith(('.', '!', '?', ':', ';')):
                        time.sleep(0.1)  # Pause after sentences
                    elif word.endswith((',', ';')):
                        time.sleep(0.05)  # Short pause after commas
                    else:
                        time.sleep(0.02)  # Normal typing speed
                
                # Send completion signal
                final_data = {
                    'type': 'complete',
                    'content': full_answer,
                    'isComplete': True,
                    'metadata': {
                        'source': result.get('source', 'agno_rag'),
                        'reasoning': result.get('reasoning', ''),
                        'context_used': result.get('context_used', 0),
                        'sources': result.get('sources', []),
                        'facts': result.get('facts', [])
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

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    health_data = {
        'status': 'healthy',
        'agno_rag_ready': agno_hybrid_qa.agno_rag.knowledge is not None,
        'metta_enabled': agno_hybrid_qa.metta_enabled,
        'model_source': agno_hybrid_qa.agno_rag.model_source,
        'use_fetchai': agno_hybrid_qa.use_fetchai
    }
    
    # Add MeTTa data only if enabled
    if agno_hybrid_qa.metta_enabled and agno_hybrid_qa.metta_kb:
        health_data['metta_atoms_loaded'] = len(agno_hybrid_qa.metta_kb.atoms)
    else:
        health_data['metta_atoms_loaded'] = 0
    
    return jsonify(health_data)

def check_port_available(port=5003):
    """Check if a specific port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def kill_process_on_port(port=5003):
    """Kill any process using the specified port"""
    import subprocess
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🔄 Killing process {pid} on port {port}")
                    subprocess.run(['kill', '-9', pid], check=False)
            print(f"✅ Freed up port {port}")
            return True
        return False
    except Exception as e:
        print(f"⚠️  Could not kill processes on port {port}: {e}")
        return False

if __name__ == '__main__':
    print("Starting Fetch.ai Agno RAG Hybrid Q&A Server...")
    
    # Force use of port 5003
    port = 5003
    
    # Check if port is available
    if not check_port_available(port):
        print(f"⚠️  Port {port} is in use, attempting to free it...")
        if kill_process_on_port(port):
            # Wait a moment for the port to be freed
            import time
            time.sleep(2)
            if check_port_available(port):
                print(f"✅ Port {port} is now available")
            else:
                print(f"❌ Port {port} is still in use. Please manually stop the process:")
                print(f"   lsof -ti:{port} | xargs kill -9")
                sys.exit(1)
        else:
            print(f"❌ Could not free port {port}. Please manually stop the process:")
            print(f"   lsof -ti:{port} | xargs kill -9")
            sys.exit(1)
    
    print(f"🚀 Starting server on port {port}")
    print(f"Open your browser to http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)