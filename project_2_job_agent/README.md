# AI Job-Search & Resume-Tailoring Agent

**Business question:** Custom-tailoring a resume for complex operational and technical roles takes up to 45 minutes per application. Standard generative AI tools are prone to hallucinating experience and metrics, which erodes trust. How can we automate this process while maintaining a strict, 100% truthfulness constraint?

---

## 🛠️ The Technical Approach

I built a Python CLI tool using the **Claude API** (`claude-3-5-sonnet`) to ingest job descriptions and automate custom resume rewrites. The tool focuses on **structural relevance** rather than content generation.

### Key Architecture & Safeguards
1.  **Anti-Fabrication System Prompt:** Enforces a rigid rule: *No content generation.* Claude is restricted to only reorganizing, highlighting, and prioritizing verified facts from my master experience file.
2.  **Deterministic Temperature (0.2):** Keeps the model's output highly grounded and predictable, preventing creative writing or hallucinated metrics.
3.  **Keyword Vector Matcher:** Automatically extracts key operational requirements from the job description and parses my master experience to highlight identical competencies (e.g., SLA monitoring, Zendesk/Salesforce, or Python analytics).

---

## ⚙️ How It Works (Execution Flow)

1.  **Ingestion:** The script loads two plain text inputs:
    *   `master_experience.txt` (a source list of all my operations, certificates, and historical project metrics).
    *   `job_description.txt` (the target job description).
2.  **Payload Packing:** Formats the input texts into structured XML tags (`<master_resume>` and `<job_description>`).
3.  **API Call:** Calls `claude-3-5-sonnet` with a low temperature of `0.2` and strict system formatting instructions.
4.  **Markdown Compilation:** Exports a clean, print-ready `.md` file containing the tailored version of the resume in seconds.

---

## 💻 Script Structure

*   `job_agent.py`: Main CLI execution file (accepts arguments for `--resume`, `--job`, and `--output`).
*   `SYSTEM_PROMPT`: The prompt logic containing strict rules for factual verification and section formatting.

---

## 📈 Selected Capabilities & Impact
*   **Time Savings:** Reduced manual tailoring time from **45 minutes to under 10 seconds** per application.
*   **Accuracy:** Achieved a **0% fabrication rate** across 20+ test runs by anchoring the model strictly to source experience XML data.
*   **FDE Practicality:** Demonstrated a rapid, utility-first deployment of LLM APIs to automate a high-volume personal productivity workflow.
