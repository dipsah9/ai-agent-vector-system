import logging
from typing import List, Dict, Any, Optional

from groq import Groq

from ..core.vector_store import VectorStore
from ..core.embedder import EmbeddingService
from ..models.schemas import AgentResponse, Source

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the EvoFarm documentation assistant.

EvoFarm is a distributed optimization platform with two solvers behind
one API:
- Evolution (genetic algorithm) for continuous, scoreable problems
- CP-SAT (Google OR-Tools) for discrete constraint problems

You answer questions about EvoFarm using ONLY the provided context from
EvoFarm's documentation (README, ARCHITECTURE.md, research notes).

Rules:
1. Answer using ONLY the provided context
2. If the context does not contain the answer, say:
   "I don't have enough information about that in the EvoFarm docs."
3. Cite sources as [Source 1], [Source 2], etc.
4. Be concise — 2-4 sentences unless a longer answer is clearly needed
5. If asked how to do something, be specific (file paths, commands)
"""


class AgentService:
    """RAG agent for EvoFarm documentation Q&A."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingService,
        groq_api_key: str,
        groq_model: str = "llama-3.3-70b-versatile",
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_model = groq_model

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks from the vector store."""
        query_embedding = self.embedder.embed_query(query)
        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
            similarity_threshold=0.5,
        )

    async def answer_question(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Answer a question using RAG."""

        # 1. Retrieve context
        search_results = await self.search(query, top_k, filter_metadata)

        # 2. Guard: no results, or all below threshold
        if not search_results:
            return AgentResponse(
                answer=(
                    "I don't have information about that in the EvoFarm docs. "
                    "Try asking about the architecture, the solvers, deployment, "
                    "or how to add a new problem."
                ),
                sources=[],
                confidence=0.0,
            )

        top_similarity = max(r["similarity"] for r in search_results)
        if top_similarity < 0.5:
            return AgentResponse(
                answer=(
                    "I couldn't find anything relevant in the EvoFarm docs. "
                    "Try rephrasing, or ask about a specific part of the system."
                ),
                sources=[],
                confidence=round(top_similarity, 3),
            )

        # 3. Build context
        context = "\n\n---\n\n".join(
            f"[Source {i+1}]: {r['text']}"
            for i, r in enumerate(search_results)
        )

        user_prompt = f"""CONTEXT FROM EVOFARM DOCS:

{context}

QUESTION: {query}

Answer using only the context above."""

        # 4. Call Groq
        try:
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            answer = response.choices[0].message.content

            confidence = sum(r["similarity"] for r in search_results) / len(
                search_results
            )

            return AgentResponse(
                answer=answer,
                sources=[
                    Source(
                        text=r["text"][:300] + ("..." if len(r["text"]) > 300 else ""),
                        similarity=r["similarity"],
                        metadata=r.get("metadata", {}),
                    )
                    for r in search_results[:3]
                ],
                confidence=round(confidence, 3),
            )

        except Exception as e:
            logger.error(f"Groq request failed: {e}")
            return AgentResponse(
                answer="I couldn't generate a response right now. Please try again.",
                sources=[],
                confidence=0.0,
            )

    async def get_system_stats(self) -> Dict[str, Any]:
        """Return vector store + Groq status."""
        stats = self.vector_store.get_statistics()
        stats["llm_provider"] = "groq"
        stats["llm_model"] = self.groq_model
        stats["embedding_model"] = self.embedder.model
        return stats