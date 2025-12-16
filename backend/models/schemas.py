"""
Pydantic schemas for request/response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Document Ingestion
class DocumentIngest(BaseModel):
    content: str
    source: str = Field(..., description="Source identifier (filename, URL, etc.)")
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None


class DocumentResponse(BaseModel):
    id: str
    source: str
    content_preview: str
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat
class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    role: Optional[str] = Field(None, description="Assistant role (e.g., 'coach', 'counselor')")
    use_rag: bool = True


class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    sources: Optional[List[DocumentResponse]] = None


# Search/RAG
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    filters: Optional[dict] = None


class SearchResult(BaseModel):
    document: DocumentResponse
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str

