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

# Import our existing components
from app_agno_hybrid import AgnoHybridQASystem
from metta_ingest import MeTTaFactExtractor

# Pydantic Models for Agent Communication
class QuestionRequest(Model):
    """Request model for asking questions"""
    question: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[str] = None

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

class HealthCheck(Model):
    """Health check model"""
    status: str
    agent_address: str
    rag_documents_loaded: int
    metta_atoms_loaded: int
    vector_store_ready: bool
    uptime: float

class ErrorResponse(Model):
    """Error response model"""
    error: str
    error_type: str
    suggestion: str

# Initialize the Document Q&A Agent
SEED_PHRASE = os.getenv("AGENT_SEED_PHRASE", "document_qa_agent_secret_seed_phrase_2024")

# Create the agent with mailbox support for Agentverse integration
agent = Agent(
    name="doc-qa-agent",
    seed=SEED_PHRASE,
    port=8001,
    mailbox=True,
    publish_agent_details=True
)

# Initialize the hybrid QA system
qa_system = None
metta_extractor = None

@agent.on_event("startup")
async def startup_function(ctx: Context):
    """Initialize the agent on startup"""
    global qa_system, metta_extractor
    
    ctx.logger.info(f"🚀 Starting Document Q&A Agent: {agent.name}")
    ctx.logger.info(f"📍 Agent address: {agent.address}")
    
    try:
        # Initialize the hybrid QA system
        ctx.logger.info("🔄 Initializing Hybrid QA System...")
        qa_system = AgnoHybridQASystem()
        ctx.logger.info("✅ Hybrid QA System initialized successfully")
        
        # Initialize MeTTa fact extractor
        ctx.logger.info("🔄 Initializing MeTTa Fact Extractor...")
        metta_extractor = MeTTaFactExtractor()
        ctx.logger.info("✅ MeTTa Fact Extractor initialized successfully")
        
        # Fund the agent if needed (skip for local development)
        try:
            if hasattr(agent, 'wallet') and agent.wallet:
                await fund_agent_if_low(str(agent.wallet.address()))
        except Exception as e:
            ctx.logger.warning(f"⚠️ Agent funding skipped (development mode): {e}")
        
        ctx.logger.info("🎉 Document Q&A Agent is ready to answer questions!")
        ctx.logger.info(f"🔗 Agent inspector: https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8001&address={agent.address}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Failed to initialize agent: {e}")
        raise

