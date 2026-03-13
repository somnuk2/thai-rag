"""
Configuration Module for Easy Local RAG
Supports both Local and Supabase (Remote) modes
"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration for RAG system"""
    
    # Mode: 'local' or 'supabase'
    MODE: str = os.getenv("RAG_MODE", "local")
    
    # ==========================================
    # Ollama Configuration
    # ==========================================
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_API_KEY: str = os.getenv("OLLAMA_API_KEY", "llama3")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
    OLLAMA_CHAT_MODEL: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
    
    # ==========================================
    # Local Mode Configuration (JSON Files)
    # ==========================================
    VAULT_PATH: str = os.getenv("VAULT_PATH", "vault.txt")
    CACHE_PATH: str = os.getenv("CACHE_PATH", "vault_embeddings_cache.json")
    
    # ==========================================
    # Supabase Configuration (Remote)
    # ==========================================
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # ==========================================
    # RAG Configuration
    # ==========================================
    TOP_K: int = int(os.getenv("TOP_K", "3"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.0"))
    
    # ==========================================
    # System Configuration
    # ==========================================
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if cls.MODE not in ["local", "supabase"]:
            raise ValueError(f"Invalid RAG_MODE: {cls.MODE}. Must be 'local' or 'supabase'")
        
        if cls.MODE == "supabase":
            if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY required for Supabase mode")
        
        if cls.MODE == "local":
            if not Path(cls.VAULT_PATH).exists():
                print(f"⚠️  Warning: {cls.VAULT_PATH} not found. Create it with document content.")
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print(f"{'='*60}")
        print(f"RAG Configuration")
        print(f"{'='*60}")
        print(f"Mode: {cls.MODE}")
        print(f"Ollama Model: {cls.OLLAMA_CHAT_MODEL}")
        print(f"Embedding Model: {cls.OLLAMA_EMBED_MODEL}")
        print(f"Top-K: {cls.TOP_K}")
        
        if cls.MODE == "local":
            print(f"Vault Path: {cls.VAULT_PATH}")
            print(f"Cache Path: {cls.CACHE_PATH}")
        elif cls.MODE == "supabase":
            print(f"Supabase URL: {cls.SUPABASE_URL}")
        
        print(f"{'='*60}\n")


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("\nPlease check your .env file or environment variables")
    import sys
    sys.exit(1)
