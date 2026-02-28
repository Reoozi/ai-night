"""ChromaDB vector storage service - No Docker required!"""
import chromadb
from chromadb.config import Settings as ChromaSettings
import numpy as np
from core.config import settings
from utils.logger import logger
from typing import List, Dict
import os


class ChromaVectorStore:
    """Manages vector storage and retrieval using ChromaDB (no external database needed)."""
    
    def __init__(self):
        self.embedding_dim = settings.embedding_dimension
        self.collection_name = settings.embeddings_table
        self.init_db()
    
    def init_db(self):
        """Initialize ChromaDB client and create collection if it doesn't exist.
        
        ChromaDB is a Python-native vector database that requires no external services.
        It stores data locally in the 'chroma_db' directory.
        """
        try:
            # Create persistent ChromaDB client
            persist_directory = os.path.join(os.getcwd(), "chroma_db")
            
            logger.info(f"Initializing ChromaDB at: {persist_directory}")
            
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=None  # We provide embeddings manually
                )
                logger.info(f"Loaded existing collection '{self.collection_name}'")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=None,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )
                logger.info(f"Created new collection '{self.collection_name}'")
            
            logger.info(f"ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"ChromaDB initialization error: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict], embeddings: List[np.ndarray]) -> List[int]:
        """Add documents with embeddings to ChromaDB.
        
        Args:
            documents: List of dicts with 'content'/'texte_fragment' and metadata
            embeddings: List of embedding vectors
            
        Returns:
            List of inserted document IDs
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match")
        
        try:
            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            embeddings_list = []
            
            # Get current count for IDs
            current_count = self.collection.count()
            
            for idx, (doc, emb) in enumerate(zip(documents, embeddings)):
                # Generate unique ID
                doc_id = f"doc_{current_count + idx}"
                ids.append(doc_id)
                
                # Get text fragment
                text = doc.get('texte_fragment') or doc.get('content', '')
                texts.append(text)
                
                # Prepare metadata
                metadata = {
                    'id_document': doc.get('id_document', idx),
                    'source': doc.get('source', 'unknown')
                }
                metadatas.append(metadata)
                
                # Convert embedding to list
                emb_list = emb.tolist() if isinstance(emb, np.ndarray) else emb
                embeddings_list.append(emb_list)
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Inserted {len(ids)} documents into ChromaDB collection '{self.collection_name}'")
            return list(range(len(ids)))
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict]:
        """Search for similar documents using cosine similarity.
        
        CONSTRAINT: Uses cosine similarity (configured in collection metadata)
        CONSTRAINT: Returns top_k=3 results
        
        Args:
            query_embedding: Query vector (from all-MiniLM-L6-v2)
            top_k: Number of results to return (default 3)
            
        Returns:
            List of dicts with 'texte_fragment', 'similarity_score'
        """
        try:
            # Convert numpy array to list
            emb_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[emb_list],
                n_results=top_k,
                include=['documents', 'distances', 'metadatas']
            )
            
            # Format results according to challenge requirements
            formatted_results = []
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    # ChromaDB returns distances, convert to similarity
                    # For cosine: similarity = 1 - distance
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    
                    formatted_results.append({
                        'rank': i + 1,
                        'texte_fragment': results['documents'][0][i],
                        'similarity_score': round(float(similarity), 2)  # 2 decimals as required
                    })
            
            logger.info(f"Found {len(formatted_results)} similar documents from ChromaDB")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def delete_all_documents(self):
        """Delete all documents from the collection. Use with caution!"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=None,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.warning(f"All documents deleted from collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the collection."""
        try:
            count = self.collection.count()
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0


# Global instance
chroma_store = ChromaVectorStore()
