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
        return ["frontend/src", "frontend/public", "frontend"], "scripts/frontend_code_snapshot.txt"
    
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
    ".md", ".svg", ".ico", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".toml", ".yml", ".yaml", ".env.template", ".env.example"  # Added config files
]

# Directories to exclude
EXCLUDE_DIRS = {
    "node_modules", "dist", "build", ".next", ".vite", "coverage",
    "__pycache__", ".git", ".vscode", ".idea", "tmp", "temp"
}

# Files to exclude (but allow .env.template and .env.example)
EXCLUDE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", ".DS_Store",
    "Thumbs.db", ".env.local", ".env.development", ".env.production", ".env"  # Exclude real .env but allow templates
}

# Important root files to always include
IMPORTANT_ROOT_FILES = [
    "package.json", "vite.config.ts", "tailwind.config.js", "postcss.config.js",
    "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", 
    "eslint.config.js", "index.html", "README.md",
    "netlify.toml", "Dockerfile", "Dockerfile.dev", ".env.template", ".env.example"
]

# Important React/src files to always include (relative to src directory)
IMPORTANT_SRC_FILES = [
    "App.tsx", "App.jsx", "main.tsx", "main.jsx", "index.tsx", "index.jsx",
    "App.css", "index.css", "main.css", "globals.css",
    "vite-env.d.ts", "env.d.ts"
]

def should_include_file(file_path, filename):
    """Check if file should be included based on extension and exclusion rules"""
    if filename in EXCLUDE_FILES:
        return False
    
    # Always include important root files
    if filename in IMPORTANT_ROOT_FILES:
        return True
        
    # Always include important src files
    if filename in IMPORTANT_SRC_FILES:
        return True
        
    return any(file_path.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def walk_and_collect(include_dirs):
    """Walk through frontend directories and collect relevant files"""
    collected = []
    found_important_src_files = []

    for base_dir in include_dirs:
        if not os.path.exists(base_dir):
            print(f"⚠️  Directory {base_dir} does not exist, skipping...")
            continue
            
        print(f"🔍 Scanning directory: {base_dir}")
        
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
                            print(f"  ✅ Found root file: {file}")
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
                    
                    # Track important src files
                    if file in IMPORTANT_SRC_FILES:
                        found_important_src_files.append(file)
                        print(f"  ✅ Found important src file: {file}")
                    
                    if should_include_file(full_path, file):
                        try:
                            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                            collected.append((rel_path, content))
                            
                            # Extra logging for key React files
                            if file.endswith(('.tsx', '.jsx')) and 'App' in file:
                                print(f"  🎯 Captured React App file: {rel_path}")
                                
                        except Exception as e:
                            print(f"❌ Error reading {rel_path}: {e}")

    # Report on important src files
    print(f"\n📋 Important src files found: {len(found_important_src_files)}")
    for file in found_important_src_files:
        print(f"  ✅ {file}")
    
    missing_src_files = set(IMPORTANT_SRC_FILES) - set(found_important_src_files)
    if missing_src_files:
        print(f"\n⚠️  Missing important src files:")
        for file in missing_src_files:
            print(f"  ❌ {file}")

    return collected

def write_snapshot(files, output_path):
    """Write collected files to snapshot file"""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("# FRONTEND CODE SNAPSHOT\n")
        out.write("# Generated for AI Face Swap App\n")
        out.write(f"# Total files: {len(files)}\n\n")
        
        # Group files by type for better organization
        config_files = []
        react_main_files = []  # App.tsx, main.tsx, etc.
        component_files = []
        service_files = []
        type_files = []
        asset_files = []
        other_files = []
        
        for path, code in files:
            filename = os.path.basename(path)
            
            # Configuration files (root level)
            if any(path.endswith(ext) for ext in ['.json', '.js', '.ts', '.toml', '.yml', '.yaml']) and not '/src/' in path:
                config_files.append((path, code))
            # Main React files (App.tsx, main.tsx, etc.)
            elif filename in IMPORTANT_SRC_FILES and filename.endswith(('.tsx', '.jsx', '.ts', '.js')):
                react_main_files.append((path, code))
            # Component files
            elif '/components/' in path:
                component_files.append((path, code))
            # Service files  
            elif '/services/' in path:
                service_files.append((path, code))
            # Type files
            elif '/types/' in path or filename.endswith('.d.ts'):
                type_files.append((path, code))
            # Asset files
            elif any(path.endswith(ext) for ext in ['.svg', '.png', '.jpg', '.css', '.html']):
                asset_files.append((path, code))
            else:
                other_files.append((path, code))
        
        # Write in organized sections
        sections = [
            ("Configuration Files", config_files),
            ("Main React Files", react_main_files),
            ("Type Definitions", type_files),
            ("Services & API", service_files),
            ("React Components", component_files),
            ("Assets & Styles", asset_files),
            ("Other Files", other_files)
        ]
        
        for section_name, section_files in sections:
            if section_files:
                out.write(f"\n\n# ==================== {section_name} ====================\n\n")
                for path, code in section_files:
                    out.write(f"\n\n# ==== {path} ====\n\n")
                    out.write(code)
                    out.write("\n\n")

def main():
    """Main execution function"""
    print("🚀 Starting comprehensive frontend code snapshot generation...")
    
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
    
    # Print detailed summary
    file_types = {}
    important_files_found = []
    react_files_found = []
    
    for path, _ in collected_files:
        filename = os.path.basename(path)
        ext = os.path.splitext(path)[1] or "no extension"
        file_types[ext] = file_types.get(ext, 0) + 1
        
        if filename in IMPORTANT_ROOT_FILES:
            important_files_found.append(filename)
        
        if filename.endswith(('.tsx', '.jsx')):
            react_files_found.append(filename)
    
    print("\n📋 File types included:")
    for ext, count in sorted(file_types.items()):
        print(f"  • {ext}: {count} files")
    
    print(f"\n🎯 Important config files found: {len(important_files_found)}")
    for file in sorted(important_files_found):
        print(f"  ✅ {file}")
    
    print(f"\n⚛️  React files found: {len(react_files_found)}")
    for file in sorted(react_files_found):
        print(f"  ✅ {file}")
    
    # Check for missing important files
    missing_files = set(IMPORTANT_ROOT_FILES) - set(important_files_found)
    if missing_files:
        print(f"\n⚠️  Missing important config files:")
        for file in sorted(missing_files):
            print(f"  ❌ {file}")
    
    # Specifically check for App.tsx
    app_files = [f for f in react_files_found if 'App' in f]
    if app_files:
        print(f"\n🎯 App files found: {', '.join(app_files)}")
    else:
        print(f"\n⚠️  No App.tsx or App.jsx found!")
            
    print(f"\n💡 Tip: If files are missing, they might not exist yet or need to be created.")

if __name__ == "__main__":
    main()