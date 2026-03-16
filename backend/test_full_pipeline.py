import sys
import os

# Add the project root to sys.path to import app modules
# CWD is backend
sys.path.append(os.getcwd())

from app.services.resume_parser import ResumeParser
from app.services.nlp_processor import NLPProcessor
from app.core.config import settings

def test_full_extraction():
    parser = ResumeParser()
    nlp = NLPProcessor(
        spacy_model=settings.SPACY_MODEL,
        embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
    )
    
    test_file = r"c:\Users\ADMIN\new-project\uploads\udhayakumar  report.pdf"
    print(f"Testing file: {test_file}")
    
    try:
        parsed = parser.parse(test_file)
        text = parsed.get("text", "")
        print(f"Extracted {len(text)} characters.")
        
        if text:
            skills = nlp.extract_skills_categorized(text)
            total_skills = sum(len(s) for s in skills.values())
            print(f"Extracted {total_skills} skills across categories.")
            for cat, s_list in skills.items():
                if s_list:
                    print(f"  {cat}: {', '.join(s_list[:5])}...")
        else:
            print("No text extracted, cannot extract skills.")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_full_extraction()
