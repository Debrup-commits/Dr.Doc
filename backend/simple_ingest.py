#!/usr/bin/env python3
"""
Dr.Doc Document Ingestion

Clean document processing utilities for RAG pipeline.
Handles markdown parsing, database storage, and embedding generation.

Author: Dr.Doc Team
"""

import os
import sys
import json
import markdown
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Configuration
load_dotenv()

def process_markdown_files(docs_dir: str):
    """Process all markdown files in the docs directory"""
    print(f"📄 Processing markdown files from {docs_dir}...")
    
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"❌ Directory {docs_dir} not found")
        return []
    
    documents = []
    
    for md_file in docs_path.glob("*.md"):
        print(f"  Processing {md_file.name}...")
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert Markdown to HTML then to text
            html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            
            # Clean up the text
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            
            document = {
                'content': text,
                'metadata': {
                    'source': str(md_file),
                    'type': 'markdown',
                    'title': md_file.stem,
                    'filename': md_file.name
                }
            }
            
            documents.append(document)
            print(f"    ✅ Processed {md_file.name} ({len(text)} characters)")
            
        except Exception as e:
            print(f"    ❌ Failed to process {md_file.name}: {e}")
    
    print(f"📚 Total documents processed: {len(documents)}")
    return documents

def store_documents_in_db(documents):
    """Store documents in the PostgreSQL database"""
    print("🗄️  Storing documents in database...")
    
    try:
        import psycopg2
        from psycopg2.extras import Json
        
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port="5532",
            database="ai",
            user="ai",
            password="ai"
        )
        
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                metadata JSONB,
                embedding VECTOR(768),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Clear existing documents
        cursor.execute("DELETE FROM documents")
        print("  🗑️  Cleared existing documents")
        
        # Insert new documents
        for doc in documents:
            cursor.execute("""
                INSERT INTO documents (content, metadata)
                VALUES (%s, %s)
            """, (doc['content'], Json(doc['metadata'])))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Stored {len(documents)} documents in database")
        return True
        
    except Exception as e:
        print(f"❌ Failed to store documents: {e}")
        return False

def generate_embeddings():
    """Generate embeddings for all documents using BGE"""
    print("🧠 Generating embeddings with BGE...")
    
    try:
        from bge_embedder import BGEEmbedder
        import psycopg2
        import numpy as np
        
        # Initialize BGE embedder
        embedder = BGEEmbedder()
        
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port="5532",
            database="ai",
            user="ai",
            password="ai"
        )
        
        cursor = conn.cursor()
        
        # Get all documents
        cursor.execute("SELECT id, content FROM documents WHERE embedding IS NULL")
        documents = cursor.fetchall()
        
        print(f"  📄 Found {len(documents)} documents to embed")
        
        # Generate embeddings in batches
        batch_size = 10
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Extract content
            contents = [doc[1] for doc in batch]
            
            # Generate embeddings
            embeddings = embedder.embed_documents(contents)
            
            # Update database with embeddings
            for (doc_id, _), embedding in zip(batch, embeddings):
                cursor.execute("""
                    UPDATE documents 
                    SET embedding = %s 
                    WHERE id = %s
                """, (embedding, doc_id))
            
            print(f"    ✅ Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Embeddings generated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate embeddings: {e}")
        return False

def test_rag_system():
    """Test the RAG system with a sample query"""
    print("🧪 Testing RAG system...")
    
    try:
        from bge_embedder import BGEEmbedder
        import psycopg2
        import numpy as np
        
        # Initialize BGE embedder
        embedder = BGEEmbedder()
        
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port="5532",
            database="ai",
            user="ai",
            password="ai"
        )
        
        cursor = conn.cursor()
        
        # Test query
        query = "What is ASI:One?"
        print(f"  🔍 Query: {query}")
        
        # Generate query embedding
        query_embedding = embedder.embed_query(query)
        
        # Search for similar documents
        cursor.execute("""
            SELECT content, metadata, 
                   embedding <=> %s::vector as distance
            FROM documents 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT 3
        """, (query_embedding, query_embedding))
        
        results = cursor.fetchall()
        
        if results:
            print(f"  ✅ Found {len(results)} relevant documents")
            for i, (content, metadata, distance) in enumerate(results, 1):
                print(f"    {i}. {metadata.get('filename', 'Unknown')} (distance: {distance:.3f})")
                print(f"       Content preview: {content[:100]}...")
        else:
            print("  ❌ No relevant documents found")
        
        cursor.close()
        conn.close()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False

def main():
    """Main ingestion function"""
    print("🚀 Starting Simple Document Ingestion")
    print("=" * 50)
    
    # Step 1: Process markdown files
    docs_dir = "../docs"
    documents = process_markdown_files(docs_dir)
    
    if not documents:
        print("❌ No documents to process")
        return False
    
    # Step 2: Store documents in database
    if not store_documents_in_db(documents):
        print("❌ Failed to store documents")
        return False
    
    # Step 3: Generate embeddings
    if not generate_embeddings():
        print("❌ Failed to generate embeddings")
        return False
    
    # Step 4: Test RAG system
    if not test_rag_system():
        print("❌ RAG system test failed")
        return False
    
    print("\n🎉 Document ingestion completed successfully!")
    print("📚 Documents are now ready for RAG queries")
    
    return True

if __name__ == "__main__":
    main()

