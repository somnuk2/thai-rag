# Supabase Migration - Quick Reference & Checklist

---

## 📋 Quick Links

| เอกสาร | คำอธิบาย |
|------|---------|
| [SUPABASE_MIGRATION_PLAN.md](SUPABASE_MIGRATION_PLAN.md) | แผนการโดยรวม (Overview) |
| [SUPABASE_SETUP.md](SUPABASE_SETUP.md) | คู่มือการตั้งค่า Supabase (Phase 1) |
| [SUPABASE_MIGRATION_PHASE2.md](SUPABASE_MIGRATION_PHASE2.md) | Migration Script Implementation (Phase 2) |

---

## ✅ Pre-Migration Checklist

### ตรวจสอบที่ต้องทำก่อนเริ่ม:

- [ ] มีไฟล์ `vault_embeddings.json` ที่ถูกต้อง
- [ ] มีไฟล์ `vault.txt` ที่ถูกต้อง
- [ ] มีไฟล์ `requirements.txt` ที่อัปเดต (รวม supabase-py)
- [ ] ติดตั้ง Python packages: `pip install -r requirements.txt`
- [ ] มี `.env` file ที่มี Supabase credentials
- [ ] ทดสอบการเชื่อมต่อกับ Supabase ได้

### Backup ข้อมูล:

```bash
# สร้าง backup folder
mkdir backups

# Backup JSON files
cp vault_embeddings.json backups/vault_embeddings.json.backup
cp vault.txt backups/vault.txt.backup
```

---

## 🚀 Phase 1: Setup Supabase

### Timeline: 1-2 วัน

**Activities:**

- [ ] สร้าง Supabase account
- [ ] สร้าง Project ใหม่
- [ ] บันทึก URL และ API Keys
- [ ] Enable pgvector extension
- [ ] สร้าง Tables (documents, embeddings, conversation_history)
- [ ] สร้าง Vector Index
- [ ] สร้าง Functions (match_embeddings)
- [ ] ตั้งค่า .env file
- [ ] ทดสอบการเชื่อมต่อ

**Verification:**
```bash
python -m supabase.config  # ต้องเห็น "✅ Supabase connection successful!"
```

**Next:** เมื่อเห็น success message ก็พร้อมสำหรับ Phase 2

---

## 🚀 Phase 2: Migration Script

### Timeline: 2-3 วัน

**Activities:**

- [ ] สร้าง `supabase/` folder
- [ ] สร้าง `supabase/config.py`
- [ ] สร้าง `supabase/vector_store.py`
- [ ] สร้าง `scripts/migrate_to_supabase.py`
- [ ] สร้าง `scripts/verify_migration.py`
- [ ] ทำการ dry-run migration
- [ ] ตรวจสอบ logs
- [ ] รัน migration จริง
- [ ] ตรวจสอบผลลัพธ์

**ขั้นตอนการรัน:**

```bash
# Step 1: Dry Run (ไม่มีการเปลี่ยนแปลง)
python scripts/migrate_to_supabase.py --dry-run

# Step 2: Migration จริง
python scripts/migrate_to_supabase.py --input vault_embeddings.json --batch-size 100

# Step 3: Verification
python scripts/verify_migration.py --compare vault_embeddings.json
```

**Success Criteria:**
- ✅ ไม่มี error ในขั้นตอน migration
- ✅ Count ของ embeddings ตรงกับต้นฉบับ
- ✅ Vector search ทำงานได้

**Next:** เมื่อ verification passed ก็พร้อมสำหรับ Phase 3

---

## 🚀 Phase 3: Update Application Code

### Timeline: 3-4 วัน

**Activities:**

- [ ] ปรับปรุง `localrag.py`
- [ ] ปรับปรุง `process_specific_pdf.py`
- [ ] ปรับปรุง `process_thai_pdf.py`
- [ ] ปรับปรุง `generate_ground_truth.py`
- [ ] สร้าง Unit Tests
- [ ] สร้าง Integration Tests
- [ ] ทดสอบ Application Flow ทั้งหมด
- [ ] ทดสอบ Query Rewriting Feature
- [ ] ทดสอบ Vector Search

