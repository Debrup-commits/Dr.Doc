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
        
        # Initialize components only if not already done
        logger.info("🔧 Initializing system components...")
        if rag_system is None:
            rag_system = SimpleRAG()
            logger.info("✅ RAG system initialized")
        else:
            logger.info("ℹ️ RAG system already initialized")
        
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
            logger.error("❌ RAG system not initialized at startup!")
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
            rag_result = {
                'answer': f"RAG query encountered an error: {str(e)}",
                'sources': [],
                'context_used': 0,
                'source': 'simple_rag',
                'error': str(e)
            }
        
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
                reasoning += "Based on symbolic reasoning from the MeTTa knowledge base:\n\n"
                
                # Group patterns by category for better organization
                security_patterns = [p for p in patterns if p.get('category') == 'security']
                api_patterns = [p for p in patterns if p.get('type') == 'api']
                performance_patterns = [p for p in patterns if p.get('type') == 'performance']
                monitoring_patterns = [p for p in patterns if p.get('category') == 'monitoring']
                
                pattern_count = 0
                
                if security_patterns:
                    reasoning += "### 🔐 Security Patterns\n"
                    for pattern in security_patterns[:3]:
                        pattern_count += 1
                        reasoning += f"**{pattern_count}. {pattern.get('pattern', 'Security Pattern')}**\n"
                        reasoning += f"   - {pattern.get('description', 'Security-related pattern')}\n\n"
                
                if api_patterns:
                    reasoning += "### 🌐 API Patterns\n"
                    for pattern in api_patterns[:3]:
                        pattern_count += 1
                        reasoning += f"**{pattern_count}. {pattern.get('pattern', 'API Pattern')}**\n"
                        reasoning += f"   - {pattern.get('description', 'API design pattern')}\n\n"
                
                if performance_patterns:
                    reasoning += "### ⚡ Performance Patterns\n"
                    for pattern in performance_patterns[:3]:
                        pattern_count += 1
                        reasoning += f"**{pattern_count}. {pattern.get('pattern', 'Performance Pattern')}**\n"
                        reasoning += f"   - {pattern.get('description', 'Performance optimization pattern')}\n\n"
                
                if monitoring_patterns:
                    reasoning += "### 📊 Monitoring Concepts\n"
                    for pattern in monitoring_patterns[:3]:
                        pattern_count += 1
                        reasoning += f"**{pattern_count}. {pattern.get('concept', 'Monitoring Concept')}**\n"
                        reasoning += f"   - {pattern.get('description', 'Monitoring and observability concept')}\n\n"
                
                # Add summary
                reasoning += f"\n**Total MeTTa patterns analyzed:** {len(patterns)}\n"
                reasoning += "These patterns provide structured insights from the symbolic knowledge base.\n\n"
                
                return reasoning
            else:
                return "## 🧠 MeTTa Symbolic Analysis\n\nNo specific patterns found in the knowledge base for this query, but the symbolic reasoning framework is active."
        else:
            return "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa symbolic reasoning is not enabled in this system."
    except Exception as e:
        logger.warning(f"⚠️ MeTTa reasoning failed: {e}")
        return "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa knowledge base query encountered an error, but the system is still functional."

