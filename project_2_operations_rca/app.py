import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import smtplib
import ssl
from email.mime.text import MIMEText
import sys
import os
import random

# Optional Chart Libraries with Fallback Safety
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# AI SDKs
try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import anthropic
    HAS_CLAUDE = True
except ImportError:
    HAS_CLAUDE = False

# Ensure root directory is on sys.path for nested module imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Enterprise AI Portfolio | Pavan Kumar V",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization (Guarantees zero AttributeError crashes)
if "current_page" not in st.session_state:
    st.session_state.current_page = "intro"
if "selected_ticket_id" not in st.session_state:
    st.session_state.selected_ticket_id = None
if "generated_draft" not in st.session_state:
    st.session_state.generated_draft = None
if "approval_history" not in st.session_state:
    st.session_state.approval_history = []
if "first_response_sent" not in st.session_state:
    st.session_state.first_response_sent = set()
if "show_first_response_preview" not in st.session_state:
    st.session_state.show_first_response_preview = {}
if "tailored_output" not in st.session_state:
    st.session_state.tailored_output = None

# Default Configurations
if "use_claude" not in st.session_state:
    st.session_state.use_claude = False
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""
if "claude_key" not in st.session_state:
    st.session_state.claude_key = ""
if "gemini_model" not in st.session_state:
    st.session_state.gemini_model = "gemini-1.5-flash"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.3
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 450
if "sender_email" not in st.session_state:
    st.session_state.sender_email = "pavanwork111@gmail.com"
if "sender_app_password" not in st.session_state:
    st.session_state.sender_app_password = ""
if "demo_recipient" not in st.session_state:
    st.session_state.demo_recipient = "pavanwork111@gmail.com"
if "threshold" not in st.session_state:
    st.session_state.threshold = 75

