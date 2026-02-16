import ollama
import json
import os
import re

def generate_questions():
    vault_path = "vault.txt"
    output_path = "ground_truth.json"
    model = "gemma3:4b" 
    
    if not os.path.exists(vault_path):
        print("vault.txt not found!")
        return

    with open(vault_path, "r", encoding="utf-8") as f:
        chunks = [line.strip() for line in f.readlines() if line.strip()]

    ground_truth = []
    total_needed = 100
    questions_per_chunk = 5 # 23 chunks * 5 = 115 questions
    
    print(f"Generating questions from {len(chunks)} chunks using {model}...")

    for i, chunk in enumerate(chunks):
        if len(ground_truth) >= total_needed:
            break
            
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        
        prompt = f"""คุณเป็นครูผู้เชี่ยวชาญด้านภาษามือไทย 
จากเนื้อหาที่กำหนดให้ ช่วยสร้างคำถามและคำตอบ (Question & Answer) จำนวน {questions_per_chunk} ข้อ
โดยให้คำถามมีความหลากหลายและครอบคลุมเนื้อหาในส่วนนี้

เนื้อหา:
{chunk}

ให้ตอบกลับเป็น JSON Array รูปแบบดังนี้เท่านั้น (ห้ามมีคำพูดอ้อมค้อมอื่น):
[
  {{"question": "คำถามที่ 1", "answer": "คำตอบที่ 1"}},
  ...
]"""

        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response['message']['content']
            
            # Try to find JSON array in the response using regex if it's not pure JSON
            json_match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                items = json.loads(json_str)
                if isinstance(items, list):
                    ground_truth.extend(items)
                    print(f"Successfully added {len(items)} questions. Current total: {len(ground_truth)}")
            else:
                print(f"Could not find JSON array in response for chunk {i+1}")
                print(f"Raw Response snippet: {content[:200]}...")
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")

    # Trim to exactly 100 if needed
    final_data = ground_truth[:total_needed]
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    print(f"\nDone! Saved {len(final_data)} questions to {output_path}")

if __name__ == "__main__":
    generate_questions()
