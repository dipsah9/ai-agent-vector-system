import logging
import requests
from typing import List, Dict, Any, Optional

from config.settings import settings

logger = logging.getLogger(__name__)

JINA_EMBEDDING_URL = "https://api.jina.ai/v1/embeddings"


class EmbeddingService:
    """Embedding service using Jina AI cloud API."""

    def __init__(self, api_key: str, model: str = "jina-embeddings-v3",
                 dimensions: int = 768):
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions

        if not api_key:
            logger.warning("JINA_API_KEY is not set — embeddings will fail")

    def embed_single(self, text: str) -> List[float]:
        """Embed a single text string."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts in one API call."""
        if not texts:
            return []

        if not self.api_key:
            raise ValueError("JINA_API_KEY is not set")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimensions,
            "task": "retrieval.passage",  # optimize for retrieval
        }

        try:
            response = requests.post(
                JINA_EMBEDDING_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Jina returns: {"data": [{"embedding": [...], "index": 0}, ...]}
            embeddings = [item["embedding"] for item in data["data"]]
            logger.info(f"Embedded {len(embeddings)} chunks via Jina")
            return embeddings

        except requests.exceptions.HTTPError as e:
            logger.error(f"Jina API error: {e} - {response.text}")
            raise
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """Embed a search query (uses query-specific task)."""
        if not self.api_key:
            raise ValueError("JINA_API_KEY is not set")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "input": [query],
            "dimensions": self.dimensions,
            "task": "retrieval.query",  # query-specific optimization
        }

        response = requests.post(
            JINA_EMBEDDING_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]


def get_embedder() -> EmbeddingService:
    """Return a configured EmbeddingService."""
    return EmbeddingService(
        api_key=settings.jina_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )