"""
Document ingestion endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.dependencies import get_current_user_dep, get_db_dep
from backend.models.database import User, Document
from backend.models.schemas import DocumentIngest, DocumentResponse
from backend.services.embedding_service import embedding_service
from backend.config import settings
import os
from datetime import datetime

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    document: DocumentIngest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """
    Ingest a document: chunk, embed, and store in Qdrant.
    """
    try:
        # Ingest document (chunk, embed, store in Qdrant)
        point_ids = await embedding_service.ingest_document(
            content=document.content,
            source=document.source,
            metadata=document.metadata,
            tags=document.tags
        )
        
        if not point_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process document"
            )
        
        # Store metadata in PostgreSQL
        for point_id in point_ids:
            doc = Document(
                id=point_id,
                source=document.source,
                content_preview=document.content[:200] + "..." if len(document.content) > 200 else document.content,
                metadata=document.metadata,
                tags=document.tags,
                is_indexed=True
            )
            db.add(doc)
        
        await db.commit()
        
        return {
            "message": "Document ingested successfully",
            "point_ids": point_ids,
            "source": document.source
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting document: {str(e)}"
        )

