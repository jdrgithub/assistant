"""
Search and RAG query endpoints.
"""
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_current_user_dep
from backend.models.schemas import SearchRequest, SearchResponse, SearchResult, DocumentResponse
from backend.services.runpod_service import runpod_service
from backend.services.qdrant_service import qdrant_service
from backend.config import settings
from datetime import datetime
from typing import List

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
async def search_documents(
    search_request: SearchRequest,
    current_user = Depends(get_current_user_dep)
):
    """
    Search documents using RAG: embed query and retrieve similar documents.
    """
    # Embed query
    query_embeddings = await runpod_service.embed_texts([search_request.query])
    if not query_embeddings:
        return SearchResponse(results=[], query=search_request.query)
    
    query_vector = query_embeddings[0]
    
    # Search Qdrant
    top_k = search_request.top_k or settings.rag_top_k
    results = await qdrant_service.search(
        query_vector=query_vector,
        top_k=top_k,
        filter=search_request.filters
    )
    
    # Format results
    search_results = [
        SearchResult(
            document=DocumentResponse(
                id=result["id"],
                source=result["payload"].get("source", "unknown"),
                content_preview=result["payload"].get("content_preview", ""),
                metadata=result["payload"].get("metadata"),
                tags=result["payload"].get("tags"),
                created_at=datetime.now()  # TODO: get from payload if stored
            ),
            score=result["score"]
        )
        for result in results
    ]
    
    return SearchResponse(results=search_results, query=search_request.query)

