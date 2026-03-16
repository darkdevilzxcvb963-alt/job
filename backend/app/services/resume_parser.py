"""
Resume Parsing Service
Handles extraction of text and structured data from PDF and DOCX files
"""
import os
from typing import Dict, Optional
from pathlib import Path
import pdfplumber
from docx import Document
from loguru import logger

# Optional imports for fallback extractors
try:
    import fitz as pymupdf
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

class ResumeParser:
    """Parse resumes from various file formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']
    
    def parse(self, file_path: str) -> Dict[str, any]:
        """
        Parse resume file and extract text
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary with parsed data including text and metadata
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._parse_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _parse_pdf(self, file_path: str) -> Dict[str, any]:
        """Parse PDF file using multiple extraction methods as fallback"""
        full_text = ""
        method_used = "none"
        
        # Method 1: pdfplumber (best for text-based PDFs)
        try:
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            full_text = "\n".join(text_content)
            if full_text.strip():
                method_used = "pdfplumber"
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}: {e}")
        
        # Method 2: PyMuPDF fallback
        if not full_text.strip() and HAS_PYMUPDF:
            try:
                # fitz / pymupdf
                doc = pymupdf.open(file_path)
                text_parts = []
                for page in doc:
                    text = page.get_text()
                    if text:
                        text_parts.append(text)
                doc.close()
                full_text = "\n".join(text_parts)
                if full_text.strip():
                    method_used = "pymupdf"
            except Exception as e:
                logger.warning(f"PyMuPDF failed for {file_path}: {e}")
        
        # Method 3: pypdf (modern replacement for PyPDF2)
        if not full_text.strip() and HAS_PYPDF:
            try:
                reader = pypdf.PdfReader(file_path)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                full_text = "\n".join(text_parts)
                if full_text.strip():
                    method_used = "pypdf"
            except Exception as e:
                logger.warning(f"pypdf failed for {file_path}: {e}")
        
        # Method 4: OCR fallback (for scanned/image PDFs)
        if not full_text.strip() and HAS_OCR:
            try:
                logger.info(f"Attempting OCR for scanned PDF: {file_path}")
                images = convert_from_path(file_path)
                text_parts = []
                for img in images:
                    text = pytesseract.image_to_string(img)
                    if text:
                        text_parts.append(text)
                full_text = "\n".join(text_parts)
                if full_text.strip():
                    method_used = "ocr"
            except Exception as e:
                logger.warning(f"OCR failed for {file_path}: {e}")
        
        if full_text.strip():
            logger.info(f"PDF parsed successfully with {method_used}: {len(full_text)} chars from {file_path}")
        else:
            logger.warning(f"All PDF extraction methods returned empty text for {file_path}. This is likely a scanned/image-based PDF.")
        
        return {
            "text": full_text,
            "file_type": "pdf",
            "extraction_method": method_used
        }
    
    def _parse_docx(self, file_path: str) -> Dict[str, any]:
        """Parse DOCX file"""
        try:
            doc = Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            
            full_text = "\n".join(text_content)
            return {
                "text": full_text,
                "file_type": "docx",
                "paragraphs": len(text_content)
            }
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise


_resume_parser = None

def get_resume_parser():
    """Factory function for ResumeParser"""
    global _resume_parser
    if _resume_parser is None:
        _resume_parser = ResumeParser()
    return _resume_parser

