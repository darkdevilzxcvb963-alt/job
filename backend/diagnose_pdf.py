import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

print("\n--- Testing Imports ---")

try:
    import pdfplumber
    print(f"[OK] pdfplumber imported (version: {pdfplumber.__version__})")
except ImportError as e:
    print(f"[FAIL] pdfplumber could not be imported: {e}")

try:
    import fitz
    print(f"[OK] PyMuPDF (fitz) imported (version: {fitz.__version__})")
except ImportError as e:
    print(f"[FAIL] PyMuPDF (fitz) could not be imported: {e}")

try:
    import PyPDF2
    print(f"[OK] PyPDF2 imported (version: {PyPDF2.__version__})")
except ImportError as e:
    print(f"[FAIL] PyPDF2 could not be imported: {e}")

try:
    import pypdf
    print(f"[OK] pypdf imported (version: {pypdf.__version__})")
except ImportError as e:
    print(f"[FAIL] pypdf could not be imported: {e}")
