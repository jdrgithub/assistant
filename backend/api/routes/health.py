"""
Health check endpoints.
"""
from fastapi import APIRouter
from backend.services.qdrant_service import qdrant_service
from backend.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database and Qdrant status."""
    status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        status["services"]["database"] = "healthy"
    except Exception as e:
        status["services"]["database"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"
    
    # Check Qdrant
    try:
        await qdrant_service.ensure_collection()
        status["services"]["qdrant"] = "healthy"
    except Exception as e:
        status["services"]["qdrant"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"
    
    return status

