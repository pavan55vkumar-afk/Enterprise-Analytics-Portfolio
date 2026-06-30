# My Business Analytics Portfolio — Pavan Kumar Vaikutherisal

Hello! I am Pavan, and welcome to my analytics portfolio. 

Over the last three years working at Deloitte and MediaMint, I have spent countless hours inside transaction systems, CRM databases, and operations dashboards. I have felt the daily pressure of keeping SLAs green, the headache of manually cleaning messy customer data, and the challenge of proving campaign ROI to stakeholders. 

I built this portfolio to bridge the gap between my operational experience and hands-on coding. Instead of sharing confidential company data, I generated realistic synthetic datasets from scratch and wrote the SQL and Python queries myself to solve the exact operational problems I face every day. 

Each project below is a real challenge I wanted to tackle, showing how clean code can make business teams work smarter.

---

## Projects

### 1. Customer Revenue, Retention, and RFM Analysis

**Business question:** Which customer groups drive revenue, how effectively are new customers retained, and which segments should receive retention attention?

**What I delivered:** DuckDB SQL analysis covering monthly revenue, return rate, cohort retention, and RFM customer segmentation.

**Dataset:** 500 customers and 929 orders.

**Selected findings:**
- Completed-order revenue was INR 5,372,250 across 887 completed orders.
- 395 active customers made at least one completed purchase.
- 249 repeat purchasers (63.0% of active customers) placed more than one completed order.
- Order return rate was 4.5% of total orders.

**Decision supported:** Prioritize retention campaigns for high-value customers showing declining activity (such as at-risk and loyal customer segments), while using monthly cohort trends to identify when repeat engagement weakens.

[View project case study](./project_1_sales_cohort/README.md)

### 2. Operational SLA Bottleneck Analysis

**Business question:** What is driving SLA failure, and where should operations leaders intervene first?

**What I delivered:** Ticket-level KPI analysis, category-level root cause analysis, and a dashboard layout specification.

**Dataset:** 1,000 service tickets, including 688 resolved tickets.

**Selected findings:**
- Overall SLA compliance was 80.67% (against a target of 90%).
- Delivery Issues had a breach rate of 40.7%.
- Average Delivery Issue handling time was 71.33 hours against a 72-hour SLA.
- Average CSAT fell from 3.98 for SLA-compliant tickets to 1.44 for breached tickets (Delta drop of 2.54 points).

**Decision supported:** Introduce milestone-based escalation, redesign the Delivery Issue workflow, and monitor category-level SLA risk rather than relying only on the overall compliance rate.

[View project case study](./project_2_operations_rca/README.md)

### 3. Product Conversion A/B Test

**Business question:** Did the proposed checkout experience improve conversion enough to justify rollout?

**What I delivered:** Experiment scorecard, two-proportion z-test calculated from scratch, confidence assessment, revenue comparison, and rollout recommendation.

**Dataset:** 5,000 simulated users split between control and variant groups.

**Selected findings:**
- Control conversion rate was 11.74% (293/2,495).
- Variant conversion rate was 14.13% (354/2,505).
- The variant produced a 2.39 percentage-point absolute lift and a 20.35% relative lift (95% CI: [+0.53% to +4.25%]).
- The result was statistically significant (`p = 0.01188` against `alpha = 0.05`).

**Decision supported:** Proceed with a controlled rollout while monitoring device-level performance, revenue per visitor, and post-launch guardrail metrics.

[View project case study](./project_3_product_ab_test/README.md)

### 4. Data Quality Audit & Profiling

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

### 5. Interactive Enterprise Analytics Dashboard

**Business question:** How can we allow stakeholders to dynamically explore operational metrics, filter retention cohorts, and simulate experiment parameters in real-time?

**What I delivered:** A multi-page Streamlit web app in Python that integrates data models and simulation rules across all analytical case studies.

**Dataset:** Integrates datasets from all 4 previous case studies (totaling 8,454 records).

**Selected findings:**
- Interactive region/category sidebar selectors that dynamically recalculate sales aggregates and RFM segments.
- Support ticket queue filters that compute SLA compliance and plot CSAT rating drops.
- Conversion z-test simulators with adjustable rates and size inputs, rendering normal distributions on the fly.
- Outlier detection models that flag billing transaction amount anomalies.

[View project case study](./project_5_streamlit_dashboard/README.md)

### 6. Data Warehouse Star Schema & ETL Pipeline

**Business question:** How do we transform normalized, inconsistent transaction tables into a clean, unified schema that minimizes join complexity and reduces analytical report latency?

**What I delivered:** A designed dimensional Star Schema (1 Fact and 3 Dimension tables) and a Python ETL pipeline that cleans data and loads it into a DuckDB database.

**Dataset:** 887 completed orders and 395 customer entities.

**Selected findings:**
- Cleaned and title-cased names, lowercased emails, and normalized region/payment methods.
- Created pre-calculated calendar metrics (quarters, months, weekend flags) in a `dim_date` dimension.
- Achieved fast aggregate analytics queries by joining surrogate keys rather than raw IDs.

[View project case study](./project_6_etl_warehouse/README.md)

### 7. Automated Executive PDF Compiler

**Business question:** How can we automate the compilation of e-commerce metrics, charts, and recommendations into print-ready, executive-style PDF updates?

**What I delivered:** An automated Python script using the ReportLab library to build a multi-page document structure, dynamically rendering performance tables and charts.

**Dataset:** Outputs from the cohort database, SLA logs, and conversion tests.

**Selected findings:**
- Compiled a professional 3-page executive performance report.
- Embedded high-res charts (monthly growth line, SLA breach Pareto bar, and A/B test normal curve) and formatted metrics.
- Generated the entire report in under 1 second, removing manual report compilation work.

[View project case study](./project_7_automated_reporting/README.md)

## Skills Demonstrated

- Business problem framing and KPI definition
- SQL using CTEs, window functions, cohort analysis, and RFM segmentation
- Python-based analysis, data profiling, and statistical testing
- SLA/TAT monitoring and root cause analysis
- Dashboard planning for Power BI and Tableau
- Data quality, validation, and governance

