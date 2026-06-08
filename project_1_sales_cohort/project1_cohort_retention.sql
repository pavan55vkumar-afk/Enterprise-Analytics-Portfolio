-- ============================================================================
-- SQL Portfolio Project 1: Enterprise Sales & Customer Cohort Retention Analytics
-- Tool Suitability: PostgreSQL, MySQL (8.0+), Snowflake, BigQuery
-- Skills Demonstrated: Common Table Expressions (CTEs), Window Functions,
--                      Date Wrangling, Cohort Analysis, RFM Customer Segmentation.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TASK 1: Month-over-Month (MoM) Revenue Growth and Return Rate
-- Goal: Analyze e-commerce sales trends, volume, and refund rates MoM.
-- ----------------------------------------------------------------------------
WITH MonthlySales AS (
    SELECT 
        DATE_TRUNC('month', CAST(order_date AS TIMESTAMP)) AS sales_month,
        SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END) AS net_revenue,
        COUNT(CASE WHEN status = 'Completed' THEN order_id END) AS completed_orders,
        SUM(CASE WHEN status = 'Returned' THEN amount ELSE 0 END) AS returned_amount,
        COUNT(order_id) AS total_orders
    FROM orders
    GROUP BY 1
),
MonthlyGrowth AS (
    SELECT 
        sales_month,
        net_revenue,
        LAG(net_revenue, 1) OVER (ORDER BY sales_month) AS prev_month_revenue,
        completed_orders,
        returned_amount,
        total_orders,
        -- Calculate Return Rate as % of total revenue
        ROUND(CAST(returned_amount AS NUMERIC) / NULLIF(returned_amount + net_revenue, 0) * 100, 2) AS return_rate_pct
    FROM MonthlySales
)
SELECT 
    TO_CHAR(sales_month, 'YYYY-MM') AS month,
    net_revenue AS current_month_net_revenue,
    prev_month_revenue AS prior_month_net_revenue,
    -- MoM Growth Calculation
    ROUND(
        (net_revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0) * 100, 2
    ) AS mom_growth_pct,
    completed_orders,
    return_rate_pct
FROM MonthlyGrowth
ORDER BY sales_month;


-- ----------------------------------------------------------------------------
-- TASK 2: Customer Cohort Retention Analysis (MoM)
-- Goal: Group customers by their signup month (cohort) and track the percentage
--       of users returning to make purchases in subsequent months (Periods 0 to 5).
-- ----------------------------------------------------------------------------
WITH CustomerAcquisition AS (
    -- Define the Cohort Month for each customer based on their signup date
    SELECT 
        customer_id,
        DATE_TRUNC('month', CAST(signup_date AS DATE)) AS cohort_month
    FROM customers
),
CustomerActivity AS (
    -- Get all active purchase months for each customer
    SELECT DISTINCT
        o.customer_id,
        DATE_TRUNC('month', CAST(o.order_date AS TIMESTAMP)) AS activity_month
    FROM orders o
    WHERE o.status = 'Completed'
),
CohortPeriods AS (
    -- Calculate the month index (Period 0, 1, 2...) for each transaction
    SELECT 
        ca.cohort_month,
        act.activity_month,
        -- Calculate index: number of months since signup
        (EXTRACT(YEAR FROM act.activity_month) - EXTRACT(YEAR FROM ca.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM act.activity_month) - EXTRACT(MONTH FROM ca.cohort_month)) AS period_index,
        COUNT(DISTINCT ca.customer_id) AS active_customers
    FROM CustomerAcquisition ca
    JOIN CustomerActivity act ON ca.customer_id = act.customer_id
    GROUP BY 1, 2, 3
),
CohortSizes AS (
    -- Find the total number of customers in each starting cohort
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM CustomerAcquisition
    GROUP BY 1
)
SELECT 
    TO_CHAR(cs.cohort_month, 'YYYY-MM') AS cohort,
    cs.cohort_size,
    -- Period Retention Percentages
    ROUND(SUM(CASE WHEN cp.period_index = 0 THEN cp.active_customers ELSE 0 END) * 100.0 / cs.cohort_size, 1) AS period_0_pct,
    ROUND(SUM(CASE WHEN cp.period_index = 1 THEN cp.active_customers ELSE 0 END) * 100.0 / cs.cohort_size, 1) AS period_1_pct,
    ROUND(SUM(CASE WHEN cp.period_index = 2 THEN cp.active_customers ELSE 0 END) * 100.0 / cs.cohort_size, 1) AS period_2_pct,
    ROUND(SUM(CASE WHEN cp.period_index = 3 THEN cp.active_customers ELSE 0 END) * 100.0 / cs.cohort_size, 1) AS period_3_pct,
    ROUND(SUM(CASE WHEN cp.period_index = 4 THEN cp.active_customers ELSE 0 END) * 100.0 / cs.cohort_size, 1) AS period_4_pct,
    ROUND(SUM(CASE WHEN cp.period_index = 5 THEN cp.active_customers ELSE 0 END) * 100.0 / cs.cohort_size, 1) AS period_5_pct