async def generate_asi_one_response(question: str, rag_result: dict, metta_reasoning: str) -> str:
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
        
        # Prepare enhanced system prompt for ASI:One Mini
        system_prompt = """You are Dr.Doc Agent, a friendly and helpful AI assistant for developers, powered by ASI:One Mini with RAG integration.

PERSONALITY & TONE:
- Be warm, friendly, and approachable
- Start technical responses with a soft intro like "Here's what you need to know 👇" or "Let me break this down for you 🔧"
- Use emojis sparingly to highlight sections (🔧 for technical details, 📜 for code examples, 🚀 for getting started)
- Be encouraging and supportive
- Keep responses developer-focused but accessible

CRITICAL REQUIREMENTS:
1. Use the RAG context to generate your response based on retrieved documents
2. If MeTTa symbolic reasoning is provided, use the SPECIFIC patterns and atoms mentioned - do not generate generic advice
3. The MeTTa reasoning contains specific authentication methods, endpoints, and patterns from the knowledge base
4. Use these specific patterns (like ip-whitelisting, api-key, request-signing, model endpoint, etc.) in your response
5. DO NOT provide generic security advice - use the actual patterns provided in the MeTTa reasoning
6. Structure your response with clear headers, lists, and code blocks
7. Be thorough but concise
8. Make complex topics approachable for developers

CITATION REQUIREMENTS:
- Your response will automatically include citations to document sources and MeTTa patterns below
- Do not include any citation sections, reference sections, or "Sources:" sections in your response text
- Do not include "## Citations" or "## References" or similar sections
- Focus on providing the main answer content only
- Citations will be automatically appended to your response

Your response should be informative and helpful based on the available context, using the specific patterns provided in MeTTa reasoning when available."""

        # Build the comprehensive prompt with conditional MeTTa reasoning
        user_prompt = f"""Question: {question}

=== RAG CONTEXT (Document Retrieval) ===
{rag_result.get('answer', '')}"""

        # Only include MeTTa reasoning if insights were found
        if metta_reasoning and "No specific patterns found" not in metta_reasoning:
            user_prompt += f"""

=== METTA REASONING (Symbolic Analysis) ===
{metta_reasoning}"""

        user_prompt += """

=== INSTRUCTIONS ===
Please provide a comprehensive answer that:
1. Uses information from the RAG context (retrieved documents)
2. If MeTTa symbolic reasoning is provided above, use the SPECIFIC patterns mentioned (like ip-whitelisting, api-key, request-signing, model endpoint, etc.)
3. DO NOT generate generic security advice - use the actual authentication methods and endpoints listed in the MeTTa reasoning
4. Provides structured, developer-friendly documentation
5. Focuses on being helpful and informative using the specific patterns provided

Your response will automatically include citations to sources and MeTTa patterns below."""
        
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
        
        answer = response.choices[0].message.content
        
        # Initialize full_response with the LLM answer
        full_response = answer
        
        # Check if RAG result already contains citations
        rag_answer = rag_result.get('answer', '')
        has_existing_citations = '📖 Citations' in rag_answer
        
        # Debug logging
        logger.info(f"🔍 Debug: RAG answer length: {len(rag_answer)}")
        logger.info(f"🔍 Debug: Has existing citations: {has_existing_citations}")
        if has_existing_citations:
            logger.info("🔍 Debug: Citations found in RAG answer")
        else:
            logger.info("🔍 Debug: No citations found in RAG answer")
            logger.info(f"🔍 Debug: RAG answer preview: {rag_answer[:200]}...")
        
        if has_existing_citations:
            # RAG already includes citations, append them to the LLM response
            citations = _extract_citations_from_rag(rag_answer)
            full_response = answer + "\n\n" + citations
            logger.info("✅ Using citations from RAG response")
        else:
            # Add citations to the response if not already present
            citation_sections = []
            
            # Always add document citations if available
            if 'sources' in rag_result and rag_result['sources']:
                citation_sections.append("\n---\n## 📖 Citations\n")
                citation_sections.append("### 📚 Document Sources\n")
                for i, source in enumerate(rag_result['sources'], 1):
                    filename = source['source']
                    score = source['score']
                    doc_link = f"/documentation#{filename.replace('.md', '').lower()}"
                    citation_sections.append(f"**[{i}]** [{filename}]({doc_link}) (relevance: {score:.2f})")
            else:
                citation_sections.append("\n---\n## 📖 Citations\n")
                citation_sections.append("### 📚 Document Sources\n")
                citation_sections.append("No specific document sources found for this query.")
            
            # Add MeTTa citations if available and reasoning was provided
            if metta_reasoning and "No specific patterns found" not in metta_reasoning:
                citation_sections.append("\n### 🧠 MeTTa Atom Citations\n")
                # Extract MeTTa citations from the reasoning
                metta_citations = _extract_metta_citations(metta_reasoning)
                if metta_citations:
                    for citation in metta_citations:
                        if "Error code" in citation:
                            citation_sections.append(f"• [{citation}](/documentation#error-codes)")
                        elif "Rate limit" in citation:
                            citation_sections.append(f"• [{citation}](/documentation#rate-limits)")
                        elif "API endpoint" in citation:
                            citation_sections.append(f"• [{citation}](/documentation#api-reference)")
                        else:
                            citation_sections.append(f"• {citation}")
                else:
                    citation_sections.append("No specific MeTTa patterns matched this query.")
            
            # Combine answer with citations
            full_response = answer + "\n".join(citation_sections)
            logger.info("✅ Added citations to agent response")
        
        logger.info("✅ Question processed successfully with both RAG and MeTTa")
        logger.info(f"🔍 Final Debug: full_response length: {len(full_response)}")
        logger.info(f"🔍 Final Debug: full_response has citations: {'📖 Citations' in full_response}")
        
        return full_response
        
    except Exception as e:
        logger.error(f"❌ ASI:One Mini call failed: {e}")
        return f"❌ Failed to generate response with ASI:One Mini: {str(e)}"

def _extract_citations_from_rag(rag_answer: str) -> str:
    """Extract citations section from RAG answer"""
    lines = rag_answer.split('\n')
    citation_start = -1
    
    # Find the start of citations section
    for i, line in enumerate(lines):
        if '📖 Citations' in line:
            citation_start = i
            break
    
    if citation_start >= 0:
        # Extract everything from citations section to the end
        citation_lines = lines[citation_start:]
        return '\n'.join(citation_lines)
    
    return ""

def _extract_metta_citations(metta_reasoning: str) -> list:
    """Extract MeTTa citations from reasoning text"""
    citations = []
    lines = metta_reasoning.split('\n')
    
    for line in lines:
        # Look for pattern references in the format: **{pattern_count}. {pattern_name}**
        if '**' in line and ('Security Pattern' in line or 'API Pattern' in line or 'Performance Pattern' in line or 'Monitoring Concept' in line):
            # Extract the pattern/concept name
            parts = line.split('**')
            if len(parts) >= 2:
                pattern_name = parts[1].strip()
                # Remove numbering and clean up the pattern name
                pattern_name = pattern_name.split('. ', 1)[-1] if '. ' in pattern_name else pattern_name
                if pattern_name and pattern_name not in ['1.', '2.', '3.', '4.', '5.'] and len(pattern_name) > 1:
                    citations.append(f"MeTTa Pattern: {pattern_name}")
    
    return citations[:3]  # Return top 3 citations

if __name__ == "__main__":
    logger.info("🚀 Starting Clean Dr.Doc MCP Server...")
    logger.info("📋 Available endpoints:")
    logger.info("   1. process_documents(docs_dir_path) - Idempotent document processing")
    logger.info("   2. ask_dr_doc(question, session_id) - ASI:One agent for document Q&A")
    
    mcp.run(transport='stdio')
