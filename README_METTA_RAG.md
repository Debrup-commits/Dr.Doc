# Metta+RAG Agent Integration

This project now includes the Metta+RAG agent system from the doc-reader project, providing intelligent document question answering capabilities.

## Features

- **MeTTa Knowledge Base**: Symbolic reasoning for precise API facts
- **RAG System**: Document retrieval and generation using Fetch.ai Agno framework
- **Hybrid Responses**: Combines MeTTa facts with RAG context for comprehensive answers
- **Fetch.ai Integration**: Uses ASI:One models for natural language processing
- **Agent Communication**: uAgents framework for autonomous operation

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the Agent System**:
   ```bash
   cd backend
   python start_agentic_system.py
   ```

4. **Access the API**:
   - API: http://localhost:5003
   - Agent Inspector: https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8001

## Configuration

### Environment Variables

- `ASI_ONE_API_KEY`: Fetch.ai ASI:One API key
- `OPENAI_API_KEY`: OpenAI API key (fallback)
- `AGENT_SEED_PHRASE`: Seed phrase for agent identity
- `ENABLE_METTA`: Enable MeTTa knowledge base (true/false)
- `USE_FETCHAI`: Use Fetch.ai models (true/false)

### Database Setup

The system uses PostgreSQL with pgvector extension:

```bash
# Install PostgreSQL and pgvector
# Create database
createdb ai
# Connect and enable pgvector
psql ai -c "CREATE EXTENSION vector;"
```

## API Endpoints

- `POST /api/ask` - Ask questions to the agent
- `GET /api/health` - Health check
- `GET /api/agent/status` - Agent status
- `GET /api/agent/info` - Agent information

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Adapter    │    │   uAgent        │
│   (Next.js)     │◄──►│   (Flask)        │◄──►│   (uAgents)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │  Hybrid QA      │
                                               │  System         │
                                               └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │  MeTTa + RAG    │
                                               │  Knowledge      │
                                               └─────────────────┘
```

## Components

- **doc_qa_agent.py**: Main uAgent implementation
- **app_agno_hybrid.py**: Hybrid QA system combining MeTTa and RAG
- **fetchai_agno_rag.py**: Fetch.ai Agno RAG implementation
- **metta_ingest.py**: MeTTa knowledge base management
- **agent_api_adapter.py**: Flask API adapter
- **start_agentic_system.py**: System startup manager

## Usage Examples

### Python Client
```python
from backend.agent_client import SyncDocumentQAClient

client = SyncDocumentQAClient("agent_address")
response = client.ask_question("What OAuth flows are supported?")
print(response['answer'])
```

### HTTP API
```bash
curl -X POST http://localhost:5003/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What authentication methods are available?"}'
```

## Troubleshooting

1. **Agent not starting**: Check API keys and database connection
2. **No responses**: Ensure documents are ingested into the knowledge base
3. **MeTTa errors**: Check if MeTTa is properly installed and configured
4. **Database errors**: Verify PostgreSQL is running and pgvector is installed

## Development

To extend the system:

1. Add new MeTTa patterns in `metta_ingest.py`
2. Extend RAG capabilities in `fetchai_agno_rag.py`
3. Add new agent behaviors in `doc_qa_agent.py`
4. Update API endpoints in `agent_api_adapter.py`

## License

This integration maintains the same license as the original doc-reader project.

