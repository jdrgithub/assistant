"""
Chat endpoints with RAG integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.api.dependencies import get_current_user_dep, get_db_dep
from backend.models.database import (
    User, Conversation, Message, CaptureItem, CategorySchema, IngestionLog
)
from backend.models.schemas import ChatRequest, ChatResponse, DocumentResponse
from backend.services.runpod_service import runpod_service
from backend.services.qdrant_service import qdrant_service
from backend.services.llm_service import llm_service
from backend.services.classification_service import classification_service
from backend.services.schema_service import ensure_default_schemas
from backend.config import settings
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db_dep)
):
    """
    Chat endpoint with optional RAG: retrieve context, generate response.
    """
    try:
        # Capture-only mode for direct ingestion
        if chat_request.mode == "capture":
            capture_item = CaptureItem(
                user_id=current_user.id,
                content=chat_request.message,
                source="chatbot"
            )
            db.add(capture_item)
            await db.flush()
            
            db.add(IngestionLog(
                capture_id=capture_item.id,
                action="capture",
                details={"source": "chatbot"},
                model=None,
                confidence=None
            ))
            
            await ensure_default_schemas(db)
            schemas = await db.execute(
                select(CategorySchema).where(CategorySchema.is_active == True)
            )
            schema_list = schemas.scalars().all()
            
            classification = None
            if schema_list:
                classification = await classification_service.classify_text(
                    text=chat_request.message,
                    schemas=schema_list
                )
                capture_item.suggested_category = classification.get("category")
                capture_item.suggested_fields = classification.get("fields")
                capture_item.confidence = classification.get("confidence")
                capture_item.status = "needs_review" if (capture_item.confidence or 0) < 70 else "pending"
                
                db.add(IngestionLog(
                    capture_id=capture_item.id,
                    action="classify",
                    details=classification,
                    model="runpod_llm",
                    confidence=capture_item.confidence
                ))
            
            await db.commit()
            await db.refresh(capture_item)
            
            response_text = "Captured for review."
            if classification and classification.get("category"):
                response_text = (
                    f"Captured. Suggested category: {classification.get('category')} "
                    f"(confidence {classification.get('confidence')}%)."
                )
            
            return ChatResponse(
                message=response_text,
                conversation_id=chat_request.conversation_id or 0,
                capture_id=capture_item.id,
                classification=classification,
                follow_up_questions=classification.get("follow_up_questions") if classification else None,
                confidence=classification.get("confidence") if classification else None
            )
        
        # Get or create conversation
        conversation = None
        if chat_request.conversation_id:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == chat_request.conversation_id,
                    Conversation.user_id == current_user.id
                )
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            conversation = Conversation(
                user_id=current_user.id,
                role=chat_request.role
            )
            db.add(conversation)
            await db.flush()
        
        # Store user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=chat_request.message
        )
        db.add(user_message)
        
        # RAG retrieval if enabled
        context_docs = None
        source_documents = []
        if chat_request.use_rag:
            # Embed query
            query_embeddings = await runpod_service.embed_texts([chat_request.message])
            if query_embeddings:
                query_vector = query_embeddings[0]
                # Retrieve context
                results = await qdrant_service.search(
                    query_vector=query_vector,
                    top_k=settings.rag_top_k
                )
                context_docs = results
                # Format source documents for response
                source_documents = [
                    DocumentResponse(
                        id=result["id"],
                        source=result["payload"].get("source", "unknown"),
                        content_preview=result["payload"].get("content_preview", ""),
                        metadata=result["payload"].get("metadata"),
                        tags=result["payload"].get("tags"),
                        created_at=datetime.now()
                    )
                    for result in results
                ]
        
        # Generate LLM response
        response_text = await llm_service.generate_response(
            user_message=chat_request.message,
            context_docs=context_docs,
            role=chat_request.role or conversation.role
        )
        
        # Store assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            sources=[doc.id for doc in source_documents] if source_documents else None
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return ChatResponse(
            message=response_text,
            conversation_id=conversation.id,
            sources=source_documents if source_documents else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )

