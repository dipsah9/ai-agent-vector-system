from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

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

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

# ✅ Configure CORS properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",      # Frontend served locally
        "http://127.0.0.1:8080",
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",      # Alternative
        "*"                           # Allow all during development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store, embedder, document_processor, agent_service
    
    logger.info("Initializing AI Agent Vector System...")
    
    try:
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
        from .api import routes
        routes.document_processor = document_processor
        routes.agent_service = agent_service
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Agent Vector System...")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.app_name}

# Include routes
app.include_router(router, prefix="/api/v1")