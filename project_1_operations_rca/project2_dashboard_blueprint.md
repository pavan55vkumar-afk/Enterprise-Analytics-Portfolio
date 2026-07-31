# Business Intelligence Dashboard Blueprint: Support Operations & SLA Performance

This document serves as the UI/UX architecture and data modeling specification for building the **Support Operations SLA Dashboard** in **Power BI** or **Tableau** using the data generated from `tickets.csv`.

---

## 1. Dashboard Layout & Visual Wireframe
A clean grid layout optimized for executive decision-makers, split into three horizontal sections:

```
+---------------------------------------------------------------------------------------------------+
|  [Logo]  OPERATIONS PERFORMANCE & SLA MONITORING DASHBOARD                [Filters: Date | Category] |
+---------------------------------------------------------------------------------------------------+
|  [KPI Card 1]           [KPI Card 2]            [KPI Card 3]             [KPI Card 4]             |
|  Total Tickets          SLA Compliance %        Avg Handling Time (AHT)  Avg Customer CSAT        |
|  1,000 (Trend: +5%)     80.4% (Target: 90%)     34.2 Hours               3.8 / 5.0                |
+---------------------------------------------------------------------------------------------------+
|  [Visual A: Line Chart]                         | [Visual B: Bar Chart]                           |
|  Daily Ticket Volume & Resolution Trends        | Ticket Volume & SLA Status by Category          |
|  - X-Axis: Created Date                         | - Y-Axis: Category                              |
|  - Y-Axis: Count of Tickets                     | - X-Axis: Count of Tickets                      |
|  - Legend: Status (Open, Resolved, In Progress) | - Stacked Segments: Met SLA vs. Breached SLA    |
+---------------------------------------------------------------------------------------------------+
|  [Visual C: Scatter Plot]                       | [Visual D: Heatmap Table]                       |
|  Handling Time vs Customer Satisfaction (CSAT)  | Agent Performance Scorecard                     |
|  - X-Axis: Handling Time (Hours)                | - Columns: Agent ID, Volume, AHT, SLA %, CSAT   |
|  - Y-Axis: Satisfaction Rating (1-5)            | - Conditional Formatting:                       |
|  - Dot Density: Clusters representing breaches  |   - Red: SLA < 85% | Green: SLA >= 90%          |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Key DAX Measures (Power BI)
Implement these measures in your Power BI tabular model:

### Total Tickets
```dax
TotalTickets = COUNT(tickets[ticket_id])
```

### Resolved Tickets
```dax
ResolvedTickets = CALCULATE(
    COUNT(tickets[ticket_id]),
    tickets[status] IN {"Resolved", "Closed"}
)
```

### SLA Compliance Rate %
```dax
SLA_Compliance_Rate = 
DIVIDE(
    CALCULATE(COUNT(tickets[ticket_id]), tickets[is_breach] = 0, tickets[status] IN {"Resolved", "Closed"}),
    [ResolvedTickets],
    0
)
```

### Average Handling Time (Hours)
```dax
AvgHandlingTime = AVERAGE(tickets[handling_time_hours])
```

---

## 3. Key Calculated Fields (Tableau)

### SLA Status Category
Create a new dimension to categorize SLA performance:
```tableau
IF [is_breach] = 1 THEN "Breached SLA"
ELSEIF ISNULL([resolved_at]) THEN "SLA Active (Open)"
ELSE "Met SLA"
END
```

### SLA Compliance % (LOD Expression)
Calculate SLA compliance globally, ignoring localized filters if necessary, or adapting to dashboard filters:
```tableau
{ FIXED [category] : SUM(IF [is_breach] = 0 AND NOT ISNULL([resolved_at]) THEN 1 ELSE 0 END) } 
/ 
{ FIXED [category] : SUM(IF NOT ISNULL([resolved_at]) THEN 1 ELSE 0 END) }
```

---

## 4. Key Insights to Highlight
When demonstrating this dashboard to a hiring manager, focus on these interactive features:
*   **Drill-Down on "Delivery Issue":** Double-clicking the "Delivery Issue" bar highlights that 100% of these tickets breach their SLA because the average handling time of 80 hours is higher than the 72-hour target limit.
*   **Filter Interaction:** Selecting "High Priority" in the filter pane shows that although High Priority tickets are resolved 40% faster, the "Delivery Issue" category still breaches SLAs due to logistics bottlenecks.
*   **CSAT Breakdown:** Showing how the customer satisfaction rating drops by 1.5 stars as soon as the handling time crosses the SLA line.
