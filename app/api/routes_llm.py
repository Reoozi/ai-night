
from fastapi import APIRouter
from pydantic import BaseModel
from services.llm_router import get_llm_response
from schemas.llm_schema import LLMRequest, LLMResponse

router = APIRouter()


@router.post("/retrivel", response_model=LLMResponse)
async def ask_llm(request: LLMRequest):
    """
    Query the LLM with optional RAG augmentation.
    
    Models available:
    - ollama: Local Ollama model
    - nvidia: NVIDIA API
    - ragwithollama: Ollama with RAG context
    - ragwithnvidia: NVIDIA with RAG context
    """
    result = await get_llm_response(request.prompt, request.model)
    return {"response": result}
