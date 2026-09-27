# IBM Bob Session 03: Code Review, Hardening & Artifact Generation

**Date:** Hackathon Sprint  
**Agent:** IBM Bob IDE  
**Role:** Senior Code Reviewer & DevOps Lead  

---

## 🎯 Prompt Given to Bob
> *"Review the ShipSafe code for security vulnerabilities, edge cases (e.g. malicious ZIP files), and usability. Implement the Streamlit UI with Before/After Bob evidence panel and exportable release artifacts."*

---

## 🔒 Security Hardening Applied by Bob
1. **Zip Slip Vulnerability Mitigation:** Added path normalization and validation inside `extract_zip()` to ensure extracted files cannot escape the designated temporary directory.
2. **Standardized Unit Testing:** Added comprehensive unit tests in `tests/test_analyzer.py` ensuring regression prevention.
3. **Automated Artifacts:** Created `RELEASE_NOTES.md` and `RELEASE_CHECKLIST.md` generators to turn audit findings into ready-to-merge pull request artifacts.
