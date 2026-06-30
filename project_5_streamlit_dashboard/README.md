# Project 5: Enterprise Analytics Interactive Dashboard

Welcome! This repository contains a **Streamlit** dashboard built from scratch to act as the interactive control hub for my business and data analytics case studies.

Instead of presenting static SQL queries and offline notebooks, I built this multi-page web application to allow stakeholders to dynamically explore the datasets, run live simulations, and filter operational support queues in real-time.

---

## 🛠️ Tech Stack
* **Framework:** Streamlit (Python-based interactive UI)
* **Data Processing:** Pandas, NumPy
* **Visualization:** Plotly Express, Plotly Graph Objects (dynamic standard normal distributions and cohort bar charts)
* **Underlying Logic:** Integrates the data models and simulation rules from Projects 1, 2, 3, and 4.

---

## 🚀 Key Dashboard Pages

### 1. Overview Hub
* **What it does:** Introduces the portfolio, states my background (3 years at Deloitte & MediaMint), and houses the high-level summary metrics (e.g., 8,454 total records analyzed).
* **Interactive Element:** High-level scorecard metrics that summarize scope and compliance rates at a glance.

### 2. Cohort & RFM Analytics (Project 1 Integration)
* **What it does:** Visualizes monthly growth trends and customer retention metrics.
* **Interactive Element:** Sidebar multi-select filters for **Region** and **Product Category**. It automatically recalculates total completed sales, active customer counts, monthly revenue trends, and assigns users dynamically to RFM segments (Champions, Sleeping, At Risk, etc.) based on your selected filters.

### 3. Operations SLA Audit (Project 2 Integration)
* **What it does:** Breaks down support ticket volumes and SLA breaches to find the root cause.
* **Interactive Element:** Multi-select filters for ticket **Priority** and **Category**. Dynamically recalculates overall SLA compliance (relative to a 90% target) and visualizes the direct customer satisfaction (CSAT) impact when SLAs are breached vs. met.

### 4. A/B Testing Simulator (Project 3 Integration)
* **What it does:** Simulates a two-proportion Z-hypothesis test comparing conversion rates.
* **Interactive Element:** Live **slider controls** for Control Conversion Rate, Variant Conversion Rate, and Sample Size (N). It computes the Z-statistic and p-value in real-time, displaying whether the difference is statistically significant, and renders a standard normal curve highlighting the critical region bounds (±1.96) and the position of your Z-statistic.

### 5. Data Quality Health (Project 4 Integration)
* **What it does:** Audits the completeness, uniqueness, and validity of transaction logs.
* **Interactive Element:** Renders a clean data quality scorecard (completeness, key uniqueness, validity rates) for all transaction columns, identifies amount outliers using the IQR (Interquartile Range) method, and outputs a table highlighting anomalous records (negative values or extreme values).

---

## 💻 How to Run Locally

### 1. Install Dependencies
Make sure you have python installed, then run:
```bash
pip install -r requirements.txt
```
*(This will install Streamlit, Pandas, NumPy, and Plotly)*

### 2. Run the App
Launch the dashboard locally in your default web browser by running:
```bash
streamlit run app.py
```
This runs the application locally on `http://localhost:8501`.
