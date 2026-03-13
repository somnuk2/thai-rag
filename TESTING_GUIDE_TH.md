# การทดสอบ Local vs Supabase - คู่มือทั้งหมด

**ภาษา:** ภาษาไทย 🇹🇭

---

## 🎯 วิธีการทดสอบ

### 1️⃣ วิธีทดสอบแบบง่ายๆ (Manual Testing)

#### ขั้นที่ 1: เตรียมการ
```bash
# ทำให้แน่ใจว่า Ollama ทำงาน
ollama serve
# (เปิดใน Terminal อื่น)
```

#### ขั้นที่ 2: ทดสอบ Local Mode
```bash
# แก้ไข .env
RAG_MODE=local

# รัน chat
python localrag_dual.py --mode local
```

**ทดสอบด้วยคำถาม:**
```
> คำถามที่ 1: วารสารวิทยาลัยราชสุดา ฉบับที่ 4 ฉบับที่ 1 ได้กล่าวถึงราษฎร์บุญญาอยู่ที่อีเมลใด?
> quit
```

#### ขั้นที่ 3: ทดสอบ Supabase Mode
```bash
# แก้ไข .env
RAG_MODE=supabase

# รัน chat
python localrag_dual.py --mode supabase
```

**ทดสอบด้วยคำถามเดียวกัน:**
```
> คำถามที่ 1: วารสารวิทยาลัยราชสุดา ฉบับที่ 4 ฉบับที่ 1 ได้กล่าวถึงราษฎร์บุญญาอยู่ที่อีเมลใด?
> quit
```

#### ขั้นที่ 4: เปรียบเทียบผลลัพธ์
- คำตอบเหมือนกันหรือไม่?
- ความเร็วต่างกันไหม?
- เอกสารที่ดึงมาเหมือนกันหรือไม่?

---

### 2️⃣ วิธีการทดสอบอัตโนมัติ (Automated Testing)

#### วิธีที่ 1: ใช้ Script ที่สร้างมาใหม่
```bash
# ก่อนอื่น เปิด Ollama ก่อน
ollama serve

# Terminal ใหม่: รันการทดสอบ
python test_dual_mode.py
```

**Output:**
```
======================================================================
🚀 DUAL-MODE RAG SYSTEM TEST
   Time: 2026-03-12 14:30:45
======================================================================

======================================================================
🧪 Testing SUPABASE Mode
======================================================================
✅ Connected to supabase vector store
   Documents in store: 45

📝 Test 1/5
   Question: คำถามที่ 1: วารสารวิทยาลัยราชสุดา...
   Score: [█████░░░░░] 0.87
   Answer: dui2543@hotmail.com...

...

📊 SUPABASE Mode Results:
   Tests passed: 5/5
   Average similarity: 0.85/1.00

...

📊 COMPARISON
======================================================================
   LOCAL: 0.83/1.00
   SUPABASE: 0.85/1.00
```

#### วิธีที่ 2: ใช้ Script ประเมินเดิม (run_eval.py)
```bash
# ทดสอบ Local Mode
python run_eval.py
```

---

## 📊 สิ่งที่ต้องเปรียบเทียบ

| เกณฑ์ | Local | Supabase |
|------|-------|----------|
| **ความเร็ว** | ⚡ เร็ว (local) | 🌐 ช้ากว่า (network) |
| **ความแม่นยำ** | ≈ เท่ากัน | ≈ เท่ากัน |
| **จำนวนเอกสาร** | ถ้าเป็นไฟล์ vault.txt | ในฐานข้อมูล |
| **Embedding ใช้** | PyTorch | pgvector |
| **Search Algorithm** | cosine_similarity | <=> operator |

---

## 🚀 ขั้นตอนการทดสอบทั้งหมด

### Step 1: เตรียมเอกสาร
```bash
# ถ้ายังไม่มีเอกสาร upload PDF ก่อน
python original_code/upload.py
```

### Step 2: เตรียม Ollama
```bash
# Terminal 1
ollama serve
```

### Step 3: ทดสอบ Local
```bash
# Terminal 2
# แก้ .env: RAG_MODE=local
python localrag_dual.py --mode local

# พิมพ์คำถาม 5 ข้อจาก ground_truth.json
> คำถามที่ 1: ...
> คำถามที่ 2: ...
> (... เป็นต้น)

# จดบันทึกผลลัพธ์
# วันที่ ผล ความเร็ว ฯลฯ
```

