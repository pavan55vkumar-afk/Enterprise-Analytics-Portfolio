# Portfolio Interview Guide

## How to Introduce the Portfolio

> I built three analytics case studies around customer retention, operational
> performance, and product experimentation. I selected these areas because they
> demonstrate the full analyst workflow: defining a business problem, validating
> data, selecting KPIs, performing analysis, interpreting results, and presenting
> a recommendation to stakeholders. The data is synthetic, but I designed the
> problems and deliverables to reflect realistic business decisions.

Do not say that a recommendation saved money or improved performance unless it
was actually implemented and measured. In these projects, distinguish between
an **observed analytical result** and an **expected business impact**.

## Project 1: Customer Revenue, Retention, and RFM Analysis

### 60-Second Explanation

> The business needed to understand revenue movement, repeat purchasing, and
> which customers should receive retention attention. I worked with customer and
> order-level data containing 500 customers and 929 orders. I first validated
> customer keys, dates, order status, and transaction amounts. I then used SQL
> CTEs and window functions to calculate monthly revenue growth, return rate,
> cohort retention, and RFM scores. The data contained INR 5.37 million in
> completed-order revenue. Of 395 purchasing customers, 249 made repeat
> purchases. The solution segments customers into groups such as champions,
> active loyal customers, at-risk customers, and lost customers. My recommendation
> was to use cohort trends to identify when engagement falls and run targeted
> campaigns for high-value customers whose activity is declining.

### Problem

Aggregate revenue alone does not show whether growth is coming from new
customers, repeat customers, or a small group of high-value buyers.

### Solution Delivered

- Monthly revenue and month-over-month growth analysis
- Return-rate monitoring
- Customer acquisition cohort and retention matrix
- RFM segmentation using recency, frequency, and monetary value
- Actionable customer groups for retention and reactivation

### Outcome

The analysis produced a reusable decision framework for customer lifecycle
management. It identified the size of the active and repeat customer base and
made it possible to prioritize retention activity by customer value and
engagement.

### Likely Follow-Up Questions

**Why use cohort analysis?**  
Cohorts separate customers by acquisition period, allowing retention behavior
to be compared fairly instead of mixing mature and newly acquired customers.

**Why use RFM?**  
RFM is interpretable for business stakeholders and converts transaction history
into practical groups for retention, loyalty, and reactivation actions.

**What would you improve with real data?**  
I would include acquisition channel, discount usage, gross margin, customer
service interactions, and campaign response. I would also validate whether RFM
segments predict future purchases.

## Project 2: Operational SLA Bottleneck Analysis

### 60-Second Explanation

> The operations team had an overall SLA problem but needed to know where the
> failure was concentrated and what action to take. I analyzed 1,000 tickets
> using volume, resolution status, handling time, SLA compliance, priority, and
> CSAT. Overall SLA compliance was 80.67%. Delivery Issues were the primary
> bottleneck, with a 40.7% breach rate and average handling time of 71.33 hours
> against a 72-hour target. I also found that average CSAT dropped from 3.98 for
> tickets completed within SLA to 1.44 for breached tickets. I proposed a
> milestone-based escalation at 50% of the SLA window, workflow redesign for
> Delivery Issues, and a category-level dashboard so leadership could intervene
> before tickets breached.

### Problem

The overall SLA percentage showed underperformance but did not identify the
category, process stage, or customer impact driving the result.

### Solution Delivered

- Defined operational KPIs: volume, resolution rate, SLA compliance, AHT, and
  CSAT
- Compared performance by category and priority
- Identified the highest-breach workflow
- Quantified the relationship between SLA breaches and customer satisfaction
- Designed a Power BI/Tableau dashboard and escalation approach

### Outcome

The analysis narrowed a broad performance issue to a specific workflow and gave
leadership a prioritized action plan. The proposed dashboard would support
earlier intervention and ongoing control monitoring.

### Likely Follow-Up Questions

**How did you identify the root cause?**  
I compared ticket volume, average handling time, SLA target, breach rate, and
CSAT by category. Delivery Issues combined high volume with handling time above
the target and the highest breach rate.

**Does this prove SLA breach causes low CSAT?**  
No. It demonstrates a strong association in this dataset. A causal conclusion
would require controlling for category, complexity, priority, and other factors.

**What would you monitor after implementation?**  
SLA compliance, tickets reaching 50% and 75% of SLA, aging backlog, reopen rate,
CSAT, and Delivery Issue handling time. I would compare pre- and post-change
periods.

## Project 3: Product Conversion A/B Test

### 60-Second Explanation

> The product team wanted to know whether a new checkout experience should be
> rolled out. I analyzed a simulated experiment with 5,000 users split between
> control and variant groups. I calculated conversion rates, absolute and
> relative lift, a two-proportion z-test, and statistical significance. Control
> converted at 11.74%, while the variant converted at 14.13%, a 2.39
> percentage-point absolute lift and 20.35% relative improvement. The p-value was
> 0.01188, so the difference was unlikely to be random at the 5% significance
> level. I recommended a controlled rollout rather than an immediate full
> release, with device-level monitoring and revenue-per-visitor guardrails.

### Problem

The team needed evidence that the observed conversion increase was meaningful,
not normal sampling variation.

### Solution Delivered

- Defined control, variant, primary KPI, and null hypothesis
- Calculated conversion rate and lift
- Performed a two-proportion z-test
- Interpreted the p-value for a business audience
- Added revenue and device dimensions for follow-up analysis

### Outcome

The experiment provided statistically supported evidence in favor of the
variant and a structured rollout recommendation with monitoring controls.

### Likely Follow-Up Questions

**Why not roll out immediately to 100%?**  
Statistical significance is not the only consideration. I would confirm data
quality, experiment duration, device consistency, revenue per visitor, technical
performance, and guardrail metrics before full rollout.

**What does the p-value mean?**  
Assuming there is no true conversion difference, the probability of observing a
difference at least this extreme is approximately 0.23%.

**What are the experiment limitations?**  
The data is simulated, the analysis does not test novelty or seasonality, and
the current design needs explicit guardrail metrics and sample-size planning.

## Closing Answer: What Did You Personally Do?

> I designed the business questions, selected the KPIs, structured the datasets,
> developed and validated the SQL/Python analysis, interpreted the findings, and
> translated them into stakeholder recommendations. I used AI tools to accelerate
> implementation and review, but I owned the analytical logic, validation, and
> business decisions.
