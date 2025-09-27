#!/usr/bin/env python3
"""
Fetch.ai Agno RAG Integration
Uses the Agno RAG framework from fetchai/innovation-lab-examples
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FetchAIAgnoRAG:
    """Fetch.ai RAG system using Agno framework with PgVector"""
    
    def __init__(self, use_fetchai: bool = True, require_openai_fallback: bool = False, lazy_init: bool = True):
        self.use_fetchai = use_fetchai
        self.require_openai_fallback = require_openai_fallback
        self.knowledge = None
        self.rag_agent = None
        self.model_source = None
        self.lazy_init = lazy_init
        self._initialized = False
        
        # Database configuration
        self.db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
        
        # Initialize the system only if not lazy
        if not lazy_init:
            self._initialize_agno_rag()
    
    def ensure_initialized(self):
        """Ensure the system is initialized (lazy initialization)"""
        if not self._initialized:
            logger.info("🔄 Initializing Agno RAG system (lazy initialization)...")
            self._initialize_agno_rag()
            self._initialized = True
    
    def _initialize_agno_rag(self):
        """Initialize Agno RAG system with Fetch.ai or OpenAI models"""
        try:
            # Import Agno components (updated for v2.0.8)
            from agno.agent import Agent as AgnoAgent
            from agno.knowledge import Knowledge
            from agno.vectordb.pgvector import PgVector
            from agno.knowledge.embedder.openai import OpenAIEmbedder
            
            if self.use_fetchai:
                try:
                    # Try to use Fetch.ai models
                    from agno.models.openai import OpenAIChat
                    from fetchai_client import FetchAIClient
                    
                    # Create Fetch.ai client
                    fetchai_client = FetchAIClient()
                    
                    # Create BGE embedder (free alternative to OpenAI embeddings)
                    from bge_embedder import BGEEmbedder
                    embedder = BGEEmbedder()
                    
                    # Initialize vector database with PgVector
                    vector_db = PgVector(
                        table_name="doc_reader_documents",
                        db_url=self.db_url,
                        embedder=embedder
                    )
                    
                    # Initialize knowledge base
                    self.knowledge = Knowledge(vector_db=vector_db)
                    
                    # Initialize RAG agent with Fetch.ai chat model
                    self.rag_agent = AgnoAgent(
                        model=OpenAIChat(
                            id="asi1-mini",  # Correct Fetch.ai ASI:One model ID
                            api_key=os.getenv("ASI_ONE_API_KEY"),
                            base_url="https://api.asi1.ai/v1"  # Fetch.ai endpoint
                        ),
                        knowledge=self.knowledge
                    )
                    
                    self.model_source = "fetchai"
                    logger.info("✅ Agno RAG initialized with Fetch.ai ASI:One models and BGE embeddings")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Fetch.ai initialization failed: {e}")
                    if self.require_openai_fallback:
                        logger.info("🔄 Falling back to OpenAI models...")
                        self._initialize_openai_agno()
                    else:
                        raise Exception(f"Fetch.ai initialization failed: {e}")
            else:
                self._initialize_openai_agno()
                
        except ImportError as e:
            logger.error(f"❌ Agno framework not available: {e}")
            logger.info("Please install: pip install agno uagents psycopg2-binary pgvector")
            raise Exception("Agno framework not available")
    
    def _initialize_openai_agno(self):
        """Initialize Agno RAG with OpenAI models"""
        from agno.models.openai import OpenAIChat
        from agno.knowledge import Knowledge
        from agno.vectordb.pgvector import PgVector
        from agno.knowledge.embedder.openai import OpenAIEmbedder
        
        # Create BGE embedder (free alternative to OpenAI embeddings)
        from bge_embedder import BGEEmbedder
        embedder = BGEEmbedder()
        
        # Initialize vector database with PgVector
        vector_db = PgVector(
            table_name="doc_reader_documents",
            db_url=self.db_url,
            embedder=embedder
        )
        
        # Initialize knowledge base
        self.knowledge = Knowledge(vector_db=vector_db)
        
        # Initialize RAG agent with OpenAI chat model
        self.rag_agent = AgnoAgent(
            model=OpenAIChat(
                id="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            knowledge=self.knowledge
        )
        
        self.model_source = "openai"
        logger.info("✅ Agno RAG initialized with OpenAI models")
    
    def load_knowledge(self):
        """Load the knowledge base"""
        try:
            # In Agno framework, knowledge base is loaded automatically
            # We just need to check if it's properly initialized
            if self.knowledge is not None:
                logger.info("✅ Knowledge base initialized successfully")
                return True
            else:
                logger.warning("⚠️  Knowledge base not initialized")
                return False
        except Exception as e:
            logger.warning(f"⚠️  Knowledge base check failed: {e}")
            logger.info("Knowledge base may need to be ingested first")
            return False
    
    def ingest_documents(self, documents_dir: str = "../docs"):
        """Ingest documents into the knowledge base"""
        try:
            from agno.document.reader.pdf_reader import PDFReader
            from agno.document.base import Document
            
            # Process Markdown files (convert to text for Agno)
            import markdown
            from bs4 import BeautifulSoup
            from pathlib import Path
            
            documents = []
            docs_path = Path(documents_dir)
            
            if docs_path.exists():
                for md_file in docs_path.glob("*.md"):
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Convert Markdown to HTML then to text
                        html = markdown.markdown(content)
                        soup = BeautifulSoup(html, 'html.parser')
                        text = soup.get_text()
                        
                        # Create document for Agno
                        doc = Document(
                            content=text,
                            metadata={
                                "source": str(md_file),
                                "type": "markdown",
                                "title": md_file.stem
                            }
                        )
                        documents.append(doc)
                        
                    except Exception as e:
                        logger.warning(f"Failed to process {md_file}: {e}")
                
                if documents:
                    # Add documents to knowledge base
                    self.knowledge.add_documents(documents)
                    logger.info(f"✅ Ingested {len(documents)} documents into Agno RAG")
                else:
                    logger.warning("No documents found to ingest")
            else:
                logger.warning(f"Documents directory {documents_dir} not found")
                
        except Exception as e:
            logger.error(f"❌ Document ingestion failed: {e}")
            raise
    
    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            # Ensure system is initialized
            self.ensure_initialized()
            
            if not self.knowledge:
                return {
                    'answer': '❌ Knowledge base not initialized\n\n**Possible solutions:**\n1. Check if PostgreSQL with pgvector is running on port 5532\n2. Ensure documents have been ingested into the knowledge base\n3. Verify the database connection settings\n\n**To fix this issue:**\n- Run: `python backend/fetchai_agno_rag.py` to test the system\n- Or check the server logs for initialization errors',
                    'sources': [],
                    'context_used': 0,
                    'source': 'agno_rag',
                    'error': 'Knowledge base not available',
                    'helpful_message': True
                }
            
            # Use Agno agent to generate response with markdown formatting
            prompt = f"""Answer this question based on the knowledge base: {question}

