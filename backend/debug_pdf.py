import os
import pdfplumber
import pypdf
import fitz
import sys

upload_dir = r"c:\Users\ADMIN\new-project\uploads"
files = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.endswith('.pdf')]

if not files:
    print("No PDF files found in uploads.")
    sys.exit()

for file_path in files:
    print(f"\n{'='*50}")
    print(f"Analyzing file: {os.path.basename(file_path)}")
    print(f"File size: {os.path.getsize(file_path)} bytes")

    # Try fitz as it is the most reliable
    try:
        doc = fitz.open(file_path)
        print(f"Pages: {len(doc)}")
        for i, page in enumerate(doc):
            text = page.get_text()
            if text:
                print(f"Page {i+1} text length: {len(text)}")
                print(f"Sample: {text[:50].strip()}...")
            else:
                print(f"Page {i+1}: No text extracted")
            
            images = page.get_images()
            if images:
                print(f"Page {i+1} has {len(images)} images.")
        doc.close()
    except Exception as e:
        print(f"Error analyzing {os.path.basename(file_path)}: {e}")
