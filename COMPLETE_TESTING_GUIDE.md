# ทดสอบระบบ Local vs Supabase - คู่มือสรุปแบบสมบูรณ์

**ภาษา:** ไทย-English

---

## 🎯 วิธีทดสอบ 3 แบบ

### 1️⃣ **Manual Testing** (ทดสอบด้วยตนเอง)

ง่ายที่สุด เหมาะสำหรับการทดสอบเร็วๆ

```bash
# Terminal 1: เปิด Ollama
ollama serve

# Terminal 2: ทดสอบ Local
RAG_MODE=local
python localrag_dual.py --mode local
>>> What is in the documents?
>>> quit

# Terminal 2: ทดสอบ Supabase
RAG_MODE=supabase
python localrag_dual.py --mode supabase
>>> What is in the documents?
>>> quit
```

**ประโยชน์:**
- ✅ เร็วที่สุด
- ✅ ดูผลลัพธ์ตรงๆ
- ✅ แค่ 5 นาที

**ข้อเสีย:**
- ⚠️ ต้องทดสอบด้วยตนเอง
- ⚠️ ไม่มีบันทึกผลลัพธ์

---

### 2️⃣ **Automated Testing** (ทดสอบอัตโนมัติ)

ใช้ script ที่สร้างมาใหม่

```bash
# Terminal 1: เปิด Ollama
ollama serve

# Terminal 2: รันการทดสอบอัตโนมัติ
python test_dual_mode.py
```

**Output:**
```
======================================================================
🚀 DUAL-MODE RAG SYSTEM TEST
======================================================================

🧪 Testing SUPABASE Mode
✅ Connected to supabase vector store

📝 Test 1/5
   Question: What is in document 1?
   Score: [█████░░░░░] 0.87
   
...

📊 COMPARISON
   LOCAL: 0.83/1.00
   SUPABASE: 0.85/1.00

✅ Test complete! Results saved to: test_results/dual_mode_test_20260312_143045.json
```

**ประโยชน์:**
- ✅ ทดสอบอัตโนมัติ
- ✅ เปรียบเทียบ Local vs Supabase
- ✅ บันทึกผลลัพธ์อย่างละเอียด
- ✅ 5 คำถามต่อการทดสอบ

**ข้อเสีย:**
- ⚠️ ต้องมีเอกสารและ ground truth

---

### 3️⃣ **Evaluation Mode** (ประเมินคุณภาพ)

ใช้ script ประเมินเดิม

```bash
# Terminal 1: เปิด Ollama
ollama serve

# Terminal 2: ประเมินคุณภาพคำตอบ
python run_eval.py
```

**Output:**
```
Evaluation Results:
Question 1: Score 5/5 (ถูกต้องสมบูรณ์)
Question 2: Score 4/5 (ดี)
Question 3: Score 3/5 (พอสมควร)

Average Score: 4.0/5.0
```

**ประโยชน์:**
- ✅ ประเมินคุณภาพอัตโนมัติ
- ✅ ใช้ LLM เพื่อประเมิน
- ✅ ให้คะแนน 1-5

---

## 📊 เปรียบเทียบวิธีการทดสอบ

| วิธี | เวลา | ความง่าย | รายละเอียด | ผลลัพธ์ |
|-----|------|---------|-----------|--------|
| Manual | 5 นาที | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❌ |
| Automated | 10 นาที | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |
| Evaluation | 15 นาที | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ |

---

## 🚀 ขั้นตอนการทดสอบอัตโนมัติแบบเต็ม

### ก่อนการทดสอบ

```bash
# 1. ตรวจสอบเอกสาร
ls -la vault.txt                      # ต้องมี
ls -la ground_truth.json              # ต้องมี

# 2. เตรียมการเชื่อมต่อ
python -c "from config import Config; Config.print_config()"
# ต้องแสดง: Mode: supabase และ all settings

# 3. ตรวจสอบ Ollama
ollama list
# ต้องแสดง: llama3, mxbai-embed-large
```

### ขั้นที่ 1: เปิด Ollama (Terminal 1)
```bash
ollama serve
```

### ขั้นที่ 2: รันการทดสอบ (Terminal 2)
```bash
python test_dual_mode.py
```

### ขั้นที่ 3: ตรวจสอบผลลัพธ์
```bash
# ดูไฟล์ JSON ที่สร้าง
cat test_results/dual_mode_test_*.json

# ใช้ Python เพื่อดูผลลัพธ์แบบสวยงาม
python << 'EOF'
import json
import glob

# โหลดไฟล์ล่าสุด
files = glob.glob('test_results/dual_mode_test_*.json')
latest = max(files)

with open(latest) as f:
    results = json.load(f)

for mode in results:
    avg = results[mode].get('average_similarity', 0)
    tests = results[mode].get('tests', [])
    passed = len([t for t in tests if 'error' not in t])
    
    print(f"{mode.upper()}:")
    print(f"  Similarity: {avg:.2f}/1.00")
    print(f"  Passed: {passed}/{len(tests)}")
EOF
```

---

## 📋 สิ่งที่ต้องตรวจสอบ

### Similarity Score (0.00 - 1.00)
```
>= 0.80  ✅ Excellent  (ดีมาก)
0.70-0.79 ✅ Good     (ดี)
0.60-0.69 ⚠️  Fair    (พอสมควร)
< 0.60   ❌ Poor    (ไม่ดี)
```

