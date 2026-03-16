"""
Resume Scorer Service
Evaluates resume quality for ATS compatibility and completeness
"""
import re
from typing import Dict, List, Optional
from loguru import logger


class ResumeScorer:
    """Scores resumes for ATS compatibility, completeness, and quality"""
    
    # Expected resume sections
    EXPECTED_SECTIONS = {
        'contact': ['email', 'phone', 'address', 'linkedin', 'github', 'portfolio'],
        'summary': ['summary', 'objective', 'about', 'profile', 'overview'],
        'experience': ['experience', 'work history', 'employment', 'professional experience', 'work experience'],
        'education': ['education', 'academic', 'qualifications', 'degree', 'university'],
        'skills': ['skills', 'technical skills', 'competencies', 'technologies', 'expertise'],
        'projects': ['projects', 'personal projects', 'portfolio', 'key projects'],
        'certifications': ['certifications', 'certificates', 'licenses', 'accreditations'],
    }
    
    # Section weights for the overall score
    SECTION_WEIGHTS = {
        'contact': 0.10,
        'summary': 0.10,
        'experience': 0.25,
        'education': 0.15,
        'skills': 0.20,
        'projects': 0.10,
        'certifications': 0.10,
    }
    
    def score_resume(self, resume_text: str, target_job_skills: List[str] = None) -> Dict:
        """
        Score a resume on multiple dimensions
        
        Args:
            resume_text: Parsed resume text
            target_job_skills: Optional target job skills for keyword matching
            
        Returns:
            Dictionary with scores and feedback
        """
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                'overall_score': 0.0,
                'section_scores': {},
                'keyword_score': 0.0,
                'formatting_score': 0.0,
                'length_score': 0.0,
                'feedback': ['Resume text is too short or empty. Please upload a valid resume.'],
                'grade': 'F'
            }
        
        text_lower = resume_text.lower()
        
        # 1. Section detection scores
        section_scores = self._score_sections(text_lower)
        
        # 2. Keyword relevance (against target job if provided)
        keyword_score = self._score_keywords(text_lower, target_job_skills) if target_job_skills else 0.7
        
        # 3. Formatting quality
        formatting_score = self._score_formatting(resume_text)
        
        # 4. Length appropriateness
        length_score = self._score_length(resume_text)
        
        # 5. Action verbs and quantification
        impact_score = self._score_impact_language(text_lower)
        
        # Calculate weighted overall score
        sections_avg = sum(
            section_scores.get(section, {}).get('score', 0) * weight
            for section, weight in self.SECTION_WEIGHTS.items()
        )
        
        overall = (
            sections_avg * 0.35 +
            keyword_score * 0.25 +
            formatting_score * 0.15 +
            length_score * 0.10 +
            impact_score * 0.15
        )
        
        # Generate feedback
        feedback = self._generate_feedback(section_scores, keyword_score, 
                                            formatting_score, length_score, impact_score)
        
        # Grade
        grade = self._score_to_grade(overall)
        
        return {
            'overall_score': round(overall, 3),
            'section_scores': section_scores,
            'keyword_score': round(keyword_score, 3),
            'formatting_score': round(formatting_score, 3),
            'length_score': round(length_score, 3),
            'impact_score': round(impact_score, 3),
            'feedback': feedback,
            'grade': grade
        }
    
    def _score_sections(self, text_lower: str) -> Dict:
        """Score presence and quality of resume sections"""
        scores = {}
        
        for section_name, keywords in self.EXPECTED_SECTIONS.items():
            found = False
            for kw in keywords:
                # Look for section headers (word at start of line or after newline)
                pattern = r'(?:^|\n)\s*' + re.escape(kw)
                if re.search(pattern, text_lower):
                    found = True
                    break
                # Also check for the keyword appearing anywhere
                if kw in text_lower:
                    found = True
                    break
            
            scores[section_name] = {
                'found': found,
                'score': 1.0 if found else 0.0,
                'label': section_name.title()
            }
        
        return scores
    
    def _score_keywords(self, text_lower: str, target_skills: List[str]) -> float:
        """Score keyword match against target job skills"""
        if not target_skills:
            return 0.7
        
        found = 0
        for skill in target_skills:
            if skill.lower() in text_lower:
                found += 1
        
        return found / len(target_skills) if target_skills else 0.7
    
    def _score_formatting(self, text: str) -> float:
        """Score formatting quality"""
        score = 0.5  # Base score
        
        # Check for bullet points
        if re.search(r'[•\-\*]\s', text):
            score += 0.15
        
        # Check for consistent capitalization in headers
        lines = text.split('\n')
        header_lines = [l.strip() for l in lines if l.strip() and len(l.strip()) < 50 and l.strip().isupper() or l.strip().istitle()]
        if header_lines:
            score += 0.15
        
        # Check for dates (indicates structured experience)
        date_patterns = [r'\d{4}', r'\d{1,2}/\d{4}', r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}']
        for pattern in date_patterns:
            if re.search(pattern, text.lower()):
                score += 0.1
                break
        
        # Penalize excessive whitespace
        if text.count('\n\n\n') > 3:
            score -= 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _score_length(self, text: str) -> float:
        """Score resume length (300-1500 words is ideal for 1-2 pages)"""
        word_count = len(text.split())
        
        if 300 <= word_count <= 1500:
            return 1.0
        elif 200 <= word_count < 300:
            return 0.7
        elif 1500 < word_count <= 2500:
            return 0.8
        elif word_count < 200:
            return 0.3
        else:
            return 0.5  # Too long
    
    def _score_impact_language(self, text_lower: str) -> float:
        """Score use of action verbs and quantified achievements"""
        action_verbs = [
            'developed', 'implemented', 'designed', 'led', 'managed', 'created',
            'built', 'improved', 'increased', 'reduced', 'optimized', 'launched',
            'delivered', 'achieved', 'established', 'streamlined', 'automated',
            'collaborated', 'mentored', 'architected', 'deployed', 'resolved'
        ]
        
        verb_count = sum(1 for verb in action_verbs if verb in text_lower)
        verb_score = min(verb_count / 5, 1.0)  # 5+ action verbs = full score
        
        # Check for quantified achievements (numbers with context)
        quant_patterns = r'\b\d+[%+]|\$\d+|\d+\s*(?:users|clients|customers|projects|team|people|members|years)'
        quant_matches = len(re.findall(quant_patterns, text_lower))
        quant_score = min(quant_matches / 3, 1.0)  # 3+ quantified items = full score
        
        return verb_score * 0.6 + quant_score * 0.4
    
    def _generate_feedback(self, section_scores: Dict, keyword_score: float,
                           formatting_score: float, length_score: float,
                           impact_score: float) -> List[str]:
        """Generate actionable feedback"""
        feedback = []
        
        # Missing sections
        missing = [name.title() for name, data in section_scores.items() if not data.get('found')]
        if missing:
            feedback.append(f"Missing sections: {', '.join(missing)}. Add these to improve ATS compatibility.")
        
        # Keywords
        if keyword_score < 0.5:
            feedback.append("Low keyword match with target job. Include more relevant skills and technologies.")
        
        # Formatting
        if formatting_score < 0.6:
            feedback.append("Improve formatting: use bullet points, consistent headers, and date ranges for experience.")
        
        # Length
        if length_score < 0.7:
            word_count_hint = "Consider adding more detail" if length_score < 0.5 else "Good length, but could be more concise"
            feedback.append(f"Resume length needs adjustment. {word_count_hint}.")
        
        # Impact
        if impact_score < 0.5:
            feedback.append("Use more action verbs (developed, implemented, led) and quantify achievements.")
        
        if not feedback:
            feedback.append("Resume looks well-structured. Keep it updated with recent achievements!")
        
        return feedback
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B'
        elif score >= 0.6:
            return 'C'
        elif score >= 0.5:
            return 'D'
        else:
            return 'F'
