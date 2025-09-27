#!/usr/bin/env python3
"""
Dr.Doc MCP Server

A clean MCP server implementation with two core endpoints:
1. process_documents - Idempotent document processing (MeTTa + RAG)
2. ask_dr_doc - ASI:One powered document Q&A agent

Author: Dr.Doc Team
"""

import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# External dependencies
from mcp.server.fastmcp import FastMCP

# Local modules
from simple_rag import SimpleRAG
from metta_ingest import MeTTaFactExtractor, MeTTaKnowledgeBase
from simple_ingest import process_markdown_files, store_documents_in_db, generate_embeddings

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server instance
mcp = FastMCP("dr-doc")

# Global application state
rag_system = None
metta_kb = None
processing_status = {"initialized": False}

@mcp.tool()
async def process_documents(docs_dir_path: str) -> str:
    """
    Idempotent document processing endpoint.
    Creates MeTTa knowledge graphs and RAG pipelines if not already set up.
    
    Args:
        docs_dir_path: Path to the directory containing documents
        
    Returns:
        Status message indicating what was done
    """
    global rag_system, metta_kb, processing_status
    
    try:
        logger.info(f"🔄 Processing documents from: {docs_dir_path}")
        
        # Validate docs directory
        docs_path = Path(docs_dir_path)
        if not docs_path.exists() or not docs_path.is_dir():
            return f"❌ Error: Directory '{docs_dir_path}' does not exist or is not a directory."
        
        # Check if system is already initialized
        if processing_status["initialized"]:
            return "✅ System already initialized. Documents are ready for Q&A."
        
        # Initialize components
        logger.info("🔧 Initializing system components...")
        rag_system = SimpleRAG()
        
        # Step 1: Create MeTTa knowledge graphs
        logger.info("📚 Creating MeTTa knowledge graphs...")
        metta_result = await create_metta_knowledge_base(docs_path)
        
        # Step 2: Create RAG pipelines
        logger.info("🔍 Creating RAG pipelines...")
        rag_result = await create_rag_pipeline(docs_path)
        
        # Update status
        processing_status["initialized"] = True
        
        success_message = f"""
✅ Document Processing Complete!

📁 Processed Directory: {docs_dir_path}
🧠 MeTTa Knowledge Graph: {metta_result}
🔍 RAG Pipeline: {rag_result}

🎯 System Status: Ready for document Q&A queries
        """
        
        logger.info("✅ Document processing completed successfully")
        return success_message.strip()
        
    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        return f"❌ Document processing failed: {str(e)}"

async def create_metta_knowledge_base(docs_path: Path) -> str:
    """Create MeTTa knowledge base from documents"""
    try:
        global metta_kb
        
        # Check if MeTTa file already exists
        metta_file = Path("api_facts.metta")
        if metta_file.exists():
            logger.info("📚 MeTTa knowledge base already exists, loading...")
            metta_kb = MeTTaKnowledgeBase()
            metta_kb.load_atoms_from_file(str(metta_file))
            return "Loaded existing MeTTa knowledge base"
        
        # Create new MeTTa knowledge base
        logger.info("📚 Creating new MeTTa knowledge base...")
        extractor = MeTTaFactExtractor()
        atoms = extractor.extract_all_facts(str(docs_path))
        
        if not atoms:
            return "No MeTTa facts could be extracted from documents"
        
        metta_kb = MeTTaKnowledgeBase()
        metta_kb.load_atoms(atoms)
        metta_kb.save_atoms(str(metta_file))
        
        logger.info(f"💾 Created MeTTa knowledge base with {len(atoms)} facts")
        return f"Created MeTTa knowledge base with {len(atoms)} facts"
        
    except Exception as e:
        logger.error(f"❌ MeTTa knowledge base creation failed: {e}")
        raise e

