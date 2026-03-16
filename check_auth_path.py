import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

try:
    from app.api.v1 import auth
    print(f"Auth module file: {auth.__file__}")
    
    with open(auth.__file__, 'r') as f:
        content = f.read()
        if "detail=f\"An error occurred during signup: {str(e)}\"" in content:
            print("Change is PRESENT in the file.")
        else:
            print("Change is MISSING from the file.")
            
except Exception as e:
    print(f"Error: {e}")
