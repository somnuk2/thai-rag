# Supabase Setup - Next Steps

**Status:** ✅ SDK Working | ⚠️ Authentication Failing | ❌ Tables Not Created

---

## 🔧 Step 1: Get Correct API Key

The error indicates your current API key `LzarSlPXTeCCnR4F` isn't working. You likely need a **different** key type.

### Find Your Supabase API Keys

1. Go to: https://supabase.com/dashboard
2. Select your project: **iiscwofszouigzwrdjuw**
3. Go to: **Settings** → **API** 
4. You'll see two keys:
   - **anon public** (safe for frontend)
   - **service_role** (server-side only, more privileges)

### Try Both Keys

**First, try the `anon` key:**
```bash
# Edit .env and update:
SUPABASE_KEY=your-anon-key-here
# (from Settings > API > Project API keys > anon)

# Test:
python -c "from supabase_vector_store import SupabaseVectorStore; SupabaseVectorStore()"
```

**If that fails, try the `service_role` key:**
```bash
# Edit .env and update:
SUPABASE_KEY=your-service-role-key-here
# (from Settings > API > Project API keys > service_role)

# Test:
python -c "from supabase_vector_store import SupabaseVectorStore; SupabaseVectorStore()"
```

---

## 🗄️ Step 2: Create Database Tables

Once authentication works, create the required tables in your Supabase database.

### Option A: Automatic (Recommended)
```bash
python setup_dual_mode.py --mode supabase
```

This will:
- ✅ Test your connection
- ✅ Create embeddings table
- ✅ Set up pgvector
- ✅ Create RPC functions for search

### Option B: Manual SQL (If automatic fails)

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Go to: **SQL Editor**
4. Click: **+ New Query**
5. Paste this SQL:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table
CREATE TABLE IF NOT EXISTS public.embeddings (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster search
CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
ON public.embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create search function
CREATE OR REPLACE FUNCTION match_embeddings(
  query_embedding VECTOR(1024),
  match_count INT DEFAULT 3,
  match_threshold FLOAT DEFAULT 0.5
)
RETURNS TABLE (
  id BIGINT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
) LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    embeddings.id,
    embeddings.content,
    embeddings.metadata,
    (1 - (embeddings.embedding <=> query_embedding)) AS similarity
  FROM embeddings
  WHERE (1 - (embeddings.embedding <=> query_embedding)) > match_threshold
  ORDER BY embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Set table permissions (RLS)
ALTER TABLE public.embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users"
  ON public.embeddings
  FOR SELECT
  USING (true);

CREATE POLICY "Enable insert for all users"
  ON public.embeddings
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Enable delete for all users"
  ON public.embeddings
  FOR DELETE
  USING (true);
```

6. Click: **Run** (or Cmd+Enter)
7. Wait for success ✅

---

## ✅ Step 3: Test Everything

Once tables are created, test the full system:

```bash
# 1. Check config
python -c "from config import Config; Config.print_config()"
# Should show: Mode: supabase

# 2. Test connection
python -c "from supabase_vector_store import SupabaseVectorStore; s = SupabaseVectorStore(); s.health_check(); print('OK')"
# Should show: OK (without errors)

# 3. Start chat
python localrag_dual.py --mode supabase
# Type: test question
# Type: quit (to exit)
```

---

## 📋 Troubleshooting

**Error: "Invalid API key"**
- ❌ Wrong key format
- ✅ Get the correct key from Supabase dashboard
- ✅ Check for copy-paste errors
- ✅ Try the service_role key instead of anon

**Error: "relation 'embeddings' does not exist"**
- ❌ Tables not created
- ✅ Run the SQL from Step 2
- ✅ Or run: `python setup_dual_mode.py --mode supabase`

**Error: "function match_embeddings does not exist"**
- ❌ RPC function not created
- ✅ Run the full SQL from Step 2
- ✅ Check that CREATE OR REPLACE FUNCTION ran successfully

**Connection times out**
- ❌ Firewall/network issue
- ✅ Check your internet connection
- ✅ Check if Supabase is accessible (https://supabase.com)
- ✅ Check VPN if using one

**Connection refused connection**
- ❌ Your IP may be blocked
- ✅ Go to Supabase → Settings → Database (whitelist your IP)
- ✅ Or allow all IPs: 0.0.0.0/0 (less secure)

---

## 🎯 Quick Decision Tree

**My API key isn't working:**
→ Go to Supabase dashboard and get the correct `anon` or `service_role` key

**I got the key but tables don't exist:**
→ Run: `python setup_dual_mode.py --mode supabase`

**Automatic setup failed:**
→ Run the SQL manually from Step 2 above

**Connection succeeds but queries fail:**
→ Make sure the RPC function `match_embeddings` exists
→ Re-run the SQL from Step 2

---

## 📊 Current Status

| Component | Status | Action |
|-----------|--------|--------|
| SDK | ✅ Installed & Working | Continue |
| Connection | ⚠️ Authentication Failing | Get correct API key |
| Tables | ❌ Not Created | Run Step 2 |
| RPC Functions | ❌ Not Created | Run Step 2 |
| Health Check | ❌ Failing | Fix connection first |

---

## 🚀 Next Action

```
1. Find correct API key in Supabase dashboard
2. Update SUPABASE_KEY in .env
3. Create tables (automatic or manual)
4. Test with: python setup_dual_mode.py --mode supabase
5. Start chat: python localrag_dual.py --mode supabase
```

**Est. time:** 10-15 minutes
