from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from pydantic import BaseModel
from ..services.document_processor import DocumentProcessor
from ..services.agent_service import AgentService
from ..core.vector_store import VectorStore
from ..core.embedder import EmbeddingService
from ..utils.logger import get_logger
import asyncio

router = APIRouter()
logger = get_logger(__name__)

# Services (initialized in main.py)
document_processor: DocumentProcessor = None
agent_service: AgentService = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filter_metadata: Optional[dict] = None

class DocumentRequest(BaseModel):
    text: str
    document_id: str
    metadata: Optional[dict] = {}

@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None)
):
    """Upload and index a document"""
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        if not document_id:
            document_id = file.filename
        
        result = await document_processor.process_document(
            text=text,
            document_id=document_id,
            metadata={'filename': file.filename, 'source': 'upload'}
        )
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_processed": result['chunks_processed']
        }
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document information"""
    stats = await document_processor.get_document_stats(document_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Document not found")
    return stats

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its embeddings"""
    await document_processor.delete_document(document_id)
    return {"status": "success", "document_id": document_id}

@router.post("/search")
async def search(request: SearchRequest):
    """Search for relevant documents"""
    results = await agent_service.search(
        query=request.query,
        top_k=request.top_k,
        filter_metadata=request.filter_metadata
    )
    return {"results": results}

@router.post("/ask")
async def ask_question(request: SearchRequest):
    """Ask a question and get an answer with context"""
    response = await agent_service.answer_question(
        query=request.query,
        top_k=request.top_k,
        filter_metadata=request.filter_metadata
    )
    return response

@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    stats = await agent_service.get_system_stats()
    return stats

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-agent-vector-system"}