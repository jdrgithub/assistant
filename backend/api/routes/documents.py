"""
Document listing and retrieval endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.api.dependencies import get_current_user_dep, get_db_dep
from backend.models.database import User, Document
from backend.models.schemas import DocumentResponse
from typing import List, Optional

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """
    List documents in the knowledge base.
    """
    query = select(Document)
    
    if source:
        query = query.where(Document.source.ilike(f"%{source}%"))
    
    query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [
        DocumentResponse(
            id=doc.id,
            source=doc.source,
            content_preview=doc.content_preview or "",
            metadata=doc.metadata,
            tags=doc.tags,
            created_at=doc.created_at
        )
        for doc in documents
    ]


@router.get("/sources", response_model=List[str])
async def list_sources(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """
    List all unique document sources.
    """
    query = select(func.distinct(Document.source))
    result = await db.execute(query)
    sources = result.scalars().all()
    return list(sources)