**Key Changes:**

```python
# ในไฟล์ localrag.py

# ก่อน:
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    # ใช้ torch.cosine_similarity กับ torch tensors
    pass

# หลัง:
def get_relevant_context(rewritten_input, vector_store, top_k=3):
    # ใช้ Supabase pgvector
    input_embedding = ollama.embeddings(...)["embedding"]
    results = vector_store.search_similar(input_embedding, top_k)
    return results
```

---

## 🚀 Phase 4: Testing & QA

### Timeline: 2-3 วัน

**Activities:**

- [ ] Unit Tests - Vector Store
- [ ] Unit Tests - Database Operations
- [ ] Integration Tests - Full RAG Flow
- [ ] Performance Tests
- [ ] Stress Tests (large number of embeddings)
- [ ] Data Validation

**Test Commands:**
```bash
# Run unit tests
pytest tests/test_supabase.py -v

# Run integration tests
pytest tests/test_localrag_supabase.py -v

# Performance test
python tests/performance_test.py
```

---

## 🚀 Phase 5: Documentation & Cleanup

### Timeline: 1-2 วัน

**Activities:**

- [ ] อัปเดต README.md
- [ ] สร้าง `.env.example`
- [ ] สร้าง `DEPLOYMENT.md`
- [ ] ปรับปรุง comments ในโค้ด
- [ ] สร้าง troubleshooting guide
- [ ] ลบหรือ archive ไฟล์ JSON เก่า (หลังจากยืนยันว่า Backup ปลอดภัย)
- [ ] อัปเดต `requirements.txt`

**Files to Update:**
```
README.md          - Add Supabase setup instructions
requirements.txt   - Add supabase-py
.gitignore         - Add .env, logs/, *.backup
config.yaml        - (optional) Add Supabase config options
```

---

## 📊 Current Status

| Phase | Task | Status | Notes |
|-------|------|--------|-------|
| 0 | Planning & Documentation | ✅ DONE | 3 คู่มือ + checklist |
| 1 | Supabase Setup | ⏳ PENDING | Ready to start |
| 2 | Migration Script | ⏳ PENDING | Code samples in guide |
| 3 | Update Code | ⏳ PENDING | Depends on Phase 2 |
| 4 | Testing & QA | ⏳ PENDING | Depends on Phase 3 |
| 5 | Documentation | ⏳ PENDING | Depends on Phase 4 |

---

## 🌐 Useful Commands Reference

### Supabase

```bash
# Test connection
python -m supabase.config

# Run migration (dry-run first!)
python scripts/migrate_to_supabase.py --dry-run
python scripts/migrate_to_supabase.py

# Verify
python scripts/verify_migration.py --compare vault_embeddings.json
```

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Run tests
pytest tests/ -v

# Lint code
pylint supabase/ scripts/ localrag.py
```

### Database Management

```bash
# Backup Supabase database
# Go to Supabase Dashboard > Settings > Backups

