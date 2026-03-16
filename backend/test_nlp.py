import sys
import os
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("DEBUG: Importing settings...")
from app.core.config import settings

print("DEBUG: Importing NLPProcessor...")
from app.services.nlp_processor import NLPProcessor

print("DEBUG: Initializing NLPProcessor...")
try:
    nlp = NLPProcessor(
        spacy_model=settings.SPACY_MODEL,
        embedding_model=settings.SENTENCE_TRANSFORMER_MODEL
    )
    print("✓ NLPProcessor initialized.")
except BaseException as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
