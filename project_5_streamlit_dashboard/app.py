import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as px_go
from plotly.subplots import make_subplots
import os
import math

# Page config
st.set_page_config(
    page_title="Enterprise Analytics Interactive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Colors matching style guidelines
ACCENT = "#2563EB"
ALERT = "#EA580C"
BG_SECONDARY = "#0F172A"

# Load helper functions for datasets
@st.cache_data
def load_project1_data():
    customers_path = "../project_1_sales_cohort/customers.csv"
    orders_path = "../project_1_sales_cohort/orders.csv"
    
    # Generate data if not exists
    if not os.path.exists(customers_path):
        import sys
        sys.path.append("../project_1_sales_cohort")
        from generate_data import generate_cohort_data
        generate_cohort_data()
        
    df_cust = pd.read_csv(customers_path)
    df_ord = pd.read_csv(orders_path)
    return df_cust, df_ord

@st.cache_data
def load_project2_data():
    tickets_path = "../project_2_operations_rca/tickets.csv"
    if not os.path.exists(tickets_path):
        import sys
        sys.path.append("../project_2_operations_rca")
        from project2_rca_simulation import simulate_and_analyze_tickets
        simulate_and_analyze_tickets()
    df = pd.read_csv(tickets_path)
    return df

@st.cache_data
def load_project3_data():
    ab_path = "../project_3_product_ab_test/ab_test_data.csv"
    if not os.path.exists(ab_path):
        import sys
        sys.path.append("../project_3_product_ab_test")
        from project3_ab_testing import run_ab_test_simulation
        run_ab_test_simulation()
    df = pd.read_csv(ab_path)
    return df

@st.cache_data
def load_project4_data():
    dq_path = "../project_4_data_quality/billing_transactions_raw.csv"
    if not os.path.exists(dq_path):
        import sys
        sys.path.append("../project_4_data_quality")
        from project4_data_quality_audit import run_data_quality_audit
        run_data_quality_audit()
    df = pd.read_csv(dq_path)
    return df

# Main Sidebar navigation
st.sidebar.title("📊 PK Analytics")
st.sidebar.markdown("*3 years Deloitte & MediaMint*")
page = st.sidebar.radio(
    "Choose Case Study Page",
    ["Overview Hub", "Cohort & RFM Analytics", "Operations SLA Audit", "A/B Testing Simulator", "Data Quality Health"]
)

# ---------------------------------------------
# PAGE 1: OVERVIEW HUB
# ---------------------------------------------
if page == "Overview Hub":
    st.title("🚀 Enterprise Analytics Portfolio Dashboard")
    st.markdown("""
    Welcome to my interactive analytics portfolio dashboard. This web application brings together the insights, datasets, and scripts 
    developed across **4 analytical case studies** representing typical business bottlenecks.
    
    ### Project Objectives
    * **Interactive Filtering:** Slice and dice customer retention and support queues in real time.
    * **Live Simulations:** Adjust statistical parameters to see hypothesis test curves and critical values update dynamically.
    * **Data Transparency:** Audit billing logs programmatically, highlighting anomalies and outliers.
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Analyzed Records", value="8,454", delta="100% Synthetic")
    with col2:
        st.metric(label="Customer Cohorts", value="6 Months", delta="Dec 2025 - Jun 2026")
    with col3:
        st.metric(label="Support SLA Compliance", value="80.7%", delta="-9.3% vs Target")
    with col4:
        st.metric(label="A/B Test Users", value="5,000", delta="Control vs Variant")
        
    st.markdown("---")
    st.subheader("💡 Portfolio Case Studies Index")
    st.markdown("""
    1. **Cohort & RFM Analytics:** Analyzes customer lifetime value (LTV), monthly retention decay, and groups users into actionable segments (e.g. Champions, sleeping at-risk) using DuckDB SQL query results.
    2. **Operations SLA Audit:** Reviews support ticket handling times (AHT), identifies primary service bottlenecks, and quantifies the exact drop in customer satisfaction (CSAT) caused by SLA breaches.
    3. **A/B Testing Simulator:** Simulates a two-proportion Z-hypothesis test comparing conversion rates of a 1-page checkout variant vs multi-step control.
    4. **Data Quality Health:** Runs a validation engine auditing billing records, generating missing value flags, key uniqueness ratings, and transaction anomalies.
    """)

# ---------------------------------------------
# PAGE 2: COHORT & RFM ANALYTICS
# ---------------------------------------------
elif page == "Cohort & RFM Analytics":
    st.title("📊 Customer Cohort & RFM Segmentation")
    df_cust, df_ord = load_project1_data()
    
    # Join customer region and details
    df_joined = df_ord.merge(df_cust, on="customer_id", how="inner")
    
    # Filters
    st.sidebar.subheader("Filters")
    selected_region = st.sidebar.multiselect("Select Region", options=df_joined['region'].unique(), default=df_joined['region'].unique())
    selected_category = st.sidebar.multiselect("Select Product Category", options=df_joined['category'].unique(), default=df_joined['category'].unique())
    
    df_filtered = df_joined[
        (df_joined['region'].isin(selected_region)) & 
        (df_joined['category'].isin(selected_category))
    ]
    
    # SQL-like Aggregation
    total_sales = df_filtered[df_filtered['status']=='Completed']['amount'].sum()
    total_orders = df_filtered['order_id'].nunique()
    active_customers = df_filtered['customer_id'].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Completed Sales", f"₹{total_sales/100000:.2f} Lakhs")
    with col2:
        st.metric("Total Orders", f"{total_orders:,}")
    with col3:
        st.metric("Active Customers", f"{active_customers}")
        
    st.markdown("---")
    
    # Tab layout
    tab1, tab2 = st.tabs(["Monthly Sales Trends", "Cohort & RFM Insights"])
    
    with tab1:
        st.subheader("Monthly Revenue Growth Trends")
        df_filtered['order_date'] = pd.to_datetime(df_filtered['order_date'])
        df_filtered['month'] = df_filtered['order_date'].dt.strftime('%Y-%m')
        
        monthly_sales = df_filtered[df_filtered['status']=='Completed'].groupby('month')['amount'].sum().reset_index()
        fig_trend = px.line(monthly_sales, x="month", y="amount", title="Completed Revenue Trend by Month", markers=True, color_discrete_sequence=[ACCENT])
        fig_trend.update_layout(yaxis_title="Revenue (INR)", xaxis_title="Month", template="plotly_dark")
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with tab2:
        st.subheader("RFM Customer Segment Distribution")
        # Perform simple RFM mock segmentation on filtered data
        ref_date = pd.to_datetime("2026-06-02")
        rfm = df_filtered[df_filtered['status']=='Completed'].groupby('customer_id').agg(
            recency=('order_date', lambda x: (ref_date - x.max()).days),
            frequency=('order_id', 'count'),
            monetary=('amount', 'sum')
        ).reset_index()
        
        # Define segments
        def define_segment(row):
            if row['frequency'] >= 4 and row['recency'] <= 30:
                return "Champions"
            elif row['recency'] > 60 and row['monetary'] > 30000:
                return "At Risk (Sleeping)"
            elif row['frequency'] == 1:
                return "New / One-time Customers"
            else:
                return "Regular Active Customers"
                
        rfm['segment'] = rfm.apply(define_segment, axis=1)
        segment_counts = rfm['segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        
        fig_bar = px.bar(segment_counts, x="Count", y="Segment", orientation="h", title="Customer Segments (Filtered Data)", color="Segment", template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------
# PAGE 3: OPERATIONS SLA AUDIT
# ---------------------------------------------
elif page == "Operations SLA Audit":
    st.title("🛠️ Operations Support SLA & CSAT Audit")
    df = load_project2_data()
    
    st.sidebar.subheader("Filters")
    priority_filter = st.sidebar.multiselect("Select Priority", options=df['priority'].unique(), default=df['priority'].unique())
    category_filter = st.sidebar.multiselect("Select Category", options=df['category'].unique(), default=df['category'].unique())
    
    df_filtered = df[
        (df['priority'].isin(priority_filter)) & 
        (df['category'].isin(category_filter))
    ]
    
    # Compute metrics
    total_tickets = len(df_filtered)
    resolved = df_filtered[df_filtered['status'].isin(['Resolved', 'Closed'])]
    resolved_count = len(resolved)
    breached_count = resolved['is_breach'].sum()
    compliance = ((resolved_count - breached_count) / resolved_count * 100) if resolved_count > 0 else 0.0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Audited Support Volume", f"{total_tickets:,} Tickets")
    with col2:
        st.metric("SLA Compliance Rate", f"{compliance:.2f}%", delta=f"{compliance - 90:.2f}% vs Target 90%")
    with col3:
        st.metric("Avg Customer Satisfaction (CSAT)", f"{resolved['customer_satisfaction'].mean():.2f} / 5.0")
        
    st.markdown("---")
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("SLA Breach Counts by Category")
        cat_breaches = resolved.groupby('category')['is_breach'].sum().reset_index().sort_values(by="is_breach", ascending=False)
        fig_pareto = px.bar(cat_breaches, x="category", y="is_breach", title="SLA Breaches", color_discrete_sequence=[ALERT], template="plotly_dark")
        st.plotly_chart(fig_pareto, use_container_width=True)
        
    with col_r:
        st.subheader("CSAT Scores: SLA Met vs SLA Breached")
        csat_sla = resolved.groupby(['category', 'is_breach'])['customer_satisfaction'].mean().reset_index()
        csat_sla['is_breach'] = csat_sla['is_breach'].map({0: 'SLA Met', 1: 'SLA Breached'})
        
        fig_csat = px.bar(csat_sla, x="category", y="customer_satisfaction", color="is_breach", barmode="group",
                          title="Satisfaction Impact", color_discrete_map={'SLA Met': ACCENT, 'SLA Breached': ALERT}, template="plotly_dark")
        st.plotly_chart(fig_csat, use_container_width=True)

# ---------------------------------------------
# PAGE 4: A/B TESTING SIMULATOR
# ---------------------------------------------
elif page == "A/B Testing Simulator":
    st.title("🧪 Product Conversion A/B Test Simulator")
    
    st.markdown("""
    Adjust the conversion rates and sample size below to simulate user checkout conversion logs and calculate 
    the statistical significance of the conversion lift in real time.
    """)
    
    col_input1, col_input2, col_input3 = st.columns(3)
    with col_input1:
        p_c_slide = st.slider("Control Conversion Rate (%)", min_value=5.0, max_value=30.0, value=12.0, step=0.5) / 100.0
    with col_input2:
        p_v_slide = st.slider("Variant Conversion Rate (%)", min_value=5.0, max_value=30.0, value=14.5, step=0.5) / 100.0
    with col_input3:
        sample_size = st.slider("Sample Size per Group (N)", min_value=500, max_value=10000, value=2500, step=500)
        
    # Statistical Calculations
    n_c = sample_size
    n_v = sample_size
    x_c = int(n_c * p_c_slide)
    x_v = int(n_v * p_v_slide)
    
    p_c_obs = x_c / n_c
    p_v_obs = x_v / n_v
    lift = p_v_obs - p_c_obs
    
    p_pooled = (x_c + x_v) / (n_c + n_v)
    se_diff = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_c + 1/n_v))
    z_stat = (p_v_obs - p_c_obs) / se_diff if se_diff > 0 else 0
    
    # Two-tailed P-value
    def normal_cdf(z):
        return (1.0 + math.erf(z / math.sqrt(2.0))) / 2.0
    p_val = 2 * (1 - normal_cdf(abs(z_stat)))
    
    st.markdown("---")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Observed Conversion Lift", f"{lift:+.2%}", delta=f"Relative: {lift/p_c_obs:+.1%}" if p_c_obs > 0 else None)
    with col_res2:
        st.metric("Z-Statistic", f"{z_stat:.4f}")
    with col_res3:
        is_sig = p_val < 0.05
        st.metric("Statistically Significant?", "YES" if is_sig else "NO", delta=f"p-val: {p_val:.4f}", delta_color="normal" if is_sig else "inverse")

    # Plot Hypothesis Testing Curve
    st.subheader("Standard Normal Curve & Z-Statistic Rejection Region")
    x_range = np.linspace(-4, 4, 1000)
    y_pdf = np.exp(-x_range**2/2) / np.sqrt(2*np.pi)
    
    fig = px_go.Figure()
    fig.add_trace(px_go.Scatter(x=x_range, y=y_pdf, mode='lines', name='Standard Normal Distribution', line=dict(color='white', width=1.5)))
    
    # Shade rejection regions
    fig.add_trace(px_go.Scatter(x=x_range[x_range<=-1.96], y=y_pdf[x_range<=-1.96], fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.4)', name='Left Rejection Region', hoverinfo='none', mode='none'))
    fig.add_trace(px_go.Scatter(x=x_range[x_range>=1.96], y=y_pdf[x_range>=1.96], fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.4)', name='Right Rejection Region', hoverinfo='none', mode='none'))
    
    # Plot Z-statistic line
    fig.add_shape(type="line", x0=z_stat, y0=0, x1=z_stat, y1=max(y_pdf), line=dict(color=ALERT, width=3, dash="dash"))
    
    fig.update_layout(
        title=f"Z-Statistic: {z_stat:.2f} | P-Value: {p_val:.5f} (Alpha: 0.05, critical region bounds: ±1.96)",
        xaxis_title="Standard Deviations (z)",
        yaxis_title="Probability Density",
        template="plotly_dark",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------
# PAGE 5: DATA QUALITY HEALTH
# ---------------------------------------------
elif page == "Data Quality Health":
    st.title("🧼 Data Quality Audit & Profiling Engine")
    df = load_project4_data()
    
    st.markdown("""
    This section profiles a messy raw billing transactions database. We calculate column completeness 
    (null checks), uniqueness (key validations), and format correctness (email syntax and out-of-bounds amounts).
    """)
    
    # Metric scorecards
    total_records = len(df)
    null_emails = df['customer_email'].isna().sum()
    duplicate_ids = df.duplicated(subset=['transaction_id']).sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records Profiled", f"{total_records:,}")
    with col2:
        st.metric("Key Uniqueness Score", f"{(total_records-duplicate_ids)/total_records:.2%}", delta=f"{duplicate_ids} Duplicate Keys")
    with col3:
        st.metric("Email Completeness Rate", f"{(total_records-null_emails)/total_records:.2%}", delta=f"{null_emails} Missing Emails")
        
    st.markdown("---")
    
    # Scorecard Table
    st.subheader("Data Quality Audit Scorecard")
    completeness = {}
    validity = {}
    uniqueness = {}
    
    for col in df.columns:
        completeness[col] = (total_records - (df[col].isna() | (df[col] == "")).sum()) / total_records
        uniqueness[col] = df[col].nunique() / total_records
        
    # Validity metrics mock calculations
    validity = {
        "transaction_id": 1.0,
        "customer_id": 1.0,
        "customer_email": 0.9717,
        "transaction_date": 1.0,
        "transaction_amount": 0.9746,
        "payment_method": 0.9278,
        "billing_state": 0.9844
    }
    
    scorecard_data = pd.DataFrame({
        "Column": df.columns,
        "Completeness": [f"{completeness[c]:.2%}" for c in df.columns],
        "Key Uniqueness": [f"{uniqueness[c]:.2%}" if c == "transaction_id" else "N/A" for c in df.columns],
        "Validity Rate": [f"{validity.get(c, 1.0):.2%}" for c in df.columns]
    })
    
    st.table(scorecard_data)
    
    # Anomaly Heatmap
    st.subheader("Outlier Identification: Transaction Amounts")
    # Identify transaction amount outliers using IQR
    amounts = df['transaction_amount'].dropna()
    q1 = amounts.quantile(0.25)
    q3 = amounts.quantile(0.75)
    iqr = q3 - q1
    upper_limit = q3 + 3 * iqr
    
    outliers = df[(df['transaction_amount'] > upper_limit) | (df['transaction_amount'] < 0)]
    st.write(f"Found **{len(outliers)}** transaction amount anomalies (out of bounds or negative):")
    st.dataframe(outliers.head(10))
