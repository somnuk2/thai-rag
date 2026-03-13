"""
Supabase Vector Store Implementation
Uses Supabase pgvector for remote storage
"""

from typing import List, Dict, Any
from vector_store_base import VectorStore
from config import Config

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  supabase-py not installed. Install with: pip install supabase")
    Client = None


class SupabaseVectorStore(VectorStore):
    """Vector store using Supabase pgvector"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Supabase vector store
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
        """
        if Client is None:
            raise ImportError("supabase-py not installed. Run: pip install supabase")
        
        self.url = supabase_url or Config.SUPABASE_URL
        self.key = supabase_key or Config.SUPABASE_KEY
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY required")
        
        try:
            self.client: Client = create_client(self.url, self.key)
            self.health_check()
            print("✅ Connected to Supabase")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
    
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar documents using pgvector
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            
        Returns:
            List of matching documents
        """
        try:
            # Call RPC function for vector search
            result = self.client.rpc(
                'match_embeddings',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': Config.SIMILARITY_THRESHOLD,
                    'match_count': top_k
                }
            ).execute()
            
            if result.data:
                return result.data
            return []
        
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def add_document(self, content: str, embedding: List[float], 
                     metadata: Dict = None, document_id: int = None) -> bool:
        """
        Add document to Supabase
        
        Args:
            content: Document text
            embedding: Document embedding
            metadata: Additional metadata
            document_id: Optional document ID
            
        Returns:
            True if successful
        """
        try:
            data = {
                'content': content[:5000],  # Truncate if too long
                'embedding': embedding,
                'metadata': metadata or {}
            }
            
            # Only include document_id if provided
            if document_id is not None:
                data['document_id'] = document_id
            
            self.client.table('embeddings').insert(data).execute()
            return True
        
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from Supabase
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful
        """
        try:
            self.client.table('embeddings').delete().eq('id', int(doc_id)).execute()
            return True
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return False
    
    def get_total_documents(self) -> int:
        """Get total number of documents"""
        try:
            result = self.client.table('embeddings').select('id').execute()
            return len(result.data) if result.data else 0
        except Exception:
            return 0
    
    def clear_all(self) -> bool:
        """Clear all documents (use with caution!)"""
        try:
            self.client.table('embeddings').delete().neq('id', 0).execute()
            return True
        except Exception as e:
            print(f"❌ Error clearing store: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Supabase is accessible"""
        try:
            self.client.table('embeddings').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"❌ Supabase health check failed: {e}")
            return False
