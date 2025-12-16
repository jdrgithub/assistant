"""
FastAPI dependencies for authentication and database.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db
from backend.core.security import get_current_user
from backend.models.database import User


async def get_current_user_dep(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency for getting current authenticated user."""
    return current_user


async def get_db_dep(
    db: AsyncSession = Depends(get_db)
) -> AsyncSession:
    """Dependency for getting database session."""
    return db

