"""
RunPod API client for embedding and LLM inference jobs.
"""
import httpx
import json
import asyncio
from typing import List, Dict, Optional, Any
from backend.config import settings


class RunPodService:
    """Service for interacting with RunPod API."""
    
    def __init__(self):
        self.api_key = settings.runpod_api_key
        self.base_url = "https://api.runpod.io/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def run_job(
        self,
        endpoint_id: str,
        input_data: Dict[str, Any],
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Run a job on RunPod endpoint.
        
        Args:
            endpoint_id: RunPod endpoint ID
            input_data: Input data for the job
            timeout: Timeout in seconds
            
        Returns:
            Job result dictionary
        """
        if not self.api_key:
            raise ValueError("RunPod API key not configured")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Start job - RunPod API uses /run-sync for synchronous jobs
            # or /run for async jobs that need polling
            response = await client.post(
                f"{self.base_url}/{endpoint_id}/run",
                headers=self.headers,
                json={"input": input_data}
            )
            response.raise_for_status()
            job_data = response.json()
            
            # Check if it's a sync job (returns output directly)
            if "output" in job_data:
                return job_data.get("output", {})
            
            # Otherwise poll for async job
            job_id = job_data.get("id")
            if not job_id:
                raise RuntimeError("No job ID returned from RunPod")
            
            # Poll for completion
            max_iterations = timeout // 2
            iteration = 0
            while iteration < max_iterations:
                status_response = await client.get(
                    f"{self.base_url}/{endpoint_id}/status/{job_id}",
                    headers=self.headers
                )
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status", "").upper()
                if status == "COMPLETED":
                    return status_data.get("output", {})
                elif status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    raise RuntimeError(f"RunPod job failed: {error}")
                
                await asyncio.sleep(2)
                iteration += 1
            
            raise TimeoutError(f"RunPod job timed out after {timeout} seconds")
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using RunPod.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not settings.runpod_embedding_pod_id:
            raise ValueError("RunPod embedding pod ID not configured")
        
        input_data = {
            "texts": texts,
            "model": settings.embedding_model
        }
        
        result = await self.run_job(settings.runpod_embedding_pod_id, input_data)
        return result.get("embeddings", [])
    
    async def generate_completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate LLM completion using RunPod.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        if not settings.runpod_llm_pod_id:
            raise ValueError("RunPod LLM pod ID not configured")
        
        input_data = {
            "prompt": prompt,
            "model": settings.llm_model,
            "temperature": temperature or settings.llm_temperature,
            "max_tokens": max_tokens or settings.llm_max_tokens
        }
        
        result = await self.run_job(settings.runpod_llm_pod_id, input_data)
        return result.get("text", "")


# Singleton instance
runpod_service = RunPodService()

