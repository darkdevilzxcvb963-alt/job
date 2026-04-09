import os
from collections import defaultdict

def generate_stats():
    base_dir = r"c:\Users\ADMIN\new-project"
    
    # Categories mapped to file extensions or specific filenames
    categories = {
        "Backend (Python)": [".py"],
        "Frontend (JavaScript/React)": [".js", ".jsx", ".ts", ".tsx", ".css", ".html"],
        "Data & Database": [".json", ".db", ".sqlite", ".sql", ".bak"],
        "Documentation": [".md"],
        "DevOps & Config": [".env", ".gitignore", "Dockerfile", ".yml", ".yaml", ".ini", ".toml", "Procfile", ".example"],
        "Media/Assets": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]
    }
    
    # Directories to ignore to get accurate counts of actual project code
    ignore_dirs = {
        "node_modules", "venv", ".venv", "env", ".env", 
        ".git", "__pycache__", ".vscode", "alembic", ".gemini", 
        "dist", "build", "site-packages", "Lib", "Include", "Scripts"
    }
    
    stats = {
        "total_files": 0,
        "by_extension": defaultdict(int),
        "by_category": defaultdict(int),
        "diagnostics_and_scripts": 0,
        "directories_count": 0
    }
    
    # Keywords to identifying testing, diagnostics, logs and ad-hoc scripts
    diagnostic_keywords = ["diag", "check", "test", "debug", "log", "output", "reset", "fix", "seed", "verify"]
    
    for root, dirs, files in os.walk(base_dir):
        # Mute ignored directories robustly case-insensitively
        dirs[:] = [d for d in dirs if d not in ignore_dirs and d.lower() not in ignore_dirs]

        stats["directories_count"] += len(dirs)
        
        for file in files:
            stats["total_files"] += 1
            ext = os.path.splitext(file)[1].lower()
            
            if not ext:
                ext = "no_extension"
                
            stats["by_extension"][ext] += 1
            
            # Check categories
            categorized = False
            for cat, prefixes in categories.items():
                if ext in prefixes or (ext == "no_extension" and file in ["Dockerfile", "Procfile"]):
                    stats["by_category"][cat] += 1
                    categorized = True
                    break
            
            if not categorized:
                if ext == ".txt":
                    stats["by_category"]["Text/Logs"] += 1
                else:
                    stats["by_category"]["Other"] += 1
                
            # Count diagnostic / test / log scripts specifically
            filename_lower = file.lower()
            if any(kw in filename_lower for kw in diagnostic_keywords) or ext == ".txt" or ext == ".log":
                stats["diagnostics_and_scripts"] += 1

    # Write output to a Markdown file in the project
    report_path = os.path.join(base_dir, "project_inventory_count.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 Project Inventory & Technology Stats\n\n")
        f.write("> An automated breakdown of all file types, tech stacks, and diagnostics files in the project.\n\n")
        
        f.write("## 📈 High Level Summary\n")
        f.write(f"- **Total Files Scanned:** {stats['total_files']}\n")
        f.write(f"- **Total Directories:** {stats['directories_count']}\n")
        f.write(f"- **Diagnostic/Testing/Log Files:** {stats['diagnostics_and_scripts']} *(includes check_, verify_, diag_, .log and .txt files)*\n\n")
        
        f.write("## 📂 Files by Category\n")
        for cat, count in sorted(stats["by_category"].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{cat}:** {count} files\n")
            
        f.write("\n## 📄 File Extensions Breakdown\n")
        # Format the extension list and sort by most files
        for ext, count in sorted(stats["by_extension"].items(), key=lambda x: x[1], reverse=True):
            ext_name = ext if ext != "no_extension" else "No Extension (e.g. Dockerfile.env)"
            f.write(f"- **`{ext_name}`**: {count}\n")
            
    print(f"Report successfully generated at: {report_path}")

if __name__ == '__main__':
    generate_stats()
