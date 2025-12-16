"""
Configuration management using Pydantic Settings.
Loads from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # API Configuration
    api_title: str = "Personal AI Assistant API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/assistant_db"
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "documents"
    
    # RunPod
    runpod_api_key: Optional[str] = None
    runpod_endpoint_id: Optional[str] = None
    runpod_embedding_pod_id: Optional[str] = None
    runpod_llm_pod_id: Optional[str] = None
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # LLM Configuration
    llm_model: str = "mistral"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    # RAG Configuration
    rag_top_k: int = 5
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 200
    
    # Document Storage
    document_storage_path: str = "./storage/documents"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

