"""
LLM Service
Handles interactions with Large Language Models for summarization and explanations
"""
import hashlib
import json
from typing import Optional, Dict
from openai import OpenAI
import google.generativeai as genai
from loguru import logger
from cachetools import LRUCache
from app.core.config import settings

class LLMService:
    """Service for LLM interactions - Optimized for Cloud Deployment"""
    
    def __init__(self):
        """Initialize LLM service (Supports Gemini and OpenAI)"""
        self.openai_client = None
        self.gemini_model = None
        self.model = settings.LLM_MODEL
        
        # LRU caches for LLM responses (avoid redundant API calls)
        self._summary_cache = LRUCache(maxsize=200)
        self._explanation_cache = LRUCache(maxsize=500)
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Initialize Gemini (Preferred for Render/Free Deployment)
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("Gemini client initialized successfully (Primary)")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")

        # Initialize OpenAI (Secondary/Fallback)
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully (Secondary)")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        if not self.gemini_model and not self.openai_client:
            logger.warning("No LLM API keys configured. AI features will be limited.")
    
    @property
    def is_available(self) -> bool:
        """Check if any LLM backend is available"""
        return bool(self.gemini_model or self.openai_client)
    
    def _call_llm(self, prompt: str, system_instruction: str = "You are a professional assistant.", max_tokens: int = 500) -> Optional[str]:
        """Internal helper to call available LLM (Gemini first, then OpenAI)"""
        # Try Gemini
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(
                    f"{system_instruction}\n\n{prompt}",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.3
                    )
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini call failed: {e}")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI fallback failed: {e}")
                
        return None

    def summarize_resume(self, resume_text: str) -> str:
        """
        Generate a summary of the resume using LLM
        """
        # Check cache first
        cache_key = hashlib.md5(resume_text[:3000].encode('utf-8')).hexdigest()
        if cache_key in self._summary_cache:
            self._cache_hits += 1
            return self._summary_cache[cache_key]
        
        self._cache_misses += 1
        
        prompt = f"""Summarize the following resume in 2-3 sentences, highlighting:
1. Key skills and expertise
2. Years of experience and career level
3. Notable achievements or projects

Resume:
{resume_text[:3000]}
"""
        result = self._call_llm(prompt, "You are a professional resume analyst.")
        
        if result:
            self._summary_cache[cache_key] = result
            return result
        
        # Final fallback: simple truncation
        return resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
    
    def normalize_job_title(self, title: str) -> str:
        """Normalize job title using LLM"""
        prompt = f"Normalize the following job title to a standard format. Return only the normalized title. Job Title: {title}"
        result = self._call_llm(prompt, "You are a job title normalizer.", max_tokens=50)
        return result if result else title.title()
    
    def generate_match_explanation(self, candidate_data: Dict, job_data: Dict, 
                                   match_scores: Dict) -> str:
        """
        Generate human-readable explanation for why a candidate matches a job
        """
        overall_score = match_scores.get('overall_score', 0)
        semantic_sim = match_scores.get('semantic_similarity', 0)
        skill_overlap = match_scores.get('skill_overlap_score', 0)
        exp_alignment = match_scores.get('experience_alignment', 0)

        # Check cache
        cache_input = f"{overall_score:.2f}-{semantic_sim:.2f}-{skill_overlap:.2f}-{exp_alignment:.2f}"
        cache_key = hashlib.md5(cache_input.encode('utf-8')).hexdigest()
        if cache_key in self._explanation_cache:
            self._cache_hits += 1
            return self._explanation_cache[cache_key]
        
        self._cache_misses += 1
        
        fit_level = "PERFECT FIT" if overall_score >= 0.9 else "EXCELLENT FIT" if overall_score >= 0.8 else "GOOD FIT" if overall_score >= 0.6 else "POTENTIAL FIT"
        
        prompt = f"""You are a senior recruitment auditor. Assess the fit between this candidate and the job.
Your response MUST start with: "**This candidate is a {fit_level} for this role.**"
Then, provide a 1-2 sentence professional summary of why they fit based on:
- Skills matched: {skill_overlap:.0%}
- Experience matched: {exp_alignment:.0%}
- Role similarity: {semantic_sim:.0%}

Candidate Profile: {', '.join(candidate_data.get('skills', [])[:10])}
Job Requirements: {job_data.get('title')} ({', '.join(job_data.get('required_skills', [])[:10])})
"""
        result = self._call_llm(prompt, "You are a senior technical recruiter.")
        
        if result:
            self._explanation_cache[cache_key] = result
            return result
        
        return f"Overall Fit: {overall_score:.1%}. This assessment is based on skill set overlap and experience matching."

    def generate_outreach_message(self, candidate_name: str, job_title: str, company: str, 
                                 match_explanation: str) -> str:
        """Generate a personalized outreach message"""
        prompt = f"Draft a professional outreach email to {candidate_name} for the {job_title} role at {company} based on this fit analysis: {match_explanation}. Max 150 words."
        result = self._call_llm(prompt, "You are a technical recruiter.")
        return result if result else f"Hi {candidate_name}, I saw your profile and think you'd be a great fit for the {job_title} role!"

    def generate_job_description(self, title: str, key_points: str) -> str:
        """Generate a full job description from a title and few points"""
        prompt = f"Create a job description for Title: {title}. Key Points: {key_points}. Include About Role, Responsibilities, Requirements."
        result = self._call_llm(prompt, "You are a professional HR copywriter.", max_tokens=600)
        return result if result else f"Role: {title}\n\nKey Points:\n{key_points}"

    def generate_interview_questions(self, candidate_skills: list, job_requirements: list, job_title: str) -> list:
        """Generate tailored interview questions"""
        prompt = f"Generate 5 technical interview questions for {job_title}. Job Requirements: {', '.join(job_requirements[:5])}. Candidate Skills: {', '.join(candidate_skills[:5])}. Return ONLY a JSON list of strings."
        result = self._call_llm(prompt, "You are a hiring manager. Return ONLY a valid JSON list of strings.")
        
        try:
            # Simple cleanup for Gemini's output
            if result:
                clean_json = result
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
                data = json.loads(clean_json)
                if isinstance(data, list): return data
                if isinstance(data, dict) and "questions" in data: return data["questions"]
        except:
            pass
            
        return ["Explain your background in " + job_title, "Tell me about your tech stack."]

    def extract_skills_categorized(self, text: str) -> Dict[str, list]:
        """Extract categorized skills using LLM fallback"""
        prompt = f"""Extract professional skills from the text categorized into:
1. Technical
2. Software & Tools
3. Leadership & Management
4. Communication & Interpersonal
5. Industry Knowledge

Text: {text[:3000]}
Return ONLY a JSON object with these keys and lists as values."""
        
        result = self._call_llm(prompt, "You are an HR assistant. Return ONLY valid JSON.", max_tokens=800)
        
        try:
            if result:
                clean_json = result
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                
                data = json.loads(clean_json)
                cats = ["Technical", "Software & Tools", "Leadership & Management", "Communication & Interpersonal", "Industry Knowledge"]
                return {cat: (data.get(cat, []) if isinstance(data.get(cat, []), list) else []) for cat in cats}
        except:
            pass
            
        return {}
