#!/usr/bin/env python3
"""
Quick Setup & Diagnostic for Dual-Mode Testing
"""

import os
import json
import subprocess
import sys

def check_ollama():
    """Check if Ollama is running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is running")
            # List models
            lines = result.stdout.split('\n')[1:]  # Skip header
            models = [l.split()[0] for l in lines if l.strip()]
            print(f"   Models available: {len(models)} installed")
            
            # Check for required models
            has_embedding = any('mxbai-embed' in m for m in models)
            has_llm = any(m.startswith(('gemma', 'llama')) for m in models)
            
            if has_embedding:
                print("   ✅ mxbai-embed-large: Found")
            else:
                print("   ❌ Missing: mxbai-embed-large")
                print("      Run: ollama pull mxbai-embed-large")
            
            if has_llm:
                llm_models = [m for m in models if m.startswith(('gemma', 'llama'))]
                print(f"   ✅ LLM Models: {', '.join(llm_models)}")
            else:
                print("   ❌ Missing: LLM model")
                print("      Run: ollama pull gemma3:4b")
            
            return has_embedding and has_llm
        else:
            print("❌ Ollama error!")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama timeout (not responding)")
        return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False


def check_documents():
    """Check if documents exist"""
    files = ["vault.txt", "ground_truth.json", "vault_embeddings_cache.json"]
    
    print("\n" + "="*70)
    print("📄 DOCUMENT STATUS")
    print("="*70)
    
    for f in files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            if size > 0:
                print(f"✅ {f}: {size:,} bytes")
            else:
                print(f"⚠️  {f}: EMPTY (0 bytes)")
        else:
            print(f"❌ {f}: NOT FOUND")
    
    vault_size = os.path.getsize("vault.txt") if os.path.exists("vault.txt") else 0
    return vault_size > 0


def show_upload_instructions():
    """Show how to upload documents"""
    print("\n" + "="*70)
    print("📤 HOW TO UPLOAD DOCUMENTS")
    print("="*70)
    print("""
1. Open file upload dialog:
   python original_code/upload.py

2. Select PDF files from your computer
   
3. Wait for processing (embedding generation)
   
4. After complete, run test again:
   python test_dual_mode.py

Expected time: 2-5 minutes per PDF
""")


def show_test_instructions():
    """Show how to run the test"""
    print("\n" + "="*70)
    print("🧪 READY TO TEST")
    print("="*70)
    print("""
1. Make sure Ollama is running:
   ollama serve
   
2. Run the test:
   python test_dual_mode.py
   
3. Results will be saved to:
   test_results/dual_mode_test_*.json
   
Expected duration: 2-3 minutes

Commands:
  - Manual test Local:    python localrag_dual.py --mode local
  - Manual test Supabase: python localrag_dual.py --mode supabase
  - Auto test both:       python test_dual_mode.py
""")


def main():
    print("="*70)
    print("🚀 DUAL-MODE RAG SYSTEM - SETUP & DIAGNOSTIC")
    print("="*70)
    
    # Check Ollama
    print("\n1️⃣  Checking Ollama...")
    ollama_ok = check_ollama()
    
    # Check documents
    print("\n2️⃣  Checking Documents...")
    docs_ok = check_documents()
    
    # Show next steps
    print("\n3️⃣  Next Steps:")
    
    if not ollama_ok:
        print("\n❌ BLOCKED: Ollama not running")
        print("   Fix: ollama serve")
        print("   Then run this script again")
        sys.exit(1)
    
    if not docs_ok:
        print("\n❌ BLOCKED: No documents found")
        show_upload_instructions()
        sys.exit(1)
    
    print("\n✅ READY TO TEST!")
    show_test_instructions()
    
    print("\n" + "="*70)
    print("🎯 RECOMMENDED NEXT COMMAND:")
    print("="*70)
    print("python test_dual_mode.py")
    print("="*70)


if __name__ == "__main__":
    main()
