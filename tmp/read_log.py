import sys

with open("backend/runtime.log", "r", encoding="utf-16", errors="ignore") as f:
    lines = f.readlines()
    
# look for the last generation call or errors
printing = False
for line in lines[-300:]:
    if "ERROR" in line or "Exception" in line or "Traceback" in line:
        printing = True
    if printing:
        print(line, end="")
