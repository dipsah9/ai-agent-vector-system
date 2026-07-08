import logging
import requests
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using Ollama"""
    
    def __init__(self, ollama_url: str, model: str = "nomic-embed-text"):
        self.ollama_url = ollama_url
        self.model = model
        self.dimension = 768
        self._check_model()
    
    def _check_model(self):
        try:
            response = requests.post(
                f"{self.ollama_url}/api/show",
                json={"name": self.model}
            )
            if response.status_code != 200:
                logger.warning(f"Model {self.model} not found, pulling...")
                self._pull_model()
        except Exception as e:
            logger.error(f"Failed to check model: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _pull_model(self):
        response = requests.post(
            f"{self.ollama_url}/api/pull",
            json={"name": self.model},
            stream=True
        )
        if response.status_code == 200:
            logger.info(f"Successfully pulled model {self.model}")
        else:
            logger.error(f"Failed to pull model: {response.text}")
            raise Exception(f"Model pull failed: {response.text}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def embed(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        
        for text in texts:
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get('embedding', [])
                    all_embeddings.append(embedding)
                else:
                    logger.error(f"Embedding API error: {response.text}")
                    all_embeddings.append([0.0] * self.dimension)
                    
            except Exception as e:
                logger.error(f"Error during embedding: {e}")
                all_embeddings.append([0.0] * self.dimension)
        
        all_embeddings = self._normalize_embeddings(all_embeddings)
        return all_embeddings
    
    def _normalize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        normalized = []
        for emb in embeddings:
            norm = np.linalg.norm(emb)
            if norm > 0:
                normalized.append((emb / norm).tolist())
            else:
                normalized.append(emb)
        return normalized
    
    def embed_single(self, text: str) -> List[float]:
        return self.embed([text])[0]