"""Direct PostgreSQL Vector Store - Bypasses Supabase SDK"""

import psycopg2
from psycopg2.extras import Json
from vector_store_base import VectorStore
import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class DirectPostgresVectorStore(VectorStore):
    """Vector store using direct PostgreSQL connection (no SDK overhead)"""

    def __init__(self):
        """Initialize direct PostgreSQL connection from DATABASE_URL"""
        self.connection_string = os.getenv(
            "DATABASE_URL",
            os.getenv("SUPABASE_DATABASE_URL", "")
        )
        
        if not self.connection_string:
            raise ValueError(
                "DATABASE_URL or SUPABASE_DATABASE_URL not set in .env\n"
                "Example: postgresql://user:password@host:port/dbname"
            )
        
        try:
            # Test connection
            self.conn = psycopg2.connect(self.connection_string)
            self.conn.autocommit = True
            print("[OK] Connected to PostgreSQL directly")
            
            # Ensure pgvector is available
            with self.conn.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create tables if needed
            self._create_tables()
            
        except psycopg2.Error as e:
            raise ConnectionError(f"PostgreSQL connection failed: {e}")

    def _create_tables(self):
        """Create embeddings table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.embeddings (
            id BIGSERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector(1024),
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
        ON public.embeddings 
        USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100);
        """
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(create_table_sql)
            print("[OK] Embeddings table ready")
        except psycopg2.Error as e:
            print(f"[!] Table creation: {e}")

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Search for similar vectors using pgvector cosine similarity"""
        if not query_embedding:
            return []
        
        # Convert to PostgreSQL vector format
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        search_sql = f"""
        SELECT 
            id,
            content,
            metadata,
            1 - (embedding <=> %s::vector(1024)) as similarity
        FROM public.embeddings
        WHERE 1 - (embedding <=> %s::vector(1024)) > 0.3
        ORDER BY embedding <=> %s::vector(1024)
        LIMIT %s;
        """
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(search_sql, (embedding_str, embedding_str, embedding_str, top_k))
                results = cursor.fetchall()
                
                return [
                    {
                        "id": row[0],
                        "content": row[1],
                        "metadata": row[2],
                        "similarity": float(row[3])
                    }
                    for row in results
                ]
        except psycopg2.Error as e:
            print(f"Search error: {e}")
            return []

    def add_document(self, content: str, embedding: List[float], metadata: Dict = None):
        """Add a document with embedding to the database"""
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        insert_sql = """
        INSERT INTO public.embeddings (content, embedding, metadata)
        VALUES (%s, %s::vector(1024), %s);
        """
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(insert_sql, (content, embedding_str, Json(metadata or {})))
            print(f"[OK] Added document: {content[:50]}...")
        except psycopg2.Error as e:
            print(f"Insert error: {e}")

    def delete_document(self, doc_id: int) -> bool:
        """Delete a document by ID"""
        delete_sql = "DELETE FROM public.embeddings WHERE id = %s;"
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(delete_sql, (doc_id,))
                return cursor.rowcount > 0
        except psycopg2.Error as e:
            print(f"Delete error: {e}")
            return False

    def clear_all(self):
        """Clear all embeddings from the database"""
        truncate_sql = "TRUNCATE TABLE public.embeddings RESTART IDENTITY;"
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(truncate_sql)
            print("[OK] Cleared all embeddings")
        except psycopg2.Error as e:
            print(f"Clear error: {e}")

    def get_total_documents(self) -> int:
        """Get total number of documents in database"""
        count_sql = "SELECT COUNT(*) FROM public.embeddings;"
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(count_sql)
                return cursor.fetchone()[0]
        except psycopg2.Error as e:
            print(f"Count error: {e}")
            return 0

    def health_check(self):
        """Test database connectivity"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
            print("[OK] Direct PostgreSQL health check passed")
        except psycopg2.Error as e:
            raise ConnectionError(f"Health check failed: {e}")
