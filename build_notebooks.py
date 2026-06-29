import os
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

def create_project_1_notebook():
    nb = new_notebook()
    
    # Title & Business Case
    cell1 = """# 📊 Project 1: Customer Sales Cohort & RFM Segmentation Analysis
**Business Domain:** E-commerce Retail & Database Marketing  
**Objective:** Profile user retention behavior and identify high-value customer segments using SQL cohort analysis and RFM (Recency, Frequency, Monetary) modeling.

### Business Context
Customer acquisition costs are rising. To maximize profitability, the business needs to transition from generic marketing to retention-focused campaigns. We need to:
1. Understand **revenue growth trends** and product return rates.
2. Build a **Cohort Retention Matrix** to identify when customers typically churn.
3. Classify customers into actionable **RFM segments** to trigger personalized email campaigns.

---"""
    nb.cells.append(new_markdown_cell(cell1))
    
    # Imports & Configurations
    cell2 = """import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Inline plots
%matplotlib inline

# Style config
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    "font.size": 10,
    "figure.figsize": (8, 4.5),
    "axes.edgecolor": "#CBD5E1",
    "axes.facecolor": "#FAFAFA"
})

ACCENT = "#2563EB"
ACCENT_LIGHT = "#93C5FD"
DARK = "#1E293B"
MUTED = "#64748B"
"""
    nb.cells.append(new_code_cell(cell2))
    
    # Load data in DuckDB
    cell3 = """# Initialize DuckDB in-memory database
con = duckdb.connect(database=':memory:')

# Load raw CSV datasets
customers_csv = "customers.csv"
orders_csv = "orders.csv"

# Load into tables
con.execute(f"CREATE TABLE customers AS SELECT * FROM read_csv_auto('{customers_csv}')")
con.execute(f"CREATE TABLE orders AS SELECT * FROM read_csv_auto('{orders_csv}')")

# Confirm counts
print(f"Loaded {con.execute('SELECT COUNT(*) FROM customers').fetchone()[0]} customers.")
print(f"Loaded {con.execute('SELECT COUNT(*) FROM orders').fetchone()[0]} orders.")
"""
    nb.cells.append(new_code_cell(cell3))
    
    # Part 1: Monthly Growth & Revenue
    cell4 = """## 📈 Part 1: Monthly Growth & Return Rate Analysis
We first run a SQL query to calculate:
* **Monthly Gross Revenue**
* **Net Completed-Order Revenue** (excluding returned orders)
* **Month-over-Month (MoM) Growth Rate**
* **Monthly Return Rate %** (returned order amount / total order amount)"""
    nb.cells.append(new_markdown_cell(cell4))
    
    cell5 = """# Read the SQL query from project SQL file
with open("project1_cohort_retention.sql", "r") as f:
    sql_queries = f.read().split(';')

# Query 1: Monthly Growth
query_1 = sql_queries[0].strip()
print("SQL Query 1:")
print(query_1)

# Execute and get pandas DataFrame
df_revenue = con.execute(query_1).df()
df_revenue"""
    nb.cells.append(new_code_cell(cell5))
    
    cell6 = """# Plot Monthly Revenue and MoM Growth
fig, ax1 = plt.subplots(figsize=(9, 5))

# Primary Axis: Net Revenue
ax1.plot(df_revenue['month'], df_revenue['current_month_net_revenue'] / 100000, marker='o', color=ACCENT, linewidth=2.5, label='Net Revenue')
ax1.set_ylabel('Net Revenue (INR Lakhs)', color=DARK, fontweight='bold')
ax1.set_xlabel('Month', fontweight='bold')
ax1.tick_params(axis='y', labelcolor=MUTED)
ax1.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1')

# Secondary Axis: MoM Growth %
ax2 = ax1.twinx()
growth_plot = df_revenue['mom_growth_pct'].fillna(0)
ax2.plot(df_revenue['month'], growth_plot, marker='s', color='#F97316', linestyle='--', linewidth=1.5, label='MoM Growth %')
ax2.set_ylabel('Month-over-Month Growth (%)', color=DARK, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=MUTED)
ax2.axhline(0, color=MUTED, linestyle='-', linewidth=0.5, alpha=0.5)

plt.title('Monthly Net Revenue Trend & MoM Growth Rate', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell6))
    
    # Part 2: Cohort Retention
    cell7 = """## 🔄 Part 2: Cohort Retention Matrix
