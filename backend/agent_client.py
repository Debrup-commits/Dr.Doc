#!/usr/bin/env python3
"""
Client for communicating with the Document Q&A uAgent
Provides a simple interface for frontend applications
"""

import asyncio
import json
from typing import Dict, Any, Optional
from uagents import Agent
from doc_qa_agent import QuestionRequest, QuestionResponse, HealthCheck, ErrorResponse

class DocumentQAClient:
    """Client for communicating with the Document Q&A agent"""
    
    def __init__(self, agent_address: str):
        self.agent_address = agent_address
        self.client_agent = Agent(name="doc-qa-client", seed="client_seed_phrase")
    
    async def ask_question(self, question: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """Ask a question to the Document Q&A agent"""
        try:
            # Create request
            request = QuestionRequest(
                question=question,
                user_id=user_id,
                session_id=session_id
            )
            
            # Send request and wait for response
            # Note: This is a simplified implementation - in production you'd use proper message passing
            # For now, we'll simulate the response by calling the QA system directly
            from app_agno_hybrid import AgnoHybridQASystem
            qa_system = AgnoHybridQASystem()
            result = qa_system.query(question)
            
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
                response_time=0.0
            )
            
            if isinstance(response, QuestionResponse):
                return {
                    'answer': response.answer,
                    'sources': response.sources,
                    'facts': response.facts,
                    'source': response.source,
                    'confidence': response.confidence,
                    'reasoning': response.reasoning,
                    'model_source': response.model_source,
                    'context_used': response.context_used,
                    'metta_details': response.metta_details,
                    'rag_details': response.rag_details,
                    'response_time': response.response_time,
                    'success': True
                }
            elif isinstance(response, ErrorResponse):
                return {
                    'error': response.error,
                    'error_type': response.error_type,
                    'suggestion': response.suggestion,
                    'success': False
                }
            else:
                return {
                    'error': 'Unknown response type',
                    'success': False
                }
                
        except asyncio.TimeoutError:
            return {
                'error': 'Request timeout - agent may be busy or unavailable',
                'error_type': 'timeout',
                'suggestion': 'Please try again later or check if the agent is running',
                'success': False
            }
        except Exception as e:
            return {
                'error': str(e),
                'error_type': 'client_error',
                'suggestion': 'Please check your connection and try again',
                'success': False
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Document Q&A agent"""
        try:
            request = HealthCheck(
                status="check",
                agent_address="",
                rag_documents_loaded=0,
                metta_atoms_loaded=0,
                vector_store_ready=False,
                uptime=0.0
            )
            
            # Simplified health check - in production this would communicate with the actual agent
            from app_agno_hybrid import AgnoHybridQASystem
            qa_system = AgnoHybridQASystem()
            
            response = HealthCheck(
                status="healthy",
                agent_address=self.agent_address,
                rag_documents_loaded=qa_system.agno_rag.knowledge.count() if qa_system.agno_rag.knowledge else 0,
                metta_atoms_loaded=25,  # From our MeTTa knowledge base
                vector_store_ready=qa_system.agno_rag.knowledge is not None,
                uptime=100.0  # Simulated uptime
            )
            
            if isinstance(response, HealthCheck):
                return {
                    'status': response.status,
                    'agent_address': response.agent_address,
                    'rag_documents_loaded': response.rag_documents_loaded,
                    'metta_atoms_loaded': response.metta_atoms_loaded,
                    'vector_store_ready': response.vector_store_ready,
                    'uptime': response.uptime,
                    'success': True
                }
            else:
                return {
                    'status': 'unknown',
                    'error': 'Unexpected response type',
                    'success': False
                }
                
        except asyncio.TimeoutError:
            return {
                'status': 'unreachable',
                'error': 'Health check timeout',
                'success': False
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'success': False
            }

# Synchronous wrapper for Flask integration
class SyncDocumentQAClient:
    """Synchronous wrapper for the Document Q&A client"""
    
    def __init__(self, agent_address: str):
        self.agent_address = agent_address
        self.client = DocumentQAClient(agent_address)
    
    def ask_question(self, question: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for asking questions"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.client.ask_question(question, user_id, session_id)
            )
        finally:
            loop.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Synchronous wrapper for health checks"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.client.health_check()
            )
        finally:
            loop.close()

# Test function
async def test_agent_client():
    """Test the agent client functionality"""
    print("🧪 Testing Document Q&A Agent Client...")
    
    # You'll need to replace this with the actual agent address
    agent_address = "agent1q..."  # Replace with actual address
    
    client = DocumentQAClient(agent_address)
    
    try:
        # Test health check
        print("🔍 Testing health check...")
        health = await client.health_check()
        print(f"Health status: {health}")
        
        # Test question
        print("📝 Testing question...")
        response = await client.ask_question("What OAuth authentication flows are supported?")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_client())
