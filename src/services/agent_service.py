import logging
import requests
from typing import List, Dict, Any, Optional

from ..core.vector_store import VectorStore
from ..core.embedder import EmbeddingService
from ..models.schemas import AgentResponse, Source

logger = logging.getLogger(__name__)

class AgentService:
    """The main AI Agent service with reasoning capabilities"""
    
    def __init__(self, vector_store: VectorStore, embedder: EmbeddingService, 
                 llm_url: str, llm_model: str = "llama3.2:1b"):
        self.vector_store = vector_store
        self.embedder = embedder
        self.llm_url = llm_url
        self.llm_model = llm_model
        
    async def search(self, query: str, top_k: int = 5, 
                     filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search the vector database"""
        query_embedding = self.embedder.embed_single(query)
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
            similarity_threshold=0.6
        )
        return results
    
    async def answer_question(self, query: str, top_k: int = 5,
                              filter_metadata: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Answer a question using RAG with reasoning"""
        
        # Step 1: Retrieve relevant context
        search_results = await self.search(query, top_k, filter_metadata)
        
        if not search_results:
            return AgentResponse(
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
                confidence=0.0
            )
        
        # Step 2: Format context for the LLM
        context = "\n\n---\n\n".join([
            f"[Source {i+1}]: {r['text']}" 
            for i, r in enumerate(search_results)
        ])
        
        # Step 3: Construct the prompt
        prompt = f"""You are a knowledgeable AI assistant with access to a document database.
        
CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Answer the question using ONLY the provided context
2. If the context doesn't contain the answer, say "I don't have enough information"
3. Cite your sources by mentioning [Source X] in your answer
4. Be concise and specific

ANSWER:"""
        
        # Step 4: Get response from LLM
        try:
            response = requests.post(
                f"{self.llm_url}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', "Sorry, I couldn't generate a response.")
                
                # Calculate confidence based on similarity scores
                confidence = sum([r['similarity'] for r in search_results]) / len(search_results)
                
                return AgentResponse(
                    answer=answer,
                    sources=[
                        Source(
                            text=r['text'][:200] + "...",
                            similarity=r['similarity'],
                            metadata=r.get('metadata', {})
                        )
                        for r in search_results[:3]
                    ],
                    confidence=round(confidence, 3)
                )
            else:
                logger.error(f"LLM API error: {response.text}")
                return AgentResponse(
                    answer=f"Error generating response: {response.status_code}",
                    sources=[],
                    confidence=0.0
                )
                
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return AgentResponse(
                answer=f"Error: {str(e)}",
                sources=[],
                confidence=0.0
            )
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = self.vector_store.get_statistics()
        
        # Add LLM status
        try:
            response = requests.get(f"{self.llm_url}/api/tags", timeout=5)
            llm_status = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            llm_status = "unreachable"
        
        stats['llm_status'] = llm_status
        stats['embedding_model'] = self.embedder.model
        stats['llm_model'] = self.llm_model
        
        return stats