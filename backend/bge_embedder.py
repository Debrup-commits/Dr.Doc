#!/usr/bin/env python3
"""
BGE Embedder for Agno RAG system
Uses BAAI/bge-base-en-v1.5 model for free embeddings
"""

import os
import logging
from typing import List, Union
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class BGEEmbedder:
    """BGE Embedder using sentence-transformers"""
    
    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        """
        Initialize BGE embedder
        
        Args:
            model_name: HuggingFace model name for BGE embeddings
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dimension = 768  # BGE-base dimension
        self.dimensions = 768  # Required by Agno framework
        
        try:
            logger.info(f"Loading BGE model: {model_name}")
            # Force CPU device to avoid meta tensor issues
            import torch
            device = 'cpu'
            self.model = SentenceTransformer(model_name, device=device)
            # Ensure model is on CPU and not using meta tensors
            self.model = self.model.to(device)
            logger.info(f"✅ BGE model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"❌ Failed to load BGE model: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents
        
        Args:
            texts: List of text documents to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self.model:
                raise ValueError("BGE model not initialized")
            
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Convert to list of lists
            if len(embeddings.shape) == 1:
                embeddings = [embeddings.tolist()]
            else:
                embeddings = embeddings.tolist()
            
            logger.info(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if not self.model:
                raise ValueError("BGE model not initialized")
            
            # Generate embedding
            embedding = self.model.encode([text], convert_to_tensor=False)
            
            # Return as list
            return embedding[0].tolist()
            
        except Exception as e:
            logger.error(f"❌ Error generating query embedding: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.embedding_dimension
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text (required by Agno framework)
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.embed_query(text)

# Test the embedder
if __name__ == "__main__":
    # Test the BGE embedder
    embedder = BGEEmbedder()
    
    # Test documents
    test_docs = [
        "This is a test document about authentication.",
        "Rate limits are important for API security."
    ]
    
    # Test query
    test_query = "How do I authenticate with the API?"
    
    print("Testing BGE Embedder...")
    
    # Test document embeddings
    doc_embeddings = embedder.embed_documents(test_docs)
    print(f"Document embeddings shape: {len(doc_embeddings)} x {len(doc_embeddings[0])}")
    
    # Test query embedding
    query_embedding = embedder.embed_query(test_query)
    print(f"Query embedding shape: {len(query_embedding)}")
    
    print("✅ BGE Embedder test completed successfully!")