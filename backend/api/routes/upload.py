"""
File upload endpoint for document ingestion.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
from backend.api.dependencies import get_current_user_dep, get_db_dep
from backend.models.database import User
from backend.models.schemas import DocumentIngest
from backend.services.embedding_service import embedding_service
from backend.config import settings
from pathlib import Path
import os

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    tags: str = None,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """
    Upload and ingest a file (Markdown, text, or PDF).
    """
    # Validate file type
    allowed_extensions = {'.md', '.txt', '.pdf', '.json'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    content = await file.read()
    
    # For text files, decode as UTF-8
    if file_ext in {'.md', '.txt', '.json'}:
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File encoding error. Please use UTF-8."
            )
    else:
        # For PDF, would need pypdf processing here
        # For now, raise error
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF processing not yet implemented"
        )
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(',')] if tags else []
    
    # Ingest document
    try:
        result = await embedding_service.ingest_document(
            content=text_content,
            source=file.filename,
            metadata={"uploaded_by": current_user.username},
            tags=tag_list
        )
        
        return {
            "message": "File uploaded and ingested successfully",
            "filename": file.filename,
            "point_ids": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

