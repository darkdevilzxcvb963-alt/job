from app.core.database import SessionLocal
from app.models.match import Match
import sys

def fix_serialization():
    # This script will read the file and replace the dictionary construction
    file_path = 'backend/app/api/v1/matches.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Target string
    old_str = """        match_dict = {
            **match.__dict__,
            "candidate_name": candidate.name,"""
            
    # Replacement string
    new_str = """        match_dict = {
            "id": match.id,
            "status": match.status,
            **{k: v for k, v in match.__dict__.items() if not k.startswith('_')},
            "candidate_name": candidate.name,"""
    
    if old_str in content:
        new_content = content.replace(old_str, new_str)
        with open(file_path, 'w') as f:
            f.write(new_content)
        print("Successfully updated matches.py")
    else:
        # Try without the precise number of spaces if it fails
        print("Could not find the target string in matches.py")
        # Let's print the first 200 chars of the file to debug
        # print(content[:200])

if __name__ == "__main__":
    fix_serialization()
