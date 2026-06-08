"""
Project 3: Simulating Product A/B Test & Conversion Funnel
Generates synthetic experiment data, computes two-proportion Z-test metrics from scratch,
saves outputs to outputs/ and charts to assets/.
All data is synthetic, generated for portfolio practice.
"""

import os
import csv
import math
import random
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Color Palette (Consistent professional theme)
ACCENT = "#2563EB"       # Professional blue
ACCENT_LIGHT = "#93C5FD"
ALERT = "#EA580C"        # Orange for highlighting
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

def run_ab_test_simulation():
    random.seed(42)
    print("Project 3: Simulating Product A/B Test & Conversion Funnel...")
    
    # 1. Setup Parameters
    # Control Group: baseline conversion rate (CR) = 12%
    # Variant Group: new checkout layout, expected CR = 14.5%
    num_users = 5000
    
    users = []
    
    for user_id in range(100001, 100001 + num_users):
        group = "variant" if random.random() < 0.5 else "control"
        device = random.choice(["Mobile", "Mobile", "Desktop", "Tablet"])
        
        cr = 0.12 if group == "control" else 0.145
        
        # Mobile conversion is lower, Desktop is higher
        device_modifier = 0.85 if device == "Mobile" else (1.2 if device == "Desktop" else 1.0)
        adjusted_cr = cr * device_modifier
        
        converted = 1 if random.random() < adjusted_cr else 0
        
        # Revenue generation for converted users
        revenue = 0.0
        if converted == 1:
            revenue = round(random.lognormvariate(math.log(1500), 0.5), 2)
            
        users.append({
            "user_id": user_id,
            "group": group,
            "device": device,
            "converted": converted,
            "revenue": revenue
        })
        
    # Write to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir
    output_dir = os.path.join(script_dir, "outputs")
    assets_dir = os.path.join(script_dir, "assets")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    csv_file = os.path.join(data_dir, "ab_test_data.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    print(f"- Saved {csv_file}")
    
    # --- Statistical Analysis ---
    df = pd.DataFrame(users)
    
    summary = df.groupby('group').agg(
        visitors=('user_id', 'count'),
        conversions=('converted', 'sum'),
        total_revenue=('revenue', 'sum')
    ).reset_index()
    
    control_row = summary[summary['group'] == 'control'].iloc[0]
    variant_row = summary[summary['group'] == 'variant'].iloc[0]
    
    n_c = control_row['visitors']
    x_c = control_row['conversions']
    p_c = x_c / n_c
    
    n_v = variant_row['visitors']
    x_v = variant_row['conversions']
    p_v = x_v / n_v
    
    # Combined pooled conversion rate
    p_pooled = (x_c + x_v) / (n_c + n_v)
    
    # Standard Error (SE) for the difference
    se_diff = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_c + 1/n_v))
    
    # Z-Score
    z_score = (p_v - p_c) / se_diff
    
    # P-Value calculation from Z-score (using standard cumulative distribution approximation)
    def normal_cdf(z):
        return (1.0 + math.erf(z / math.sqrt(2.0))) / 2.0
    
    p_value = 2 * (1 - normal_cdf(abs(z_score)))
    
    # Confidence Interval (95%)
    z_critical = 1.96
    ci_margin = z_critical * math.sqrt(p_c*(1-p_c)/n_c + p_v*(1-p_v)/n_v)
    diff = p_v - p_c
    ci_lower = diff - ci_margin
    ci_upper = diff + ci_margin
    
    print("=" * 70)
    print("                   PRODUCT A/B EXPERIMENT SCORECARD")
    print("=" * 70)
    print(f"Control Group (Current Flow):  n = {n_c:<5} | Conversions = {x_c:<4} | Conversion Rate = {p_c:.2%}")
    print(f"Variant Group (New Checkout):  n = {n_v:<5} | Conversions = {x_v:<4} | Conversion Rate = {p_v:.2%}")
    print("-" * 70)
    print(f"Observed Conversion Rate Lift: {diff:+.2%}")
    print(f"95% Confidence Interval (CI):  [{ci_lower:+.2%} to {ci_upper:+.2%}]")
    print(f"Calculated Z-Statistic:         {z_score:.4f}")
    print(f"Calculated P-Value:             {p_value:.5f}")
    print("-" * 70)
    
    alpha = 0.05
    is_significant = p_value < alpha
    
    print("HYPOTHESIS TESTING CONCLUSION:")
    if is_significant:
        print(f"SUCCESS: The P-Value ({p_value:.5f}) is LESS than the significance level alpha ({alpha}).")
        print("-> Reject the Null Hypothesis. The change in checkout layout has a statistically")
        print("   significant positive effect on conversion rates.")
        print("-> RECOMMENDATION: Roll out the new checkout layout to 100% of traffic.")
    else:
        print(f"INCONCLUSIVE: The P-Value ({p_value:.5f}) is GREATER than or equal to alpha ({alpha}).")
        print("-> Fail to Reject the Null Hypothesis. The conversion difference could be due to random noise.")
        print("-> RECOMMENDATION: Do not deploy variant; run test longer or iterate on the design.")
    print("=" * 70)
    
    # Save metrics to CSV
    metrics_summary = pd.DataFrame([{
        "control_visitors": n_c,
        "control_conversions": x_c,
        "control_cr": p_c,
        "variant_visitors": n_v,
        "variant_conversions": x_v,
        "variant_cr": p_v,
        "absolute_lift": diff,
        "relative_lift": diff / p_c,
        "z_score": z_score,
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "is_statistically_significant": 1 if is_significant else 0
    }])
    metrics_summary.to_csv(os.path.join(output_dir, "ab_test_metrics.csv"), index=False)
    
    # --- Generate Charts ---
    # Chart 1: Grouped Bar Chart with CI Error Bars
    plt.figure(figsize=(8, 4.5))
    groups = ['Control', 'Variant']
    rates = [p_c * 100, p_v * 100]
    
    # Error bar represents the 95% CI margin of error for each proportion
    # Margin of error for control: z_critical * sqrt(p_c*(1-p_c)/n_c)
    err_c = z_critical * math.sqrt(p_c * (1 - p_c) / n_c) * 100
    err_v = z_critical * math.sqrt(p_v * (1 - p_v) / n_v) * 100
    yerr = [err_c, err_v]
    
    bars = plt.bar(groups, rates, yerr=yerr, color=[ACCENT_LIGHT, ACCENT], capsize=10, width=0.5, edgecolor='#CBD5E1')
    
    # Annotate rates on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height / 2.0, f'{height:.2f}%', 
                 ha='center', va='center', color='white', fontweight='bold', fontsize=11)
                 
    plt.ylabel('Conversion Rate (%)', fontweight='bold')
    plt.title('Checkout Conversion Rate: Control vs. Variant (95% CI)', fontsize=12, fontweight='bold', pad=15)
    plt.ylim(0, max(rates) * 1.3)
    plt.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "conversion_rate_comparison.png"), dpi=150)
    plt.close()
    
    # Chart 2: Normal Distribution Hypothesis Curve
    plt.figure(figsize=(8, 4.5))
    x = np.linspace(-4, 4, 1000)
    y = np.exp(-x**2/2) / np.sqrt(2*np.pi)
    
    plt.plot(x, y, color=DARK, linewidth=1.5, label='Standard Normal Curve')
    
    # Highlight Critical Regions (Rejection Region at alpha = 0.05, two-tailed z = 1.96)
    plt.fill_between(x, y, where=(x <= -1.96), color='#FCA5A5', alpha=0.5, label='Rejection Region (alpha = 0.05)')
    plt.fill_between(x, y, where=(x >= 1.96), color='#FCA5A5', alpha=0.5)
    
    # Plot Z-statistic line
    plt.axvline(z_score, color=ALERT, linestyle='-', linewidth=2.0, label=f'Z-Statistic ({z_score:.2f})')
    
    # Plot annotations
    plt.text(z_score - 0.2, 0.25, f'Z = {z_score:.2f}\n(p = {p_value:.5f})', color=ALERT, 
             fontweight='bold', ha='right', va='center')
    plt.text(1.96 + 0.1, 0.02, 'z_crit = +1.96', color='#DC2626', fontsize=8, ha='left')
    plt.text(-1.96 - 0.1, 0.02, 'z_crit = -1.96', color='#DC2626', fontsize=8, ha='right')
    
    plt.title('Hypothesis Testing: Z-Statistic vs. Rejection Regions', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Standard Deviations (z)', fontweight='bold')
    plt.ylabel('Probability Density', fontweight='bold')
    plt.legend(loc='upper left', frameon=False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "normal_distribution_hypothesis.png"), dpi=150)
    plt.close()
    
    print("\nSUCCESS: Project 3 A/B test simulation and analysis complete.")

if __name__ == "__main__":
    run_ab_test_simulation()
