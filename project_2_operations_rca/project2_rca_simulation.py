import csv
import random
import os
from datetime import datetime, timedelta

def simulate_and_analyze_tickets():
    print("Project 2: Simulating Support Tickets & SLA Analysis...")
    
    # Configuration
    num_tickets = 1000
    start_date = datetime(2026, 4, 1)
    
    categories = {
        "Billing": {"sla_hours": 24, "base_time_hours": 12, "satisfaction_base": 4.2},
        "Technical Support": {"sla_hours": 48, "base_time_hours": 36, "satisfaction_base": 3.8},
        "Account Access": {"sla_hours": 12, "base_time_hours": 6, "satisfaction_base": 4.5},
        "Delivery Issue": {"sla_hours": 72, "base_time_hours": 80, "satisfaction_base": 2.9} # Intentional bottleneck: avg time exceeds SLA!
    }
    
    priorities = ["Low", "Medium", "High"]
    statuses = ["Resolved", "Resolved", "Resolved", "Resolved", "Closed", "Open", "In Progress"] # Mostly resolved for performance stats
    
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
        sat_score = ""
        
        if status in ["Resolved", "Closed"]:
            # Generate random handling time in hours following lognormal-like distribution
            handling_time = abs(random.normalvariate(base_time * pri_factor, base_time * 0.4 * pri_factor))
            handling_time = max(0.5, round(handling_time, 2)) # Min 30 mins
            
            resolved_dt = created_dt + timedelta(hours=handling_time)
            
            # Determine SLA Breach
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
            "handling_time_hours": handling_time if resolved_dt else "",
            "is_breach": 1 if is_breach else 0,
            "customer_satisfaction": sat_score
        })
        
    # Write to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "tickets.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
        writer.writeheader()
        writer.writerows(tickets)
    print(f"- Saved {csv_file}")
    
    # -------------------------------------------------------------------------
    # ANALYSIS ENGINE (Replicating typical Business/Data Analyst workflow)
    # -------------------------------------------------------------------------
    print("\nExecuting Operations Analytics Engine...")
    
    total_count = len(tickets)
    resolved_count = sum(1 for t in tickets if t["resolved_at"] != "")
    breached_count = sum(1 for t in tickets if t["is_breach"] == 1)
    
    sla_compliance = (resolved_count - breached_count) / resolved_count * 100
    
    # Group By Category
    cat_stats = {}
    for t in tickets:
        cat = t["category"]
        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "resolved": 0, "breaches": 0, "total_time": 0.0, "sat_scores": []}
            
        cat_stats[cat]["total"] += 1
        if t["resolved_at"]:
            cat_stats[cat]["resolved"] += 1
            cat_stats[cat]["total_time"] += float(t["handling_time_hours"])
            if t["is_breach"] == 1:
                cat_stats[cat]["breaches"] += 1
            if t["customer_satisfaction"] != "":
                cat_stats[cat]["sat_scores"].append(int(t["customer_satisfaction"]))
                
    # Print RCA Report
    print("=" * 70)
    print("                     OPERATIONAL METRICS & RCA REPORT")
    print("=" * 70)
    print(f"Reporting Window: {start_date.strftime('%Y-%m-%d')} to 2026-06-01")
    print(f"Total Tickets Received: {total_count}")
    print(f"Total Tickets Resolved: {resolved_count} ({resolved_count/total_count*100:.1f}% Resolution Rate)")
    print(f"Overall SLA Compliance: {sla_compliance:.2f}%\n")
    
    print(f"{'Ticket Category':<20} | {'Volume':<8} | {'Avg Handling (Hrs)':<18} | {'SLA Target':<10} | {'SLA Breach %':<12} | {'Avg CSAT':<8}")
    print("-" * 85)
    
    bottleneck_cat = ""
    max_breach_rate = 0.0
    
    for cat, stats in cat_stats.items():
        avg_time = stats["total_time"] / stats["resolved"] if stats["resolved"] > 0 else 0
        breach_rate = (stats["breaches"] / stats["resolved"] * 100) if stats["resolved"] > 0 else 0
        avg_csat = sum(stats["sat_scores"]) / len(stats["sat_scores"]) if len(stats["sat_scores"]) > 0 else 0
        
        if breach_rate > max_breach_rate:
            max_breach_rate = breach_rate
            bottleneck_cat = cat
            
        print(f"{cat:<20} | {stats['total']:<8} | {avg_time:<18.2f} | {tickets[0]['sla_hours'] if cat==tickets[0]['category'] else categories[cat]['sla_hours']:<10} | {breach_rate:<12.1f}% | {avg_csat:<8.2f}")
    
    print("-" * 85)
    print("\nROOT CAUSE ANALYSIS (RCA) & PROCESS RECOMMENDATIONS:")
    print(f"1. Primary Bottleneck Identified: '{bottleneck_cat}' requests.")
    print(f"   - SLA Breach Rate is {max_breach_rate:.1f}%, which dramatically exceeds acceptable thresholds.")
    print(f"   - Root Cause: The average handling time ({cat_stats[bottleneck_cat]['total_time']/cat_stats[bottleneck_cat]['resolved']:.1f} hours) exceeds the SLA target of {categories[bottleneck_cat]['sla_hours']} hours.")
    print("2. Customer Sentiment Impact:")
    
    # Calculate CSAT comparison for SLA breached vs met
    satisfied_sla_met = []
    satisfied_sla_breached = []
    for t in tickets:
        if t["customer_satisfaction"] != "":
            csat = int(t["customer_satisfaction"])
            if t["is_breach"] == 1:
                satisfied_sla_breached.append(csat)
            else:
                satisfied_sla_met.append(csat)
                
    avg_met_csat = sum(satisfied_sla_met)/len(satisfied_sla_met) if satisfied_sla_met else 0
    avg_breached_csat = sum(satisfied_sla_breached)/len(satisfied_sla_breached) if satisfied_sla_breached else 0
    
    print(f"   - Tickets resolved WITHIN SLA achieved an average CSAT of {avg_met_csat:.2f}/5.0.")
    print(f"   - Tickets breaching SLA dropped to an average CSAT of {avg_breached_csat:.2f}/5.0 (Delta of {avg_met_csat - avg_breached_csat:.2f} points).")
    print("3. Business Analyst Action Plan:")
    print("   - Redesign standard operating procedures (SOPs) for 'Delivery Issue' processing.")
    print("   - Implement an automated escalation trigger in the CRM when a ticket hits 50% of its SLA timeline.")
    print("   - Conduct a time-motion audit of agents working on 'Delivery Issues' to re-allocate resource bandwidth.")
    print("=" * 70)

if __name__ == "__main__":
    simulate_and_analyze_tickets()
