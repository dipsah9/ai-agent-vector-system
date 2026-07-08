from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://agent_user:agent_password@postgres:5432/agent_memory"
    
    # LLM
    ollama_url: str = "http://ollama:11434"
    embedding_model: str = "nomic-embed-text"
    llm_model: str = "llama3.2:1b"
    
    # Application
    app_name: str = "AI Agent Vector System"
    log_level: str = "INFO"
    max_document_size: int = 10 * 1024 * 1024
    
    # Vector Search
    default_top_k: int = 5
    similarity_threshold: float = 0.6
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()