"""
NLP Processing Service
Handles text preprocessing, NER, skill extraction, and embeddings
"""
import hashlib
import re
import nltk
import threading
from typing import List, Dict, Optional
# import spacy (removed from top-level to speed up build)
import httpx
from loguru import logger
from cachetools import LRUCache
from app.core.config import settings
import os

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag

# Import categorized skill database
from app.services.skill_categories import (
    SKILL_CATEGORIES, 
    SKILL_TO_CATEGORY, 
    SKILL_SYNONYMS,
    SKILL_HIERARCHY,
    TRANSFERABLE_SKILLS
)

class NLPProcessor:
    """Natural Language Processing for resume and job description analysis"""
    
    def __init__(self, spacy_model: str = "en_core_web_sm", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize NLP processor
        
        Args:
            spacy_model: SpaCy model name
            embedding_model: Sentence transformer model name
        """
        self._embedding_model_name = embedding_model
        self._spacy_model_name = spacy_model
        self.nlp = None
        self.embedding_model = None
        self._initialized = False
        self._lock = threading.Lock()
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # LRU cache for embeddings (max 500 unique texts)
        self._embedding_cache = LRUCache(maxsize=500)
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Use hierarchies from skill_categories
        self.skill_keywords = SKILL_CATEGORIES
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase
        text = text.lower().strip()
        return text
    
    def _ensure_initialized(self):
        """Lazy load models on first use"""
        with self._lock:
            if self._initialized:
                return
            
            logger.info("Initializing NLP models (this may take a moment)...")
            try:
                if settings.ENVIRONMENT == "production":
                    logger.warning("Production mode: Skipping heavy spaCy model load.")
                    self.nlp = None
                else:
                    import spacy
                    self.nlp = spacy.load(self._spacy_model_name)
            except Exception as e:
                logger.warning(f"SpaCy model {self._spacy_model_name} not available: {e}.")
                self.nlp = None
            
            try:
                if settings.ENVIRONMENT == "production":
                    logger.info("Production mode: Using Cloud Gemini for embeddings (Torch disabled).")
                    self.embedding_model = "cloud"
                else:
                    from sentence_transformers import SentenceTransformer
                    self.embedding_model = SentenceTransformer(self._embedding_model_name)
                    logger.info("Local mode: SentenceTransformer loaded.")
            except Exception as e:
                logger.warning(f"Failed to load local embedding model: {e}. Falling back to Cloud API.")
                self.embedding_model = "cloud"
            
            self._initialized = True
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        tokens = word_tokenize(text)
        return [token.lower() for token in tokens if token.isalnum()]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using SpaCy NER
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with entity types and values
        """
        self._ensure_initialized()
        
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],  # Locations
            'DATE': [],
            'MONEY': []
        }
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)
        else:
            # Simple regex-based fallback for production if spaCy is missing
            # PERSON (Capitalized words followed by space and capitalized word)
            names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
            entities['PERSON'] = names[:5]
            
            # GPE (Locations - very simple check)
            locations = re.findall(r'\b(New York|San Francisco|London|Berlin|India|USA|UK|Remote)\b', text, re.I)
            entities['GPE'] = list(set(locations))
            
            # Dates
            dates = re.findall(r'\b\d{4}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b', text)
            entities['DATE'] = [d[0] if isinstance(d, tuple) else d for d in dates]
            
        return entities
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted skills
        """
        self._ensure_initialized()
        text_lower = text.lower()
        found_skills = []
        
        # Prioritize predefined keywords
        high_confidence_skills = []
        
        # Check standard categories
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                # regex to match whole words only
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    # Use canonical name if synonym
                    canonical_name = SKILL_SYNONYMS.get(skill.lower(), skill)
                    high_confidence_skills.append(canonical_name)
                    
        # Check transferable skills keys (Roles)
        for role in TRANSFERABLE_SKILLS.keys():
            if re.search(r'\b' + re.escape(role.lower()) + r'\b', text_lower):
                if role not in high_confidence_skills:
                    high_confidence_skills.append(role)
        
        # Use NER for additional skill extraction (lower confidence)
        inferred_skills = []
        if self.nlp:
            doc = self.nlp(text)
            # Look for noun phrases that might be skills
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.strip()
                chunk_lower = chunk_text.lower()
                
                # Filter noise
                if (len(chunk_lower.split()) <= 3 and 
                    len(chunk_text) >= 2 and 
                    chunk_lower.split()[0] not in self.stop_words):
                    
                    # Normalize
                    clean_chunk = re.sub(r'\s*\(.*?\)', '', chunk_text).strip()
                    skill_name = SKILL_SYNONYMS.get(clean_chunk.lower(), clean_chunk.title())
                    
                    if skill_name not in high_confidence_skills:
                        inferred_skills.append(skill_name)
        
        # Combine and deduplicate
        all_skills = list(dict.fromkeys(high_confidence_skills + inferred_skills))
        
        # Add inferred transferable skills
        all_skills = self.infer_skills(all_skills)
        
        return all_skills
    
    def infer_skills(self, existing_skills: List[str]) -> List[str]:
        """
        Infer additional skills based on transferable skills map
        e.g., "Customer Support" -> ["Communication", "Problem Solving"]
        
        Args:
            existing_skills: List of already identified skills/roles
            
        Returns:
            Updated list of skills
        """
        inferred = []
        existing_lower = [s.lower() for s in existing_skills]
        
        for base_skill, related_skills in TRANSFERABLE_SKILLS.items():
            if base_skill.lower() in existing_lower:
                for related in related_skills:
                    if related not in existing_skills:
                        inferred.append(related)
        
        return list(dict.fromkeys(existing_skills + inferred))
    
    def infer_role_details(self, title: str, text: str) -> Dict[str, any]:
        """
        Infer seniority and scope from role title and description
        
        Args:
            title: Job title or candidate previous role
            text: Contextual text (description)
            
        Returns:
            Dictionary with seniority level and scope
        """
        text_lower = (title + " " + text).lower()
        
        details = {
            "seniority": "Junior/Intermediate",
            "is_managerial": False,
            "years_hint": 0
        }
        
        # Seniority markers
        senior_markers = ["senior", "sr", "lead", "architect", "principal", "staff", "head of", "director", "vp"]
        junior_markers = ["junior", "jr", "entry", "intern", "associate", "graduate"]
        
        if any(marker in title.lower() for marker in senior_markers):
            details["seniority"] = "Senior+"
        elif any(marker in title.lower() for marker in junior_markers):
            details["seniority"] = "Entry-level"
            
        # Management markers
        mgmt_markers = ["manager", "managing", "director", "lead", "head of", "vp", "chief"]
        if any(marker in title.lower() for marker in mgmt_markers):
            details["is_managerial"] = True
            
        # Look for years in text
        years_match = re.search(r'(\d+)\+?\s*years?', text_lower)
        if years_match:
            details["years_hint"] = int(years_match.group(1))
            
        return details
    
    def extract_skills_categorized(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from text and organize them by category
        Performs deep analysis using comprehensive skill database
        
        Args:
            text: Input resume or job description text
            
        Returns:
            Dictionary with categories as keys and lists of found skills as values
        """
        self._ensure_initialized()
        text_lower = text.lower()
        
        # Initialize result structure
        categorized_skills = {category: [] for category in SKILL_CATEGORIES}
        
        # Extract skills from each category
        for category, skills in SKILL_CATEGORIES.items():
            found_skills = []
            for skill in skills:
                # Use word boundary regex for accurate matching
                # Special handling for skills with symbols like C++, .NET, C#
                safe_skill = re.escape(skill.lower())
                if re.search(r'[+#.]$', skill):
                     # If skill ends with a symbol, \b at the end won't work
                     pattern = r'\b' + safe_skill + r'(?!\w)'
                else:
                     pattern = r'\b' + safe_skill + r'\b'
                     
                if re.search(pattern, text_lower):
                    # Check for synonyms and normalize
                    canonical_name = SKILL_SYNONYMS.get(skill.lower(), skill)
                    if canonical_name not in found_skills:
                        found_skills.append(canonical_name)
            
            categorized_skills[category] = found_skills
        
        # Also try to extract additional skills using old method and categorize them
        legacy_skills = self.extract_skills(text)
        for skill in legacy_skills:
            skill_lower = skill.lower()
            # Check if this skill belongs to a category
            if skill_lower in SKILL_TO_CATEGORY:
                category = SKILL_TO_CATEGORY[skill_lower]
                # Add if not already in the list
                if skill not in categorized_skills[category]:
                    categorized_skills[category].append(skill)
        
        return categorized_skills
    
    def generate_embedding(self, text: str) -> list:
        """
        Generate semantic embedding for text with LRU caching.
        
        Args:
            text: Input text
            
        Returns:
            List of floats (embedding vector)
        """
        self._ensure_initialized()
        # Create a hash key for the cache
        cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        if cache_key in self._embedding_cache:
            self._cache_hits += 1
            return self._embedding_cache[cache_key]
        
        self._cache_misses += 1
        
        # 1. Try Cloud Embedding if configured
        if self.embedding_model == "cloud" or not self._is_local_model(self.embedding_model):
            try:
                embedding = self._generate_cloud_embedding(text)
                if embedding:
                    self._embedding_cache[cache_key] = embedding
                    return embedding
            except Exception as e:
                logger.error(f"Cloud embedding error: {e}")

        # 2. Try Local Embedding as fallback (if not in production)
        if self._is_local_model(self.embedding_model):
            try:
                embedding = self.embedding_model.encode(text, convert_to_numpy=True)
                result = embedding.tolist()
                self._embedding_cache[cache_key] = result
                return result
            except Exception as e:
                logger.error(f"Local embedding error: {e}")
        
        # 3. Final Fallback
        return [0.0] * 384

    def _is_local_model(self, model):
        """Check if model is a local SentenceTransformer instance"""
        return not isinstance(model, str)

    def _generate_cloud_embedding(self, text: str) -> Optional[List[float]]:
        """Call Gemini API for embeddings"""
        if not settings.GEMINI_API_KEY:
            return None
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "model": "models/embedding-001",
            "content": {"parts": [{"text": text}]}
        }
        
        try:
            # Note: Using synchronous request for simplicity in this helper, 
            # though async is preferred for high-throughput
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    return res.json().get("embedding", {}).get("values", [])
                else:
                    logger.error(f"Gemini Embedding API Error: {res.status_code} - {res.text}")
        except Exception as e:
            logger.error(f"Network error calling Gemini Embedding: {e}")
        return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[list]:
        """
        Generate embeddings for multiple texts at once (batch processing).
        Uses cache for already-seen texts and batches only new ones.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        self._ensure_initialized()
        if not self.embedding_model:
            return [[0.0] * 384 for _ in texts]
        
        results = [None] * len(texts)
        texts_to_encode = []  # (index, text) pairs for uncached texts
        
        for i, text in enumerate(texts):
            cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
            if cache_key in self._embedding_cache:
                results[i] = self._embedding_cache[cache_key]
                self._cache_hits += 1
            else:
                texts_to_encode.append((i, text, cache_key))
                self._cache_misses += 1
        
        if texts_to_encode:
            batch_texts = [t[1] for t in texts_to_encode]
            batch_embeddings = self.embedding_model.encode(batch_texts, convert_to_numpy=True, batch_size=32)
            
            for j, (orig_idx, text, cache_key) in enumerate(texts_to_encode):
                embedding_list = batch_embeddings[j].tolist()
                self._embedding_cache[cache_key] = embedding_list
                results[orig_idx] = embedding_list
        
        return results
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Return cache hit/miss statistics"""
        total = self._cache_hits + self._cache_misses
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "total": total,
            "hit_rate": f"{(self._cache_hits / total * 100):.1f}%" if total > 0 else "N/A",
            "cache_size": len(self._embedding_cache)
        }
    
    def normalize_job_title(self, title: str) -> str:
        """
        Normalize job title using simple rules
        (Can be enhanced with LLM)
        
        Args:
            title: Job title
            
        Returns:
            Normalized title
        """
        title_lower = title.lower()
        
        # Common normalizations
        normalizations = {
            'software engineer': 'Software Engineer',
            'dev': 'Developer',
            'swe': 'Software Engineer',
            'sde': 'Software Development Engineer'
        }
        
        for key, value in normalizations.items():
            if key in title_lower:
                return value
        
        return title.title()