### ผลลัพธ์ที่คาดหวัง
```
Local Mode:
  ✅ Similarity: 0.70-0.90
  ✅ Response time: 1-2 seconds
  ✅ Documents retrieved: 3-5

Supabase Mode:
  ✅ Similarity: 0.70-0.90 (เหมือน Local)
  ✅ Response time: 2-4 seconds (ช้ากว่า Local)
  ✅ Documents retrieved: 3-5 (เหมือน Local)

ความต่างทั่วไป:
  ≈ คุณภาพเท่ากัน
  ≈ Local เร็วกว่า Supabase 2-3 วินาที
  ≈ ผลลัพธ์เดียวกัน 90% ของเวลา
```

---

## 🔍 วิธีวิเคราะห์ผลลัพธ์

### 1. เปรียบเทียบความเร็ว
```
Local:    1-2 วินาที ⚡
Supabase: 2-4 วินาที 🌐

ผลต่าง: 1-2 วินาที (เนื่องจาก network)
```

### 2. เปรียบเทียบความถูกต้อง
```
- ถ้า similarity score เหมือนกัน → ทั้งสองโหมดดีเท่ากัน ✅
- ถ้า similarity score ต่างกัน → อาจมีปัญหา ❌
```

### 3. เปรียบเทียบเอกสารที่ดึงมา
```
- ดูว่าเอกสารที่ดึงมาเหมือนกันหรือไม่
- ถ้าเหมือนกัน → embedding และ search ตรงกัน ✅
- ถ้าต่างกัน → อาจมีปัญหาในการ index ❌
```

---

## 📊 ตัวอย่างผลลัพธ์

### ตัวอย่าง 1: ผลดี (สำเร็จ)
```json
{
  "local": {
    "average_similarity": 0.87,
    "tests": 5,
    "passed": 5
  },
  "supabase": {
    "average_similarity": 0.85,
    "tests": 5,
    "passed": 5
  }
}

วิเคราะห์: ✅
- ทั้งสองโหมดทำงานได้ดี
- ความต่างเล็กน้อย (0.02) เป็นปกติ
- สามารถใช้โหมดใดก็ได้
```

### ตัวอย่าง 2: ผลมีปัญหา
```json
{
  "local": {
    "average_similarity": 0.88,
    "tests": 5,
    "passed": 5
  },
  "supabase": {
    "average_similarity": 0.40,
    "tests": 5,
    "passed": 3
  }
}

วิเคราะห์: ⚠️
- Supabase มีปัญหา
- ตรวจสอบ:
  1. Database tables ถูก?
  2. API key ถูก?
  3. pgvector ติดตั้ง?
  4. Documents หลายไปหรือไม่?
```

---

## 🛠️ Troubleshooting

### ปัญหา: Documents = 0
```bash
# ตรวจสอบ
ls -la vault.txt
# ถ้าว่าง → Upload เอกสารก่อน
python original_code/upload.py

# Local: ตรวจสอบ cache
ls -la vault_embeddings_cache.json

# Supabase: ตรวจสอบ database
SELECT COUNT(*) FROM public.embeddings;
```

### ปัญหา: Similarity score ต่ำ
```bash
# ตรวจสอบ embedding
python -c "
import ollama
text = 'test'
result = ollama.embeddings(model='mxbai-embed-large', prompt=text)
print(f'Embedding length: {len(result[\"embedding\"])}')
"
# ต้อง = 1024
```

### ปัญหา: Supabase ช้า
```
เป็นปกติ! 🌐
- Network latency 2-3 วินาที
- Database query อีก 1-2 วินาที
- รวม: 3-5 วินาที
```

---

## 📚 ไฟล์ที่ใช้ในการทดสอบ

| ไฟล์ | ที่ตั้ง | วัตถุประสงค์ |
|-----|-------|----------|
| `test_dual_mode.py` | 📍 `./` | 🆕 **ทดสอบ Local vs Supabase** |
| `run_eval.py` | 📍 `./` | ประเมินคุณภาพ (Local เท่านั้น) |
| `ground_truth.json` | 📍 `./` | คำถามและคำตอบที่ถูกต้อง |
| `vault.txt` | 📍 `./` | เอกสารที่ upload |
| `vault_embeddings_cache.json` | 📍 `./` | Cache embedding (Local) |
| `.env` | 📍 `./` | Configuration (RAG_MODE=supabase) |
| `test_results/` | 📍 `./test_results/` | 📂 ผลการทดสอบ |

---

## ✅ Checklist การทดสอบ

### ก่อนการทดสอบ
- [ ] Ollama ติดตั้ง (`ollama --version`)
- [ ] Models ดาวน์โหลด (`ollama list`)
- [ ] เอกสาร vault.txt มี
- [ ] Ground truth JSON มี
- [ ] .env ตั้ง RAG_MODE=supabase
- [ ] Supabase table สร้าง

### ระหว่างการทดสอบ
- [ ] Terminal 1: `ollama serve` ทำงาน
- [ ] Terminal 2: `python test_dual_mode.py` รัน
- [ ] ไม่มี error ขาดหาย
- [ ] Response ตรงทั้งสองโหมด

### หลังการทดสอบ
- [ ] ผลลัพธ์บันทึกใน `test_results/`
- [ ] JSON ถูกสร้าง
- [ ] Similarity scores ดู
- [ ] เปรียบเทียบผล

---

## 🎉 สรุป

### ขั้นตอนโดยสรุป (5 นาที)

```bash
# 1. เปิด Ollama
ollama serve

# 2. รันการทดสอบ (Terminal อื่น)
python test_dual_mode.py

# 3. ตรวจสอบผลลัพธ์
cat test_results/dual_mode_test_*.json
```

### ผลลัพธ์ที่คาดหวัง

```
✅ Local: similarity 0.70-0.90, response 1-2s
✅ Supabase: similarity 0.70-0.90, response 2-4s
✅ ทั้งสองโหมดตอบคำถามได้ถูกต้อง
```

---

**ทดสอบได้เลยตอนนี้! 🚀**
