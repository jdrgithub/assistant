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
    mode: Optional[str] = Field(None, description="chat or capture")


class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    sources: Optional[List[DocumentResponse]] = None
    capture_id: Optional[int] = None
    classification: Optional[dict] = None
    follow_up_questions: Optional[List[str]] = None
    confidence: Optional[int] = None


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


# Dynamic schemas and capture
class CategorySchemaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    fields: dict


class CategorySchemaResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    fields: dict
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CaptureCreate(BaseModel):
    content: str
    source: Optional[str] = None


class CaptureResponse(BaseModel):
    id: int
    content: str
    source: Optional[str] = None
    status: str
    suggested_category: Optional[str] = None
    suggested_fields: Optional[dict] = None
    confidence: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClassificationResponse(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    fields: Optional[dict] = None
    confidence: Optional[int] = None
    follow_up_questions: Optional[List[str]] = None


class ReviewApproveRequest(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    fields: Optional[dict] = None
    source: Optional[str] = None


class StructuredEntryResponse(BaseModel):
    id: int
    category_id: int
    title: Optional[str] = None
    data: dict
    source: Optional[str] = None
    capture_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

