"""
Project 1 Analysis Runner: Customer Revenue, Retention, and RFM Analysis
Runs the SQL analysis using DuckDB, saves CSV outputs, and generates charts.
All data is synthetic, generated for portfolio practice.
"""

import os
import duckdb
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Color Palette (Consistent, professional blue accent)
ACCENT = "#2563EB"
ACCENT_LIGHT = "#93C5FD"
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

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir
    output_dir = os.path.join(script_dir, "outputs")
    assets_dir = os.path.join(script_dir, "assets")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    # Initialize DuckDB in-memory database
    con = duckdb.connect(database=':memory:')
    
    # Load CSV data
    customers_csv = os.path.join(data_dir, "customers.csv")
    orders_csv = os.path.join(data_dir, "orders.csv")
    
    if not os.path.exists(customers_csv) or not os.path.exists(orders_csv):
        print("CSV files not found. Running generate_data.py first...")
        from generate_data import generate_cohort_data
        generate_cohort_data()
        
    con.execute(f"CREATE TABLE customers AS SELECT * FROM read_csv_auto('{customers_csv}')")
    con.execute(f"CREATE TABLE orders AS SELECT * FROM read_csv_auto('{orders_csv}')")
    
    print("DuckDB loaded data:")
    print(f"- Customers: {con.execute('SELECT COUNT(*) FROM customers').fetchone()[0]} rows")
    print(f"- Orders: {con.execute('SELECT COUNT(*) FROM orders').fetchone()[0]} rows")
    
    # Read the SQL queries
    sql_path = os.path.join(script_dir, "project1_cohort_retention.sql")
    with open(sql_path, "r") as f:
        sql_content = f.read()
        
    # Split queries by semicolon (excluding empty statements)
    # DuckDB can run multiple commands, but to capture individual results, we split them.
    queries = []
    current_query = []
    for line in sql_content.split('\n'):
        if line.strip().startswith('--'):
            continue
        current_query.append(line)
        if ';' in line:
            queries.append('\n'.join(current_query))
            current_query = []
            
    if current_query and ''.join(current_query).strip():
        queries.append('\n'.join(current_query))
        
    # Filter empty queries
    queries = [q.strip() for q in queries if q.strip()]
    
    print(f"Found {len(queries)} main analysis queries in SQL file.")
    
    # Execute Query 1: Monthly Growth & Return Rate
    print("\nExecuting Query 1: Monthly Revenue & Growth...")
    df_revenue = con.execute(queries[0]).df()
    df_revenue.to_csv(os.path.join(output_dir, "monthly_revenue_mom.csv"), index=False)
    print(df_revenue.to_string(index=False))
    
    # Execute Query 2: Cohort Retention
    print("\nExecuting Query 2: Cohort Retention Matrix...")
    df_retention = con.execute(queries[1]).df()
    df_retention.to_csv(os.path.join(output_dir, "cohort_retention.csv"), index=False)
    print(df_retention.to_string(index=False))
    
    # Execute Query 3: RFM Segmentation
    print("\nExecuting Query 3: RFM Customer Segmentation...")
    df_rfm = con.execute(queries[2]).df()
    df_rfm.to_csv(os.path.join(output_dir, "rfm_segmentation.csv"), index=False)
    print(df_rfm.head(10).to_string(index=False))
    
    # --- Generate Charts ---
    print("\nGenerating charts...")
    
    # Chart 1: Monthly Revenue Trend
    plt.figure(figsize=(8, 4.5))
    ax1 = plt.gca()
    # Plot revenue
    ax1.plot(df_revenue['month'], df_revenue['current_month_net_revenue'] / 100000, marker='o', color=ACCENT, linewidth=2, label='Net Revenue')
    ax1.set_ylabel('Net Revenue (INR Lakhs)', color=DARK, fontweight='bold')
    ax1.set_xlabel('Month', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=MUTED)
    ax1.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1')
    
    # Secondary axis for growth rate
    ax2 = ax1.twinx()
    # Fill NaN for plotting line
    growth_plot = df_revenue['mom_growth_pct'].fillna(0)
    ax2.plot(df_revenue['month'], growth_plot, marker='s', color='#F97316', linestyle='--', linewidth=1.5, label='MoM Growth %')
    ax2.set_ylabel('Month-over-Month Growth (%)', color=DARK, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=MUTED)
    
    # Add a baseline at 0% for growth
    ax2.axhline(0, color=MUTED, linestyle='-', linewidth=0.5, alpha=0.5)
    
    plt.title('Monthly Completed-Order Revenue & Month-over-Month Growth', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "monthly_revenue.png"), dpi=150)
    plt.close()
    
    # Chart 2: Cohort Retention Heatmap
    plt.figure(figsize=(8, 4.5))
    # Prepare data for heatmap: index=cohort, columns=periods
    heatmap_data = df_retention.set_index('cohort')[[c for c in df_retention.columns if 'pct' in c]]
    # Clean up column labels (e.g. 'period_0_pct' -> 'Month 0')
    heatmap_data.columns = [f"M{c.split('_')[1]}" for c in heatmap_data.columns]
    
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="Blues", cbar=False, 
                annot_kws={"size": 10, "weight": "bold"}, linewidths=0.5)
    plt.title('Customer Cohort Retention Rate (%)', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Periods (Months Since Signup)', fontweight='bold')
    plt.ylabel('Signup Month Cohort', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "cohort_retention_heatmap.png"), dpi=150)
    plt.close()
    
    # Chart 3: RFM Segment Distribution
    plt.figure(figsize=(8, 4.5))
    segment_counts = df_rfm['customer_segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Customer Count']
    
    # Sort segments by size
    segment_counts = segment_counts.sort_values(by='Customer Count', ascending=True)
    
    # Horizontal bar plot
    bars = plt.barh(segment_counts['Segment'], segment_counts['Customer Count'], color=ACCENT, height=0.6)
    
    # Customize labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                 va='center', ha='left', fontsize=9, fontweight='bold', color=DARK)
                 
    plt.title('Customer Segment Distribution (RFM)', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Number of Customers', fontweight='bold')
    plt.xlim(0, segment_counts['Customer Count'].max() * 1.15)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.grid(axis='x', linestyle=':', alpha=0.6, color='#CBD5E1')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "rfm_distribution.png"), dpi=150)
    plt.close()
    
    # Verify Champions logic
    champions = df_rfm[df_rfm['customer_segment'].str.contains('Champions')]
    print(f"\nVerification: Found {len(champions)} Champions.")
    print("Top 5 Champions details:")
    print(champions.head(5)[['customer_id', 'recency_days', 'frequency_count', 'monetary_value', 'rfm_code']])
    
    # Make sure Champions have recent purchases, high frequency, high spend
    assert len(champions) > 0, "No Champions found. Check RFM scoring logic."
    for idx, row in champions.iterrows():
        # rfm_code characters represent R, F, M scores.
        # R should be >= 4, F should be >= 4, M should be >= 4 (as defined in code segment categorization)
        # Note: Champions segment is ('555', '554', '545', '455', '454', '445')
        r, f, m = int(row['rfm_code'][0]), int(row['rfm_code'][1]), int(row['rfm_code'][2])
        assert r >= 4 and f >= 4 and m >= 4, f"Invalid Champion RFM score: {row['rfm_code']} for customer {row['customer_id']}"
        
    print("\nSUCCESS: Project 1 analysis complete. All CSVs and charts saved, and RFM Champions verified.")

if __name__ == "__main__":
    main()
