import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger
import threading

class VectorStore:
    """
    A service for fast vector similarity search using NumPy.
    Provides a lightweight alternative to Scikit-Learn for Render environments.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VectorStore, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.candidate_embeddings = None
        self.candidate_ids = []
        self.job_embeddings = None
        self.job_ids = []
        
        self._initialized = True
        logger.info("VectorStore service initialized (Pure NumPy mode).")

    def update_candidate_index(self, candidates: List[Dict[str, Any]]):
        """Store normalized embeddings for candidate search"""
        if not candidates:
            return
            
        embeddings = []
        self.candidate_ids = []
        
        for cand in candidates:
            if 'embedding' in cand and cand['embedding']:
                embeddings.append(cand['embedding'])
                self.candidate_ids.append(cand['id'])
        
        if embeddings:
            X = np.array(embeddings)
            # Normalize for cosine similarity
            norm = np.linalg.norm(X, axis=1, keepdims=True)
            norm[norm == 0] = 1.0 # Avoid division by zero
            self.candidate_embeddings = X / norm
            logger.info(f"Candidate vector store updated with {len(self.candidate_ids)} records.")

    def find_similar_candidates(self, job_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Find candidates similar to a job's requirements using matrix multiplication"""
        if self.candidate_embeddings is None or not self.candidate_ids:
            return []
            
        query_vec = np.array(job_embedding)
        norm = np.linalg.norm(query_vec)
        if norm == 0: return []
        query_vec = query_vec / norm
        
        # Brute-force cosine similarity via dot product
        similarities = np.dot(self.candidate_embeddings, query_vec)
        
        # Get top K indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "id": self.candidate_ids[idx],
                "score": float((similarities[idx] + 1) / 2) # Normalized to 0-1
            })
            
        return results

    def update_job_index(self, jobs: List[Dict[str, Any]]):
        """Store normalized embeddings for job search"""
        if not jobs:
            return
            
        embeddings = []
        self.job_ids = []
        
        for job in jobs:
            if 'embedding' in job and job['embedding'] and len(job['embedding']) > 0:
                embeddings.append(job['embedding'])
                self.job_ids.append(job['id'])
        
        if embeddings:
            X = np.array(embeddings)
            norm = np.linalg.norm(X, axis=1, keepdims=True)
            norm[norm == 0] = 1.0
            self.job_embeddings = X / norm
            logger.info(f"Job vector store updated with {len(self.job_ids)} records.")

    def find_similar_jobs(self, candidate_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Find jobs similar to a candidate's profile"""
        if self.job_embeddings is None or not self.job_ids:
            return []
            
        if not candidate_embedding or len(candidate_embedding) == 0:
            return []

        query_vec = np.array(candidate_embedding)
        norm = np.linalg.norm(query_vec)
        if norm == 0: return []
        query_vec = query_vec / norm
        
        similarities = np.dot(self.job_embeddings, query_vec)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "id": self.job_ids[idx],
                "score": float((similarities[idx] + 1) / 2)
            })
            
        return results

# global singleton
vector_store = VectorStore()
