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
    
    # Initialize and test MeTTa knowledge base
    if rag_system.metta_enabled and rag_system.metta_kb:
        ctx.logger.info("🧠 Testing MeTTa knowledge base...")
        try:
            # Test MeTTa with a simple query
            test_patterns = rag_system.metta_kb.query_advanced_patterns("authentication")
            if test_patterns:
                ctx.logger.info(f"✅ MeTTa knowledge base working - found {len(test_patterns)} patterns")
                ctx.logger.info(f"🧠 MeTTa atoms loaded and queryable")
            else:
                ctx.logger.warning("⚠️ MeTTa knowledge base loaded but no patterns found in test query")
        except Exception as e:
            ctx.logger.error(f"❌ MeTTa knowledge base test failed: {e}")
    else:
        ctx.logger.warning("⚠️ MeTTa integration not available")
    
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
    
    ctx.logger.info("🎯 Agent ready to process questions with MeTTa symbolic reasoning")

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
                    metta_reasoning += "Based on symbolic reasoning from the MeTTa knowledge base:\n\n"
                    
                    # Group patterns by category for better organization
                    security_patterns = [p for p in patterns if p.get('category') == 'security']
                    api_patterns = [p for p in patterns if p.get('type') == 'api']
                    performance_patterns = [p for p in patterns if p.get('type') == 'performance']
                    monitoring_patterns = [p for p in patterns if p.get('category') == 'monitoring']
                    
                    pattern_count = 0
                    
                    if security_patterns:
                        metta_reasoning += "### 🔐 Security Patterns\n"
                        for pattern in security_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('pattern', 'Security Pattern')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'Security-related pattern')}\n\n"
                    
                    if api_patterns:
                        metta_reasoning += "### 🌐 API Patterns\n"
                        for pattern in api_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('pattern', 'API Pattern')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'API design pattern')}\n\n"
                    
                    if performance_patterns:
                        metta_reasoning += "### ⚡ Performance Patterns\n"
                        for pattern in performance_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('pattern', 'Performance Pattern')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'Performance optimization pattern')}\n\n"
                    
                    if monitoring_patterns:
                        metta_reasoning += "### 📊 Monitoring Concepts\n"
                        for pattern in monitoring_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('concept', 'Monitoring Concept')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'Monitoring and observability concept')}\n\n"
                    
                    # Add summary
                    metta_reasoning += f"\n**Total MeTTa patterns analyzed:** {len(patterns)}\n"
                    metta_reasoning += "These patterns provide structured insights from the symbolic knowledge base.\n\n"
                    
                    # Add MeTTa citations
                    metta_citations = [f"MeTTa Pattern: {p.get('pattern', 'N/A')}" for p in patterns[:3]]
                else:
                    # No patterns found - don't include MeTTa reasoning in the LLM prompt
                    metta_reasoning = None
                    metta_citations = []
            except Exception as e:
                ctx.logger.warning(f"MeTTa reasoning failed: {e}")
                metta_reasoning = None
                metta_citations = []
        else:
            metta_reasoning = None
            metta_citations = []
        
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
        user_prompt = f"""Question: {msg.question}

=== RAG CONTEXT (Document Retrieval) ===
{rag_result.get('answer', '')}"""

        # Only include MeTTa reasoning if insights were found
        if metta_reasoning:
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
        
        # Initialize full_response with the LLM answer
        full_response = answer
        
        # Check if RAG result already contains citations
        rag_answer = rag_result.get('answer', '')
        has_existing_citations = '📖 Citations' in rag_answer
        
        # Debug logging
        logger.info(f"🔍 HTTP Debug: RAG answer length: {len(rag_answer)}")
        logger.info(f"🔍 HTTP Debug: Has existing citations: {has_existing_citations}")
        if has_existing_citations:
            logger.info("🔍 HTTP Debug: Citations found in RAG answer")
        else:
            logger.info("🔍 HTTP Debug: No citations found in RAG answer")
            logger.info(f"🔍 HTTP Debug: RAG answer preview: {rag_answer[:200]}...")
        
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
            
            # Add MeTTa citations if available
            if rag_system.metta_enabled:
                citation_sections.append("\n### 🧠 MeTTa Atom Citations\n")
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
        
        # Send comprehensive response
        await ctx.send(
            sender,
            QuestionResponse(
                answer=full_response,
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
                    metta_reasoning += "Based on symbolic reasoning from the MeTTa knowledge base:\n\n"
                    
                    # Group patterns by category for better organization
                    security_patterns = [p for p in patterns if p.get('category') == 'security']
                    api_patterns = [p for p in patterns if p.get('type') == 'api']
                    performance_patterns = [p for p in patterns if p.get('type') == 'performance']
                    monitoring_patterns = [p for p in patterns if p.get('category') == 'monitoring']
                    
                    pattern_count = 0
                    
                    if security_patterns:
                        metta_reasoning += "### 🔐 Security Patterns\n"
                        for pattern in security_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('pattern', 'Security Pattern')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'Security-related pattern')}\n\n"
                    
                    if api_patterns:
                        metta_reasoning += "### 🌐 API Patterns\n"
                        for pattern in api_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('pattern', 'API Pattern')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'API design pattern')}\n\n"
                    
                    if performance_patterns:
                        metta_reasoning += "### ⚡ Performance Patterns\n"
                        for pattern in performance_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('pattern', 'Performance Pattern')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'Performance optimization pattern')}\n\n"
                    
                    if monitoring_patterns:
                        metta_reasoning += "### 📊 Monitoring Concepts\n"
                        for pattern in monitoring_patterns[:3]:
                            pattern_count += 1
                            metta_reasoning += f"**{pattern_count}. {pattern.get('concept', 'Monitoring Concept')}**\n"
                            metta_reasoning += f"   - {pattern.get('description', 'Monitoring and observability concept')}\n\n"
                    
                    # Add summary
                    metta_reasoning += f"\n**Total MeTTa patterns analyzed:** {len(patterns)}\n"
                    metta_reasoning += "These patterns provide structured insights from the symbolic knowledge base.\n\n"
                    
                    # Add MeTTa citations
                    metta_citations = [f"MeTTa Pattern: {p.get('pattern', 'N/A')}" for p in patterns[:3]]
                else:
                    # No patterns found - don't include MeTTa reasoning in the LLM prompt
                    metta_reasoning = None
                    metta_citations = []
            except Exception as e:
                logger.warning(f"MeTTa reasoning failed: {e}")
                metta_reasoning = None
                metta_citations = []
        else:
            metta_reasoning = None
            metta_citations = []
        
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
        if metta_reasoning:
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
        
        # Initialize full_response with the LLM answer
        full_response = answer
        
        # Check if RAG result already contains citations
        rag_answer = rag_result.get('answer', '')
        has_existing_citations = '📖 Citations' in rag_answer
        
        # Debug logging
        logger.info(f"🔍 HTTP Debug: RAG answer length: {len(rag_answer)}")
        logger.info(f"🔍 HTTP Debug: Has existing citations: {has_existing_citations}")
        if has_existing_citations:
            logger.info("🔍 HTTP Debug: Citations found in RAG answer")
        else:
            logger.info("🔍 HTTP Debug: No citations found in RAG answer")
            logger.info(f"🔍 HTTP Debug: RAG answer preview: {rag_answer[:200]}...")
        
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
            
            # Add MeTTa citations if available
            if rag_system.metta_enabled:
                citation_sections.append("\n### 🧠 MeTTa Atom Citations\n")
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
        
        return web.json_response({
            "answer": full_response,
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


