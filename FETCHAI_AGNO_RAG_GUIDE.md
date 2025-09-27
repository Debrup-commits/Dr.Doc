# 🚀 Fetch.ai Agno RAG Integration Guide

## ✅ **Yes! We Can Use Fetch.ai RAG from the GitHub Repo**

The [fetchai/innovation-lab-examples repository](https://github.com/fetchai/innovation-lab-examples) provides a sophisticated RAG implementation using **Agno RAG framework** with **PgVector** database. This solves our OpenAI dependency issue!

## 🏗️ **What We Integrated**

### **From the GitHub Repository:**
- **Agno RAG Framework** - Fetch.ai's native RAG implementation
- **PgVector Database** - More scalable than FAISS
- **Hybrid Search** - Semantic + keyword search
- **uAgent Integration** - Native Fetch.ai agent protocol

### **Key Advantages:**
✅ **No OpenAI dependency** for embeddings (can use Fetch.ai models)  
✅ **PgVector database** - better than FAISS  
✅ **Hybrid search** - semantic + keyword  
✅ **Native Fetch.ai integration** - uAgent protocol  
✅ **Scalable architecture** - PostgreSQL backend  

## 🚀 **How to Use Fetch.ai Agno RAG**

### **Step 1: Install Dependencies**
```bash
# Install Agno RAG dependencies
pip install -r requirements-agno-minimal.txt
```

### **Step 2: Start PgVector Database**
```bash
# Start PostgreSQL with pgvector extension
docker-compose up -d
```

### **Step 3: Configure Environment**
```bash
# Copy Fetch.ai environment
cp env-fetchai-only.example .env

# Edit .env with your ASI:One API key
# ASI_ONE_API_KEY=your_actual_key_here
```

### **Step 4: Start Agno RAG System**
```bash
# Start Fetch.ai Agno RAG hybrid system
python backend/app_agno_hybrid.py
# Opens on: http://localhost:5003
```

## 📋 **System Comparison**

| Feature | Original FAISS | Fetch.ai Agno RAG |
|---------|----------------|-------------------|
| **Vector DB** | FAISS (local) | PgVector (PostgreSQL) |
| **Embeddings** | OpenAI only | Fetch.ai + OpenAI |
| **Search** | Semantic only | Hybrid (semantic + keyword) |
| **Scalability** | Limited | High (PostgreSQL) |
| **Agent Integration** | None | uAgent protocol |
| **Database** | Files | PostgreSQL |
| **Port** | 5002 | 5003 |

## 🔧 **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Web Frontend  │  │  Agentverse     │  │    ASI:One      │ │
│  │   (Next.js)     │  │  (Discovery)    │  │  (Agentic LLM)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FETCH.AI AGNO LAYER                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Agno RAG      │  │   PgVector      │  │   uAgent        │ │
│  │   Framework     │  │   Database      │  │   Protocol      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Fetch.ai      │  │   OpenAI        │  │   Automatic     │ │
│  │   ASI:One       │  │   (Fallback)    │  │   Fallback      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 **Available Commands**

### **For Fetch.ai Agno RAG System:**
```bash
# Terminal 1 - Start PgVector database
docker-compose up -d

# Terminal 2 - Start Agno RAG system
python backend/app_agno_hybrid.py
```

### **For MeTTa Integration:**
```bash
# Enable MeTTa in .env
ENABLE_METTA=true

# Install MeTTa dependencies
pip install hyperon

# Ingest documents with MeTTa
python backend/metta_ingest.py

# Start system with MeTTa
python backend/app_agno_hybrid.py
```

## 🔍 **Testing the System**

### **Test Agno RAG:**
```bash
python backend/fetchai_agno_rag.py
```

### **Test MeTTa:**
```bash
python backend/metta_ingest.py
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Database Connection Error:**
   - Ensure PostgreSQL is running: `docker-compose up -d`
   - Check port 5532 is available

2. **API Key Issues:**
   - Verify `ASI_ONE_API_KEY` is set in `.env`
   - Check API key is valid and not placeholder

3. **Import Errors:**
   - Install dependencies: `pip install -r requirements-agno-minimal.txt`
   - Check Python version compatibility

4. **MeTTa Issues:**
   - Install hyperon: `pip install hyperon`
   - Check `ENABLE_METTA=true` in `.env`

## 📚 **Additional Resources**

- [Fetch.ai ASI:One Documentation](https://docs.fetch.ai/asi-one/)
- [Agno RAG Framework](https://github.com/fetchai/innovation-lab-examples)
- [PgVector Documentation](https://github.com/pgvector/pgvector)
- [MeTTa Documentation](https://github.com/trueagi-io/hyperon)

