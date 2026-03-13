# 🚀 Dual-Mode RAG System Setup Guide

## ⚡ Quick Start

### Local Mode (Original - JSON files)
```powershell
# PowerShell
.\setup_and_run.ps1 -ChatOnly

# Or Python
python localrag_dual.py --mode local

# Or with new setup script
python setup_dual_mode.py --mode local
```

### Supabase Mode (Remote Database)
```powershell
# PowerShell (future - will add mode support)
# For now, use Python:

python setup_dual_mode.py --mode supabase
# This will ask for Supabase credentials

# Then run chat
python localrag_dual.py --mode supabase
```

---

## 🎯 Architecture

### Two-Tier System

```
┌─────────────────────────────────┐
│   localrag_dual.py              │ ← Main chat application
│   (Unified interface)           │
└──────────────┬──────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
   ┌─────────┐   ┌─────────────┐
   │ Local   │   │ Supabase    │
   │ Mode    │   │ Mode        │
   ├─────────┤   ├─────────────┤
   │ JSON    │   │ pgvector    │
   │ Files   │   │ Database    │
   └─────────┘   └─────────────┘
```

### Component Layer

```
Application Layer
        ↓
api: vector_store_factory
        ↓
         ┌─────────────────────────┐
         │ VectorStore (abstract)  │
         └──────┬──────────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
  LocalVectorStore  SupabaseVectorStore
  (JSON/torch)      (pgvector/http)
```

---

## 📝 Configuration

### .env File Structure

```bash
# Select mode: 'local' or 'supabase'
RAG_MODE=local

# For Supabase mode:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key

# Ollama (both modes)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_CHAT_MODEL=llama3
OLLAMA_EMBED_MODEL=mxbai-embed-large

# RAG parameters
TOP_K=3
SIMILARITY_THRESHOLD=0.0
```

### How to Switch Modes

1. **Edit .env:**
   ```bash
   # Change this line:
   RAG_MODE=local    # ← Change to 'supabase'
   ```

2. **Or use CLI:**
   ```bash
   # Override at runtime
   python localrag_dual.py --mode supabase
   ```

---

## 🔍 Supported Commands

### Python Script (Unified)

```bash
# Local mode (default)
python localrag_dual.py

# Explicit local
python localrag_dual.py --mode local

# Supabase mode
python localrag_dual.py --mode supabase

# Use different model
python localrag_dual.py --model mistral

# Combine options
python localrag_dual.py --mode supabase --model mistral
```

### Setup Scripts

```bash
# Full setup - local mode
python setup_dual_mode.py

# Full setup - supabase mode (asks for credentials)
python setup_dual_mode.py --mode supabase

# Skip model downloading
python setup_dual_mode.py --mode local --skip-models

# Just run chat
python setup_dual_mode.py --chat-only
```

---

## 🚀 Migration Path

### Option 1: Start Local, Migrate to Supabase

```bash
# 1. Use local mode (default)
python localrag_dual.py --mode local

# 2. When ready, setup Supabase (see SUPABASE_SETUP.md)

# 3. Migrate data (see SUPABASE_MIGRATION_PHASE2.md)

# 4. Switch to Supabase
python localrag_dual.py --mode supabase
```

### Option 2: Start Fresh with Supabase

```bash
# 1. Create Supabase project (see SUPABASE_SETUP.md)

# 2. Run setup with supabase mode
python setup_dual_mode.py --mode supabase

# 3. Start with remote database from the beginning
python localrag_dual.py --mode supabase
```

---

## 📊 Comparison

| Feature | Local Mode | Supabase Mode |
|---------|-----------|---------------|
| **Storage** | JSON files | PostgreSQL |
| **Setup Time** | < 5 min | 30+ min |
| **Initial Cost** | Free | Free (tier) |
| **Scalability** | Limited | Unlimited |
| **Concurrent Users** | 1 | Many |
| **Backup** | Manual | Automatic |
| **Search Speed** | O(n) | O(log n) |
| **Requirements** | Just Python | Supabase account |

---

## 🔧 Troubleshooting

### "Vector store error"
```bash
# Check which mode is active
grep RAG_MODE .env

# Verify it's set correctly
python -c "from config import Config; print(Config.MODE)"
```

### "Supabase connection failed"
```bash
# Check credentials in .env
# Verify Supabase project exists
# Test manually:
python -c "from supabase import create_client; c = create_client('URL', 'KEY'); print(c)"
```

### "Can't find vector store"
```bash
# Make sure requirements.txt is installed
pip install -r requirements.txt

# For Supabase mode:
pip install supabase
```

---

## 📋 File Structure

```
easy-local-rag/
├── config.py                      ← Configuration management
├── vector_store_base.py           ← Abstract base class
├── local_vector_store.py          ← JSON implementation
├── supabase_vector_store.py       ← Supabase implementation
├── vector_store_factory.py        ← Create store based on mode
├── localrag_dual.py               ← Main unified chat app
├── setup_dual_mode.py             ← Enhanced setup script
├── .env.example                   ← Config template
└── localrag.py                    ← Original (still works)
```

---

## 🎓 Understanding the System

### Local Mode (Original)

```
┌──────────────────┐
│  localrag_dual   │
│  --mode local    │
└────────┬─────────┘
         │
    ┌────▼─────┐
    │ LocalVS  │◄─── Uses torch.cosine_similarity
    └────┬─────┘
         │
    ┌────▼──────────┐
    │ vault.txt     │
    │ embeddings    │
    │ .json         │
    └───────────────┘
```

### Supabase Mode (New)

```
┌──────────────────┐
│  localrag_dual   │
│  --mode supa     │
└────────┬─────────┘
         │
    ┌────▼──────────┐
    │ SupabaseVS   │◄─── Uses pgvector (SQL)
    └────┬──────────┘
         │
    ┌────▼──────────────────────┐
    │ Supabase PostgreSQL        │
    │ - embeddings table         │
    │ - documents table          │
    │ - pgvector extension       │
    │ - Vector index (IVFFlat)   │
    └────────────────────────────┘
```

---

## 🔐 Security Notes

### Local Mode
- No external service needed
- Complete privacy
- All data stays local

### Supabase Mode
- API key in .env (keep private!)
- Service role key (NEVER expose!)
- Use Row-Level Security for production
- Supabase automatically encrypted

---

## 📞 Next Steps

1. **Read the full documentation:**
   - [START_HERE.md](START_HERE.md)
   - [SUPABASE_MIGRATION_PLAN.md](SUPABASE_MIGRATION_PLAN.md)

2. **Choose your mode:**
   - Local: Start right away
   - Supabase: Follow [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

3. **Run the chat:**
   ```bash
   python localrag_dual.py --mode [local|supabase]
   ```

---

**Status:** ✅ Ready to use both modes!
