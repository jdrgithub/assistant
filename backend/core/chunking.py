"""
Text chunking utilities using LangChain.
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import settings
from typing import List


def create_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create a text splitter with configured chunk size and overlap."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        length_function=len,
    )


def chunk_text(text: str) -> List[str]:
    """
    Split text into chunks for embedding.
    
    Args:
        text: Input text to chunk
        
    Returns:
        List of text chunks
    """
    splitter = create_text_splitter()
    return splitter.split_text(text)

