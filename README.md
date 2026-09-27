# 🛡️ ShipSafe — AI Release-Readiness Assistant

> **IBM Bob 2.0 AI Hackathon Submission**  
> *Theme: "Turn Idea into Impact Faster"*  
> *Track: Developer Productivity & Pre-Release Assurance*

---

## 📌 Problem
Small software teams and developers frequently face last-minute release bottlenecks:
- **Discovered Late:** Missing unit tests, absent README instructions, and broken configs are often caught only after opening a PR or failing in CI.
- **Accidental Secret Leaks:** API keys, database credentials, or active `.env` files are accidentally committed to source control.
- **Manual Overhead:** Developers waste 45–60 minutes manually preparing release checklists and hand-writing `RELEASE_NOTES.md`.

---

## 💡 Solution: What is ShipSafe?
**ShipSafe** is a lightweight, ultra-fast pre-release gatekeeper for software repositories. It audits a project in seconds, calculates a release-readiness score, prioritizes blockers, and generates drop-in fix templates.

### ✨ Key Features
1. **Repository Structural Audit:** Identifies primary languages, entry points, documentation, tests, and dependency manifests.
2. **Deterministic Security Hunter:** Detects hardcoded API keys, JWT tokens, AWS credentials, and `.env` leaks with automatic masking.
3. **4-Pillar Release Readiness Score (0–100):**
   - 📖 **Documentation (25 pts):** README quality & Licensing.
   - 🧪 **Testing (25 pts):** Test suite presence & coverage breadth.
   - 🔒 **Security Hygiene (25 pts):** Secret detection & `.env` exclusion.
   - ⚙️ **Maintainability (25 pts):** Dependency declarations, `.gitignore`, and binary bloat checks.
4. **Instant AI Remediation Stubs:** Generates 1-click starter `README.md`, `tests/test_core.py`, `.env` refactor snippets, and `.gitignore`.
5. **One-Click Release Gate Export:** Generates signed `RELEASE_NOTES.md` and `RELEASE_CHECKLIST.md` for PR approvals.

---

## 🤖 How IBM Bob was Used
IBM Bob IDE was our central pair-programming and development partner throughout the project lifecycle:
- **Architectural Planning:** Designed the 4-pillar modular pipeline and deterministic scanner structure.
- **Scanner & Security Implementation:** Developed regex heuristics and token masking algorithms.
- **Security Hardening & Code Review:** Implemented Zip Slip vulnerability protections in file extraction.
- **Test Generation:** Authored the automated unit test suite.
- **Evidence Logs:** Complete transcripts are preserved in [`bob_sessions/`](bob_sessions/).

---

## 🚀 Quickstart & Local Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd shipsafe
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```

---

## 🧪 Running Unit Tests
```bash
python -m unittest discover -s tests
```

---

## 📊 Live Demo Flow for Judges
1. **Pre-Bob Imperfect Repo:** Select *"⚡ Quick Demo: Pre-Bob Imperfect Project"* from the sidebar.
   - Observe the low score (`~38/100`), critical secret alerts in `predict.py`, missing tests, and missing README.
2. **One-Click Fixes:** Navigate to the *"🛠️ AI Fix Stubs"* tab to copy the generated `.env` refactor and test scaffolds.
3. **Post-Bob Remediated Repo:** Select *"✨ Quick Demo: Post-Bob Remediated Project"* from the sidebar.
   - Observe the score jumping to `95+/100` (Release Ready).
4. **Export Artifacts:** Go to the *"📑 Export Release Gate Artifacts"* tab and download `RELEASE_NOTES.md` & `RELEASE_CHECKLIST.md`.

---

## ⚠️ Important Limitation Notice
*ShipSafe is an early-warning developer productivity assistant designed to accelerate release workflows. It is intended to complement, not replace, full enterprise security audits, penetration testing, or human code review.*
