"""
Dual-Mode Testing Script
Test both Local (JSON) and Supabase (Remote) modes with the same questions
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import torch
import ollama
from openai import OpenAI
from vector_store_factory import create_vector_store
from config import Config

load_dotenv()

# Configuration
GROUND_TRUTH_PATH = "ground_truth.json"
RESULTS_DIR = "test_results"
OLLAMA_MODEL = "gemma3:4b"  # Use available model (llama3 not found)  # Change to llama2 if llama3 not available
EMBEDDING_MODEL = "mxbai-embed-large"

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# Initialize OpenAI client for Ollama
client = OpenAI(base_url='http://localhost:11434/v1', api_key='gemma3:4b')


def load_ground_truth():
    """Load ground truth questions and answers"""
    if not os.path.exists(GROUND_TRUTH_PATH):
        print(f"❌ {GROUND_TRUTH_PATH} not found!")
        return []
    
    with open(GROUND_TRUTH_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_documents_loaded():
    """Ensure documents are loaded into the vector store before testing"""
    print("\n" + "="*70)
    print("📚 DOCUMENT LOADING CHECK")
    print("="*70)
    
    # Check vault.txt exists
    if not os.path.exists("vault.txt"):
        print("❌ vault.txt not found!")
        print("   Run: python original_code/upload.py")
        return False
    
    vault_size = os.path.getsize("vault.txt")
    if vault_size == 0:
        print("❌ vault.txt is empty!")
        print("   Run: python original_code/upload.py")
        print("   to upload PDF documents")
        return False
    
    print(f"✅ vault.txt found ({vault_size:,} bytes)")
    
    # For Local mode: ensure cache is built
    if not os.path.exists("vault_embeddings_cache.json"):
        print("⚠️  Building embeddings cache for Local mode...")
        try:
            from local_vector_store import LocalVectorStore
            local_store = LocalVectorStore()
            local_store._load_from_cache()
            print(f"✅ Built cache: {local_store.get_total_documents()} documents")
        except Exception as e:
            print(f"⚠️  Cache build failed: {e}")
    else:
        cache_size = os.path.getsize("vault_embeddings_cache.json")
        print(f"✅ Cache exists ({cache_size:,} bytes)")
    
    # For Supabase mode: check if documents exist
    print("\n📤 Loading documents into Supabase if needed...")
    try:
        from supabase_vector_store import SupabaseVectorStore
        from local_vector_store import LocalVectorStore
        
        supabase_store = SupabaseVectorStore()
        doc_count = supabase_store.get_total_documents()
        
        if doc_count == 0:
            print("⚠️  Supabase is empty, loading from vault.txt...")
            
            # Load from local cache
            local_store = LocalVectorStore()
            results = local_store.search([0.0] * 1024, top_k=10000)  # Get all
            
            if results:
                print(f"   Adding {len(results)} documents to Supabase...")
                successful = 0
                for i, doc in enumerate(results):
                    try:
                        # Re-generate embedding for this document
                        embedding = get_query_embedding(doc['content'])
                        if embedding:
                            success = supabase_store.add_document(
                                content=doc['content'],
                                embedding=embedding,
                                metadata=doc.get('metadata', {})
                            )
                            if success:
                                successful += 1
                        if (i + 1) % 5 == 0:
                            print(f"   ✓ Processed {i + 1}/\{len(results)} documents")
                    except Exception as e:
                        pass  # Suppress individual errors to avoid clutter
                
                # Verify load
                final_count = supabase_store.get_total_documents()
                print(f"✅ Loaded {final_count} documents to Supabase")
            else:
                print("⚠️  Could not load documents from local cache")
        else:
            print(f"✅ Supabase already has {doc_count} documents")
    
    except Exception as e:
        print(f"⚠️  Supabase load warning: {e}")
    
    print("✅ Document check complete")
    return True


def get_query_embedding(query):
    """Generate embedding for a query using Ollama"""
    try:
        response = ollama.embeddings(model='mxbai-embed-large', prompt=query)
        return response["embedding"]
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None


def llm_chat(system_prompt, user_message):
    """Send message to LLM and get response"""
    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def retrieve_context(vector_store, query, top_k=3):
    """Retrieve relevant documents from vector store"""
    try:
        embedding = get_query_embedding(query)
        if embedding is None:
            return []
        
        results = vector_store.search(embedding, top_k=top_k)
        return [r["content"] for r in results]
    except Exception as e:
        print(f"Search error: {e}")
        return []


def answer_question(vector_store, question):
    """Generate answer for a question using RAG"""
    # Get context
    context_docs = retrieve_context(vector_store, question, top_k=3)
    context = "\n\n".join(context_docs) if context_docs else "No relevant documents found"
    
    # Generate answer
    system_prompt = """คุณเป็นผู้ช่วยที่มีความรู้ตอบคำถามจากเอกสารที่ให้มา
ตอบคำถามโดยอิงจากบริบทที่ให้มา
ถ้าไม่พบคำตอบในบริบท ให้บอกว่าไม่พบข้อมูล
ตอบเป็นภาษาไทย"""
    
    user_message = f"""บริบท:
{context}

คำถาม: {question}

