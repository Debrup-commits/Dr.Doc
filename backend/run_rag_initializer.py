#!/usr/bin/env python3
"""
RAG Initializer Runner

Independent script to initialize the RAG pipeline before starting the API server.
This ensures optimal performance by having the RAG system ready beforehand.

Usage:
    python run_rag_initializer.py [docs_directory]

Author: Dr.Doc Team
"""

import sys
import asyncio
from pathlib import Path
from rag_initializer import full_initialization

def main():
    """Main function to run RAG initialization"""
    # Get docs directory from command line or use default
    docs_dir = "../docs"
    if len(sys.argv) > 1:
        docs_dir = sys.argv[1]
    
    print("🚀 RAG Pipeline Initializer")
    print("=" * 50)
    print(f"📁 Docs directory: {docs_dir}")
    print(f"📁 Absolute path: {Path(docs_dir).resolve()}")
    print()
    
    # Run full initialization
    try:
        success = asyncio.run(full_initialization(docs_dir))
        
        if success:
            print("\n🎯 Initialization completed successfully!")
            print("🚀 RAG system is ready to serve requests!")
            print("\n💡 You can now start the API server:")
            print("   python start_system.py api")
            return 0
        else:
            print("\n❌ Initialization failed!")
            print("   Please check the logs and try again")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Initialization interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during initialization: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
