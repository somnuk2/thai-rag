# Supabase Setup Guide - Step by Step

**เอกสารคู่มือการตั้งค่า Supabase สำหรับโปรเจกต์ Local RAG**

---

## ✅ Step 1: สมัครสมาชิก Supabase

1. ไปที่ https://supabase.com
2. คลิก "Sign Up" หรือ "Get Started for Free"
3. เลือก Sign Up method (GitHub / Google / Email)
4. ยืนยันอีเมล (check inbox)
5. ทำการตั้งค่า Organization name

---

## ✅ Step 2: สร้าง Project ใหม่

1. ใน Dashboard ให้คลิก "New Project"
2. กรอก Database Password (บันทึกไว้อย่างปลอดภัย!)
3. เลือก Region ที่ใกล้ที่สุด (แนะนำ: Singapore หรือ Tokyo สำหรับเอเชีย)
4. เลือก Pricing Plan:
   - **Free Tier**: เหมาะสำหรับสำหรับทดสอบ (1 GB storage, 2 GB bandwidth)
   - **Pro**: สำหรับ production (pay as you go)
5. คลิก "Create new project"
6. รอ 2-3 นาทีให้ project ทำการตั้งค่าเสร็จ

---

## ✅ Step 3: บันทึก Connection Details

เมื่อ project สร้างเสร็จ:

1. ไปที่ **Settings** > **Database** > **Connection Info**
2. บันทึก:
   - **Host**: `db.xxxxxx.supabase.co`
   - **Password**: (ที่คุณตั้งไว้)
   - **Database name**: `postgres`
   - **User**: `postgres`

---

## ✅ Step 4: บันทึก API Keys

1. ไปที่ **Settings** > **API**
2. บันทึก:
   - **Project URL**: `https://xxxxxx.supabase.co`
   - **anon public**: `your-anon-key`
   - **service_role secret**: `your-service-role-key` (เก็บไว้ส่วนตัว!)

---

## ✅ Step 5: Enable pgvector Extension

1. ไปที่ **SQL Editor**
2. คลิก "New Query"
3. วาง SQL นี้:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

4. คลิก "Run"
5. ควรเห็น "Success" notification

---

## ✅ Step 6: สร้าง Tables

### Option A: ใช้ SQL Editor (แนะนำ)

1. ไปที่ **SQL Editor** > **New Query**
2. Copy-paste SQL ทั้งหมดด้านล่าง
3. คลิก "Run"

### SQL Script - สร้าง All Tables

```sql
-- ==========================================
-- TABLE 1: documents - เก็บข้อมูลเอกสาร
-- ==========================================
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512),
    file_hash VARCHAR(32) UNIQUE,
    file_size INTEGER,
    content_type VARCHAR(50),  -- 'pdf', 'txt', 'json'
    total_chunks INTEGER DEFAULT 0,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'  -- pending, processing, completed, failed
);

-- Index สำหรับการค้นหาด้วย file_hash
CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);


-- ==========================================
-- TABLE 2: embeddings - เก็บ vector embeddings
-- ==========================================
CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER DEFAULT 0,
    content TEXT NOT NULL,
    file_name VARCHAR(255),
    embedding VECTOR(1024) NOT NULL,  -- mxbai-embed-large dimension
    metadata JSONB DEFAULT '{}',  -- เก็บข้อมูลเพิ่มเติม
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

-- Vector Index - ใช้สำหรับการค้นหา similarity อย่างรวดเร็ว
CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
ON embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Regular Indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_file_name ON embeddings(file_name);


-- ==========================================
-- TABLE 3: conversation_history
-- ==========================================
CREATE TABLE IF NOT EXISTS conversation_history (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_history(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_created ON conversation_history(created_at);


-- ==========================================
-- TABLE 4: cache (optional - สำหรับ caching)
-- ==========================================
CREATE TABLE IF NOT EXISTS cache (
    id BIGSERIAL PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    results JSONB,
    ttl TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cache_ttl ON cache(ttl);
```

---

## ✅ Step 7: สร้าง Functions (สำหรับ Vector Search)

Copy-paste SQL ต่อไปนี้ใน SQL Editor:

```sql
-- ==========================================
-- FUNCTION: match_embeddings
-- ใช้สำหรับค้นหา embeddings ที่คล้ายคลึง
-- ==========================================
CREATE OR REPLACE FUNCTION match_embeddings (
    query_embedding VECTOR(1024),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    content TEXT,
    file_name VARCHAR,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT 
        embeddings.id,
        embeddings.document_id,
        embeddings.content,
        embeddings.file_name,
        (1 - (embeddings.embedding <=> query_embedding))::FLOAT as similarity
    FROM embeddings
    WHERE 1 - (embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- ==========================================
-- FUNCTION: match_embeddings_by_file
-- ค้นหาใน embeddings ของไฟล์เฉพาะ
-- ==========================================
CREATE OR REPLACE FUNCTION match_embeddings_by_file (
    query_embedding VECTOR(1024),
    target_file_name VARCHAR,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    content TEXT,
    file_name VARCHAR,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT 
        embeddings.id,
        embeddings.document_id,
        embeddings.content,
        embeddings.file_name,
        (1 - (embeddings.embedding <=> query_embedding))::FLOAT as similarity
    FROM embeddings
    WHERE embeddings.file_name = target_file_name
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
$$;
```

---

## ✅ Step 8: ตั้งค่า .env File

สร้างไฟล์ `.env` ในโฟลเดอร์โปรเจกต์:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Ollama Configuration (ยังคงใช้เดิม)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=llama3
OLLAMA_EMBED_MODEL=mxbai-embed-large

