🚀 EvoFarm Documentation Assistant

A Retrieval-Augmented Generation (RAG) service that answers questions about EvoFarm’s documentation using local embeddings with Ollama and a fast cloud LLM with Groq.

⸻

📖 Overview

The EvoFarm Documentation Assistant is a RAG service built to answer natural-language questions about the EvoFarm distributed optimization platform.

Instead of asking a general-purpose LLM to answer questions from its own knowledge, the service first retrieves relevant information from indexed EvoFarm documentation and then provides that context to the LLM.

The workflow is:

1. Embed the user’s question using the local nomic-embed-text model through Ollama.
2. Search the indexed documentation using PostgreSQL + pgvector.
3. Retrieve the most relevant document chunks.
4. Generate an answer using a Groq-hosted LLM.
5. Return the answer together with source excerpts and a confidence value.

The assistant is explicitly instructed to answer only from the retrieved EvoFarm documentation. When relevant documentation cannot be found, it returns an “I don’t have information” response rather than inventing an answer.

Local vs. Cloud

The architecture intentionally separates embeddings from chat generation:

Component	Where it runs	Purpose
Embeddings	Local — Ollama	Converts documents and questions into vectors
Vector search	PostgreSQL + pgvector	Finds semantically relevant documentation
Chat generation	Cloud — Groq	Produces the final grounded answer

This keeps the embedding workload local while using Groq for fast LLM inference.

⸻

🏗️ Architecture

flowchart LR
    U[👤 User] --> API[FastAPI<br/>/api/v1/ask]
    API --> EMB[Ollama<br/>nomic-embed-text]
    EMB --> QV[Query Vector]
    QV --> DB[(PostgreSQL<br/>+ pgvector)]
    DB --> CTX[Top-k Relevant Chunks]
    CTX --> GROQ[Groq<br/>llama-3.3-70b-versatile]
    API --> GROQ
    GROQ --> ANS[Answer + Sources]
    ANS --> U

Core design principle

Retrieve first, generate second.

The LLM does not independently search the internet or rely on general knowledge for EvoFarm-specific questions. It receives the retrieved documentation as context and is instructed to answer from that context only.

⸻

⚙️ Technology Stack

Layer	Technology	Purpose
API	FastAPI	REST API and request handling
Server	Uvicorn	ASGI application server
Embeddings	Ollama + nomic-embed-text	Local semantic embeddings
Vector store	PostgreSQL + pgvector	Vector storage and similarity search
ORM	SQLAlchemy 2.x	Database access
Chat LLM	Groq	Cloud LLM inference
Chat model	llama-3.3-70b-versatile	Answer generation
Containers	Docker Compose	Local infrastructure
Monitoring	Prometheus	Metrics collection
Dashboard	Grafana	Metrics visualization

⸻

✨ Features

* 📄 Document ingestion through a REST API
* 🧠 Semantic document retrieval using pgvector
* 🔍 Configurable top-k vector search
* 🤖 Local embeddings with Ollama
* ⚡ Fast cloud inference through Groq
* 📚 Source attribution in generated answers
* 🛡️ Grounded-answer guardrails
* 📊 Confidence score based on retrieved similarities
* 🐳 Docker Compose infrastructure
* 📈 Prometheus metrics endpoint
* 📊 Grafana monitoring
* 🗂️ Document collections/namespacing
* 🔎 Optional metadata filtering
* 🧩 Designed specifically for EvoFarm documentation

⸻

📁 Project Structure

ai-agent-vector-system/
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.frontend
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── index.html
│
├── src/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── vector_store.py
│   │   └── embedder.py
│   ├── services/
│   │   ├── document_processor.py
│   │   └── agent_service.py
│   ├── models/
│   │   └── schemas.py
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

⸻

🚀 Quick Start

Prerequisites

* Docker
* Docker Compose
* Python 3.11+
* Git
* A Groq API key

Create a Groq API key from:

https://console.groq.com/keys

Depending on the local environment, allow sufficient memory for PostgreSQL and Ollama. The repository’s Docker configuration reserves memory for both services.

⸻

1. Clone the repository

git clone https://github.com/dipsah9/ai-agent-vector-system.git
cd ai-agent-vector-system

⸻

2. Start infrastructure

Start PostgreSQL and Ollama:

docker compose up -d postgres ollama

PostgreSQL is configured with pgvector and is exposed on port 5432.

