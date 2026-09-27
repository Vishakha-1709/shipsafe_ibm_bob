import re
import os
from typing import List, Dict, Any

# Common secret detection regexes
SECRET_PATTERNS = [
    {
        "name": "Generic API Key / Secret Token",
        "pattern": r'''(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|access[_-]?token|private[_-]?key)\s*[:=]\s*["']([A-Za-z0-9_\-\.]{16,})["']''',
        "severity": "Critical",
        "category": "Secret Leak"
    },
    {
        "name": "AWS Access Key ID",
        "pattern": r'''\b(AKIA[0-9A-Z]{16})\b''',
        "severity": "Critical",
        "category": "Cloud Credentials"
    },
    {
        "name": "OpenAI / Cloud AI Secret Key",
        "pattern": r'''\b(sk-[A-Za-z0-9]{32,})\b''',
        "severity": "Critical",
        "category": "AI API Key"
    },
    {
        "name": "Database Connection String / Password",
        "pattern": r'''(?i)(postgres|mysql|mongodb(?:\+srv)?):\/\/[a-zA-Z0-9_-]+:([a-zA-Z0-9!@#$%^&*()_+\-=]+)@''',
        "severity": "Critical",
        "category": "Database Credentials"
    },
    {
        "name": "Hardcoded Password / Auth Secret",
        "pattern": r'''(?i)(password|passwd|pwd|client_secret)\s*[:=]\s*["']([^"'\s]{6,})["']''',
        "severity": "High",
        "category": "Hardcoded Credential"
    },
    {
        "name": "RSA / OpenSSH Private Key Header",
        "pattern": r'''-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----''',
        "severity": "Critical",
        "category": "Private Key"
    },
    {
        "name": "JWT Token",
        "pattern": r'''\beyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+\b''',
        "severity": "High",
        "category": "Authentication Token"
    }
]

def mask_secret(secret_str: str) -> str:
    """Mask secret value for safe display in UI."""
    if len(secret_str) <= 6:
        return "***"
    return secret_str[:3] + "..." + secret_str[-3:]

def scan_for_secrets(repo_path: str, file_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scans text files for potential hardcoded secrets and security flaws."""
    findings = []
    
    for file_info in file_list:
        rel_path = file_info["rel_path"]
        full_path = file_info["full_path"]
        ext = file_info["ext"]
        
        # Skip binaries, lockfiles, minified files, or huge files
        if ext not in {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', '.env', '.ini', '.cfg', '.txt', '.sh', '.html'}:
            continue
        if file_info["size"] > 1024 * 1024:  # > 1MB
            continue
        if "package-lock.json" in rel_path or "yarn.lock" in rel_path or "node_modules" in rel_path:
            continue

        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_idx, line in enumerate(lines, start=1):
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#") or clean_line.startswith("//"):
                    # Basic comment line skip unless explicitly testing config comments
                    pass
                
                for p in SECRET_PATTERNS:
                    match = re.search(p["pattern"], line)
                    if match:
                        matched_val = match.group(0)
                        # Extract the specific captured group if available
                        secret_val = match.group(2) if len(match.groups()) >= 2 else (match.group(1) if len(match.groups()) >= 1 else matched_val)
                        
                        # Filter out common placeholders / falses
                        placeholder_indicators = ["your_", "example", "placeholder", "dummy", "fake", "todo", "xxx", "000", "<", ">", "process.env", "os.getenv"]
                        if any(ind in secret_val.lower() for ind in placeholder_indicators):
                            continue
                            
                        findings.append({
                            "type": p["name"],
                            "severity": p["severity"],
                            "category": p["category"],
                            "file": rel_path,
                            "line": line_idx,
                            "snippet": clean_line[:120],
                            "masked_value": mask_secret(secret_val),
                            "raw_secret": secret_val
                        })
        except Exception:
            continue

    return findings
