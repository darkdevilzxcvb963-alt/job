# Literature Review

## Overview
The AI-Powered Resume & Job Matching Platform addresses the inefficiencies of traditional keyword-based recruitment systems. Traditional systems often fail due to:
- **Exact Match Dependency**: Requiring identical phrasing (e.g., "Python Developer" vs "Software Engineer with Python").
- **Lack of Context**: Ignoring the semantic meaning behind job titles and descriptions.
- **Surface-Level Analysis**: Failing to understand the depth of skill and experience.

## Chosen Technologies & Rationale

### 1. Natural Language Processing (NLP)
The system utilizes modern NLP techniques to preprocess and normalize data.
- **SpaCy**: Used for Named Entity Recognition (NER) to extract entities like organizations, locations, and dates.
- **NLTK**: Used for tokenization, lemmatization, and stopword removal to clean the text before processing.
- **Skill Extraction**: A custom-built pipeline that combines keyword matching with noun phrase analysis from SpaCy to identify technical and soft skills.

### 2. Semantic Embeddings (Sentence-BERT)
To move beyond keyword matching, the system uses **Sentence-BERT (SBERT)**.
- **Model**: `all-MiniLM-L6-v2` is used as the default embedding model.
- **Mechanism**: It converts resumes and job descriptions into high-dimensional vectors (384 dimensions).
- **Benefit**: Contextually similar words (e.g., "AI" and "Machine Learning") map to similar vector spaces, allowing for semantic similarity calculations.

### 3. Large Language Models (LLMs)
The system integrates with **OpenAI's GPT-4** (or similar) for high-level reasoning.
- **Summarization**: Condensing long resumes into concise professional profiles.
- **Matching Explanations**: Generating human-readable reasons why a candidate is a good fit for a specific job.
- **Title Normalization**: Converting varying job titles into standard formats.

## Comparison Table

| Feature | Traditional Systems | Our AI Platform |
|---------|---------------------|-----------------|
| **Matching Logic** | Exact keyword match | Semantic similarity |
| **Parsing** | Basic text extraction | Structured NLP analysis |
| **Logic** | Boolean (AND/OR) | Vector-based scoring |
| **Experience** | Simple year counts | Semantic alignment |
| **Transparency** | Black box (often) | LLM-generated explanations |
