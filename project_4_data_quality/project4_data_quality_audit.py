"""
Project 4: Data Quality Audit & Profiling (Python)
Generates a messy synthetic billing transactions dataset, profiles columns for 
completeness, uniqueness, and validity, highlights outliers, and creates visualizations.
All data is synthetic, generated for portfolio practice.
"""

import os
import csv
import random
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Color Palette (Consistent professional theme)
ACCENT = "#2563EB"       # Professional blue
ACCENT_LIGHT = "#93C5FD"
ALERT = "#EA580C"        # Orange for highlighting errors
DARK = "#1E293B"
MUTED = "#64748B"
BG = "#FAFAFA"

# Set matplotlib parameters
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.facecolor": BG,
    "figure.facecolor": "white",
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": DARK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": DARK,
    "legend.frameon": False,
})

def run_data_quality_audit():
    random.seed(42)
    np.random.seed(42)
    print("Project 4: Simulating Billing Data & Profiling Quality...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir
    output_dir = os.path.join(script_dir, "outputs")
    assets_dir = os.path.join(script_dir, "assets")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Generate messy billing transaction data
    num_records = 1000
    valid_states = ["NY", "CA", "TX", "WA", "FL", "IL", "MA"]
    payment_methods_standard = ["Credit Card", "Debit Card", "UPI", "Net Banking"]

    data = []
    
    # Track metrics for validation during generation
    null_email_count = 0
    null_amount_count = 0
    null_state_count = 0
    duplicate_count = 0
    invalid_email_format = 0
    invalid_state_format = 0
    invalid_amount_val = 0  # negative or extreme outlier

    for i in range(num_records):
        tx_id = 1000000 + i
        cust_id = 50000 + random.randint(1, 450)
        
        # Customer Email
        r = random.random()
        if r < 0.05: # 5% null
            email = ""
            null_email_count += 1
        elif r < 0.08: # 3% invalid format
            email = f"cust_{cust_id}_at_gmail.com"
            invalid_email_format += 1
        else:
            email = f"customer_{cust_id}@gmail.com"

        # Transaction Date
        days_ago = random.randint(0, 90)
        tx_date = (pd.Timestamp('2026-06-01') - pd.Timedelta(days=days_ago)).strftime('%Y-%m-%d')

        # Transaction Amount
        r = random.random()
        if r < 0.03: # 3% null
            amount = np.nan
            null_amount_count += 1
        elif r < 0.05: # 2% negative amount
            amount = -1 * round(random.uniform(50.0, 500.0), 2)
            invalid_amount_val += 1
            null_amount_count += 0  # it is non-null but invalid
        elif r < 0.06: # 1% extreme high outlier
            amount = round(random.uniform(25000.0, 50000.0), 2)
            invalid_amount_val += 1
        else:
            amount = round(random.lognormvariate(5.5, 0.8), 2) # median ~245

        # Payment Method
        r = random.random()
        if r < 0.08: # casing issues
            payment = random.choice(["credit card", "CREDIT CARD", "cc", "upi", "UPI "])
        else:
            payment = random.choice(payment_methods_standard)

        # Billing State
        r = random.random()
        if r < 0.02: # 2% null
            state = ""
            null_state_count += 1
        elif r < 0.04: # 2% invalid code
            state = random.choice(["ZZ", "99", "XX"])
            invalid_state_format += 1
        else:
            state = random.choice(valid_states)

        data.append({
            "transaction_id": tx_id,
            "customer_id": cust_id,
            "customer_email": email,
            "transaction_date": tx_date,
            "transaction_amount": amount,
            "payment_method": payment,
            "billing_state": state
        })

    # Add 25 complete duplicate rows to make it 1,025 rows total
    duplicates = random.sample(data, 25)
    for row in duplicates:
        data.append(row.copy())
        duplicate_count += 1

    df_messy = pd.DataFrame(data)
    
    # Save the raw messy CSV (named logically)
    raw_csv = os.path.join(data_dir, "billing_transactions_raw.csv")
    df_messy.to_csv(raw_csv, index=False)
    print(f"- Saved raw data to {raw_csv}")

    # 2. Perform Data Quality Profiling & Audit
    total_rows = len(df_messy)
    
    # Completeness Check
    completeness = {}
    for col in df_messy.columns:
        nulls = df_messy[col].isna() | (df_messy[col] == "")
        completeness[col] = (total_rows - nulls.sum()) / total_rows

    # Uniqueness Check
    # (Checking duplicates relative to transaction_id)
    unique_tx = df_messy['transaction_id'].nunique()
    uniqueness = {
        "transaction_id": unique_tx / total_rows,
        "customer_id": 1.0, # Customer_id naturally repeats across transactions
        "customer_email": 1.0,
        "transaction_date": 1.0,
        "transaction_amount": 1.0,
        "payment_method": 1.0,
        "billing_state": 1.0
    }
    
    # Validity Check
    validity = {}
    
    # transaction_id validity (must be numeric and length 7)
    validity["transaction_id"] = df_messy["transaction_id"].apply(lambda x: str(x).isdigit() and len(str(x)) == 7).mean()
    
    # customer_id validity (must be integer > 0)
    validity["customer_id"] = df_messy["customer_id"].apply(lambda x: isinstance(x, (int, np.integer)) and x > 0).mean()
    
    # customer_email validity (must contain '@' and '.' and not be empty if present)
    def validate_email(email):
        if not email: return True # Non-null is checked by completeness
        return "@" in str(email) and "." in str(email).split("@")[-1]
    validity["customer_email"] = df_messy["customer_email"].apply(lambda x: validate_email(x) if pd.notna(x) and x != "" else True).mean()
    
    # transaction_date validity (must match YYYY-MM-DD)
    def validate_date(d):
        try:
            pd.to_datetime(d, format='%Y-%m-%d')
            return True
        except:
            return False
    validity["transaction_date"] = df_messy["transaction_date"].apply(validate_date).mean()
    
    # transaction_amount validity (must be positive and <= 10,000)
    def validate_amount(a):
        if pd.isna(a): return True # completeness handles null
        return a > 0 and a <= 10000.0
    validity["transaction_amount"] = df_messy["transaction_amount"].apply(validate_amount).mean()
    
    # payment_method validity (must be one of the standard methods exactly)
    validity["payment_method"] = df_messy["payment_method"].apply(lambda x: x in payment_methods_standard if pd.notna(x) and x != "" else True).mean()
    
    # billing_state validity (must be in the valid list)
    validity["billing_state"] = df_messy["billing_state"].apply(lambda x: x in valid_states if pd.notna(x) and x != "" else True).mean()

    # Consolidate Scorecard
    metrics = []
    for col in df_messy.columns:
        metrics.append({
            "Column": col,
            "Completeness": completeness[col],
            "Uniqueness": uniqueness[col],
            "Validity": validity[col]
        })
    df_scorecard = pd.DataFrame(metrics)
    scorecard_csv = os.path.join(output_dir, "data_quality_scorecard.csv")
    df_scorecard.to_csv(scorecard_csv, index=False)
    print(f"- Saved scorecard to {scorecard_csv}")

    # Outlier Analysis on Amount
    # Using IQR method
    valid_amounts = df_messy["transaction_amount"].dropna()
    valid_amounts = valid_amounts[valid_amounts > 0] # exclude negative/errors for IQR calculation
    q1 = valid_amounts.quantile(0.25)
    q3 = valid_amounts.quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 3 * iqr # 3x IQR for extreme outliers
    
    outliers_df = df_messy[
        (df_messy["transaction_amount"] > upper_bound) | 
        (df_messy["transaction_amount"] < 0)
    ]
    outliers_csv = os.path.join(output_dir, "amount_outliers.csv")
    outliers_df.to_csv(outliers_csv, index=False)
    print(f"- Saved {len(outliers_df)} amount outliers to {outliers_csv}")

    # Counts of issues for visualization
    # 1. Null counts
    null_counts = df_messy.apply(lambda x: (x.isna() | (x == "")).sum())
    
    # 2. Duplicate rows count
    duplicate_rows = df_messy.duplicated(subset=['transaction_id'], keep='first').sum()
    
    # 3. Format/Validity violations count
    # Let's count them specifically
    format_issues = {
        "transaction_id": 0,
        "customer_id": 0,
        "customer_email": df_messy["customer_email"].apply(lambda x: 0 if validate_email(x) else 1).sum(),
        "transaction_date": df_messy["transaction_date"].apply(lambda x: 0 if validate_date(x) else 1).sum(),
        "transaction_amount": df_messy["transaction_amount"].apply(lambda x: 0 if validate_amount(x) else 1).sum(),
        "payment_method": df_messy["payment_method"].apply(lambda x: 0 if (pd.isna(x) or x == "" or x in payment_methods_standard) else 1).sum(),
        "billing_state": df_messy["billing_state"].apply(lambda x: 0 if (pd.isna(x) or x == "" or x in valid_states) else 1).sum()
    }
    
    # Print statistics scorecard
    print("=" * 70)
    print("                    DATA QUALITY AUDIT SCORECARD")
    print("=" * 70)
    print(f"Total Rows Checked: {total_rows:<5} | Unique Transactions: {unique_tx:<4} | Duplicate Rows: {duplicate_rows}")
    print("-" * 70)
    print(df_scorecard.to_string(index=False, formatters={
        "Completeness": lambda x: f"{x:.2%}",
        "Uniqueness": lambda x: f"{x:.2%}" if x < 1.0 else "N/A",
        "Validity": lambda x: f"{x:.2%}"
    }))
    print("-" * 70)
    print("ISSUE SUMMARY COUNTS:")
    print(f"- Missing (Null) Values:   Email={null_counts['customer_email']}, Amount={null_counts['transaction_amount']}, State={null_counts['billing_state']}")
    print(f"- Validity / Format:       Invalid Email Casing/Format={format_issues['customer_email']}, Out-of-bounds State={format_issues['billing_state']}")
    print(f"- Amount Violations:       Negative/Extreme Outliers={format_issues['transaction_amount']}")
    print("=" * 70)

    # --- Generate Charts ---
    # Chart 1: Heatmap of Scorecard
    plt.figure(figsize=(7, 4))
    heatmap_data = df_scorecard.set_index("Column")
    # Drop Uniqueness for columns that are not keys to prevent distortion
    heatmap_data_clean = heatmap_data[["Completeness", "Validity"]].copy()
    heatmap_data_clean["Uniqueness"] = [unique_tx/total_rows if idx == "transaction_id" else 1.0 for idx in heatmap_data_clean.index]
    
    sns.heatmap(heatmap_data_clean, annot=True, fmt=".2%", cmap="Blues", cbar=False, linewidths=.5, annot_kws={"weight": "bold"})
    plt.title("Data Quality Profile Heatmap", fontsize=12, fontweight='bold', pad=15)
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "data_quality_heatmap.png"), dpi=150)
    plt.close()

    # Chart 2: Stacked Bar Chart of Issues by Column
    # Issues to plot: Null, Duplicate Key (only for tx_id), Format/Outlier Error
    plt.figure(figsize=(8, 4.5))
    columns = df_messy.columns
    nulls_to_plot = [null_counts[col] for col in columns]
    duplicates_to_plot = [duplicate_rows if col == "transaction_id" else 0 for col in columns]
    format_to_plot = [format_issues[col] for col in columns]
    
    ind = np.arange(len(columns))
    width = 0.5
    
    p1 = plt.bar(ind, nulls_to_plot, width, color='#93C5FD', edgecolor='#CBD5E1', label='Missing (Null)')
    p2 = plt.bar(ind, duplicates_to_plot, width, bottom=nulls_to_plot, color='#EA580C', edgecolor='#CBD5E1', label='Duplicate Key')
    bottom_3 = [n + d for n, d in zip(nulls_to_plot, duplicates_to_plot)]
    p3 = plt.bar(ind, format_to_plot, width, bottom=bottom_3, color='#FCA5A5', edgecolor='#CBD5E1', label='Format/Outlier Error')
    
    plt.ylabel('Issue Count', fontweight='bold')
    plt.title('Identified Data Anomalies per Column', fontsize=12, fontweight='bold', pad=15)
    plt.xticks(ind, columns, rotation=25, ha='right')
    plt.legend(loc='upper right', frameon=False)
    plt.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "data_issues_stacked_bar.png"), dpi=150)
    plt.close()

    # Chart 3: Donut Chart of Issue Share (<= 5 slices)
    plt.figure(figsize=(6, 5))
    total_nulls = sum(nulls_to_plot)
    total_duplicates = duplicate_rows
    total_format_err = sum(format_to_plot)
    
    issue_types = ['Missing (Null)', 'Duplicate Records', 'Format/Outliers']
    issue_counts = [total_nulls, total_duplicates, total_format_err]
    
    # Filter out zeros
    issue_types = [t for t, c in zip(issue_types, issue_counts) if c > 0]
    issue_counts = [c for c in issue_counts if c > 0]
    
    colors = ['#93C5FD', '#EA580C', '#FCA5A5']
    
    wedges, texts, autotexts = plt.pie(
        issue_counts, 
        labels=issue_types, 
        autopct='%1.1f%%',
        startangle=140, 
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    
    plt.setp(texts, fontweight='bold')
    plt.setp(autotexts, size=10, weight="bold")
    plt.title('Distribution of Data Quality Issues', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "issue_distribution_donut.png"), dpi=150)
    plt.close()

    print("\nSUCCESS: Project 4 Data Quality Audit complete. Saved scorecard and charts.")

if __name__ == "__main__":
    run_data_quality_audit()
