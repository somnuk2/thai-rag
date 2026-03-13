"""
Factory for creating appropriate Vector Store based on configuration
"""

import os
from config import Config
from vector_store_base import VectorStore
from local_vector_store import LocalVectorStore


def create_vector_store() -> VectorStore:
    """
    Create vector store based on configuration priority:
    
    1. Direct PostgreSQL (DATABASE_URL) - Fastest, no SDK
    2. Supabase SDK (RAG_MODE=supabase) - Cloud managed
    3. Local JSON (Default) - Always available
    
    Returns:
        VectorStore instance
    """
    
    # Priority 1: Direct PostgreSQL connection (bypasses SDK issues)
    if os.getenv("DATABASE_URL"):
        try:
            from direct_postgres_vector_store import DirectPostgresVectorStore
            print("[✓] Using Direct PostgreSQL Vector Store")
            return DirectPostgresVectorStore()
        except Exception as e:
            print(f"[!] Direct PostgreSQL failed: {e}")
            print("    Falling back to alternative...")
    
    # Priority 2: Supabase SDK
    if Config.MODE == "supabase":
        try:
            from supabase_vector_store import SupabaseVectorStore
            print("[✓] Using Supabase Vector Store (SDK)")
            return SupabaseVectorStore()
        except ImportError:
            print("[!] Supabase SDK not installed")
        except Exception as e:
            print(f"[!] Supabase connection failed: {e}")
    
    # Priority 3: Local JSON (fallback)
    print("[✓] Using Local Vector Store (JSON files)")
    return LocalVectorStore()
