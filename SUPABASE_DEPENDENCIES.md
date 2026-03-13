# Requirements Update for Supabase Integration

## 📦 Updated requirements.txt

```txt
# ============================================
# Original Dependencies (keep)
# ============================================
openai>=1.0.0
torch>=2.0.0
PyPDF2>=3.0.0
ollama>=0.1.0
pyyaml>=6.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-dotenv>=1.0.0

# ============================================
# New Dependencies (for Supabase)
# ============================================
supabase>=2.0.0
httpx>=0.24.0

# ============================================
# Optional: For Development & Testing
# ============================================
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# ============================================
# Optional: For Production Deployment
# ============================================
gunicorn>=20.1.0
uvicorn>=0.23.0
```

### Installation Command:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration Files

### `.env.example` (COMMIT TO REPO)

```bash
# ============================================
# Supabase Configuration
# ============================================
# Copy from Supabase Dashboard > Settings > API

# Your Supabase project URL
# Example: https://your-project-id.supabase.co
SUPABASE_URL=https://your-project-id.supabase.co

# Anon public key (safe to use in frontend)
# Found in: Settings > API > Project API keys > anon
SUPABASE_KEY=your-anon-key-here

# Service role key (KEEP PRIVATE - server side only)
# Found in: Settings > API > Project API keys > service_role
# NEVER expose this in frontend or public code
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# ============================================
# Ollama Configuration
# ============================================
# Base URL สำหรับ Ollama API
OLLAMA_BASE_URL=http://localhost:11434/v1

# API Key (usually matches model name)
OLLAMA_API_KEY=llama3

# Embedding model (must match installed model)
OLLAMA_EMBED_MODEL=mxbai-embed-large

# LLM model for chat
OLLAMA_CHAT_MODEL=llama3

# ============================================
# RAG Configuration
# ============================================
# Path to document vault
DOC_VAULT_PATH=./vault.txt

# Chunk size for splitting documents
CHUNK_SIZE=1000

# Overlap between chunks (for context continuity)
OVERLAP=200

# Number of top-k results for similarity search
TOP_K=3

# Similarity threshold for retrieval
SIMILARITY_THRESHOLD=0.7

# ============================================
# Application Configuration
# ============================================
# Debug mode
DEBUG=false

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Batch size for migrations
MIGRATION_BATCH_SIZE=100
```

### `.env` (DON'T COMMIT - LOCAL ONLY)

Copy `.env.example` and fill in your actual values:

```bash
# ============================================
# Supabase Configuration (ACTUAL VALUES)
# ============================================
SUPABASE_URL=https://xxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI...

# ============================================
# Ollama Configuration
# ============================================
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=llama3
OLLAMA_EMBED_MODEL=mxbai-embed-large
OLLAMA_CHAT_MODEL=llama3

# ============================================
# RAG Configuration
# ============================================
DOC_VAULT_PATH=./vault.txt
CHUNK_SIZE=1000
OVERLAP=200
TOP_K=3
SIMILARITY_THRESHOLD=0.7

# ============================================
# Application Configuration
# ============================================
DEBUG=false
LOG_LEVEL=INFO
MIGRATION_BATCH_SIZE=100
```

### `.gitignore` (UPDATE)

Add these lines to `.gitignore`:

```bash
# Environment variables (NEVER commit!)
.env
.env.local
.env*.local

# Backups
backups/
*.backup
*.bak

# Logs
logs/
*.log

# Cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Application-specific
vault_embeddings.json  # (optional - comment out if want to backup)
vault.txt.bak
```

---

## 🔄 Setup Instructions

### Step 1: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup Environment Variables

```bash
# Create .env from example
cp .env.example .env

# Edit .env with your actual values
# (Use your favorite editor: VSCode, nano, etc.)
```

### Step 4: Verify Setup

```bash
# Test Supabase connection
python -m supabase.config

# Test Ollama connection
python -c "import ollama; print(ollama.list())"
```

---

