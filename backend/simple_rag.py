#!/usr/bin/env python3
"""
Dr.Doc Simple RAG System

Clean RAG implementation using BGE embeddings and PostgreSQL.
Provides document retrieval and similarity search capabilities.

Author: Dr.Doc Team
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# MeTTa integration (optional)
METTA_AVAILABLE = False
MeTTaKnowledgeBase = None

try:
    from metta_ingest import MeTTaKnowledgeBase
    METTA_AVAILABLE = True
    print("✅ MeTTa integration available")
except ImportError as e:
    print(f"⚠️  MeTTa import failed: {e}")
    print("⚠️  Continuing without MeTTa integration")

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRAG:
    """Simple RAG system using BGE embeddings and PostgreSQL"""
    
    def __init__(self):
        self.embedder = None
        self.db_url = "postgresql://ai:ai@localhost:5532/ai"
        self._initialized = False
        self.metta_kb = None
        self.metta_enabled = METTA_AVAILABLE
        
    def ensure_initialized(self):
        """Ensure the system is initialized"""
        if not self._initialized:
            logger.info("🔄 Initializing Simple RAG system...")
            self._initialize_embedder()
            self._initialize_metta()
            self._initialized = True
    
    def _format_content_for_developers(self, content: str, metadata: dict = None, max_length: int = None) -> str:
        """Format content to be developer-friendly and readable"""
        if not content:
            return "No content available."
        
        # Clean up the content
        lines = content.split('\n')
        formatted_lines = []
        
        # Track if we're in a code block
        in_code_block = False
        code_block_language = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if not in_code_block:
                    formatted_lines.append("")
                continue
            
            # Handle code blocks
            if line.startswith('```'):
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    code_block_language = line[3:].strip()
                    formatted_lines.append(f"```{code_block_language}")
                else:
                    # Ending a code block
                    in_code_block = False
                    formatted_lines.append("```")
                continue
            
            if in_code_block:
                # Inside code block - preserve formatting
                formatted_lines.append(line)
                continue
            
            # Handle headers
            if line.startswith('#'):
                # Convert to proper markdown headers
                level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('# ').strip()
                formatted_lines.append(f"{'#' * level} {header_text}")
                continue
            
            # Handle lists
            if line.startswith('- ') or line.startswith('* '):
                formatted_lines.append(f"• {line[2:]}")
                continue
            
            # Handle numbered lists
            if line and line[0].isdigit() and '. ' in line:
                formatted_lines.append(f"**{line}**")
                continue
            
            # Handle API endpoints and code-like content
            if any(keyword in line.lower() for keyword in ['api', 'endpoint', 'curl', 'http', 'post', 'get', 'put', 'delete']):
                if line.startswith('curl') or 'http' in line.lower():
                    formatted_lines.append(f"```bash")
                    formatted_lines.append(line)
                    formatted_lines.append("```")
                else:
                    formatted_lines.append(f"`{line}`")
                continue
            
            # Handle key-value pairs
            if ':' in line and not line.startswith('http'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    formatted_lines.append(f"**{key}**: {value}")
                    continue
            
            # Regular text
            formatted_lines.append(line)
        
        # Join all lines
        formatted_content = '\n'.join(formatted_lines)
        
        # Apply length limit if specified
        if max_length and len(formatted_content) > max_length:
            formatted_content = formatted_content[:max_length] + "..."
        
        return formatted_content
    
    def _initialize_embedder(self):
        """Initialize BGE embedder"""
        try:
            from bge_embedder import BGEEmbedder
            self.embedder = BGEEmbedder()
            logger.info("✅ BGE embedder initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize BGE embedder: {e}")
            raise
    
    def _initialize_metta(self):
        """Initialize MeTTa knowledge base"""
        if self.metta_enabled:
            try:
                self.metta_kb = MeTTaKnowledgeBase()
                # Load atoms from file if it exists
                atoms_file = "../api_facts.metta"
                if os.path.exists(atoms_file):
                    self.metta_kb.load_atoms_from_file(atoms_file)
                    logger.info("✅ MeTTa knowledge base initialized with atoms")
                else:
                    # Try alternative path
                    atoms_file = "api_facts.metta"
                    if os.path.exists(atoms_file):
                        self.metta_kb.load_atoms_from_file(atoms_file)
                        logger.info("✅ MeTTa knowledge base initialized with atoms")
                    else:
                        logger.warning("⚠️  MeTTa atoms file not found, running without MeTTa reasoning")
                        self.metta_enabled = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize MeTTa: {e}")
                self.metta_enabled = False
        else:
            logger.info("ℹ️  MeTTa integration disabled")
    
    def _get_metta_reasoning(self, question: str) -> Optional[str]:
        """Get MeTTa reasoning for the question"""
        if not self.metta_enabled or not self.metta_kb:
            return None
        
        try:
            # Query MeTTa for relevant patterns
            patterns = self.metta_kb.query_advanced_patterns(question)
            
            if not patterns:
                return None
            
            reasoning_parts = []
            reasoning_parts.append("Based on MeTTa knowledge base analysis:")
            
            for pattern in patterns[:3]:  # Limit to top 3 patterns
                if pattern.get('category') == 'security':
                    reasoning_parts.append(f"• Security pattern: {pattern.get('pattern', 'N/A')}")
                elif pattern.get('type') == 'performance':
                    reasoning_parts.append(f"• Performance pattern: {pattern.get('pattern', 'N/A')}")
                elif pattern.get('category') == 'monitoring':
                    reasoning_parts.append(f"• Monitoring concept: {pattern.get('concept', 'N/A')}")
            
            return "\n".join(reasoning_parts)
            
        except Exception as e:
            logger.warning(f"MeTTa reasoning failed: {e}")
            return None
    
    def _get_metta_citations(self, question: str) -> List[str]:
        """Get MeTTa atom citations for the question"""
        if not self.metta_enabled or not self.metta_kb:
            return []
        
        try:
            citations = []
            
            # Query for different types of patterns
            if 'error' in question.lower() or 'exception' in question.lower():
                error_codes = self.metta_kb.query_error_codes()
                for error in error_codes[:3]:
                    citations.append(f"Error code {error.get('code', 'N/A')}: {error.get('description', 'N/A')}")
            
            if 'rate' in question.lower() or 'limit' in question.lower():
                rate_limits = self.metta_kb.query_rate_limits()
                for rate in rate_limits[:3]:
                    citations.append(f"Rate limit: {rate.get('limit', 'N/A')} requests per {rate.get('period', 'N/A')}")
            
            if 'endpoint' in question.lower() or 'api' in question.lower():
                endpoints = self.metta_kb.query_endpoints()
                for endpoint in endpoints[:3]:
                    citations.append(f"API endpoint: {endpoint}")
            
            return citations
            
        except Exception as e:
            logger.warning(f"MeTTa citations failed: {e}")
            return []
    
    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Query the RAG system with MeTTa reasoning and citations"""
        try:
            self.ensure_initialized()
            
            # Generate query embedding
            query_embedding = self.embedder.embed_query(question)
            
            # Search for similar documents
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT content, metadata, 
                       embedding <=> %s::vector as distance
                FROM documents 
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, k))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not results:
                return {
                    'answer': '❌ No relevant documents found in the knowledge base.\n\n**Possible solutions:**\n1. Check if documents have been ingested\n2. Verify the database contains documents with embeddings\n3. Try rephrasing your question',
                    'sources': [],
                    'context_used': 0,
                    'source': 'simple_rag',
                    'error': 'No documents found'
                }
            
            # Get MeTTa reasoning if available
            metta_reasoning = self._get_metta_reasoning(question)
            metta_citations = self._get_metta_citations(question)
            
            # Create structured answer from retrieved documents
            answer_parts = []
            sources = []
            
            # Process the most relevant document first
            primary_content, primary_metadata, primary_distance = results[0]
            
            # Add to sources
            sources.append({
                'content': primary_content[:200] + '...' if len(primary_content) > 200 else primary_content,
                'source': primary_metadata.get('filename', 'Unknown') if primary_metadata else 'Unknown',
                'score': 1.0 - primary_distance
            })
            
            # Format the primary answer with better structure
            answer_parts.append("## 📋 Answer")
            answer_parts.append("")
            
            # Add MeTTa reasoning only if insights are found
            if metta_reasoning and "No specific patterns found" not in metta_reasoning:
                answer_parts.append("### 🧠 MeTTa Reasoning")
                answer_parts.append("")
                answer_parts.append(metta_reasoning)
                answer_parts.append("")
            
            # Clean and structure the content
            structured_content = self._format_content_for_developers(primary_content, primary_metadata)
            answer_parts.append(structured_content)
            
            # Add additional context if available
            if len(results) > 1:
                answer_parts.append("\n---\n")
                answer_parts.append("## 📚 Additional Resources")
                answer_parts.append("")
                
                for i, (content, metadata, distance) in enumerate(results[1:], 2):
                    # Add to sources
                    sources.append({
                        'content': content[:200] + '...' if len(content) > 200 else content,
                        'source': metadata.get('filename', 'Unknown') if metadata else 'Unknown',
                        'score': 1.0 - distance
                    })
                    
                    # Add structured additional context with clickable links
                    filename = metadata.get('filename', 'Document') if metadata else 'Source'
                    doc_link = f"/documentation#{filename.replace('.md', '').lower()}"
                    answer_parts.append(f"### 📄 [{filename}]({doc_link})")
                    answer_parts.append("")
                    
                    # Format additional content
                    additional_content = self._format_content_for_developers(content, metadata, max_length=300)
                    answer_parts.append(additional_content)
                    answer_parts.append("")
            
            # Add citations section - always present
            answer_parts.append("\n---\n")
            answer_parts.append("## 📖 Citations")
            answer_parts.append("")
            
            # Add document citations - always present
            if sources:
                answer_parts.append("### 📚 Document Sources")
                answer_parts.append("")
                for i, source in enumerate(sources, 1):
                    filename = source['source']
                    score = source['score']
                    # Create clickable link to documentation page
                    doc_link = f"/documentation#{filename.replace('.md', '').lower()}"
                    answer_parts.append(f"**[{i}]** [{filename}]({doc_link}) (relevance: {score:.2f})")
            else:
                answer_parts.append("### 📚 Document Sources")
                answer_parts.append("")
                answer_parts.append("No specific document sources found for this query.")
            
            # Add MeTTa citations - always present when MeTTa is enabled
            if self.metta_enabled and metta_citations:
                answer_parts.append("")
                answer_parts.append("### 🧠 MeTTa Atom Citations")
                answer_parts.append("")
                for citation in metta_citations:
                    # Make MeTTa citations clickable to relevant sections
                    if "Error code" in citation:
                        answer_parts.append(f"• [{citation}](/documentation#error-codes)")
                    elif "Rate limit" in citation:
                        answer_parts.append(f"• [{citation}](/documentation#rate-limits)")
                    elif "API endpoint" in citation:
                        answer_parts.append(f"• [{citation}](/documentation#api-reference)")
                    else:
                        answer_parts.append(f"• {citation}")
            elif self.metta_enabled:
                # Show MeTTa section even when no citations found
                answer_parts.append("")
                answer_parts.append("### 🧠 MeTTa Atom Citations")
                answer_parts.append("")
                answer_parts.append("No specific MeTTa patterns matched this query.")
            
            answer = "\n".join(answer_parts)
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': len(results),
                'source': 'simple_rag',
                'model_source': 'bge_embeddings',
                'metta_enabled': self.metta_enabled,
                'metta_citations': metta_citations
            }
            
        except Exception as e:
            logger.error(f"❌ RAG query failed: {e}")
            
            return {
                'answer': f'❌ Sorry, I encountered an error while processing your question: {str(e)}\n\n**Troubleshooting:**\n1. Check if the database is running on port 5532\n2. Verify that documents have been ingested\n3. Ensure the BGE embedder is working correctly\n4. Check the server logs for more detailed error information',
                'sources': [],
                'context_used': 0,
                'source': 'simple_rag',
                'error': str(e)
            }

def test_simple_rag():
    """Test the Simple RAG system"""
    print("🧪 Testing Simple RAG System...")
    
    try:
        rag = SimpleRAG()
        result = rag.query("What is ASI:One?")
        
        if result and 'answer' in result:
            print("✅ Simple RAG system working correctly")
            print(f"📝 Answer preview: {result['answer'][:200]}...")
            print(f"📚 Sources found: {len(result.get('sources', []))}")
            return True
        else:
            print("❌ Simple RAG system test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_simple_rag()
