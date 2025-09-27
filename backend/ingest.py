#!/usr/bin/env python3
"""
RAG Ingestion Script for API Documentation
Fallback system using FAISS and OpenAI embeddings
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
import markdown
from bs4 import BeautifulSoup
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentChunker:
    """Handles splitting of Markdown documents into meaningful chunks."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_heading_structure(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract heading structure from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        headings = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            text = heading.get_text().strip()
            headings.append({
                'level': level,
                'text': text,
                'element': heading
            })
        
        return headings
    
    def chunk_by_heading(self, html_content: str, file_path: str) -> List[Dict[str, Any]]:
        """Split document into chunks based on heading structure."""
        soup = BeautifulSoup(html_content, 'html.parser')
        chunks = []
        
        # Find all headings and their content
        current_chunk = {
            'content': '',
            'heading': '',
            'level': 0,
            'file_path': file_path,
            'metadata': {}
        }
        
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table', 'pre', 'code']):
            if element.name.startswith('h'):
                # Save previous chunk if it has content
                if current_chunk['content'].strip():
                    chunks.append(current_chunk.copy())
                
                # Start new chunk
                level = int(element.name[1])
                heading_text = element.get_text().strip()
                current_chunk = {
                    'content': f"# {heading_text}\n\n",
                    'heading': heading_text,
                    'level': level,
                    'file_path': file_path,
                    'metadata': {
                        'heading_level': level,
                        'heading_text': heading_text
                    }
                }
            else:
                # Add content to current chunk
                element_text = element.get_text().strip()
                if element_text:
                    current_chunk['content'] += element_text + '\n\n'
        
        # Add final chunk
        if current_chunk['content'].strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def split_large_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split chunks that are too large into smaller pieces."""
        final_chunks = []
        
        for chunk in chunks:
            content = chunk['content']
            if len(content) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by paragraphs
                paragraphs = content.split('\n\n')
                current_chunk_content = ''
                
                for para in paragraphs:
                    if len(current_chunk_content + para) <= self.chunk_size:
                        current_chunk_content += para + '\n\n'
                    else:
                        if current_chunk_content.strip():
                            new_chunk = chunk.copy()
                            new_chunk['content'] = current_chunk_content.strip()
                            final_chunks.append(new_chunk)
                        current_chunk_content = para + '\n\n'
                
                # Add remaining content
                if current_chunk_content.strip():
                    new_chunk = chunk.copy()
                    new_chunk['content'] = current_chunk_content.strip()
                    final_chunks.append(new_chunk)
        
        return final_chunks

class EmbeddingGenerator:
    """Handles generation of embeddings using OpenAI's API."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                print(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            except Exception as e:
                print(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
                # Add None embeddings for failed batch
                embeddings.extend([None] * len(batch))
        
        return embeddings

class VectorStore:
    """Handles FAISS vector store operations."""
    
    def __init__(self, dimension: int = 1536):  # text-embedding-3-small dimension
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.documents = []
        self.metadata = []
    
    def add_embeddings(self, embeddings: List[List[float]], documents: List[Dict[str, Any]]):
        """Add embeddings and documents to the vector store."""
        valid_embeddings = []
        valid_docs = []
        valid_metadata = []
        
        for i, (embedding, doc) in enumerate(zip(embeddings, documents)):
            if embedding is not None:
                valid_embeddings.append(embedding)
                valid_docs.append(doc)
                valid_metadata.append({
                    'index': len(valid_docs) - 1,
                    'file_path': doc['file_path'],
                    'heading': doc.get('heading', ''),
                    'level': doc.get('level', 0),
                    'metadata': doc.get('metadata', {})
                })
        
        if valid_embeddings:
            # Normalize embeddings for cosine similarity
            embeddings_array = np.array(valid_embeddings).astype('float32')
            faiss.normalize_L2(embeddings_array)
            
            self.index.add(embeddings_array)
            self.documents.extend(valid_docs)
            self.metadata.extend(valid_metadata)
            
            print(f"Added {len(valid_embeddings)} documents to vector store")
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.documents:
            return []
        
        query_array = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_array)
        
        scores, indices = self.index.search(query_array, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                results.append({
                    'document': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'score': float(score)
                })
        
        return results
    
    def save(self, filepath: str):
        """Save the vector store to disk."""
        faiss.write_index(self.index, f"{filepath}.index")
        
        with open(f"{filepath}.metadata", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'dimension': self.dimension
            }, f)
        
        print(f"Vector store saved to {filepath}")
    
    def load(self, filepath: str):
        """Load the vector store from disk."""
        self.index = faiss.read_index(f"{filepath}.index")
        
        with open(f"{filepath}.metadata", 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
            self.dimension = data['dimension']
        
        print(f"Vector store loaded from {filepath}")

def process_markdown_files(docs_dir: str) -> List[Dict[str, Any]]:
    """Process all Markdown files in the docs directory."""
    chunker = DocumentChunker()
    all_chunks = []
    
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        raise FileNotFoundError(f"Documentation directory {docs_dir} not found")
    
    for md_file in docs_path.glob("*.md"):
        print(f"Processing {md_file.name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert Markdown to HTML for better parsing
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        # Extract chunks
        chunks = chunker.chunk_by_heading(html_content, str(md_file))
        chunks = chunker.split_large_chunks(chunks)
        
        all_chunks.extend(chunks)
        print(f"  Extracted {len(chunks)} chunks from {md_file.name}")
    
    return all_chunks

def main():
    """Main ingestion pipeline."""
    # Configuration
    docs_dir = "../docs"
    vector_store_path = "../vector_store"
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    print("Starting RAG ingestion pipeline...")
    
    # Step 1: Process Markdown files
    print("\n1. Processing Markdown files...")
    chunks = process_markdown_files(docs_dir)
    print(f"Total chunks extracted: {len(chunks)}")
    
    # Step 2: Generate embeddings
    print("\n2. Generating embeddings...")
    embedding_gen = EmbeddingGenerator(api_key)
    
    texts = [chunk['content'] for chunk in chunks]
    embeddings = embedding_gen.generate_embeddings_batch(texts)
    
    # Step 3: Create and populate vector store
    print("\n3. Creating vector store...")
    vector_store = VectorStore()
    vector_store.add_embeddings(embeddings, chunks)
    
    # Step 4: Save vector store
    print("\n4. Saving vector store...")
    vector_store.save(vector_store_path)
    
    print("\n✅ Ingestion completed successfully!")
    print(f"Vector store saved to {vector_store_path}.index and {vector_store_path}.metadata")
    print(f"Total documents indexed: {len(vector_store.documents)}")

if __name__ == "__main__":
    main()