import datetime
from typing import Dict, Any, List

def generate_release_notes(scan_data: Dict[str, Any], score_data: Dict[str, Any], version: str = "v1.0.0") -> str:
    """Generates clean RELEASE_NOTES.md."""
    date_str = datetime.date.today().strftime("%B %d, %Y")
    langs = ", ".join(scan_data["languages"].keys()) if scan_data["languages"] else "Multi-language"
    
    notes = f"""# Release Notes - {version} ({date_str})

## 📦 Release Summary
- **Overall Release Readiness Score:** `{score_data['total_score']}/100` ({score_data['grade']})
- **Total Files Audited:** {scan_data['total_files']} files ({scan_data['total_size_mb']} MB)
- **Primary Languages:** {langs}
- **Entry Points:** {', '.join(scan_data['entry_points']) if scan_data['entry_points'] else 'Standard Module'}

---

## 🎯 Verification Highlights
- **Documentation:** {score_data['breakdown']['Documentation']['score']}/25 pts
- **Test Suite Status:** {score_data['breakdown']['Testing']['score']}/25 pts ({len(scan_data['test_files'])} test files detected)
- **Security Hygiene:** {score_data['breakdown']['Security Hygiene']['score']}/25 pts
- **Maintainability & Packaging:** {score_data['breakdown']['Maintainability']['score']}/25 pts

---

## 🚀 Key Features & Changes Included
- Core application implementation
- Dependency manifests configured ({', '.join(scan_data['dependency_files']) if scan_data['dependency_files'] else 'Standard'})
- Automated release-readiness verification passed via **ShipSafe**.

---
*Generated automatically by ShipSafe AI Release Readiness Assistant.*
"""
    return notes

def generate_release_checklist_md(scan_data: Dict[str, Any], score_data: Dict[str, Any]) -> str:
    """Generates actionable markdown checklist for Pull Requests & Release Gate."""
    checklist = score_data.get("checklist", [])
    
    md = f"""# 🛡️ ShipSafe Release Gate Checklist

**Audit Date:** {datetime.date.today().strftime("%Y-%m-%d")}  
**Overall Readiness Score:** `{score_data['total_score']}/100` — **{score_data['grade']}**

---

## 📋 Prioritized Action Items
"""
    if not checklist:
        md += "\n🎉 **All release gate checks passed! Ready for production deployment.**\n"
    else:
        for item in checklist:
            box = "[ ]"
            md += f"\n- {box} **[{item['priority'].upper()}]** {item['action']} (`{item['impact']}`)\n"
            md += f"  - *Category:* {item['category']}\n"
            md += f"  - *Reason:* {item['reason']}\n"

    md += """
---

## 🔍 Pre-Release Sign-Off Gate
- [ ] Code review completed by senior engineer
- [ ] No uncommitted secrets or `.env` files in staging
- [ ] All unit and integration tests passing in CI/CD
- [ ] Documentation and version bumps verified

---
*Signed off via ShipSafe AI Release Readiness Assistant.*
"""
    return md
