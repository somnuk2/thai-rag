import pdfplumber
import re
import os

def process_thai_pdf(file_path, vault_path="vault.txt"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"Processing {file_path} with pdfplumber (Thai support)...")
    
    try:
        all_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + " "
        
        # Basic cleanup
        # Replace multiple spaces/newlines with single space
        clean_text = re.sub(r'\s+', ' ', all_text).strip()
        
        # For Thai, we don't have clear sentence markers like English '.' 
        # but we can use spaces as a proxy or just fixed length chunks.
        # Since the project's RAG uses 1000 chars, let's stick to that but try to break at spaces.
        
        max_chunk_size = 1000
        chunks = []
        
        # Simple chunking by length with space awareness
        while len(clean_text) > 0:
            if len(clean_text) <= max_chunk_size:
                chunks.append(clean_text)
                break
            
            # Find the last space within the limit
            chunk = clean_text[:max_chunk_size]
            last_space = chunk.rfind(' ')
            
            if last_space > 500: # Ensure we don't make too small chunks
                chunks.append(clean_text[:last_space].strip())
                clean_text = clean_text[last_space:].strip()
            else:
                chunks.append(clean_text[:max_chunk_size].strip())
                clean_text = clean_text[max_chunk_size:].strip()
        
        with open(vault_path, "a", encoding="utf-8") as vault_file:
            for chunk in chunks:
                if chunk:
                    vault_file.write(chunk + "\n")
        
        print(f"Successfully processed {file_path}. Added {len(chunks)} chunks to {vault_path}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_thai_pdf("Sign_Language_Language_of_the_Deaf.pdf")
