import os
import sys

# Add backend to path
sys.path.append(os.path.abspath('.'))

from app.services.resume_parser import ResumeParser
from app.services.nlp_processor import NLPProcessor
from app.services.llm_service import LLMService

def test_processing():
    parser = ResumeParser()
    nlp = NLPProcessor()
    llm = LLMService()
    
    # Try the most recent file if it exists
    # Try the most recent file if it exists
    # uploads is in the project root, one level up from backend
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(base_dir, 'uploads')
    
    if not os.path.exists(uploads_dir):
        print(f"Uploads directory not found at: {uploads_dir}")
        return

    files = [f for f in os.listdir(uploads_dir) if f.endswith(('.pdf', '.docx'))]
    if not files:
        print("No resumes found in uploads directory.")
        return
    
    test_file = os.path.join(uploads_dir, files[0])
    print(f"Testing with file: {test_file}")
    
    try:
        # 1. Parse
        print("Step 1: Parsing...")
        parsed = parser.parse(test_file)
        text = parsed.get("text", "")
        print(f"Extraction successful! Length: {len(text)} chars.")
        
        # 2. NLP (Skills)
        print("Step 2: Extracting skills...")
        skills = nlp.extract_skills_categorized(text)
        total_skills = sum(len(s) for s in skills.values())
        print(f"Skills extracted: {total_skills}")
        
        # 3. LLM (Summary)
        print("Step 3: Generating summary (LLM)...")
        summary = llm.summarize_resume(text)
        print(f"Summary generated: {summary[:100]}...")
        
        print("\nSUCCESS: Entire pipeline is functional!")
    except Exception as e:
        print(f"\nFAILURE: {str(e)}")

if __name__ == "__main__":
    test_processing()
