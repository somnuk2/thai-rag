import PyPDF2
import os

def test_extract(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            print(f"Total Pages: {len(pdf_reader.pages)}")
            first_page_text = pdf_reader.pages[0].extract_text()
            print("--- First Page Content (Start) ---")
            print(repr(first_page_text))
            print("--- First Page Content (End) ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_extract("ThaiSignLanguageBook_1.pdf")
