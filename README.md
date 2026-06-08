# Enterprise Data & Business Intelligence Analytics Portfolio

Welcome! This repository houses end-to-end analytical solutions, simulations, and dashboards designed to solve key business challenges across Sales, Operations, and Product Growth. 

Each project uses clean, production-grade SQL and Python to extract actionable insights from data and guide corporate decision-making.

---

## 🚀 Projects Overview

### 📈 1. Customer Cohort & Lifecycle Analytics (SQL)
*   **Business Problem:** How do customer purchase cycles evolve, and how can we segment customers to target high-value users?
*   **Methodology:**
    *   Synthesized transactional databases using standard statistical models.
    *   Designed SQL queries using **Common Table Expressions (CTEs)** and **Window Functions** to build Month-over-Month cohort retention matrices.
    *   Implemented an **RFM (Recency, Frequency, Monetary) Segmentation** matrix to rank customers into actionable tiers (Champions, Active Loyal, At Risk, Lost, etc.).
*   **Key Tech:** PostgreSQL, SQL CTEs, NTILE, LAG, Cohort Matrix.
*   **Location:** [`/project_1_sales_cohort`](./project_1_sales_cohort)

### 📋 2. Service SLA Optimization & Root Cause Analysis (Python & BI)
*   **Business Problem:** Support operations were experiencing high SLA breach rates, dragging down customer satisfaction (CSAT) scores.
*   **Methodology:**
    *   Analyzed support tickets logs to calculate **Average Handling Time (AHT)** and SLA violation distributions.
    *   Conducted a **Root Cause Analysis (RCA)** identifying "Delivery Issues" as a bottleneck breaching SLAs at a rate of 49.7%.
    *   Quantified impact: SLA breaches correlate directly with a **2.5+ point drop in CSAT** (4.01 to 1.34).
    *   Drafted a complete **Power BI / Tableau Wireframe & Specification Blueprint** including necessary DAX measures and Level of Detail (LOD) formulas.
*   **Key Tech:** Python (math/datetime), Power BI, Tableau (DAX/LOD), RCA.
*   **Location:** [`/project_2_operations_rca`](./project_2_operations_rca)

### 🧪 3. Product Conversion Funnel A/B Testing Simulator (Python)
*   **Business Problem:** Evaluating if a new checkout funnel variant significantly boosts the user sign-up-to-purchase conversion rate.
*   **Methodology:**
    *   Simulated user trial conversions for Control and Variant streams (n = 5,000).
    *   Developed a statistical testing engine in pure Python calculating Standard Error, Z-statistic, Confidence Intervals, and two-tailed P-values.
    *   Evaluated significance at $\alpha = 0.05$ to recommend product release rollouts.
*   **Key Tech:** Python, Hypothesis Testing, Z-Tests, P-Value Calculation.
*   **Location:** [`/project_3_product_ab_test`](./project_3_product_ab_test)

---

## 🛠️ How to Run Locally

Ensure you have Python 3 installed. Run the simulations with the following terminal commands:

```bash
# Seed the transactional data
python3 project_1_sales_cohort/generate_data.py

# Run SLA analytics
python3 project_2_operations_rca/project2_rca_simulation.py

# Run A/B test statistical analysis
python3 project_3_product_ab_test/project3_ab_testing.py
```
