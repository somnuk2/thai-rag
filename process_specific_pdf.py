import PyPDF2
import re
import os

def process_pdf(file_path, vault_path="vault.txt"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"Processing {file_path}...")
    
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + " "
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip() + " "
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk.strip())
            
            with open(vault_path, "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk + "\n")
            
            print(f"Successfully processed {file_path}. Added {len(chunks)} chunks to {vault_path}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_pdf("ThaiSignLanguageBook_1.pdf")
