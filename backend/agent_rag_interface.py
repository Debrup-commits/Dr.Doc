#!/usr/bin/env python3
"""
Agent RAG/MeTTa Interface
Provides a unified interface for agents to query both RAG and MeTTa systems
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries that can be processed"""
    RAG = "rag"
    METTA = "metta"
    HYBRID = "hybrid"
    AUTO = "auto"

@dataclass
class QueryResult:
    """Result from a query operation"""
    answer: str
    sources: List[Dict[str, Any]]
    facts: List[Dict[str, Any]]
    query_type: QueryType
    confidence: float
    reasoning: str
    model_source: str
    response_time: float
    metadata: Dict[str, Any]

class AgentRAGInterface:
    """Unified interface for agents to query RAG and MeTTa systems"""
    
    def __init__(self, use_fetchai: bool = True, enable_metta: bool = True):
        self.use_fetchai = use_fetchai
        self.enable_metta = enable_metta
        self.agno_rag = None
        self.metta_kb = None
        self._initialized = False
        
        # Initialize systems
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize RAG and MeTTa systems"""
        try:
            # Initialize Agno RAG system
            from fetchai_agno_rag import FetchAIAgnoRAG
            self.agno_rag = FetchAIAgnoRAG(
                use_fetchai=self.use_fetchai,
                require_openai_fallback=True,
                lazy_init=True
            )
            logger.info("✅ Agno RAG system initialized")
            
            # Initialize MeTTa system if enabled
            if self.enable_metta:
                try:
                    from metta_ingest import MeTTaKnowledgeBase
                    self.metta_kb = MeTTaKnowledgeBase()
                    self.metta_kb.load_atoms_from_file("api_facts.metta")
                    logger.info("✅ MeTTa knowledge base initialized")
                except Exception as e:
                    logger.warning(f"⚠️  MeTTa initialization failed: {e}")
                    self.enable_metta = False
            
            self._initialized = True
            logger.info("✅ Agent RAG Interface fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize systems: {e}")
            raise
    
    def query(self, question: str, query_type: QueryType = QueryType.AUTO, 
              context: Optional[str] = None, user_id: Optional[str] = None) -> QueryResult:
        """
        Main query method that processes questions using RAG and/or MeTTa
        
        Args:
            question: The question to answer
            query_type: Type of query to perform (auto-detects if AUTO)
            context: Additional context for the query
            user_id: User identifier for tracking
            
        Returns:
            QueryResult with answer and metadata
        """
        start_time = time.time()
        
        if not self._initialized:
            raise RuntimeError("Agent RAG Interface not initialized")
        
        # Auto-detect query type if needed
        if query_type == QueryType.AUTO:
            query_type = self._detect_query_type(question)
        
        logger.info(f"Processing query: '{question}' with type: {query_type.value}")
        
        # Process based on query type
        if query_type == QueryType.RAG:
            result = self._query_rag_only(question, context)
        elif query_type == QueryType.METTA:
            result = self._query_metta_only(question, context)
        elif query_type == QueryType.HYBRID:
            result = self._query_hybrid(question, context)
        else:
            raise ValueError(f"Unknown query type: {query_type}")
        
        # Add timing and metadata
        result.response_time = time.time() - start_time
        result.metadata.update({
            'user_id': user_id,
            'context': context,
            'timestamp': time.time()
        })
        
        logger.info(f"Query completed in {result.response_time:.2f}s with confidence {result.confidence:.2f}")
        return result
    
    def _detect_query_type(self, question: str) -> QueryType:
        """Auto-detect the best query type for a question"""
        question_lower = question.lower()
        
        # MeTTa-suitable patterns (precise facts)
        metta_patterns = [
            r'what.*error.*code',
            r'what.*rate.*limit',
            r'what.*parameters',
            r'list.*endpoints',
            r'what.*tier',
            r'how.*many.*requests',
            r'what.*authentication',
            r'what.*endpoint.*supports',
            r'what.*status.*code',
            r'what.*slippage',
            r'what.*gas',
            r'what.*fee',
            r'what.*oauth',
            r'what.*security',
            r'what.*performance',
            r'what.*monitoring'
        ]
        
        # Check for MeTTa patterns
        import re
        for pattern in metta_patterns:
            if re.search(pattern, question_lower):
                if self.enable_metta:
                    return QueryType.HYBRID  # Use hybrid for best results
                else:
                    return QueryType.RAG
        
        # Default to RAG for general questions
        return QueryType.RAG
    
    def _query_rag_only(self, question: str, context: Optional[str] = None) -> QueryResult:
        """Query using only RAG system"""
        try:
            # Enhance question with context if provided
            enhanced_question = question
            if context:
                enhanced_question = f"Context: {context}\n\nQuestion: {question}"
            
            # Query RAG system
            rag_result = self.agno_rag.query(enhanced_question)
            
            return QueryResult(
                answer=rag_result.get('answer', 'No answer available'),
                sources=rag_result.get('sources', []),
                facts=[],
                query_type=QueryType.RAG,
                confidence=0.8,  # Default confidence for RAG
                reasoning="Used RAG system for comprehensive answer",
                model_source=rag_result.get('model_source', 'unknown'),
                response_time=0.0,  # Will be set by caller
                metadata={
                    'rag_details': {
                        'sources_found': len(rag_result.get('sources', [])),
                        'context_used': rag_result.get('context_used', 0)
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return QueryResult(
                answer=f"Error querying RAG system: {str(e)}",
                sources=[],
                facts=[],
                query_type=QueryType.RAG,
                confidence=0.0,
                reasoning="RAG query failed",
                model_source="error",
                response_time=0.0,
                metadata={'error': str(e)}
            )
    
    def _query_metta_only(self, question: str, context: Optional[str] = None) -> QueryResult:
        """Query using only MeTTa system"""
        if not self.enable_metta or not self.metta_kb:
            return QueryResult(
                answer="MeTTa system not available",
                sources=[],
                facts=[],
                query_type=QueryType.METTA,
                confidence=0.0,
                reasoning="MeTTa system not enabled or available",
                model_source="none",
                response_time=0.0,
                metadata={'error': 'MeTTa not available'}
            )
        
        try:
            # Query MeTTa system
            metta_result = self.metta_kb.query_advanced_patterns(question)
            
            if metta_result:
                # Format MeTTa results
                answer_parts = ["## MeTTa Knowledge Base Results"]
                for result in metta_result:
                    if 'pattern' in result:
                        answer_parts.append(f"• **{result['pattern']}**: {result.get('flow_type', result.get('concept', 'N/A'))}")
                    elif 'concept' in result:
                        answer_parts.append(f"• **{result['concept']}**: {result.get('type', 'N/A')}")
                
                answer = "\n".join(answer_parts)
                confidence = 0.9  # High confidence for MeTTa facts
            else:
                answer = "No specific facts found in MeTTa knowledge base for this question."
                confidence = 0.0
            
            return QueryResult(
                answer=answer,
                sources=[],
                facts=metta_result,
                query_type=QueryType.METTA,
                confidence=confidence,
                reasoning="Used MeTTa knowledge base for precise facts",
                model_source="metta",
                response_time=0.0,
                metadata={
                    'metta_details': {
                        'facts_found': len(metta_result),
                        'confidence': confidence
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"MeTTa query failed: {e}")
            return QueryResult(
                answer=f"Error querying MeTTa system: {str(e)}",
                sources=[],
                facts=[],
                query_type=QueryType.METTA,
                confidence=0.0,
                reasoning="MeTTa query failed",
                model_source="error",
                response_time=0.0,
                metadata={'error': str(e)}
            )
    
    def _query_hybrid(self, question: str, context: Optional[str] = None) -> QueryResult:
        """Query using both RAG and MeTTa systems for hybrid results"""
        try:
            # Get MeTTa results first
            metta_result = self._query_metta_only(question, context)
            
            # Get RAG results
            rag_result = self._query_rag_only(question, context)
            
            # Combine results intelligently
            if metta_result.confidence > 0.5 and metta_result.facts:
                # MeTTa found good facts, create hybrid response
                hybrid_answer = self._create_hybrid_answer(metta_result, rag_result)
                confidence = max(metta_result.confidence, rag_result.confidence)
                reasoning = f"Combined MeTTa facts (confidence: {metta_result.confidence:.2f}) with RAG context"
            else:
                # Use RAG as primary, MeTTa as fallback
                hybrid_answer = rag_result.answer
                if metta_result.facts:
                    hybrid_answer += f"\n\n## Additional Facts\n{metta_result.answer}"
                confidence = rag_result.confidence
                reasoning = f"Used RAG as primary (confidence: {rag_result.confidence:.2f}), MeTTa provided additional context"
            
            return QueryResult(
                answer=hybrid_answer,
                sources=rag_result.sources,
                facts=metta_result.facts,
                query_type=QueryType.HYBRID,
                confidence=confidence,
                reasoning=reasoning,
                model_source=rag_result.model_source,
                response_time=0.0,
                metadata={
                    'metta_details': metta_result.metadata.get('metta_details', {}),
                    'rag_details': rag_result.metadata.get('rag_details', {})
                }
            )
            
        except Exception as e:
            logger.error(f"Hybrid query failed: {e}")
            # Fallback to RAG only
            return self._query_rag_only(question, context)
    
    def _create_hybrid_answer(self, metta_result: QueryResult, rag_result: QueryResult) -> str:
        """Create a hybrid answer combining MeTTa facts with RAG context"""
        response_parts = []
        
        # Start with MeTTa facts (precise information)
        if metta_result.answer:
            response_parts.append(metta_result.answer)
        
        # Add RAG context if it's complementary
        rag_content = rag_result.answer.strip()
        if rag_content and len(rag_content) > 100:
            response_parts.append("\n---\n")
            response_parts.append("## Additional Context")
            response_parts.append(rag_content)
        
        # Add sources if available
        if rag_result.sources:
            response_parts.append("\n---\n")
            response_parts.append("## Documentation Sources")
            for i, source in enumerate(rag_result.sources[:3], 1):
                source_name = source.get('source', 'Unknown')
                score = source.get('score', 0)
                response_parts.append(f"**{i}. {source_name}** (relevance: {score:.1%})")
        
        return "\n".join(response_parts)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the status of all systems"""
        status = {
            'initialized': self._initialized,
            'rag_available': self.agno_rag is not None,
            'metta_available': self.enable_metta and self.metta_kb is not None,
            'use_fetchai': self.use_fetchai
        }
        
        if self.agno_rag:
            status['rag_model_source'] = getattr(self.agno_rag, 'model_source', 'unknown')
            status['rag_knowledge_ready'] = self.agno_rag.knowledge is not None
        
        if self.metta_kb:
            status['metta_atoms_loaded'] = len(self.metta_kb.atoms)
        
        return status
    
    def ingest_documents(self, docs_dir: str = "../docs") -> bool:
        """Ingest documents into the knowledge base"""
        try:
            if self.agno_rag:
                self.agno_rag.ingest_documents(docs_dir)
                logger.info("✅ Documents ingested into RAG system")
                return True
            else:
                logger.error("❌ RAG system not available for ingestion")
                return False
        except Exception as e:
            logger.error(f"❌ Document ingestion failed: {e}")
            return False
    
    def extract_metta_facts(self, docs_dir: str = "../docs") -> bool:
        """Extract MeTTa facts from documents"""
        try:
            if self.enable_metta:
                from metta_ingest import MeTTaFactExtractor
                extractor = MeTTaFactExtractor()
                atoms = extractor.extract_all_facts(docs_dir)
                
                if self.metta_kb:
                    self.metta_kb.load_atoms(atoms)
                    self.metta_kb.save_atoms("api_facts.metta")
                    logger.info(f"✅ Extracted {len(atoms)} MeTTa facts")
                    return True
            else:
                logger.warning("⚠️  MeTTa system not enabled")
                return False
        except Exception as e:
            logger.error(f"❌ MeTTa fact extraction failed: {e}")
            return False

