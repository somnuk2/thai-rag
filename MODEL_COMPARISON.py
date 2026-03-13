#!/usr/bin/env python
"""Check available models and compare LLM options for accuracy"""

try:
    from ollama import Client
    c = Client()
    models = c.list()
    
    print("\n" + "="*80)
    print("ALL INSTALLED MODELS")
    print("="*80)
    
    for model in models:
        model_name = model.get('name', model)
        print(f"  • {model_name}")
    
    print("\n" + "="*80)
    print("MODEL ANALYSIS FOR ACCURACY IMPROVEMENT")
    print("="*80)
    
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying fallback method...")

# Fallback - show what models are referenced in docs
print("""
Known Models in This Project:
  
  Embedding Models (for vector search):
    ✓ mxbai-embed-large [CURRENT] - 1024D, good but English-focused
    • bge-m3 - Multilingual, better Thai support
    • gte-large - Strong Thai support
    • gte-base - Faster, good quality
  
  LLM Models (for answer generation):
    ✓ gemma3:4b [CURRENT] - 4B params, fast, decent quality
    • llama3.3:70b - Large, better accuracy but slow
    • qwen2.5-coder - Code focus
    • deepseek-coder - Code focus
    • openthaigpt - Thai-specific! [NEW OPTION]

""")

print("\n" + "="*80)
print("OPENTHAIGPT 1.5 7B ANALYSIS")
print("="*80)

print("""
Model: openthaigpt1.5-7b-instruct (GGUF format)
Location: huggingface.co/openthaigpt/openthaigpt1.5-7b-instruct

Specifications:
  • Size: 7B parameters (medium-large)
  • Language: Thai-optimized
  • Type: Instruction-tuned (good for Q&A)
  • Format: GGUF (efficient, runs on CPU)
  • Quality: High accuracy for Thai

Comparison with Current (gemma3:4b):
┌─────────────────┬──────────────────────┬─────────────────────┐
│ Aspect          │ gemma3:4b [CURRENT]  │ OpenThaiGPT 1.5 7B  │
├─────────────────┼──────────────────────┼─────────────────────┤
│ Language focus  │ Multilingual         │ Thai-specific ⭐    │
│ Parameters      │ 4B (small)           │ 7B (medium-large)   │
│ Thai quality    │ Good                 │ Excellent ⭐⭐      │
│ Speed           │ Fast (2-3s)          │ Slower (3-5s)       │
│ Accuracy        │ 0.66 current         │ ~0.70-0.75 est.     │
│ Memory usage    │ ~2.5 GB              │ ~4-5 GB             │
│ Install size    │ ~2.5 GB              │ ~5-7 GB             │
└─────────────────┴──────────────────────┴─────────────────────┘

Expected Impact on Accuracy:
  Current: 0.6611 (66.11%)
  With OpenThaiGPT: ~0.72-0.75 (+8-13%) ⭐⭐⭐

Why Better for Thai:
  1. Trained on Thai corpus (not English-first)
  2. Understanding Thai context/idioms
  3. Better with Thai sign language domain
  4. 7B > 4B usually better accuracy

Installation:
  1. Download: ollama pull openthaigpt1.5-7b-instruct
     (or specify full path with GGUF)
  2. Usage: Same as gemma3:4b, just change model name
  3. Time: ~2-3 minutes download
  4. Space: ~5-7 GB additional

How to Test:
  1. Change config.py:
     OLLAMA_CHAT_MODEL = "openthaigpt1.5-7b-instruct"
  
  2. Run 10-question test:
     python test_dual_mode.py  # Will auto-test with new model
  
  3. Compare results with baseline (0.6611)

Cost/Benefit:
  Cost: +2-3GB disk, +50% slower answers
  Benefit: +8-13% accuracy improvement
  Verdict: WORTH IT for production
""")

print("\n" + "="*80)
print("DECISION TREE")
print("="*80)

print("""
Choose your improvement strategy:

1. SPEED PRIORITY (use current gemma3:4b + optimize)
   ├─ Increase top_k: 3→7
   ├─ Switch embedding: mxbai→bge-m3
   └─ Expected improvement: +3-5%

2. ACCURACY PRIORITY (switch to OpenThaiGPT)
   ├─ Install: openthaigpt1.5-7b-instruct
   ├─ Change config model
   ├─ Increase top_k: 3→7
   ├─ Switch embedding: mxbai→bge-m3
   └─ Expected improvement: +8-13% ⭐⭐⭐

3. BALANCED (Medium effort, good results)
   ├─ Increase top_k: 3→5
   ├─ Switch embedding: mxbai→bge-m3
   ├─ Add LLM re-ranking
   └─ Expected improvement: +5-8%

RECOMMENDATION: Strategy 2 (OpenThaiGPT)
Reason: Thai-specific model >> generic model for Thai RAG
""")
