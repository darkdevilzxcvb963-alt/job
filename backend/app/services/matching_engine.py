"""
Enhanced Matching Engine Service
Computes multi-factor similarity scores between candidates and jobs
"""
import numpy as np
import re
import json
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
from app.services.skill_categories import SKILL_SYNONYMS, SKILL_TO_CATEGORY, SKILL_HIERARCHY


class MatchingEngine:
    """Engine for matching candidates with job postings using 6-factor scoring"""
    
    def __init__(self):
        """Initialize matching engine"""
        pass
    
    def calculate_semantic_similarity(self, embedding1: List[float], 
                                     embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            if not embedding1 or not embedding2:
                return 0.5  # Neutral similarity if missing embeddings
                
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)
            
            if vec1.shape[1] == 0 or vec2.shape[1] == 0:
                return 0.5
                
            similarity = cosine_similarity(vec1, vec2)[0][0]
            # Normalize to 0-1 range
            return float((similarity + 1) / 2)
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.5
    
    def calculate_skill_overlap(self, candidate_skills: any, 
                                job_skills: List[str],
                                preferred_skills: List[str] = None) -> float:
        """
        Calculate weighted skill overlap score with preferred vs required differentiation
        
        Args:
            candidate_skills: List or dictionary of candidate skills
            job_skills: List of required job skills
            preferred_skills: List of preferred (nice-to-have) job skills
            
        Returns:
            Overlap score between 0 and 1
        """
        if not job_skills:
            return 1.0
        
        # Flatten skills if dictionary
        flat_candidate_skills = []
        if isinstance(candidate_skills, dict):
            for category_skills in candidate_skills.values():
                if isinstance(category_skills, list):
                    flat_candidate_skills.extend(category_skills)
        else:
            flat_candidate_skills = candidate_skills or []
            
        # Helper to normalize skills
        def normalize(s):
             skill = re.sub(r'\s*\(.*?\)', '', str(s)).lower().strip()
             return SKILL_SYNONYMS.get(skill, skill).lower()

        candidate_skills_lower = [normalize(s) for s in flat_candidate_skills]
        job_skills_lower = [normalize(s) for s in job_skills]
        preferred_lower = [normalize(s) for s in (preferred_skills or [])]
        
        candidate_skills_set = set(candidate_skills_lower)
        job_skills_set = set(job_skills_lower)
        preferred_set = set(preferred_lower) - job_skills_set  # Don't double-count
        
        # Required skills matching (weight 1.0 each)
        required_matches = len(candidate_skills_set & job_skills_set)
        
        # Preferred skills matching (weight 0.5 each)
        preferred_matches = len(candidate_skills_set & preferred_set)
        
        # Add partial credits for hierarchical matches (required only)
        partial_credit = 0.0
        missing_job_skills = job_skills_set - candidate_skills_set
        
        for job_skill in missing_job_skills:
            job_cat = SKILL_TO_CATEGORY.get(job_skill)
            if not job_cat:
                continue
                
            for cand_skill in candidate_skills_set:
                cand_cat = SKILL_TO_CATEGORY.get(cand_skill)
                if cand_cat == job_cat:
                    # Sliding scale: same category earns 0.3, same sub-tree earns 0.5
                    hierarchy_entry = SKILL_HIERARCHY.get(job_cat, {})
                    if isinstance(hierarchy_entry, dict):
                        # Check if both skills are in the same sub-group
                        for sub_group, members in hierarchy_entry.items():
                            if isinstance(members, list):
                                if job_skill in [m.lower() for m in members] and cand_skill in [m.lower() for m in members]:
                                    partial_credit += 0.5
                                    break
                        else:
                            partial_credit += 0.3
                    else:
                        partial_credit += 0.3
                    break
        
        total_weight = len(job_skills_set) + len(preferred_set) * 0.5
        if total_weight == 0:
            return 1.0
            
        score = (required_matches + partial_credit + preferred_matches * 0.5) / total_weight
        return min(float(score), 1.0)
    
    def calculate_experience_alignment(self, candidate_exp: float, 
                                      job_exp_required: float,
                                      relevance_boost: float = 0.0) -> float:
        """
        Calculate experience alignment score with relevance boost
        """
        if job_exp_required is None or job_exp_required == 0:
            return 1.0
        
        if candidate_exp is None:
            return 0.0
            
        effective_exp = candidate_exp * (1.0 + relevance_boost)
        
        if effective_exp >= job_exp_required:
            return 1.0
        
        return min(effective_exp / job_exp_required, 1.0)
    
    def calculate_location_match(self, candidate_locations: any,
                                  job_location: str,
                                  remote_ok: bool = False) -> float:
        """
        Calculate location alignment score
        
        Args:
            candidate_locations: Candidate's preferred locations (list/JSON string or None)
            job_location: Job's location string
            remote_ok: Whether the job allows remote work
            
        Returns:
            Location match score between 0 and 1
        """
        if remote_ok:
            return 1.0
            
        if not job_location:
            return 0.8  # Unknown location, mild assumption
        
        if not candidate_locations:
            return 0.5  # No preference specified
        
        # Parse candidate locations from JSON string if needed
        if isinstance(candidate_locations, str):
            try:
                candidate_locations = json.loads(candidate_locations)
            except (json.JSONDecodeError, TypeError):
                candidate_locations = [candidate_locations]
        
        if not isinstance(candidate_locations, list):
            candidate_locations = [str(candidate_locations)]
            
        job_loc_lower = job_location.lower().strip()
        
        # Check for remote keywords
        remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere']
        if any(kw in job_loc_lower for kw in remote_keywords):
            return 1.0
        
        for pref in candidate_locations:
            pref_lower = str(pref).lower().strip()
            
            # Exact city match
            if pref_lower == job_loc_lower:
                return 1.0
            
            # City contained in job location (e.g. "New York" in "New York, NY")
            if pref_lower in job_loc_lower or job_loc_lower in pref_lower:
                return 0.9
            
            # State-level match (simplified)
            pref_parts = set(pref_lower.replace(',', ' ').split())
            job_parts = set(job_loc_lower.replace(',', ' ').split())
            if pref_parts & job_parts:
                return 0.6
        
        return 0.2  # No location match
    
    def calculate_salary_alignment(self, candidate_min: float, candidate_max: float,
                                    job_min: float, job_max: float) -> float:
        """
        Calculate salary range overlap score
        
        Args:
            candidate_min/max: Candidate's salary expectations
            job_min/max: Job's salary range
            
        Returns:
            Salary alignment score between 0 and 1
        """
        # If either side has no salary info, return neutral
        if (candidate_min is None and candidate_max is None) or (job_min is None and job_max is None):
            return 0.7  # Neutral
        
        c_min = candidate_min or 0
        c_max = candidate_max or float('inf')
        j_min = job_min or 0
        j_max = job_max or float('inf')
        
        # Calculate overlap
        overlap_start = max(c_min, j_min)
        overlap_end = min(c_max, j_max)
        
        if overlap_start <= overlap_end:
            # There is overlap
            total_range = max(c_max, j_max) - min(c_min, j_min)
            if total_range > 0:
                overlap = (overlap_end - overlap_start) / total_range
                return min(0.5 + overlap * 0.5, 1.0)  # Scale to 0.5-1.0
            return 1.0
        else:
            # No overlap — penalize based on gap
            gap = overlap_start - overlap_end
            max_salary = max(c_max if c_max != float('inf') else 0, 
                           j_max if j_max != float('inf') else 0, 1)
            penalty = min(gap / max_salary, 1.0)
            return max(0.0, 0.5 - penalty * 0.5)
    
    def calculate_seniority_alignment(self, candidate_seniority: str,
                                       job_title: str,
                                       job_experience_required: float = None) -> float:
        """
        Calculate seniority level alignment
        
        Args:
            candidate_seniority: Candidate's seniority level string
            job_title: Job title to infer required seniority
            job_experience_required: Years of experience required
            
        Returns:
            Seniority alignment score between 0 and 1
        """
        # Map seniority levels to numeric scale
        seniority_scale = {
            'entry-level': 1, 'intern': 1, 'junior': 2, 'associate': 2,
            'mid': 3, 'intermediate': 3, 'junior/intermediate': 3,
            'senior': 4, 'senior+': 4, 'lead': 5, 'staff': 5,
            'principal': 6, 'director': 6, 'vp': 7, 'head': 7
        }
        
        # Infer job seniority from title
        job_title_lower = (job_title or '').lower()
        job_level = 3  # Default to mid
        
        senior_markers = ['senior', 'sr', 'lead', 'principal', 'staff', 'head', 'director', 'vp']
        junior_markers = ['junior', 'jr', 'entry', 'intern', 'associate', 'graduate', 'trainee']
        
        for marker in senior_markers:
            if marker in job_title_lower:
                job_level = seniority_scale.get(marker, 4)
                break
        for marker in junior_markers:
            if marker in job_title_lower:
                job_level = seniority_scale.get(marker, 2)
                break
        
        # Also use experience requirement as a hint
        if job_experience_required:
            if job_experience_required >= 8:
                job_level = max(job_level, 5)
            elif job_experience_required >= 5:
                job_level = max(job_level, 4)
            elif job_experience_required >= 2:
                job_level = max(job_level, 3)
        
        # Get candidate level
        candidate_level = 3  # Default
        if candidate_seniority:
            candidate_level = seniority_scale.get(candidate_seniority.lower().strip(), 3)
        
        # Calculate alignment (perfect match = 1.0, each level away reduces score)
        diff = abs(candidate_level - job_level)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.8  # One level off is still a decent fit
        elif diff == 2:
            return 0.5
        else:
            return max(0.2, 1.0 - diff * 0.2)
    
    def calculate_overall_score(self, semantic_sim: float, skill_overlap: float,
                             exp_alignment: float, location_match: float = None,
                             salary_alignment: float = None,
                             seniority_alignment: float = None,
                             weights: Dict[str, float] = None) -> float:
        """
        Calculate overall job-fit score using 6-factor weighted formula
        
        Args:
            semantic_sim: Semantic similarity score
            skill_overlap: Skill overlap score
            exp_alignment: Experience alignment score
            location_match: Location match score (optional)
            salary_alignment: Salary alignment score (optional)
            seniority_alignment: Seniority alignment score (optional)
            weights: Optional custom weights
            
        Returns:
            Overall score between 0 and 1
        """
        if weights is None:
            # Use extended weights if all factors are available
            if location_match is not None and salary_alignment is not None and seniority_alignment is not None:
                weights = {
                    'semantic': 0.35,
                    'skills': 0.25,
                    'experience': 0.15,
                    'location': 0.10,
                    'salary': 0.08,
                    'seniority': 0.07
                }
            else:
                # Fallback to original 3-factor weights
                weights = {
                    'semantic': 0.5,
                    'skills': 0.3,
                    'experience': 0.2
                }
        
        overall = (
            weights.get('semantic', 0) * semantic_sim +
            weights.get('skills', 0) * skill_overlap +
            weights.get('experience', 0) * exp_alignment
        )
        
        if location_match is not None and 'location' in weights:
            overall += weights['location'] * location_match
        if salary_alignment is not None and 'salary' in weights:
            overall += weights['salary'] * salary_alignment
        if seniority_alignment is not None and 'seniority' in weights:
            overall += weights['seniority'] * seniority_alignment
        
        return float(overall)
    
    def match_candidate_to_job(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """
        Match a candidate to a job and return scores (enhanced 6-factor version)
        
        Args:
            candidate_data: Candidate data with embeddings, skills, location prefs, salary etc.
            job_data: Job data with embeddings, requirements, location, salary range etc.
            
        Returns:
            Dictionary with all matching scores
        """
        # 1. Semantic similarity (existing)
        semantic_sim = self.calculate_semantic_similarity(
            candidate_data.get('embedding', []),
            job_data.get('embedding', [])
        )
        
        # 2. Skill overlap (enhanced with preferred skills)
        candidate_skills = candidate_data.get('skills', [])
        job_skills = job_data.get('required_skills', [])
        preferred_skills = job_data.get('preferred_skills', [])
        
        # Aggregate job skills if categorized
        if 'skills_by_category' in job_data and job_data['skills_by_category']:
            cat_jobs = job_data['skills_by_category']
            aggregated_job_skills = []
            for cat_list in cat_jobs.values():
                if isinstance(cat_list, list):
                    aggregated_job_skills.extend(cat_list)
            if aggregated_job_skills:
                job_skills = aggregated_job_skills
        
        skill_overlap = self.calculate_skill_overlap(
            candidate_skills, job_skills, preferred_skills
        )
        
        # 3. Experience alignment (existing + relevance boost)
        relevance_boost = 0.0
        cand_title = candidate_data.get('title', '').lower()
        job_title = job_data.get('title', '').lower()
        
        if cand_title and job_title:
            cand_words = set(cand_title.split())
            job_words = set(job_title.split())
            if cand_words & job_words:
                relevance_boost = 0.15
                
        exp_alignment = self.calculate_experience_alignment(
            candidate_data.get('experience_years', 0),
            job_data.get('experience_required', 0),
            relevance_boost=relevance_boost
        )
        
        # 4. Location match (NEW)
        location_match = self.calculate_location_match(
            candidate_data.get('preferred_locations'),
            job_data.get('location'),
            job_data.get('remote_ok', False)
        )
        
        # 5. Salary alignment (NEW)
        salary_alignment = self.calculate_salary_alignment(
            candidate_data.get('salary_expectation_min'),
            candidate_data.get('salary_expectation_max'),
            job_data.get('salary_min'),
            job_data.get('salary_max')
        )
        
        # 6. Seniority alignment (NEW)
        seniority_alignment = self.calculate_seniority_alignment(
            candidate_data.get('seniority_level'),
            job_data.get('title', ''),
            job_data.get('experience_required')
        )
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(
            semantic_sim, skill_overlap, exp_alignment,
            location_match, salary_alignment, seniority_alignment
        )
        
        return {
            'semantic_similarity': semantic_sim,
            'skill_overlap_score': skill_overlap,
            'experience_alignment': exp_alignment,
            'location_score': location_match,
            'salary_score': salary_alignment,
            'seniority_score': seniority_alignment,
            'overall_score': overall_score
        }
