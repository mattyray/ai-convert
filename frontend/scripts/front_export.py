import os

# Auto-detect if we're in frontend directory or project root
def detect_directories():
    """Auto-detect the correct directories based on current location"""
    current_dir = os.getcwd()
    
    # Check if we're in the frontend directory
    if os.path.basename(current_dir) == "frontend" and os.path.exists("src"):
        print("📍 Detected: Running from frontend directory")
        return ["src", "public", "."], "scripts/frontend_code_snapshot.txt"
    
    # Check if we're in project root and frontend exists
    elif os.path.exists("frontend"):
        print("📍 Detected: Running from project root")
        return ["frontend/src", "frontend/public", "frontend"], "frontend/scripts/frontend_code_snapshot.txt"
    
    # Check if we're in project root but no frontend directory
    elif os.path.exists("backend"):
        print("📍 Detected: Project root, but no frontend directory yet")
        return [], "scripts/frontend_code_snapshot.txt"
    
    else:
        print("❌ Could not detect project structure")
        return [], "frontend_code_snapshot.txt"

# File extensions to include
INCLUDE_EXTENSIONS = [
    ".ts", ".tsx", ".js", ".jsx", ".json", ".html", ".css", ".scss", 
    ".md", ".svg", ".ico", ".png", ".jpg", ".jpeg", ".gif", ".webp"
]

# Directories to exclude
EXCLUDE_DIRS = {
    "node_modules", "dist", "build", ".next", ".vite", "coverage",
    "__pycache__", ".git", ".vscode", ".idea", "tmp", "temp"
}

# Files to exclude
EXCLUDE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", ".DS_Store",
    "Thumbs.db", ".env.local", ".env.development", ".env.production"
}

def should_include_file(file_path, filename):
    """Check if file should be included based on extension and exclusion rules"""
    if filename in EXCLUDE_FILES:
        return False
    return any(file_path.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def walk_and_collect(include_dirs):
    """Walk through frontend directories and collect relevant files"""
    collected = []

    for base_dir in include_dirs:
        if not os.path.exists(base_dir):
            print(f"⚠️  Directory {base_dir} does not exist, skipping...")
            continue
            
        # Handle root-level frontend files
        if base_dir in [".", "frontend"]:
            for file in os.listdir(base_dir):
                file_path = os.path.join(base_dir, file)
                if os.path.isfile(file_path):
                    if should_include_file(file_path, file):
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                            collected.append((file_path, content))
                        except Exception as e:
                            print(f"❌ Error reading {file_path}: {e}")
        else:
            # Handle subdirectories
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
                        except Exception as e:
                            print(f"❌ Error reading {rel_path}: {e}")

    return collected

def write_snapshot(files, output_path):
    """Write collected files to snapshot file"""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("# FRONTEND CODE SNAPSHOT\n")
        out.write("# Generated for AI Face Swap App\n")
        out.write(f"# Total files: {len(files)}\n\n")
        
        for path, code in files:
            out.write(f"\n\n# ==== {path} ====\n\n")
            out.write(code)
            out.write("\n\n")

def main():
    """Main execution function"""
    print("🚀 Starting smart frontend code snapshot generation...")
    
    # Auto-detect directories
    include_dirs, output_path = detect_directories()
    
    if not include_dirs:
        print("⚠️  No frontend structure detected!")
        print("🔧 To set up frontend, run from project root:")
        print("   npm create vite@latest frontend -- --template react-ts")
        return
    
    print(f"📁 Output file: {output_path}")
    
    collected_files = walk_and_collect(include_dirs)
    
    if not collected_files:
        print("⚠️  No frontend files found!")
        return
    
    write_snapshot(collected_files, output_path)
    
    print(f"✅ Frontend snapshot created: {output_path}")
    print(f"📊 Files included: {len(collected_files)}")
    
    # Print summary of file types
    file_types = {}
    for path, _ in collected_files:
        ext = os.path.splitext(path)[1] or "no extension"
        file_types[ext] = file_types.get(ext, 0) + 1
    
    print("\n📋 File types included:")
    for ext, count in sorted(file_types.items()):
        print(f"  • {ext}: {count} files")

if __name__ == "__main__":
    main()