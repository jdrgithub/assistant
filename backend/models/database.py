"""
SQLAlchemy models for PostgreSQL database.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    """Chat conversation model."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    role = Column(String, nullable=True, comment="Assistant role (coach, counselor, etc.)")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Individual chat message."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False, comment="user or assistant")
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True, comment="List of document IDs used in RAG")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    """Document metadata stored in PostgreSQL."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True, comment="Qdrant point ID")
    source = Column(String, nullable=False, index=True)
    content_preview = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_indexed = Column(Boolean, default=True)


class CategorySchema(Base):
    """Dynamic category schema for classification."""
    __tablename__ = "category_schemas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    fields = Column(JSON, nullable=False, comment="Schema fields definition")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CaptureItem(Base):
    """Captured raw input waiting for classification or review."""
    __tablename__ = "capture_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True, comment="CLI, chatbot, upload, etc.")
    status = Column(String, default="pending", comment="pending, needs_review, approved, rejected")
    suggested_category = Column(String, nullable=True)
    suggested_fields = Column(JSON, nullable=True, comment="Proposed structured data")
    confidence = Column(Integer, nullable=True, comment="0-100 confidence score")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")


class StructuredEntry(Base):
    """Structured, classified entry derived from captured content."""
    __tablename__ = "structured_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("category_schemas.id"), nullable=False)
    title = Column(String, nullable=True)
    data = Column(JSON, nullable=False, comment="Structured data per schema")
    source = Column(String, nullable=True)
    capture_id = Column(Integer, ForeignKey("capture_items.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    category = relationship("CategorySchema")


class IngestionLog(Base):
    """Audit trail for ingestion and classification actions."""
    __tablename__ = "ingestion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    capture_id = Column(Integer, ForeignKey("capture_items.id"), nullable=True)
    action = Column(String, nullable=False, comment="capture, classify, approve, reject")
    details = Column(JSON, nullable=True)
    model = Column(String, nullable=True)
    confidence = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