We aggregate customers into monthly cohorts based on their `signup_date` (Month 0) and track the percentage of those customers who return to purchase in subsequent months (Period 1 to Period 5)."""
    nb.cells.append(new_markdown_cell(cell7))
    
    cell8 = """# Query 2: Cohort Retention
query_2 = sql_queries[1].strip()
print("SQL Query 2 (Cohort Retention):")
df_retention = con.execute(query_2).df()
df_retention"""
    nb.cells.append(new_code_cell(cell8))
    
    cell9 = """# Plot Retention Heatmap
plt.figure(figsize=(10, 5))
heatmap_data = df_retention.set_index('cohort')[[c for c in df_retention.columns if 'pct' in c]]
heatmap_data.columns = [f"Month {c.split('_')[1]}" for c in heatmap_data.columns]

sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="Blues", cbar=False, 
            annot_kws={"size": 10, "weight": "bold"}, linewidths=0.5)
plt.title('Customer Cohort Retention Rate (%)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Periods (Months Since Signup)', fontweight='bold')
plt.ylabel('Signup Month Cohort', fontweight='bold')
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell9))
    
    # Part 3: RFM Segmentation
    cell10 = """## 🎯 Part 3: RFM Customer Segmentation
We run an RFM model using SQL window functions and NTILE:
1. **Recency**: Days since last order (Lower is better $\rightarrow$ Higher score)
2. **Frequency**: Count of completed orders (Higher is better $\rightarrow$ Higher score)
3. **Monetary**: Sum of order amounts (Higher is better $\rightarrow$ Higher score)
4. Score segments based on code combinations."""
    nb.cells.append(new_markdown_cell(cell10))
    
    cell11 = """# Query 3: RFM Segmentation
query_3 = sql_queries[2].strip()
df_rfm = con.execute(query_3).df()
print("Top 10 Customers Segmented:")
df_rfm.head(10)"""
    nb.cells.append(new_code_cell(cell11))
    
    cell12 = """# Plot RFM Segment Distribution
plt.figure(figsize=(9, 5))
segment_counts = df_rfm['customer_segment'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Customer Count']
segment_counts = segment_counts.sort_values(by='Customer Count', ascending=True)

bars = plt.barh(segment_counts['Segment'], segment_counts['Customer Count'], color=ACCENT, height=0.6)

for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2, f' {int(width)}', 
             va='center', ha='left', fontsize=9, fontweight='bold', color=DARK)
             
plt.title('Customer Segment Distribution (RFM)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Number of Customers', fontweight='bold')
plt.xlim(0, segment_counts['Customer Count'].max() * 1.15)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='x', linestyle=':', alpha=0.6, color='#CBD5E1')
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell12))
    
    # Part 4: Recommendations
    cell13 = """## 💡 Part 4: Business Insights & Recommendations
Based on the analysis, here are the recommendations:
1. **At Risk Retention:** Retarget the **"At Risk (High Value, Sleeping)"** segment with a reactivation discount code. These are historical high spenders who haven't purchased recently.
2. **Loyalty Program:** Reward **"Champions"** with exclusive early access to product releases to build brand advocacy.
3. **Retention Bottleneck:** Cohort Month 1 drops significantly. Investigate the onboarding process or initial product experience to improve first-month retention.
"""
    nb.cells.append(new_markdown_cell(cell13))
    
    # Save notebook
    out_path = "project1_cohort_rfm_analysis.ipynb"
    with open(out_path, "w") as f:
        nbformat.write(nb, f)
    print(f"Created {out_path}")


def create_project_2_notebook():
    nb = new_notebook()
    
    cell1 = """# 🛠️ Project 2: Operations Support SLA & CSAT Root Cause Analysis
**Business Domain:** Customer Operations & Service Level Agreements (SLA)  
**Objective:** Audit support ticket resolution rates, identify category bottlenecks, and quantify the correlation between SLA breaches and Customer Satisfaction (CSAT) score drops.

