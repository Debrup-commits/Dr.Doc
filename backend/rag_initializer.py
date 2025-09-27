#!/usr/bin/env python3
"""
RAG Pipeline Initializer

Independent module for initializing the RAG pipeline before API startup.
This ensures the RAG system is fully ready and optimized before serving requests.

Author: Dr.Doc Team
"""

import os
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Local imports
from simple_rag import SimpleRAG
from metta_ingest import MeTTaFactExtractor, MeTTaKnowledgeBase
from simple_ingest import process_markdown_files, store_documents_in_db, generate_embeddings

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG system instance
rag_system = None
metta_kb = None
processing_status = {"initialized": False}

def initialize_rag_system():
    """Initialize the RAG system with BGE embeddings"""
    global rag_system
    
    try:
        logger.info("🔄 Initializing RAG system...")
        print("🔄 Initializing RAG system...")
        
        if rag_system is None:
            print("📡 Loading BGE embeddings and preparing the system for fast responses")
            rag_system = SimpleRAG()
            
            print("✅ RAG system initialized successfully!")
            logger.info("✅ RAG system initialized successfully")
        else:
            print("ℹ️ RAG system was already initialized")
            logger.info("ℹ️ RAG system was already initialized")
            
        return rag_system
        
    except Exception as e:
        error_msg = f"⚠️ Could not initialize RAG system: {e}"
        print(error_msg)
        logger.error(error_msg)
        raise e

async def initialize_documents(docs_dir_path: str = "../docs") -> bool:
    """Initialize documents and create MeTTa knowledge base"""
    global metta_kb, processing_status
    
    try:
        logger.info(f"🔄 Initializing documents from: {docs_dir_path}")
        print(f"🔄 Initializing documents from: {docs_dir_path}")
        
        # Validate docs directory
        docs_path = Path(docs_dir_path)
        if not docs_path.exists() or not docs_path.is_dir():
            error_msg = f"❌ Directory '{docs_dir_path}' does not exist or is not a directory."
            print(error_msg)
            logger.error(error_msg)
            return False
        
        # Check if system is already initialized
        if processing_status["initialized"]:
            success_msg = "✅ System already initialized. Documents are ready for Q&A."
            print(success_msg)
            logger.info(success_msg)
            return True
        
        # Initialize MeTTa knowledge graphs
        logger.info("📚 Creating MeTTa knowledge graphs...")
        print("📚 Creating MeTTa knowledge graphs...")
        metta_result = await create_metta_knowledge_base(docs_path)
        print(f"✅ MeTTa: {metta_result}")
        
        # Initialize RAG pipelines
        logger.info("🔍 Creating RAG pipelines...")
        print("🔍 Creating RAG pipelines...")
        rag_result = await create_rag_pipeline(docs_path)
        print(f"✅ RAG: {rag_result}")
        
        # Update status
        processing_status["initialized"] = True
        
        success_message = f"""
✅ Document Processing Complete!

📁 Processed Directory: {docs_dir_path}
🧠 MeTTa Knowledge Graph: {metta_result}
🔍 RAG Pipeline: {rag_result}

🎯 System Status: Ready for document Q&A queries
        """
        
        print(success_message.strip())
        logger.info("✅ Document processing completed successfully")
        return True
        
    except Exception as e:
        error_msg = f"❌ Document processing failed: {e}"
        print(error_msg)
        logger.error(error_msg)
        return False

async def create_metta_knowledge_base(docs_path: Path) -> str:
    """Create MeTTa knowledge base from documents"""
    global metta_kb
    
    try:
        # Check if MeTTa file already exists
        metta_file = Path("api_facts.metta")
        if metta_file.exists():
            logger.info("📚 MeTTa knowledge base already exists, loading...")
            print("📚 MeTTa knowledge base already exists, loading...")
            metta_kb = MeTTaKnowledgeBase()
            metta_kb.load_atoms_from_file(str(metta_file))
            return "Loaded existing MeTTa knowledge base"
        
        # Create new MeTTa knowledge base
        logger.info("📚 Creating new MeTTa knowledge base...")
        print("📚 Creating new MeTTa knowledge base...")
        extractor = MeTTaFactExtractor()
        atoms = extractor.extract_all_facts(str(docs_path))
        
        if not atoms:
            return "No MeTTa facts could be extracted from documents"
        
        metta_kb = MeTTaKnowledgeBase()
        metta_kb.load_atoms(atoms)
        metta_kb.save_atoms(str(metta_file))
        
        logger.info(f"💾 Created MeTTa knowledge base with {len(atoms)} facts")
        return f"Created MeTTa knowledge base with {len(atoms)} facts"
        
    except Exception as e:
        logger.error(f"❌ MeTTa knowledge base creation failed: {e}")
        raise e

