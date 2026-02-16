import pdfplumber
import os

def test_extract_plumber(file_path):
    print(f"Testing extraction with pdfplumber on: {file_path}")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"Total Pages: {len(pdf.pages)}")
            
            # Extract text from the first page
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            if text:
                print("\n--- First Page Content (Start) ---")
                print(text)
                print("--- First Page Content (End) ---")
            else:
                print("\n[Warning] First page is empty or contains no extractable text.")
                
            # Try a random page in the middle just in case the first page is cover image
            if len(pdf.pages) > 10:
                middle_page = pdf.pages[10]
                text_mid = middle_page.extract_text()
                print("\n--- Page 11 Content (Start) ---")
                print(text_mid[:500] if text_mid else "[Empty]") 
                print("--- Page 11 Content (End) ---")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_extract_plumber("ThaiSignLanguageBook_1.pdf")