async def create_rag_pipeline(docs_path: Path) -> str:
    """Create RAG pipeline from documents"""
    try:
        # Check if database already has documents
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
            
            if doc_count > 0:
                logger.info(f"📚 RAG pipeline already exists with {doc_count} documents")
                return f"RAG pipeline already exists with {doc_count} documents"
        except:
            pass
        
        # Create new RAG pipeline
        logger.info("📚 Creating new RAG pipeline...")
        
        # Process documents
        documents = process_markdown_files(str(docs_path))
        if not documents:
            return "No documents found for RAG processing"
        
        # Store in database
        if not store_documents_in_db(documents):
            return "Failed to store documents in database"
        
        # Generate embeddings
        if not generate_embeddings():
            return "Failed to generate embeddings"
        
        logger.info(f"💾 Created RAG pipeline with {len(documents)} documents")
        return f"Created RAG pipeline with {len(documents)} documents"
        
    except Exception as e:
        logger.error(f"❌ RAG pipeline creation failed: {e}")
        raise e

@mcp.tool()
async def ask_dr_doc(question: str, session_id: Optional[str] = None) -> str:
    """
    Ask questions to the Dr.Doc agent about processed documents.
    Uses ASI:One Mini with RAG and MeTTa integration.
    
    Args:
        question: The question to ask about the documents
        session_id: Optional session ID for conversation tracking
        
    Returns:
        Comprehensive answer combining RAG context and MeTTa reasoning
    """
    global rag_system, metta_kb, processing_status
    
    try:
        logger.info(f"🤖 Dr.Doc Agent received question: {question[:100]}...")
        
        # RAG system should be initialized at server startup
        if rag_system is None:
            return """
❌ RAG system not initialized!

The RAG system should be initialized at server startup. Please restart the server.
            """.strip()
        
        # Step 1: Get RAG context
        logger.info("🔍 Querying RAG pipeline...")
        try:
            rag_result = rag_system.query(question)
            logger.info("✅ RAG query completed")
        except Exception as e:
            logger.warning(f"⚠️ RAG query failed: {e}")
            rag_result = f"RAG query encountered an error: {str(e)}"
        
        # Step 2: Get MeTTa reasoning
        logger.info("🧠 Querying MeTTa knowledge base...")
        metta_reasoning = await get_metta_reasoning(question)
        
        # Step 3: Generate response with ASI:One Mini
        logger.info("🤖 Generating response with ASI:One Mini...")
        answer = await generate_asi_one_response(question, rag_result, metta_reasoning)
        
        logger.info("✅ Dr.Doc response generated successfully")
        return answer
        
    except Exception as e:
        logger.error(f"❌ Dr.Doc Agent query failed: {e}")
        return f"❌ Dr.Doc Agent query failed: {str(e)}"

async def get_metta_reasoning(question: str) -> str:
    """Get MeTTa symbolic reasoning for the question"""
    global metta_kb
    
    try:
        if metta_kb:
            patterns = metta_kb.query_advanced_patterns(question)
            if patterns:
                reasoning = "## 🧠 MeTTa Symbolic Analysis\n\n"
                reasoning += "Based on symbolic reasoning from the knowledge base:\n\n"
                
                for i, pattern in enumerate(patterns[:5], 1):
                    if pattern.get('category') == 'security':
                        reasoning += f"**{i}. Security Pattern:** {pattern.get('pattern', 'N/A')}\n"
                        reasoning += f"   - Description: {pattern.get('description', 'Security-related pattern')}\n\n"
                    elif pattern.get('type') == 'performance':
                        reasoning += f"**{i}. Performance Pattern:** {pattern.get('pattern', 'N/A')}\n"
                        reasoning += f"   - Description: {pattern.get('description', 'Performance optimization pattern')}\n\n"
                    elif pattern.get('category') == 'monitoring':
                        reasoning += f"**{i}. Monitoring Concept:** {pattern.get('concept', 'N/A')}\n"
                        reasoning += f"   - Description: {pattern.get('description', 'Monitoring and observability concept')}\n\n"
                    elif pattern.get('type') == 'api':
                        reasoning += f"**{i}. API Pattern:** {pattern.get('pattern', 'N/A')}\n"
                        reasoning += f"   - Description: {pattern.get('description', 'API design pattern')}\n\n"
                
                return reasoning
            else:
                return "## 🧠 MeTTa Symbolic Analysis\n\nNo specific patterns found in the knowledge base for this query, but the symbolic reasoning framework is active."
        else:
            return "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa symbolic reasoning is not enabled in this system."
    except Exception as e:
        logger.warning(f"⚠️ MeTTa reasoning failed: {e}")
        return "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa knowledge base query encountered an error, but the system is still functional."

