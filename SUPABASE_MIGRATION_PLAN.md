# แผนการย้ายข้อมูล Vector เข้าสู่ Supabase

**วันที่:** March 2026  
**สถานะ:** แผนการการก่อน

---

## 📋 สรุปอย่างย่อ

แผนนี้อธิบายขั้นตอนการเปลี่ยน Local RAG ให้ใช้ Supabase Vector Database แทนการเก็บข้อมูล JSON ไฟล์ในเครื่อง

---

## 🎯 วัตถุประสงค์

- ✅ ย้าย embeddings จากไฟล์ JSON ไป Supabase pgvector
- ✅ ปรับปรุงประสิทธิภาพการค้นหา vector
- ✅ รองรับ scaling ที่ดีขึ้น
- ✅ ปลอดภัยและเข้าถึงจากระยะไกลได้
- ✅ บริหารจัดการข้อมูล metadata ร่วมกับ embeddings

---

## 📊 สถาปัตยกรรมปัจจุบันเทียบกับเป้าหมาย

### โครงสร้างปัจจุบัน:
```
┌─────────────┐
│  PDF/TXT    │
│   Files     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Ollama Local   │  ◄── Embedding Generation
│  mxbai-embed    │
└──────┬──────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Local Storage (JSON Files)       │
│  - vault_embeddings.json          │
│  - vault.txt                      │
│  - vault_embeddings_cache.json    │
└──────────────────────────────────┘
```

### โครงสร้างเป้าหมาย:
```
┌─────────────┐
│  PDF/TXT    │
│   Files     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Ollama Local    │  ◄── Embedding Generation
│  mxbai-embed     │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Supabase PostgreSQL             │
│  - pgvector Extension            │
│  - embeddings table              │
│  - metadata storage              │
│  - Vector Search (similarity)    │
└──────────────────────────────────┘
```

---

## 🔑 Key Components ที่ต้องการ

### 1. Supabase Setup
- **Database:** PostgreSQL with pgvector extension
- **Authentication:** Supabase API Key
- **Vector Storage:** pgvector table

### 2. Python Dependencies (ใหม่)
```
supabase-py
python-dotenv  (อยู่แล้ว)
```

### 3. Environment Configuration
```
SUPABASE_URL: "https://xxx.supabase.co"
SUPABASE_KEY: "your_anon_key"
```

---

## 📝 ขั้นตอนการนำไปปฏิบัติ

### Phase 1: ตั้งค่า Supabase (1-2 วัน)

#### 1.1 สร้าง Supabase Project
- [ ] สมัครสมาชิก Supabase (https://supabase.com)
- [ ] สร้าง Organization ใหม่
- [ ] สร้าง Project ใหม่
- [ ] เลือก Region ที่ใกล้ที่สุด
- [ ] บันทึก URL และ API Keys

#### 1.2 Enable pgvector Extension
```sql
-- ใน Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 1.3 สร้าง Database Schema

**Table 1: embeddings**
```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    file_name VARCHAR(255),
    file_hash VARCHAR(32),
    embedding VECTOR(1024),  -- mxbai-embed-large dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_type VARCHAR(50) DEFAULT 'pdf'  -- pdf, email, text, etc.
);
```

**Table 2: documents**
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512),
    file_hash VARCHAR(32) UNIQUE,
    file_size INTEGER,
    content_type VARCHAR(50),
    total_chunks INTEGER DEFAULT 0,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);
```

**Table 3: conversation_history** (สำหรับ feature ในอนาคต)
```sql
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    role VARCHAR(50),  -- user, assistant, system
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 1.4 สร้าง Vector Index
```sql
-- สร้าง index เพื่อเร่งความเร็วในการค้นหา
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

#### 1.5 สร้าง Functions ในฐานข้อมูล (Optional)
```sql
-- Function สำหรับค้นหา vector ที่คล้ายคลึง
CREATE OR REPLACE FUNCTION match_embeddings (
    query_embedding VECTOR(1024),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id INT,
    content TEXT,
    file_name VARCHAR,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT 
        id,
        content,
        file_name,
        1 - (embedding <=> query_embedding) as similarity
    FROM embeddings
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
```

---

### Phase 2: สร้าง Migration Script (2-3 วัน)

#### 2.1 สร้าง Script: `migrate_to_supabase.py`

**วัตถุประสงค์:**
- อ่านข้อมูลจากไฟล์ JSON เดิม
- อัปโหลด embeddings ไปยัง Supabase
- บันทึก metadata ของแต่ละเอกสาร

