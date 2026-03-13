# Supabase Setup - FINAL STEPS

**Status:** ✅ **SDK Connected** | ✅ **Credentials Verified** | ⏳ **Database Tables Pending**

---

## 🎯 What's Done

✅ Supabase SDK installed and working  
✅ Credentials verified (anon key: `sb_publishable_eEb6gUzc8Zq6ygtiA_C2lQ_Up6_mjub`)  
✅ Connection established to: `https://iiscwofszouigzwrdjuw.supabase.co`  
✅ SQL script generated for table creation  

---

## 🚀 ONE FINAL STEP: Create Database Table

You must **manually run the SQL** in Supabase. This takes 2 minutes:

### Step 1: Open Supabase SQL Editor
1. Go to: **https://supabase.com/dashboard**
2. Select project: **iiscwofszouigzwrdjuw**
3. Click: **SQL Editor** (left menu)
4. Click: **+ New Query** (top right)

### Step 2: Copy and Paste the SQL

**Paste this entire SQL block:**

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

### Step 3: Run It!
- Click: **Run** button (or press `Cmd+Enter` or `Ctrl+Enter`)
- Wait for success ✅

---

## ✅ Verification

After running the SQL, verify it worked:

```bash
python -c "from supabase_vector_store import SupabaseVectorStore; s = SupabaseVectorStore(); s.health_check(); print('SUCCESS!')"
```

**Expected output:**
```
[OK] Direct PostgreSQL health check passed
SUCCESS!
```

---

## 🎉 Then You're Ready!

Once the SQL is executed and verified, start using:

```bash
# 1. Make sure Ollama is running
ollama serve  # (in another terminal)

# 2. Start the RAG chat
python localrag_dual.py --mode supabase

# 3. Ask a question!
```

---

## 📊 Current Configuration

**File:** `.env`

```
RAG_MODE=supabase
SUPABASE_URL=https://iiscwofszouigzwrdjuw.supabase.co
SUPABASE_KEY=sb_publishable_eEb6gUzc8Zq6ygtiA_C2lQ_Up6_mjub
```

---

## 🆘 Troubleshooting

**SQL execution fails with "permission denied"**
- You may need to run SQL as the admin user
- Or you may need to enable pgvector in extensions first

**Table created but health check still fails**
- The Supabase cache may need to refresh
- Wait 30 seconds and try again
- Or go to **SQL Editor** and refresh the schema

**Cannot see the embeddings table after creation**
- Go to **Database** > **Tables** and refresh
- Make sure you're looking in the `public` schema

---

## ✨ What's Next?

1. **Run the SQL** (Step 1-3 above)
2. **Verify the connection** (Verification section)
3. **Start the chat** (Ready section)
4. **Upload documents** (use `original_code/upload.py`)
5. **Ask questions!**

---

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Start chat (Supabase) | `python localrag_dual.py --mode supabase` |
| Start chat (Local) | `python localrag_dual.py --mode local` |
| Upload PDF | `python original_code/upload.py` |
| Check config | `python -c "from config import Config; Config.print_config()"` |
| Run Ollama | `ollama serve` |
| Test connection | `python setup_supabase_tables.py` |

---

**Status:** ✅ READY AFTER ONE SQL RUN  
**Estimated time to complete:** 2-3 minutes  
**Next action:** Open Supabase SQL Editor and run the SQL  

Go! 🚀