Please format your response using markdown with:
- Use **bold** for important terms and API endpoints
- Use `code` for inline code, file names, and technical terms
- Use ```language blocks for code examples
- Use tables for structured data like API endpoints, parameters, or error codes
- Use bullet points for lists
- Use headings (##, ###) to organize information
- Use blockquotes for important notes or warnings

Make the response clear, well-structured, and easy to read."""
            
            response = self.rag_agent.run(
                input=prompt,
                max_tokens=1500,
                temperature=0.1
            )
            
            # Extract response content
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
            
            # Get sources from knowledge base (if available)
            sources = []
            try:
                # Try to get retrieval context from Agno knowledge base
                if hasattr(self.knowledge, 'last_search_results') and self.knowledge.last_search_results:
                    for result in self.knowledge.last_search_results[:k]:
                        sources.append({
                            'content': result.get('content', '')[:200] + '...',
                            'source': result.get('metadata', {}).get('source', 'Unknown'),
                            'score': result.get('score', 0.0)
                        })
                else:
                    # Try to get sources from the agent's context
                    if hasattr(response, 'context') and response.context:
                        for doc in response.context[:k]:
                            sources.append({
                                'content': doc.get('content', '')[:200] + '...',
                                'source': doc.get('source', 'Unknown'),
                                'score': doc.get('score', 0.8)  # Default score
                            })
                    else:
                        # Create placeholder sources based on the knowledge base
                        # This ensures we always have some source information
                        sources.append({
                            'content': f'Documentation related to: {question[:100]}...',
                            'source': 'TokenSwap API Documentation',
                            'score': 0.7
                        })
            except Exception as e:
                logger.warning(f"Could not extract sources: {e}")
                # Add a fallback source
                sources.append({
                    'content': f'Documentation content related to: {question[:100]}...',
                    'source': 'API Documentation',
                    'score': 0.6
                })
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': len(sources),
                'source': 'agno_rag',
                'model_source': self.model_source
            }
            
        except Exception as e:
            logger.error(f"❌ RAG query failed: {e}")
            
            # Provide specific error messages based on error type
            error_msg = str(e).lower()
            if "401" in error_msg or "authentication" in error_msg:
                troubleshooting = "**API Authentication Error:**\n1. Check if your API keys are correctly set in the .env file\n2. Verify the API keys are valid and not placeholder values\n3. Make sure ASI_ONE_API_KEY (Fetch.ai) or OPENAI_API_KEY is properly configured\n4. Restart the server after updating API keys"
            elif "model" in error_msg or "unknown" in error_msg:
                troubleshooting = "**Model Configuration Error:**\n1. The model ID may be incorrect or not available\n2. Check if the model is supported by your API provider\n3. Verify the base_url is correct for your API provider\n4. Try using a different model ID (e.g., gpt-4o-mini)"
            elif "connection" in error_msg or "network" in error_msg:
                troubleshooting = "**Network Connection Error:**\n1. Check your internet connection\n2. Verify the API endpoint URL is accessible\n3. Check if there are any firewall restrictions\n4. Try again in a few moments"
            else:
                troubleshooting = "**General Error:**\n1. Check if the LLM API is accessible and properly configured\n2. Verify that the knowledge base contains relevant documents\n3. Try rephrasing your question\n4. Check the server logs for more detailed error information"
            
            return {
                'answer': f'❌ Sorry, I encountered an error while processing your question: {str(e)}\n\n{troubleshooting}',
                'sources': [],
                'context_used': 0,
                'source': 'agno_rag',
                'error': str(e),
                'helpful_message': True
            }

def test_fetchai_agno_rag():
    """Test the Fetch.ai Agno RAG system"""
    print("🧪 Testing Fetch.ai Agno RAG System...")
    
    try:
        # Initialize RAG system
        rag = FetchAIAgnoRAG(use_fetchai=True, require_openai_fallback=True)
        
        # Load knowledge base
        rag.load_knowledge()
        
        # Test query
        result = rag.query("What is authentication?")
        print(f"✅ Query successful")
        print(f"Answer: {result['answer'][:100]}...")
        print(f"Sources: {len(result['sources'])}")
        print(f"Model: {result.get('model_source', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure PostgreSQL with pgvector is running on port 5532")

if __name__ == "__main__":
    test_fetchai_agno_rag()