### Step 4: ทดสอบ Supabase
```bash
# แก้ .env: RAG_MODE=supabase
python localrag_dual.py --mode supabase

# พิมพ์คำถามเดียวกัน 5 ข้อ
> คำถามที่ 1: ...
> คำถามที่ 2: ...
> (... เป็นต้น)

# จดบันทึกผลลัพธ์
```

### Step 5: เปรียบเทียบผลลัพธ์
```
ประเด็น:
1. ความถูกต้องของคำตอบ (เหมือนกันหรือดีกว่า?)
2. ความเร็ว (Local เร็วกว่า Supabase ไหม?)
3. Relevance ของเอกสารที่ดึงมา (เหมือนกันไหม?)
4. Error rate (ข้อมูลหายไหม?)
```

---

## 📈 การรันทดสอบอัตโนมัติแบบเต็ม

### Option A: ทดสอบเฉพาะโหมดปัจจุบัน
```bash
python test_dual_mode.py
```

### Option B: ทดสอบ Local เท่านั้น
```bash
# แก้ .env
RAG_MODE=local

# จากนั้น
python run_eval.py
```

### Option C: ทดสอบ Supabase เท่านั้น
```bash
# แก้ .env
RAG_MODE=supabase

# ต้องสร้าง evaluation script สำหรับ Supabase ด้วย
# (หรือใช้ test_dual_mode.py)
```

---

## ✅ สิ่งที่ต้องตรวจสอบ

### Local Mode Checklist
- [ ] vault.txt มีเอกสาร
- [ ] vault_embeddings_cache.json ถูกสร้าง
- [ ] Ollama ทำงาน
- [ ] Chat ตอบคำถาม
- [ ] ความเร็วปกติ (< 2 วินาที)

### Supabase Mode Checklist
- [ ] Database tables ถูกสร้าง
- [ ] pgvector ติดตั้งแล้ว
- [ ] Supabase API key ถูกต้อง
- [ ] Chat ตอบคำถาม
- [ ] ความเร็วปกติ (< 5 วินาที, network latency)

---

## 🔢 ผลลัพธ์ที่คาดหวัง

```
Local Mode:
  ✅ Documents retrieved: 3-5
  ✅ Response time: 1-2 seconds
  ✅ Similarity score: 0.70-0.90
  ✅ Answers: Relevant and accurate

Supabase Mode:
  ✅ Documents retrieved: 3-5 (from database)
  ✅ Response time: 2-4 seconds (network)
  ✅ Similarity score: 0.70-0.90 (เหมือนกับ Local)
  ✅ Answers: Relevant and accurate (เหมือนกับ Local)
```

---

## 🛠️ Troubleshooting

### ปัญหา: Local ทำงาน แต่ Supabase ไม่ทำงาน
```bash
# ตรวจสอบ
python -c "from supabase_vector_store import SupabaseVectorStore; s = SupabaseVectorStore(); s.health_check()"

# ต้อง reconnect ฐานข้อมูล
# หรือตรวจสอบ API key
```

### ปัญหา: ผลลัพธ์ต่างกัน
- อาจเป็นเพราะ Ollama version ต่างกัน
- หรือ embeddings model ต่าง
- ลองรัน `ollama pull mxbai-embed-large` ใหม่

### ปัญหา: การทดสอบเร็วไป Supabase
- เป็นปกติเพราะ network latency
- Supabase ช้าประมาณ 2-3 วินาที

---

## 📚 ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | วัตถุประสงค์ |
|-----|----------|
| `ground_truth.json` | คำถามและคำตอบที่ถูกต้อง |
| `test_dual_mode.py` | **🆕 Script ทดสอบ Local vs Supabase** |
| `run_eval.py` | ประเมินผลลัพธ์ (Local เท่านั้น) |
| `localrar_dual.py` | Chat application (ทดสอบด้วยตนเอง) |
| `evaluation_results.json` | ผลการประเมินที่บันทึก |

---

## 🎉 สรุป

### ขั้นที่ 1: ทดสอบแบบง่าย (Manual)
```bash
# Local
python localrag_dual.py --mode local

# Supabase
python localrag_dual.py --mode supabase

# พิมพ์คำถามเดียวกันทั้งสองโหมด
```

### ขั้นที่ 2: ทดสอบอัตโนมัติ (Automated)
```bash
# รันการทดสอบอัตโนมัติทั้งสองโหมด
python test_dual_mode.py
```

### ขั้นที่ 3: เปรียบเทียบผลลัพธ์
```
ดูไฟล์ test_results/dual_mode_test_*.json
```

---

**ทดสอบได้เลย! 🚀**