# RAG Configuration
DOC_VAULT_PATH=./vault.txt
CHUNK_SIZE=1000
OVERLAP=200
TOP_K=3
```

⚠️ **สำคัญ:** ไม่ควร commit `.env` ไปยัง git!

แทนนั้น commit `.env.example`:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=llama3
OLLAMA_EMBED_MODEL=mxbai-embed-large

# RAG Configuration
DOC_VAULT_PATH=./vault.txt
CHUNK_SIZE=1000
OVERLAP=200
TOP_K=3
```

---

## ✅ Step 9: ตัวอย่าง Python Code สำหรับการเชื่อมต่อ

### สร้างไฟล์: `supabase/config.py`

```python
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase_client() -> Client:
    """สร้าง Supabase client instance"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
    
    return create_client(supabase_url, supabase_key)


def test_connection():
    """ทดสอบการเชื่อมต่อกับ Supabase"""
    try:
        client = get_supabase_client()
        # ทดสอบการอ่านข้อมูล
        response = client.table("documents").select("*").limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
```

### สร้างไฟล์: `supabase/vector_store.py`

```python
import numpy as np
from supabase import Client
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SupabaseVectorStore:
    """Vector Store ที่ใช้ Supabase pgvector"""
    
    def __init__(self, client: Client):
        self.client = client
    
    def search_similar(
        self, 
        embedding: List[float], 
        top_k: int = 3,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        ค้นหา embeddings ที่คล้ายคลึง
        
        Args:
            embedding: Query embedding vector
            top_k: จำนวน results ที่ต้องการ
            threshold: Similarity threshold (0-1)
        
        Returns:
            List of similar embeddings with scores
        """
        try:
            # เรียกใช้ function ที่สร้างไว้
            result = self.client.rpc(
                'match_embeddings',
                {
                    'query_embedding': embedding,
                    'match_threshold': threshold,
                    'match_count': top_k
                }
            ).execute()
            
            return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    def add_embedding(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
        embedding: List[float],
        file_name: str = None,
        metadata: Dict = None
    ) -> bool:
        """เพิ่ม embedding ไปยัง database"""
        try:
            data = {
                'document_id': document_id,
                'chunk_index': chunk_index,
                'content': content,
                'embedding': embedding,
                'file_name': file_name,
                'metadata': metadata or {}
            }
            
            self.client.table('embeddings').insert(data).execute()
            return True
        
        except Exception as e:
            logger.error(f"Error adding embedding: {e}")
            return False
    
    def add_document(
        self,
        file_name: str,
        file_hash: str,
        content_type: str = 'pdf'
    ) -> int:
        """เพิ่มเอกสารใหม่ไปยัง database"""
        try:
            result = self.client.table('documents').insert({
                'file_name': file_name,
                'file_hash': file_hash,
                'content_type': content_type,
                'status': 'pending'
            }).execute()
            
            return result.data[0]['id'] if result.data else None
        
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return None
    
    def delete_document(self, document_id: int) -> bool:
        """ลบเอกสารและ embeddings ทั้งหมด"""
        try:
            self.client.table('documents').delete().eq('id', document_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False


# ตัวอย่างการใช้:
if __name__ == "__main__":
    from config import get_supabase_client
    
    client = get_supabase_client()
    vector_store = SupabaseVectorStore(client)
    
    # ตัวอย่าง: ค้นหา similar embeddings
    query_embedding = [0.1] * 1024  # dummy embedding
    results = vector_store.search_similar(query_embedding, top_k=5)
    print(f"Found {len(results)} similar embeddings")
```

---

## ✅ Step 10: ทดสอบการเชื่อมต่อ

1. เปิด Terminal ในโปรเจกต์
2. รัน:

```bash
python -m supabase.config
```

ผลลัพธ์ที่คาดหวัง:
```
✅ Supabase connection successful!
```

---

## 🐛 Troubleshooting

### ❌ "Missing SUPABASE_URL or SUPABASE_KEY"
- ตรวจสอบว่ามีไฟล์ `.env` ในโฟลเดอร์โปรเจกต์
- ตรวจสอบการเขียนค่าถูกต้อง

### ❌ "pgvector extension not found"
- ไปยัง SQL Editor
- Rerun: `CREATE EXTENSION IF NOT EXISTS vector;`

### ❌ Connection timeout
- ตรวจสอบ SUPABASE_URL ถูกต้อง
- ตรวจสอบ network connectivity

### ❌ "Table does not exist"
- ตรวจสอบว่า Tables สร้างแล้ว
- ตรวจสอบชื่อตัวพิมพ์เล็กใหญ่

---

## 📊 Verify Tables ถูกสร้างแล้ว

ใน SQL Editor รัน:

```sql
-- ดูทุก tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- ดูโครงสร้าง embeddings table
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'embeddings';

-- ดู indexes
SELECT indexname 
FROM pg_indexes 
WHERE tablename IN ('embeddings', 'documents');
```

ควรเห็น:
- ✅ documents
- ✅ embeddings
- ✅ conversation_history
- ✅ cache
- ✅ indexes สำหรับ vector search

---

## 🎯 Success!

ถ้าทำครบทุกขั้นตอน คุณอยู่พร้อมสำหรับ:
- Phase 2: Migration Script
- Phase 3: ปรับปรุง Code

---

**Next:** ดูเอกสาร `SUPABASE_MIGRATION_PLAN.md` สำหรับขั้นตอนต่อไป
