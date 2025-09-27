# 🤖 Agent Integration Guide - RAG/MeTTa Systems

This guide explains how to integrate and use the RAG/MeTTa systems in the ethNewDelhi2025 project for agent-based query answering.

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   uAgent        │  │   API Adapter   │  │   Direct        │ │
│  │   (Autonomous)  │  │   (REST API)    │  │   Interface     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED INTERFACE                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Agent RAG     │  │   Query Type    │  │   Result        │ │
│  │   Interface     │  │   Detection     │  │   Formatting    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE SYSTEMS                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   MeTTa KB      │  │   Agno RAG      │  │   FAISS         │ │
│  │   (Symbolic)    │  │   (Neural)      │  │   (Fallback)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Install dependencies
pip install -r requirements-agno-minimal.txt

# Configure environment
cp env-fetchai-only.example .env
# Edit .env with your ASI_ONE_API_KEY

# Start database
docker-compose up -d
```

### **2. Start the Systems**
```bash
# Option 1: One-command startup
python start_metta_rag.py

# Option 2: Manual startup
# Terminal 1: Start uAgent
python backend/doc_qa_agent.py

# Terminal 2: Start API adapter
python backend/agent_api_adapter.py

# Terminal 3: Start hybrid system
python backend/app_agno_hybrid.py
```

## 🔧 **Integration Methods**

### **Method 1: Direct Interface (Recommended)**

```python
from backend.agent_rag_interface import get_agent_interface, QueryType

# Initialize interface
interface = get_agent_interface()

# Query with auto-detection
result = interface.query("What OAuth flows are supported?")

# Query with specific type
result = interface.query(
    question="What are the rate limits?",
    query_type=QueryType.METTA,
    context="API documentation",
    user_id="user123"
)

print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
print(f"Facts: {len(result.facts)}")
print(f"Sources: {len(result.sources)}")
```

### **Method 2: REST API**

```python
import requests

# Ask a question
response = requests.post('http://localhost:5001/api/ask', json={
    'question': 'What OAuth flows are supported?',
    'query_type': 'hybrid',
    'context': 'API documentation',
    'user_id': 'user123'
})

result = response.json()
print(f"Answer: {result['answer']}")
```

### **Method 3: uAgent Communication**

```python
from uagents import Agent, Context, Model
from backend.doc_qa_agent import QuestionRequest, QuestionResponse

# Create your agent
my_agent = Agent(name="MyAgent", seed="your-seed")

@my_agent.on_message(model=QuestionResponse)
async def handle_response(ctx: Context, sender: str, msg: QuestionResponse):
    print(f"Answer: {msg.answer}")
    print(f"Confidence: {msg.confidence}")

# Send question to Document Q&A agent
async def ask_question(question: str):
    await my_agent.send(
        "agent1q...",  # Document Q&A agent address
        QuestionRequest(question=question, query_type="hybrid")
    )
```

## 📊 **Query Types**

### **Auto Detection (Recommended)**
```python
# Automatically detects best query type
result = interface.query("What OAuth flows are supported?")
# Uses hybrid for security patterns
```

### **RAG Only**
```python
# For comprehensive, contextual answers
result = interface.query(
    question="How do I implement authentication?",
    query_type=QueryType.RAG
)
```

### **MeTTa Only**
```python
# For precise facts and structured data
result = interface.query(
    question="What error codes does /swap return?",
    query_type=QueryType.METTA
)
```

### **Hybrid (Best Results)**
```python
# Combines MeTTa facts with RAG context
result = interface.query(
    question="What OAuth flows are supported?",
    query_type=QueryType.HYBRID
)
```

## 🧠 **MeTTa Knowledge Base**

### **Available Fact Types**
- **Security Patterns**: OAuth flows, authentication methods
- **Performance Patterns**: Caching strategies, optimization
- **Monitoring Concepts**: Logging, metrics, observability
- **Error Codes**: HTTP status codes and descriptions
- **Rate Limits**: API quotas and limits
- **API Endpoints**: Available endpoints and methods

### **Querying MeTTa Facts**
```python
# Direct MeTTa queries
if interface.metta_kb:
    # Get all endpoints
    endpoints = interface.metta_kb.query_endpoints()
    
    # Get error codes for specific endpoint
    error_codes = interface.metta_kb.query_error_codes("/swap")
    
    # Get security patterns
    security_patterns = interface.metta_kb.query_security_patterns()
    
    # Advanced pattern queries
    results = interface.metta_kb.query_advanced_patterns("OAuth authentication")
```

## 🔍 **RAG System**

### **Agno RAG (Primary)**
- **Vector Database**: PgVector (PostgreSQL)
- **Embeddings**: BGE (free, local)
- **LLM**: Fetch.ai ASI:One
- **Search**: Hybrid (semantic + keyword)

### **FAISS RAG (Fallback)**
- **Vector Database**: FAISS (local files)
- **Embeddings**: OpenAI (requires API key)
- **LLM**: OpenAI GPT models
- **Search**: Semantic only

### **Document Processing**
```python
# Ingest documents
success = interface.ingest_documents("../docs")

