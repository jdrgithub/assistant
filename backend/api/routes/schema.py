"""
Schema management endpoints for dynamic categories.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.dependencies import get_current_user_dep, get_db_dep
from backend.models.database import CategorySchema, User
from backend.models.schemas import CategorySchemaCreate, CategorySchemaResponse
from typing import List
from backend.services.schema_service import ensure_default_schemas

router = APIRouter(prefix="/schema", tags=["schema"])


@router.get("/", response_model=List[CategorySchemaResponse])
async def list_schemas(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """List active category schemas."""
    await ensure_default_schemas(db)
    result = await db.execute(select(CategorySchema).where(CategorySchema.is_active == True))
    return result.scalars().all()


@router.post("/", response_model=CategorySchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_schema(
    schema: CategorySchemaCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """Create a new category schema."""
    existing = await db.execute(select(CategorySchema).where(CategorySchema.name == schema.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Schema name already exists")
    new_schema = CategorySchema(
        name=schema.name,
        description=schema.description,
        fields=schema.fields,
        is_active=True
    )
    db.add(new_schema)
    await db.commit()
    await db.refresh(new_schema)
    return new_schema


@router.put("/{schema_id}", response_model=CategorySchemaResponse)
async def update_schema(
    schema_id: int,
    schema: CategorySchemaCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """Update an existing schema definition."""
    result = await db.execute(select(CategorySchema).where(CategorySchema.id == schema_id))
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Schema not found")
    existing.name = schema.name
    existing.description = schema.description
    existing.fields = schema.fields
    await db.commit()
    await db.refresh(existing)
    return existing
