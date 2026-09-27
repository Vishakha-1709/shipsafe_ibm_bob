import os
from typing import Dict, Any, List

def calculate_release_readiness(scan_data: Dict[str, Any], secret_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes a 0-100 release readiness score across 4 pillars:
    1. Documentation (25 pts)
    2. Testing (25 pts)
    3. Security Hygiene (25 pts)
    4. Maintainability & Config (25 pts)
    """
    checklist = []
    
    # Pillar 1: Documentation (25 pts)
    doc_score = 0
    if scan_data["has_readme"]:
        doc_score += 15
        # Check README quality (length/sections)
        readme_path = os.path.join(scan_data["repo_path"], scan_data["readme_path"])
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if len(content) > 300:
                    doc_score += 5
                if any(sec in content.lower() for sec in ["install", "setup", "usage", "getting started", "run"]):
                    doc_score += 5
                else:
                    checklist.append({
                        "priority": "Medium",
                        "category": "Documentation",
                        "action": "Add setup/installation instructions to README.md",
                        "impact": "+5 pts",
                        "reason": "Users and CI maintainers cannot easily determine how to run the project."
                    })
        except Exception:
            pass
    else:
        checklist.append({
            "priority": "Critical",
            "category": "Documentation",
            "action": "Create a comprehensive README.md file",
            "impact": "+20 pts",
            "reason": "Repository completely lacks project overview, setup, and usage documentation."
        })

    if scan_data["has_license"]:
        doc_score = min(25, doc_score + 5)
    else:
        checklist.append({
            "priority": "Low",
            "category": "Documentation",
            "action": "Add a LICENSE file (e.g., Apache 2.0, MIT)",
            "impact": "+5 pts",
            "reason": "Without a license, default copyright prevents open contribution."
        })

    # Pillar 2: Testing (25 pts)
    test_score = 0
    if scan_data["has_tests"]:
        test_count = len(scan_data["test_files"])
        if test_count >= 3:
            test_score = 25
        elif test_count >= 1:
            test_score = 15
            checklist.append({
                "priority": "Medium",
                "category": "Testing",
                "action": f"Expand test coverage (currently found {test_count} test file(s))",
                "impact": "+10 pts",
                "reason": "Basic test files detected, but comprehensive suite is recommended before release."
            })
    else:
        checklist.append({
            "priority": "Critical",
            "category": "Testing",
            "action": "Implement automated unit/integration tests",
            "impact": "+25 pts",
            "reason": "No test directory or test files detected in the project."
        })

    # Pillar 3: Security Hygiene (25 pts)
    sec_score = 25
    critical_secrets = [s for s in secret_findings if s["severity"] == "Critical"]
    high_secrets = [s for s in secret_findings if s["severity"] == "High"]
    
    if critical_secrets:
        sec_score = max(0, sec_score - (len(critical_secrets) * 15))
        for cs in critical_secrets:
            checklist.append({
                "priority": "Critical",
                "category": "Security Hygiene",
                "action": f"Remove {cs['type']} from {cs['file']} (line {cs['line']})",
                "impact": "+15 pts",
                "reason": f"Hardcoded credential exposed: {cs['masked_value']}. Move to environment variables."
            })

    if high_secrets:
        sec_score = max(0, sec_score - (len(high_secrets) * 8))
        for hs in high_secrets:
            checklist.append({
                "priority": "High",
                "category": "Security Hygiene",
                "action": f"Sanitize potential secret {hs['type']} in {hs['file']}",
                "impact": "+8 pts",
                "reason": f"Suspected secret found on line {hs['line']}."
            })

    if scan_data["has_env_file"]:
        sec_score = max(0, sec_score - 10)
        checklist.append({
            "priority": "Critical",
            "category": "Security Hygiene",
            "action": f"Delete or .gitignore active .env files ({', '.join(scan_data['env_files'])})",
            "impact": "+10 pts",
            "reason": "Active .env files contain live runtime secrets and should never be committed."
        })

    # Pillar 4: Maintainability & Configuration (25 pts)
    maint_score = 0
    if scan_data["has_dependencies"]:
        maint_score += 10
    else:
        checklist.append({
            "priority": "High",
            "category": "Maintainability",
            "action": "Add dependency declaration (requirements.txt, package.json, pyproject.toml)",
            "impact": "+10 pts",
            "reason": "Missing dependency manifests will break builds and onboarding."
        })

    if scan_data["has_gitignore"]:
        maint_score += 5
    else:
        checklist.append({
            "priority": "Medium",
            "category": "Maintainability",
            "action": "Add a .gitignore file to prevent clutter and temporary files",
            "impact": "+5 pts",
            "reason": "Prevents OS cache, bytecode, and virtualenv files from polluting git history."
        })

    if scan_data["entry_points"]:
        maint_score += 5
    else:
        checklist.append({
            "priority": "Low",
            "category": "Maintainability",
            "action": "Provide clear application entry point (e.g., app.py, main.py, index.js)",
            "impact": "+5 pts",
            "reason": "Makes executing the project straightforward for new contributors."
        })

    if not scan_data["large_files"]:
        maint_score += 5
    else:
        checklist.append({
            "priority": "Medium",
            "category": "Maintainability",
            "action": f"Review {len(scan_data['large_files'])} oversized file(s) (>5MB)",
            "impact": "+5 pts",
            "reason": "Large binaries bloat git repositories; consider Git LFS or external storage."
        })

    # Bounds check
    doc_score = max(0, min(25, doc_score))
    test_score = max(0, min(25, test_score))
    sec_score = max(0, min(25, sec_score))
    maint_score = max(0, min(25, maint_score))
    
    total_score = doc_score + test_score + sec_score + maint_score
    
    # Priority sorting for checklist
    priority_weights = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    checklist.sort(key=lambda x: priority_weights.get(x["priority"], 99))
    
    # Grade determination
    if total_score >= 90:
        grade = "A (Ship Ready)"
        status_color = "#10B981"
    elif total_score >= 75:
        grade = "B (Minor Polish Needed)"
        status_color = "#3B82F6"
    elif total_score >= 50:
        grade = "C (Action Required)"
        status_color = "#F59E0B"
    else:
        grade = "D (Not Ready for Release)"
        status_color = "#EF4444"

    return {
        "total_score": total_score,
        "grade": grade,
        "status_color": status_color,
        "breakdown": {
            "Documentation": {"score": doc_score, "max": 25},
            "Testing": {"score": test_score, "max": 25},
            "Security Hygiene": {"score": sec_score, "max": 25},
            "Maintainability": {"score": maint_score, "max": 25}
        },
        "checklist": checklist
    }