### Business Context
Support operations has seen a recent increase in negative customer feedback. The Operations team needs to:
1. Measure **SLA compliance** across all ticket categories.
2. Identify which ticket categories cause the most **SLA breaches** (Pareto principle).
3. Quantify how **breaching SLAs** hurts customer sentiment (CSAT scores).
4. Provide process recommendations to resolve bottlenecks.

---"""
    nb.cells.append(new_markdown_cell(cell1))
    
    cell2 = """import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

%matplotlib inline

# Style config
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    "font.size": 10,
    "figure.figsize": (8, 4.5),
    "axes.edgecolor": "#CBD5E1",
    "axes.facecolor": "#FAFAFA"
})

ACCENT = "#2563EB"
ALERT = "#EA580C"
DARK = "#1E293B"
MUTED = "#64748B"
"""
    nb.cells.append(new_code_cell(cell2))
    
    cell3 = """# Load raw simulated tickets data
df = pd.read_csv("tickets.csv")

# Parse dates and numeric columns
df['created_at'] = pd.to_datetime(df['created_at'])
df['resolved_at'] = pd.to_datetime(df['resolved_at'])
df['handling_time_hours'] = pd.to_numeric(df['handling_time_hours'], errors='coerce')
df['customer_satisfaction'] = pd.to_numeric(df['customer_satisfaction'], errors='coerce')

print(f"Dataset shape: {df.shape}")
df.head()"""
    nb.cells.append(new_code_cell(cell3))
    
    cell4 = """## 📊 Part 1: Overall SLA Compliance Metrics
Let's calculate the total volume, resolution rate, and SLA compliance rate."""
    nb.cells.append(new_markdown_cell(cell4))
    
    cell5 = """total_tickets = len(df)
resolved_df = df[df['status'].isin(['Resolved', 'Closed'])]
resolved_count = len(resolved_df)
breached_count = resolved_df['is_breach'].sum()
sla_compliance = ((resolved_count - breached_count) / resolved_count) * 100

print(f"Total Tickets: {total_tickets}")
print(f"Resolved Tickets: {resolved_count} ({resolved_count/total_tickets:.1%})")
print(f"SLA Compliance Rate: {sla_compliance:.2f}%")"""
    nb.cells.append(new_code_cell(cell5))
    
    cell6 = """## 🔍 Part 2: Category Breakdown & Bottleneck Identification
Let's see which support categories are failing their SLA commitments."""
    nb.cells.append(new_markdown_cell(cell6))
    
    cell7 = """cat_df = resolved_df.groupby('category').agg(
    volume=('ticket_id', 'count'),
    avg_handling_time=('handling_time_hours', 'mean'),
    sla_target=('sla_hours', 'first'),
    breach_count=('is_breach', 'sum'),
    avg_csat=('customer_satisfaction', 'mean')
).reset_index()

cat_df['breach_rate_pct'] = (cat_df['breach_count'] / cat_df['volume']) * 100
cat_df.sort_values(by='breach_rate_pct', ascending=False)"""
    nb.cells.append(new_code_cell(cell7))
    
    cell8 = """# Pareto Analysis of SLA Breaches
pareto_data = cat_df.sort_values(by='breach_count', ascending=False)
pareto_data['cumulative_pct'] = (pareto_data['breach_count'].cumsum() / pareto_data['breach_count'].sum()) * 100

fig, ax1 = plt.subplots(figsize=(9, 5))
bars = ax1.bar(pareto_data['category'], pareto_data['breach_count'], color=ACCENT, alpha=0.8, width=0.4)
ax1.set_ylabel('Number of SLA Breaches', color=DARK, fontweight='bold')
ax1.tick_params(axis='y', labelcolor=MUTED)

ax2 = ax1.twinx()
ax2.plot(pareto_data['category'], pareto_data['cumulative_pct'], color=ALERT, marker='D', ms=6, linewidth=1.8)
ax2.set_ylabel('Cumulative % of Breaches', color=DARK, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=MUTED)
ax2.set_ylim(0, 110)

plt.title('SLA Breaches by Category (Pareto Analysis)', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell8))
    
    cell9 = """## 🗣️ Part 3: CSAT Impact Quantification
