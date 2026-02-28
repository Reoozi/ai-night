import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file automatically

class Settings:
    embedding_ollama: str = os.environ.get("Embedding_OLLAMA", "nomic-embed-text:latest")
    nvidia_key: str = os.environ.get("NVIDIA_API_KEY", "")  
    
    # PostgreSQL Vector Database
    pgvector_host: str = os.environ.get("PGVECTOR_HOST", "localhost")
    pgvector_port: int = int(os.environ.get("PGVECTOR_PORT", "5432"))
    pgvector_database: str = os.environ.get("PGVECTOR_DB", "rag_db")
    pgvector_user: str = os.environ.get("PGVECTOR_USER", "postgres")
    pgvector_password: str = os.environ.get("PGVECTOR_PASSWORD", "password")
    pgvector_connection_string: str = f"postgresql://{pgvector_user}:{pgvector_password}@{pgvector_host}:{pgvector_port}/{pgvector_database}"
    
    # Embedding settings - CONSTRAINT: Must be all-MiniLM-L6-v2
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_dimension: int = 384  # For all-MiniLM-L6-v2 (FIXED)
    
    # Document splitting
    chunk_size: int = int(os.environ.get("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.environ.get("CHUNK_OVERLAP", "50"))
    
    # RAG settings - CONSTRAINT: Must be 3
    top_k_results: int = int(os.environ.get("TOP_K_RESULTS", "3"))
    
    # Database table name for bakery ingredients embeddings
    embeddings_table: str = "embeddings"
    fragments_column: str = "texte_fragment"
    vector_column: str = "vecteur"

settings = Settings()