async def create_rag_pipeline(docs_path: Path) -> str:
    """Create RAG pipeline from documents"""
    try:
        # Check if database already has documents
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost", port="5532", database="ai", 
                user="ai", password="ai"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            if doc_count > 0:
                logger.info(f"📚 RAG pipeline already exists with {doc_count} documents")
                print(f"📚 RAG pipeline already exists with {doc_count} documents")
                return f"RAG pipeline already exists with {doc_count} documents"
        except:
            pass
        
        # Create new RAG pipeline
        logger.info("📚 Creating new RAG pipeline...")
        print("📚 Creating new RAG pipeline...")
        
        # Process documents
        documents = process_markdown_files(str(docs_path))
        if not documents:
            return "No documents found for RAG processing"
        
        # Store in database
        if not store_documents_in_db(documents):
            return "Failed to store documents in database"
        
        # Generate embeddings
        if not generate_embeddings():
            return "Failed to generate embeddings"
        
        logger.info(f"💾 Created RAG pipeline with {len(documents)} documents")
        print(f"💾 Created RAG pipeline with {len(documents)} documents")
        return f"Created RAG pipeline with {len(documents)} documents"
        
    except Exception as e:
        logger.error(f"❌ RAG pipeline creation failed: {e}")
        raise e

def check_system_status():
    """Check if MeTTa files and RAG pipelines are properly set up"""
    try:
        # Check if MeTTa knowledge base exists
        metta_file = Path("api_facts.metta")
        metta_available = metta_file.exists() and metta_file.stat().st_size > 0
        
        # Check if RAG pipeline has documents
        rag_available = False
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost", port="5532", database="ai", 
                user="ai", password="ai"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            rag_available = doc_count > 0
        except Exception as e:
            logger.warning(f"Could not check database status: {e}")
        
        return {
            "docs_processed": metta_available and rag_available,
            "system_initialized": metta_available and rag_available,
            "metta_available": metta_available,
            "rag_available": rag_available
        }
        
    except Exception as e:
        logger.error(f"Error checking system status: {e}")
        return {
            "docs_processed": False,
            "system_initialized": False,
            "metta_available": False,
            "rag_available": False
        }

async def auto_process_documents_if_needed(docs_dir: str = "../docs"):
    """Auto-process documents if system status indicates they're needed"""
    try:
        print("🔍 Checking if documents need to be processed...")
        logger.info("🔍 Checking if documents need to be processed...")
        
        status = check_system_status()
        
        # Check if any critical status fields are False
        needs_processing = not status.get("docs_processed", False) or not status.get("system_initialized", False)
        
        if needs_processing:
            print("📚 System needs document processing. Auto-processing documents...")
            logger.info("📚 System needs document processing. Auto-processing documents...")
            
            docs_path = Path(docs_dir)
            if docs_path.exists() and docs_path.is_dir():
                print(f"🔄 Processing documents from: {docs_dir}")
                logger.info(f"🔄 Processing documents from: {docs_dir}")
                
                success = await initialize_documents(docs_dir)
                if success:
                    print("✅ Auto-processing completed successfully")
                    logger.info("✅ Auto-processing completed successfully")
                    return True
                else:
                    print("❌ Auto-processing failed")
                    logger.error("❌ Auto-processing failed")
                    return False
            else:
                print(f"⚠️ Docs directory not found or invalid: {docs_dir}")
                print("   Please create the docs directory and add documents, then call /api/process-documents")
                print("   System will be ready once documents are processed")
                logger.warning(f"Docs directory not found: {docs_dir}")
                return False
        else:
            print("✅ System is already fully initialized - no processing needed")
            logger.info("✅ System is already fully initialized - no processing needed")
            return True
            
    except Exception as e:
        error_msg = f"⚠️ Could not auto-process documents: {e}"
        print(error_msg)
        logger.error(error_msg)
        return False

async def full_initialization(docs_dir: str = "../docs"):
    """Complete initialization of RAG system and documents"""
    print("🚀 Starting full RAG system initialization...")
    logger.info("🚀 Starting full RAG system initialization...")
    
    try:
        # Step 1: Initialize RAG system
        rag_system = initialize_rag_system()
        
        # Step 2: Auto-process documents if needed
        docs_success = await auto_process_documents_if_needed(docs_dir)
        
        if docs_success:
            print("🎯 Full initialization completed successfully!")
            print("🚀 RAG system is ready to serve requests!")
            logger.info("🎯 Full initialization completed successfully!")
            return True
        else:
            print("⚠️ Initialization completed with warnings")
            print("   RAG system is ready, but documents may need manual processing")
            logger.warning("Initialization completed with warnings")
            return True
            
    except Exception as e:
        error_msg = f"❌ Full initialization failed: {e}"
        print(error_msg)
        logger.error(error_msg)
        return False

def get_rag_system():
    """Get the initialized RAG system instance"""
    return rag_system

def get_metta_kb():
    """Get the initialized MeTTa knowledge base instance"""
    return metta_kb

def get_processing_status():
    """Get the current processing status"""
    return processing_status.copy()

if __name__ == "__main__":
    print("🚀 RAG Pipeline Initializer")
    print("=" * 40)
    
    # Run full initialization
    asyncio.run(full_initialization())