Ollama is exposed on port 11434.

⸻

3. Pull the embedding model

The service uses nomic-embed-text for local embeddings.

docker exec ollama_server ollama pull nomic-embed-text

The chat model is hosted by Groq, so a local chat model is not required for the current EvoFarm assistant configuration.

⸻

4. Configure environment variables

Copy the example environment file:

cp .env.example .env

Configure the values required by the application:

DATABASE_URL=postgresql://agent_user:agent_password@localhost:5432/agent_memory
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
SIMILARITY_THRESHOLD=0.6
CHUNK_SIZE=500
CHUNK_OVERLAP=50
DEFAULT_COLLECTION=evofarm-docs

Optional authentication configuration

The application configuration also supports a shared JWT secret for integration with the EvoFarm API:

JWT_SECRET=your-shared-secret

Do not commit real API keys or secrets to Git.

⸻

5. Install Python dependencies

Create a virtual environment:

python3.11 -m venv .venv

Activate it:

macOS / Linux

source .venv/bin/activate

Windows

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

⸻

6. Initialize the database

The Docker Compose PostgreSQL service mounts scripts/init_db.sql into PostgreSQL’s initialization directory.

For an already-existing database, initialize the schema manually if necessary:

docker exec -i vector_db psql \
  -U agent_user \
  -d agent_memory \
  < scripts/init_db.sql

If the PostgreSQL volume already contains an initialized database, Docker will not automatically re-run initialization scripts. In that case, use the project’s database initialization/migration procedure rather than assuming the script will execute again.

⸻

7. Run the FastAPI service

Run the API from the repository root:

uvicorn src.main:app --reload

The API will be available at:

http://localhost:8000

Interactive Swagger documentation:

http://localhost:8000/docs

OpenAPI JSON:

http://localhost:8000/openapi.json

⸻

🔄 RAG Workflow

The assistant follows a simple retrieval-augmented generation pipeline.

sequenceDiagram
    participant User
    participant API as FastAPI
    participant Ollama
    participant DB as PostgreSQL + pgvector
    participant Groq
    User->>API: Upload document
    API->>Ollama: Generate embeddings
    Ollama-->>API: Document vectors
    API->>DB: Store chunks + vectors
    User->>API: Ask question
    API->>Ollama: Embed question
    Ollama-->>API: Query vector
    API->>DB: Similarity search
    DB-->>API: Top-k relevant chunks
    API->>Groq: Context + question
    Groq-->>API: Grounded answer
    API-->>User: Answer + sources + confidence

Step-by-step

1. Document ingestion

A document is uploaded through the /api/v1/documents endpoint.

The service:

* reads the document
* splits it into chunks
* generates embeddings locally using Ollama
* stores the chunks and vectors in PostgreSQL

2. Question embedding

When a user asks a question, the same embedding model converts the question into a vector.

3. Similarity search

pgvector compares the question vector with stored document vectors and returns the most relevant chunks.

The default retrieval configuration is:

top_k = 5
similarity_threshold = 0.6

4. Context construction

The retrieved chunks are converted into a context block and labelled:

[Source 1]
[Source 2]
[Source 3]
...

5. Answer generation

The context and question are sent to the Groq LLM.

The system prompt instructs the model to:

* use only the supplied EvoFarm documentation
* avoid inventing information
* cite relevant sources
* keep answers concise
* provide specific file paths or commands when documentation supports them

6. Response

The API returns:

* generated answer
* source excerpts
* similarity values
* metadata
* confidence score

⸻

📡 API Reference

The API routes are exposed under the /api/v1 prefix.

Method	Endpoint	Description
POST	/api/v1/documents	Upload and index a document
GET	/api/v1/documents/{document_id}	Get document information
DELETE	/api/v1/documents/{document_id}	Delete a document and its embeddings
POST	/api/v1/search	Perform raw vector search
POST	/api/v1/ask	Run the complete RAG pipeline
GET	/api/v1/stats	Get system statistics
GET	/health	Health check
GET	/metrics	Prometheus metrics

⸻

📄 Upload a document

curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@README.md"

Example response:

{
  "status": "success",
  "document_id": "README.md",
  "chunks_processed": 5
}

You can optionally provide a document ID:

curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@README.md" \
  -F "document_id=evofarm-readme"

⸻

🔍 Search documentation

The raw search endpoint is useful for inspecting retrieval independently from LLM generation.

curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What solvers does EvoFarm support?",
    "top_k": 5
  }'

The request can also include metadata filters:

{
  "query": "How does the CP-SAT solver work?",
  "top_k": 5,
  "filter_metadata": {
    "filename": "README.md"
  }
}

⸻

🤖 Ask a question

curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What solvers does EvoFarm support?"
  }'

Example response:

{
  "answer": "EvoFarm provides two solvers: an Evolution solver for continuous, scoreable problems and a CP-SAT solver for discrete constraint problems [Source 1].",
  "sources": [
    {
      "text": "...",
      "similarity": 0.72,
      "metadata": {
        "filename": "README.md"
      }
    }
  ],
  "confidence": 0.68
}

The exact answer, similarity values, and source contents depend on the documents currently indexed.

⸻

📊 Get system statistics

curl http://localhost:8000/api/v1/stats

The statistics endpoint exposes information about the vector store and the configured LLM and embedding models.

⸻

❤️ Health check

curl http://localhost:8000/health

⸻

📈 Metrics

curl http://localhost:8000/metrics

The metrics endpoint is designed for Prometheus scraping.

⸻

🎯 Grounded Answers

A central design goal of the service is to avoid unsupported answers.

The system prompt explicitly tells the LLM to use only the retrieved EvoFarm documentation.

When retrieval produces no relevant results, the service returns:

“I don’t have information about that in the EvoFarm docs. Try asking about the architecture, the solvers, deployment, or how to add a new problem.”

When the retrieved content is not sufficiently relevant, it instead asks the user to rephrase or ask about a more specific part of the system.

This behavior is intentional.

A documentation assistant should prefer:

"I don't have information about that in the EvoFarm docs."

over an unsupported or fabricated answer.

⸻

📚 Documentation Coverage

The RAG system only knows about documentation that has been indexed.

This means that improving the assistant’s coverage is primarily a documentation-ingestion task.

Recommended EvoFarm sources

Topic	Suggested source
EvoFarm overview	README.md
System architecture	ARCHITECTURE.md
Scheduling and scalability	scheduling-scalability.md
Nurse rostering	worker/problems/nurse_rostering.py
Authentication	api/auth.go
Deployment	docker-compose.yml, fly.toml
CP-SAT benchmarks	docs/benchmarks/cpsat-baseline.md
Adding a problem	worker/routing.py

The table above describes recommended sources to index. It should not be interpreted as a guarantee that every file currently exists or is currently indexed.

⸻

Add more documentation

For a text-based source:

curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@path/to/document.md"

For example:

curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@ARCHITECTURE.md"

After indexing, questions about the new content can be answered through /api/v1/ask.

⸻

⚙️ Configuration

The main application configuration is defined in config/settings.py.

Variable	Default	Purpose
DATABASE_URL	PostgreSQL connection string	PostgreSQL connection
OLLAMA_URL	http://ollama:11434	Ollama endpoint
EMBEDDING_MODEL	nomic-embed-text	Embedding model
GROQ_API_KEY	Required	Groq authentication
GROQ_MODEL	llama-3.3-70b-versatile	Chat model
DEFAULT_TOP_K	5	Number of chunks retrieved
SIMILARITY_THRESHOLD	0.6	Minimum retrieval similarity
CHUNK_SIZE	500	Chunk size
CHUNK_OVERLAP	50	Chunk overlap
DEFAULT_COLLECTION	evofarm-docs	Default document collection
JWT_SECRET	Empty	Optional shared authentication secret
LOG_LEVEL	INFO	Application logging level

Similarity threshold

The default threshold is:

0.6

Lowering it may retrieve more potentially relevant documents but can also introduce more noise.

Increasing it makes retrieval stricter and can cause the assistant to return “not found” responses more frequently.

⸻

🗄️ Why PostgreSQL + pgvector?

PostgreSQL is used as the vector store instead of introducing a separate vector database.

Advantages include:

* PostgreSQL is already a mature production database
* pgvector adds vector similarity search directly to PostgreSQL
* document metadata and vectors can live together
* fewer infrastructure components are required
* SQLAlchemy can be used for normal database access
* PostgreSQL backups and operational tooling can be reused

This keeps the architecture relatively simple:

FastAPI
   │
   ├── Ollama
   │    └── Embeddings
   │
   └── PostgreSQL
        └── pgvector

⸻

🐳 Docker Services

The repository’s Docker Compose configuration provides infrastructure services including:

