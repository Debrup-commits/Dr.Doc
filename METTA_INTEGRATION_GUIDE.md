# MeTTa Integration Guide - Advanced API Documentation Analysis

This guide explains how to fully integrate MeTTa (Meta Type Theory) with the ethNewDelhi2025 system for sophisticated API documentation analysis and precise query answering.

## 🧠 What is MeTTa?

MeTTa is a symbolic reasoning system that provides:
- **Structured Knowledge Representation**: Facts are stored as atoms in a knowledge graph
- **Precise Querying**: Exact matching and logical reasoning over facts
- **Pattern Recognition**: Complex pattern matching and inference
- **Hybrid Intelligence**: Combines with RAG for comprehensive answers

## 🎯 MeTTa Integration Benefits

### **Precision vs. Retrieval**
- **RAG**: Great for general context and explanations
- **MeTTa**: Perfect for exact facts, patterns, and structured information

### **Use Cases for MeTTa**
1. **Security Patterns**: OAuth flows, authentication methods
2. **Performance Optimization**: Caching strategies, database patterns
3. **Error Codes**: Exact error mappings and descriptions
4. **Rate Limits**: Precise quota and limit information
5. **API Endpoints**: Exact endpoint specifications
6. **Monitoring Concepts**: Logging patterns, metrics definitions

## 🔧 Setup MeTTa Integration

### **Step 1: Enable MeTTa**

Edit your `.env` file:
```env
# Enable MeTTa integration
ENABLE_METTA=true
```

### **Step 2: Install MeTTa Dependencies**

```bash
pip install hyperon
```

### **Step 3: Ingest Documentation with MeTTa**

```bash
python backend/metta_ingest.py
```

This will:
- Parse all Markdown documentation files
- Extract structured facts as MeTTa atoms
- Save atoms to `api_facts.metta`

### **Step 4: Start Server with MeTTa**

```bash
python backend/app_agno_hybrid.py
```

You should see:
```
✅ MeTTa integration enabled and available
```

## 📊 MeTTa Knowledge Structure

### **Atom Types**

```metta
; Security patterns
(security_flow "oauth 2.0 pkce" "oauth2")
(auth_method "bearer token")
(auth_method "api key management")

; Performance patterns
(performance_pattern "caching" "memory cache")
(performance_pattern "database" "query optimization")

; Monitoring concepts
(monitoring_concept "logging" "structured logging")
(monitoring_concept "metrics" "performance metrics")

; Error codes
(error-code "/swap" "4003" "Invalid field value")

; Rate limits
(rate-limit "free" "100 requests/minute")

; Endpoints
(endpoint "/swap")
(method "/swap" "POST")
```

### **Query Patterns**

```metta
; Find all security flows
(security_flow $pattern $flow_type)

; Find error codes for specific endpoint
(error-code "/swap" $code $description)

; Find rate limits
(rate-limit $endpoint $limit $period)

; Find all endpoints
(endpoint $endpoint)
```

## 🚀 **Usage Examples**

### **Query Security Patterns:**
```python
# Query OAuth flows
security_patterns = kb.query_security_patterns()

# Query specific authentication methods
auth_methods = kb.query_authentication()
```

### **Query API Information:**
```python
# Get all endpoints
endpoints = kb.query_endpoints()

# Get error codes for specific endpoint
error_codes = kb.query_error_codes("/swap")

# Get rate limits
rate_limits = kb.query_rate_limits()
```

### **Advanced Pattern Queries:**
```python
# Natural language query
results = kb.query_advanced_patterns("What OAuth flows are supported?")
```

## 🔧 **Configuration Options**

### **Environment Variables:**
```env
# Enable/disable MeTTa
ENABLE_METTA=true

# MeTTa atoms file
ATOMS_FILE=../api_facts.metta

# Documentation directory
DOCS_DIR=../docs
```

### **MeTTa Settings:**
```python
# In backend/metta_ingest.py
class MeTTaKnowledgeBase:
    def __init__(self):
        self.metta = MeTTa()
        self.atoms = []
```

## 🧪 **Testing MeTTa Integration**

### **Test Fact Extraction:**
```bash
python backend/metta_ingest.py
```

### **Test Queries:**
```python
from backend.metta_ingest import MeTTaKnowledgeBase

kb = MeTTaKnowledgeBase()
kb.load_atoms_from_file("api_facts.metta")

# Test queries
endpoints = kb.query_endpoints()
print(f"Found {len(endpoints)} endpoints")
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **MeTTa Import Error:**
   ```bash
   pip install hyperon
   ```

2. **Atoms File Not Found:**
   ```bash
   python backend/metta_ingest.py
   ```

3. **No Facts Extracted:**
   - Check if docs directory exists
   - Verify Markdown files are present
   - Check file permissions

4. **Query Errors:**
   - Ensure atoms are loaded: `kb.load_atoms_from_file("api_facts.metta")`
   - Check MeTTa syntax in atoms file

## 📚 **Advanced Features**

### **Custom Fact Extractors:**
```python
def extract_custom_patterns(self, content: str, file_path: str) -> List[Atom]:
    """Extract custom patterns from documentation."""
    atoms = []
    # Add your custom extraction logic
    return atoms
```

### **Custom Query Methods:**
```python
def query_custom_patterns(self, pattern: str) -> List[Dict[str, Any]]:
    """Query custom patterns."""
    query = f"(custom_pattern {pattern} $result)"
    return self.query(query)
```

## 🔗 **Integration with RAG**

MeTTa works seamlessly with the Agno RAG system:

1. **Hybrid Responses**: MeTTa provides precise facts, RAG provides context
2. **Fallback Logic**: If MeTTa doesn't find facts, RAG handles the query
3. **Combined Results**: Both systems contribute to comprehensive answers

## 📖 **Additional Resources**

- [MeTTa Documentation](https://github.com/trueagi-io/hyperon)
- [Hyperon Python API](https://hyperon.readthedocs.io/)
- [Symbolic AI Concepts](https://en.wikipedia.org/wiki/Symbolic_artificial_intelligence)