# Extract MeTTa facts
success = interface.extract_metta_facts("../docs")
```

## 📡 **API Endpoints**

### **Core Endpoints**
- `POST /api/ask` - Ask a question
- `POST /api/ask/stream` - Streaming questions
- `GET /api/health` - Health check
- `GET /api/status` - System status

### **Management Endpoints**
- `POST /api/ingest` - Ingest documents
- `POST /api/extract-facts` - Extract MeTTa facts
- `GET /api/query-types` - Available query types
- `GET /api/examples` - Example questions

### **Example API Usage**
```bash
# Health check
curl http://localhost:5001/api/health

# Ask question
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What OAuth flows are supported?", "query_type": "hybrid"}'

# Ingest documents
curl -X POST http://localhost:5001/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"docs_dir": "../docs"}'
```

## 🎯 **Use Cases**

### **1. API Documentation Q&A**
```python
# Questions about API endpoints, parameters, errors
questions = [
    "What endpoints are available?",
    "What parameters does /swap accept?",
    "What error codes can /swap return?",
    "What are the rate limits?"
]
```

### **2. Security Analysis**
```python
# Questions about authentication and security
questions = [
    "What OAuth flows are supported?",
    "How do I authenticate with the API?",
    "What security patterns are implemented?",
    "What authentication methods are available?"
]
```

### **3. Performance Optimization**
```python
# Questions about performance and optimization
questions = [
    "What caching strategies are used?",
    "How can I optimize API performance?",
    "What monitoring concepts are implemented?",
    "What performance patterns are available?"
]
```

### **4. Implementation Guidance**
```python
# Questions about implementation and usage
questions = [
    "How do I implement OAuth 2.0?",
    "How do I handle rate limiting?",
    "How do I implement error handling?",
    "How do I monitor API performance?"
]
```

## 🔧 **Configuration**

### **Environment Variables**
```env
# Fetch.ai Configuration
ASI_ONE_API_KEY=your_fetchai_key_here
USE_FETCHAI=true
REQUIRE_OPENAI_FALLBACK=false

# MeTTa Configuration
ENABLE_METTA=true

# Agent Configuration
AGENT_ADDRESS=agent1q...
AGENT_SEED=your-agent-seed

# Database Configuration
DB_URL=postgresql+psycopg://ai:ai@localhost:5532/ai
```

### **Query Type Detection**
The system automatically detects the best query type based on question patterns:

- **Security/Auth questions** → Hybrid (MeTTa + RAG)
- **Error codes/Rate limits** → MeTTa
- **General questions** → RAG
- **Implementation questions** → RAG

## 🧪 **Testing**

### **Test Individual Components**
```bash
# Test MeTTa system
python backend/metta_ingest.py

# Test RAG system
python backend/fetchai_agno_rag.py

# Test agent interface
python backend/agent_rag_interface.py
```

### **Test Complete System**
```bash
# Test hybrid system
python backend/app_agno_hybrid.py

# Test agent
python backend/doc_qa_agent.py

# Test API adapter
python backend/agent_api_adapter.py
```

### **Example Test Questions**
```python
test_questions = [
    "What OAuth flows are supported?",
    "What are the rate limits for the free tier?",
    "How do I authenticate with the API?",
    "What error codes can the /swap endpoint return?",
    "What caching strategies are implemented?",
    "How do I implement monitoring?",
    "What performance optimization patterns are available?",
    "What security patterns are used?"
]
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **RAG System Not Initialized**
   ```bash
   # Check database
   docker-compose up -d
   
   # Check API keys
   echo $ASI_ONE_API_KEY
   ```

2. **MeTTa Not Available**
   ```bash
   # Install MeTTa
   pip install hyperon
   
   # Extract facts
   python backend/metta_ingest.py
   ```

3. **Agent Communication Failed**
   ```bash
   # Check agent address
   echo $AGENT_ADDRESS
   
   # Check agent status
   curl http://localhost:5001/api/health
   ```

4. **No Documents Found**
   ```bash
   # Check docs directory
   ls -la docs/
   
   # Ingest documents
   curl -X POST http://localhost:5001/api/ingest
   ```

## 📚 **Additional Resources**

- [Fetch.ai Agno RAG Guide](FETCHAI_AGNO_RAG_GUIDE.md)
- [MeTTa Integration Guide](METTA_INTEGRATION_GUIDE.md)
- [System Overview](README_METTA_RAG.md)
- [API Documentation](docs/)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Add your agent integration
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is part of the ethNewDelhi2025 initiative and follows the project's licensing terms.

