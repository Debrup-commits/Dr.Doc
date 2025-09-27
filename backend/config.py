"""
Configuration settings for the Doc-Reader backend system.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MeTTa Integration Settings
ENABLE_METTA = os.getenv('ENABLE_METTA', 'false').lower() in ('true', '1', 'yes', 'on')

# API Settings
API_PORT = int(os.getenv('API_PORT', '5001'))
RAG_PORT = int(os.getenv('RAG_PORT', '5000'))

# File Paths
VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', '../vector_store')
ATOMS_FILE = os.getenv('ATOMS_FILE', '../api_facts.metta')
DOCS_DIR = os.getenv('DOCS_DIR', '../docs')

# OpenAI Settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', 'gpt-3.5-turbo')

# Debug Settings
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() in ('true', '1', 'yes', 'on')

def get_metta_status():
    """Get MeTTa integration status message."""
    return "ENABLED" if ENABLE_METTA else "DISABLED"

def print_config():
    """Print current configuration."""
    print("🔧 Doc-Reader Configuration:")
    print(f"  MeTTa Integration: {get_metta_status()}")
    print(f"  API Port: {API_PORT}")
    print(f"  RAG Port: {RAG_PORT}")
    print(f"  Vector Store: {VECTOR_STORE_PATH}")
    print(f"  Atoms File: {ATOMS_FILE}")
    print(f"  Docs Directory: {DOCS_DIR}")
    print(f"  Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}")
    
    if not ENABLE_METTA:
        print("⚠️  MeTTa integration is DISABLED. Set ENABLE_METTA=true to enable.")
