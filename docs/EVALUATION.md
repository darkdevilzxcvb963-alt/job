# Performance Evaluation Guide

## Metrics

### 1. Precision, Recall, and F1-Score

These metrics evaluate the quality of matches:

- **Precision**: Proportion of recommended matches that are actually relevant
- **Recall**: Proportion of relevant matches that were recommended
- **F1-Score**: Harmonic mean of precision and recall

### 2. Ranking Metrics

#### Mean Reciprocal Rank (MRR)
Average of reciprocal ranks of the first relevant match for each query.

#### Normalized Discounted Cumulative Gain (NDCG)
Measures ranking quality by considering the position of relevant items.

### 3. User Feedback Metrics

- Click-through rate (CTR)
- Application rate
- User satisfaction scores

## Evaluation Scripts

Create evaluation scripts in the `tests/` directory:

```python
# tests/evaluate_matching.py
from app.services.matching_engine import MatchingEngine
from app.models import Candidate, Job, Match

def evaluate_precision_recall():
    """Calculate precision and recall for matches"""
    # Implementation here
    pass

def calculate_mrr():
    """Calculate Mean Reciprocal Rank"""
    # Implementation here
    pass

def calculate_ndcg():
    """Calculate NDCG"""
    # Implementation here
    pass
```

## Test Dataset

Create a test dataset with:
- Ground truth labels (relevant/not relevant)
- Candidate-job pairs with known matches
- User feedback data

## Baseline Comparison

Compare against:
- Keyword-based matching
- Simple skill overlap
- Random matching

## Continuous Evaluation

- A/B testing different matching algorithms
- Monitoring user feedback
- Tracking match quality over time
