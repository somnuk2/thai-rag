#!/usr/bin/env python
"""
Accuracy Improvement Strategies
Four approaches to boost similarity scores from ~0.66 to 0.75+
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    4 STRATEGIES TO IMPROVE ACCURACY                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Current Status: 66% average accuracy, 61% in Fair range
Goal: Move 61% Fair → Better ratings (target 75%+ average)

═══════════════════════════════════════════════════════════════════════════════

🟢 STRATEGY 1: Increase top_k (Document Retrieval)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Current: top_k=3 (retrieve 3 documents)                                    │
│ Improvement: top_k=5-7 (retrieve more context)                             │
│                                                                             │
│ Expected Impact: +3-5% accuracy improvement                                │
│ Trade-off: +50% slower (-3-5 seconds per answer)                           │
│                                                                             │
│ Why it works:                                                              │
│ - More context = better LLM understanding                                  │
│ - Thai complex topics need multiple perspectives                           │
│ - Reduces "no data found" errors                                           │
│                                                                             │
│ Implementation: Change in test_dual_mode.py                                │
└─────────────────────────────────────────────────────────────────────────────┘

BEFORE (test_dual_mode.py):
    results = {
        "config": {
            "top_k": 3,  # ← Current
        }
    }
    
AFTER:
    results = {
        "config": {
            "top_k": 7,  # ← Increased
        }
    }

Files to modify:
  - test_dual_mode.py: line 248, change top_k: 3 → 7
  - answer_question() function: top_k parameter

═══════════════════════════════════════════════════════════════════════════════

🟠 STRATEGY 2: Use Better Embedding Model
┌─────────────────────────────────────────────────────────────────────────────┐
│ Current: mxbai-embed-large (1024D, good for English)                       │
│ Alternatives (all installed in Ollama):                                    │
│   - bge-m3 (Baidu) - Best for multilingual + Thai                         │
│   - gte-large (Alibaba) - Strong Thai support                             │
│   - gte-base (Alibaba) - Faster, still good                               │
│                                                                             │
│ Expected Impact: +5-8% accuracy (best improvement)                         │
│ Trade-off: +100ms slower per embedding (still fast)                        │
│                                                                             │
│ Why it works:                                                              │
│ - BGE-M3 trained on multilingual corpora                                   │
│ - Better Thai language understanding                                       │
│ - Stronger semantic matching                                               │
│                                                                             │
│ Test command (before full test):                                           │
│   1. Try BGE-M3 on sample 5 questions                                      │
│   2. If better, run full 100-question test                                 │
│   3. Compare metrics                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

To test different embeddings:
    
CURRENT (config.py):
    EMBEDDING_MODEL = "mxbai-embed-large"
    
TRY ALTERNATIVE (config.py):
    EMBEDDING_MODEL = "bge-m3"  # Better for Thai
    
Then run quick 10-question test:
    python -c "
    from test_dual_mode import test_mode, create_vector_store
    from config import Config
    test_mode('supabase', num_questions=10)
    "

═══════════════════════════════════════════════════════════════════════════════

🟡 STRATEGY 3: Add LLM Re-ranking (Highest Impact)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Current: Simple vector similarity + LLM generation                          │
│ Improvement: Add reranker step before LLM generation                        │
│                                                                             │
│ Process:                                                                   │
│   1. Retrieve top_k=10 documents (via vector search)                       │
│   2. Use LLM to re-rank: "Score 0-100 relevance to question"              │
│   3. Use top-3 re-ranked documents for answer                              │
│                                                                             │
│ Expected Impact: +8-12% accuracy improvement (BEST)                        │
│ Trade-off: +200-300% slower (-6-9 seconds per answer)                      │
│            Worth it for production                                         │
│                                                                             │
│ Why it works:                                                              │
│ - LLM understands semantic relevance better than vectors                   │
│ - Can reason about Thai context                                            │
│ - Filters irrelevant but similar documents                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Implementation Pattern:
    
    def rerank_documents(question, documents):
        '''Use LLM to re-rank retrieved documents'''
        from localrag import llm_chat
        
        scores = []
        for doc in documents:
            prompt = f'''Question: {question}
Document: {doc['content'][:500]}
Score the relevance 0-100: '''
            response = llm_chat('system', prompt)
            score = extract_score(response)  # Parse "85" from response
            scores.append((doc, score))
        
        # Return top-3 re-ranked
        return sorted(scores, key=lambda x: x[1], reverse=True)[:3]

═══════════════════════════════════════════════════════════════════════════════

🔵 STRATEGY 4: Better Document Chunking (For Thai)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Current: Paragraph-based chunking                                          │
│ Improvement: Sentence-based + Thai language awareness                      │
│                                                                             │
│ Why Thai is different:                                                     │
│ - No spaces between words (need word tokenizer)                            │
│ - Complex compound meanings (need semantic chunking)                       │
│ - Short sentences more relevant than long paragraphs                       │
│                                                                             │
│ Expected Impact: +2-4% accuracy                                            │
│ Trade-off: Need to re-process vault.txt & rebuild embeddings               │
│                                                                             │
│ How to implement:                                                          │
│   pip install pythainlp   # Thai tokenizer                                 │
│   Then rebuild vault_embeddings_cache.json                                 │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

📊 RECOMMENDED APPROACH (Step by Step)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Priority 1 (QUICK - 5 min, +5-8%): Switch to BGE-M3 embedding              │
│   - Easy to test: just change config.py                                    │
│   - High impact: +5-8% improvement                                         │
│   - No code changes needed                                                 │
│                                                                             │
│ Priority 2 (MEDIUM - 20 min, +8-12%): Add LLM re-ranking                   │
│   - More complex: requires new function                                    │
│   - Highest impact: +8-12% improvement                                     │
│   - Worth the effort for production                                        │
│                                                                             │
│ Priority 3 (EASY - 2 min, +3-5%): Increase top_k=7                         │
│   - Just change one parameter                                              │
│   - Decent improvement: +3-5%                                              │
│   - Minimal code change                                                    │
│                                                                             │
│ Priority 4 (HARD - 1 hour, +2-4%): Better chunking                         │
│   - Most complex: needs Thai tokenizer                                     │
│   - Small improvement: +2-4%                                               │
│   - Only if others not enough                                              │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

🎯 QUICK TEST - BGE-M3 EMBEDDING (START HERE!)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Quickest way to test: Just 3 steps!                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Verify BGE-M3 is installed
    CMD: python -c "from ollama import Client; c = Client(); [print(m['name']) for m in c.list()['models'] if 'bge' in m['name'].lower()]"
    Expected: bge-m3

Step 2: Update config.py
    Change: EMBEDDING_MODEL = "mxbai-embed-large"
    To:     EMBEDDING_MODEL = "bge-m3"

Step 3: Run 10-question test
    CMD: python -c "
from test_dual_mode import load_ground_truth, answer_question, create_vector_store, get_query_embedding, evaluate_similarity
import statistics

ground_truth = load_ground_truth()[:10]
scores = []

for q in ground_truth:
    question = q['question']
    expected = q['answer']
    vector_store = create_vector_store()
    ai_answer, _ = answer_question(vector_store, question)
    sim = evaluate_similarity(ai_answer, expected)
    scores.append(sim)
    print(f'Q: {question[:50]}... → Score: {sim:.2f}')

print(f'\\nAverage (BGE-M3): {statistics.mean(scores):.4f}')
"

═══════════════════════════════════════════════════════════════════════════════

📈 EXPECTED IMPROVEMENTS

Current Baseline: 0.6611 (Supabase)

Possible Scenarios:

Strategy 1 (top_k=7):
    Old: 0.6611
    New: ~0.6911 (+3%)
    
Strategy 2 (BGE-M3):
    Old: 0.6611
    New: ~0.7108 (+5-8%) ⭐
    
Strategy 3 (Re-ranking):
    Old: 0.6611
    New: ~0.7422 (+8-12%) ⭐⭐
    
Combined (all three):
    Old: 0.6611
    New: ~0.7611 (+15%) ⭐⭐⭐

═══════════════════════════════════════════════════════════════════════════════

🚀 READY TO IMPLEMENT?

Start with Strategy 2 (BGE-M3) - it's the quickest high-impact option!
Would you like me to implement it?
""")
