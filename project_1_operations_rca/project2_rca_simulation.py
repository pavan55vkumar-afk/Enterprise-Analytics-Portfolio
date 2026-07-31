"""
Project 2: Simulating Support Tickets & SLA Analysis
Generates synthetic tickets, performs Pandas SLA and CSAT analysis,
saves outputs to outputs/ and charts to assets/.
All data is synthetic, generated for portfolio practice.
"""

import os
import csv
import random
import pandas as pd
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Color Palette (Consistent, professional orange/red theme for operational alert context)
ACCENT = "#2563EB"  # Keep consistent professional blue
ACCENT_LIGHT = "#93C5FD"
ALERT = "#EA580C"   # Orange for warnings/breaches
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

def simulate_and_analyze_tickets():
    random.seed(42)
    print("Project 2: Simulating Support Tickets & SLA Analysis...")
    
    # Configuration
    num_tickets = 1000
    start_date = datetime(2026, 4, 1)
    
    categories = {
        "Billing": {"sla_hours": 24, "base_time_hours": 12, "satisfaction_base": 4.2},
        "Technical Support": {"sla_hours": 48, "base_time_hours": 36, "satisfaction_base": 3.8},
        "Account Access": {"sla_hours": 12, "base_time_hours": 6, "satisfaction_base": 4.5},
        "Delivery Issue": {"sla_hours": 72, "base_time_hours": 80, "satisfaction_base": 2.9} # Intentional bottleneck
    }
    
    priorities = ["Low", "Medium", "High"]
    statuses = ["Resolved", "Resolved", "Resolved", "Resolved", "Closed", "Open", "In Progress"]
    
    tickets = []
    
    for ticket_id in range(20001, 20001 + num_tickets):
        cat = random.choice(list(categories.keys()))
        pri = random.choice(priorities)
        status = random.choice(statuses)
        
        # Created Date
        created_days = random.randint(0, 60)
        created_seconds = random.randint(0, 86400)
        created_dt = start_date + timedelta(days=created_days, seconds=created_seconds)
        
        sla = categories[cat]["sla_hours"]
        base_time = categories[cat]["base_time_hours"]
        
        # Scaling handling time based on priority (high priority resolved faster)
        pri_factor = 0.6 if pri == "High" else (1.0 if pri == "Medium" else 1.4)
        
        # Resolved Date & Satisfaction
        resolved_dt = None
        sat_score = None
        handling_time = None
        is_breach = False
        
        if status in ["Resolved", "Closed"]:
            # Generate random handling time in hours following lognormal-like distribution
            handling_time = abs(random.normalvariate(base_time * pri_factor, base_time * 0.4 * pri_factor))
            handling_time = max(0.5, round(handling_time, 2))
            
            resolved_dt = created_dt + timedelta(hours=handling_time)
            is_breach = handling_time > sla
            
            # Satisfaction rating based on SLA breach and category baseline
            if is_breach:
                sat_score = max(1, round(categories[cat]["satisfaction_base"] - random.uniform(1.5, 2.5)))
            else:
                sat_score = min(5, round(categories[cat]["satisfaction_base"] + random.uniform(-0.5, 0.5)))
        else:
            is_breach = False
            
        tickets.append({
            "ticket_id": ticket_id,
            "created_at": created_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": resolved_dt.strftime("%Y-%m-%d %H:%M:%S") if resolved_dt else "",
            "status": status,
            "priority": pri,
            "category": cat,
            "sla_hours": sla,
            "handling_time_hours": handling_time if handling_time is not None else "",
            "is_breach": 1 if is_breach else 0,
            "customer_satisfaction": sat_score if sat_score is not None else ""
        })
        
    # Write to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir
    output_dir = os.path.join(script_dir, "outputs")
    assets_dir = os.path.join(script_dir, "assets")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    csv_file = os.path.join(data_dir, "tickets.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
        writer.writeheader()
        writer.writerows(tickets)
    print(f"- Saved {csv_file}")
    
    # --- Pandas Analysis ---
    print("\nExecuting Operations Analytics Engine (Pandas)...")
    df = pd.DataFrame(tickets)
    
    # Cast column types
    df['handling_time_hours'] = pd.to_numeric(df['handling_time_hours'], errors='coerce')
    df['customer_satisfaction'] = pd.to_numeric(df['customer_satisfaction'], errors='coerce')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['resolved_at'] = pd.to_datetime(df['resolved_at'])
    
    # SLA Metrics
    total_count = len(df)
    resolved_df = df[df['status'].isin(['Resolved', 'Closed'])]
    resolved_count = len(resolved_df)
    breached_count = resolved_df['is_breach'].sum()
    sla_compliance = ((resolved_count - breached_count) / resolved_count) * 100
    
    print("=" * 70)
    print("                     OPERATIONAL METRICS & RCA REPORT")
    print("=" * 70)
    print(f"Reporting Window: {start_date.strftime('%Y-%m-%d')} to 2026-06-01")
    print(f"Total Tickets Received: {total_count}")
    print(f"Total Tickets Resolved: {resolved_count} ({resolved_count/total_count*100:.1f}% Resolution Rate)")
    print(f"Overall SLA Compliance: {sla_compliance:.2f}%\n")
    
    # Category Grouping
    cat_df = resolved_df.groupby('category').agg(
        volume=('ticket_id', 'count'),
        avg_handling_time=('handling_time_hours', 'mean'),
        sla_target=('sla_hours', 'first'),
        breach_count=('is_breach', 'sum'),
        avg_csat=('customer_satisfaction', 'mean')
    ).reset_index()
    
    cat_df['breach_rate_pct'] = (cat_df['breach_count'] / cat_df['volume']) * 100
    cat_df.to_csv(os.path.join(output_dir, "sla_by_category.csv"), index=False)
    
    print(f"{'Ticket Category':<20} | {'Volume':<8} | {'Avg Handling (Hrs)':<18} | {'SLA Target':<10} | {'SLA Breach %':<12} | {'Avg CSAT':<8}")
    print("-" * 85)
    for _, row in cat_df.iterrows():
        print(f"{row['category']:<20} | {int(row['volume']):<8} | {row['avg_handling_time']:<18.2f} | {int(row['sla_target']):<10} | {row['breach_rate_pct']:<12.1f}% | {row['avg_csat']:<8.2f}")
    print("-" * 85)
    
    # Root Cause Analysis
    bottleneck_row = cat_df.loc[cat_df['breach_rate_pct'].idxmax()]
    print("\nROOT CAUSE ANALYSIS (RCA) & PROCESS RECOMMENDATIONS:")
    print(f"1. Primary Bottleneck Identified: '{bottleneck_row['category']}' requests.")
    print(f"   - SLA Breach Rate is {bottleneck_row['breach_rate_pct']:.1f}%, which dramatically exceeds acceptable thresholds.")
    print(f"   - Root Cause: The average handling time ({bottleneck_row['avg_handling_time']:.1f} hours) exceeds the SLA target of {bottleneck_row['sla_target']} hours.")
    
    # CSAT Analysis
    csat_df = resolved_df.groupby('is_breach')['customer_satisfaction'].mean().reset_index()
    csat_df.to_csv(os.path.join(output_dir, "csat_by_sla_status.csv"), index=False)
    
    avg_met_csat = resolved_df[resolved_df['is_breach'] == 0]['customer_satisfaction'].mean()
    avg_breached_csat = resolved_df[resolved_df['is_breach'] == 1]['customer_satisfaction'].mean()
    
    print("2. Customer Sentiment Impact:")
    print(f"   - Tickets resolved WITHIN SLA achieved an average CSAT of {avg_met_csat:.2f}/5.0.")
    print(f"   - Tickets breaching SLA dropped to an average CSAT of {avg_breached_csat:.2f}/5.0 (Delta of {avg_met_csat - avg_breached_csat:.2f} points).")
    print("3. Business Analyst Action Plan:")
    print("   - Redesign standard operating procedures (SOPs) for 'Delivery Issue' processing.")
    print("   - Implement an automated escalation trigger in the CRM when a ticket hits 50% of its SLA timeline.")
    print("   - Conduct a time-motion audit of agents working on 'Delivery Issues' to re-allocate resource bandwidth.")
    print("=" * 70)
    
    # --- Generate Charts ---
    # Chart 1: Pareto Chart of Breaches
    plt.figure(figsize=(8, 4.5))
    pareto_data = cat_df.sort_values(by='breach_count', ascending=False)
    pareto_data['cumulative_pct'] = (pareto_data['breach_count'].cumsum() / pareto_data['breach_count'].sum()) * 100
    
    ax1 = plt.gca()
    bars = ax1.bar(pareto_data['category'], pareto_data['breach_count'], color=ACCENT, alpha=0.8, width=0.5)
    ax1.set_ylabel('Number of SLA Breaches', color=DARK, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=MUTED)
    ax1.set_xticks(range(len(pareto_data)))
    ax1.set_xticklabels(pareto_data['category'], rotation=15, ha='right')
    
    ax2 = ax1.twinx()
    ax2.plot(pareto_data['category'], pareto_data['cumulative_pct'], color=ALERT, marker='D', ms=5, linewidth=1.5)
    ax2.set_ylabel('Cumulative % of Breaches', color=DARK, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=MUTED)
    ax2.set_ylim(0, 110)
    
    plt.title('SLA Breaches by Category (Pareto Analysis)', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "pareto_sla_breaches.png"), dpi=150)
    plt.close()
    
    # Chart 2: Grouped Bar CSAT
    plt.figure(figsize=(8, 4.5))
    csat_groups = resolved_df.groupby(['category', 'is_breach'])['customer_satisfaction'].mean().unstack().reset_index()
    csat_groups.columns = ['Category', 'SLA Met', 'SLA Breached']
    
    x_positions = range(len(csat_groups))
    width = 0.35
    
    plt.bar([x - width/2 for x in x_positions], csat_groups['SLA Met'], width, label='SLA Met', color=ACCENT)
    plt.bar([x + width/2 for x in x_positions], csat_groups['SLA Breached'], width, label='SLA Breached', color=ALERT)
    
    plt.xticks(x_positions, csat_groups['Category'])
    plt.ylabel('Average CSAT Score (1-5)', fontweight='bold')
    plt.title('Average Customer Satisfaction (CSAT): SLA Met vs. Breached', fontsize=12, fontweight='bold', pad=15)
    plt.ylim(0, 5.5)
    plt.legend(loc='upper right')
    plt.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "csat_comparison.png"), dpi=150)
    plt.close()
    
    # Chart 3: Stacked Bar - Tickets by Month and Status
    plt.figure(figsize=(8, 4.5))
    df['month'] = df['created_at'].dt.strftime('%Y-%m')
    
    # Categorize status
    def categorize_status(row):
        if row['status'] in ['Open', 'In Progress']:
            return 'Open'
        elif row['is_breach'] == 1:
            return 'Resolved (Breached)'
        else:
            return 'Resolved (Met)'
            
    df['ticket_status'] = df.apply(categorize_status, axis=1)
    
    status_monthly = df.groupby(['month', 'ticket_status']).size().unstack(fill_value=0)
    # Ensure correct column order
    cols = [c for c in ['Resolved (Met)', 'Resolved (Breached)', 'Open'] if c in status_monthly.columns]
    status_monthly = status_monthly[cols]
    
    status_monthly.plot(kind='bar', stacked=True, color=[ACCENT, ALERT, '#CBD5E1'], ax=plt.gca(), width=0.6)
    plt.ylabel('Number of Tickets', fontweight='bold')
    plt.xlabel('Month', fontweight='bold')
    plt.title('Ticket Volume and SLA Performance over Time', fontsize=12, fontweight='bold', pad=15)
    plt.xticks(rotation=0)
    plt.legend(loc='upper left')
    plt.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "ticket_status_volume.png"), dpi=150)
    plt.close()
    
    print("\nSUCCESS: Project 2 SLA simulation and analysis complete.")

if __name__ == "__main__":
    simulate_and_analyze_tickets()