## 📋 Dependency Explanation

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >=1.0.0 | For OpenAI API calls (if needed) |
| `torch` | >=2.0.0 | Vector operations & embeddings |
| `PyPDF2` | >=3.0.0 | PDF extraction & processing |
| `ollama` | >=0.1.0 | Local LLM interface |
| `pyyaml` | >=6.0 | YAML config file parsing |
| `beautifulsoup4` | >=4.12.0 | HTML/XML parsing |
| `lxml` | >=4.9.0 | XML processing |
| `python-dotenv` | >=1.0.0 | Environment variable loading |

### Supabase Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `supabase` | >=2.0.0 | Supabase Python client |
| `httpx` | >=0.24.0 | HTTP client (dependency for supabase) |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >=7.4.0 | Testing framework |
| `pytest-asyncio` | >=0.21.0 | Async test support |
| `pytest-cov` | >=4.1.0 | Code coverage |
| `black` | >=23.0.0 | Code formatting |
| `flake8` | >=6.0.0 | Code linting |
| `mypy` | >=1.0.0 | Static type checking |

---

## 🚀 Quick Start Commands

### Initialize Project

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy and configure .env
cp .env.example .env
# Edit .env with your Supabase credentials

# 6. Verify setup
python -m supabase.config
```

### Run Migration

```bash
# Dry run first
python scripts/migrate_to_supabase.py --dry-run

# Actual migration
python scripts/migrate_to_supabase.py

# Verify
python scripts/verify_migration.py
```

### Run Application

```bash
# Start RAG chat
python localrag.py --model llama3

# Process PDF
python process_specific_pdf.py document.pdf

# Process Thai PDF
python process_thai_pdf.py thai_document.pdf
```

### Run Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_supabase.py

# With coverage
pytest tests/ --cov=supabase --cov=scripts
```

---

## ⚠️ Security Best Practices

### DO:
- ✅ Keep `.env` in `.gitignore`
- ✅ Use separate keys for development and production
- ✅ Rotate Supabase keys regularly
- ✅ Use environment variables for all secrets
- ✅ Keep service role key private (server-side only)

### DON'T:
- ❌ Commit `.env` to git
- ❌ Log sensitive information
- ❌ Expose service role key in frontend code
- ❌ Use hardcoded credentials
- ❌ Share `.env` files via email or chat

---

## 🔍 Checking Installed Packages

```bash
# List all installed packages
pip list

# Check specific package
pip show supabase

# Check compatibility
pip check
```

---

## 🐛 Troubleshooting Installation

### Issue: "No module named 'X'"

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or specific package
pip install -U supabase
```

### Issue: "Version conflict"

```bash
# Create fresh virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "supabase-py import error"

```bash
# Verify Supabase is installed
pip show supabase

# If not, install explicitly
pip install supabase==2.0.0 httpx==0.24.0

# Check imports
python -c "from supabase import create_client; print('OK')"
```

---

## 📊 Dependency Tree (Simplified)

```
easy-local-rag/
├── Supabase Integration
│   ├── supabase (main client)
│   └── httpx (HTTP library)
│
├── Document Processing
│   ├── PyPDF2 (PDF reading)
│   ├── beautifulsoup4 (HTML parsing)
│   └── lxml (XML processing)
│
├── Machine Learning
│   ├── torch (tensor operations)
│   └── ollama (LLM interface)
│
├── Configuration
│   ├── pyyaml (YAML parsing)
│   └── python-dotenv (env vars)
│
├── API Integration
│   └── openai (OpenAI API - optional)
│
└── Development
    ├── pytest (testing)
    ├── black (formatting)
    ├── flake8 (linting)
    └── mypy (type checking)
```

---

## ✅ Verification Checklist

After installation:

```bash
# 1. Check Python version
python --version
# Expected: Python 3.8+

# 2. Check all packages
pip check
# Expected: No broken dependencies

# 3. Test Supabase import
python -c "from supabase import create_client; print('✅ Supabase OK')"

# 4. Test other imports
python -c "import torch, ollama, PyPDF2; print('✅ Core imports OK')"

# 5. Test environment loading
python -c "from dotenv import load_dotenv; load_dotenv(); print('✅ dotenv OK')"

# 6. Test Ollama connection
python -c "import ollama; models = ollama.list(); print(f'✅ Ollama OK - {len(models.models)} models')"
```

---

**Status:** Ready to use  
**Last Updated:** March 12, 2026
