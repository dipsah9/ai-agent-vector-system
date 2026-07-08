from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from pydantic import BaseModel
import asyncio

router = APIRouter()

# These will be set by main.py
document_processor = None
agent_service = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filter_metadata: Optional[dict] = None

@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None)
):
    """Upload and index a document"""
    if document_processor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document information"""
    if document_processor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    stats = await document_processor.get_document_stats(document_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Document not found")
    return stats

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its embeddings"""
    if document_processor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    await document_processor.delete_document(document_id)
    return {"status": "success", "document_id": document_id}

@router.post("/search")
async def search(request: SearchRequest):
    """Search for relevant documents"""
    if agent_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    results = await agent_service.search(
        query=request.query,
        top_k=request.top_k,
        filter_metadata=request.filter_metadata
    )
    return {"results": results}

@router.post("/ask")
async def ask_question(request: SearchRequest):
    """Ask a question and get an answer with context"""
    if agent_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    response = await agent_service.answer_question(
        query=request.query,
        top_k=request.top_k,
        filter_metadata=request.filter_metadata
    )
    return response.dict()

@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    if agent_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    stats = await agent_service.get_system_stats()
    return stats