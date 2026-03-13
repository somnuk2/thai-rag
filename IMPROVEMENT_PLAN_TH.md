# 📋 แผนการปรับปรุงความถูกต้อง (Accuracy Improvement Plan)

## 📊 สถานะปัจจุบัน (Current Status)
```
Baseline: 0.6611 (66.11%) - Supabase Mode
          0.6528 (65.28%) - Local Mode

Distribution:
  13% Excellent (0.85-1.00)
  17% Good (0.70-0.85)
  61% Fair (0.50-0.70) ← ปัญหา: มากเกินไป
   9% Poor (<0.50)

Goal: ปรับปรุง → 0.75+ (75%+)
```

---

## 🎯 4 กลยุทธ์การปรับปรุง (4 Improvement Strategies)

### ⭐ **ลำดับความสำคัญ 1: เปลี่ยนโมเดล LLM → OpenThaiGPT**
**ความยากง่าย:** ⚫⚫⚪⚪⚪ (ง่าย)  
**คาดหวังปรับปรุง:** +8-13% (0.66 → 0.72-0.75)  
**เวลาทำการ:** 15-20 นาที  
**ความจำเพิ่ม:** +5-7 GB  

#### ทำไมถึงดีกว่า?
- ✅ แบบจำลองที่ออกแบบเพื่อภาษาไทยเฉพาะ
- ✅ ขนาด 7B > 4B (gemma3) = แม่นยำมากขึ้น
- ✅ เข้าใจบริบทไทยและศัพท์เฉพาะ
- ✅ ฝึกจากข้อมูลภาษาไทย

#### ขั้นตอน:
1. **ติดตั้ง:** `ollama pull openthaigpt1.5-7b-instruct`
2. **แก้ไข config.py:**
   ```python
   OLLAMA_CHAT_MODEL = "openthaigpt1.5-7b-instruct"
   ```
3. **ทดสอบ:** `python test_dual_mode.py` (ทดสอบแบบเดิม)
4. **เปรียบเทียบ:** offline 0.6611 vs. ใหม่

---

### 🟠 **ลำดับความสำคัญ 2: เปลี่ยนโมเดล Embedding → BGE-M3**
**ความยากง่าย:** ⚫⚪⚪⚪⚪ (ง่ายที่สุด)  
**คาดหวังปรับปรุง:** +5-8% (0.66 → 0.69-0.71)  
**เวลาทำการ:** 5 นาที  
**ความจำเพิ่ม:** 0 (เปลี่ยนเท่านั้น)  

#### ทำไมถึงดีกว่า?
- ✅ BGE-M3 = Baidu's multilingual embedding
- ✅ รู้จักภาษาไทยได้ดีกว่า mxbai
- ✅ ใช้เวลาเท่าเดิม (~100ms per query)
- ✅ ไม่ต้องสร้าง embedding ใหม่

#### ขั้นตอน:
1. **แก้ไข config.py:**
   ```python
   EMBEDDING_MODEL = "bge-m3"
   ```
2. **ทดสอบ 10 คำถาม:**
   ```bash
   python -c "
   from test_dual_mode import load_ground_truth, answer_question, create_vector_store, evaluate_similarity
   import statistics
   
   gt = load_ground_truth()[:10]
   scores = [evaluate_similarity(answer_question(create_vector_store(), q['question'])[0], q['answer']) for q in gt]
   print(f'Average (BGE-M3): {statistics.mean(scores):.4f}')
   "
   ```
3. **ถ้าดีขึ้น:** ก็ให้อัพเดท embedding cache

---

### 🟡 **ลำดับความสำคัญ 3: เพิ่ม top_k (Document Retrieval)**
**ความยากง่าย:** ⚫⚪⚪⚪⚪ (ง่ายที่สุด)  
**คาดหวังปรับปรุง:** +3-5% (0.66 → 0.68-0.70)  
**เวลาทำการ:** 2 นาที  
**ความลึกลง:** +50% ช้า (-3-5 วินาที)  

#### ทำไมถึงดีกว่า?
- ✅ เอกสารมากเข้า = ข้อมูลข้างเคียงมากขึ้น
- ✅ LLM มีข้อมูล context มากขึ้น
- ✅ สำหรับภาษาไทยซับซ้อน = ต้องการเอกสารหลายฉบับ

#### ขั้นตอน:
1. **แก้ไข test_dual_mode.py:**
   ```python
   # From: top_k: 3
   # To:   top_k: 7
   
   results = {
       "config": {
           "top_k": 7,  # ← เปลี่ยนจาก 3
       }
   }
   ```
2. **ทดสอบ:** `python test_dual_mode.py`

---

