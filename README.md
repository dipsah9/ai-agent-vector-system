# 🚀 AI Agent Vector System

> A production-ready Retrieval-Augmented Generation (RAG) framework that gives AI agents long-term memory using **PostgreSQL + pgvector**, **Ollama**, and **FastAPI**.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# 📖 Overview

AI Agent Vector System is a complete **Retrieval-Augmented Generation (RAG)** backend that enables AI assistants to remember information, retrieve relevant context, and answer questions using local Large Language Models.

Instead of sending data to cloud APIs, the entire pipeline runs locally using **Ollama**, making it fast, private, and cost-effective.

The project is designed for both rapid prototyping and production deployments.

---

# ✨ Features

- 📄 Document Ingestion (TXT, PDF, Web Pages)
- 🧠 Long-Term Memory using pgvector
- 🔍 Semantic Search
- 🤖 Local LLMs with Ollama
- ⚡ FastAPI REST API
- 🐳 Docker Compose Deployment
- 📈 Prometheus Metrics
- 📊 Grafana Dashboards
- 🔒 Fully Offline (No API Costs)
- 🚀 Production Ready Architecture

---

# 🏗️ System Architecture

```mermaid
flowchart LR

    U[👤 User]

    API[FastAPI API]

    AGENT[AI Agent]

    DB[(PostgreSQL<br/>pgvector)]

    OLLAMA[Ollama]

    EMBED[nomic-embed-text]

    CHAT[llama3.2:1b]

    PROM[Prometheus]

    GRAF[Grafana]

    U --> API

    API --> AGENT

    AGENT --> DB

    AGENT --> OLLAMA

    OLLAMA --> EMBED

    OLLAMA --> CHAT

    API --> PROM
    AGENT --> PROM
    DB --> PROM
    OLLAMA --> PROM

    PROM --> GRAF
```

---

# ⚙️ Technology Stack

| Layer | Technology |
|--------|------------|
| API | FastAPI |
| Server | Uvicorn |
| Database | PostgreSQL 16 |
| Vector Database | pgvector |
| ORM | SQLAlchemy 2.x |
| LLM Runtime | Ollama |
| Embedding Model | nomic-embed-text |
| Chat Model | llama3.2:1b |
| Monitoring | Prometheus |
| Dashboard | Grafana |
| Containers | Docker Compose |

---

# 📁 Project Structure

```text
ai-agent-vector-system/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── .env.example
│
├── src/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── vector_store.py
│   │   └── embedder.py
│   │
│   ├── services/
│   │   ├── document_processor.py
│   │   └── agent_service.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── utils/
│       └── logger.py
│
├── config/
│   ├── settings.py
│   └── prometheus.yml
│
├── scripts/
│   ├── setup.sh
│   └── init_db.sql
│
├── data/
│   ├── postgres/
│   ├── ollama/
│   ├── prometheus/
│   └── grafana/
│
└── tests/
    └── test_vector_store.py
```

---

# 🚀 Quick Start

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+
- Git
- 8 GB RAM minimum
- 10 GB free storage

---

## Clone Repository

```bash
git clone https://github.com/dipsah9/ai-agent-vector-system.git

cd ai-agent-vector-system
```

---

## Start Infrastructure

```bash
docker compose up -d postgres ollama
```

---

## Download Models

```bash
docker exec ollama_server ollama pull nomic-embed-text

docker exec ollama_server ollama pull llama3.2:1b
```

---

## Configure Environment

```bash
cp .env.example .env
```

Example:

```env
DATABASE_URL=postgresql://agent_user:agent_password@localhost:5432/agent_memory

OLLAMA_URL=http://localhost:11434

EMBEDDING_MODEL=nomic-embed-text

LLM_MODEL=llama3.2:1b
```

---

## Install Python Dependencies

```bash
python3.11 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

## Run API

```bash
uvicorn src.main:app --reload
```

Open

```
http://localhost:8000/docs
```

---

# 🔄 RAG Workflow

```mermaid
sequenceDiagram

participant User

participant API

participant Agent

participant Embedder

participant VectorDB

participant LLM

User->>API: Upload Document

API->>Embedder: Generate Embeddings

Embedder->>VectorDB: Store Vectors

User->>API: Ask Question

API->>Embedder: Embed Query

Embedder->>VectorDB: Similarity Search

VectorDB-->>Agent: Relevant Context

Agent->>LLM: Context + Prompt

LLM-->>Agent: Response

Agent-->>User: Final Answer
```

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /upload | Upload documents |
| POST | /query | Ask questions |
| GET | /documents | List indexed documents |
| DELETE | /documents/{id} | Delete document |
| GET | /health | Health check |
| GET | /metrics | Prometheus metrics |

---

# 📊 Monitoring

The project includes built-in observability.

| Service | URL |
|----------|-----|
| FastAPI Docs | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

---

# 💡 Example Use Cases

### Customer Support Assistant

Answer customer questions using previous tickets and documentation.

---

### Code Documentation Assistant

Search APIs, functions, architecture, and developer documentation.

---

### Personal Knowledge Base

Store notes, books, PDFs, and research for semantic search.

---

### Enterprise Wiki Search

Search internal documentation instantly using natural language.

---

# 🔮 Future Improvements

- Multi-user authentication
- Streaming responses
- Hybrid Search (BM25 + Vector)
- LangGraph Agents
- Multi-modal document support
- Redis Cache
- Kubernetes Deployment
- GPU Inference Support

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

- PostgreSQL
- pgvector
- Ollama
- FastAPI
- SQLAlchemy
- Prometheus
- Grafana

---

## ⭐ If you found this project useful, consider giving it a star!