ตอบคำถาม:"""
    
    answer = llm_chat(system_prompt, user_message)
    return answer, context_docs


def evaluate_similarity(ai_answer, ground_truth_answer):
    """Evaluate similarity between AI answer and ground truth"""
    try:
        # Get embeddings
        ai_embedding = get_query_embedding(ai_answer)
        truth_embedding = get_query_embedding(ground_truth_answer)
        
        if ai_embedding is None or truth_embedding is None:
            return 0.0
        
        # Calculate cosine similarity
        similarity = torch.cosine_similarity(
            torch.tensor(ai_embedding).unsqueeze(0),
            torch.tensor(truth_embedding).unsqueeze(0)
        ).item()
        
        return max(0.0, similarity)  # Ensure non-negative
    except Exception as e:
        print(f"Similarity evaluation error: {e}")
        return 0.0


def test_mode(mode_name, num_questions=5):
    """Test a specific mode (local or supabase)"""
    print(f"\n{'='*70}")
    print(f"🧪 Testing {mode_name.upper()} Mode")
    print(f"{'='*70}")
    
    # Load vector store for this mode
    try:
        vector_store = create_vector_store()
        print(f"✅ Connected to {mode_name} vector store")
        print(f"   Documents in store: {vector_store.get_total_documents()}")
    except Exception as e:
        print(f"❌ Failed to connect to {mode_name}: {e}")
        return None
    
    # Load ground truth
    ground_truth = load_ground_truth()
    if not ground_truth:
        print("❌ No ground truth data found")
        return None
    
    # Test first N questions
    test_data = ground_truth[:min(num_questions, len(ground_truth))]
    results = {
        "mode": mode_name,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model": OLLAMA_MODEL,
            "embedding_model": "mxbai-embed-large",
            "top_k": 3,
        },
        "tests": []
    }
    
    total_similarity = 0
    
    for idx, test_case in enumerate(test_data, 1):
        question = test_case["question"]
        ground_truth_answer = test_case["answer"]
        
        # Show progress less frequently for large test sets
        if len(test_data) > 20:
            if idx % 10 == 1 or idx == len(test_data):
                print(f"\n⏳ Progress: {idx}/{len(test_data)} tests...")
        else:
            print(f"\n📝 Test {idx}/{len(test_data)}")
            print(f"   Question: {question[:60]}...")
        
        try:
            # Generate answer
            ai_answer, context_docs = answer_question(vector_store, question)
            
            # Evaluate similarity
            similarity = evaluate_similarity(ai_answer, ground_truth_answer)
            total_similarity += similarity
            
            # Store result
            result = {
                "test_num": idx,
                "question": question,
                "ground_truth": ground_truth_answer,
                "ai_answer": ai_answer,
                "context_docs_count": len(context_docs),
                "similarity_score": float(similarity)
            }
            results["tests"].append(result)
            
            # Print result only for small test sets
            if len(test_data) <= 20:
                score_bar = "█" * int(similarity * 10) + "░" * (10 - int(similarity * 10))
                print(f"   Score: [{score_bar}] {similarity:.2f}")
                print(f"   Answer: {ai_answer[:80]}...")
            
        except Exception as e:
            results["tests"].append({
                "test_num": idx,
                "question": question,
                "error": str(e)
            })
            if len(test_data) <= 20:
                print(f"   ❌ Error: {e}")
    
    # Calculate average
    avg_similarity = total_similarity / len(test_data) if test_data else 0
    results["average_similarity"] = float(avg_similarity)
    
    print(f"\n{'─'*70}")
    print(f"📊 {mode_name.upper()} Mode Results:")
    print(f"   Tests passed: {len([t for t in results['tests'] if 'error' not in t])}/{len(test_data)}")
    print(f"   Average similarity: {avg_similarity:.2f}/1.00")
    print(f"{'─'*70}")
    
    return results


def run_dual_mode_test():
    """Run tests on both local and supabase modes"""
    print("\n" + "="*70)
    print("🚀 DUAL-MODE RAG SYSTEM TEST")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Model: {OLLAMA_MODEL}")
    print(f"   Embedding: mxbai-embed-large")
    print("="*70)
    
    # Step 1: Ensure documents are loaded
    ensure_documents_loaded()
    
    # Check if documents exist
    if not os.path.exists(GROUND_TRUTH_PATH):
        print(f"\n⚠️  WARNING: {GROUND_TRUTH_PATH} not found!")
        print("   Run: python original_code/upload.py")
        return
    
    test_results = {}
    
    # Get total questions
    ground_truth = load_ground_truth()
    num_all_questions = len(ground_truth)
    print(f"\n📊 Testing with ALL {num_all_questions} ground truth questions")
    
    # Test 1: Current mode
    current_mode = Config.MODE
    print(f"\n✓ Current mode in config: {current_mode}")
    results = test_mode(current_mode, num_questions=num_all_questions)
    if results:
        test_results[current_mode] = results
    
    # Test 2: Switch and test other mode
    other_mode = "local" if current_mode == "supabase" else "supabase"
    print(f"\n🔄 Switching to {other_mode} mode...")
    
    # Switch mode in environment
    os.environ['RAG_MODE'] = other_mode
    # Reload config
    from importlib import reload
    import config as config_module
    reload(config_module)
    
    results = test_mode(other_mode, num_questions=num_all_questions)
    if results:
        test_results[other_mode] = results
    
    # Save results
    results_file = os.path.join(
        RESULTS_DIR,
        f"dual_mode_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Test complete! Results saved to: {results_file}")
    
    # Print comparison
    if len(test_results) == 2:
        print(f"\n{'='*70}")
        print("📊 COMPARISON")
        print(f"{'='*70}")
        for mode in test_results:
            avg = test_results[mode].get('average_similarity', 0)
            print(f"   {mode.upper()}: {avg:.2f}/1.00")
    
    return test_results


if __name__ == "__main__":
    # Check if Ollama is running
    try:
        ollama.list()
    except Exception as e:
        print(f"❌ Ollama is not running!")
        print(f"   Please start Ollama first: ollama serve")
        sys.exit(1)
    
    # Run tests
    results = run_dual_mode_test()
    
    print("\n✅ Testing complete!")
    print(f"   Results saved in: {RESULTS_DIR}/")
