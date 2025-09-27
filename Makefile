# Makefile for Metta+RAG Agent System

.PHONY: help install setup start stop test clean

help: ## Show this help message
	@echo "Metta+RAG Agent System Commands:"
	@echo "================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

setup: ## Setup the system (install deps and create .env)
	@echo "🔧 Setting up Metta+RAG system..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env file with your API keys"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Setup complete"

start: ## Start the Metta+RAG agent system
	@echo "🚀 Starting Metta+RAG system..."
	python start_metta_rag.py

start-backend: ## Start only the backend system
	@echo "🤖 Starting backend system..."
	cd backend && python start_agentic_system.py

start-agent: ## Start only the uAgent
	@echo "🤖 Starting uAgent..."
	cd backend && python doc_qa_agent.py

start-api: ## Start only the API adapter
	@echo "🌐 Starting API adapter..."
	cd backend && python agent_api_adapter.py

test: ## Test the system
	@echo "🧪 Testing Metta+RAG system..."
	cd backend && python -c "from app_agno_hybrid import AgnoHybridQASystem; qa = AgnoHybridQASystem(); print('✅ System test passed')"

test-rag: ## Test RAG system
	@echo "🧪 Testing RAG system..."
	cd backend && python fetchai_agno_rag.py

test-metta: ## Test MeTTa system
	@echo "🧪 Testing MeTTa system..."
	cd backend && python metta_ingest.py

ingest: ## Ingest documents into the knowledge base
	@echo "📚 Ingesting documents..."
	cd backend && python ingest.py

stop: ## Stop all running processes
	@echo "🛑 Stopping all processes..."
	@pkill -f "python.*start_metta_rag.py" || true
	@pkill -f "python.*start_agentic_system.py" || true
	@pkill -f "python.*doc_qa_agent.py" || true
	@pkill -f "python.*agent_api_adapter.py" || true
	@echo "✅ All processes stopped"

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	@echo "✅ Cleanup complete"

status: ## Check system status
	@echo "📊 System Status:"
	@echo "================="
	@echo "Python processes:"
	@ps aux | grep -E "python.*(start_metta_rag|doc_qa_agent|agent_api_adapter)" | grep -v grep || echo "No processes running"
	@echo ""
	@echo "Port usage:"
	@lsof -i :5003 2>/dev/null || echo "Port 5003: Available"
	@lsof -i :8001 2>/dev/null || echo "Port 8001: Available"

logs: ## Show system logs (if available)
	@echo "📋 System logs:"
	@echo "==============="
	@if [ -f "system.log" ]; then \
		tail -n 50 system.log; \
	else \
		echo "No log file found"; \
	fi

health: ## Check system health
	@echo "💚 Health Check:"
	@echo "================"
	@curl -s http://localhost:5003/api/health 2>/dev/null | python -m json.tool || echo "❌ API not responding"

# Development targets
dev-setup: setup ## Development setup with additional tools
	@echo "🔧 Setting up development environment..."
	pip install -r requirements.txt
	pip install pytest black flake8 mypy
	@echo "✅ Development setup complete"

format: ## Format Python code
	@echo "🎨 Formatting Python code..."
	black backend/*.py
	@echo "✅ Code formatted"

lint: ## Lint Python code
	@echo "🔍 Linting Python code..."
	flake8 backend/*.py
	@echo "✅ Linting complete"

type-check: ## Type check Python code
	@echo "🔍 Type checking Python code..."
	mypy backend/*.py
	@echo "✅ Type checking complete"

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "See README_METTA_RAG.md for detailed documentation"
	@echo "✅ Documentation available"

# Database targets
db-setup: ## Setup PostgreSQL database
	@echo "🗄️  Setting up PostgreSQL database..."
	@echo "Please ensure PostgreSQL is installed and running"
	@echo "Then run: createdb ai && psql ai -c 'CREATE EXTENSION vector;'"
	@echo "✅ Database setup instructions provided"

db-reset: ## Reset the database
	@echo "🗄️  Resetting database..."
	@echo "⚠️  This will delete all data in the 'ai' database"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] && dropdb ai && createdb ai && psql ai -c 'CREATE EXTENSION vector;' || echo "Database reset cancelled"





