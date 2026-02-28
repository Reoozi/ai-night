"""PostgreSQL pgvector storage service."""
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
import numpy as np
from core.config import settings
from utils.logger import logger
from typing import List, Dict, Tuple
import json


class PgVectorStore:
    """Manages vector storage and retrieval using PostgreSQL pgvector."""
    
    def __init__(self):
        self.connection_string = settings.pgvector_connection_string
        self.embedding_dim = settings.embedding_dimension
        self.table_name = settings.embeddings_table
        self.fragments_column = settings.fragments_column
        self.vector_column = settings.vector_column
        self.init_db()
    
    def _get_connection(self):
        """Create a new database connection."""
        try:
            conn = psycopg2.connect(self.connection_string)
            register_vector(conn)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def init_db(self):
        """Initialize database and create tables if they don't exist.
        
        For the bakery challenge, uses the 'embeddings' table:
        - id (PRIMARY KEY)
        - id_document (int)
        - texte_fragment (text)
        - vecteur (vector(384))
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Enable pgvector extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create embeddings table if it doesn't exist
            # (For the challenge, the table should already be populated)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    id_document INT,
                    {self.fragments_column} TEXT NOT NULL,
                    {self.vector_column} vector({self.embedding_dim}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster similarity search
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.table_name}_vector_idx 
                ON {self.table_name} USING ivfflat ({self.vector_column} vector_cosine_ops)
                WITH (lists = 100)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Database initialized successfully with table '{self.table_name}'")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict], embeddings: List[np.ndarray]) -> List[int]:
        """Add documents with embeddings to database.
        
        Args:
            documents: List of dicts with 'content'/'texte_fragment' and metadata
            embeddings: List of embedding vectors
            
        Returns:
            List of inserted document IDs
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Prepare data for insertion
            data = []
            for doc, emb in zip(documents, embeddings):
                fragment_text = doc.get('texte_fragment') or doc.get('content', '')
                id_doc = doc.get('id_document', None)
                
                # Convert numpy array to list for psycopg2
                emb_list = emb.tolist() if isinstance(emb, np.ndarray) else emb
                
                data.append((id_doc, fragment_text, emb_list))
            
            # Batch insert
            query = f"""
                INSERT INTO {self.table_name} (id_document, {self.fragments_column}, {self.vector_column})
                VALUES %s
                RETURNING id
            """
            
            execute_values(cursor, query, data, fetch=False)
            conn.commit()
            
            inserted_count = cursor.rowcount
            cursor.close()
            conn.close()
            
            logger.info(f"Inserted {inserted_count} documents into {self.table_name}")
            return list(range(inserted_count))
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict]:
        """Search for similar documents using cosine similarity (pgvector <=> operator).
        
        CONSTRAINT: Uses cosine similarity via pgvector <=> operator
        CONSTRAINT: Returns top_k=3 results
        
        Args:
            query_embedding: Query vector (from all-MiniLM-L6-v2)
            top_k: Number of results to return (default 3)
            
        Returns:
            List of dicts with 'texte_fragment', 'similarity_score'
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convert numpy array to list
            emb_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
            
            # Search using cosine similarity with pgvector <=> operator
            # The <=> operator returns cosine distance, so we compute 1 - distance = similarity
            query = f"""
                SELECT id, {self.fragments_column}, 
                       1 - ({self.vector_column} <=> %s::vector) as similarity_score
                FROM {self.table_name}
                ORDER BY similarity_score DESC
                LIMIT %s
            """
            
            cursor.execute(query, (emb_list, top_k))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Format results according to challenge requirements
            formatted_results = []
            for i, row in enumerate(results, 1):
                doc_id, fragment, similarity = row
                formatted_results.append({
                    'rank': i,
                    'texte_fragment': fragment,
                    'similarity_score': round(float(similarity), 2)  # 2 decimals as required
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def delete_all_documents(self):
        """Delete all documents from the database. Use with caution!"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {self.table_name}")
            conn.commit()
            cursor.close()
            conn.close()
            logger.warning(f"All documents deleted from {self.table_name}")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    def get_document_count(self) -> int:
        """Get the total number of documents in database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0


# Global instance
pgvector_store = PgVectorStore()