async def generate_asi_one_response(question: str, rag_context: str, metta_reasoning: str) -> str:
    """Generate response using ASI:One Mini"""
    try:
        from openai import OpenAI
        
        # Initialize ASI:One client
        api_key = os.getenv("ASI_ONE_API_KEY")
        if not api_key:
            return "❌ Error: ASI_ONE_API_KEY environment variable not set"
        
        # Create OpenAI client with explicit configuration
        # Fix httpx compatibility issue where 'proxies' is passed instead of 'proxy'
        import httpx
        
        # Monkey patch httpx.Client to handle proxies parameter correctly
        original_httpx_init = httpx.Client.__init__
        
        def fixed_httpx_init(self, **kwargs):
            # Convert 'proxies' to 'proxy' if present
            if 'proxies' in kwargs and 'proxy' not in kwargs:
                kwargs['proxy'] = kwargs.pop('proxies')
            return original_httpx_init(self, **kwargs)
        
        # Apply the fix
        httpx.Client.__init__ = fixed_httpx_init
        
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.asi1.ai/v1"
            )
        finally:
            # Restore original httpx.Client.__init__
            httpx.Client.__init__ = original_httpx_init
        
        # Prepare system prompt
        system_prompt = """You are Dr.Doc, an AI assistant powered by ASI:One Mini, with integration of both RAG (Retrieval-Augmented Generation) and MeTTa symbolic reasoning systems.

CRITICAL REQUIREMENTS:
1. You MUST use BOTH the RAG context AND MeTTa reasoning to generate your response
2. The RAG context provides factual information from documents
3. The MeTTa reasoning provides symbolic analysis and patterns
4. Combine both sources to create a comprehensive, well-structured answer
5. Always acknowledge both information sources in your response
6. Structure your response with clear headers, lists, and code blocks
7. Provide clickable citations to documentation
8. Be thorough but concise
9. Focus on helping users understand the document contents better

Your response should demonstrate that you've considered both the retrieved documents (RAG) and the symbolic reasoning (MeTTa) in your answer."""

        # Build user prompt
        user_prompt = f"""Question: {question}

=== RAG CONTEXT (Document Retrieval) ===
{rag_context}

=== METTA REASONING (Symbolic Analysis) ===
{metta_reasoning}

=== INSTRUCTIONS ===
Please provide a comprehensive answer that:
1. Uses information from the RAG context (retrieved documents)
2. Incorporates insights from the MeTTa symbolic reasoning
3. Combines both sources to give a complete answer
4. Acknowledges both information sources
5. Provides structured, developer-friendly documentation
6. Includes relevant citations and links

Your response should demonstrate the integration of both RAG and MeTTa pipelines."""
        
        # Call ASI:One Mini
        response = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"❌ ASI:One Mini call failed: {e}")
        return f"❌ Failed to generate response with ASI:One Mini: {str(e)}"

if __name__ == "__main__":
    logger.info("🚀 Starting Clean Dr.Doc MCP Server...")
    logger.info("📋 Available endpoints:")
    logger.info("   1. process_documents(docs_dir_path) - Idempotent document processing")
    logger.info("   2. ask_dr_doc(question, session_id) - ASI:One agent for document Q&A")
    
    mcp.run(transport='stdio')
