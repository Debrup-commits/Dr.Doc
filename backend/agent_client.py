#!/usr/bin/env python3
"""
Client for communicating with the ASI:One RAG uAgent
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from uagents import Agent
from uagents.query import query

# Import message models
from asi_one_agent import QuestionRequest, QuestionResponse, HealthCheck, HealthResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ASIOneRAGClient:
    """Client for communicating with the ASI:One RAG uAgent"""
    
    def __init__(self, agent_address: str = None):
        """
        Initialize the client
        
        Args:
            agent_address: The address of the ASI:One RAG agent
        """
        # Default agent address (will be set when agent starts)
        self.agent_address = agent_address or "agent1q..."
        self.agent = Agent(name="client", seed="client_seed")
    
    async def ask_question(self, question: str, session_id: str = None) -> Dict[str, Any]:
        """
        Ask a question to the ASI:One RAG agent
        
        Args:
            question: The question to ask
            session_id: Optional session ID
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Create request
            request = QuestionRequest(
                question=question,
                session_id=session_id
            )
            
            # Query the agent
            response = await query(
                destination=self.agent_address,
                message=request,
                response_type=QuestionResponse,
                timeout=30.0
            )
            
            return {
                "answer": response.answer,
                "sources": response.sources,
                "metta_reasoning": response.metta_reasoning,
                "success": response.success,
                "error": response.error
            }
            
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the ASI:One RAG agent
        
        Returns:
            Dictionary containing health status
        """
        try:
            # Create health check request
            request = HealthCheck()
            
            # Query the agent
            response = await query(
                destination=self.agent_address,
                message=request,
                response_type=HealthResponse,
                timeout=10.0
            )
            
            return {
                "status": response.status,
                "system": response.system,
                "embedder": response.embedder,
                "database": response.database,
                "metta_enabled": response.metta_enabled
            }
            
        except Exception as e:
            logger.error(f"Error checking health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Synchronous wrapper for Flask integration
class SyncASIOneRAGClient:
    """Synchronous wrapper for the ASI:One RAG client"""
    
    def __init__(self, agent_address: str = None):
        self.client = ASIOneRAGClient(agent_address)
    
    def ask_question(self, question: str, session_id: str = None) -> Dict[str, Any]:
        """Synchronous version of ask_question"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.client.ask_question(question, session_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in ask_question: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Synchronous version of health_check"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.client.health_check())
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in health_check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global client instance
_global_client = None

def get_client(agent_address: str = None) -> SyncASIOneRAGClient:
    """Get or create the global client instance"""
    global _global_client
    if _global_client is None:
        _global_client = SyncASIOneRAGClient(agent_address)
    return _global_client

def set_agent_address(agent_address: str):
    """Set the agent address for the global client"""
    global _global_client
    _global_client = SyncASIOneRAGClient(agent_address)
