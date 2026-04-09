"""
LLM Service
Handles interactions with Large Language Models for summarization and explanations
"""
import hashlib
from typing import Optional, Dict
from openai import OpenAI
from loguru import logger
from cachetools import LRUCache
from app.core.config import settings

class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        """Initialize LLM service"""
        self.client = None
        self.model = settings.LLM_MODEL
        
        # LRU caches for LLM responses (avoid redundant API calls)
        self._summary_cache = LRUCache(maxsize=200)
        self._explanation_cache = LRUCache(maxsize=500)
        self._cache_hits = 0
        self._cache_misses = 0
        
        try:
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not configured. LLM features will be limited.")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}. LLM features will be limited.")
    
    def summarize_resume(self, resume_text: str) -> str:
        """
        Generate a summary of the resume using LLM
        
        Args:
            resume_text: Full resume text
            
        Returns:
            Generated summary
        """
        if not self.client:
            # Fallback to simple truncation
            return resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        
        # Check cache first
        cache_key = hashlib.md5(resume_text[:3000].encode('utf-8')).hexdigest()
        if cache_key in self._summary_cache:
            self._cache_hits += 1
            return self._summary_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            prompt = f"""Summarize the following resume in 2-3 sentences, highlighting:
1. Key skills and expertise
2. Years of experience and career level
3. Notable achievements or projects

Resume:
{resume_text[:3000]}  # Limit input size
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional resume analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            result = response.choices[0].message.content.strip()
            self._summary_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Error generating resume summary: {e}")
            return resume_text[:500] + "..."
    
    def normalize_job_title(self, title: str) -> str:
        """
        Normalize job title using LLM
        
        Args:
            title: Job title to normalize
            
        Returns:
            Normalized job title
        """
        if not self.client:
            return title.title()
        
        try:
            prompt = f"""Normalize the following job title to a standard format.
Return only the normalized title, nothing else.

Job Title: {title}
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a job title normalizer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error normalizing job title: {e}")
            return title.title()
    
    def generate_match_explanation(self, candidate_data: Dict, job_data: Dict, 
                                   match_scores: Dict) -> str:
        """
        Generate human-readable explanation for why a candidate matches a job
        
        Args:
            candidate_data: Candidate information
            job_data: Job information
            match_scores: Matching scores
            
        Returns:
            Explanation text
        """
        overall_score = match_scores.get('overall_score', 0)
        semantic_sim = match_scores.get('semantic_similarity', 0)
        skill_overlap = match_scores.get('skill_overlap_score', 0)
        exp_alignment = match_scores.get('experience_alignment', 0)

        if not self.client:
            # Fallback explanation
            return f"Overall Fit: {overall_score:.1%}. " \
                   f"This assessment is based on a {semantic_sim:.0%} semantic alignment, " \
                   f"{skill_overlap:.0%} skill set overlap, and {exp_alignment:.0%} experience matching."
        
        # Check cache
        cache_input = f"{overall_score:.2f}-{semantic_sim:.2f}-{skill_overlap:.2f}-{exp_alignment:.2f}"
        cache_key = hashlib.md5(cache_input.encode('utf-8')).hexdigest()
        if cache_key in self._explanation_cache:
            self._cache_hits += 1
            return self._explanation_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            # Special indicator for high-fit candidates
            fit_level = "PERFECT FIT" if overall_score >= 0.9 else "EXCELLENT FIT" if overall_score >= 0.8 else "GOOD FIT" if overall_score >= 0.6 else "POTENTIAL FIT"
            
            prompt = f"""You are a senior recruitment auditor. Assess the fit between this candidate and the job.
Your response MUST start with a clear, bold fit assessment sentence like: "**This candidate is a {fit_level} for this role.**"
Then, provide a 1-2 sentence explanation of the 'how much' they fit based on these specific alignment metrics:
- Skills matched: {skill_overlap:.0%}
- Experience matched: {exp_alignment:.0%}
- Role similarity: {semantic_sim:.0%}

Do NOT include numerical percentages in your generated text (they are already displayed in the UI).
Focus on a professional summary of the candidate's suitability.

Candidate Profile: {', '.join(candidate_data.get('skills', [])[:12])} ({candidate_data.get('experience_years', 'N/A')} yrs exp)
Job Requirements: {job_data.get('title')} ({', '.join(job_data.get('required_skills', [])[:12])})
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior technical recruiter providing quantitative and qualitative fit analysis. Focus on the 'why' behind the score."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.4
            )
            result = response.choices[0].message.content.strip()
            self._explanation_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Error generating match explanation: {e}")
            return f"Strategic Fit Score: {overall_score:.1%}. The candidate shows a {skill_overlap:.0%} skill match and {exp_alignment:.0%} experience alignment."

    def generate_outreach_message(self, candidate_name: str, job_title: str, company: str, 
                                 match_explanation: str) -> str:
        """Generate a personalized outreach message"""
        if not self.client:
            return f"Hi {candidate_name}, I saw your profile and think you'd be a great fit for the {job_title} role at {company}!"
            
        try:
            prompt = f"""Draft a professional, warm, and personalized outreach email to a candidate.