**โครงสร้างของ Script:**
```python
# migrate_to_supabase.py

import json
from supabase import create_client, Client
from pathlib import Path
import os
from dotenv import load_dotenv

class SupabaseMigrator:
    def __init__(self):
        # Initialize Supabase client
        # Load embeddings from JSON
        # Create batch upload system
        pass
    
    def load_json_embeddings(self):
        # อ่านไฟล์ vault_embeddings.json
        # อ่านไฟล์ vault.txt
        pass
    
    def upload_to_supabase(self):
        # Split data into chunks
        # Upload in batches (เพราะฉะนั้นจึงเหมาะสำหรับจำนวนมากของ records)
        # Handle errors and retries
        pass
    
    def verify_migration(self):
        # ตรวจสอบจำนวน records
        # ทดสอบค้นหา vector
        pass

# Usage:
# migrator = SupabaseMigrator()
# migrator.load_json_embeddings()
# migrator.upload_to_supabase()
# migrator.verify_migration()
```

---

### Phase 3: ปรับปรุง Main Code (3-4 วัน)

#### 3.1 สร้าง Supabase Vector Store Class
```python
# supabase_vector_store.py

class SupabaseVectorStore:
    def __init__(self, supabase_url, supabase_key):
        self.client = create_client(supabase_url, supabase_key)
    
    def get_relevant_context(self, query_embedding, top_k=3):
        """เทียบเท่ากับ get_relevant_context() เดิม"""
        # ใช้ pgvector สำหรับค้นหา similarity
        pass
    
    def add_document(self, content, file_name, embedding):
        """เพิ่มเอกสารใหม่"""
        pass
    
    def delete_document(self, document_id):
        """ลบเอกสาร"""
        pass
    
    def update_document(self, document_id, content, embedding):
        """อัปเดตเอกสาร"""
        pass
```

#### 3.2 ปรับปรุง `localrag.py`
```python
# แก้ไขจำเป็น:

# ก่อน:
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    # ใช้ torch.cosine_similarity กับไฟล์ JSON
    pass

# หลัง:
def get_relevant_context(rewritten_input, vector_store, top_k=3):
    # ใช้ Supabase pgvector
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    results = vector_store.get_relevant_context(input_embedding, top_k)
    return results
```

#### 3.3 ปรับปรุง `process_specific_pdf.py`, `process_thai_pdf.py`
- เปลี่ยนจากบันทึกไฟล์ JSON → บันทึก Supabase
- แก้ไข file hash tracking

#### 3.4 สร้างไฟล์ `.env.example`
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=llama3
```

---

### Phase 4: ทดสอบและตรวจสอบ (2-3 วัน)

#### 4.1 Unit Tests
```python
# test_supabase_vector_store.py

def test_connection():
    # ทดสอบการเชื่อมต่อกับ Supabase
    pass

def test_upload_embedding():
    # ทดสอบอัปโหลด embedding
    pass

def test_similarity_search():
    # ทดสอบการค้นหา similarity
    pass

def test_metadata_storage():
    # ทดสอบการเก็บ metadata
    pass
```

#### 4.2 Integration Tests
```python
# test_localrag_supabase.py

def test_full_rag_flow():
    # ทดสอบ flow ทั้งหมด:
    # 1. อัปโหลด PDF
    # 2. สร้าง embeddings
    # 3. บันทึก Supabase
    # 4. ค้นหา vector
    # 5. ตอบคำถาม
    pass
