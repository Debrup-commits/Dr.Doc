#!/usr/bin/env python3
"""
Intelligent Document Q&A uAgent
Integrates MeTTa knowledge base and RAG system for autonomous document question answering
Based on Fetch.ai uAgents framework
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our agent interface
from agent_rag_interface import get_agent_interface, QueryType

# Pydantic Models for Agent Communication
class QuestionRequest(Model):
    """Request model for asking questions"""
    question: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[str] = None
    query_type: Optional[str] = "auto"  # "rag", "metta", "hybrid", "auto"

class QuestionResponse(Model):
    """Response model for question answers"""
    answer: str
    sources: List[Dict[str, Any]]
    facts: List[Dict[str, Any]]
    source: str  # 'rag', 'metta', 'hybrid'
    confidence: float
    reasoning: str
    model_source: str
    context_used: int
    metta_details: Dict[str, Any]
    rag_details: Dict[str, Any]
    response_time: float
    success: bool
    error: Optional[str] = None

class HealthCheck(Model):
    """Health check model"""
    status: str
    agent_address: str
    rag_documents_loaded: int
    metta_atoms_loaded: int
    vector_store_ready: bool
    metta_available: bool
    model_source: str
    success: bool
    error: Optional[str] = None

class DocumentIngestionRequest(Model):
    """Request model for document ingestion"""
    docs_dir: str = "../docs"
    force_refresh: bool = False

class DocumentIngestionResponse(Model):
    """Response model for document ingestion"""
    success: bool
    documents_processed: int
    facts_extracted: int
    message: str
    error: Optional[str] = None

# Create the Document Q&A Agent
DOC_QA_AGENT = Agent(
    name="DocumentQAAgent",
    seed=os.getenv("AGENT_SEED", "your-agent-seed-here"),
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Fund the agent if needed
fund_agent_if_low(DOC_QA_AGENT.wallet.address())

# Initialize the RAG interface
rag_interface = None

def initialize_rag_interface():
    """Initialize the RAG interface"""
    global rag_interface
    try:
        rag_interface = get_agent_interface()
        print("✅ RAG interface initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize RAG interface: {e}")
        return False

@DOC_QA_AGENT.on_event("startup")
async def startup(ctx: Context):
    """Initialize the agent on startup"""
    ctx.logger.info("🚀 Document Q&A Agent starting up...")
    
    # Initialize RAG interface
    if initialize_rag_interface():
        ctx.logger.info("✅ Agent fully initialized and ready")
    else:
        ctx.logger.error("❌ Agent initialization failed")

@DOC_QA_AGENT.on_message(model=QuestionRequest, replies=QuestionResponse)
async def handle_question(ctx: Context, sender: str, msg: QuestionRequest):
    """Handle incoming questions"""
    ctx.logger.info(f"📝 Received question from {sender}: {msg.question[:50]}...")
    
    try:
        if not rag_interface:
            await ctx.send(sender, QuestionResponse(
                answer="RAG system not initialized",
                sources=[],
                facts=[],
                source="error",
                confidence=0.0,
                reasoning="System not ready",
                model_source="none",
                context_used=0,
                metta_details={},
                rag_details={},
                response_time=0.0,
                success=False,
                error="RAG system not initialized"
            ))
            return
        
        # Convert query type string to enum
        query_type = QueryType.AUTO
        if msg.query_type:
            if msg.query_type.lower() == "rag":
                query_type = QueryType.RAG
            elif msg.query_type.lower() == "metta":
                query_type = QueryType.METTA
            elif msg.query_type.lower() == "hybrid":
                query_type = QueryType.HYBRID
        
        # Query the RAG interface
        result = rag_interface.query(
            question=msg.question,
            query_type=query_type,
            context=msg.context,
            user_id=msg.user_id
        )
        
        # Prepare response
        response = QuestionResponse(
            answer=result.answer,
            sources=result.sources,
            facts=result.facts,
            source=result.query_type.value,
            confidence=result.confidence,
            reasoning=result.reasoning,
            model_source=result.model_source,
            context_used=len(result.sources),
            metta_details=result.metadata.get('metta_details', {}),
            rag_details=result.metadata.get('rag_details', {}),
            response_time=result.response_time,
            success=True
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Question answered successfully (confidence: {result.confidence:.2f})")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing question: {e}")
        await ctx.send(sender, QuestionResponse(
            answer=f"Error processing question: {str(e)}",
            sources=[],
            facts=[],
            source="error",
            confidence=0.0,
            reasoning="Error occurred",
            model_source="error",
            context_used=0,
            metta_details={},
            rag_details={},
            response_time=0.0,
            success=False,
            error=str(e)
        ))

@DOC_QA_AGENT.on_message(model=HealthCheck, replies=HealthCheck)
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    """Handle health check requests"""
    ctx.logger.info("🏥 Health check requested")
    
    try:
        if not rag_interface:
            await ctx.send(sender, HealthCheck(
                status="error",
                agent_address=str(DOC_QA_AGENT.address),
                rag_documents_loaded=0,
                metta_atoms_loaded=0,
                vector_store_ready=False,
                metta_available=False,
                model_source="none",
                success=False,
                error="RAG system not initialized"
            ))
            return
        
        # Get system status
        status = rag_interface.get_system_status()
        
        # Count documents and atoms
        rag_docs = 0
        metta_atoms = 0
        
        if rag_interface.agno_rag and rag_interface.agno_rag.knowledge:
            # Try to get document count from RAG system
            try:
                # This is a placeholder - actual implementation depends on Agno API
                rag_docs = 1  # Assume at least one document is loaded
            except:
                rag_docs = 0
        
        if rag_interface.metta_kb:
            metta_atoms = len(rag_interface.metta_kb.atoms)
        
        response = HealthCheck(
            status="healthy" if status['initialized'] else "error",
            agent_address=str(DOC_QA_AGENT.address),
            rag_documents_loaded=rag_docs,
            metta_atoms_loaded=metta_atoms,
            vector_store_ready=status.get('rag_knowledge_ready', False),
            metta_available=status.get('metta_available', False),
            model_source=status.get('rag_model_source', 'unknown'),
            success=status['initialized']
        )
        
        await ctx.send(sender, response)
        ctx.logger.info("✅ Health check completed")
        
    except Exception as e:
        ctx.logger.error(f"❌ Health check failed: {e}")
        await ctx.send(sender, HealthCheck(
            status="error",
            agent_address=str(DOC_QA_AGENT.address),
            rag_documents_loaded=0,
            metta_atoms_loaded=0,
            vector_store_ready=False,
            metta_available=False,
            model_source="error",
            success=False,
            error=str(e)
        ))

@DOC_QA_AGENT.on_message(model=DocumentIngestionRequest, replies=DocumentIngestionResponse)
async def handle_document_ingestion(ctx: Context, sender: str, msg: DocumentIngestionRequest):
    """Handle document ingestion requests"""
    ctx.logger.info(f"📚 Document ingestion requested for: {msg.docs_dir}")
    
    try:
        if not rag_interface:
            await ctx.send(sender, DocumentIngestionResponse(
                success=False,
                documents_processed=0,
                facts_extracted=0,
                message="RAG system not initialized",
                error="RAG system not initialized"
            ))
            return
        
        documents_processed = 0
        facts_extracted = 0
        
        # Ingest documents into RAG system
        if rag_interface.ingest_documents(msg.docs_dir):
            documents_processed = 1  # Placeholder - actual count depends on implementation
        
        # Extract MeTTa facts
        if rag_interface.extract_metta_facts(msg.docs_dir):
            facts_extracted = len(rag_interface.metta_kb.atoms) if rag_interface.metta_kb else 0
        
        response = DocumentIngestionResponse(
            success=True,
            documents_processed=documents_processed,
            facts_extracted=facts_extracted,
            message=f"Successfully processed {documents_processed} documents and extracted {facts_extracted} facts"
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"✅ Document ingestion completed: {documents_processed} docs, {facts_extracted} facts")
        
    except Exception as e:
        ctx.logger.error(f"❌ Document ingestion failed: {e}")
        await ctx.send(sender, DocumentIngestionResponse(
            success=False,
            documents_processed=0,
            facts_extracted=0,
            message=f"Document ingestion failed: {str(e)}",
            error=str(e)
        ))

# Additional utility functions for the agent

async def ask_question(question: str, query_type: str = "auto", 
                      context: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to ask a question directly to the agent
    
    Args:
        question: The question to ask
        query_type: Type of query ("rag", "metta", "hybrid", "auto")
        context: Additional context
        user_id: User identifier
        
    Returns:
        Dictionary with the answer and metadata
    """
    if not rag_interface:
        return {
            'answer': 'RAG system not initialized',
            'success': False,
            'error': 'RAG system not initialized'
        }
    
    try:
        # Convert query type string to enum
        query_type_enum = QueryType.AUTO
        if query_type.lower() == "rag":
            query_type_enum = QueryType.RAG
        elif query_type.lower() == "metta":
            query_type_enum = QueryType.METTA
        elif query_type.lower() == "hybrid":
            query_type_enum = QueryType.HYBRID
        
        result = rag_interface.query(
            question=question,
            query_type=query_type_enum,
            context=context,
            user_id=user_id
        )
        
        return {
            'answer': result.answer,
            'sources': result.sources,
            'facts': result.facts,
            'query_type': result.query_type.value,
            'confidence': result.confidence,
            'reasoning': result.reasoning,
            'model_source': result.model_source,
            'response_time': result.response_time,
            'metadata': result.metadata,
            'success': True
        }
        
    except Exception as e:
        return {
            'answer': f'Error processing question: {str(e)}',
            'success': False,
            'error': str(e)
        }

def get_agent_status() -> Dict[str, Any]:
    """Get the current status of the agent and RAG systems"""
    if not rag_interface:
        return {
            'agent_initialized': False,
            'rag_available': False,
            'metta_available': False,
            'error': 'RAG system not initialized'
        }
    
    status = rag_interface.get_system_status()
    status['agent_initialized'] = True
    status['agent_address'] = str(DOC_QA_AGENT.address)
    
    return status

if __name__ == "__main__":
    print("🚀 Starting Document Q&A Agent...")
    print(f"Agent Address: {DOC_QA_AGENT.address}")
    print(f"Agent Endpoint: {DOC_QA_AGENT.endpoint}")
    
    # Initialize RAG interface
    if initialize_rag_interface():
        print("✅ Agent ready to receive questions")
        
        # Run the agent
        DOC_QA_AGENT.run()
    else:
        print("❌ Failed to initialize agent")
        exit(1)