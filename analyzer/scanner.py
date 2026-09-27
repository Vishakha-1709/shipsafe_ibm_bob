import os
import zipfile
import tempfile
import io
from typing import Dict, List, Any, Tuple

IGNORE_DIRS = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', '.idea', '.vscode', 'dist', 'build'}
TEXT_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml', '.toml', '.md', '.txt', '.html', '.css', '.sh', '.env', '.ini', '.cfg', '.xml', '.sql', '.go', '.rs', '.java', '.c', '.cpp', '.h'}

def extract_zip(zip_source) -> str:
    """Extract uploaded zip (BytesIO, UploadedFile, or bytes) to a temporary directory safely and return path."""
    temp_dir = tempfile.mkdtemp(prefix="shipsafe_repo_")
    
    if hasattr(zip_source, "getvalue"):
        file_bytes = zip_source.getvalue()
    elif hasattr(zip_source, "read"):
        file_bytes = zip_source.read()
    elif isinstance(zip_source, bytes):
        file_bytes = zip_source
    else:
        raise ValueError("Unsupported zip file input type.")
    
    with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zip_ref:
        # Prevent Zip Slip vulnerability
        for member in zip_ref.infolist():
            target_path = os.path.abspath(os.path.join(temp_dir, member.filename))
            if not target_path.startswith(os.path.abspath(temp_dir)):
                raise Exception("Potential Zip Slip vulnerability detected.")
        zip_ref.extractall(temp_dir)
        
    # Auto-unwrap single root folder (e.g. GitHub 'repo-main/' download format)
    extracted_items = [item for item in os.listdir(temp_dir) if not item.startswith('.')]
    if len(extracted_items) == 1:
        single_sub = os.path.join(temp_dir, extracted_items[0])
        if os.path.isdir(single_sub):
            return single_sub

    return temp_dir

def scan_repository(repo_path: str) -> Dict[str, Any]:
    """Inspects files, directories, languages, and core project indicators."""
    total_files = 0
    total_dirs = 0
    total_size_bytes = 0
    file_list = []
    file_types = {}
    
    has_readme = False
    readme_path = None
    has_tests = False
    test_files = []
    has_dependencies = False
    dependency_files = []
    has_license = False
    has_gitignore = False
    has_env_file = False
    env_files = []
    large_files = []
    entry_points = []
    
    for root, dirs, files in os.walk(repo_path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        total_dirs += len(dirs)
        
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, repo_path).replace("\\", "/")
            total_files += 1
            
            try:
                file_size = os.path.getsize(full_path)
                total_size_bytes += file_size
            except OSError:
                file_size = 0
                
            _, ext = os.path.splitext(f)
            ext = ext.lower() if ext else "no_extension"
            file_types[ext] = file_types.get(ext, 0) + 1
            
            file_list.append({
                "rel_path": rel_path,
                "full_path": full_path,
                "size": file_size,
                "ext": ext
            })
            
            # Check README
            if f.lower().startswith("readme") and ext in [".md", ".rst", ".txt", "no_extension"]:
                has_readme = True
                readme_path = rel_path
                
            # Check Tests
            if "test" in f.lower() or "tests" in rel_path.lower().split("/"):
                if ext in [".py", ".js", ".ts", ".go", ".rs", ".java"]:
                    has_tests = True
                    test_files.append(rel_path)
                    
            # Check Dependencies
            if f in ["requirements.txt", "package.json", "pyproject.toml", "Pipfile", "go.mod", "Cargo.toml", "pom.xml", "Gemfile", "environment.yml"]:
                has_dependencies = True
                dependency_files.append(rel_path)
                
            # Check License
            if f.lower().startswith("license") or f.lower().startswith("copying"):
                has_license = True
                
            # Check .gitignore
            if f == ".gitignore":
                has_gitignore = True
                
            # Check .env
            if f.startswith(".env") and not f.endswith(".example") and not f.endswith(".sample"):
                has_env_file = True
                env_files.append(rel_path)
                
            # Check large files (> 5MB)
            if file_size > 5 * 1024 * 1024:
                large_files.append({"path": rel_path, "size_mb": round(file_size / (1024 * 1024), 2)})
                
            # Check entry points
            if f in ["app.py", "main.py", "index.js", "index.ts", "server.js", "main.go", "App.java"]:
                entry_points.append(rel_path)

    # Determine primary languages
    lang_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".go": "Go", ".rs": "Rust", ".java": "Java", ".c": "C", ".cpp": "C++",
        ".html": "HTML/Web", ".css": "CSS", ".sh": "Shell", ".json": "JSON"
    }
    languages = {}
    for ext, count in file_types.items():
        lang = lang_map.get(ext)
        if lang:
            languages[lang] = languages.get(lang, 0) + count

    return {
        "repo_path": repo_path,
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
        "file_types": file_types,
        "languages": languages,
        "has_readme": has_readme,
        "readme_path": readme_path,
        "has_tests": has_tests,
        "test_files": test_files,
        "has_dependencies": has_dependencies,
        "dependency_files": dependency_files,
        "has_license": has_license,
        "has_gitignore": has_gitignore,
        "has_env_file": has_env_file,
        "env_files": env_files,
        "large_files": large_files,
        "entry_points": entry_points,
        "file_list": file_list
    }
