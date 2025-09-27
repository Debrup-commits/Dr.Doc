# Dr.Doc Backend

A clean, minimal MCP-based backend implementation for document processing and Q&A.

## Architecture

The backend consists of 7 core modules:

- **`mcp_server.py`** - Core MCP server with two endpoints
- **`api_wrapper.py`** - Flask HTTP wrapper for frontend integration  
- **`simple_rag.py`** - RAG system using BGE embeddings
- **`metta_ingest.py`** - MeTTa knowledge base for symbolic reasoning
- **`simple_ingest.py`** - Document processing utilities
- **`start_system.py`** - Unified startup script
- **`dr_doc_agent.py`** - uAgent implementation with MCP integration
- **`server.py`** - Server wrapper for uAgent compatibility

## Core Endpoints

### 1. Document Processing (`process_documents`)
- **Purpose**: Idempotent document processing (MeTTa + RAG)
- **Input**: `docs_dir_path` (string)
- **Output**: Processing status and results
- **Features**: Creates MeTTa knowledge graphs and RAG pipelines

### 2. Dr.Doc Agent (`ask_dr_doc`)
- **Purpose**: ASI:One powered document Q&A
- **Input**: `question` (string), `session_id` (optional)
- **Output**: Comprehensive answer combining RAG + MeTTa
- **Features**: Integrated document retrieval and symbolic reasoning

## Quick Start

1. **Environment Setup**:
   ```bash
   cp ../env-fetchai-only.example .env
   # Edit .env with your ASI_ONE_API_KEY
   ```

2. **Database Setup**:
   ```bash
   docker-compose up -d  # Start PostgreSQL with pgvector
   ```

3. **Start System**:
   ```bash
   python3 start_system.py init       # Initialize RAG pipeline first
   python3 start_system.py api        # HTTP API wrapper
   python3 start_system.py mcp        # MCP server (stdio)
   python3 start_system.py uagent     # uAgent with MCP integration
   python3 start_system.py test-uagent # Test uAgent integration
   ```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/status` - System status
- `POST /api/process-documents` - Process documents
- `POST /api/ask` - Ask questions to Dr.Doc

## uAgent Integration

The system supports uAgent integration for deployment on Agentverse:

### Prerequisites
```bash
pip install uagents uagents-adapter fastmcp
```

### Usage
```bash
# Test uAgent integration
python3 start_system.py test-uagent

# Run uAgent
python3 start_system.py uagent
```

### Features
- **MCP Server Adapter**: Converts MCP server to uAgent-compatible interface
- **ASI:One Integration**: Uses ASI:One API for agent communication
- **RAG + MeTTa**: Full document processing and symbolic reasoning
- **Agentverse Deployment**: Ready for deployment on Fetch.ai's Agentverse

## Dependencies

Essential Python packages:
- `fastmcp` - MCP server framework
- `flask` - HTTP API wrapper
- `flask-cors` - CORS support
- `psycopg2` - PostgreSQL client
- `openai` - ASI:One integration
- `hyperon` - MeTTa symbolic reasoning
- `transformers` - BGE embeddings
- `torch` - ML framework

## File Structure

```
backend/
├── mcp_server.py      # Core MCP server
├── api_wrapper.py     # HTTP API wrapper
├── simple_rag.py      # RAG system
├── metta_ingest.py    # MeTTa knowledge base
├── simple_ingest.py   # Document processing
├── start_system.py    # Startup script
├── api_facts.metta    # MeTTa knowledge file
└── README.md          # This file
```

## Configuration

Set the following environment variables:
- `ASI_ONE_API_KEY` - Your ASI:One API key (required)
- Database settings (defaults to localhost PostgreSQL)

## Development

The codebase follows clean architecture principles:
- Minimal dependencies
- Clear separation of concerns
- Consistent naming conventions
- Comprehensive error handling
- Detailed logging
