# 🔄 How to Switch Between Local and Supabase Modes

## 🎯 Quick Switch Guide

### Option 1: Via .env File (Recommended)

**Step 1: Open .env**
```bash
# If .env doesn't exist, create it from .env.example:
cp .env.example .env
```

**Step 2: Change One Line**

**Local Mode (Default):**
```bash
RAG_MODE=local
```

**Supabase Mode:**
```bash
RAG_MODE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**Step 3: Save and Run**
```bash
python localrag_dual.py
# It will automatically use the mode from .env!
```

---

### Option 2: Via Command Line (Override)

```bash
# Force local mode (ignore .env)
python localrag_dual.py --mode local

# Force Supabase mode (ignore .env)
python localrag_dual.py --mode supabase

# Use different model
python localrag_dual.py --mode supabase --model mistral
```

**Note:** CLI overrides .env file

---

## 📋 Complete Setup for Each Mode

### Complete Local Setup (5 minutes)

```bash
# 1. Create .env (if needed)
cp .env.example .env

# 2. Edit .env - make sure it has:
# RAG_MODE=local

# 3. Install if not done
pip install -r requirements.txt

# 4. Make sure Ollama is running
ollama serve  # (in another terminal) or open Ollama app

# 5. Add a document (optional, can start with empty vault.txt)
python original_code/upload.py
# Or: python process_specific_pdf.py file.pdf

# 6. Run chat!
python localrag_dual.py --mode local
```

### Complete Supabase Setup (45 minutes first time)

```bash
# 1. Create Supabase account at https://supabase.com
   - Create a project
   - Copy project URL
   - Copy anon key
   - Keep them safe!

# 2. Follow SUPABASE_SETUP.md to:
   - Enable pgvector extension
   - Create tables (embeddings, documents, etc.)
   - Create functions for search

# 3. Create .env
cp .env.example .env

# 4. Edit .env with your Supabase credentials
RAG_MODE=supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# 5. Install with Supabase support
pip install -r requirements.txt
pip install supabase

# 6. Run setup to verify connection
python setup_dual_mode.py --mode supabase

# 7. Add documents (will go to Supabase)
python original_code/upload.py
# Or: python process_specific_pdf.py file.pdf

# 8. Run chat!
python localrag_dual.py --mode supabase
```

---

## 🔄 Migration: Local → Supabase

If you're already using **local mode** and want to upgrade:

### Step 1: Keep Your Local Data
```bash
# Your current files stay intact:
vault.txt                      # Still has your documents
vault_embeddings_cache.json    # Still has your embeddings
```

### Step 2: Setup Supabase
```bash
# Follow "Complete Supabase Setup" above (steps 1-6)
```

### Step 3: Migrate Your Data

```bash
# See SUPABASE_MIGRATION_PHASE2.md for detailed steps
# Quick version:
python scripts/migrate_to_supabase.py \
    --input vault_embeddings.json \
    --vault vault.txt

# Verify migration worked
python scripts/verify_migration.py
```

### Step 4: Switch to Supabase Mode

```bash
# Edit .env:
RAG_MODE=supabase

# Run chat (will use Supabase instead of JSON files)
python localrag_dual.py
```

### Step 5: (Optional) Keep Local Data as Backup

```bash
# Keep your JSON files as backup
mkdir backups
cp vault_embeddings_cache.json backups/
cp vault.txt backups/

# Or on Windows:
mkdir backups
copy vault_embeddings_cache.json backups\
copy vault.txt backups\
```

---

## 🔀 Migration: Supabase → Local (If Needed)

To go back to local mode from Supabase:

```bash
# 1. Change .env
RAG_MODE=local

# 2. Export data from Supabase
# (This would require custom export script - contact admin if needed)