Let's analyze customer satisfaction (CSAT) scores when SLAs are met vs when they are breached."""
    nb.cells.append(new_markdown_cell(cell9))
    
    cell10 = """# Grouped bar chart comparing CSAT
csat_groups = resolved_df.groupby(['category', 'is_breach'])['customer_satisfaction'].mean().unstack().reset_index()
csat_groups.columns = ['Category', 'SLA Met', 'SLA Breached']

x_positions = range(len(csat_groups))
width = 0.35

plt.figure(figsize=(9, 5))
plt.bar([x - width/2 for x in x_positions], csat_groups['SLA Met'], width, label='SLA Met', color=ACCENT)
plt.bar([x + width/2 for x in x_positions], csat_groups['SLA Breached'], width, label='SLA Breached', color=ALERT)

plt.xticks(x_positions, csat_groups['Category'])
plt.ylabel('Average CSAT Score (1-5)', fontweight='bold')
plt.title('CSAT Performance: SLA Met vs. Breached', fontsize=13, fontweight='bold', pad=15)
plt.ylim(0, 5.5)
plt.legend(loc='upper right')
plt.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell10))
    
    cell11 = """## 💡 Part 4: Root Cause & Process Recommendations
Based on the analysis, here is our operational action plan:
1. **Target Delivery Issues:** **Delivery Issues** are our primary bottleneck, with a high breach rate. The average handling time exceeds the target.
2. **Quantify CSAT Impact:** Tickets that breach SLA drop dramatically in CSAT, showing a significant drop in customer satisfaction compared to tickets met within SLA.
3. **Escalation Rules:** Implement real-time alerts in Salesforce/CRM when 'Delivery Issue' or 'Technical Support' tickets reach 50% of SLA thresholds.
"""
    nb.cells.append(new_markdown_cell(cell11))
    
    out_path = "project2_operations_sla_rca.ipynb"
    with open(out_path, "w") as f:
        nbformat.write(nb, f)
    print(f"Created {out_path}")


def create_project_3_notebook():
    nb = new_notebook()
    
    cell1 = """# 🧪 Project 3: Checkout UI Conversion Rate A/B Test Analysis
**Business Domain:** Product Management & Conversion Rate Optimization (CRO)  
**Objective:** Analyze checkout flow conversion logs, perform two-proportion Z-hypothesis testing, calculate confidence intervals, and recommend deployment strategies.

### Business Context
The design team has introduced a simplified 1-page checkout flow (Variant) to replace the existing multi-step flow (Control). The Product team needs to:
1. Conduct an **A/B test analysis** on 5,000 users.
2. Perform a **two-proportion Z-test** to verify if the conversion rate lift is statistically significant.
3. Compute the **95% Confidence Interval** for the conversion rate difference.
4. Render the standard normal curve showing the **rejection regions** and Z-statistic.
5. Provide a launch/no-launch business recommendation.

---"""
    nb.cells.append(new_markdown_cell(cell1))
    
    cell2 = """import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

%matplotlib inline

# Style config
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    "font.size": 10,
    "figure.figsize": (8, 4.5),
    "axes.edgecolor": "#CBD5E1",
    "axes.facecolor": "#FAFAFA"
})

ACCENT = "#2563EB"
ACCENT_LIGHT = "#93C5FD"
ALERT = "#EA580C"
DARK = "#1E293B"
MUTED = "#64748B"
"""
    nb.cells.append(new_code_cell(cell2))
    
    cell3 = """# Load experiment log
df = pd.read_csv("ab_test_data.csv")

print(f"Total Users in Experiment: {len(df)}")
df.groupby('group').agg(
    users=('user_id', 'count'),
    conversions=('converted', 'sum'),
    conversion_rate=('converted', 'mean'),
    revenue=('revenue', 'sum')
)"""
    nb.cells.append(new_code_cell(cell3))
    
    cell4 = """## 🔢 Part 1: Z-Test for Two Proportions from Scratch
We calculate the statistical test parameters using analytical formulas."""
    nb.cells.append(new_markdown_cell(cell4))
    
    cell5 = """# Extraction of metrics
summary = df.groupby('group').agg(
    n=('user_id', 'count'),
    x=('converted', 'sum')
)

