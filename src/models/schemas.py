from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Source(BaseModel):
    text: str
    similarity: float
    metadata: Optional[Dict[str, Any]] = {}

class AgentResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float

class SearchResult(BaseModel):
    text: str
    similarity: float
    metadata: Optional[Dict[str, Any]] = {}

class DocumentMetadata(BaseModel):
    document_id: str
    filename: Optional[str] = None
    source: Optional[str] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    processed_at: Optional[str] = None