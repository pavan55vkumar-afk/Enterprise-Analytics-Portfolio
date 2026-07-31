# Enterprise Analytics & AI Portfolio — Pavan Kumar Vaikutherisal

Welcome to my portfolio! I am an Operations Analyst & Business Strategist with 3+ years of client-facing experience at Deloitte and MediaMint. 

I specialize in managing, auditing, and troubleshooting high-volume transaction systems (Epic Systems EHR, Zendesk, JIRA, Salesforce) and applying AI/LLM automation to solve operational bottlenecks.

Each project below represents an operational challenge I tackled, demonstrating how Python, SQL, Streamlit, and LLM prompt engineering turn high-volume operational logs into proactive, zero-fabrication automated systems.

---

## 🚀 Interactive Streamlit Web Application

👉 **[Live Enterprise AI Portfolio Dashboard](https://enterprise-analytics-portfolio-nsbdpzsq8qyra3tqxs7swa.streamlit.app/)**

Explore both live projects in an interactive control console built with Streamlit, Plotly, and AI API integrations.

---

## 📁 Projects Showcase

### 1. 🚨 SLA Incident Warning & Response System (`project_1_operations_rca`)

**Business Challenge:** How can support operations teams prevent customer satisfaction (CSAT) crashes when service tickets approach their SLA expiration window?

**Solution Delivered:** A Streamlit incident triage console and automated alerting pipeline. It flags tickets reaching 75%+ SLA elapsed threshold, triggers immediate first responses via Gmail SMTP SSL, and leverages LLMs to draft contextual resolution updates for human approval.

**Key Features & Findings:**
- **CSAT Quantified:** Demonstrated that SLA breaches cause a catastrophic CSAT rating drop from **3.98/5.0 down to 1.44/5.0** (a 2.54-point drop).
- **Automated First Acknowledgment:** Fired instant template acknowledgments via Gmail SMTP port 465 to confirm receipt without agent overhead.
- **Human-in-the-Loop AI Drafts:** Utilized Gemini/Claude to draft warm, factual resolution updates based on ticket category and priority, keeping human review before sending.
- **Analytics & Bottlenecks:** Integrated Plotly Pareto charts isolating *Delivery Issues* as the primary 80/20 breach bottleneck.

📂 **[View Project 1 Case Study & Source Code](./project_1_operations_rca/README.md)**

---

### 2. 💼 AI Job-Search & Resume-Tailoring Agent (`project_2_job_agent`)

**Business Challenge:** How can candidates automate high-volume resume customization for target job descriptions while guaranteeing **100% factual truthfulness and zero fabrication**?

**Solution Delivered:** An AI prompt engineering pipeline and Streamlit workspace that extracts key competencies from target Job Descriptions and aligns them with a candidate's master experience profile under strict anti-hallucination guardrails.

**Key Features & Findings:**
- **Zero-Fabrication Guardrail:** Engineered system prompts that strictly prohibit inventing skills, metrics, or titles not present in the master profile.
- **Deterministic Generation:** Configured a low-temperature (`0.2 / 0.3`) sampling parameter to ensure factual, repeatable profile alignment.
- **Time Savings:** Reduced manual resume tailoring time from **45 minutes to under 10 seconds** per application.
- **One-Click Export:** Renders formatted, ATS-friendly Markdown outputs ready for immediate application submission.

📂 **[View Project 2 Case Study & Source Code](./project_2_job_agent/README.md)**

---

## 🛠️ Core Technical Skills

- **Operations & Systems:** Epic Systems EHR, SLA Triage, Incident Management, Anomaly Diagnostics, Process SOP Documentation
- **Tools & CRMs:** Zendesk Support, JIRA Ticketing, Salesforce Admin, Tableau, Alteryx Workflow
- **Data & Scripting:** SQL (DuckDB, PostgreSQL, CTEs, Window Functions), Python (pandas, numpy, Streamlit, Plotly)
- **AI & Prompt Engineering:** Anthropic Claude API, Google Gemini API, Zero-Fabrication Guardrails, System Prompt Architecture
