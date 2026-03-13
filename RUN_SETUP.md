# 🚀 Complete Setup & Run Scripts - Quick Guide

## Windows Users

### Option 1: PowerShell (Recommended)
```powershell
# Open PowerShell in project folder
# Full setup + run chat
.\setup_and_run.ps1

# Skip model downloading (faster if you have models)
.\setup_and_run.ps1 -SkipModels

# Just run chat (skip setup)
.\setup_and_run.ps1 -ChatOnly

# Use different model
.\setup_and_run.ps1 -Model mistral
```

### Option 2: Batch File
```batch
# Open Command Prompt in project folder
# Full setup + run chat
setup_and_run.bat

# Skip model downloading
setup_and_run.bat --skip-models

# Just open Command Prompt and run any command in this readme
```

---

## All Users (Python)

### Full Setup + Run Chat
```bash
python setup_and_run.py

# Equivalent to:
# 1. Check Python version
# 2. Check Ollama installation
# 3. Install dependencies (pip install -r requirements.txt)
# 4. Pull models (ollama pull llama3, mxbai-embed-large)
# 5. Prepare vault.txt
# 6. Run localrag.py
```

### Skip Model Downloading (Faster)
```bash
python setup_and_run.py --skip-models
# If you already have models installed
```

### Just Run Chat (Skip Setup)
```bash
python setup_and_run.py --chat-only
# Much faster if setup already done
```

### Use Different Model
```bash
python setup_and_run.py --model mistral
python setup_and_run.py --model neural-chat
# (must have pulled the model first)
```

---

## What These Scripts Do

### Automated Steps:
```
1. ✅ Check Python version (3.8+)
2. ✅ Check Ollama installed
3. ✅ Check Ollama running
4. ✅ Install dependencies (pip)
5. ✅ Pull models (llama3, mxbai-embed-large)
6. ✅ Check vault.txt exists
7. ✅ Verify all setup
8. ✅ Start interactive chat
```

### Time Estimate:
- **First time:** 15-45 minutes (includes model downloads)
- **Subsequent times:** < 1 minute (with --chat-only)

---

## Troubleshooting

### "Ollama not found"
```powershell
# Download from https://ollama.ai
# Then restart the script
```

### "Ollama not running"
```powershell
# Option 1: Start Ollama app (GUI)
# Option 2: Run in another terminal:
ollama serve
# Then press Enter in the setup script
```

### "vault.txt not found"
```bash
# Option 1: Upload PDF via GUI
python original_code/upload.py

# Option 2: Process PDF via CLI
python process_specific_pdf.py

# Option 3: Create manually
# Create empty vault.txt, then run setup again
```

### "Connection refused (Ollama port)"
```bash
# Make sure Ollama is running
# Check: ollama list
# If error, run: ollama serve
```

---

## Next Steps After First Run

### For Subsequent Runs:
```bash
# Fast way (skip setup, just chat)
python setup_and_run.py --chat-only

# Or PowerShell
.\setup_and_run.ps1 -ChatOnly

# Or just run chat directly
python localrag.py
```

### If You Add New Documents:
```bash
# Upload new PDF
python original_code/upload.py

# Then run setup again (will regenerate embeddings)
python setup_and_run.py --skip-models

# Or with --clear-cache to force regenerate
python localrag.py --clear-cache
```

### Change Model for Next Run:
```bash
# List available models
ollama list

# Pull new model
ollama pull mistral

# Run with new model
python setup_and_run.py --model mistral
```

---

## File Comparison

| Script | Platform | Best For | Time to Run |
|--------|----------|----------|------------|
| `setup_and_run.py` | All | Full automation, cross-platform | 20-40 min |
| `setup_and_run.ps1` | Windows | Native PowerShell, colored output | 20-40 min |
| `setup_and_run.bat` | Windows | Classic CMD, simplest | 20-40 min |
| `localrag.py` | All | Chat only, skip setup | < 1 min |

---

## Advanced Usage

### Check Setup Without Running Chat:
```python
# Edit setup_and_run.py, comment out run_chat() call
# Or manually check:
python -c "import torch; import ollama; print('OK')"
```

### Dry Run (Check without doing anything):
```bash
# Currently not supported, but you can:
# 1. Run python --version
# 2. Run ollama list
# 3. Check requirements.txt
```

### Custom Configuration:
Edit the scripts to change:
- Default model name
- Chat parameters
- Setup steps

---

## Summary

**One-line quickstart:**
```powershell
# PowerShell (Windows)
.\setup_and_run.ps1

# Python (All platforms, if PowerShell doesn't work)
python setup_and_run.py

# Batch (Windows Command Prompt)
setup_and_run.bat
```

That's it! The script will handle everything automatically. 🎉
