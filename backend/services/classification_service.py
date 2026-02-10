"""
Service for flexible classification using local LLM.
"""
import json
from typing import List, Dict, Any, Optional
from backend.services.runpod_service import runpod_service
from backend.models.database import CategorySchema


class ClassificationService:
    """Classify captured content into dynamic schemas."""
    
    async def classify_text(
        self,
        text: str,
        schemas: List[CategorySchema]
    ) -> Dict[str, Any]:
        """
        Classify text into one of the provided schemas.
        
        Returns dict with: category, title, fields, confidence, follow_up_questions
        """
        schema_spec = [
            {
                "name": schema.name,
                "description": schema.description or "",
                "fields": schema.fields,
            }
            for schema in schemas
        ]
        
        prompt = (
            "You are a classification engine. Return JSON only, no markdown.\n"
            "Choose exactly one category from the provided list.\n"
            "Output JSON keys: category, title, fields, confidence, follow_up_questions.\n"
            "- category: string\n"
            "- title: short title for the entry\n"
            "- fields: object with only keys defined in the chosen schema\n"
            "- confidence: integer 0-100\n"
            "- follow_up_questions: list of short questions if info is missing\n\n"
            f"SCHEMAS: {json.dumps(schema_spec)}\n\n"
            f"INPUT: {text}\n"
        )
        
        result_text = await runpod_service.generate_completion(
            prompt=prompt,
            temperature=0.2,
            max_tokens=500
        )
        
        try:
            parsed = json.loads(result_text)
            return {
                "category": parsed.get("category"),
                "title": parsed.get("title"),
                "fields": parsed.get("fields"),
                "confidence": parsed.get("confidence"),
                "follow_up_questions": parsed.get("follow_up_questions"),
            }
        except Exception:
            return {
                "category": None,
                "title": None,
                "fields": None,
                "confidence": 0,
                "follow_up_questions": [
                    "I could not parse the classification output. Please specify the category."
                ],
            }


classification_service = ClassificationService()
