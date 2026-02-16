import pdfplumber
import os

file_name = "Sign_Language_Language_of_the_Deaf.pdf"

if not os.path.exists(file_name):
    print(f"Error: {file_name} not found.")
else:
    print(f"Testing extraction with pdfplumber on: {file_name}")
    try:
        with pdfplumber.open(file_name) as pdf:
            print(f"Total Pages: {len(pdf.pages)}")
            
            # Extract text from the first page
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                print("\n--- First Page Content (Start) ---")
                print(text[:1000] if text else "[Empty]")
                print("--- First Page Content (End) ---")
            
            # Try a middle page
            if len(pdf.pages) > 5:
                mid_page = pdf.pages[5]
                text = mid_page.extract_text()
                print("\n--- Page 6 Content (Start) ---") 
                print(text[:1000] if text else "[Empty]")
                print("--- Page 6 Content (End) ---")

    except Exception as e:
        print(f"An error occurred: {e}")
