"""
Service for schema defaults and management helpers.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.database import CategorySchema


DEFAULT_SCHEMAS = [
    {
        "name": "people",
        "description": "People you interact with and relationship notes.",
        "fields": {
            "name": "string",
            "context": "string",
            "follow_up": "string",
            "last_contact": "string"
        }
    },
    {
        "name": "projects",
        "description": "Active or upcoming projects with next actions.",
        "fields": {
            "name": "string",
            "status": "string",
            "next_action": "string",
            "notes": "string"
        }
    },
    {
        "name": "ideas",
        "description": "Ideas, insights, and concepts worth revisiting.",
        "fields": {
            "title": "string",
            "summary": "string",
            "notes": "string"
        }
    },
    {
        "name": "admin",
        "description": "Administrative tasks, errands, and reminders.",
        "fields": {
            "task": "string",
            "due_date": "string",
            "status": "string",
            "notes": "string"
        }
    }
]


async def ensure_default_schemas(db: AsyncSession) -> None:
    result = await db.execute(select(CategorySchema))
    existing = result.scalars().all()
    if existing:
        return
    for schema in DEFAULT_SCHEMAS:
        db.add(CategorySchema(
            name=schema["name"],
            description=schema["description"],
            fields=schema["fields"],
            is_active=True
        ))
    await db.commit()
