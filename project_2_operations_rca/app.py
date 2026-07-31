import sys
import os

# Add root folder to path so parent-level imports work when running from any sub-directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="Enterprise Analytics & AI Portfolio",
    layout="wide",
    page_icon="💼",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global theme: deep navy enterprise dashboard, teal + orange accents
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Hide default Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* App background: soft, bright, easy on the eyes */
    .stApp {
        background: linear-gradient(180deg, #F8FAFF 0%, #F1F5F9 100%);
        color: #1E293B;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Headings */
    h1, h2, h3, h4 { color: #1E293B !important; font-weight: 700; }

    /* KPI cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #6366F1;
        border-radius: 14px;
        padding: 18px 14px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(99,102,241,0.08);
    }
    .kpi-card h2 { margin: 0; font-size: 1.9rem; color: #1E293B; }
    .kpi-card span { color: #64748B; font-size: 0.85rem; }

    /* Content cards */
    .content-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(15,23,42,0.05);
    }
    .ticket-card {
        border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;
        border-left: 5px solid #CBD5E1; background: #FFFFFF;
        border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;
        box-shadow: 0 1px 4px rgba(15,23,42,0.05);
    }
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 999px;
        font-size: 11px; font-weight: 700; color: white; margin-left: 6px;
    }
    .badge-breached { background: #DC2626; }
    .badge-critical { background: #EA580C; }
    .badge-watch { background: #D97706; }

    /* Hero banner: vibrant gradient, white text */
    .hero {
        background: linear-gradient(120deg, #4F46E5 0%, #7C3AED 50%, #0D9488 100%);
        color: white; padding: 34px 38px; border-radius: 18px;
        margin-bottom: 26px; box-shadow: 0 10px 26px rgba(79,70,229,0.28);
    }
    .hero h1 { margin: 0; font-size: 2.1rem; color: white !important; }
    .hero p { margin: 10px 0 0 0; color: #E0E7FF; font-size: 1.02rem; }

    .accent-indigo { color: #4F46E5; }
    .accent-teal { color: #0D9488; }
    .accent-orange { color: #EA580C; }

    .pill {
        display: inline-block; background: #EEF2FF; color: #4F46E5;
        border: 1px solid #C7D2FE; border-radius: 999px;
        padding: 3px 12px; font-size: 12px; font-weight: 600; margin: 3px 4px 3px 0;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #C7D2FE;
        background: #FFFFFF;
        color: #4F46E5;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton > button:hover { border-color: #4F46E5; background: #EEF2FF; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5, #6366F1);
        border: none; color: white;
        box-shadow: 0 4px 12px rgba(79,70,229,0.3);
    }
    .stButton > button[kind="primary"]:hover { filter: brightness(1.08); color: white; }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: #FFFFFF !important; color: #1E293B !important;
        border: 1px solid #CBD5E1 !important; border-radius: 10px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF; border-radius: 10px 10px 0 0;
        border: 1px solid #E2E8F0; border-bottom: none;
        padding: 8px 18px; color: #64748B; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { color: #4F46E5 !important; border-color: #4F46E5; }

    /* Expanders */
    details {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] { border: 1px solid #E2E8F0; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar: clean navigation + collapsed advanced settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 💼 Enterprise AI Portfolio")
    st.caption("Pavan Kumar Vaikutherisal · Operations & Analytics Strategist")
    st.divider()

    selected_page = st.radio(
        "Navigate",
        ["🏠 Home", "🚨 Project 1: SLA Incident Responder", "💼 Project 2: Job-Search Agent"],
        label_visibility="collapsed",
    )

    st.divider()

    with st.expander("⚙️ Advanced Settings", expanded=False):
        use_claude = st.checkbox("Use Anthropic Claude (instead of Gemini)")
        st.session_state.use_claude = use_claude

        if use_claude:
            claude_key = st.text_input("Anthropic Claude API Key", type="password",
                                       value=st.session_state.get("claude_key", ""))
            st.session_state.claude_key = claude_key
            st.session_state.claude_model = st.selectbox(
                "Claude Model",
                ["claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"],
                index=0,
            )
        else:
            gemini_key = st.text_input("Google Gemini API Key", type="password",
                                       value=st.session_state.get("gemini_key", ""))
            st.session_state.gemini_key = gemini_key
            st.session_state.gemini_model = st.selectbox(
                "Gemini Model",
                ["gemini-flash-latest", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
                index=0,
            )

        st.session_state.temperature = st.slider("LLM Temperature", 0.0, 1.0, 0.3, 0.1)
        st.session_state.max_tokens = st.slider("LLM Max Tokens", 100, 1000, 450, 50)

    with st.expander("📧 Email (SMTP) Settings", expanded=False):
        st.caption("Gmail App Password required (not your normal password).")
        st.session_state.sender_email = st.text_input(
            "Sender Gmail", value=st.session_state.get("sender_email", "pavanwork111@gmail.com"))
        st.session_state.sender_app_password = st.text_input(
            "Gmail App Password", type="password",
            value=st.session_state.get("sender_app_password", ""))
        st.session_state.demo_recipient = st.text_input(
            "Recipient Email", value=st.session_state.get("demo_recipient", "pavanwork111@gmail.com"))

    st.session_state.threshold = 75

# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------
def show_home():
    st.markdown("""
    <div class="hero">
        <h1>Applied AI for Operational Efficiency</h1>
        <p>Two live systems. One idea: put the LLM only where judgment is needed, and a human before anything ships.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-card">
        <h3>👋 About this portfolio</h3>
        <p style="color:#475569">
        I'm an Operations & Analytics Strategist. At Deloitte I took an undefined operations problem
        from scoping to a 90% inventory reduction in 28 days. These projects apply the same instinct
        with LLMs: find where the work is high-volume and language-heavy, automate exactly that,
        and keep a human approval gate on everything customer-facing.
        </p>
        <span class="pill">Python</span><span class="pill">Streamlit</span><span class="pill">SQL · DuckDB</span>
        <span class="pill">Gemini API</span><span class="pill">Claude API</span><span class="pill">Gmail SMTP</span>
        <span class="pill">Plotly</span><span class="pill">Human-in-the-loop</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="content-card">
            <h3>🚨 <span class="accent-orange">Reactive Ops</span> — SLA Incident Responder</h3>
            <p style="color:#475569">
            Watches 1,000 live support tickets, flags anything past 75% of its SLA window,
            auto-sends a fixed first response by real email, and drafts AI resolution updates
            that a human reviews before approval. Includes a full analytics view: breach Pareto,
            CSAT impact, weekly trends.
            </p>
            <p style="color:#64748B;font-size:0.85rem">
            The design decision: the first response is a template on purpose — speed and consistency,
            no judgment needed. The AI only writes where reasoning about the specific ticket matters.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="content-card">
            <h3>💼 <span class="accent-teal">Proactive Ops</span> — Job-Search Agent</h3>
            <p style="color:#475569">
            Tailors a master resume against any pasted job description through an LLM with a hard
            anti-fabrication constraint: it can reorganize and emphasize verified experience,
            but can never invent a skill, metric, or title. Output downloads as clean Markdown.
            </p>
            <p style="color:#64748B;font-size:0.85rem">
            The design decision: hallucination treated as a design problem, not a surprise —
            the system prompt bans generation of anything not present in the source profile.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-card">
        <h3>🧭 How to explore</h3>
        <p style="color:#475569">
        Pick a project from the sidebar. Add a Gemini API key under <b>Advanced Settings</b> to run
        the AI features live; the dashboards and analytics work without any key.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Routing with friendly error handling
# ---------------------------------------------------------------------------
if selected_page == "🏠 Home":
    show_home()

elif selected_page == "🚨 Project 1: SLA Incident Responder":
    try:
        import project_1_operations_rca.app_page as p1_page
        p1_page.show_page()
    except Exception as e:
        st.error(f"⚠️ The SLA dashboard hit an unexpected issue: {e}")

elif selected_page == "💼 Project 2: Job-Search Agent":
    try:
        import project_2_job_agent.app_page as p2_page
        p2_page.show_page()
    except Exception as e:
        st.error(f"⚠️ The Job-Search Agent hit an unexpected issue: {e}")
