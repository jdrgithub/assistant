"""
Initialize database: create tables if they don't exist.
Useful for development when Alembic isn't set up yet.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from backend.models.database import Base
from backend.config import settings


async def init_db():
    """Create all database tables."""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())

