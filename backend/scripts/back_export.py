#!/usr/bin/env python3
"""
Clean Backend Code Snapshot for HuggingFace Debugging
Only includes essential files for troubleshooting
"""

import os
from pathlib import Path

# Only include these specific directories (backend only)
INCLUDE_DIRS = [
    "accounts",      # API auth
    "faceswap",      # Main HuggingFace integration 
    "imagegen",      # Might have HF code too
    "django_project" # Settings and main config
]

# Essential file extensions only
INCLUDE_EXTENSIONS = [
    ".py",           # Python code
    ".txt",          # Requirements, etc.
    ".yml", ".yaml", # Docker compose
    ".toml"          # Fly.toml
]

# Essential root files
ROOT_FILES = [
    "requirements.txt",
    "requirements-dev.txt", 
    "Dockerfile",
    "docker-compose.yml",
    "fly.toml",
    "manage.py"
]

# Skip these directories completely
EXCLUDE_DIRS = {
    "__pycache__", "migrations", "venv", "env", "node_modules",
    "media", "static", "staticfiles", "uploads", "tests", ".git",
    "source", "target", "data"  # Skip image/data folders
}

# Skip these files
EXCLUDE_FILES = {
    ".env", ".env.local", ".env.production", "db.sqlite3",
    "embeddings.json",  # Large JSON file
    "test_", "tests.py"  # Test files
}

def should_exclude_file(filename):
    """Check if file should be excluded"""
    if filename in EXCLUDE_FILES:
        return True
    if any(filename.startswith(pattern) for pattern in EXCLUDE_FILES):
        return True
    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.log', '.pyc')):
        return True
    return False

def should_include_file(file_path, filename):
    """Check if file should be included"""
    if should_exclude_file(filename):
        return False
    return any(file_path.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def collect_files():
    """Collect all essential files"""
    collected = []
    
    # Collect from specific directories
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
                
                if should_include_file(full_path, file):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        collected.append((rel_path, content))
                        print(f"✅ Included: {rel_path}")
                    except Exception as e:
                        print(f"❌ Error reading {rel_path}: {e}")

    # Add essential root files
    for file in ROOT_FILES:
        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                collected.append((file, content))
                print(f"✅ Included: {file}")
            except Exception as e:
                print(f"❌ Error reading {file}: {e}")

    return collected

def write_snapshot(files):
    """Write the clean snapshot"""
    os.makedirs("scripts", exist_ok=True)
    output_path = "scripts/clean_backend_snapshot.txt"
    
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("# CLEAN BACKEND CODE SNAPSHOT\n")
        out.write("# Essential files for HuggingFace debugging\n")
        out.write(f"# Total files: {len(files)}\n")
        out.write("# Excludes: migrations, tests, media, large JSON files\n\n")
        
        # Group files by type for better organization
        config_files = []
        python_files = []
        
        for path, code in files:
            if path.endswith(('.txt', '.yml', '.yaml', '.toml')) or path == 'manage.py':
                config_files.append((path, code))
            else:
                python_files.append((path, code))
        
        # Write config files first
        out.write("# ===== CONFIGURATION FILES =====\n\n")
        for path, code in config_files:
            out.write(f"\n## {path}\n```\n{code}\n```\n")
        
        # Write Python files
        out.write("\n\n# ===== PYTHON CODE =====\n\n")
        for path, code in python_files:
            out.write(f"\n## {path}\n```python\n{code}\n```\n")
    
    return output_path

def main():
    print("🧹 Creating clean backend snapshot for HuggingFace debugging...")
    print("📁 Including only essential files\n")
    
    collected_files = collect_files()
    
    if not collected_files:
        print("⚠️  No files found!")
        return
    
    output_path = write_snapshot(collected_files)
    
    print(f"\n✅ Clean snapshot created: {output_path}")
    print(f"📊 Total files: {len(collected_files)}")
    
    # Show what was included
    print(f"\n📋 Files included:")
    for path, _ in collected_files:
        ext = os.path.splitext(path)[1] or "config"
        print(f"  • {path}")

if __name__ == "__main__":
    main()