# 3. Run local chat
python localrag_dual.py --mode local
```

**Note:** Going back requires exporting data from Supabase. Keep your original JSON files if you think you might do this!

---

## ✅ Verification Checklist

### For Local Mode:
- [ ] .env has `RAG_MODE=local`
- [ ] vault.txt exists
- [ ] Ollama is running
- [ ] Can run: `python localrag_dual.py`

### For Supabase Mode:
- [ ] .env has `RAG_MODE=supabase`
- [ ] .env has `SUPABASE_URL` and `SUPABASE_KEY`
- [ ] Ollama is running  
- [ ] Can run: `python localrag_dual.py --mode supabase`
- [ ] Supabase project exists with tables created
- [ ] Can run: `python -c "from supabase import create_client; c = create_client('URL', 'KEY'); c.table('embeddings').select('id').limit(1).execute(); print('OK')"`

---

## 🆘 Troubleshooting Mode Switching

### "It's using the wrong mode"

**Check what mode it's actually using:**
```bash
python -c "from config import Config; print(f'Current mode: {Config.MODE}')"
```

**Fix:** Make sure .env has the right `RAG_MODE=` line at the top

### "I get 'supabase not installed' error"

**For Supabase mode, install the dependency:**
```bash
pip install supabase
```

### "Connection refused to Ollama"

**Make sure Ollama is running:**
```bash
# Check if running
ollama list

# If not, start it:
ollama serve
# Or open the Ollama app
```

### "Supabase says 'Invalid API key'"

**Check your .env file:**
```bash
# Make sure you have:
SUPABASE_URL=https://xxxxx.supabase.co  (exact URL)
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...   (exact key)

# Test manually:
python -c "from supabase import create_client; c = create_client('YOUR_URL', 'YOUR_KEY'); print('Connection OK')"
```

---

## 📊 Mode-Specific Features

### Local Mode Only:
```bash
# Clear and regenerate embeddings
python localrag.py --clear-cache
```

### Supabase Mode Only:
```bash
# These features in future versions:
# - Multi-user collaboration
# - Cloud backups
# - Real-time sync
# - Advanced analytics
```

---

## 🎓 Examples

### Example 1: Test Both Modes with Same Data

```bash
# Step 1: Add a document in local mode
python localrag_dual.py --mode local
# > Ask a query about your documents: upload a PDF first!
# (Use menu to upload PDF)

# Step 2: Export and setup Supabase
# (Follow migration guide)

# Step 3: Switch to Supabase
python localrag_dual.py --mode supabase
# > Same document, different backend!
```

### Example 2: Different Databases for Different Uses

```bash
# Local for development:
python localrag_dual.py --mode local

# Supabase for production:
RAG_MODE=supabase python localrag_dual.py
```

### Example 3: Use CLI Override

```bash
# Usually local, but this time use Supabase:
python localrag_dual.py --mode supabase

# Usually Supabase, but for testing use local:
python localrag_dual.py --mode local
```

---

## 🚀 Pro Tips

### Tip 1: Create a Script for Each Mode

**Windows - local.bat:**
```batch
@echo off
python localrag_dual.py --mode local
```

**Windows - supabase.bat:**
```batch
@echo off
python localrag_dual.py --mode supabase
```

**Then just double-click to run!**

### Tip 2: Environment Variables Override

```bash
# Set permanently in your shell:

# On Windows PowerShell:
$env:RAG_MODE = "supabase"
python localrag_dual.py

# On Linux/Mac:
export RAG_MODE=local
python localrag_dual.py
```

### Tip 3: Testing Both

```bash
# Side-by-side terminal testing:

# Terminal 1:
python localrag_dual.py --mode local

# Terminal 2:
python localrag_dual.py --mode supabase

# Same chat interface, different backends!
```

---

## 📝 Summary

| Action | Command |
|--------|---------|
| **Use local (default)** | `python localrag_dual.py` |
| **Force local** | `python localrag_dual.py --mode local` |
| **Force Supabase** | `python localrag_dual.py --mode supabase` |
| **Change config** | Edit `RAG_MODE=` in `.env` |
| **See which mode** | `python -c "from config import Config; print(Config.MODE)"` |
| **Setup Supabase** | `python setup_dual_mode.py --mode supabase` |
| **Migrate data** | `python scripts/migrate_to_supabase.py` |

---

## 🎯 Decision Tree

```
Want to use RAG?
    ├─ ✅ Start immediately → Use LOCAL mode
    │  └─ Run: python localrag_dual.py --mode local
    │
    └─ 📊 Need multiple users/cloud → Use SUPABASE
       ├─ Setup Supabase (SUPABASE_SETUP.md)
       ├─ Migrate data (SUPABASE_MIGRATION_PHASE2.md)
       └─ Run: python localrag_dual.py --mode supabase
```

---

**Remember:** Switching is as easy as changing one line in `.env`! 🎉
