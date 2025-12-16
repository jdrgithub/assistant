"""
Service for orchestrating the embedding pipeline.
"""
from typing import List, Dict, Any, Optional
from backend.services.runpod_service import runpod_service
from backend.services.qdrant_service import qdrant_service
from backend.core.chunking import chunk_text
import uuid


class EmbeddingService:
    """Service for document embedding and storage."""
    
    async def ingest_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """
        Ingest a document: chunk, embed, and store in Qdrant.
        
        Args:
            content: Document content
            source: Source identifier
            metadata: Additional metadata
            tags: Document tags
            
        Returns:
            List of point IDs created
        """
        # Chunk the document
        chunks = chunk_text(content)
        
        if not chunks:
            return []
        
        # Generate embeddings via RunPod
        embeddings = await runpod_service.embed_texts(chunks)
        
        # Prepare payloads for Qdrant
        point_ids = []
        payloads = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)
            
            payload = {
                "source": source,
                "chunk_index": i,
                "content": chunk,
                "content_preview": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                "metadata": metadata or {},
                "tags": tags or []
            }
            payloads.append(payload)
        
        # Store in Qdrant
        await qdrant_service.upsert_points(
            vectors=embeddings,
            payloads=payloads,
            ids=point_ids
        )
        
        return point_ids


# Singleton instance
embedding_service = EmbeddingService()

