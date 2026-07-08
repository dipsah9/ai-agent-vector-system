import logging
from typing import List, Dict, Any, Optional
import re
from datetime import datetime

from ..core.vector_store import VectorStore
from ..core.embedder import EmbeddingService

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process and index documents for the AI agent"""
    
    def __init__(self, vector_store: VectorStore, embedder: EmbeddingService):
        self.vector_store = vector_store
        self.embedder = embedder
        self.chunk_size = 500
        self.chunk_overlap = 50
    
    async def process_document(self, text: str, document_id: str, 
                               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a document and store it in the vector database"""
        
        logger.info(f"Processing document: {document_id}")
        
        # Clean the text
        text = self._clean_text(text)
        
        # Split into chunks
        chunks = self._chunk_text(text)
        
        # Generate embeddings
        embeddings = self.embedder.embed(chunks)
        
        # Prepare metadata for each chunk
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            meta = metadata.copy() if metadata else {}
            meta['chunk_index'] = i
            meta['total_chunks'] = len(chunks)
            meta['processed_at'] = datetime.utcnow().isoformat()
            chunk_metadata.append(meta)
        
        # Store in vector database
        self.vector_store.insert(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=chunk_metadata
        )
        
        logger.info(f"Document processed: {document_id} with {len(chunks)} chunks")
        
        return {
            'document_id': document_id,
            'chunks_processed': len(chunks),
            'total_characters': len(text)
        }
    
    async def get_document_stats(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific document"""
        stats = self.vector_store.get_statistics()
        return {
            'document_id': document_id,
            'status': 'indexed',
            'stats': stats
        }
    
    async def delete_document(self, document_id: str):
        """Delete a document from the vector database"""
        self.vector_store.delete_document(document_id)
        logger.info(f"Document deleted: {document_id}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s.,!?;:]', '', text)
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        if len(words) <= self.chunk_size:
            return [text]
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            chunks.append(chunk)
            
            if i + self.chunk_size >= len(words):
                break
        
        return chunks