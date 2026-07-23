# My Business Analytics Portfolio — Pavan Kumar Vaikutherisal

Hello! I am Pavan, and welcome to my analytics portfolio. 

Over the last three years working at Deloitte and MediaMint, I have spent countless hours inside transaction systems, CRM databases, and operations dashboards. I have felt the daily pressure of keeping SLAs green, the headache of manually cleaning messy customer data, and the challenge of proving campaign ROI to stakeholders. 

I built this portfolio to bridge the gap between my operational experience and hands-on coding. Instead of sharing confidential company data, I generated realistic synthetic datasets from scratch and wrote the SQL and Python queries myself to solve the exact operational problems I face every day. 

Each project below is a real challenge I wanted to tackle, showing how clean code can make business teams work smarter.

---

## Projects

### 1. LLM-Powered Customer RFM & Cohort Copywriter

**Business question:** Which customer groups drive repeat revenue, and how can we automate personalized re-engagement campaigns at scale?

**What I delivered:** A SQL-based RFM (Recency, Frequency, Monetary) segmentation model integrated with the Claude API to automatically generate hyper-targeted promotional copies based on a cohort's buying patterns.

**Dataset:** 500 customers and 929 transactional order records.

**Selected findings & capabilities:**
- Segmented the customer base into actionable cohorts (Champions, At-Risk High-Value, Lost) using SQL window functions.
- Integrated the Claude API to read cohort order profiles (e.g., top-purchased categories like "Home Office") and automatically draft customized email incentives.
- Replaced a manual copywriting process with a 2-second dynamic copy generator.

[View project case study](./project_1_sales_cohort/README.md)

### 2. AI-Powered SLA Incident Warning & Response System

**Business question:** How can we prevent customer satisfaction (CSAT) drops when support tickets approach their SLA limit?

**What I delivered:** A Python workflow that detects support ticket delays at a 75% SLA elapsed threshold and calls the Claude API to generate highly personalized, context-aware recovery emails.

**Dataset:** 1,000 operations service tickets.

**Selected findings & capabilities:**
- Found that SLA breaches cause a catastrophic CSAT drop from 3.98/5.0 down to 1.44/5.0.
- Implemented a proactive trigger to query customer profile metadata (lifetime value, category, history) when a ticket is running late.
- Programmed Claude to generate high-empathy status updates and troubleshooting recommendations, saving agents 15 minutes per incident.

[View project case study](./project_2_operations_rca/README.md)

### 3. Data Quality Audit & Profiling

**Business question:** Which fields in our billing transactions suffer from completeness issues, what is the duplicate rate of our transactions, and what data governance steps should we implement?

**What I delivered:** Python data-quality audit covering completeness (% non-null), uniqueness (% unique keys), and validity (% conforming to format rules) metrics, and transaction outlier checks.

**Dataset:** 1,025 synthetic billing transaction logs.

**Selected findings:**
- Email completeness was 95.90% with a 97.17% validity rate (42 missing, 29 invalid emails).
- Amount completeness was 97.56% with a 97.46% validity rate (25 missing, 26 negative or extreme outliers).
- Payment method validity rate was 92.78% due to casing/label inconsistency (74 records).
- Unique Transactions: 1,000 (25 duplicate rows detected).

**Decision supported:** Enforce database constraints (NOT NULL, UNIQUE keys), restrict UI inputs using drop-downs, and audit statistical amount outliers monthly.

[View project case study](./project_4_data_quality/README.md)

## Skills Demonstrated

- Business problem framing and KPI definition
- SQL using CTEs, window functions, cohort analysis, and RFM segmentation
- Python-based analysis, data profiling, and statistical testing
- Claude LLM API integration and structured prompt engineering
- SLA/TAT monitoring and proactive incident automation
- Data quality, validation, and governance


