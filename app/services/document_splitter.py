"""Document splitting service for RAG."""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import settings
from utils.logger import logger
from typing import List


class DocumentSplitter:
    """Splits documents into chunks for vector embedding."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        logger.info(f"DocumentSplitter initialized with chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap}")
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        if not text or not text.strip():
            logger.warning("Empty text provided to split_text")
            return []
        
        chunks = self.splitter.split_text(text)
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks
    
    def split_documents(self, documents: List[dict]) -> List[dict]:
        """Split documents maintaining metadata.
        
        Args:
            documents: List of dicts with 'content' and optional metadata
            
        Returns:
            List of dicts with 'content', 'chunk_id', and original metadata
        """
        chunks_with_metadata = []
        chunk_id = 0
        
        for doc_idx, doc in enumerate(documents):
            content = doc.get('content', '')
            metadata = {k: v for k, v in doc.items() if k != 'content'}
            
            chunks = self.split_text(content)
            
            for chunk_idx, chunk in enumerate(chunks):
                chunks_with_metadata.append({
                    'content': chunk,
                    'chunk_id': chunk_id,
                    'doc_index': doc_idx,
                    'chunk_index': chunk_idx,
                    **metadata
                })
                chunk_id += 1
        
        logger.info(f"Total chunks created: {len(chunks_with_metadata)}")
        return chunks_with_metadata


# Global instance
document_splitter = DocumentSplitter()