n_c = summary.loc['control', 'n']
x_c = summary.loc['control', 'x']
p_c = x_c / n_c

n_v = summary.loc['variant', 'n']
x_v = summary.loc['variant', 'x']
p_v = x_v / n_v

# Combined pooled proportion
p_pooled = (x_c + x_v) / (n_c + n_v)

# Standard error
se_diff = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_c + 1/n_v))

# Z-score
z_stat = (p_v - p_c) / se_diff

# P-value calculation
def normal_cdf(z):
    return (1.0 + math.erf(z / math.sqrt(2.0))) / 2.0
p_val = 2 * (1 - normal_cdf(abs(z_stat)))

# 95% Confidence Interval margin
z_critical = 1.96
ci_margin = z_critical * math.sqrt(p_c*(1-p_c)/n_c + p_v*(1-p_v)/n_v)
diff = p_v - p_c
ci_lower = diff - ci_margin
ci_upper = diff + ci_margin

print(f"Control Conversion Rate: {p_c:.4f} ({p_c:.2%})")
print(f"Variant Conversion Rate: {p_v:.4f} ({p_v:.2%})")
print(f"Observed Lift (Absolute): {diff:+.4f} ({diff:+.2%})")
print(f"Z-Statistic: {z_stat:.4f}")
print(f"P-Value: {p_val:.5f}")
print(f"95% Confidence Interval: [{ci_lower:+.2%} to {ci_upper:+.2%}]")"""
    nb.cells.append(new_code_cell(cell5))
    
    cell6 = """# Visualizing Conversion Rate Comparison
plt.figure(figsize=(7, 4.5))
groups = ['Control', 'Variant']
rates = [p_c * 100, p_v * 100]
err_c = z_critical * math.sqrt(p_c * (1 - p_c) / n_c) * 100
err_v = z_critical * math.sqrt(p_v * (1 - p_v) / n_v) * 100

bars = plt.bar(groups, rates, yerr=[err_c, err_v], color=[ACCENT_LIGHT, ACCENT], capsize=8, width=0.45, edgecolor='#CBD5E1')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height / 2.0, f'{height:.2f}%', 
             ha='center', va='center', color='white', fontweight='bold', fontsize=11)
             
plt.ylabel('Conversion Rate (%)', fontweight='bold')
plt.title('Checkout Conversion Rates (95% CI)', fontsize=13, fontweight='bold', pad=15)
plt.ylim(0, max(rates) * 1.35)
plt.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell6))
    
    cell7 = """# Plot Rejection Regions and Z-statistic
plt.figure(figsize=(9, 4.5))
x = np.linspace(-4, 4, 1000)
y = np.exp(-x**2/2) / np.sqrt(2*np.pi)

plt.plot(x, y, color=DARK, linewidth=1.5, label='Standard Normal Curve')
plt.fill_between(x, y, where=(x <= -1.96), color='#FCA5A5', alpha=0.5, label='Rejection Region (alpha = 0.05)')
plt.fill_between(x, y, where=(x >= 1.96), color='#FCA5A5', alpha=0.5)

plt.axvline(z_stat, color=ALERT, linestyle='-', linewidth=2.0, label=f'Z-Statistic ({z_stat:.2f})')
plt.text(z_stat - 0.15, 0.25, f'Z = {z_stat:.2f}\\n(p = {p_val:.5f})', color=ALERT, fontweight='bold', ha='right')

plt.title('Hypothesis Testing: Z-Statistic vs. Rejection Regions', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Standard Deviations (z)', fontweight='bold')
plt.ylabel('Probability Density', fontweight='bold')
plt.legend(loc='upper left')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell7))
    
    cell8 = """## 💡 Part 2: Business Decision Summary
Based on the experiment data:
1. **Statistical Significance Met:** Check if the Z-statistic lies inside the rejection region. The P-value is compared against our significance threshold ($\alpha = 0.05$).
2. **Quantified Uplift:** The Variant design generated a positive conversion rate lift.
3. **95% Confidence:** We are 95% confident that the true conversion lift lies within the CI range.
4. **RECOMMENDATION:** Approve rollout if results are statistically significant.
"""
    nb.cells.append(new_markdown_cell(cell8))
    
    out_path = "project3_checkout_ab_test.ipynb"
    with open(out_path, "w") as f:
        nbformat.write(nb, f)
    print(f"Created {out_path}")


def create_project_4_notebook():
    nb = new_notebook()
    
    cell1 = """# 🧼 Project 4: Enterprise Data Quality Audit & Profiling Engine
