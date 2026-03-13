# Phase 2: Migration Script - Guide and Implementation

**คู่มือการสร้าง Migration Script เพื่อย้ายข้อมูลจาก JSON ไป Supabase**

---

## 📋 Overview

Migration Script จะทำหน้าที่:
1. อ่านข้อมูล embeddings จากไฟล์ JSON เดิม
2. อ่านเนื้อหาจากไฟล์ vault.txt
3. แบ่ง (chunk) และสร้าง metadata ที่เหมาะสม
4. อัปโหลด embeddings ไปยัง Supabase ในแบบ batch
5. ตรวจสอบความถูกต้องของการอัปโหลด

---

## 🗂️ File Structure

```
scripts/
├── migrate_to_supabase.py          # Main migration script
├── verify_migration.py              # Verify migration results
└── rollback.py                      # (optional) Rollback script
```

---

## 📝 Step 1: สร้าง Main Migration Script

สร้างไฟล์: `scripts/migrate_to_supabase.py`

```python
"""
Migration Script: Migrate embeddings from JSON to Supabase
===========================================================

Usage:
    python scripts/migrate_to_supabase.py --input vault_embeddings.json --verify
    python scripts/migrate_to_supabase.py --input vault_embeddings.json --batch-size 100
    python scripts/migrate_to_supabase.py --input vault_embeddings.json --dry-run
"""

import os
import json
import logging
import argparse
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import time

from dotenv import load_dotenv
from supabase import create_client, Client
import numpy as np

# ==========================================
# SETUP LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")


# ==========================================
# MIGRATION CLASS
# ==========================================

class SupabaseMigrator:
    """Migrate embeddings from JSON files to Supabase"""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize migrator
        
        Args:
            dry_run: If True, don't actually update database
        """
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.dry_run = dry_run
        self.total_uploaded = 0
        self.total_failed = 0
        self.failed_items = []
        
        logger.info(f"Initialized migrator (dry_run={dry_run})")
    
    def load_json_embeddings(self, json_path: str) -> Tuple[List[List[float]], List[str]]:
        """
        Load embeddings and content from JSON file
        
        File format expected:
        {
            "embeddings": [[1.0, 2.0, ...], ...],
            "content": ["chunk1", "chunk2", ...]
        }
        
        Args:
            json_path: Path to embeddings JSON file
            
        Returns:
            Tuple of (embeddings list, content list)
        """
        logger.info(f"Loading embeddings from {json_path}")
        
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"File not found: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            embeddings = data.get('embeddings', [])
            content = data.get('content', [])
            
            logger.info(f"Loaded {len(embeddings)} embeddings and {len(content)} content chunks")
            
            if len(embeddings) != len(content):
                logger.warning(f"Mismatch: {len(embeddings)} embeddings vs {len(content)} content")
            
            return embeddings, content
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
    
    def load_vault_content(self, vault_path: str) -> str:
        """
        Load vault content from text file
        
        Args:
            vault_path: Path to vault.txt file
            
        Returns:
            Full vault content
        """
        logger.info(f"Loading vault content from {vault_path}")
        
        if not os.path.exists(vault_path):
            raise FileNotFoundError(f"File not found: {vault_path}")
        
        try:
            with open(vault_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Loaded vault content ({len(content)} characters)")
            return content
        
        except Exception as e:
            logger.error(f"Error loading vault: {e}")
            raise
    
    def get_file_hash(self, filepath: str) -> str:
        """
        Calculate MD5 hash of a file
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hash hex string
        """
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        
        return file_hash.hexdigest()
    
    def add_or_get_document(self, file_name: str, file_path: str = None) -> int:
        """
        Add document to database or get existing document ID
        
        Args:
            file_name: Name of the document
            file_path: Path to the file
            
        Returns:
            Document ID
        """
        file_hash = self.get_file_hash(file_path) if file_path else None
        
        try:
            # Check if document already exists
            if file_hash:
                result = self.client.table('documents').select('id').eq('file_hash', file_hash).execute()
                if result.data:
                    logger.info(f"Document '{file_name}' already exists (ID: {result.data[0]['id']})")
                    return result.data[0]['id']
            
            # Create new document entry
            if self.dry_run:
                logger.info(f"[DRY RUN] Would add document: {file_name}")
                return -1  # Dummy ID for dry run
            
            data = {
                'file_name': file_name,
                'file_hash': file_hash,
                'content_type': 'json',
                'status': 'processing',
                'processed_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('documents').insert(data).execute()
            doc_id = result.data[0]['id']
            logger.info(f"Created new document entry (ID: {doc_id})")
            return doc_id
        
        except Exception as e:
            logger.error(f"Error managing document: {e}")
            raise
    
    def upload_embeddings_batch(
        self,
        document_id: int,
        embeddings: List[List[float]],
        content: List[str],
        file_name: str = "vault",
        batch_size: int = 100,
        retry_count: int = 3
    ) -> Tuple[int, int]:
        """
        Upload embeddings in batches
        
        Args:
            document_id: Document ID in database
            embeddings: List of embedding vectors
            content: List of content chunks
            file_name: Name to tag embeddings with
            batch_size: Size of each batch
            retry_count: Number of retries for failed batches
            
        Returns:
            Tuple of (successful uploads, failed uploads)
        """
        total_items = len(embeddings)
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch upload: {total_items} items, batch size: {batch_size}")
        
        for batch_idx in range(0, total_items, batch_size):
            batch_end = min(batch_idx + batch_size, total_items)
            batch_embeddings = embeddings[batch_idx:batch_end]
            batch_content = content[batch_idx:batch_end]
            
            # Prepare batch data
            batch_data = []
            for i, (embedding, text) in enumerate(zip(batch_embeddings, batch_content)):
                item = {
                    'document_id': document_id,
                    'chunk_index': batch_idx + i,
                    'content': text[:5000],  # Truncate if too long
                    'embedding': embedding,
                    'file_name': file_name,
                    'metadata': {
                        'batch_idx': batch_idx // batch_size,
                        'chunk_number': batch_idx + i + 1,
                        'total_chunks': total_items
                    }
                }
                batch_data.append(item)
            
            # Try uploading batch
            uploaded = False
            for attempt in range(retry_count):
                try:
                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would upload batch {batch_idx//batch_size + 1} ({len(batch_data)} items)")
                        successful += len(batch_data)
                        uploaded = True
                        break
                    
                    self.client.table('embeddings').insert(batch_data).execute()
                    successful += len(batch_data)
                    uploaded = True
                    
                    pct = (batch_end / total_items) * 100
                    logger.info(f"Batch {batch_idx//batch_size + 1} uploaded ({batch_end}/{total_items}, {pct:.1f}%)")
                    break
                
                except Exception as e:
                    if attempt == retry_count - 1:
                        failed += len(batch_data)
                        self.failed_items.extend(batch_data)
                        logger.error(f"Failed to upload batch {batch_idx//batch_size + 1} after {retry_count} retries: {e}")
                    else:
                        logger.warning(f"Batch upload attempt {attempt + 1} failed, retrying... ({e})")
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            # Add delay between batches to avoid rate limiting
            if batch_end < total_items:
                time.sleep(0.5)
        
        return successful, failed
    
    def verify_migration(self, document_id: int, expected_count: int) -> bool:
        """
        Verify migration was successful
        
        Args:
            document_id: Document ID to verify
            expected_count: Expected number of embeddings
            
        Returns:
            True if verification passed
        """
        logger.info("Verifying migration...")
        
        try:
            result = self.client.table('embeddings').select('id').eq('document_id', document_id).execute()
            actual_count = len(result.data) if result.data else 0
            
            logger.info(f"Expected: {expected_count}, Actual: {actual_count}")
            
            if actual_count == expected_count:
                logger.info("✅ Verification passed!")
                return True
            else:
                logger.warning(f"⚠️ Count mismatch: {actual_count} vs {expected_count}")
                return False
        
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False
    
    def run(
        self,
        embeddings_json: str = "vault_embeddings.json",
        vault_file: str = "vault.txt",
        batch_size: int = 100
    ) -> bool:
        """
        Execute migration
        
        Args:
            embeddings_json: Path to embeddings JSON file
            vault_file: Path to vault text file
            batch_size: Batch size for uploads
            
        Returns:
            True if migration successful
        """
        logger.info("=" * 60)
        logger.info("SUPABASE MIGRATION STARTED")
        logger.info("=" * 60)
        logger.info(f"Dry Run: {self.dry_run}")
        
        start_time = time.time()
        
        try:
            # Step 1: Load data
            logger.info("\n[STEP 1] Loading embeddings and vault content...")
            embeddings, content = self.load_json_embeddings(embeddings_json)
            vault_content = self.load_vault_content(vault_file)
            
            # Step 2: Add/Get document
            logger.info("\n[STEP 2] Creating/Getting document entry...")
            doc_id = self.add_or_get_document("vault.txt", vault_file)
            
            # Step 3: Upload embeddings
            logger.info("\n[STEP 3] Uploading embeddings...")
            successful, failed = self.upload_embeddings_batch(
                doc_id,
                embeddings,
                content,
                batch_size=batch_size
            )
            
            # Step 4: Verify
            logger.info("\n[STEP 4] Verifying migration...")
            if not self.dry_run:
                verified = self.verify_migration(doc_id, len(embeddings))
            else:
                verified = True
            
            # Summary
            elapsed = time.time() - start_time
            logger.info("\n" + "=" * 60)
            logger.info("MIGRATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total embeddings: {len(embeddings)}")
            logger.info(f"Successfully uploaded: {successful}")
            logger.info(f"Failed uploads: {failed}")
            logger.info(f"Verified: {verified}")
            logger.info(f"Elapsed time: {elapsed:.2f} seconds")
            logger.info(f"Speed: {len(embeddings) / elapsed:.2f} items/second")
            
            if failed > 0:
                logger.warning(f"\n⚠️ {failed} items failed to upload")
                logger.info("Check failed_items for details")
            
            if verified:
                logger.info("\n✅ MIGRATION SUCCESSFUL!")
            else:
                logger.warning("\n⚠️ Verification failed - please check manually")
            
            return verified
        
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            raise


# ==========================================
# COMMAND LINE INTERFACE
# ==========================================

def main():
    parser = argparse.ArgumentParser(
        description='Migrate embeddings from JSON to Supabase'
    )
    parser.add_argument(
        '--input',
        default='vault_embeddings.json',
        help='Path to embeddings JSON file'
    )
    parser.add_argument(
        '--vault',
        default='vault.txt',
        help='Path to vault text file'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for uploads'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without actually updating database'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify migration after completion'
    )
    
    args = parser.parse_args()
    
    # Run migration
    migrator = SupabaseMigrator(dry_run=args.dry_run)
    success = migrator.run(
        embeddings_json=args.input,
        vault_file=args.vault,
        batch_size=args.batch_size
    )
    
    # Report results
    exit_code = 0 if success else 1
    exit(exit_code)


if __name__ == "__main__":
    main()
```

