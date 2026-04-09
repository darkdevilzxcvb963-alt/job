import numpy as np
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Any, Optional
from loguru import logger
import threading

class VectorStore:
    """
    A service for fast vector similarity search using Scikit-Learn's NearestNeighbors.
    Provides a scalable alternative to linear cosine similarity for large datasets.
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
            
        self.candidate_index = None
        self.candidate_ids = []
        self.job_index = None
        self.job_ids = []
        
        self._initialized = True
        logger.info("VectorStore service initialized.")

    def update_candidate_index(self, candidates: List[Dict[str, Any]]):
        """Build or update the spatial index for candidates"""
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
            # Normalize for cosine similarity via L2 distance on unit vectors
            X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)
            
            self.candidate_index = NearestNeighbors(
                n_neighbors=min(50, len(self.candidate_ids)),
                metric='l2',
                algorithm='auto'
            ).fit(X_norm)
            
            logger.info(f"Candidate vector index updated with {len(self.candidate_ids)} records.")

    def find_similar_candidates(self, job_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Find candidates similar to a job's requirements"""
        if self.candidate_index is None or not self.candidate_ids:
            return []
            
        query_vec = np.array(job_embedding).reshape(1, -1)
        # Normalize
        query_vec = query_vec / np.linalg.norm(query_vec)
        
        distances, indices = self.candidate_index.kneighbors(query_vec, n_neighbors=min(top_k, len(self.candidate_ids)))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # Convert L2 distance on unit vectors back to cosine similarity
            # d^2 = 2 - 2*cos(theta) => cos(theta) = 1 - (d^2 / 2)
            similarity = 1 - (dist**2 / 2)
            results.append({
                "id": self.candidate_ids[idx],
                "score": float(similarity)
            })
            
        return results

    def update_job_index(self, jobs: List[Dict[str, Any]]):
        """Build or update the spatial index for jobs"""
        if not jobs:
            return
            
        embeddings = []
        self.job_ids = []
        
        for job in jobs:
            if 'embedding' in job and job['embedding']:
                embeddings.append(job['embedding'])
                self.job_ids.append(job['id'])
        
        if embeddings:
            X = np.array(embeddings)
            X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)
            
            self.job_index = NearestNeighbors(
                n_neighbors=min(50, len(self.job_ids)),
                metric='l2',
                algorithm='auto'
            ).fit(X_norm)
            
            logger.info(f"Job vector index updated with {len(self.job_ids)} records.")

    def find_similar_jobs(self, candidate_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Find jobs similar to a candidate's profile"""
        if self.job_index is None or not self.job_ids:
            return []
            
        if not candidate_embedding:
            return []

        query_vec = np.array(candidate_embedding).reshape(1, -1)
        query_vec = query_vec / np.linalg.norm(query_vec)
        
        distances, indices = self.job_index.kneighbors(query_vec, n_neighbors=min(top_k, len(self.job_ids)))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            similarity = 1 - (dist**2 / 2)
            results.append({
                "id": self.job_ids[idx],
                "score": float(similarity)
            })
            
        return results

# global singleton
vector_store = VectorStore()