```

#### 4.3 Performance Tests
- ทดสอบความเร็วการค้นหา
- ทดสอบจำนวน records ที่สามารถบันทึกได้
- ทดสอบการอัปโหลด batch ที่ใหญ่ขึ้น

#### 4.4 Data Validation
- ตรวจสอบจำนวน embeddings ตรงกัน
- ตรวจสอบความถูกต้องของ embeddings values
- ตรวจสอบ metadata ที่ครบถ้วน

---

### Phase 5: การปรับปรุงและการเพิ่มเติม (ค่อนข้างหลัง)

#### 5.1 Features เพิ่มเติม
- [ ] Conversation history tracking (ตารางมีอยู่แล้ว)
- [ ] Document tagging/categorization
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] Batch processing improvements

#### 5.2 Monitoring และ Logging
```python
# logging setup
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/supabase_rag.log'),
        logging.StreamHandler()
    ]
)
```

#### 5.3 Documentation Updates
- [ ] อัปเดต README.md
- [ ] สร้าง SUPABASE_SETUP.md (step-by-step guide)
- [ ] อัปเดต config.yaml documentation

---

## 🛠️ Required Tools และ Libraries

### ใหม่ที่เพิ่ม:
```txt
supabase[python]==1.0.0
python-dotenv==1.0.0
```

### ที่มีอยู่แล้ว (ยังคง ใช้):
```txt
openai
torch
PyPDF2
ollama
pyyaml
beautifulsoup4
lxml
```

---

## 📁 File Structure หลังการย้าย

```
easy-local-rag/
├── localrag.py                    (ปรับปรุง)
├── process_specific_pdf.py        (ปรับปรุง)
├── process_thai_pdf.py            (ปรับปรุง)
├── generate_ground_truth.py       (ปรับปรุง)
├── run_eval.py                    (ปรับปรุง)
├── config.yaml                    (ปรับปรุง)
├── .env.example                   (ใหม่)
├── .env                           (ใหม่ - local only)
├── requirements.txt               (ปรับปรุง)
├── SUPABASE_MIGRATION_PLAN.md    (ไฟล์นี้)
├── SUPABASE_SETUP.md             (ใหม่)
│
├── supabase/
│   ├── __init__.py
│   ├── config.py                  (ใหม่)
│   ├── vector_store.py            (ใหม่)
│   └── db_client.py               (ใหม่)
│
├── scripts/
│   ├── migrate_to_supabase.py    (ใหม่)
│   └── verify_migration.py        (ใหม่)
│
├── tests/
│   ├── test_supabase.py           (ใหม่)
│   ├── test_vector_store.py       (ใหม่)
│   └── test_localrag_supabase.py (ใหม่)
│
├── logs/                          (ใหม่)
│   └── .gitkeep
│
└── original_code/                 (ดังเดิม)
    ├── emailrag2.py
    ├── localrag_no_rewrite.py
    └── upload.py
```

---

## ⏱️ Timeline ประมาณการ

| Phase | งาน | เวลาประมาณการ |
|-------|-----|:-----:|
| 1 | Supabase Setup | 1-2 วัน |
| 2 | Migration Script | 2-3 วัน |
| 3 | Code Updates | 3-4 วัน |
| 4 | Testing & QA | 2-3 วัน |
| 5 | Polish & Docs | 1-2 วัน |
| **รวม** | | **9-14 วัน** |

---

## ⚠️ Considerations & Risks

### Potential Issues:
1. **Dimensionality:** mxbai-embed-large ใช้ 1024 dimensions ✅ (pgvector รองรับ)
2. **Batch Size:** ระวังขนาด batch สำหรับการอัปโหลด (แนะนำ 100-500 items ต่อ batch)
3. **Large Documents:** ต้องแบ่ง chunks ขนาดใหญ่ก่อน embedding
4. **Latency:** Network latency ต่ต่างจากการใช้ local files
5. **Costs:** Supabase มีค่าใช้บริการเมื่อเกิน free tier

### Mitigation:
- ✅ ใช้ batch uploads
- ✅ เพิ่ม caching layer หากต้อง
- ✅ ทดสอบ latency thoroughly
- ✅ Monitor costs อย่างสม่ำเสมอ

---

## 🚀 Success Criteria

✅ Migration สำเร็จถ้า:
- [ ] Supabase project ตั้งค่าแล้วและเชื่อมต่อได้
- [ ] ทุก embeddings อัปโหลดสำเร็จ (จำนวน records ตรงกัน)
- [ ] การค้นหา similarity ผลลัพธ์ที่ถูกต้อง
- [ ] Latency ยอมรับได้ (< 500ms สำหรับแต่ละค้นหา)
- [ ] Code tests ทั้งหมดผ่าน
- [ ] Documentation ครบถ้วนและชัดเจน
- [ ] JSON files สามารถลบออกได้ (optional backup ไว้ก่อน)

---

## 📚 Resources & References

- [Supabase Documentation](https://supabase.com/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Ollama Embeddings](https://ollama.ai/library/mxbai-embed-large)
- [RAG Best Practices](https://python.langchain.com/docs/modules/data_connection/retrievers/vectorstore)

---

## 📝 Notes & Questions

**คำถามที่ต้องตัดสินใจ:**
1. ต้องการเก็บ conversation history ใน Supabase หรือไม่?
2. ต้องการ backup ไฟล์ JSON เดิมหรือไม่? (recommended ตอนแรก)
3. มี email rag feature ที่ต้องย้ายด้วยหรือไม่?
4. ต้องการ real-time updates หรือเพียง batch uploads?
5. ต้องการ Row-level security (RLS) หรือไม่?

**Next Steps:**
1. Confirm สระดับปลายน้ำ (approval)
2. สร้าง Supabase project
3. เริ่มต้น Phase 1
4. ติดตามแต่ละ Phase

---

**อัปเดตล่าสุด:** March 12, 2026
**ผู้จัดทำ:** AI Assistant
**สถานะ:** Ready for Review
