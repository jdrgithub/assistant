"""
Qdrant vector database client wrapper.
"""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional, Any
from backend.config import settings
import uuid


class QdrantService:
    """Service for interacting with Qdrant vector database."""
    
    def __init__(self):
        self.client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.collection_name = settings.qdrant_collection_name
    
    async def ensure_collection(self):
        """Ensure the collection exists with correct configuration."""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            # If Qdrant is not available, log but don't fail
            import logging
            logging.warning(f"Could not ensure Qdrant collection: {e}")
    
    async def upsert_points(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Insert or update points in Qdrant.
        
        Args:
            vectors: List of embedding vectors
            payloads: List of metadata payloads
            ids: Optional list of point IDs (generated if not provided)
        """
        await self.ensure_collection()
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in vectors]
        
        points = [
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            for point_id, vector, payload in zip(ids, vectors, payloads)
        ]
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of search results with score and payload
        """
        await self.ensure_collection()
        
        search_result = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=filter
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in search_result
        ]
    
    async def delete_points(self, point_ids: List[str]) -> None:
        """Delete points by IDs."""
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=point_ids
        )


# Singleton instance
qdrant_service = QdrantService()

