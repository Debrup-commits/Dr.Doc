#!/usr/bin/env python3
"""
Simple RAG Application using BGE embeddings
"""

import os
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
from simple_rag import SimpleRAG

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Simple RAG system
print("🚀 Initializing Simple RAG System...")
simple_rag = SimpleRAG()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple RAG Q&A</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .search-form {
            margin-bottom: 30px;
        }
        .search-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .search-input:focus {
            outline: none;
            border-color: #007bff;
        }
        .search-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        .search-button:hover {
            background: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }
        .answer {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .sources {
            margin-top: 20px;
        }
        .source {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .source-header {
            font-weight: bold;
            color: #333;
        }
        .source-details {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #f5c6cb;
        }
        .system-info {
            background: #e8f5e8;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 14px;
            color: #2e7d32;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Simple RAG Q&A System</h1>
        <div class="system-info">
            <strong>BGE Embeddings + PostgreSQL:</strong> This system uses BGE embeddings for semantic search 
            and PostgreSQL with pgvector for document storage and retrieval.
        </div>
        
        <form class="search-form" onsubmit="askQuestion(event)">
            <input type="text" id="question" class="search-input" 
                   placeholder="Ask about the documentation..." 
                   required>
            <button type="submit" class="search-button">Ask Question</button>
        </form>
        
        <div id="result"></div>
    </div>

    <script>
        async function askQuestion(event) {
            event.preventDefault();
            
            const question = document.getElementById('question').value;
            const resultDiv = document.getElementById('result');
            
            if (!question.trim()) return;
            
            // Show loading state
            resultDiv.innerHTML = '<div class="loading">Searching knowledge base...</div>';
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    displayResult(data);
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        function displayResult(data) {
            const resultDiv = document.getElementById('result');
            
            let sourcesHtml = '';
            if (data.sources && data.sources.length > 0) {
                sourcesHtml = '<div class="sources"><h3>Sources:</h3>';
                data.sources.forEach((source, index) => {
                    sourcesHtml += `
                        <div class="source">
                            <div class="source-header">${source.source}</div>
                            <div class="source-details">
                                Content: ${source.content}<br>
                                Score: ${(source.score || 0).toFixed(3)}
                            </div>
                        </div>
                    `;
                });
                sourcesHtml += '</div>';
            }
            
            resultDiv.innerHTML = `
                <div class="result">
                    <div class="answer">${data.answer}</div>
                    ${sourcesHtml}
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint for asking questions."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Process the question using Simple RAG
        result = simple_rag.query(question)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'system': 'simple_rag',
        'embedder': 'bge',
        'database': 'postgresql_pgvector'
    })

if __name__ == '__main__':
    print("🚀 Starting Simple RAG Server...")
    print("📍 Server will be available at: http://localhost:5003")
    app.run(debug=True, host='0.0.0.0', port=5003, use_reloader=False)