### 🔵 **ลำดับความสำคัญ 4: เพิ่ม LLM Re-ranking (ใหญ่ที่สุด)**
**ความยากง่าย:** ⚫⚫⚫⚪⚪ (ปานกลาง)  
**คาดหวังปรับปรุง:** +8-12% (0.66 → 0.71-0.74)  
**เวลาทำการ:** 30-45 นาที  
**ความลึกลง:** +200-300% ช้า (-6-9 วินาที)  

#### ทำไมถึงดีกว่า?
- ✅ LLM เข้าใจความเกี่ยวข้องได้ดีกว่า vectors
- ✅ กรองเอกสารที่ไม่เกี่ยวข้องออก
- ✅ ได้ context ที่ดีที่สุด

#### ขั้นตอน:
1. **สร้างฟังก์ชัน reranker:**
   ```python
   def rerank_documents(question, documents):
       """Use LLM to re-rank retrieved documents by relevance"""
       from localrag import llm_chat
       
       scores = []
       for doc in documents[:10]:  # Re-rank top 10
           prompt = f"""Question: {question}
Document: {doc['content'][:300]}

Rate relevance 0-100:"""
           response = llm_chat('system', prompt)
           try:
               score = int(response.split()[0])
           except:
               score = 50
           scores.append((doc, score))
       
       # Return top-3 re-ranked
       return sorted(scores, key=lambda x: x[1], reverse=True)[:3]
   ```

2. **ใช้ใน answer_question():**
   ```python
   # From: 
   # results = vector_store.search(embedding, top_k=7)
   
   # To:
   # results = vector_store.search(embedding, top_k=10)
   # results = rerank_documents(question, results)
   ```

3. **ทดสอบ:** `python test_dual_mode.py`

---

## 📅 แผนการดำเนินการแบบแนะนำ (Recommended Action Plan)

### **Phase 1: การทดสอบแบบง่าย** (5 นาที)
```
1. ทดสอบ BGE-M3 embedding (10 คำถาม)
   - If better: อัพเดท config + ดำเนินการต่อ
   - If not better: ข้ามไป Phase 2

ผลคาดหวัง: +5-8% improvement
```

### **Phase 2: อัพเกรด LLM** (20 นาที)
```
1. ติดตั้ง OpenThaiGPT: ollama pull openthaigpt1.5-7b-instruct
2. แก้ไข config.py: OLLAMA_CHAT_MODEL = "openthaigpt1.5-7b-instruct"
3. ทดสอบเต็ม: python test_dual_mode.py (100 คำถาม)

ผลคาดหวัง: +8-13% improvement
```

### **Phase 3: ปรับแต่ง Retrieval** (5 นาที)
```
1. เพิ่ม top_k: 3 → 7
2. ทดสอบ: python test_dual_mode.py

ผลคาดหวัง: +3-5% improvement เพิ่มเติม
```

### **Phase 4: เพิ่ม Re-ranking** (45 นาที, optional)
```
1. เพิ่มฟังก์ชัน reranking
2. ทดสอบและเปรียบเทียบ

ผลคาดหวัง: +8-12% improvement เพิ่มเติม
```

---

## 📈 คาดการณ์ผลลัพธ์ (Expected Results)

| Phase | Action | Before | After | Improvement |
|-------|--------|--------|-------|-------------|
| Baseline | - | **0.6611** | - | - |
| 1 | BGE-M3 | 0.6611 | 0.7011 | +6% |
| 2 | OpenThaiGPT | 0.7011 | 0.7511 | +7% |
| 3 | top_k=7 | 0.7511 | 0.7711 | +3% |
| 4 | Re-ranking | 0.7711 | 0.8011 | +4% |
| **Final** | **All** | **0.6611** | **~0.80** | **+21%** |

---

## ✅ Checklist ก่อนเริ่ม

- [ ] ทำสำเร็จหรือทำความเข้าใจแผนนี้แล้ว
- [ ] มีที่เก็บข้อมูล 5-7 GB สำหรับ OpenThaiGPT (ถ้าใช้)
- [ ] เข้าใจความแตกต่างระหว่าง phases
- [ ] รู้ว่า Phase 3 จะ affect response speed
- [ ] พร้อมทดสอบตามลำดับ

---

## 📧 ติดต่อสำหรับข้อมูล

**Files ที่เกี่ยวข้อง:**
- `config.py` - ปรับสตร์เซตติ้ง
- `test_dual_mode.py` - ทดสอบ
- `analyze_results.py` - วิเคราะห์ผล
- `MODEL_COMPARISON.py` - เปรียบเทียบโมเดล

---

**🚀 พร้อมให้เริ่มต้นเมื่อใดก็ได้ เลือก Phase แล้วแจ้งให้ฉันรู้!**
