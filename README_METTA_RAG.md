# 🚀 ethNewDelhi2025 - Metta+RAG System

A sophisticated document ingestion and query system that combines **MeTTa symbolic reasoning** with **Fetch.ai Agno RAG** for precise API documentation analysis without requiring OpenAI keys.

## ✨ **Key Features**

- 🧠 **MeTTa Integration**: Symbolic reasoning for precise fact extraction
- 🤖 **Fetch.ai Agno RAG**: Advanced RAG with PgVector database
- 🔓 **No OpenAI Required**: Uses Fetch.ai ASI:One + BGE embeddings
- 📊 **Hybrid Intelligence**: Combines symbolic and neural approaches
- 🚀 **Easy Setup**: One-command startup with automatic configuration

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Web Frontend  │  │   MeTTa Facts   │  │   RAG Context   │ │
│  │   (Next.js)     │  │   (Precise)     │  │   (General)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HYBRID SYSTEM                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   MeTTa KB      │  │   Agno RAG      │  │   PgVector      │ │
│  │   (Symbolic)    │  │   (Neural)      │  │   (Database)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Fetch.ai      │  │   BGE Embedder  │  │   Hyperon       │ │
│  │   ASI:One       │  │   (Free)        │  │   (MeTTa)       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### **Option 1: One-Command Setup**
```bash
# Clone and setup everything automatically
python start_metta_rag.py
```

### **Option 2: Manual Setup**
```bash
# 1. Install dependencies
pip install -r requirements-agno-minimal.txt

# 2. Start database
docker-compose up -d

# 3. Configure environment
cp env-fetchai-only.example .env
# Edit .env with your ASI_ONE_API_KEY

# 4. Ingest documents (optional)
python backend/metta_ingest.py

# 5. Start server
python backend/app_agno_hybrid.py
```

## 🔧 **Configuration**

### **Environment Setup**
```bash
# Copy configuration
cp env-fetchai-only.example .env

# Edit .env file
ASI_ONE_API_KEY=your_actual_fetchai_key_here
USE_FETCHAI=true
REQUIRE_OPENAI_FALLBACK=false
ENABLE_METTA=true  # Enable MeTTa integration
```

### **Available Configurations**

| File | Description | Use Case |
|------|-------------|----------|
| `env-fetchai-only.example` | Pure Fetch.ai setup | No OpenAI dependency |
| `env-enhanced.example` | Enhanced with fallback | OpenAI fallback support |

## 📚 **Document Ingestion**

### **MeTTa Fact Extraction**
```bash
# Extract structured facts from documentation
python backend/metta_ingest.py
```

**Extracted Facts:**
- API endpoints and methods
- Error codes and descriptions
- Rate limits and tiers
- Security patterns (OAuth, auth methods)
- Performance patterns (caching, optimization)
- Monitoring concepts (logging, metrics)

### **RAG Document Processing**
```bash
# Process documents for RAG
python backend/fetchai_agno_rag.py
```

**Features:**
- Markdown to text conversion
- BGE embedding generation
- PgVector storage
- Hybrid search (semantic + keyword)

## 🧠 **MeTTa Knowledge Base**

### **Atom Types**
```metta
; API endpoints
(endpoint "/swap")
(method "/swap" "POST")

; Error codes
(error-code "/swap" "400" "Invalid request")

; Rate limits
(rate-limit "free" "100" "minute")

; Security patterns
(security_flow "oauth 2.0 pkce" "oauth2")
(auth_method "bearer token")

; Performance patterns
(performance_pattern "caching" "memory cache")
```

### **Query Examples**
```python
# Query all endpoints
endpoints = kb.query_endpoints()

# Query error codes for specific endpoint
error_codes = kb.query_error_codes("/swap")

# Query security patterns
security_patterns = kb.query_security_patterns()

# Advanced pattern queries
results = kb.query_advanced_patterns("What OAuth flows are supported?")
```

## 🔍 **System Components**

### **Backend Files**
- `backend/metta_ingest.py` - MeTTa fact extraction
- `backend/bge_embedder.py` - Free BGE embeddings
- `backend/fetchai_agno_rag.py` - Agno RAG system
- `backend/app_agno_hybrid.py` - Hybrid server

### **Configuration Files**
- `env-fetchai-only.example` - Pure Fetch.ai config
- `env-enhanced.example` - Enhanced config with fallback
- `docker-compose.yml` - PostgreSQL with PgVector
- `requirements-agno-minimal.txt` - Minimal dependencies

### **Data Files**
- `api_facts.metta` - Extracted MeTTa facts
- `docs/` - Documentation files (Markdown)

## 🧪 **Testing**

### **Test MeTTa System**
```bash
python backend/metta_ingest.py
```

### **Test RAG System**
```bash
python backend/fetchai_agno_rag.py
```

### **Test Complete System**
```bash
python start_metta_rag.py
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker-compose up -d
   docker ps
   ```

2. **API Key Issues**
   ```bash
   # Verify API key in .env
   cat .env | grep ASI_ONE_API_KEY
   ```

3. **Import Errors**
   ```bash
   # Install dependencies
   pip install -r requirements-agno-minimal.txt
   ```

4. **MeTTa Issues**
   ```bash
   # Install MeTTa
   pip install hyperon
   ```

### **Port Conflicts**
- **PostgreSQL**: 5532
- **Main Server**: 5003
- **API Server**: 5001

## 📖 **Documentation**

- [Fetch.ai Agno RAG Guide](FETCHAI_AGNO_RAG_GUIDE.md)
- [MeTTa Integration Guide](METTA_INTEGRATION_GUIDE.md)
- [API Documentation](docs/)

## 🔗 **External Resources**

- [Fetch.ai ASI:One](https://docs.fetch.ai/asi-one/)
- [Agno RAG Framework](https://github.com/fetchai/innovation-lab-examples)
- [MeTTa/Hyperon](https://github.com/trueagi-io/hyperon)
- [PgVector](https://github.com/pgvector/pgvector)

## 🎯 **Use Cases**

1. **API Documentation Analysis**: Precise fact extraction and querying
2. **Developer Support**: Intelligent Q&A about APIs
3. **Code Generation**: Structured information for code generation
4. **Security Analysis**: Authentication and authorization patterns
5. **Performance Optimization**: Caching and database patterns

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is part of the ethNewDelhi2025 initiative and follows the project's licensing terms.