@agent.on_message(model=QuestionRequest, replies=QuestionResponse)
async def handle_question(ctx: Context, sender: str, msg: QuestionRequest):
    """Handle incoming question requests"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        ctx.logger.info(f"📝 Received question from {sender}: {msg.question[:100]}...")
        
        if qa_system is None:
            error_response = ErrorResponse(
                error="QA system not initialized",
                error_type="initialization_error",
                suggestion="Please wait for the agent to fully initialize and try again"
            )
            await ctx.send(sender, error_response)
            return
        
        # Process the question using our hybrid QA system
        result = qa_system.query(msg.question)
        
        # Calculate response time
        response_time = asyncio.get_event_loop().time() - start_time
        
        # Create response
        response = QuestionResponse(
            answer=result.get('answer', 'No answer available'),
            sources=result.get('sources', []),
            facts=result.get('facts', []),
            source=result.get('source', 'unknown'),
            confidence=result.get('confidence', 0.0),
            reasoning=result.get('reasoning', 'No reasoning provided'),
            model_source=result.get('model_source', 'unknown'),
            context_used=result.get('context_used', 0),
            metta_details=result.get('metta_details', {}),
            rag_details=result.get('rag_details', {}),
            response_time=response_time
        )
        
        ctx.logger.info(f"✅ Answer generated (confidence: {response.confidence:.2f}, time: {response_time:.2f}s)")
        await ctx.send(sender, response)
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing question: {e}")
        
        error_response = ErrorResponse(
            error=str(e),
            error_type="processing_error",
            suggestion="Please rephrase your question or try again later"
        )
        await ctx.send(sender, error_response)

@agent.on_message(model=HealthCheck, replies=HealthCheck)
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    """Handle health check requests"""
    try:
        # Get system status
        rag_docs = qa_system.agno_rag.knowledge.count() if qa_system and qa_system.agno_rag.knowledge else 0
        metta_atoms = len(metta_extractor.atoms) if metta_extractor else 0
        
        health_response = HealthCheck(
            status="healthy",
            agent_address=str(agent.address),
            rag_documents_loaded=rag_docs,
            metta_atoms_loaded=metta_atoms,
            vector_store_ready=qa_system is not None and qa_system.agno_rag.knowledge is not None,
            uptime=asyncio.get_event_loop().time() - agent.start_time if hasattr(agent, 'start_time') else 0
        )
        
        ctx.logger.info("💚 Health check completed")
        await ctx.send(sender, health_response)
        
    except Exception as e:
        ctx.logger.error(f"❌ Health check failed: {e}")
        
        error_response = HealthCheck(
            status="unhealthy",
            agent_address=str(agent.address),
            rag_documents_loaded=0,
            metta_atoms_loaded=0,
            vector_store_ready=False,
            uptime=0
        )
        await ctx.send(sender, error_response)

@agent.on_interval(period=300.0)  # Every 5 minutes
async def periodic_health_check(ctx: Context):
    """Periodic health monitoring"""
    try:
        if qa_system is None:
            ctx.logger.warning("⚠️ QA system not initialized")
            return
            
        # Check system health
        rag_status = "healthy" if qa_system.agno_rag.knowledge else "unhealthy"
        metta_status = "healthy" if metta_extractor and len(metta_extractor.atoms) > 0 else "unhealthy"
        
        ctx.logger.info(f"📊 System Status - RAG: {rag_status}, MeTTa: {metta_status}")
        
        # Log current statistics
        if qa_system.agno_rag.knowledge:
            doc_count = qa_system.agno_rag.knowledge.count()
            ctx.logger.info(f"📚 Knowledge Base: {doc_count} documents loaded")
        
        if metta_extractor:
            atom_count = len(metta_extractor.atoms)
            ctx.logger.info(f"🧠 MeTTa Knowledge: {atom_count} atoms loaded")
            
    except Exception as e:
        ctx.logger.error(f"❌ Periodic health check failed: {e}")

# Additional message handlers for different types of requests
@agent.on_message(model=ErrorResponse, replies=QuestionResponse)
async def handle_error_recovery(ctx: Context, sender: str, msg: ErrorResponse):
    """Handle error recovery requests"""
    ctx.logger.info(f"🔄 Error recovery requested: {msg.error}")
    
    try:
        # Attempt to reinitialize the system
        global qa_system, metta_extractor
        
        if msg.error_type == "initialization_error":
            ctx.logger.info("🔄 Attempting to reinitialize QA system...")
            qa_system = AgnoHybridQASystem()
            metta_extractor = MeTTaFactExtractor()
            
            recovery_response = QuestionResponse(
                answer="System has been reinitialized successfully. Please try your question again.",
                sources=[],
                facts=[],
                source="system",
                confidence=1.0,
                reasoning="System recovery completed",
                model_source="recovery",
                context_used=0,
                metta_details={"status": "recovered"},
                rag_details={"status": "recovered"},
                response_time=0.0
            )
            
            await ctx.send(sender, recovery_response)
            
    except Exception as e:
        ctx.logger.error(f"❌ Error recovery failed: {e}")

if __name__ == "__main__":
    print("🤖 Starting Intelligent Document Q&A Agent...")
    print(f"📍 Agent will be available at: {agent.address}")
    print("🔗 Agent inspector will be available after startup")
    print("🛑 Press Ctrl+C to stop the agent")
    print("=" * 60)
    
    # Set start time for uptime tracking
    agent.start_time = asyncio.get_event_loop().time()
    
    agent.run()