Service	Port	Purpose
PostgreSQL	5432	Vector database
Ollama	11434	Local embedding inference
Frontend	8080	Static frontend
Prometheus	9090	Metrics
Grafana	3000	Monitoring dashboard

The FastAPI application can be run separately with:

uvicorn src.main:app --reload

The FastAPI agent_api service definition in the current docker-compose.yml is commented out. If you later enable it, make sure its environment variables and service dependencies match the current Groq-based configuration.

⸻

📊 Monitoring

The project includes Prometheus and Grafana infrastructure.

Service	URL
FastAPI Swagger	http://localhost:8000/docs
FastAPI OpenAPI	http://localhost:8000/openapi.json
Prometheus	http://localhost:9090
Grafana	http://localhost:3000
Frontend	http://localhost:8080

The application exposes Prometheus-compatible metrics at:

GET /metrics

⸻

🛡️ Error Handling and Fallbacks

The RAG service has several fallback paths.

No retrieved documents

The service returns a grounded “not found” response instead of calling the LLM.

Low relevance

If retrieved content does not meet the configured relevance requirements, the service asks the user to rephrase the question.

Groq failure

If the Groq request fails, the API returns:

I couldn't generate a response right now. Please try again.

This prevents infrastructure failures from being presented as generated answers.

⸻

🔐 Security Notes

The service uses a Groq API key for cloud LLM inference.

Never commit:

GROQ_API_KEY
JWT_SECRET

or other credentials to Git.

Use .env for local secrets and keep .env excluded from version control.

For production deployment, consider adding:

* JWT verification
* request authentication
* per-user rate limiting
* request size limits
* CORS restrictions
* secret management through the deployment platform
* audit logging
* HTTPS/TLS

⸻

🧪 Testing

The repository contains tests under:

tests/

Run the test suite with:

pytest

If the project environment does not yet include pytest, install it separately:

pip install pytest

⸻

🎨 Why This Design?

Grounded answers

The assistant is designed around the principle that documentation questions should be answered from documentation.

The LLM is not treated as the source of truth.

Instead:

Documentation
      ↓
  Embeddings
      ↓
Vector Search
      ↓
Relevant Context
      ↓
    Groq LLM
      ↓
Grounded Answer

⸻

Local embeddings

Embedding documents locally through Ollama means the embedding pipeline does not require an external embedding API.

The same embedding model is used for:

* document embeddings
* question embeddings

This makes vector similarity meaningful and keeps the embedding layer self-hosted.

⸻

Fast cloud generation

The final response is generated through Groq.

This provides a separation of responsibilities:

Local:
  document embedding
  query embedding
  vector retrieval
Cloud:
  natural-language answer generation

⸻

Source attribution

Answers contain source references such as:

[Source 1]
[Source 2]

The API also returns the underlying source excerpts and similarity information so the frontend can display supporting context.

⸻

🔮 Future Improvements

Potential next steps for the EvoFarm documentation assistant include:

* JWT verification using the shared EvoFarm API secret
* Per-user rate limiting
* Chat widget embedded in the EvoFarm dashboard
* Streaming LLM responses
* Multi-collection support
* Hybrid BM25 + vector search
* User feedback loop (thumbs up / thumbs down)
* Better document-type handling
* Automated documentation synchronization
* Retrieval evaluation and benchmark suite
* Improved citation rendering
* Production Kubernetes deployment
* Caching for repeated questions
* Automated re-indexing when EvoFarm documentation changes

⸻

🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

git checkout -b feature/my-change

3. Make your changes.
4. Run the tests.

pytest

5. Commit your changes.

git add .
git commit -m "feat: describe my change"

6. Push the branch.
7. Open a Pull Request.

⸻

📄 License

This project is licensed under the MIT License.

See LICENSE for details.

⸻

🙏 Acknowledgements

This project builds on several open-source technologies:

* PostgreSQL
* pgvector
* Ollama
* FastAPI
* SQLAlchemy
* Prometheus
* Grafana
* Groq

The assistant is built specifically to support documentation for EvoFarm.

⸻

⭐ EvoFarm Documentation Assistant

The goal of this service is simple:

Ask a question about EvoFarm, retrieve the relevant documentation, and receive a concise answer grounded in the actual source material.

Repository:

https://github.com/dipsah9/ai-agent-vector-system

EvoFarm:

https://evofarm.vercel.app