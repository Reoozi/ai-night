import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file automatically

class Settings:
    embedding_ollama: str = os.environ.get("Embedding_OLLAMA", "nomic-embed-text:latest")
    nvidia_key: str = os.environ.get("NVIDIA_API_KEY", "")  
    
    # ChromaDB Vector Database (No Docker required!)
    # ChromaDB stores data locally in the 'chroma_db' directory
    chroma_persist_directory: str = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Embedding settings - CONSTRAINT: Must be all-MiniLM-L6-v2
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_dimension: int = 384  # For all-MiniLM-L6-v2 (FIXED)
    
    # Document splitting
    chunk_size: int = int(os.environ.get("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.environ.get("CHUNK_OVERLAP", "50"))
    
    # RAG settings - CONSTRAINT: Must be 3
    top_k_results: int = int(os.environ.get("TOP_K_RESULTS", "3"))
    
    # Collection name for bakery ingredients embeddings
    embeddings_table: str = "embeddings"
    fragments_column: str = "texte_fragment"
    vector_column: str = "vecteur"

settings = Settings()

