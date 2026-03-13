"""
Abstract Base Class for Vector Store
Supports both Local and Remote implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple


class VectorStore(ABC):
    """Base class for vector storage"""
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            List of results with content and similarity score
        """
        pass
    
    @abstractmethod
    def add_document(self, content: str, embedding: List[float], metadata: Dict = None) -> bool:
        """
        Add a document with embedding
        
        Args:
            content: Document content
            embedding: Document embedding
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def get_total_documents(self) -> int:
        """Get total number of documents"""
        pass
    
    @abstractmethod
    def clear_all(self) -> bool:
        """Clear all vectors"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if vector store is accessible"""
        pass
