"""
Simple demo showing how matching works and displaying current matches.
"""
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# Configuration
DB_PATH = "../resume_matching.db"

def run_demo():
    print("="*80)
    print("MATCHING SYSTEM DEMO")
    print("="*80)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Show logic summary
    print("\n[1] HOW IT WORKS (Logic)")
    print("-" * 30)
    print("The system uses 3 main factors to calculate a match score:")
    print("  a. Semantic Similarity (50% weight): Uses AI embeddings to understand meaning.")
    print("  b. Skill Overlap (30% weight): Checks how many required skills you have.")
    print("  c. Experience Alignment (20% weight): Compares years of experience.")
    print("\n   Overall Score = (Semantic * 0.5) + (Skills * 0.3) + (Exp * 0.2)")
    
    # 2. Show Database Stats
    print("\n[2] DATABASE STATUS")
    print("-" * 30)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")
    jobs_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM candidates")
    cand_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM matches")
    match_count = cursor.fetchone()[0]
    
    print(f"Total Jobs: {jobs_count}")
    print(f"Total Candidates: {cand_count}")
    print(f"Generated Matches: {match_count}")
    
    # 3. Show Top Matches (Sample)
    print("\n[3] TOP MATCHES SAMPLE")
    print("-" * 30)
    query = """
    SELECT 
        j.title as job_title, 
        c.name as candidate_name, 
        m.overall_score,
        m.semantic_similarity,
        m.skill_overlap_score
    FROM matches m
    JOIN jobs j ON m.job_id = j.id
    JOIN candidates c ON m.candidate_id = c.id
    ORDER BY m.overall_score DESC
    LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No matches found in database yet.")
    else:
        # Format for display
        df['overall_score'] = df['overall_score'].apply(lambda x: f"{x*100:.1f}%")
        df['semantic_similarity'] = df['semantic_similarity'].apply(lambda x: f"{x*100:.1f}%")
        df['skill_overlap_score'] = df['skill_overlap_score'].apply(lambda x: f"{x*100:.1f}%")
        print(df.to_string(index=False))
        
    # 4. Show a "Low Score" match example
    print("\n[4] LEAST SCORE MATCH EXAMPLE (Working as requested)")
    print("-" * 30)
    query_low = """
    SELECT 
        j.title as job_title, 
        c.name as candidate_name, 
        m.overall_score
    FROM matches m
    JOIN jobs j ON m.job_id = j.id
    JOIN candidates c ON m.candidate_id = c.id
    ORDER BY m.overall_score ASC
    LIMIT 1
    """
    df_low = pd.read_sql_query(query_low, conn)
    if not df_low.empty:
        row = df_low.iloc[0]
        print(f"Job: {row['job_title']}")
        print(f"Candidate: {row['candidate_name']}")
        print(f"Score: {row['overall_score']*100:.1f}% (This is a low-score match preserved for you!)")

    print("\n" + "="*80)
    conn.close()

if __name__ == "__main__":
    run_demo()
