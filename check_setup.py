"""Check what's available and pull missing models"""

import subprocess
import sys

print("="*70)
print("🔍 OLLAMA DIAGNOSTIC")
print("="*70)

# Check if Ollama is running
try:
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
    print("\n✅ Ollama is running!\n")
    print("Available models:")
    print(result.stdout)
except Exception as e:
    print(f"\n❌ Ollama not running: {e}")
    print("   Start it with: ollama serve")
    sys.exit(1)

# Check for required models
required_models = ['llama3', 'llama2', 'mxbai-embed-large']
print("\n" + "="*70)
print("📦 REQUIRED MODELS")
print("="*70)

# Parse available models
available = result.stdout.lower()

for model in required_models:
    if model.lower() in available:
        print(f"✅ {model} - Installed")
    else:
        print(f"❌ {model} - NOT INSTALLED")
        print(f"   Install with: ollama pull {model}")

# Recommend model
print("\n" + "="*70)
print("💡 RECOMMENDATIONS")
print("="*70)

if 'llama3' in available:
    print("✅ Use: OLLAMA_MODEL = 'llama3'")
elif 'llama2' in available:
    print("⚠️  Use: OLLAMA_MODEL = 'llama2' (llama3 not found)")
elif 'mistral' in available:
    print("⚠️  Use: OLLAMA_MODEL = 'mistral' (llama not found)")
else:
    print("❌ No chat models found!")
    print("   Install one: ollama pull llama3")

if 'mxbai-embed-large' in available:
    print("✅ Embedding model ready: mxbai-embed-large")
else:
    print("❌ Embedding model not found!")
    print("   Install it: ollama pull mxbai-embed-large")

# Check documents
print("\n" + "="*70)
print("📄 DOCUMENTS")
print("="*70)

import os
if os.path.exists('vault.txt'):
    size = os.path.getsize('vault.txt')
    print(f"✅ vault.txt exists ({size} bytes)")
    if size < 100:
        print("   ⚠️  File is very small, might be empty")
else:
    print("❌ vault.txt not found")
    print("   Upload PDFs first: python original_code/upload.py")

if os.path.exists('ground_truth.json'):
    print("✅ ground_truth.json exists")
else:
    print("❌ ground_truth.json not found")

print("\n" + "="*70)
print("🚀 NEXT STEPS")
print("="*70)
print("""
1. Pull missing models:
   ollama pull llama3
   ollama pull mxbai-embed-large

2. Upload documents:
   python original_code/upload.py

3. Run test:
   python test_dual_mode.py
""")