FROM CohortSizes cs
LEFT JOIN CohortPeriods cp ON cs.cohort_month = cp.cohort_month
GROUP BY cs.cohort_month, cs.cohort_size
ORDER BY cs.cohort_month;


-- ----------------------------------------------------------------------------
-- TASK 3: RFM Customer Segmentation (Recency, Frequency, Monetary Value)
-- Goal: Use NTILE window functions to rank customers into percentiles for RFM,
--       then group them into actionable marketing segments.
-- ----------------------------------------------------------------------------
WITH RawRFM AS (
    SELECT 
        customer_id,
        -- Recency: Days since last order relative to a fixed extraction date (2026-06-01)
        EXTRACT(EPOCH FROM (CAST('2026-06-01 00:00:00' AS TIMESTAMP) - MAX(CAST(order_date AS TIMESTAMP)))) / 86400 AS recency_days,
        -- Frequency: Total completed orders
        COUNT(CASE WHEN status = 'Completed' THEN order_id END) AS frequency_count,
        -- Monetary: Total spend on completed orders
        SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END) AS monetary_value
    FROM orders
    GROUP BY customer_id
),
RFMScores AS (
    SELECT 
        customer_id,
        recency_days,
        frequency_count,
        monetary_value,
        -- Score 1 to 5 (5 is best, which means lower recency days)
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        -- Score 1 to 5 (5 is best, higher frequency)
        NTILE(5) OVER (ORDER BY frequency_count DESC) AS f_score,
        -- Score 1 to 5 (5 is best, higher spend)
        NTILE(5) OVER (ORDER BY monetary_value DESC) AS m_score
    FROM RawRFM
),
RFMConcatenated AS (
    SELECT 
        customer_id,
        recency_days,
        frequency_count,
        monetary_value,
        -- Convert ranks to score code e.g. '555' or '111'
        CAST(r_score AS CHAR) || CAST(f_score AS CHAR) || CAST(m_score AS CHAR) AS rfm_code,
        r_score,
        f_score,
        m_score
    FROM RFMScores
)
SELECT 
    customer_id,
    recency_days,
    frequency_count,
    monetary_value,
    rfm_code,
    CASE 
        WHEN rfm_code IN ('555', '554', '545', '455', '454', '445') THEN 'Champions (Loyal High-Spenders)'
        WHEN r_score >= 4 AND f_score >= 3 THEN 'Active Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Inactive / New Customers'
        WHEN r_score <= 2 AND f_score >= 4 THEN 'At Risk (High Value, Sleeping)'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost Customers / Churned'
        ELSE 'Regular Mid-Tier Customers'
    END AS customer_segment
FROM RFMConcatenated
ORDER BY monetary_value DESC
LIMIT 50;
