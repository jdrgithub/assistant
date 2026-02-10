"""
Review and approval endpoints for captured items.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.dependencies import get_current_user_dep, get_db_dep
from backend.models.database import (
    User, CaptureItem, CategorySchema, StructuredEntry, IngestionLog, Document
)
from backend.models.schemas import ReviewApproveRequest, StructuredEntryResponse
from backend.services.embedding_service import embedding_service
from datetime import datetime

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/{capture_id}/approve", response_model=StructuredEntryResponse)
async def approve_capture(
    capture_id: int,
    approval: ReviewApproveRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """Approve a capture item and create a structured entry."""
    result = await db.execute(
        select(CaptureItem).where(
            CaptureItem.id == capture_id,
            CaptureItem.user_id == current_user.id
        )
    )
    capture = result.scalar_one_or_none()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture item not found")
    
    category_name = approval.category or capture.suggested_category
    if not category_name:
        raise HTTPException(status_code=400, detail="Category is required")
    
    schema_result = await db.execute(
        select(CategorySchema).where(CategorySchema.name == category_name)
    )
    schema = schema_result.scalar_one_or_none()
    if not schema:
        raise HTTPException(status_code=400, detail="Category schema not found")
    
    fields = approval.fields or capture.suggested_fields
    if not fields:
        raise HTTPException(status_code=400, detail="Structured fields are required")
    
    entry = StructuredEntry(
        user_id=current_user.id,
        category_id=schema.id,
        title=approval.title or None,
        data=fields,
        source=approval.source or capture.source,
        capture_id=capture.id
    )
    db.add(entry)
    await db.flush()
    
    capture.status = "approved"
    
    # Log approval
    db.add(IngestionLog(
        capture_id=capture.id,
        action="approve",
        details={"category": category_name, "entry_id": entry.id},
        model=None,
        confidence=capture.confidence
    ))
    
    # Store embeddings + metadata
    point_ids = await embedding_service.ingest_document(
        content=capture.content,
        source=category_name,
        metadata={
            "category": category_name,
            "entry_id": entry.id,
            "capture_id": capture.id,
            "fields": fields
        },
        tags=[category_name]
    )
    
    for point_id in point_ids:
        doc = Document(
            id=point_id,
            source=category_name,
            content_preview=capture.content[:200] + "..." if len(capture.content) > 200 else capture.content,
            metadata={
                "category": category_name,
                "entry_id": entry.id,
                "capture_id": capture.id
            },
            tags=[category_name],
            is_indexed=True
        )
        db.add(doc)
    
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/{capture_id}/reject")
async def reject_capture(
    capture_id: int,
    reason: str = "",
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """Reject a capture item."""
    result = await db.execute(
        select(CaptureItem).where(
            CaptureItem.id == capture_id,
            CaptureItem.user_id == current_user.id
        )
    )
    capture = result.scalar_one_or_none()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture item not found")
    
    capture.status = "rejected"
    
    db.add(IngestionLog(
        capture_id=capture.id,
        action="reject",
        details={"reason": reason},
        model=None,
        confidence=capture.confidence
    ))
    
    await db.commit()
    return {"message": "Capture rejected"}