# -----------------------------------------------------------------------------
# 2. GLOBAL CSS STYLING & GLASSMORPHISM DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark Mode Core Theme */
    .main {
        background-color: #0B0F17;
        color: #F1F5F9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Ambient Background Gradient */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(37, 99, 235, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
                    #0B0F17;
    }

    /* 3D Glassmorphism Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    .glass-card-interactive {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 24px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }

    .glass-card-interactive:hover {
        transform: translateY(-4px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 12px 24px rgba(37, 99, 235, 0.15);
    }

    /* Tech Color Gradient Titles */
    .gradient-text {
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .gradient-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
    }

    /* KPI Metric Container */
    .kpi-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 14px;
        text-align: center;
    }

    /* Ticket Badge Styling */
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 999px;
        font-size: 11px; font-weight: 700; color: white; margin-left: 6px;
    }
    .badge-breached { background: #EF4444; }
    .badge-critical { background: #F97316; }
    .badge-watch { background: #FACC15; color: #1E293B; }

    /* Hide Sidebar on Intro Screen */
    """ + ("""
    [data-testid="stSidebar"] { display: none; }
    """ if st.session_state.current_page == "intro" else "") + """
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS & DATASETS
# -----------------------------------------------------------------------------
FIRST_RESPONSE_TEMPLATE = """Hi there,

Thank you for reaching out to us. We wanted to confirm that we've received your request and it's currently being worked on by our support team.

We understand your time is valuable, and we're actively looking into this. Someone from our team will follow up with you as soon as there's an update.

We appreciate your patience in the meantime.

Thank you,
Support Team"""

DEFAULT_MASTER_RESUME = """PAVAN KUMAR VAIKUTHERISAL
Hyderabad, India | +91 90597 45757 | Pavan55vkumar@gmail.com
LinkedIn: linkedin.com/in/pavankumarv55 | GitHub: github.com/pavan55vkumar-afk

SUMMARY:
Client-facing Operations Analyst and self-taught programmer with 3+ years of experience at Deloitte and MediaMint. Specialized in managing, troubleshooting, and resolving data exceptions within Epic Systems and CRM platform integrations (Zendesk, Salesforce, JIRA). Skilled in SQL, Python, and workflow automation.

EXPERIENCE:
Deloitte Consulting Pvt. Ltd. | Lead Junior Associate — Operations Support
Hyderabad, India | Jan 2025 – Present
- Troubleshoot and debug transactional data pipelines from Epic Systems using Python and Alteryx, resolving formatting errors to save 8 hours of manual analysis weekly.
- Audit Epic EHR account logs for US healthcare revenue cycle pilots handling USD 2K–6K in daily throughput, identifying validation discrepancies and resolving account sync issues.
- Monitor SLA/TAT compliance dashboards in Tableau and Excel across 3 operational segments, proactively flagging bottleneck trends.
- Placed 12th of 57 teams at Deloitte AWS GameDay building multi-agent systems on AWS Bedrock AgentCore.

MediaMint | Campaign Manager — Performance Reporting
Hyderabad, India | Jul 2024 – Dec 2024
- Monitored ad campaign performance tracking systems (CM360, GA4, GTM), troubleshooting tracking tag fire errors and data discrepancies.
- Analyzed performance anomaly trends using automated GA4 API scripts, contributing to a 15% reduction in technical escalation tickets.

MediaMint | Customer Operations Specialist — CRM & Support
Hyderabad, India | Apr 2023 – Jul 2024
- Resolved 300–450+ complex technical support tickets monthly under strict SLA guidelines via Zendesk, utilizing root-cause analysis.
- Documented and tracked platform bugs in JIRA, collaborating with development teams to test configurations and verify fixes.

SKILLS:
- Core Skills: Epic Systems EHR, Application Support, Troubleshooting, Incident Management, SLA Governance, Anomaly Diagnostics
- Tools & CRMs: Zendesk Support, JIRA Ticket Tracking, Salesforce Admin, Alteryx Workflow, Tableau, SharePoint
- Languages & Data: SQL (DuckDB, PostgreSQL), Python (pandas, Streamlit, API clients), REST APIs, JSON data integrations"""

DEFAULT_JOB_DESCRIPTION = """Accenture - Application Support Engineer
Proficiency in EPIC Systems.
Strong analytical skills to diagnose and resolve software issues.
Experience with troubleshooting and debugging applications.
Familiarity with system integration and data flow management.
Ability to communicate technical information effectively to non-technical users.
Expected to perform independently and become an SME.
Documentation of processes and procedures to enhance team knowledge."""

SYSTEM_PROMPT = """
You are an expert recruitment consultant and career agent. Your task is to customize a candidate's master resume to fit a target job description.

CRITICAL INSTRUCTION FOR TRUTHFULNESS:
1. You MUST NEVER fabricate, exaggerate, or invent any experience, metrics, skills, projects, or job titles.
2. You can ONLY highlight, rephrase, and prioritize existing facts already listed in the candidate's master resume.
3. If a key skill is required in the job description but NOT present in the master resume, do NOT add it. Keep it missing.
4. All adjusted metrics (percentages, values) must exactly match the ones present in the master resume.
5. Output the result in clean Markdown format. Output the final resume ONLY.
"""

def generate_tickets_if_missing():
    try:
        if os.path.exists("tickets.csv"):
            return
        np.random.seed(42)
        random.seed(42)
        num_tickets = 1000

        ticket_ids = [f"TKT-{i+1:05d}" for i in range(num_tickets)]
        priorities = np.random.choice(['Low', 'Medium', 'High'], num_tickets, p=[0.3, 0.5, 0.2])
        categories = np.random.choice(
            ['Billing', 'Technical Support', 'Account Access', 'Delivery Issue'],
            num_tickets, p=[0.3, 0.3, 0.2, 0.2]
        )
        sla_map = {
            ('Billing', 'High'): 12, ('Billing', 'Medium'): 24, ('Billing', 'Low'): 48,
            ('Technical Support', 'High'): 8, ('Technical Support', 'Medium'): 24, ('Technical Support', 'Low'): 48,
            ('Account Access', 'High'): 4, ('Account Access', 'Medium'): 12, ('Account Access', 'Low'): 24,
            ('Delivery Issue', 'High'): 24, ('Delivery Issue', 'Medium'): 48, ('Delivery Issue', 'Low'): 72,
        }
        sla_limits = [sla_map.get((cat, pri), 24) for cat, pri in zip(categories, priorities)]

        now = datetime.now()
        created_ats = [now - timedelta(hours=random.randint(1, 2160)) for _ in range(num_tickets)]
        statuses = np.random.choice(['Open', 'In Progress', 'Resolved'], num_tickets, p=[0.3, 0.4, 0.3])
        elapsed_hours = [round(random.uniform(0, sla_limits[i] * 1.5), 1) for i in range(num_tickets)]

        resolved_ats = []
        for i, status in enumerate(statuses):
            if status == 'Resolved':
                resolved_ats.append((created_ats[i] + timedelta(hours=elapsed_hours[i])).strftime('%Y-%m-%d %H:%M:%S'))
            else:
                resolved_ats.append(None)

        sla_breaches = [1 if elapsed_hours[i] > sla_limits[i] else 0 for i in range(num_tickets)]
        csat_scores = [round(random.uniform(1.0, 5.0), 1) if s == 'Resolved' else None for s in statuses]

        out = pd.DataFrame({
            'ticket_id': ticket_ids,
            'created_at': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in created_ats],
            'resolved_at': resolved_ats,
            'status': statuses,
            'priority': priorities,
            'category': categories,
            'sla_limit_hours': sla_limits,
            'elapsed_hours': elapsed_hours,
            'sla_breach': sla_breaches,
            'csat_score': csat_scores,
        })
        out.to_csv("tickets.csv", index=False)
    except Exception as e:
        st.toast(f"Data Generation Note: {e}")

@st.cache_data
def load_tickets():
    try:
        generate_tickets_if_missing()
        if os.path.exists("tickets.csv"):
            df = pd.read_csv("tickets.csv")
            df["sla_percent"] = (df["elapsed_hours"] / df["sla_limit_hours"] * 100).round(1)
            return df
    except Exception as e:
        st.error(f"Failed loading dataset: {e}")
    # Fallback dummy DataFrame
    return pd.DataFrame({
        'ticket_id': ['TKT-00001'], 'created_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'status': ['Open'], 'priority': ['High'], 'category': ['Technical Support'],
        'sla_limit_hours': [8], 'elapsed_hours': [7.2], 'sla_breach': [0],
        'csat_score': [4.5], 'sla_percent': [90.0]
    })

def send_real_email(sender, app_password, recipient, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient, msg.as_string())
        return True, "Email delivered successfully."
    except Exception as e:
        return False, str(e)

# -----------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & ENGINE CONFIGURATION POPOVER
# -----------------------------------------------------------------------------
if st.session_state.current_page != "intro":
    with st.sidebar:
        st.markdown("<h2 style='margin-bottom:0;'>Enterprise Portal</h2>", unsafe_allow_html=True)
        st.caption("Pavan Kumar V | Operations & AI")
        st.divider()

        # Navigation Control
        st.subheader("🧭 Page Navigation")
        nav_choice = st.radio(
            "Select View:",
            [
                "🏠 Home / 3D Splash Screen",
                "🚨 Project 1: SLA Incident Responder",
                "💼 Project 2: Job-Search Agent"
            ],
            index=0 if st.session_state.current_page == "intro" else (1 if st.session_state.current_page == "p1_sla" else 2)
        )

        # Handle Radio State Changes
        if "Home" in nav_choice and st.session_state.current_page != "intro":
            st.session_state.current_page = "intro"
            st.rerun()
        elif "Project 1" in nav_choice and st.session_state.current_page != "p1_sla":
            st.session_state.current_page = "p1_sla"
            st.rerun()
        elif "Project 2" in nav_choice and st.session_state.current_page != "p2_job":
            st.session_state.current_page = "p2_job"
            st.rerun()

        st.divider()

        # Engine Configuration Inside Popover Dialog (Clean UI requirement)
        with st.popover("⚙️ Engine Configuration", use_container_width=True):
            st.markdown("### 🤖 AI Engine Settings")
            st.session_state.use_claude = st.checkbox("Use Anthropic Claude", value=st.session_state.use_claude)

            if st.session_state.use_claude:
                st.session_state.claude_key = st.text_input("Claude API Key", type="password", value=st.session_state.claude_key)
            else:
                st.session_state.gemini_key = st.text_input("Gemini API Key", type="password", value=st.session_state.gemini_key)
                st.session_state.gemini_model = st.selectbox(
                    "Gemini Model",
                    ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"],
                    index=0
                )

            st.session_state.temperature = st.slider("LLM Temperature", 0.0, 1.0, st.session_state.temperature, 0.1)
            st.session_state.max_tokens = st.slider("Max Tokens", 100, 1000, st.session_state.max_tokens, 50)

            if st.session_state.current_page == "p1_sla":
                st.divider()
                st.markdown("### 📧 Gmail SMTP Settings")
                st.session_state.sender_email = st.text_input("Sender Gmail", value=st.session_state.sender_email)
                st.session_state.sender_app_password = st.text_input("App Password", type="password", value=st.session_state.sender_app_password)
                st.session_state.demo_recipient = st.text_input("Recipient Email", value=st.session_state.demo_recipient)
                st.session_state.threshold = st.slider("SLA Warning %", 50, 100, st.session_state.threshold)

# -----------------------------------------------------------------------------
# 5. PAGE 1: 3D GLASSMORPHISM INTRO & SPLASH SCREEN
# -----------------------------------------------------------------------------
if st.session_state.current_page == "intro":
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    # 3D Glass Floating Hero Card
    st.markdown("""
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="background:rgba(59,130,246,0.15); color:#60A5FA; padding:6px 16px; border-radius:999px; font-size:13px; font-weight:700; border:1px solid rgba(59,130,246,0.3);">
                ⚡ ENTERPRISE AI PORTFOLIO
            </span>
            <span style="color:#94A3B8; font-size:14px;">Pavan Kumar Vaikutherisal · Operations Lead</span>
        </div>
        <h1 style="font-size: 3rem; margin-top: 20px; margin-bottom: 10px; line-height: 1.15;">
            Applied AI for <span class="gradient-text">Operational Efficiency</span>
        </h1>
        <p style="font-size: 1.25rem; color: #94A3B8; max-width: 850px; line-height: 1.6; margin-bottom: 25px;">
            Bridging Reactive Risk Management & Proactive Talent Optimization. Designed for high-volume support centers, automated exception workflows, and guardrailed prompt architectures.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Project Cards
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="glass-card-interactive">
            <h3 style="color:#60A5FA; margin-top:0;">🚨 Project 1: SLA Incident Responder</h3>
            <p style="color:#94A3B8; font-size:0.95rem; line-height:1.5;">
                <b>Reactive Risk Mitigation:</b> Monitors support queues in real-time, isolates tickets reaching 75%+ SLA thresholds, triggers automated Gmail SMTP acknowledgments, and uses Gemini to draft contextual resolution updates.
            </p>
            <ul style="color:#CBD5E1; font-size:0.88rem; padding-left:20px;">
                <li>Real-time KPI metrics & breach tracking</li>
                <li>Interactive Plotly donut & trend charts</li>
                <li>Human-in-the-Loop review & SMTP dispatcher</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Project 1 →", key="btn_intro_p1", use_container_width=True, type="primary"):
            st.session_state.current_page = "p1_sla"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="glass-card-interactive">
            <h3 style="color:#C084FC; margin-top:0;">💼 Project 2: Job-Search & Resume Agent</h3>
            <p style="color:#94A3B8; font-size:0.95rem; line-height:1.5;">
                <b>Proactive Talent Matching:</b> Custom-tailors candidate resumes against target job descriptions using strict zero-fabrication LLM guardrails (temperature 0.2) to ensure 100% factual accuracy.
            </p>
            <ul style="color:#CBD5E1; font-size:0.88rem; padding-left:20px;">
                <li>Side-by-side workspace comparison</li>
                <li>Strict anti-hallucination system prompt rules</li>
                <li>One-click Markdown exporter</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Project 2 →", key="btn_intro_p2", use_container_width=True, type="secondary"):
            st.session_state.current_page = "p2_job"
            st.rerun()

    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)

    # Master CTA Button
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    with col_cta2:
        if st.button("Enter Enterprise Dashboard →", key="btn_enter_dash", use_container_width=True, type="primary"):
            st.session_state.current_page = "p1_sla"
            st.rerun()

# -----------------------------------------------------------------------------
# 6. PAGE 2: SLA INCIDENT RESPONDER (PROJECT 1)
# -----------------------------------------------------------------------------
elif st.session_state.current_page == "p1_sla":
    df = load_tickets()

    # Header Banner
    st.markdown("""
    <div class="gradient-banner">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h2 style="margin:0; color:#F8FAFC;">🚨 SLA Incident Responder</h2>
                <p style="margin:4px 0 0 0; color:#94A3B8;">Reactive Risk Mitigation & Automated Support Triage Console</p>
            </div>
            <span style="background:rgba(239,68,68,0.2); color:#FCA5A5; padding:6px 14px; border-radius:999px; font-weight:700; font-size:12px; border:1px solid rgba(239,68,68,0.4);">
                LIVE QUEUE AUDITOR
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    threshold = st.session_state.threshold
    warning_df = df[(df["sla_percent"] >= threshold) & (df["status"] != "Resolved")].copy()
    warning_df = warning_df.sort_values("sla_percent", ascending=False)
    breached_now = int((warning_df["sla_percent"] >= 100).sum())
    critical_now = int(((warning_df["sla_percent"] >= 90) & (warning_df["sla_percent"] < 100)).sum())
    compliance_rate = round(100 - (df["sla_breach"].sum() / len(df) * 100), 1)

    # Metrics Row with Delta Comparison Stats
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-container">
            <span style="color:#94A3B8; font-size:12px;">TOTAL TICKETS</span>
            <h2 style="margin:4px 0; color:#F8FAFC;">{len(df):,}</h2>
            <span style="color:#10B981; font-size:11px;">↑ Active Queue</span>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-container" style="border-color:rgba(250,204,21,0.3);">
            <span style="color:#94A3B8; font-size:12px;">AT RISK (≥{threshold}% SLA)</span>
            <h2 style="margin:4px 0; color:#FACC15;">{len(warning_df)}</h2>
            <span style="color:#FACC15; font-size:11px;">⚠️ Requires Action</span>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-container" style="border-color:rgba(239,68,68,0.3);">
            <span style="color:#94A3B8; font-size:12px;">BREACHED</span>
            <h2 style="margin:4px 0; color:#EF4444;">{breached_now}</h2>
            <span style="color:#EF4444; font-size:11px;">↓ High Impact</span>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-container" style="border-color:rgba(16,185,129,0.3);">
            <span style="color:#94A3B8; font-size:12px;">OVERALL COMPLIANCE</span>
            <h2 style="margin:4px 0; color:#10B981;">{compliance_rate}%</h2>
            <span style="color:#10B981; font-size:11px;">Target 90.0%</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    def severity(pct):
        if pct >= 100:
            return "#EF4444", "🔴 BREACHED", "badge-breached"
        elif pct >= 90:
            return "#F97316", "🟠 CRITICAL", "badge-critical"
        else:
            return "#FACC15", "🟡 WATCH", "badge-watch"

    tab_action, tab_insights = st.tabs(["🎫 Ticket Action Center", "📊 Insights & Analytics"])

    with tab_action:
        col_list, col_detail = st.columns([1, 1.4])

        with col_list:
            st.subheader("Tickets at Risk")
            st.caption(f"Sorted worst-first · {breached_now} breached · {critical_now} critical")

            if warning_df.empty:
                st.success("No tickets currently at risk. 🎉")
            else:
                for _, row in warning_df.head(25).iterrows():
                    color, label, badge_class = severity(row["sla_percent"])
                    is_selected = st.session_state.selected_ticket_id == row["ticket_id"]
                    border = "3px solid #38BDF8" if is_selected else f"4px solid {color}"

                    st.markdown(
                        f"""<div style="background:rgba(30,41,59,0.5); padding:12px 14px; border-radius:10px; border-left:{border}; margin-bottom:8px;">
                            <b>{row['ticket_id']}</b>
                            <span class="badge {badge_class}">{label}</span><br>
                            <span style="color:#94A3B8; font-size:13px">{row['category']} · {row['priority']} priority</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    st.progress(min(int(row["sla_percent"]), 100) / 100)

                    already_sent = row["ticket_id"] in st.session_state.first_response_sent
                    b1, b2 = st.columns(2)

                    if b1.button("Select Ticket →", key=f"btn_{row['ticket_id']}", use_container_width=True):
                        st.session_state.selected_ticket_id = row["ticket_id"]
                        st.session_state.generated_draft = None

                    if already_sent:
                        b2.button("✅ Response Sent", key=f"sent_{row['ticket_id']}", use_container_width=True, disabled=True)
                    else:
                        if b2.button("📧 First Response", key=f"auto_{row['ticket_id']}", use_container_width=True):
                            st.session_state.show_first_response_preview[row["ticket_id"]] = True
                            st.rerun()

                    if st.session_state.show_first_response_preview.get(row["ticket_id"], False):
                        st.divider()
                        st.write("**Email Preview:**")
                        st.text_area("Fixed Template:", value=FIRST_RESPONSE_TEMPLATE, height=140, disabled=True)
                        col_a, col_b = st.columns(2)
                        if col_a.button("Confirm & Send", key=f"confirm_{row['ticket_id']}", type="primary", use_container_width=True):
                            success, msg = send_real_email(
                                st.session_state.sender_email,
                                st.session_state.sender_app_password,
                                st.session_state.demo_recipient,
                                f"Ticket Acknowledgment — {row['ticket_id']}",
                                FIRST_RESPONSE_TEMPLATE
                            )
                            if success:
                                st.session_state.first_response_sent.add(row["ticket_id"])
                                st.session_state.approval_history.append({
                                    "time": datetime.now().strftime("%H:%M:%S"),
                                    "ticket_id": row["ticket_id"],
                                    "type": "first_response",
                                    "draft": FIRST_RESPONSE_TEMPLATE,
                                })
                                st.session_state.show_first_response_preview[row["ticket_id"]] = False
                                st.toast(f"Email delivered to {st.session_state.demo_recipient}!")
                                st.rerun()
                            else:
                                st.error(f"Send Failed: {msg}. Configure credentials in Engine Configuration.")
                        if col_b.button("Cancel", key=f"cancel_{row['ticket_id']}", use_container_width=True):
                            st.session_state.show_first_response_preview[row["ticket_id"]] = False
                            st.rerun()
                        st.divider()

                    st.write("")

        with col_detail:
            st.subheader("Ticket Detail & AI Resolution Update")

            if st.session_state.selected_ticket_id is None:
                st.info("👈 Select a ticket from the left queue to view details and generate AI drafts.")
            else:
                ticket = df[df["ticket_id"] == st.session_state.selected_ticket_id].iloc[0]
                color, label, _ = severity(ticket["sla_percent"])

                st.markdown(f"### {ticket['ticket_id']} &nbsp; <span style='color:{color}'>{label}</span>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Priority", ticket["priority"])
                c2.metric("Category", ticket["category"])
                c3.metric("SLA Used", f"{ticket['sla_percent']:.0f}%")

                st.progress(min(int(ticket["sla_percent"]), 100) / 100)
                st.caption(f"Created: {ticket['created_at']}  ·  Elapsed: {ticket['elapsed_hours']:.1f}h of {ticket['sla_limit_hours']:.0f}h limit")

                st.divider()

                if st.button("✨ Generate Resolution Update", type="primary", use_container_width=True):
                    with st.spinner("AI is drafting resolution update..."):
                        prompt = (
                            "You are a support manager writing a short update email to a customer "
                            "after working on their support ticket. This is a status update as you resolve the issue.\n\n"
                            f"Ticket ID: {ticket['ticket_id']}\nCategory: {ticket['category']}\n"
                            f"Priority: {ticket['priority']}\nElapsed: {ticket['elapsed_hours']:.1f}h of {ticket['sla_limit_hours']:.0f}h\n\n"
                            "Write the ACTUAL EMAIL TEXT ONLY starting with 'Hi there,' and ending with sign-off. Under 140 words."
                        )
                        try:
                            if st.session_state.use_claude:
                                if not st.session_state.claude_key:
                                    st.error("Enter Anthropic Claude API Key in Engine Configuration popover.")
                                else:
                                    client = anthropic.Anthropic(api_key=st.session_state.claude_key)
                                    msg = client.messages.create(
                                        model="claude-3-5-sonnet",
                                        max_tokens=st.session_state.max_tokens,
                                        temperature=st.session_state.temperature,
                                        messages=[{"role": "user", "content": prompt}]
                                    )
                                    st.session_state.generated_draft = msg.content[0].text
                            else:
                                if not st.session_state.gemini_key:
                                    st.error("Enter Google Gemini API Key in Engine Configuration popover.")
                                else:
                                    client = genai.Client(api_key=st.session_state.gemini_key)
                                    resp = client.models.generate_content(
                                        model=st.session_state.gemini_model,
                                        contents=prompt,
                                        config={
                                            "temperature": st.session_state.temperature,
                                            "max_output_tokens": st.session_state.max_tokens,
                                            "thinking_config": {"thinking_budget": 0},
                                        }
                                    )
                                    st.session_state.generated_draft = resp.text
                        except Exception as e:
                            st.error(f"API Draft Generation Error: {e}")

                if st.session_state.generated_draft:
                    draft = st.text_area("📝 Draft Resolution Update (editable):", value=st.session_state.generated_draft, height=160)
                    b1, b2 = st.columns(2)
                    if b1.button("✅ Approve & Queue", type="primary", use_container_width=True):
                        st.session_state.approval_history.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "ticket_id": ticket["ticket_id"],
                            "type": "resolution_update",
                            "draft": draft,
                        })
                        st.toast(f"Approved resolution draft for {ticket['ticket_id']}!")
                        st.session_state.generated_draft = None
                        st.rerun()
                    if b2.button("❌ Discard", use_container_width=True):
                        st.session_state.generated_draft = None
                        st.rerun()

                if st.session_state.approval_history:
                    st.divider()
                    st.write("**Approved Activity Log:**")
                    for rec in reversed(st.session_state.approval_history[-4:]):
                        with st.expander(f"{rec['ticket_id']} — {rec['time']}"):
                            st.text_area("", value=rec["draft"], height=100, disabled=True)

    with tab_insights:
        st.subheader("Queue Performance Analytics & Visualizations")

        col_ch1, col_ch2 = st.columns(2)

        with col_ch1:
            st.markdown("**Status Breakdown Distribution**")
            if HAS_PLOTLY:
                status_counts = df["status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                fig_donut = px.pie(
                    status_counts, values="Count", names="Status", hole=0.5,
                    color_discrete_sequence=["#38BDF8", "#F97316", "#10B981"]
                )
                fig_donut.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#F8FAFC", margin=dict(t=20, b=20, l=20, r=20), height=280
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.dataframe(df["status"].value_counts(), use_container_width=True)

        with col_ch2:
            st.markdown("**SLA Breaches by Category (Pareto)**")
            resolved_df = df[df["status"] == "Resolved"]
            if not resolved_df.empty:
                cat_breaches = resolved_df.groupby("category")["sla_breach"].sum().reset_index()
                if HAS_PLOTLY:
                    fig_bar = px.bar(
                        cat_breaches, x="category", y="sla_breach",
                        color="category", color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_bar.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#F8FAFC", margin=dict(t=20, b=20, l=20, r=20), height=280, showlegend=False
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.dataframe(cat_breaches, use_container_width=True)

        st.markdown("**High-Priority Warning Table**")
        st.dataframe(
            warning_df[["ticket_id", "category", "priority", "elapsed_hours", "sla_limit_hours", "sla_percent"]].head(15),
            use_container_width=True,
            hide_index=True
        )

# -----------------------------------------------------------------------------
# 7. PAGE 3: JOB-SEARCH & RESUME-TAILORING AGENT (PROJECT 2)
# -----------------------------------------------------------------------------
elif st.session_state.current_page == "p2_job":
    st.markdown("""
    <div class="gradient-banner">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h2 style="margin:0; color:#F8FAFC;">💼 Job-Search & Resume-Tailoring Agent</h2>
                <p style="margin:4px 0 0 0; color:#94A3B8;">Guardrailed Semantic Profile Alignment & 0% Fabrication Pipeline</p>
            </div>
            <span style="background:rgba(192,132,252,0.2); color:#E9D5FF; padding:6px 14px; border-radius:999px; font-weight:700; font-size:12px; border:1px solid rgba(192,132,252,0.4);">
                LLM GUARDRAILS ACTIVE
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.markdown("### 📥 Candidate Inputs")
        master_resume = st.text_area("Master Experience Profile:", value=DEFAULT_MASTER_RESUME, height=220)
        job_desc = st.text_area("Target Job Description (JD):", value=DEFAULT_JOB_DESCRIPTION, height=180)

        if st.button("🚀 Tailor Resume", type="primary", use_container_width=True):
            with st.spinner("Applying semantic alignment & anti-fabrication guardrails..."):
                prompt = f"""
                Here is my Master Resume:
                <master_resume>
                {master_resume}
                </master_resume>

                Here is the Target Job Description:
                <job_description>
                {job_desc}
                </job_description>

                Customize my resume to highlight operational experience matching the JD. Follow all strict guardrails.
                """
                try:
                    if st.session_state.use_claude:
                        if not st.session_state.claude_key:
                            st.error("Enter Anthropic Claude API Key in Engine Configuration popover.")
                        else:
                            client = anthropic.Anthropic(api_key=st.session_state.claude_key)
                            msg = client.messages.create(
                                model="claude-3-5-sonnet",
                                max_tokens=st.session_state.max_tokens,
                                temperature=st.session_state.temperature,
                                system=SYSTEM_PROMPT,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            st.session_state.tailored_output = msg.content[0].text
                    else:
                        if not st.session_state.gemini_key:
                            st.error("Enter Google Gemini API Key in Engine Configuration popover.")
                        else:
                            client = genai.Client(api_key=st.session_state.gemini_key)
                            resp = client.models.generate_content(
                                model=st.session_state.gemini_model,
                                contents=prompt,
                                config={
                                    "system_instruction": SYSTEM_PROMPT,
                                    "temperature": st.session_state.temperature,
                                    "max_output_tokens": st.session_state.max_tokens,
                                    "thinking_config": {"thinking_budget": 0},
                                }
                            )
                            st.session_state.tailored_output = resp.text
                    st.toast("Resume tailored factually!")
                except Exception as e:
                    st.error(f"Tailoring Error: {e}")

    with col_output:
        st.markdown("### 📝 Tailored Resume Output")
        if st.session_state.tailored_output:
            st.markdown(st.session_state.tailored_output)
            st.divider()
            st.download_button(
                label="📥 Download Tailored Resume (Markdown)",
                data=st.session_state.tailored_output,
                file_name="Tailored_Resume.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.info("Paste a target Job Description on the left and click 'Tailor Resume' to generate a tailored profile.")
