"""
Skill Gap Analysis Service
Identifies missing skills and recommends learning paths
"""
import re
import json
from typing import List, Dict, Optional
from loguru import logger
from app.services.skill_categories import SKILL_SYNONYMS, SKILL_TO_CATEGORY, SKILL_HIERARCHY, SKILL_CATEGORIES
from app.services.llm_service import LLMService


class SkillGapService:
    """Analyzes skill gaps between candidates and target jobs"""
    
    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize a skill name to its canonical form"""
        cleaned = re.sub(r'\s*\(.*?\)', '', str(skill)).lower().strip()
        return SKILL_SYNONYMS.get(cleaned, cleaned)
    
    def _flatten_skills(self, skills: any) -> List[str]:
        """Extract flat list of skill names from list or dict"""
        flat = []
        if isinstance(skills, dict):
            for category_skills in skills.values():
                if isinstance(category_skills, list):
                    flat.extend(category_skills)
        elif isinstance(skills, list):
            flat = skills
        return [self._normalize_skill(s) for s in flat]
    
    def analyze_gap(self, candidate_skills: any, job_required_skills: List[str],
                    job_preferred_skills: List[str] = None) -> Dict:
        """
        Perform skill gap analysis
        
        Args:
            candidate_skills: Candidate's skills (list or dict)
            job_required_skills: Required skills for the job
            job_preferred_skills: Preferred skills for the job
            
        Returns:
            Dictionary with gap analysis results
        """
        candidate_normalized = set(self._flatten_skills(candidate_skills))
        required_normalized = set(self._normalize_skill(s) for s in (job_required_skills or []))
        preferred_normalized = set(self._normalize_skill(s) for s in (job_preferred_skills or []))
        
        # Matched skills
        matched_required = candidate_normalized & required_normalized
        matched_preferred = candidate_normalized & preferred_normalized
        
        # Missing skills
        missing_required = required_normalized - candidate_normalized
        missing_preferred = preferred_normalized - candidate_normalized
        
        # Classify missing skills by severity and find bridgeable ones
        missing_analysis = []
        bridgeable = []
        
        for skill in missing_required:
            skill_cat = SKILL_TO_CATEGORY.get(skill)
            related_from_candidate = []
            
            if skill_cat:
                for cs in candidate_normalized:
                    if SKILL_TO_CATEGORY.get(cs) == skill_cat:
                        related_from_candidate.append(cs)
            
            if related_from_candidate:
                bridgeable.append({
                    'skill': skill,
                    'severity': 'moderate',
                    'category': skill_cat or 'General',
                    'you_know': ', '.join(related_from_candidate[:3]),
                    'learning_path': f"Build on your {related_from_candidate[0]} knowledge to learn {skill}"
                })
            else:
                missing_analysis.append({
                    'skill': skill,
                    'severity': 'critical',
                    'category': skill_cat or 'General'
                })
        
        # Also note missing preferred skills (lower severity)
        for skill in missing_preferred:
            if skill not in [m['skill'] for m in missing_analysis] and skill not in [b['skill'] for b in bridgeable]:
                missing_analysis.append({
                    'skill': skill,
                    'severity': 'low',
                    'category': SKILL_TO_CATEGORY.get(skill, 'General')
                })
        
        # Coverage score
        total_required = len(required_normalized)
        coverage = len(matched_required) / total_required if total_required > 0 else 1.0
        
        return {
            'coverage_score': round(coverage, 3),
            'matched_skills': sorted(list(matched_required | matched_preferred)),
            'missing_skills': sorted(missing_analysis, key=lambda x: {'critical': 0, 'moderate': 1, 'low': 2}.get(x['severity'], 3)),
            'bridgeable_skills': bridgeable,
            'total_required': total_required,
            'total_matched': len(matched_required)
        }
    
    def generate_recommendations(self, gap_analysis: Dict) -> List[Dict]:
        """
        Generate course/learning recommendations for missing skills using LLM
        
        Args:
            gap_analysis: Output from analyze_gap()
            
        Returns:
            List of recommendation dictionaries
        """
        missing = gap_analysis.get('missing_skills', [])
        bridgeable = gap_analysis.get('bridgeable_skills', [])
        
        all_gaps = missing + bridgeable
        if not all_gaps:
            return []
        
        skill_names = [g['skill'] for g in all_gaps[:10]]  # Limit to top 10
        
        if self.llm_service and (self.llm_service.gemini_model or self.llm_service.openai_client):
            try:
                prompt = f"""For each of the following technical skills, provide a learning recommendation.
Return a JSON array of objects with keys: "skill", "course", "platform", "duration", "url".

Skills: {', '.join(skill_names)}

Example format:
[{{"skill": "Docker", "course": "Docker Mastery", "platform": "Udemy", "duration": "4 weeks", "url": "https://www.udemy.com/"}}]
Return ONLY valid JSON."""

                result = self.llm_service._call_llm(
                    prompt, 
                    "You are a career advisor specializing in tech skills. Return only valid JSON.",
                    max_tokens=800
                )
                
                if result:
                    content = result
                    # Clean up markdown code block if present
                    if content.startswith('```'):
                        if '\n' in content:
                            content = content.split('\n', 1)[1]
                        if '```' in content:
                            content = content.rsplit('```', 1)[0]
                    
                    recs = json.loads(content.strip())
                    if isinstance(recs, list):
                        return recs
            except Exception as e:
                logger.error(f"Error generating recommendations: {e}")
        
        # Fallback: generate basic recommendations without LLM
        recommendations = []
        for gap in all_gaps[:10]:
            skill = gap['skill']
            recommendations.append({
                'skill': skill,
                'course': f"Introduction to {skill.title()}",
                'platform': 'Online Learning',
                'duration': '4-6 weeks',
                'url': f"https://www.coursera.org/search?query={skill.replace(' ', '+')}"
            })
        
        return recommendations
