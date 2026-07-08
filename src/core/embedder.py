import logging
import requests
import time
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using Ollama"""
    
    def __init__(self, ollama_url: str, model: str = "nomic-embed-text"):
        self.ollama_url = ollama_url
        self.model = model
        self.dimension = 768  # nomic-embed-text dimension
        self._check_model()
    
    def _check_model(self):
        """Ensure the embedding model is available"""
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
        """Pull the embedding model"""
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
    def embed(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        
        all_embeddings = []
        total_texts = len(texts)
        
        for i in range(0, total_texts, batch_size):
            batch = texts[i:i+batch_size]
            
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": batch  # Ollama supports batch embedding
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Ollama returns embeddings as a list
                    embeddings = data.get('embeddings', [])
                    all_embeddings.extend(embeddings)
                    logger.debug(f"Embedded batch {i//batch_size + 1}/{(total_texts-1)//batch_size + 1}")
                else:
                    logger.error(f"Embedding API error: {response.text}")
                    # Fallback: use a zero vector if API fails
                    zero_vector = [0.0] * self.dimension
                    all_embeddings.extend([zero_vector] * len(batch))
                    
            except Exception as e:
                logger.error(f"Error during embedding: {e}")
                # Return a zero vector as fallback
                zero_vector = [0.0] * self.dimension
                all_embeddings.extend([zero_vector] * len(batch))
        
        # Normalize the vectors (important for cosine similarity)
        all_embeddings = self._normalize_embeddings(all_embeddings)
        return all_embeddings
    
    def _normalize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """L2 normalize embeddings for better similarity search"""
        normalized = []
        for emb in embeddings:
            norm = np.linalg.norm(emb)
            if norm > 0:
                normalized.append((emb / norm).tolist())
            else:
                normalized.append(emb)
        return normalized
    
    def embed_single(self, text: str) -> List[float]:
        """Embed a single text"""
        return self.embed([text])[0]