# Clear all embeddings (use with caution!)
# In Supabase SQL Editor:
# DELETE FROM embeddings;
# DELETE FROM documents;
```

---

## 💾 File Structure After Migration

```
easy-local-rag/
│
├── Core Files
├── localrag.py                    ✅ (UPDATED)
├── process_specific_pdf.py        ✅ (UPDATED)
├── process_thai_pdf.py            ✅ (UPDATED)
├── generate_ground_truth.py       ✅ (UPDATED)
├── run_eval.py                    ✅ (UPDATED)
├── config.yaml                    ✅ (UPDATED)
├── requirements.txt               ✅ (UPDATED)
│
├── Configuration
├── .env                           ✅ (NEW - local only)
├── .env.example                   ✅ (NEW - commit to repo)
│
├── Supabase / Database
├── supabase/
│   ├── __init__.py               ✅ (NEW)
│   ├── config.py                 ✅ (NEW)
│   └── vector_store.py           ✅ (NEW)
│
├── Migration Scripts
├── scripts/
│   ├── migrate_to_supabase.py    ✅ (NEW)
│   └── verify_migration.py        ✅ (NEW)
│
├── Tests
├── tests/
│   ├── test_supabase.py           ✅ (NEW)
│   ├── test_vector_store.py       ✅ (NEW)
│   └── test_localrag_supabase.py  ✅ (NEW)
│
├── Logs
├── logs/
│   └── .gitkeep                   ✅ (NEW)
│
├── Documentation
├── SUPABASE_MIGRATION_PLAN.md    ✅ (NEW)
├── SUPABASE_SETUP.md             ✅ (NEW)
├── SUPABASE_MIGRATION_PHASE2.md  ✅ (NEW)
├── SUPABASE_QUICK_REFERENCE.md   ✅ (NEW - this file)
├── DEPLOYMENT.md                  ⏳ (TODO)
├── README.md                      ✅ (UPDATED)
│
├── Backup / Legacy
├── backups/
│   ├── vault_embeddings.json.backup
│   └── vault.txt.backup
│
└── Original Code (Keep for reference)
└── original_code/
    ├── emailrag2.py
    ├── localrag_no_rewrite.py
    └── upload.py
```

---

## 🔗 External Resources

### Supabase
- [Supabase Docs](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

### RAG / Vector Search
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [LangChain Vector Store](https://python.langchain.com/docs/modules/data_connection/vectorstores/)
- [Similarity Search Best Practices](https://milvus.io/docs/glossary.md)

### Tools & Libraries
- [Ollama Embeddings](https://ollama.ai/)
- [PyTorch Similarity](https://pytorch.org/docs/stable/generated/torch.nn.CosineSimilarity.html)

---

## 🆘 Support & Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Unable to connect to Supabase | Check `.env` file, verify URL and keys |
| Vector dimension mismatch | Ensure `VECTOR(1024)` in schema matches embedding size |
| Batch upload timeout | Reduce batch size (try 50 instead of 100) |
| Query returns no results | Check embedding similarity threshold, test with lower value |
| Performance degradation | Consider adding more indexes, optimize query patterns |

### Getting Help

1. Check the detailed guides: `SUPABASE_SETUP.md`, `SUPABASE_MIGRATION_PHASE2.md`
2. Review logs in `logs/` folder
3. Verify each step carefully
4. Test with `--dry-run` flag first

---

## 📝 Notes & Decisions

**Questions Answered Earlier:**
- ✅ Store conversation history in Supabase? 
  - ยืนยัน: ตาราง `conversation_history` ได้สร้างไว้แล้ว
  
- ✅ Keep original JSON files as backup?
  - แนะนำ: ใช่ ในโฟลเดอร์ `backups/`
  
- ✅ Email RAG feature needs migration?
  - ต้องประเมิน: ดู `emailrag2.py` ในขั้น Phase 3
  
- ✅ Real-time updates or batch?
  - ใช้: Batch uploads (scaling ได้ดี, ราคาถูก)

---

## 🎯 Success Metrics

✅ Migration สำเร็จเมื่อ:

- [ ] ทั้งหมด embeddings อัปโหลดสำเร็จ
- [ ] Count ของ records ตรงกับต้นฉบับ
- [ ] Query similarity search ทำงาน
- [ ] Application code ทำงานเหมือนเดิม (หรือดีกว่า)
- [ ] Tests ทั้งหมดผ่าน
- [ ] Latency ยอมรับได้ (< 500ms per search)
- [ ] Documentation ครบถ้วน

---

**Last Updated:** March 12, 2026  
**Status:** Ready for Implementation  
**Next Step:** Start Phase 1 (Supabase Setup)
