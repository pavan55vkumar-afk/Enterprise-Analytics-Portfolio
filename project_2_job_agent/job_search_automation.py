import os
import sys
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuration for Job Search Agent
TARGET_ROLES = ["Business Analyst (BA)", "Data Analyst (DA)", "Forward Deployed Engineer (FDE) / Solutions Engineer"]
LOCATIONS = ["Hyderabad", "Bengaluru", "Remote (India)"]
DEFAULT_RECIPIENT = "pavanwork111@gmail.com"
CC_RECIPIENT = "pavan55vkumar@gmail.com"

# Master Candidate Skills for Matching
CANDIDATE_SKILLS = [
    "Epic Systems EHR", "SQL (DuckDB, PostgreSQL)", "Python (pandas, API clients)",
    "Zendesk Support", "JIRA Bug Tracking", "Salesforce Admin", "Alteryx Workflow",
    "SLA / TAT Governance", "Root Cause Analysis (RCA)", "AWS Bedrock / Gemini / Claude APIs"
]

def fetch_sample_live_jobs():
    """Simulates real-time job aggregation for BA, DA, and FDE roles across tech hubs."""
    jobs = [
        {
            "job_id": "JOB-FDE-01",
            "title": "Forward Deployed Engineer (FDE) - Analytics & AI",
            "company": "Palantir / Enterprise AI Systems",
            "location": "Bengaluru (Hybrid)",
            "role_category": "Forward Deployed Engineer (FDE)",
            "required_skills": ["Python", "SQL", "Client-facing Problem Solving", "Data Pipelines", "API Integrations"],
            "match_score": 96,
            "link": "https://www.linkedin.com/jobs/view/fde-analytics-ai",
            "description": "Work directly with client operations teams to deploy data pipelines, troubleshoot system integrations, and configure customized AI/LLM workflows."
        },
        {
            "job_id": "JOB-FDE-02",
            "title": "Forward Deployed Solutions Engineer",
            "company": "Samsara / Healthcare Analytics",
            "location": "Hyderabad (Remote/Hybrid)",
            "role_category": "Forward Deployed Engineer (FDE)",
            "required_skills": ["Epic EHR Integration", "Troubleshooting", "SQL", "Zendesk/JIRA", "Python"],
            "match_score": 94,
            "link": "https://www.naukri.com/job-listings-forward-deployed-engineer",
            "description": "Drive technical deployment and data validation for enterprise healthcare clients. Troubleshoot EHR data synchronization issues and monitor SLA performance."
        },
        {
            "job_id": "JOB-BA-03",
            "title": "Senior Operations & Business Analyst",
            "company": "Deloitte / US Healthcare Ops",
            "location": "Hyderabad",
            "role_category": "Business Analyst (BA)",
            "required_skills": ["SLA Monitoring", "Root Cause Analysis", "Tableau/Excel", "SQL", "Process SOPs"],
            "match_score": 92,
            "link": "https://www.deloitte.com/careers/business-analyst-ops",
            "description": "Analyze operations bottlenecks, audit billing accounts, and build SLA compliance dashboards to optimize revenue cycle management."
        },
        {
            "job_id": "JOB-DA-04",
            "title": "Product Data Analyst - Incident Management",
            "company": "MediaMint / Tech Ops",
            "location": "Bengaluru / Remote",
            "role_category": "Data Analyst (DA)",
            "required_skills": ["Python (pandas)", "SQL Window Functions", "GA4 / Ad Analytics", "JIRA", "Streamlit"],
            "match_score": 90,
            "link": "https://www.linkedin.com/jobs/view/data-analyst-ops",
            "description": "Query operational databases to detect data anomalies, track incident SLA metrics, and present monthly KPI trends to leadership."
        }
    ]
    return jobs

def format_job_digest_email(jobs):
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #1E293B; background-color: #F8FAFF; padding: 20px; }}
            .container {{ max-width: 650px; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #4F46E5, #0D9488); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .header h2 {{ margin: 0; font-size: 20px; }}
            .header p {{ margin: 5px 0 0 0; opacity: 0.9; font-size: 13px; }}
            .badge {{ display: inline-block; background: #EEF2FF; color: #4F46E5; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: bold; margin-right: 5px; }}
            .badge-fde {{ background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }}
            .job-card {{ border: 1px solid #E2E8F0; border-left: 4px solid #4F46E5; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #FAFAFA; }}
            .job-title {{ font-size: 16px; font-weight: bold; color: #1E293B; margin: 0 0 5px 0; }}
            .company {{ color: #64748B; font-size: 13px; font-weight: 600; }}
            .match-score {{ float: right; background: #4F46E5; color: white; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; }}
            .desc {{ font-size: 13px; color: #475569; margin: 8px 0; line-height: 1.4; }}
            .btn {{ display: inline-block; background: #4F46E5; color: white !important; text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-top: 5px; }}
            .footer {{ font-size: 11px; color: #94A3B8; margin-top: 20px; text-align: center; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🤖 Job Agent Alert: FDE, BA & DA Matches</h2>
                <p>Curated matches for Pavan Kumar Vaikutherisal · {now_str}</p>
            </div>
            
            <p>Here are your top-matched live openings across <b>Forward Deployed Engineer (FDE)</b>, <b>Business Analyst (BA)</b>, and <b>Data Analyst (DA)</b> roles:</p>
    """
    
    for job in jobs:
        badge_cls = "badge-fde" if "FDE" in job["role_category"] else ""
        html += f"""
            <div class="job-card">
                <span class="match-score">{job['match_score']}% Match</span>
                <p class="job-title">{job['title']}</p>
                <p class="company">🏢 {job['company']} · 📍 {job['location']}</p>
                <p><span class="badge {badge_cls}">{job['role_category']}</span></p>
                <p class="desc">{job['description']}</p>
                <p><b>Key Skills:</b> {", ".join(job["required_skills"])}</p>
                <a class="btn" href="{job['link']}" target="_blank">View & Apply Job ↗</a>
            </div>
        """
        
    html += f"""
            <div class="footer">
                Job Search Agent v2.0 · Targeted Roles: BA, DA, FDE · Sent to {DEFAULT_RECIPIENT}
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_job_alert_email(sender, app_password, recipient, cc_recipient, jobs):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎯 Job Agent Digest: {len(jobs)} Active FDE, BA & DA Roles Found"
    msg["From"] = sender
    msg["To"] = recipient
    msg["Cc"] = cc_recipient

    html_content = format_job_digest_email(jobs)
    msg.attach(MIMEText(html_content, "html"))

    recipients = [recipient, cc_recipient]
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipients, msg.as_string())
    print(f"Successfully sent job alert digest to {recipient} and {cc_recipient}")

if __name__ == "__main__":
    print("🤖 Job Agent Active: Fetching openings for BA, DA, and FDE roles...")
    jobs = fetch_sample_live_jobs()
    print(f"Found {len(jobs)} high-match roles (BA, DA, FDE).")

    sender = os.environ.get("SENDER_GMAIL", "pavanwork111@gmail.com")
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    
    if not app_password:
        print("Note: GMAIL_APP_PASSWORD env var not set. Run script with GMAIL_APP_PASSWORD to dispatch email alerts.")
        print(json.dumps(jobs, indent=2))
    else:
        send_job_alert_email(sender, app_password, DEFAULT_RECIPIENT, CC_RECIPIENT, jobs)