**Business Domain:** Data Governance, Data Warehousing, & BI Engineering  
**Objective:** Audit a messy billing transaction log, profile columns for Completeness, Uniqueness, and Validity, map data anomalies, and export actionable Data Quality (DQ) scorecards.

### Business Context
The Data Warehousing team has been encountering frequent dashboard failures and aggregation errors. To prevent garbage-in, garbage-out analytics, we must build an automated quality check process that:
1. Audits dataset **completeness** (null rate metrics).
2. Profiles **uniqueness** of transaction keys (duplicate detection).
3. Validates formats (regex-style email verification, out-of-bounds metrics, and negative values).
4. Generates an easy-to-read Data Quality Scorecard for data engineers.

---"""
    nb.cells.append(new_markdown_cell(cell1))
    
    cell2 = """import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

%matplotlib inline

# Style config
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    "font.size": 10,
    "figure.figsize": (8, 4.5),
    "axes.edgecolor": "#CBD5E1",
    "axes.facecolor": "#FAFAFA"
})

ACCENT = "#2563EB"
ACCENT_LIGHT = "#93C5FD"
ALERT = "#EA580C"
DARK = "#1E293B"
MUTED = "#64748B"
"""
    nb.cells.append(new_code_cell(cell2))
    
    cell3 = """# Load raw billing data
df = pd.read_csv("billing_transactions_raw.csv")

print(f"Auditing Dataset Shape: {df.shape}")
df.head()"""
    nb.cells.append(new_code_cell(cell3))
    
    cell4 = """## 🔍 Part 1: Column-by-Column Data Quality Auditing
We evaluate three core dimensions of data quality:
1. **Completeness:** Percentage of non-missing (non-null/non-empty) records.
2. **Uniqueness:** Rate of unique values in the primary key field.
3. **Validity:** Percent of values conforming to business-defined validation rules."""
    nb.cells.append(new_markdown_cell(cell4))
    
    cell5 = """total_rows = len(df)

# 1. Completeness Check
completeness = {}
for col in df.columns:
    nulls = df[col].isna() | (df[col] == "")
    completeness[col] = (total_rows - nulls.sum()) / total_rows

# 2. Uniqueness (Key constraints)
unique_tx = df['transaction_id'].nunique()
uniqueness = {col: 1.0 for col in df.columns}
uniqueness['transaction_id'] = unique_tx / total_rows

# 3. Validity Checks
validity = {}
validity["transaction_id"] = df["transaction_id"].apply(lambda x: str(x).isdigit() and len(str(x)) == 7).mean()
validity["customer_id"] = df["customer_id"].apply(lambda x: isinstance(x, (int, np.integer)) and x > 0).mean()

def validate_email(email):
    if not email: return True
    return "@" in str(email) and "." in str(email).split("@")[-1]
validity["customer_email"] = df["customer_email"].apply(lambda x: validate_email(x) if pd.notna(x) and x != "" else True).mean()

def validate_date(d):
    try:
        pd.to_datetime(d, format='%Y-%m-%d')
        return True
    except:
        return False
validity["transaction_date"] = df["transaction_date"].apply(validate_date).mean()

def validate_amount(a):
    if pd.isna(a): return True
    return a > 0 and a <= 10000.0
validity["transaction_amount"] = df["transaction_amount"].apply(validate_amount).mean()

valid_payment_methods = ["Credit Card", "Debit Card", "UPI", "Net Banking"]
validity["payment_method"] = df["payment_method"].apply(lambda x: x in valid_payment_methods if pd.notna(x) and x != "" else True).mean()

valid_states = ["NY", "CA", "TX", "WA", "FL", "IL", "MA"]
validity["billing_state"] = df["billing_state"].apply(lambda x: x in valid_states if pd.notna(x) and x != "" else True).mean()

