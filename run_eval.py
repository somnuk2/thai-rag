import torch
import ollama
import json
import os
from openai import OpenAI

# Configuration
VAULT_PATH = "vault.txt"
CACHE_PATH = "vault_embeddings_cache.json"
GROUND_TRUTH_PATH = "ground_truth.json"
OUTPUT_PATH = "evaluation_results.json"
MODEL = "gemma3:4b"

client = OpenAI(base_url='http://localhost:11434/v1', api_key='llama3')

def get_relevant_context(query, vault_embeddings, vault_content, top_k=3):
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=query)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(top_k, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    return [vault_content[idx].strip() for idx in top_indices]

def evaluate_answer(question, ground_truth, ai_answer):
    prompt = f"""คุณเป็นกรรมการตัดสินคุณภาพของระบบ AI 
เปรียบเทียบคำตอบที่ AI ตอบ กับคำตอบที่ถูกต้อง (Ground Truth) 
แล้วให้คะแนนความถูกต้อง 1 ถึง 5 (5 คือถูกต้องสมบูรณ์, 1 คือผิดทั้งหมดหรือตอบไม่ตรงประเด็น)

คำถาม: {question}
คำตอบที่ถูกต้อง: {ground_truth}
คำตอบจาก AI: {ai_answer}

ให้ตอบเพียงตัวเลขคะแนน 1-5 เท่านั้น ห้ามตอบอย่างอื่น"""
    
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        score_str = response['message']['content'].strip()
        # Extract only the first digit found
        import re
        match = re.search(r'[1-5]', score_str)
        return int(match.group(0)) if match else 0
    except:
        return 0

def run_evaluation():
    if not os.path.exists(VAULT_PATH) or not os.path.exists(GROUND_TRUTH_PATH):
        print("Missing required files (vault.txt or ground_truth.json)")
        return

    print("Loading data...")
    with open(VAULT_PATH, "r", encoding="utf-8") as f:
        vault_content = f.readlines()
    
    vault_embeddings = []
    if os.path.exists(CACHE_PATH):
        print("Loading embeddings from cache...")
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
            vault_embeddings = torch.tensor(cache_data["embeddings"])
    else:
        print("Generating new embeddings...")
        for content in vault_content:
            if content.strip():
                response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
                vault_embeddings.append(response["embedding"])
        vault_embeddings = torch.tensor(vault_embeddings)
        # Save to cache for next time
        print("Saving embeddings to cache...")
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"embeddings": vault_embeddings.tolist()}, f)

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []
    total_score = 0
    count = 0

    print(f"Starting evaluation of {len(questions)} questions...")

    for i, item in enumerate(questions):
        question = item["question"]
        expected = item["answer"]
        
        print(f"[{i+1}/{len(questions)}] Testing: {question[:50]}...")

        # 1. Retrieval
        context = get_relevant_context(question, vault_embeddings, vault_content)
        context_str = "\n".join(context)

        # 2. Generation
        messages = [
            {"role": "system", "content": "คุณเป็นผู้ช่วยที่ตอบคำถามจากข้อมูลที่ให้มาเท่านั้น ตอบเป็นภาษาไทย"},
            {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {question}"}
        ]
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=500
            )
            ai_answer = response.choices[0].message.content.strip()
            
            # 3. Scoring
            score = evaluate_answer(question, expected, ai_answer)
            
            results.append({
                "question": question,
                "ground_truth": expected,
                "ai_answer": ai_answer,
                "context_used": context,
                "score": score
            })
            
            total_score += score
            count += 1
            print(f"   Score: {score}")

        except Exception as e:
            print(f"   Error: {e}")

    # Save results
    report = {
        "average_score": total_score / count if count > 0 else 0,
        "total_questions": count,
        "details": results
    }
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    print(f"\nEvaluation Complete!")
    print(f"Average Accuracy Score: {report['average_score']:.2f} / 5.0")
    print(f"Results saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    run_evaluation()
