from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from contextlib import asynccontextmanager

from .api.routes import router
from .core.vector_store import VectorStore
from .core.embedder import EmbeddingService
from .services.document_processor import DocumentProcessor
from .services.agent_service import AgentService
from .utils.logger import setup_logging
from config.settings import settings

# Setup logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Global service instances
vector_store = None
embedder = None
document_processor = None
agent_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    global vector_store, embedder, document_processor, agent_service
    
    # Startup
    logger.info("Initializing AI Agent Vector System...")
    
    # Initialize core services
    vector_store = VectorStore(settings.database_url)
    embedder = EmbeddingService(settings.ollama_url, settings.embedding_model)
    
    # Initialize business services
    document_processor = DocumentProcessor(vector_store, embedder)
    agent_service = AgentService(
        vector_store=vector_store,
        embedder=embedder,
        llm_url=settings.ollama_url,
        llm_model=settings.llm_model
    )
    
    # Inject services into routes
    from .api.routes import document_processor as dp, agent_service as ag
    dp = document_processor
    ag = agent_service
    
    logger.info("All services initialized successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down AI Agent Vector System...")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)