import os

# Directories to include for backend
INCLUDE_DIRS = [
    "accounts", 
    "chat", 
    "imagegen", 
    "faceswap",  # Added missing faceswap app
    "django_project", 
    "scripts",
    "face_data"  # Added face embeddings data
]

# File extensions to include
INCLUDE_EXTENSIONS = [
    ".py", ".json", ".html", ".js", ".ts", ".css", 
    ".txt", ".md", ".yml", ".yaml", ".toml", ".env.template"  # Added config files
]

# Directories to exclude
EXCLUDE_DIRS = {
    "__pycache__", "migrations", "venv", "env", "node_modules", 
    "media", "static", ".git", "staticfiles", "uploads"
}

# Files to exclude
EXCLUDE_FILES = {
    ".env", ".env.local", ".env.production", "db.sqlite3", 
    "*.log", "*.pyc", ".DS_Store"
}

# Output file
OUTPUT_PATH = os.path.join("scripts", "backend_code_snapshot.txt")

def should_include(file_path, filename):
    """Check if file should be included"""
    if filename in EXCLUDE_FILES or filename.startswith('.'):
        return False
    return any(file_path.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def walk_and_collect():
    collected = []

    for base_dir in INCLUDE_DIRS:
        if not os.path.exists(base_dir):
            print(f"⚠️  Directory {base_dir} does not exist, skipping...")
            continue
            
        for root, dirs, files in os.walk(base_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path)
                
                if should_include(full_path, file):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        collected.append((rel_path, content))
                    except Exception as e:
                        print(f"❌ Error reading {rel_path}: {e}")

    # Also include root-level config files
    root_files = [
        "requirements.txt", "requirements-dev.txt", "manage.py", 
        "Dockerfile", "docker-compose.yml", "fly.toml"
    ]
    
    for file in root_files:
        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                collected.append((file, content))
            except Exception as e:
                print(f"❌ Error reading {file}: {e}")

    return collected

def write_snapshot(files):
    # Ensure scripts directory exists
    os.makedirs("scripts", exist_ok=True)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        out.write("# BACKEND CODE SNAPSHOT\n")
        out.write("# Generated for AI Face Swap App\n")
        out.write(f"# Total files: {len(files)}\n\n")
        
        for path, code in files:
            out.write(f"\n\n# ==== {path} ====\n\n")
            out.write(code)
            out.write("\n\n")

def main():
    print("🚀 Starting backend code snapshot generation...")
    print(f"📁 Output file: {OUTPUT_PATH}")
    
    collected_files = walk_and_collect()
    
    if not collected_files:
        print("⚠️  No backend files found!")
        return
    
    write_snapshot(collected_files)
    
    print(f"✅ Backend snapshot created: {OUTPUT_PATH}")
    print(f"📊 Files included: {len(collected_files)}")
    
    # Print summary
    file_types = {}
    for path, _ in collected_files:
        ext = os.path.splitext(path)[1] or "no extension"
        file_types[ext] = file_types.get(ext, 0) + 1
    
    print("\n📋 File types included:")
    for ext, count in sorted(file_types.items()):
        print(f"  • {ext}: {count} files")

if __name__ == "__main__":
    main()