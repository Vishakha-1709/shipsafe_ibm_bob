import streamlit as st
import os
import io
import time
import zipfile
import plotly.graph_objects as go

from analyzer.scanner import extract_zip, scan_repository
from analyzer.security import scan_for_secrets
from analyzer.scoring import calculate_release_readiness

st.set_page_config(
    page_title="ShipSafe | AI Release-Readiness Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .severity-badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .severity-badge-high {
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .severity-badge-medium {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .severity-badge-low {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .bob-tag {
        background: linear-gradient(135deg, #0F62FE 0%, #0043CE 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .risk-callout {
        background-color: #FFF7ED;
        border-left: 4px solid #F97316;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-top: 8px;
        font-size: 0.9rem;
        color: #7C2D12;
    }
</style>
""", unsafe_allow_html=True)

# Helper for Polished Gauge Chart
def create_gauge(score, grade, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': "", 'font': {'size': 44, 'color': '#0F172A', 'family': 'Inter'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "#F8FAFC",
            'borderwidth': 1,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 50], 'color': '#FEE2E2'},
                {'range': [50, 75], 'color': '#FEF3C7'},
                {'range': [75, 100], 'color': '#ECFDF5'}
            ],
            'threshold': {
                'line': {'color': "#0F172A", 'width': 3},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(
        height=230, 
        margin=dict(l=15, r=15, t=20, b=10), 
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Inter"}
    )
    return fig

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=85)
    st.markdown("### 🛡️ **ShipSafe Control Panel**")
    st.caption("AI-assisted pre-release assurance engine powered by IBM Bob workflows.")
    
    st.markdown("---")
    st.subheader("📁 Select Repository Input")
    
    input_source = st.radio(
        "Choose analysis target:",
        [
            "⚡ Quick Demo: Pre-Bob Imperfect Project",
            "✨ Quick Demo: Post-Bob Remediated Project",
            "📤 Upload Custom Project (ZIP)"
        ]
    )

    st.markdown("---")
    st.markdown("### 💡 Why ShipSafe?")
    st.markdown("""
    * **Automated Structure Audit**
    * **Secret & Credentials Hunter**
    * **Test & Docs Gap Detector**
    * **4-Pillar Release Readiness Score**
    * **Actionable PR Checklist**
    """)
    st.markdown("---")
    st.caption("IBM Bob Hackathon 2.0 • Turn Idea into Impact Faster")

# Main Header
st.markdown('<div class="main-header">ShipSafe <span class="bob-tag">IBM Bob Partner</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated pre-release gatekeeper. Detect gaps, sanitize secrets, and verify release readiness in seconds.</div>', unsafe_allow_html=True)

# Target resolution
sample_dir = os.path.join(os.path.dirname(__file__), "samples")
target_repo_path = None

if "Pre-Bob Imperfect" in input_source:
    bad_zip_path = os.path.join(sample_dir, "sample_bad_repo.zip")
    if not os.path.exists(bad_zip_path):
        import samples.generate_samples as gs
        gs.build_all_samples()
    with open(bad_zip_path, "rb") as f:
        target_repo_path = extract_zip(io.BytesIO(f.read()))

elif "Post-Bob Remediated" in input_source:
    clean_zip_path = os.path.join(sample_dir, "sample_clean_repo.zip")
    if not os.path.exists(clean_zip_path):
        import samples.generate_samples as gs
        gs.build_all_samples()
    with open(clean_zip_path, "rb") as f:
        target_repo_path = extract_zip(io.BytesIO(f.read()))

elif "Upload Custom Project" in input_source:
    with st.container(border=True):
        st.markdown("#### 📤 Upload Your Software Project")
        st.write("Upload a `.zip` file of any software repository to run the full ShipSafe pre-release audit.")
        
        uploaded_file = st.file_uploader("Select or Drag & Drop Repository ZIP", type=["zip"], key="repo_uploader")
        
        if uploaded_file is not None:
            try:
                with st.spinner("Extracting and inspecting repository..."):
                    target_repo_path = extract_zip(uploaded_file)
                st.success(f"✅ Successfully loaded `{uploaded_file.name}` ({round(uploaded_file.size / (1024*1024), 2)} MB)")
            except Exception as e:
                st.error(f"❌ Error processing zip file: {e}")
                st.stop()
        else:
            st.info("👆 Please drag and drop or browse for a `.zip` repository file above to begin the audit.")
            st.stop()

if not target_repo_path:
    st.stop()

# Perform Fast Analysis
start_time = time.time()
scan_data = scan_repository(target_repo_path)
secret_findings = scan_for_secrets(target_repo_path, scan_data["file_list"])
score_data = calculate_release_readiness(scan_data, secret_findings)
elapsed_time = round(time.time() - start_time, 3)

# Top Metric Banner in modern cards
m1, m2, m3, m4 = st.columns(4)
with m1:
    with st.container(border=True):
        st.caption("🏆 Overall Release Score")
        st.markdown(f"### {score_data['total_score']} <span style='font-size:16px;color:#64748B'>/ 100</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:{score_data['status_color']};font-weight:700;'>● {score_data['grade']}</span>", unsafe_allow_html=True)
with m2:
    with st.container(border=True):
        crit_count = len([i for i in score_data['checklist'] if i['priority'] == 'Critical'])
        st.caption("🚨 Critical Blockers")
        st.markdown(f"### {crit_count}", unsafe_allow_html=True)
        if crit_count > 0:
            st.markdown("<span style='color:#EF4444;font-weight:600;'>Immediate Fix Required</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#10B981;font-weight:600;'>All Clear</span>", unsafe_allow_html=True)
with m3:
    with st.container(border=True):
        st.caption("⚡ Audit Execution Time")
        st.markdown(f"### {elapsed_time}s", unsafe_allow_html=True)
        st.markdown("<span style='color:#10B981;font-weight:600;'>Instant Automated Scan</span>", unsafe_allow_html=True)
with m4:
    with st.container(border=True):
        st.caption("⏱️ Manual Time Saved")
        st.markdown("### ~35 mins", unsafe_allow_html=True)
        st.markdown("<span style='color:#0F62FE;font-weight:600;'>IBM Bob Assisted Workflow</span>", unsafe_allow_html=True)

st.write("")

# Navigation Tabs - Streamlined to Core Focus
tab_overview, tab_checklist, tab_bob_evidence = st.tabs([
    "📊 Readiness Dashboard",
    "⚠️ Prioritized Action Checklist",
    "🤖 Before vs After Bob Evidence"
])

# ----------------- TAB 1: DASHBOARD -----------------
with tab_overview:
    col_gauge, col_breakdown = st.columns([1.1, 1.9])
    
    with col_gauge:
        with st.container(border=True):
            st.markdown("<div style='text-align:center;font-weight:700;color:#334155;margin-bottom:6px;'>Release Readiness Gauge</div>", unsafe_allow_html=True)
            st.plotly_chart(create_gauge(score_data['total_score'], score_data['grade'], score_data['status_color']), use_container_width=True)
            st.caption("<div style='text-align:center;'>Scores &ge; 90 qualify for automatic release gate bypass.</div>", unsafe_allow_html=True)

    with col_breakdown:
        with st.container(border=True):
            st.markdown("#### 🎯 4-Pillar Score Breakdown")
            for pillar, pdata in score_data['breakdown'].items():
                pct = int((pdata['score'] / pdata['max']) * 100)
                col_pname, col_pval = st.columns([3, 1])
                col_pname.write(f"**{pillar}**")
                col_pval.write(f"**{pdata['score']}** / {pdata['max']} pts")
                st.progress(pct / 100)

    st.write("")
    with st.container(border=True):
        st.markdown("#### 📁 Repository Structural Anatomy")
        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        with c_f1:
            st.markdown(f"**Total Files:** `{scan_data['total_files']}`")
            st.markdown(f"**Total Size:** `{scan_data['total_size_mb']} MB`")
        with c_f2:
            st.markdown(f"**README.md:** {'✅ Present' if scan_data['has_readme'] else '❌ Missing'}")
            st.markdown(f"**LICENSE:** {'✅ Present' if scan_data['has_license'] else '❌ Missing'}")
        with c_f3:
            st.markdown(f"**Unit Tests:** {'✅ ' + str(len(scan_data['test_files'])) + ' file(s)' if scan_data['has_tests'] else '❌ Missing'}")
            st.markdown(f"**Dependencies:** {'✅ ' + ', '.join(scan_data['dependency_files']) if scan_data['has_dependencies'] else '❌ Missing'}")
        with c_f4:
            st.markdown(f"**Committed `.env`:** {'❌ DANGER (Exposed)' if scan_data['has_env_file'] else '✅ Clean'}")
            st.markdown(f"**.gitignore:** {'✅ Present' if scan_data['has_gitignore'] else '❌ Missing'}")

        if scan_data["languages"]:
            st.markdown("---")
            st.markdown("**Detected Tech Stack / Languages:** " + " ".join([f"`{lang} ({count})`" for lang, count in scan_data["languages"].items()]))


# ----------------- TAB 2: ACTION CHECKLIST -----------------
with tab_checklist:
    st.markdown("### 📋 Prioritized Remediation Checklist")
    st.markdown("All items ordered by severity and score impact.")
    
    if not score_data['checklist']:
        st.success("🎉 **Zero release blockers detected! This repository is 100% ready for immediate production deployment.**")
    else:
        for idx, item in enumerate(score_data['checklist'], start=1):
            sev_class = f"severity-badge-{item['priority'].lower()}"
            
            with st.expander(f"#{idx} [{item['priority'].upper()}] - {item['action']}", expanded=(item['priority'] == 'Critical')):
                c_a, c_b = st.columns([3, 1])
                with c_a:
                    st.markdown(f"**Category:** `{item['category']}`")
                    st.markdown(f"**Why this matters:** {item['reason']}")
                with c_b:
                    st.markdown(f'<span class="{sev_class}">{item["priority"]} Priority</span>', unsafe_allow_html=True)
                    st.markdown(f"**Score Impact:** `{item['impact']}`")

    # Security Secret Table if any
    if secret_findings:
        st.markdown("---")
        st.markdown("### 🚨 Detected Secrets & Credential Exposure")
        
        st.markdown("""
        <div class="risk-callout">
            <strong>⚠️ Security Warning:</strong> Hardcoded credentials in source control can be extracted by anyone with read access. 
            Migrate these credentials immediately to secure environment variables or a key vault before merging.
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        sec_rows = []
        for s in secret_findings:
            sec_rows.append({
                "Severity": s["severity"],
                "Credential Type": s["type"],
                "File Location": f"{s['file']}:{s['line']}",
                "Masked Value": s["masked_value"]
            })
        st.table(sec_rows)


# ----------------- TAB 3: BEFORE VS AFTER BOB -----------------
with tab_bob_evidence:
    st.markdown("### 🤖 Before vs. After IBM Bob Workflow Evidence")
    st.markdown("Demonstrating how IBM Bob accelerates developer productivity across release cycles.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        with st.container(border=True):
            st.markdown("<h4 style='color:#EF4444;'>❌ Traditional Manual Workflow (Before Bob)</h4>", unsafe_allow_html=True)
            st.markdown("""
            * **Manual Repo Inspection:** Developer spends 25-45 minutes digging through directories to check configs.
            * **Late Bug & Test Discovery:** Missing test coverage is only noticed during CI pipeline failures.
            * **Accidental Secret Leaks:** Keys in code slip through peer review and get pushed to production.
            * **Manual Documentation:** Release notes and PR checklists are hand-written and often incomplete.
            * **Average Turnaround:** `~45 - 60 minutes per release`
            """)
    
    with col_b2:
        with st.container(border=True):
            st.markdown("<h4 style='color:#10B981;'>✅ ShipSafe + IBM Bob Workflow (After Bob)</h4>", unsafe_allow_html=True)
            st.markdown("""
            * **Instant Structure Synthesis:** Automated scan delivers complete repository anatomy in `<2 seconds`.
            * **Pre-emptive Gap Detection:** Test gaps & missing dependencies are flagged before opening PR.
            * **Early Secret Interception:** Regex security hunter intercepts API keys before git commit.
            * **One-Click Release Assessment:** Generates comprehensive readiness checklist automatically.
            * **Average Turnaround:** `<1 minute per release (98% time reduction)`
            """)

    st.write("")
    with st.container(border=True):
        st.markdown("#### 🔬 How IBM Bob was used as our Core Development Partner:")
        st.markdown("""
        1. **Architecture & Design:** IBM Bob planned the modular separation of the scanner, scoring engine, and audit pipeline.
        2. **Implementation:** IBM Bob wrote deterministic Python AST/regex inspectors to avoid unreliable network LLM dependencies during live deployment.
        3. **Test Suite Generation:** Bob scaffolded unit tests for secret matching and readiness thresholds.
        4. **Code Review & Hardening:** Bob performed security audits, enforcing Zip Slip protection and memory safety.
        """)

# Footer Limitation Notice
st.markdown("---")
st.caption("🔒 **ShipSafe Notice:** ShipSafe is an AI release-readiness early warning productivity assistant designed to accelerate developer workflows. It is intended to complement, not replace, full enterprise security audits and human code review.")
