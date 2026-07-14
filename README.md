# 🚀 AI Agent Vector System

A production-ready Retrieval-Augmented Generation (RAG) system for building AI agents with long-term memory using PostgreSQL + pgvector and local LLMs.

---

## 📚 Table of Contents
- [Overview](#-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Monitoring](#-monitoring)
- [Use Cases](#-example-use-cases)
- [Contributing](#-contributing)
- [License](#-license)

## 📋 Overview

This system enables your AI agent to:
- **Ingest** documents (text files, PDFs, websites)
- **Remember** information using a vector database
- **Retrieve** relevant context when answering questions
- **Reason** using local LLMs (no API costs)
- **Scale** from prototype to production

**Status:** ✅ Fully Operational

---

flowchart LR
    User[User] --> API[FastAPI]
    
    subgraph Core["AI Agent System"]
        API --> Agent[AI Agent Core]
        Agent --> DB[("PostgreSQL + pgvector")]
        Agent --> Ollama[Ollama]
    end
    
    subgraph Models["LLM Models"]
        Ollama --> Embed[nomic-embed-text]
        Ollama --> Chat[llama3.2:1b]
    end
    
    subgraph Monitor["Observability"]
        Prom[Prometheus] --> Graf[Grafana]
        API -.-> Prom
        Agent -.-> Prom
        DB -.-> Prom
        Ollama -.-> Prom
    end

## 🛠️ Tech Stack

| Component | Technology | Version |
| :--- | :--- | :--- |
| **API Framework** | FastAPI | 0.104.1 |
| **Server** | Uvicorn | 0.24.0 |
| **Database** | PostgreSQL + pgvector | 16 |
| **ORM** | SQLAlchemy | 2.0.23 |
| **LLM Runtime** | Ollama | Latest |
| **Embedding Model** | nomic-embed-text | 768 dims |
| **Chat Model** | llama3.2:1b | 1B params |
| **Containerization** | Docker Compose | 3.8 |
| **Monitoring** | Prometheus + Grafana | Latest |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- At least **8GB RAM** (16GB recommended)
- **10GB free disk space**
- **Git**

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-agent-vector-system.git
cd ai-agent-vector-system

# Make setup script executable
chmod +x scripts/setup.sh

# Run the setup (this will pull models and start everything)
./scripts/setup.sh

# 1. Create environment file
cp .env.example .env

# 2. Start the database and Ollama
docker compose up -d postgres ollama

# 3. Wait for services to be ready
sleep 10

# 4. Pull the embedding model
docker exec ollama_server ollama pull nomic-embed-text

# 5. Pull a lightweight chat model
docker exec ollama_server ollama pull llama3.2:1b

# 6. Start the full system
docker compose up -d

# 7. Check if everything is running
docker compose ps


# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start PostgreSQL and Ollama in Docker
docker compose up -d postgres ollama

# Update .env for localhost
echo 'DATABASE_URL=postgresql://agent_user:agent_password@localhost:5432/agent_memory' > .env
echo 'OLLAMA_URL=http://localhost:11434' >> .env
echo 'EMBEDDING_MODEL=nomic-embed-text' >> .env
echo 'LLM_MODEL=llama3.2:1b' >> .env

# Run the API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload


Project Structure

ai-agent-vector-system/
├── docker-compose.yml          # Service orchestration
├── Dockerfile                   # API container
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
│
├── src/                         # Application source code
│   ├── main.py                  # FastAPI entry point
│   ├── api/
│   │   └── routes.py            # API endpoints
│   ├── core/
│   │   ├── vector_store.py      # PostgreSQL + pgvector operations
│   │   └── embedder.py          # Embedding generation
│   ├── services/
│   │   ├── document_processor.py # Document ingestion
│   │   └── agent_service.py      # RAG and agent logic
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   └── utils/
│       └── logger.py             # Logging configuration
│
├── config/
│   ├── settings.py               # Configuration management
│   └── prometheus.yml            # Monitoring config
│
├── scripts/
│   ├── init_db.sql               # Database initialization
│   └── setup.sh                  # One-command setup
│
├── data/                        # Persistent data storage
│   ├── postgres/                 # PostgreSQL data
│   ├── ollama/                   # LLM models
│   ├── prometheus/               # Metrics data
│   └── grafana/                  # Dashboard data
│
└── tests/
    └── test_vector_store.py      # Unit tests


💡 Example Use Cases

1. Customer Support Agent

Upload support tickets and knowledge base articles. The agent can answer customer questions with context from previous tickets.

2. Code Documentation Assistant

Index your codebase documentation. Developers can ask questions about APIs, functions, and architecture.

3. Personal Knowledge Base

Store your notes, book highlights, and research papers. Query across your entire knowledge repository.

4. Internal Wiki Search

Ingest your company wiki. Employees can find relevant information instantly.

🙏 Acknowledgments

pgvector - Vector extension for PostgreSQL
Ollama - Local LLM runtime
FastAPI - Web framework
SQLAlchemy - ORM

Built with ❤️ by Herr Sah
Version: 1.0.0
Status: ✅ Production Ready


---

## 📝 How to Use

1. Copy the entire content above
2. Create a new file in your project root called `README.md`
3. Paste the content
4. Save the file
5. Optionally, update the GitHub repository URL in the clone commands

---