---

## 📋 Step 2: สร้าง Verification Script

สร้างไฟล์: `scripts/verify_migration.py`

```python
"""
Verify Migration Results
========================

Usage:
    python scripts/verify_migration.py --detailed
    python scripts/verify_migration.py --compare
"""

import os
import json
import logging
import argparse
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from supabase import create_client, Client
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class MigrationVerifier:
    """Verify that migration was successful"""
    
    def __init__(self):
        self.client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    def verify_tables(self) -> bool:
        """Verify all required tables exist"""
        logger.info("Verifying tables...")
        
        try:
            tables = ['documents', 'embeddings', 'conversation_history']
            for table in tables:
                result = self.client.table(table).select('id').limit(1).execute()
                logger.info(f"✅ Table '{table}' exists")
            
            return True
        except Exception as e:
            logger.error(f"❌ Table verification failed: {e}")
            return False
    
    def verify_vector_function(self) -> bool:
        """Verify pgvector functions exist"""
        logger.info("Verifying pgvector functions...")
        
        try:
            # Test match_embeddings function
            dummy_embedding = [0.1] * 1024
            result = self.client.rpc('match_embeddings', {
                'query_embedding': dummy_embedding,
                'match_threshold': 0.5,
                'match_count': 1
            }).execute()
            
            logger.info("✅ match_embeddings function works")
            return True
        except Exception as e:
            logger.error(f"❌ Function verification failed: {e}")
            return False
    
    def count_embeddings(self) -> int:
        """Count total embeddings in database"""
        try:
            result = self.client.table('embeddings').select('id').execute()
            count = len(result.data) if result.data else 0
            logger.info(f"Total embeddings in database: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting embeddings: {e}")
            return 0
    
    def compare_with_original(self, json_path: str) -> bool:
        """Compare database count with original JSON"""
        logger.info("Comparing with original JSON...")
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                original_count = len(data.get('embeddings', []))
            
            db_count = self.count_embeddings()
            
            logger.info(f"Original JSON embeddings: {original_count}")
            logger.info(f"Database embeddings: {db_count}")
            
            if original_count == db_count:
                logger.info("✅ Counts match!")
                return True
            else:
                logger.warning(f"⚠️ Mismatch: {db_count} vs {original_count}")
                return False
        
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            return False
    
    def test_search(self) -> bool:
        """Test vector similarity search"""
        logger.info("Testing vector similarity search...")
        
        try:
            # Get first embedding from database
            result = self.client.table('embeddings').select('embedding').limit(1).execute()
            
            if not result.data:
                logger.warning("No embeddings in database to test search")
                return False
            
            test_embedding = result.data[0]['embedding']
            
            # Perform search
            search_result = self.client.rpc('match_embeddings', {
                'query_embedding': test_embedding,
                'match_threshold': 0.0,
                'match_count': 5
            }).execute()
            
            count = len(search_result.data) if search_result.data else 0
            logger.info(f"✅ Search returned {count} results")
            
            return count > 0
        
        except Exception as e:
            logger.error(f"Search test failed: {e}")
            return False
    
    def run_full_verification(self, json_path: str = None) -> bool:
        """Run all verification checks"""
        logger.info("=" * 60)
        logger.info("MIGRATION VERIFICATION REPORT")
        logger.info("=" * 60)
        
        checks = [
            ("Tables", self.verify_tables()),
            ("Vector Functions", self.verify_vector_function()),
            ("Vector Search", self.test_search()),
        ]
        
        if json_path and os.path.exists(json_path):
            checks.append(("JSON Comparison", self.compare_with_original(json_path)))
        
        self.count_embeddings()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for _, result in checks if result)
        total = len(checks)
        
        for name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status}: {name}")
        
        logger.info(f"\nTotal: {passed}/{total} checks passed")
        
        return passed == total


def main():
    parser = argparse.ArgumentParser(description='Verify migration')
    parser.add_argument('--compare', default='vault_embeddings.json',
                        help='Compare with original JSON')
    
    args = parser.parse_args()
    
    verifier = MigrationVerifier()
    success = verifier.run_full_verification(args.compare)
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

---

## 🏃 Step 3: การรัน Migration

### สำหรับการ Test (Dry Run):

```bash
python scripts/migrate_to_supabase.py --dry-run
```

### สำหรับการแท้จริง:

```bash
# ปกติ
python scripts/migrate_to_supabase.py

