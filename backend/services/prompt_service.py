"""
Service for building prompts with role injection and context.
"""
from typing import List, Dict, Any, Optional


class PromptService:
    """Service for constructing assistant prompts."""
    
    ROLE_TEMPLATES = {
        "coach": "You are a creative coach helping with projects and motivation.",
        "counselor": "You are a thoughtful counselor providing reflection and guidance.",
        "planner": "You are a planning assistant helping organize tasks and timelines.",
        "default": "You are a helpful personal assistant."
    }
    
    def build_rag_prompt(
        self,
        user_message: str,
        context_docs: List[Dict[str, Any]],
        role: Optional[str] = None
    ) -> str:
        """
        Build a prompt with RAG context and role injection.
        
        Args:
            user_message: User's message
            context_docs: Retrieved documents from RAG
            role: Assistant role (coach, counselor, etc.)
            
        Returns:
            Formatted prompt string
        """
        # Role injection
        role_text = self.ROLE_TEMPLATES.get(role, self.ROLE_TEMPLATES["default"])
        
        # Build context section
        context_section = ""
        if context_docs:
            context_section = "\n\nRelevant context from your knowledge base:\n"
            for i, doc in enumerate(context_docs, 1):
                content = doc.get("payload", {}).get("content", "")
                source = doc.get("payload", {}).get("source", "unknown")
                context_section += f"\n[{i}] From {source}:\n{content}\n"
        
        # Construct full prompt
        prompt = f"""{role_text}

{context_section}

User: {user_message}

Assistant:"""
        
        return prompt
    
    def build_simple_prompt(
        self,
        user_message: str,
        role: Optional[str] = None
    ) -> str:
        """Build a simple prompt without RAG context."""
        role_text = self.ROLE_TEMPLATES.get(role, self.ROLE_TEMPLATES["default"])
        
        prompt = f"""{role_text}

User: {user_message}

Assistant:"""
        
        return prompt


# Singleton instance
prompt_service = PromptService()

