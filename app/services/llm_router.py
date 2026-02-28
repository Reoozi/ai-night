from services import nvidia_services
from services.rag_service import rag_service
from utils.logger import logger
from typing import Optional


async def get_llm_response(prompt: str, model: str = "nvidia") -> str:
    """
    Get response from LLM with optional RAG augmentation.
    
    Args:
        prompt: User prompt/question
        model: One of ["ollama", "nvidia", "ragwithollama", "ragwithnvidia"]
    
    Returns:
        Generated response from the LLM
    """
    try:
        # Check if RAG should be used
        if model in ["ragwithollama", "ragwithnvidia"]:
            # Retrieve relevant context using RAG
            logger.info(f"Using RAG with model: {model}")
            retrieval_result = await rag_service.retrieve(
                query=prompt,
                top_k=3,
                use_reranker=True
            )
            
            if retrieval_result.get("status") == "success":
                # Build augmented prompt with retrieved context
                context = "\n\n".join([
                    f"[Chunk {i+1}] {result['content']}"
                    for i, result in enumerate(retrieval_result.get("results", []))
                ])
                
                augmented_prompt = f"""Context from knowledge base:
{context}

---

User Question: {prompt}

Please answer the question based on the context provided above."""
                
                logger.info(f"Augmented prompt with {len(retrieval_result.get('results', []))} context chunks")
            else:
                logger.warning(f"RAG retrieval failed: {retrieval_result.get('message')}")
                augmented_prompt = prompt
        else:
            augmented_prompt = prompt
        
        # Route to appropriate LLM service
        # Currently using NVIDIA API for all models
        logger.info(f"Using NVIDIA API for model: {model}")
        response = await nvidia_services.ask(augmented_prompt)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in get_llm_response: {str(e)}")
        raise