Candidate: {candidate_name}
Job: {job_title} at {company}
Fit Analysis: {match_explanation}

The email should be brief (max 150 words), cite specific reasons from the Fit Analysis why they are a good match, and end with a call to action to chat.
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical recruiter known for personalized, non-spammy outreach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating outreach: {e}")
            return f"Hi {candidate_name}, I'm reaching out regarding the {job_title} role at {company}. Your background looks interesting!"

    def generate_job_description(self, title: str, key_points: str) -> str:
        """Generate a full job description from a title and few points"""
        if not self.client:
            return f"Job Title: {title}\nKey Requirements: {key_points}"
            
        try:
            prompt = f"""Create a professional and engaging job description for the following role:
Title: {title}
Key Points: {key_points}

Include sections for: About the Role, Responsibilities, and Requirements. Use a modern, inclusive tone.
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional HR copywriter."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating JD: {e}")
            return f"Role: {title}\n\nKey Points:\n{key_points}"

    def generate_interview_questions(self, candidate_skills: list, job_requirements: list, job_title: str) -> list:
        """Generate tailored interview questions based on candidate skills and job requirements"""
        if not self.client:
            return ["Tell me about your experience with " + (job_requirements[0] if job_requirements else "this role"), 
                    "How do your skills align with " + job_title + "?"]
            
        try:
            prompt = f"""Generate 5 tailored technical and behavioral interview questions for a candidate applying for the role of {job_title}.
Target Job Requirements: {', '.join(job_requirements[:10])}
Candidate Skills: {', '.join(candidate_skills[:10])}
 
Focus on the intersection of what the job needs and what the candidate knows, as well as probing for any missing critical skills.
Return ONLY a JSON list of strings."""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical hiring manager. Return output as a valid JSON list of strings."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5,
                response_format={"type": "json_object"} if "gpt-4" in self.model or "gpt-3.5" in self.model else None
            )
            import json
            content = response.choices[0].message.content.strip()
            # If it's a json_object but we asked for a list, it might be wrapped
            data = json.loads(content)
            if isinstance(data, dict):
                # Look for a list in the dictionary
                for val in data.values():
                    if isinstance(val, list):
                        return val
            return data if isinstance(data, list) else [content]
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return ["Explain your background in " + job_title, "What is your experience with the required tech stack?"]

    def extract_skills_categorized(self, text: str) -> Dict[str, list]:
        """
        Extract categorized skills from resume/job text using LLM.
        Great fallback when local NLTK/SpaCy parser yields too few results.
        """
        if not self.client:
            return {}
            
        try:
            # We use a structured prompt to get precisely what the NLPProcessor expects
            prompt = f"""Analyze the provided text (resume or job description) and extract professional skills categorized into exactly these 5 groups:
1. Technical (Programming, Frameworks, Architecture, etc.)
2. Software & Tools (IDEs, Version Control, SaaS tools, etc.)
3. Leadership & Management (Team leading, Budgeting, Strategy, etc.)
4. Communication & Interpersonal (Negotiation, Public Speaking, Customer Service, etc.)
5. Industry Knowledge (FinTech, Healthcare, Logistics, etc.)

Text:
{text[:4000]}

Return only a JSON object where keys are the category names and values are lists of extracted skill strings.
Example: {{"Technical": ["Python", "React"], "Software & Tools": ["Git", "VS Code"], ...}}
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant specialized in skill taxonomy. Return output in strict JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2,
                response_format={"type": "json_object"} if "gpt-4" in self.model or "gpt-3.5" in self.model else None
            )
            import json
            content = response.choices[0].message.content.strip()
            data = json.loads(content)
            
            # Ensure all keys exist
            cats = ["Technical", "Software & Tools", "Leadership & Management", "Communication & Interpersonal", "Industry Knowledge"]
            for cat in cats:
                if cat not in data:
                    data[cat] = []
                elif not isinstance(data[cat], list):
                    # Handle cases where LLM might return a single string or non-list
                    data[cat] = [str(data[cat])] if data[cat] else []
            
            return data
        except Exception as e:
            logger.error(f"Error in LLM categorized skill extraction: {e}")
            return {}
