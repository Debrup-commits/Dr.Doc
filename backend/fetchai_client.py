#!/usr/bin/env python3
"""
Fetch.ai ASI:One Client for Chat Completions and Embeddings
Uses Fetch.ai's own models instead of OpenAI while maintaining OpenAI-compatible interface
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FetchAIClient:
    """Fetch.ai ASI:One client with OpenAI-compatible interface"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ASI_ONE_API_KEY")
        if not self.api_key:
            raise ValueError("ASI_ONE_API_KEY environment variable not set")
        
        # Use OpenAI client with Fetch.ai endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.asi1.ai/v1"  # Fetch.ai ASI:One endpoint
        )
        
        # Fetch.ai model configurations
        self.chat_model = "asi1-mini"  # ASI:One chat model
        self.embedding_model = "text-embedding-3-small"  # ASI:One embedding model
    
    def chat_completions_create(self, **kwargs):
        """Create chat completion using Fetch.ai models"""
        # Ensure we're using Fetch.ai models
        if 'model' not in kwargs:
            kwargs['model'] = self.chat_model
        
        # Add Fetch.ai specific parameters if needed
        kwargs.setdefault('temperature', 0.1)
        kwargs.setdefault('max_tokens', 1000)
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            return response
        except Exception as e:
            print(f"Fetch.ai API error: {e}")
            raise
    
    def embeddings_create(self, **kwargs):
        """Create embeddings using Fetch.ai models"""
        # Ensure we're using Fetch.ai embedding model
        if 'model' not in kwargs:
            kwargs['model'] = self.embedding_model
        
        try:
            response = self.client.embeddings.create(**kwargs)
            return response
        except Exception as e:
            print(f"Fetch.ai embeddings error: {e}")
            raise

class HybridClient:
    """Hybrid client that can use either Fetch.ai or OpenAI"""
    
    def __init__(self, use_fetchai: bool = True, require_openai_fallback: bool = False):
        self.use_fetchai = use_fetchai
        self.require_openai_fallback = require_openai_fallback
        
        if use_fetchai:
            try:
                self.client = FetchAIClient()
                self.model_source = "fetchai"
                print("✅ Using Fetch.ai ASI:One models")
            except Exception as e:
                print(f"⚠️  Fetch.ai client failed: {e}")
                if require_openai_fallback:
                    print("🔄 Falling back to OpenAI...")
                    self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    self.model_source = "openai"
                else:
                    print("❌ Fetch.ai client failed and OpenAI fallback disabled")
                    raise Exception(f"Fetch.ai client failed: {e}")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model_source = "openai"
            print("✅ Using OpenAI models")
    
    def chat_completions_create(self, **kwargs):
        """Create chat completion"""
        if self.model_source == "fetchai":
            return self.client.chat_completions_create(**kwargs)
        else:
            return self.client.chat.completions.create(**kwargs)
    
    def embeddings_create(self, **kwargs):
        """Create embeddings"""
        if self.model_source == "fetchai":
            return self.client.embeddings_create(**kwargs)
        else:
            return self.client.embeddings.create(**kwargs)

# Test function
def test_fetchai_client():
    """Test Fetch.ai client functionality"""
    print("🧪 Testing Fetch.ai ASI:One Client...")
    
    try:
        # Test chat completion
        client = FetchAIClient()
        
        response = client.chat_completions_create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Can you tell me about Fetch.ai?"}
            ],
            max_tokens=100
        )
        
        print("✅ Chat completion test successful")
        print(f"Response: {response.choices[0].message.content[:100]}...")
        
        # Test embeddings
        embedding_response = client.embeddings_create(
            model="text-embedding-3-small",
            input="Test text for embedding"
        )
        
        print("✅ Embeddings test successful")
        print(f"Embedding dimension: {len(embedding_response.data[0].embedding)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_fetchai_client()
