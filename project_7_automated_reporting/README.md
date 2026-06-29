# 📊 Automated Stakeholder Reporting: Executive PDF Compiler

[![Python](https://img.shields.io/badge/Python-3.9-blue?style=flat-square&logo=python&logoColor=white)](generate_report.py)
[![ReportLab](https://img.shields.io/badge/Library-ReportLab-blue?style=flat-square)](#)
[![Automated Reporting](https://img.shields.io/badge/Domain-BI%20%26%20Reporting-blue?style=flat-square)](#)
[![Status](https://img.shields.io/badge/Status-Complete-green?style=flat-square)](#)

---

## Why I Built This Project (Personal Context)

In business operations, completing the analysis and writing the code represents only 80% of the job. The final and most critical "last mile" is **communicating the results to stakeholders** in a format they can immediately digest—often a clean, printable PDF report or a presentation slide. 

I built this project to demonstrate how to automate this reporting workflow. I wrote a Python script that utilizes the **ReportLab** library to compile findings from all our e-commerce operations, checkout A/B tests, and cohort retention models, dynamically inserting KPI tables and embedding generated charts into a structured, executive-ready PDF report (`Executive_Performance_Report.pdf`).

---

## 🛠️ Automated PDF Compilation Flow

```
[ Gather Inputs ]  -->  Read generated charts (PNGs) & datasets (CSV)
                             |
                             v
[ Build Templates ] --> Define ReportLab SimpleDocTemplate margins & grid layouts
                             |
                             v
[ Format Styles ]  -->  Apply Hex Color palettes (Professional Tech Blue Accent) 
                        & Helvetica-Bold typography
                             |
                             v
[ Render PDF ]     -->  Export structured multi-page document with KPI tables 
                        & embedded graphics
```

---

## 📇 Executive Report Structure

The generated [Executive_Performance_Report.pdf](Executive_Performance_Report.pdf) consists of three structured pages:

1. **Page 1: Title Block & Executive Summary**
   * High-level project objectives.
   * **Cohort Retention Profile KPI Table** (Gross Sales, active repeat rates, return rates).
   * **Monthly Completed Order Sales & Growth Curve** (embedded PNG chart).
2. **Page 2: Operations Support & Product A/B Test Results**
   * **Queue SLA Breach Pareto Analysis** (embedded PNG chart).
   * **Checkout Funnel Conversion Uplift Z-Test Chart** (embedded PNG chart).
3. **Page 3: Process Recommendations & Action Plan**
   * Direct operational feedback: restructuring Delivery workflows, implementing milestone queue alerts, rolling out checkout layout variations, and database data staging gate constraints.

---

## 🚀 How to Run

1. Make sure you are in the project folder:
   ```bash
   cd project_7_automated_reporting
   ```
2. Execute the PDF reporting compiler:
   ```bash
   python3 generate_report.py
   ```
   This will query the metrics, fetch the charts from the root `assets/` directory, compile the ReportLab story elements, and export the document as `Executive_Performance_Report.pdf` in the current folder.
