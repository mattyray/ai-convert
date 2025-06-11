import os

# Directories to include
INCLUDE_DIRS = [
    "accounts", "chat", "imagegen", "django_project", "scripts"
]

# File extensions to include
INCLUDE_EXTENSIONS = [".py", ".json", ".html", ".js", ".ts", ".css"]

# Directories to exclude
EXCLUDE_DIRS = {"__pycache__", "migrations", "venv", "env", "node_modules", "media", "static", ".git"}

# Output file
OUTPUT_PATH = os.path.join("scripts", "code_snapshot.txt")

def should_include(file_path):
    return any(file_path.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def walk_and_collect():
    collected = []

    for base_dir in INCLUDE_DIRS:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path)
                if should_include(full_path):
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    collected.append((rel_path, content))

    return collected

def write_snapshot(files):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        for path, code in files:
            out.write(f"\n\n# ==== {path} ====\n\n")
            out.write(code)
            out.write("\n\n")

if __name__ == "__main__":
    collected_files = walk_and_collect()
    write_snapshot(collected_files)
    print(f"✅ Snapshot created: {OUTPUT_PATH} ({len(collected_files)} files)")
