import streamlit as st
from google import genai

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
- Languages & Data: SQL (DuckDB, PostgreSQL), Python (pandas, Streamlit, API clients), REST APIs, JSON data integrations

EDUCATION & CERTIFICATIONS:
- MBA, Operations Management — IGNOU (Distance) | Expected 2027
- BBA, Business Analytics — Koneru Lakshmaiah University | 2023
- Certifications: Epic Systems Revenue Cycle (Deloitte Training) · Alteryx Designer Core · AWS Bedrock & Generative AI"""

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


def show_page():
    if "tailored_output" not in st.session_state:
        st.session_state.tailored_output = None

    st.markdown("""
    <div class="hero" style="padding:24px 30px;">
        <h1 style="font-size:1.6rem;">💼 Job-Search & Resume-Tailoring Agent</h1>
        <p>Proactive operations: tailor a verified experience profile against any JD — with a hard anti-fabrication guardrail.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-card">
        <b style="color:#1E293B">🛡️ The guardrail:</b>
        <span style="color:#475569"> the model may reorganize and re-emphasize verified experience —
        it may never invent a skill, metric, or title. If the JD asks for something not in the source
        profile, the correct output is silence on that skill, not an invented line.</span>
    </div>
    """, unsafe_allow_html=True)

    api_key = st.session_state.get("gemini_key", "")
    model_choice = st.session_state.get("gemini_model", "gemini-flash-latest")
    temperature = st.session_state.get("temperature", 0.3)
    max_tokens = st.session_state.get("max_tokens", 450)
    use_claude = st.session_state.get("use_claude", False)
    claude_key = st.session_state.get("claude_key", "")
    claude_model = st.session_state.get("claude_model", "claude-haiku-4-5-20251001")

    col_input, col_tailor = st.columns([1, 1.3])

    with col_input:
        st.markdown("#### Inputs")
        master_resume = st.text_area("Your Master Experience Profile:", value=DEFAULT_MASTER_RESUME, height=240)
        job_desc = st.text_area("Paste Target Job Description (JD):", value=DEFAULT_JOB_DESCRIPTION, height=200)
        tailor_btn = st.button("🚀 Tailor Resume", type="primary", width="stretch")

    with col_tailor:
        st.markdown("#### 📝 Tailored Resume Output")

        if tailor_btn:
            if use_claude and not claude_key:
                st.warning("Open **⚙️ Advanced Settings** in the sidebar and add your Claude API key first.")
            elif not use_claude and not api_key:
                st.warning("Open **⚙️ Advanced Settings** in the sidebar and add your Gemini API key first.")
            elif not master_resume.strip() or not job_desc.strip():
                st.warning("Both the master profile and the job description need content before tailoring.")
            else:
                with st.spinner("Tailoring your experience profile against the JD..."):
                    prompt = f"""
Here is my Master Resume:
<master_resume>
{master_resume}
</master_resume>

Here is the Target Job Description:
<job_description>
{job_desc}
</job_description>

Please customize my resume by highlighting my most relevant operations and Epic systems experiences that align with the job description. Follow the strict anti-fabrication rules provided in the system prompt.
"""
                    try:
                        if use_claude:
                            import anthropic
                            client = anthropic.Anthropic(api_key=claude_key)
                            message = client.messages.create(
                                model=claude_model,
                                max_tokens=max_tokens,
                                temperature=temperature,
                                system=SYSTEM_PROMPT,
                                messages=[{"role": "user", "content": prompt}],
                            )
                            st.session_state.tailored_output = message.content[0].text
                        else:
                            client = genai.Client(api_key=api_key)
                            resp = client.models.generate_content(
                                model=model_choice,
                                contents=prompt,
                                config={
                                    "system_instruction": SYSTEM_PROMPT,
                                    "temperature": temperature,
                                    "max_output_tokens": max_tokens,
                                    "thinking_config": {"thinking_budget": 0},
                                },
                            )
                            st.session_state.tailored_output = resp.text
                        st.toast("Resume tailored factually", icon="✅")
                    except Exception as e:
                        st.error("The tailoring call didn't go through — try a different model under "
                                 f"**⚙️ Advanced Settings** in the sidebar. ({e})")

        if st.session_state.tailored_output:
            st.markdown(st.session_state.tailored_output)
            st.divider()
            st.download_button(
                label="📥 Download Tailored Resume (Markdown)",
                data=st.session_state.tailored_output,
                file_name="Tailored_Resume.md",
                mime="text/markdown",
                width="stretch",
            )
        else:
            st.info("Paste a Job Description on the left and click 'Tailor Resume' to generate a tailored factual profile.")