# กับ batch size ที่กำหนด
python scripts/migrate_to_supabase.py --batch-size 200

# กับ verification
python scripts/migrate_to_supabase.py --verify
```

### Verify ผลการ Migration:

```bash
python scripts/verify_migration.py --compare vault_embeddings.json
```

---

## ⚠️ Tips และ Best Practices

### 1. **Backup ข้อมูลเดิมก่อน**
```bash
cp vault_embeddings.json vault_embeddings.backup.json
cp vault.txt vault.backup.txt
```

### 2. **ทำการทดสอบ Dry Run ก่อน**
```bash
python scripts/migrate_to_supabase.py --dry-run
```

### 3. **Monitor Logs**
logs จะถูกบันทึกไปยัง: `logs/migration_YYYYMMDD_HHMMSS.log`

### 4. **Batch Size Tuning**
- ถ้า ขาด timeout ลอง batch size ที่เล็กลง (50-75)
- ถ้าความเร็วช้า ลองเพิ่ม batch size (150-200)

### 5. **Network Issues**
script มี retry mechanism ที่ใช้ exponential backoff:
- Attempt 1: ทันทีการพยายาม
- Attempt 2: รอ 2 วินาที
- Attempt 3: รอ 4 วินาที

---

## 🐛 Troubleshooting

### ❌ "Failed to upload batch"
- ตรวจสอบ SUPABASE_KEY มีสิทธิ์เขียนข้อมูล
- ลองลดขนาด batch size

### ❌ "Count mismatch"
- ตรวจสอบความล้มเหลวของ batch ในขั้นตอนอัปโหลด
- เรียกใช้ `verify_migration.py` เพื่อตรวจสอบรายละเอียด

### ❌ "Vector dimension mismatch"
- ตรวจสอบว่า embeddings จาก `mxbai-embed-large` มี 1024 dimensions
- Table schema ต้องมี `VECTOR(1024)`

---

**Next Step:** Phase 3 - ปรับปรุง Application Code