# Consolidate DQ Scorecard
metrics = []
for col in df.columns:
    metrics.append({
        "Column": col,
        "Completeness": completeness[col],
        "Uniqueness": uniqueness[col],
        "Validity": validity[col]
    })
df_scorecard = pd.DataFrame(metrics)
df_scorecard"""
    nb.cells.append(new_code_cell(cell5))
    
    cell6 = """# Heatmap of Scorecard
plt.figure(figsize=(8, 4))
heatmap_data = df_scorecard.set_index("Column")[["Completeness", "Uniqueness", "Validity"]]
sns.heatmap(heatmap_data, annot=True, fmt=".2%", cmap="Blues", cbar=False, linewidths=.5, annot_kws={"weight": "bold"})
plt.title("Data Quality Profile Heatmap", fontsize=13, fontweight='bold', pad=15)
plt.ylabel("")
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell6))
    
    cell7 = """## ⚠️ Part 2: Outlier & Anomaly Breakdown
We profile anomaly metrics and count instances of nulls, duplicates, and bad formats."""
    nb.cells.append(new_markdown_cell(cell7))
    
    cell8 = """# Count null values
null_counts = df.apply(lambda x: (x.isna() | (x == "")).sum())
duplicate_rows = df.duplicated(subset=['transaction_id'], keep='first').sum()

# Count formatting anomalies
format_issues = {
    "transaction_id": 0,
    "customer_id": 0,
    "customer_email": df["customer_email"].apply(lambda x: 0 if validate_email(x) else 1).sum(),
    "transaction_date": df["transaction_date"].apply(lambda x: 0 if validate_date(x) else 1).sum(),
    "transaction_amount": df["transaction_amount"].apply(lambda x: 0 if validate_amount(x) else 1).sum(),
    "payment_method": df["payment_method"].apply(lambda x: 0 if (pd.isna(x) or x == "" or x in valid_payment_methods) else 1).sum(),
    "billing_state": df["billing_state"].apply(lambda x: 0 if (pd.isna(x) or x == "" or x in valid_states) else 1).sum()
}

# Stacked bar plot
plt.figure(figsize=(9, 5))
columns = df.columns
nulls_to_plot = [null_counts[col] for col in columns]
duplicates_to_plot = [duplicate_rows if col == "transaction_id" else 0 for col in columns]
format_to_plot = [format_issues[col] for col in columns]

ind = np.arange(len(columns))
width = 0.45

p1 = plt.bar(ind, nulls_to_plot, width, color='#93C5FD', edgecolor='#CBD5E1', label='Missing (Null)')
p2 = plt.bar(ind, duplicates_to_plot, width, bottom=nulls_to_plot, color='#EA580C', edgecolor='#CBD5E1', label='Duplicate Key')
bottom_3 = [n + d for n, d in zip(nulls_to_plot, duplicates_to_plot)]
p3 = plt.bar(ind, format_to_plot, width, bottom=bottom_3, color='#FCA5A5', edgecolor='#CBD5E1', label='Format/Outlier Error')

plt.ylabel('Issue Count', fontweight='bold')
plt.title('Identified Data Anomalies per Column', fontsize=13, fontweight='bold', pad=15)
plt.xticks(ind, columns, rotation=20, ha='right')
plt.legend(loc='upper right')
plt.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
plt.tight_layout()
plt.show()"""
    nb.cells.append(new_code_cell(cell8))
    
    cell9 = """## 💡 Part 3: Data Integrity Recommendations
Based on the audit report:
1. **Enforce Database Schema Constraints:** Set `transaction_id` as a `PRIMARY KEY` to resolve duplicate entries.
2. **Email Sanitation:** Enforce lowercase values and validation regex patterns upon user signup to fix malformed email records.
3. **Outlier Filtering:** Create an ETL staging gate that flags negative order amounts and orders exceeding \$10,000 to catch anomalies.
"""
    nb.cells.append(new_markdown_cell(cell9))
    
    # Save notebook
    out_path = "project4_data_quality_audit.ipynb"
    with open(out_path, "w") as f:
        nbformat.write(nb, f)
    print(f"Created {out_path}")

if __name__ == "__main__":
    create_project_1_notebook()
    create_project_2_notebook()
    create_project_3_notebook()
    create_project_4_notebook()
