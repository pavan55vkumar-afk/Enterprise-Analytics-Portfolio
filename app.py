import streamlit as st

# Set single page config for the entire multi-page app
st.set_page_config(
    page_title="Enterprise Analytics & AI Portfolio",
    layout="wide",
    page_icon="💼"
)

# Shared Custom CSS for the unified portal
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    h1 { color: #1E293B; font-weight: 800; margin-bottom: 0.2rem; }
    h2 { color: #334155; }
    .project-header {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        color: white; padding: 20px 25px; border-radius: 12px;
        margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Shared Configurations
with st.sidebar:
    st.image("https://img.icons8.com/clouds/150/000000/artificial-intelligence.png", width=90)
    st.title("Enterprise AI Portfolio")
    st.caption("Pavan Kumar Vaikutherisal | Operations & Analytics")
    
    st.divider()
    
    # 1. Project Navigation Selection
    st.subheader("📁 Select Project Showcase")
    selected_project = st.radio(
        "Navigate pages:",
        [
            "🚨 Project 2: SLA Incident Responder",
            "💼 Project 3: Job-Search Agent"
        ]
    )

    st.divider()

    # 2. Shared API Credentials
    st.subheader("🔑 AI Credentials")
    
    use_claude = st.checkbox("Use Anthropic Claude (instead of Gemini)")
    st.session_state.use_claude = use_claude

    if use_claude:
        claude_key = st.text_input("Anthropic Claude API Key", type="password", value=st.session_state.get("claude_key", ""))
        st.session_state.claude_key = claude_key
    else:
        gemini_key = st.text_input("Google Gemini API Key", type="password", value=st.session_state.get("gemini_key", ""))
        st.session_state.gemini_key = gemini_key

    # Hidden or default models
    st.session_state.gemini_model = "gemini-2.0-flash"
    
    # Sliders
    st.session_state.temperature = st.slider("LLM Temperature", 0.0, 1.0, 0.3, 0.1)
    st.session_state.max_tokens = st.slider("LLM Max Tokens", 100, 1000, 450, 50)

    # 3. SMTP parameters (Project 2 only)
    if selected_project == "🚨 Project 2: SLA Incident Responder":
        st.divider()
        st.subheader("📧 Real Email SMTP settings")
        st.caption("App Passwords required to bypass Gmail MFA.")
        st.session_state.sender_email = st.text_input("Sender Gmail", value=st.session_state.get("sender_email", "pavanwork111@gmail.com"))
        st.session_state.sender_app_password = st.text_input("Gmail App Password", type="password", value=st.session_state.get("sender_app_password", ""))
        st.session_state.demo_recipient = st.text_input("Recipient Email", value=st.session_state.get("demo_recipient", "pavanwork111@gmail.com"))
        st.session_state.threshold = st.slider("SLA warning threshold (%)", 50, 100, 75)

# Render main banner
st.markdown(
    f"""<div class="project-header">
        <h1 style='color:white;margin:0;'>Enterprise Analytics & AI Portfolio Portal</h1>
        <p style='margin:5px 0 0 0;opacity:0.8;'>Demonstrating FDE Strategist Case Studies: SLA Incident Dashboard & AI Resume-Tailoring Agent.</p>
    </div>""",
    unsafe_allow_html=True
)

# Route execution to correct page
if selected_project == "🚨 Project 2: SLA Incident Responder":
    import project_2_operations_rca.app_page as p2_page
    p2_page.show_page()
    
elif selected_project == "💼 Project 3: Job-Search Agent":
    import project_3_job_agent.app_page as p3_page
    p3_page.show_page()
