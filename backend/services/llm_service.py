"""
Service for LLM inference orchestration.
"""
from typing import Optional
from backend.services.runpod_service import runpod_service
from backend.services.prompt_service import prompt_service
from backend.config import settings


class LLMService:
    """Service for LLM completion generation."""
    
    async def generate_response(
        self,
        user_message: str,
        context_docs: Optional[list] = None,
        role: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate LLM response with optional RAG context.
        
        Args:
            user_message: User's message
            context_docs: Retrieved documents for RAG
            role: Assistant role
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        # Build prompt
        if context_docs:
            prompt = prompt_service.build_rag_prompt(
                user_message=user_message,
                context_docs=context_docs,
                role=role
            )
        else:
            prompt = prompt_service.build_simple_prompt(
                user_message=user_message,
                role=role
            )
        
        # Generate completion via RunPod
        response = await runpod_service.generate_completion(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response


# Singleton instance
llm_service = LLMService()

