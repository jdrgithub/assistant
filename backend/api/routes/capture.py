"""
Capture endpoints for raw input.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.dependencies import get_current_user_dep, get_db_dep
from backend.models.database import User, CaptureItem, CategorySchema, IngestionLog
from backend.models.schemas import CaptureCreate, CaptureResponse
from backend.services.classification_service import classification_service
from backend.services.schema_service import ensure_default_schemas
from typing import List

router = APIRouter(prefix="/capture", tags=["capture"])

CONFIDENCE_THRESHOLD = 70


@router.post("/", response_model=CaptureResponse, status_code=status.HTTP_201_CREATED)
async def create_capture(
    capture: CaptureCreate,
    classify: bool = Query(True, description="Run classification immediately"),
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """Create a capture item, optionally classify it."""
    item = CaptureItem(
        user_id=current_user.id,
        content=capture.content,
        source=capture.source or "cli"
    )
    db.add(item)
    await db.flush()
    
    # Log capture
    db.add(IngestionLog(
        capture_id=item.id,
        action="capture",
        details={"source": item.source},
        model=None,
        confidence=None
    ))
    
    if classify:
        await ensure_default_schemas(db)
        schemas = await db.execute(select(CategorySchema).where(CategorySchema.is_active == True))
        schema_list = schemas.scalars().all()
        if not schema_list:
            # If no schemas, leave as pending
            item.status = "pending"
        else:
            classification = await classification_service.classify_text(
                text=capture.content,
                schemas=schema_list
            )
            item.suggested_category = classification.get("category")
            item.suggested_fields = classification.get("fields")
            item.confidence = classification.get("confidence")
            item.status = "needs_review" if (item.confidence or 0) < CONFIDENCE_THRESHOLD else "pending"
            
            db.add(IngestionLog(
                capture_id=item.id,
                action="classify",
                details=classification,
                model="runpod_llm",
                confidence=item.confidence
            ))
    
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/queue", response_model=List[CaptureResponse])
async def get_capture_queue(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """List capture items that need review."""
    result = await db.execute(
        select(CaptureItem).where(
            CaptureItem.user_id == current_user.id,
            CaptureItem.status.in_(["pending", "needs_review"])
        ).order_by(CaptureItem.created_at.desc())
    )
    return result.scalars().all()
