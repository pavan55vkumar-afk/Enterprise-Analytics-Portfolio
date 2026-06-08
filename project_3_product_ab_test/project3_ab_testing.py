import csv
import random
import math
import os
from collections import defaultdict

def run_ab_test_simulation():
    print("Project 3: Simulating Product A/B Test & Conversion Funnel...")
    
    # 1. Setup Parameters
    # Control Group: baseline conversion rate (CR) = 12%
    # Variant Group: new checkout layout, expected CR = 14.5% (a 2.5% absolute lift)
    num_users = 5000
    
    users = []
    
    for user_id in range(100001, 100001 + num_users):
        group = "variant" if random.random() < 0.5 else "control"
        device = random.choice(["Mobile", "Mobile", "Desktop", "Tablet"])
        
        # Determine conversion based on group probability
        cr = 0.12 if group == "control" else 0.145
        
        # Mobile conversion is usually slightly lower, Desktop is higher
        device_modifier = 0.85 if device == "Mobile" else (1.2 if device == "Desktop" else 1.0)
        adjusted_cr = cr * device_modifier
        
        converted = 1 if random.random() < adjusted_cr else 0
        
        # Revenue generation for converted users
        revenue = 0.0
        if converted == 1:
            revenue = round(random.lognormvariate(math.log(1500), 0.5), 2) # Avg spend around 1500 INR
            
        users.append({
            "user_id": user_id,
            "group": group,
            "device": device,
            "converted": converted,
            "revenue": revenue
        })
        
    # Write to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "ab_test_data.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    print(f"- Saved {csv_file}")
    
    # -------------------------------------------------------------------------
    # STATISTICAL ANALYSIS ENGINE (Pure Python Implementation of Z-Test)
    # -------------------------------------------------------------------------
    print("\nCalculating A/B Test Metrics and Hypothesis Testing...")
    
    # Aggregate counts
    groups = defaultdict(lambda: {"visitors": 0, "conversions": 0, "total_revenue": 0.0})
    for u in users:
        g = u["group"]
        groups[g]["visitors"] += 1
        if u["converted"] == 1:
            groups[g]["conversions"] += 1
            groups[g]["total_revenue"] += u["revenue"]
            
    control = groups["control"]
    variant = groups["variant"]
    
    n_c = control["visitors"]
    x_c = control["conversions"]
    p_c = x_c / n_c
    
    n_v = variant["visitors"]
    x_v = variant["conversions"]
    p_v = x_v / n_v
    
    # Combined pooled conversion rate
    p_pooled = (x_c + x_v) / (n_c + n_v)
    
    # Standard Error (SE) for the difference
    se_diff = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_c + 1/n_v))
    
    # Z-Score
    z_score = (p_v - p_c) / se_diff
    
    # P-Value calculation from Z-score (using standard cumulative distribution approximation)
    # Two-tailed test
    def normal_cdf(z):
        return (1.0 + math.erf(z / math.sqrt(2.0))) / 2.0
    
    p_value = 2 * (1 - normal_cdf(abs(z_score)))
    
    # Confidence Interval (95%)
    z_critical = 1.96 # For 95% confidence
    ci_margin = z_critical * math.sqrt(p_c*(1-p_c)/n_c + p_v*(1-p_v)/n_v)
    diff = p_v - p_c
    ci_lower = diff - ci_margin
    ci_upper = diff + ci_margin
    
    # Print Statistical Report
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
    print("HYPOTHESIS TESTING CONCLUSION:")
    if p_value < alpha:
        print(f"SUCCESS: The P-Value ({p_value:.5f}) is LESS than the significance level alpha ({alpha}).")
        print("-> Reject the Null Hypothesis. The change in checkout layout has a statistically")
        print("   significant positive effect on conversion rates.")
        print("-> RECOMMENDATION: Roll out the new checkout layout to 100% of traffic.")
    else:
        print(f"INCONCLUSIVE: The P-Value ({p_value:.5f}) is GREATER than or equal to alpha ({alpha}).")
        print("-> Fail to Reject the Null Hypothesis. The conversion difference could be due to random noise.")
        print("-> RECOMMENDATION: Do not deploy variant; run test longer or iterate on the design.")
    print("=" * 70)

if __name__ == "__main__":
    run_ab_test_simulation()
