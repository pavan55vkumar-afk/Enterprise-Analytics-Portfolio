# Business Analytics Portfolio

This portfolio presents four analytics case studies across customer growth, service operations, product experimentation, and database quality. Each project starts with a business question and ends with a decision or recommendation for stakeholders.

The datasets are synthetic and contain no confidential employer or client information. The business problems, KPI definitions, analysis approach, quality checks, interpretation, and recommendations were designed as realistic analytics engagements.

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

## Skills Demonstrated

- Business problem framing and KPI definition
- SQL using CTEs, window functions, cohort analysis, and RFM segmentation
- Python-based analysis, data profiling, and statistical testing
- SLA/TAT monitoring and root cause analysis
- Dashboard planning for Power BI and Tableau
- Data quality, validation, and governance

## Interview Guide

See [INTERVIEW_GUIDE.md](./INTERVIEW_GUIDE.md) for concise explanations, follow-up questions, limitations, and evidence-based answers for each project.
