from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://agent_user:agent_password@postgres:5432/agent_memory"

    # Embeddings (Jina AI cloud API)
    jina_api_key: str = ""
    embedding_model: str = "jina-embeddings-v3"
    embedding_dimensions: int = 768  # match existing vector(768) schema


    # Embeddings (local Ollama)
    ollama_url: str = "http://ollama:11434"
    embedding_model: str = "nomic-embed-text"

    # Chat LLM (Groq cloud API)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Application
    app_name: str = "EvoFarm Documentation Assistant"
    log_level: str = "INFO"
    max_document_size: int = 10 * 1024 * 1024

    # Vector Search
    default_top_k: int = 5
    similarity_threshold: float = 0.6
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Collections (namespacing for multiple document sets)
    default_collection: str = "evofarm-docs"

    # Auth (shared secret with EvoFarm Go API)
    jwt_secret: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()