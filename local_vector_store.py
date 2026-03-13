"""
Local Vector Store Implementation
Uses JSON files for storage (Original System)
"""

import json
import torch
from pathlib import Path
from typing import List, Dict, Any
from vector_store_base import VectorStore
from config import Config


class LocalVectorStore(VectorStore):
    """Vector store using local JSON files"""
    
    def __init__(self, vault_path: str = None, cache_path: str = None):
        """
        Initialize local vector store
        
        Args:
            vault_path: Path to vault.txt (document content)
            cache_path: Path to embeddings cache JSON
        """
        self.vault_path = Path(vault_path or Config.VAULT_PATH)
        self.cache_path = Path(cache_path or Config.CACHE_PATH)
        
        # Load existing embeddings and content
        self.embeddings = []
        self.content = []
        self.embeddings_tensor = None
        
        self._load_from_cache()
    
    def _load_from_cache(self):
        """Load embeddings from cache file"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.embeddings = data.get('embeddings', [])
                    print(f"✅ Loaded {len(self.embeddings)} embeddings from cache")
            except Exception as e:
                print(f"❌ Error loading cache: {e}")
        
        # Load content from vault
        if self.vault_path.exists():
            try:
                with open(self.vault_path, 'r', encoding='utf-8') as f:
                    self.content = f.readlines()
                print(f"✅ Loaded {len(self.content)} content chunks from vault")
            except Exception as e:
                print(f"❌ Error loading vault: {e}")
        
        # Convert to tensor
        if self.embeddings:
            self.embeddings_tensor = torch.tensor(self.embeddings)
        else:
            self.embeddings_tensor = torch.tensor([])
    
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity
        
        Args:
            query_embedding: Query vector (1024 dims for mxbai-embed-large)
            top_k: Number of top results
            
        Returns:
            List of matching documents with similarity scores
        """
        if self.embeddings_tensor.nelement() == 0:
            return []
        
        # Calculate cosine similarity
        query_tensor = torch.tensor(query_embedding).unsqueeze(0)
        cos_scores = torch.cosine_similarity(query_tensor, self.embeddings_tensor)
        
        # Get top-k
        top_k = min(top_k, len(cos_scores))
        top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
        
        # Format results
        results = []
        for idx in top_indices:
            if idx < len(self.content):
                results.append({
                    'id': idx,
                    'content': self.content[idx].strip(),
                    'similarity': float(cos_scores[idx].item())
                })
        
        return results
    
    def add_document(self, content: str, embedding: List[float], metadata: Dict = None) -> bool:
        """
        Add document to local store
        
        Args:
            content: Document text
            embedding: Document embedding vector
            metadata: Additional metadata (ignored in local mode)
            
        Returns:
            True if successful
        """
        try:
            # Add to content
            with open(self.vault_path, 'a', encoding='utf-8') as f:
                f.write(content + "\n")
            
            # Add to embeddings
            self.embeddings.append(embedding)
            self.embeddings_tensor = torch.tensor(self.embeddings)
            
            # Save cache
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump({'embeddings': self.embeddings}, f)
            
            return True
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from local store
        Note: This is not efficient for JSON-based storage
        
        Args:
            doc_id: Index as string
            
        Returns:
            True if successful
        """
        try:
            idx = int(doc_id)
            if 0 <= idx < len(self.embeddings):
                self.embeddings.pop(idx)
                self.content.pop(idx)
                self.embeddings_tensor = torch.tensor(self.embeddings)
                
                # Rebuild files
                with open(self.vault_path, 'w', encoding='utf-8') as f:
                    f.writelines(self.content)
                
                with open(self.cache_path, 'w', encoding='utf-8') as f:
                    json.dump({'embeddings': self.embeddings}, f)
                
                return True
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
        
        return False
    
    def get_total_documents(self) -> int:
        """Get total number of documents"""
        return len(self.embeddings)
    
    def clear_all(self) -> bool:
        """Clear all documents"""
        try:
            with open(self.vault_path, 'w', encoding='utf-8') as f:
                f.write("")
            
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump({'embeddings': []}, f)
            
            self.embeddings = []
            self.content = []
            self.embeddings_tensor = torch.tensor([])
            
            return True
        except Exception as e:
            print(f"❌ Error clearing store: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if store is accessible"""
        try:
            return self.vault_path.exists() or True  # Local is always "healthy"
        except Exception:
            return False
