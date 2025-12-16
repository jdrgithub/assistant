"""
File utility functions for document processing.
"""
import os
from pathlib import Path
from typing import Optional
import aiofiles
from backend.config import settings


async def save_document(content: str, filename: str) -> str:
    """
    Save a document to the storage directory.
    
    Args:
        content: Document content
        filename: Filename to save as
        
    Returns:
        Full path to saved file
    """
    storage_path = Path(settings.document_storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    file_path = storage_path / filename
    
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(content)
    
    return str(file_path)


async def read_document(file_path: str) -> Optional[str]:
    """
    Read a document from the storage directory.
    
    Args:
        file_path: Path to the document
        
    Returns:
        Document content or None if file doesn't exist
    """
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    except FileNotFoundError:
        return None