# Global instance for easy access
_agent_interface = None

def get_agent_interface() -> AgentRAGInterface:
    """Get the global agent interface instance"""
    global _agent_interface
    if _agent_interface is None:
        use_fetchai = os.getenv("USE_FETCHAI", "true").lower() in ('true', '1', 'yes', 'on')
        enable_metta = os.getenv("ENABLE_METTA", "true").lower() in ('true', '1', 'yes', 'on')
        _agent_interface = AgentRAGInterface(use_fetchai=use_fetchai, enable_metta=enable_metta)
    return _agent_interface

def query_for_agent(question: str, query_type: str = "auto", 
                   context: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for agents to query the system
    
    Args:
        question: The question to answer
        query_type: Type of query ("rag", "metta", "hybrid", "auto")
        context: Additional context
        user_id: User identifier
        
    Returns:
        Dictionary with query results
    """
    interface = get_agent_interface()
    
    # Convert string to enum
    query_type_enum = QueryType.AUTO
    if query_type.lower() == "rag":
        query_type_enum = QueryType.RAG
    elif query_type.lower() == "metta":
        query_type_enum = QueryType.METTA
    elif query_type.lower() == "hybrid":
        query_type_enum = QueryType.HYBRID
    
    result = interface.query(question, query_type_enum, context, user_id)
    
    # Convert to dictionary for easy serialization
    return {
        'answer': result.answer,
        'sources': result.sources,
        'facts': result.facts,
        'query_type': result.query_type.value,
        'confidence': result.confidence,
        'reasoning': result.reasoning,
        'model_source': result.model_source,
        'response_time': result.response_time,
        'metadata': result.metadata
    }

if __name__ == "__main__":
    # Test the agent interface
    print("🧪 Testing Agent RAG Interface...")
    
    try:
        interface = AgentRAGInterface()
        
        # Test system status
        status = interface.get_system_status()
        print(f"System Status: {status}")
        
        # Test queries
        test_questions = [
            "What OAuth flows are supported?",
            "What are the rate limits for the free tier?",
            "How do I authenticate with the API?",
            "What error codes can the /swap endpoint return?"
        ]
        
        for question in test_questions:
            print(f"\n🔍 Testing: {question}")
            result = interface.query(question)
            print(f"Answer: {result.answer[:100]}...")
            print(f"Type: {result.query_type.value}, Confidence: {result.confidence:.2f}")
            print(f"Facts: {len(result.facts)}, Sources: {len(result.sources)}")
        
        print("\n✅ Agent RAG Interface test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

