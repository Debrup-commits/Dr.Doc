#!/usr/bin/env python3
"""
ASI:One Mini uAgent with MeTTa and RAG integration
Based on Fetch.ai uAgents framework and ASI:One Mini model
Includes HTTP API for frontend communication
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# uAgents imports
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# OpenAI client for ASI:One Mini
from openai import OpenAI

# HTTP server for API endpoints
from aiohttp import web, web_request
import aiohttp_cors

# Local imports
from simple_rag import SimpleRAG

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Message models
class QuestionRequest(Model):
    """Request model for questions"""
    question: str
    session_id: Optional[str] = None

class QuestionResponse(Model):
    """Response model for answers"""
    answer: str
    sources: Optional[list] = None
    metta_reasoning: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

class HealthCheck(Model):
    """Health check model"""
    status: str = "checking"

class HealthResponse(Model):
    """Health response model"""
    status: str
    system: str
    embedder: str
    database: str
    metta_enabled: bool = False

# Initialize ASI:One Mini client
def get_asi_one_client():
    """Initialize ASI:One Mini client"""
    api_key = os.getenv("ASI_ONE_API_KEY")
    if not api_key:
        raise ValueError("ASI_ONE_API_KEY environment variable not set")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.asi1.ai/v1"
    )

# Initialize the agent
SEED_PHRASE = os.getenv("AGENTVERSE_API_KEY")

agent = Agent(
    name="asi_one_rag_agent",
    seed=SEED_PHRASE,
    port=8001,
    mailbox=True
)

# Initialize RAG system
rag_system = SimpleRAG()

@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize the agent on startup"""
    ctx.logger.info(f"🚀 ASI:One RAG Agent starting up...")
    ctx.logger.info(f"📍 Agent address: {agent.address}")
    
    # Initialize RAG system
    rag_system.ensure_initialized()
    ctx.logger.info("✅ RAG system initialized")
    
    # Test ASI:One connection
    try:
        client = get_asi_one_client()
        # Simple test call
        response = client.chat.completions.create(
            model="asi1-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        ctx.logger.info("✅ ASI:One Mini connection successful")
    except Exception as e:
        ctx.logger.error(f"❌ ASI:One Mini connection failed: {e}")
    
    ctx.logger.info("🎯 Agent ready to process questions")

@agent.on_message(model=QuestionRequest, replies=QuestionResponse)
async def handle_question(ctx: Context, sender: str, msg: QuestionRequest):
    """Handle incoming questions with mandatory RAG and MeTTa integration"""
    ctx.logger.info(f"📝 Received question: {msg.question[:100]}...")
    
    try:
        # MANDATORY: Query both RAG and MeTTa pipelines
        ctx.logger.info("🔍 Querying RAG pipeline...")
        rag_result = rag_system.query(msg.question)
        
        ctx.logger.info("🧠 Querying MeTTa knowledge base...")
        metta_reasoning = None
        metta_citations = []
        
        if rag_system.metta_enabled and rag_system.metta_kb:
            try:
                # Query MeTTa for relevant patterns and facts
                patterns = rag_system.metta_kb.query_advanced_patterns(msg.question)
                if patterns:
                    metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\n"
                    metta_reasoning += "Based on symbolic reasoning from the knowledge base:\n\n"
                    
                    for i, pattern in enumerate(patterns[:5], 1):
                        if pattern.get('category') == 'security':
                            metta_reasoning += f"**{i}. Security Pattern:** {pattern.get('pattern', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'Security-related pattern')}\n\n"
                        elif pattern.get('type') == 'performance':
                            metta_reasoning += f"**{i}. Performance Pattern:** {pattern.get('pattern', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'Performance optimization pattern')}\n\n"
                        elif pattern.get('category') == 'monitoring':
                            metta_reasoning += f"**{i}. Monitoring Concept:** {pattern.get('concept', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'Monitoring and observability concept')}\n\n"
                        elif pattern.get('type') == 'api':
                            metta_reasoning += f"**{i}. API Pattern:** {pattern.get('pattern', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'API design pattern')}\n\n"
                    
                    # Add MeTTa citations
                    metta_citations = [f"MeTTa Pattern: {p.get('pattern', 'N/A')}" for p in patterns[:3]]
                else:
                    metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\nNo specific patterns found in the knowledge base for this query, but the symbolic reasoning framework is active."
            except Exception as e:
                ctx.logger.warning(f"MeTTa reasoning failed: {e}")
                metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa knowledge base query encountered an error, but the system is still functional."
        else:
            metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa symbolic reasoning is not enabled in this system."
        
        # Prepare enhanced system prompt for ASI:One Mini
        system_prompt = """You are an AI assistant powered by ASI:One Mini, with MANDATORY integration of both RAG (Retrieval-Augmented Generation) and MeTTa symbolic reasoning systems.

CRITICAL REQUIREMENTS:
1. You MUST use BOTH the RAG context AND MeTTa reasoning to generate your response
2. The RAG context provides factual information from documents
3. The MeTTa reasoning provides symbolic analysis and patterns
4. Combine both sources to create a comprehensive, well-structured answer
5. Always acknowledge both information sources in your response
6. Structure your response with clear headers, lists, and code blocks
7. Provide clickable citations to documentation
8. Be thorough but concise

Your response should demonstrate that you've considered both the retrieved documents (RAG) and the symbolic reasoning (MeTTa) in your answer."""

        # Build the comprehensive prompt with both contexts
        user_prompt = f"""Question: {msg.question}

=== RAG CONTEXT (Document Retrieval) ===
{rag_result}

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
        
        # Call ASI:One Mini with enhanced context
        client = get_asi_one_client()
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
        
        # Extract sources from RAG context
        sources = []
        if isinstance(rag_result, dict) and 'sources' in rag_result:
            sources = rag_result['sources']
        elif "## 📖 Citations" in str(rag_result):
            # Parse sources from the RAG response
            lines = str(rag_result).split('\n')
            in_citations = False
            for line in lines:
                if "## 📖 Citations" in line:
                    in_citations = True
                    continue
                if in_citations and line.startswith('**['):
                    sources.append(line.strip())
                elif in_citations and line.startswith('##'):
                    break
        
        # Send comprehensive response
        await ctx.send(
            sender,
            QuestionResponse(
                answer=answer,
                sources=sources,
                metta_reasoning=metta_reasoning,
                success=True
            )
        )
        
        ctx.logger.info("✅ Question processed successfully with both RAG and MeTTa")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing question: {e}")
        await ctx.send(
            sender,
            QuestionResponse(
                answer="I apologize, but I encountered an error while processing your question. Please try again.",
                success=False,
                error=str(e)
            )
        )

@agent.on_message(model=HealthCheck, replies=HealthResponse)
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    """Handle health check requests"""
    ctx.logger.info("🏥 Health check requested")
    
    try:
        # Check RAG system status
        rag_system.ensure_initialized()
        
        # Check ASI:One connection
        client = get_asi_one_client()
        test_response = client.chat.completions.create(
            model="asi1-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        await ctx.send(
            sender,
            HealthResponse(
                status="healthy",
                system="asi_one_rag_agent",
                embedder="bge",
                database="postgresql_pgvector",
                metta_enabled=rag_system.metta_enabled
            )
        )
        
        ctx.logger.info("✅ Health check passed")
        
    except Exception as e:
        ctx.logger.error(f"❌ Health check failed: {e}")
        await ctx.send(
            sender,
            HealthResponse(
                status="unhealthy",
                system="asi_one_rag_agent",
                embedder="bge",
                database="postgresql_pgvector",
                metta_enabled=rag_system.metta_enabled
            )
        )

# Global variables for HTTP server
app = None
agent_instance = None

async def handle_health_check(request: web_request.Request) -> web.Response:
    """Handle health check requests"""
    try:
        # Check RAG system status
        rag_system.ensure_initialized()
        
        # Check ASI:One connection
        client = get_asi_one_client()
        test_response = client.chat.completions.create(
            model="asi1-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        return web.json_response({
            "status": "healthy",
            "system": "asi_one_rag_agent",
            "embedder": "bge",
            "database": "postgresql_pgvector",
            "metta_enabled": rag_system.metta_enabled
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return web.json_response({
            "status": "unhealthy",
            "error": str(e)
        }, status=503)

async def handle_ask_question(request: web_request.Request) -> web.Response:
    """Handle question requests"""
    try:
        data = await request.json()
        question = data.get('question', '').strip()
        
        if not question:
            return web.json_response({
                "answer": "Please provide a non-empty question.",
                "success": False,
                "error": "Empty question"
            }, status=400)
        
        # Create a mock context for the agent
        class MockContext:
            def __init__(self):
                self.logger = logger
        
        # Use the agent's question handling logic
        mock_ctx = MockContext()
        
        # MANDATORY: Query both RAG and MeTTa pipelines
        logger.info("🔍 Querying RAG pipeline...")
        rag_result = rag_system.query(question)
        
        logger.info("🧠 Querying MeTTa knowledge base...")
        metta_reasoning = None
        metta_citations = []
        
        if rag_system.metta_enabled and rag_system.metta_kb:
            try:
                # Query MeTTa for relevant patterns and facts
                patterns = rag_system.metta_kb.query_advanced_patterns(question)
                if patterns:
                    metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\n"
                    metta_reasoning += "Based on symbolic reasoning from the knowledge base:\n\n"
                    
                    for i, pattern in enumerate(patterns[:5], 1):
                        if pattern.get('category') == 'security':
                            metta_reasoning += f"**{i}. Security Pattern:** {pattern.get('pattern', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'Security-related pattern')}\n\n"
                        elif pattern.get('type') == 'performance':
                            metta_reasoning += f"**{i}. Performance Pattern:** {pattern.get('pattern', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'Performance optimization pattern')}\n\n"
                        elif pattern.get('category') == 'monitoring':
                            metta_reasoning += f"**{i}. Monitoring Concept:** {pattern.get('concept', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'Monitoring and observability concept')}\n\n"
                        elif pattern.get('type') == 'api':
                            metta_reasoning += f"**{i}. API Pattern:** {pattern.get('pattern', 'N/A')}\n"
                            metta_reasoning += f"   - Description: {pattern.get('description', 'API design pattern')}\n\n"
                    
                    # Add MeTTa citations
                    metta_citations = [f"MeTTa Pattern: {p.get('pattern', 'N/A')}" for p in patterns[:3]]
                else:
                    metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\nNo specific patterns found in the knowledge base for this query, but the symbolic reasoning framework is active."
            except Exception as e:
                logger.warning(f"MeTTa reasoning failed: {e}")
                metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa knowledge base query encountered an error, but the system is still functional."
        else:
            metta_reasoning = "## 🧠 MeTTa Symbolic Analysis\n\nMeTTa symbolic reasoning is not enabled in this system."
        
        # Prepare enhanced system prompt for ASI:One Mini
        system_prompt = """You are an AI assistant powered by ASI:One Mini, with MANDATORY integration of both RAG (Retrieval-Augmented Generation) and MeTTa symbolic reasoning systems.

CRITICAL REQUIREMENTS:
1. You MUST use BOTH the RAG context AND MeTTa reasoning to generate your response
2. The RAG context provides factual information from documents
3. The MeTTa reasoning provides symbolic analysis and patterns
4. Combine both sources to create a comprehensive, well-structured answer
5. Always acknowledge both information sources in your response
6. Structure your response with clear headers, lists, and code blocks
7. Provide clickable citations to documentation
8. Be thorough but concise

Your response should demonstrate that you've considered both the retrieved documents (RAG) and the symbolic reasoning (MeTTa) in your answer."""

        # Build the comprehensive prompt with both contexts
        user_prompt = f"""Question: {question}

=== RAG CONTEXT (Document Retrieval) ===
{rag_result}

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
        
        # Call ASI:One Mini with enhanced context
        client = get_asi_one_client()
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
        
        # Extract sources from RAG context
        sources = []
        if isinstance(rag_result, dict) and 'sources' in rag_result:
            sources = rag_result['sources']
        elif "## 📖 Citations" in str(rag_result):
            # Parse sources from the RAG response
            lines = str(rag_result).split('\n')
            in_citations = False
            for line in lines:
                if "## 📖 Citations" in line:
                    in_citations = True
                    continue
                if in_citations and line.startswith('**['):
                    sources.append(line.strip())
                elif in_citations and line.startswith('##'):
                    break
        
        logger.info("✅ Question processed successfully with both RAG and MeTTa")
        
        return web.json_response({
            "answer": answer,
            "sources": sources,
            "metta_reasoning": metta_reasoning,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return web.json_response({
            "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
            "success": False,
            "error": str(e)
        }, status=500)

async def create_http_app():
    """Create the HTTP application with CORS support"""
    global app
    app = web.Application()
    
    # Configure CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get('/api/health', handle_health_check)
    app.router.add_post('/api/ask', handle_ask_question)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

async def start_http_server():
    """Start the HTTP server"""
    app = await create_http_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5003)
    await site.start()
    logger.info("🌐 HTTP API server started on http://0.0.0.0:5003")
    return runner

async def main():
    """Main function to run both uAgent and HTTP server"""
    global agent_instance
    
    # Fund the agent if needed
    fund_agent_if_low(agent.wallet.address())
    
    # Start HTTP server
    http_runner = await start_http_server()
    
    # Start the uAgent in a separate thread
    import threading
    def run_agent():
        agent.run()
    
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()
    
    try:
        # Keep the HTTP server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        await http_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())


