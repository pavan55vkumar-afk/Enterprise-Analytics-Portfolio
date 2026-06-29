import os
import sqlite3
import pandas as pd
import numpy as np
import duckdb
from datetime import datetime, timedelta

def build_etl_pipeline():
    print("Starting ETL pipeline process...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "../project_1_sales_cohort")
    warehouse_db_path = os.path.join(script_dir, "analytics_warehouse.db")
    
    # Check source files
    cust_path = os.path.join(source_dir, "customers.csv")
    ord_path = os.path.join(source_dir, "orders.csv")
    
    if not os.path.exists(cust_path) or not os.path.exists(ord_path):
        print("Source files not found. Creating synthetic data first...")
        import sys
        sys.path.append(source_dir)
        from generate_data import generate_cohort_data
        generate_cohort_data()
        
    # 1. EXTRACT
    print("- Extracting source files...")
    df_cust = pd.read_csv(cust_path)
    df_ord = pd.read_csv(ord_path)
    
    # 2. TRANSFORM
    print("- Transforming data...")
    
    # --- Clean Customers ---
    df_cust['customer_name'] = df_cust['name'].str.strip().str.title()
    df_cust['customer_email'] = df_cust['email'].str.strip().str.lower()
    df_cust['region'] = df_cust['region'].str.strip().str.upper()
    df_cust['signup_date'] = pd.to_datetime(df_cust['signup_date'])
    df_cust = df_cust.drop(columns=['name', 'email'])
    
    # Generate surrogate key for dim_customers
    df_cust = df_cust.sort_values(by="customer_id").reset_index(drop=True)
    df_cust['customer_key'] = df_cust.index + 1000
    df_cust['is_active'] = 1
    
    # --- Clean Products & Build Dimension ---
    # Retrieve unique product catalog from orders
    df_ord['product_name'] = df_ord['product_name'].str.strip()
    df_ord['category'] = df_ord['category'].str.strip()
    
    # Estimate unit price (amount / qty)
    df_ord['order_date'] = pd.to_datetime(df_ord['order_date'])
    # In synthetic data, pricing is stable. Take maximum price as unit price.
    product_prices = df_ord.groupby('product_name').apply(
        lambda x: round(x['amount'].max() / 2.0) if 'Resistance' in x.name else round(x['amount'].max())
    ).reset_index()
    product_prices.columns = ['product_name', 'unit_price_inr']
    
    # Add categories
    prod_cat = df_ord[['product_name', 'category']].drop_duplicates().reset_index(drop=True)
    df_prod = prod_cat.merge(product_prices, on='product_name', how='inner')
    df_prod = df_prod.sort_values(by="product_name").reset_index(drop=True)
    df_prod['product_key'] = df_prod.index + 5000
    
    # --- Build Date Dimension ---
    min_date = df_ord['order_date'].min()
    max_date = df_ord['order_date'].max()
    date_range = pd.date_range(start=min_date.floor('D') - pd.Timedelta(days=5), end=max_date.ceil('D') + pd.Timedelta(days=5))
    
    dim_date_records = []
    for d in date_range:
        dim_date_records.append({
            "date_key": int(d.strftime("%Y%m%d")),
            "calendar_date": d.strftime("%Y-%m-%d"),
            "year": d.year,
            "quarter": (d.month - 1) // 3 + 1,
            "month": d.month,
            "month_name": d.strftime("%B"),
            "day_of_month": d.day,
            "day_of_week": d.dayofweek + 1,
            "day_name": d.strftime("%A"),
            "is_weekend": 1 if d.dayofweek >= 5 else 0
        })
    df_date = pd.DataFrame(dim_date_records)
    
    # --- Build Fact Table ---
    df_ord['date_key'] = df_ord['order_date'].dt.strftime("%Y%m%d").astype(int)
    
    # Map surrogate keys
    df_fact = df_ord.merge(df_cust[['customer_id', 'customer_key']], on='customer_id', how='left')
    df_fact = df_fact.merge(df_prod[['product_name', 'product_key', 'unit_price_inr']], on='product_name', how='left')
    
    # In order generation, quantity is 1 or 2. We calculate quantity as round(amount / price)
    df_fact['quantity'] = (df_fact['amount'] / df_fact['unit_price_inr']).round().astype(int)
    
    # Calculate facts
    df_fact['gross_amount'] = df_fact['amount']
    df_fact['returned_amount'] = np.where(df_fact['status'] == 'Returned', df_fact['amount'], 0.0)
    df_fact['net_amount'] = df_fact['gross_amount'] - df_fact['returned_amount']
    df_fact['order_status'] = df_fact['status']
    
    # Select target columns for fact_sales
    df_fact = df_fact.sort_values(by="order_id").reset_index(drop=True)
    df_fact['sales_key'] = df_fact.index + 80000
    
    df_fact_sales = df_fact[[
        'sales_key', 'order_id', 'customer_key', 'product_key', 
        'date_key', 'quantity', 'gross_amount', 'returned_amount', 
        'net_amount', 'order_status'
    ]]
    
    # 3. LOAD
    print(f"- Loading tables into analytics warehouse: {warehouse_db_path}...")
    
    # Setup schema
    con = duckdb.connect(database=warehouse_db_path)
    
    # Read and execute schema definition SQL
    schema_sql_path = os.path.join(script_dir, "warehouse_schema.sql")
    with open(schema_sql_path, "r") as f:
        schema_sql = f.read()
    
    # Split queries and run
    for stmt in schema_sql.split(";"):
        if stmt.strip():
            con.execute(stmt)
            
    # Load DataFrames into DB
    con.execute("DELETE FROM fact_sales")
    con.execute("DELETE FROM dim_customers")
    con.execute("DELETE FROM dim_products")
    con.execute("DELETE FROM dim_date")
    
    con.execute("INSERT INTO dim_customers SELECT customer_key, customer_id, customer_name, customer_email, region, signup_date, is_active, CURRENT_TIMESTAMP FROM df_cust")
    con.execute("INSERT INTO dim_products SELECT product_key, product_name, category, unit_price_inr, CURRENT_TIMESTAMP FROM df_prod")
    con.execute("INSERT INTO dim_date SELECT date_key, calendar_date, year, quarter, month, month_name, day_of_month, day_of_week, day_name, is_weekend FROM df_date")
    con.execute("INSERT INTO fact_sales SELECT sales_key, order_id, customer_key, product_key, date_key, quantity, gross_amount, returned_amount, net_amount, order_status, CURRENT_TIMESTAMP FROM df_fact_sales")
    
    # 4. VERIFY / TEST RUN
    print("\n- Verification queries:")
    
    # Check count matching
    count_fact = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    count_cust = con.execute("SELECT COUNT(*) FROM dim_customers").fetchone()[0]
    count_prod = con.execute("SELECT COUNT(*) FROM dim_products").fetchone()[0]
    
    print(f"  * Fact Sales Count: {count_fact} (expected {len(df_fact_sales)})")
    print(f"  * Dim Customers Count: {count_cust} (expected {len(df_cust)})")
    print(f"  * Dim Products Count: {count_prod} (expected {len(df_prod)})")
    
    # Check integrity: no nulls in keys in fact table
    null_keys = con.execute("SELECT COUNT(*) FROM fact_sales WHERE customer_key IS NULL OR product_key IS NULL OR date_key IS NULL").fetchone()[0]
    print(f"  * Referential Integrity Violations: {null_keys} (expected 0)")
    assert null_keys == 0, "Referential integrity broken during ETL mapping!"
    
    # Sample Star Join Query
    print("\nExecuting Sample Star Query (Net Sales by Region & Product Category):")
    join_query = """
        SELECT 
            c.region,
            p.category,
            SUM(f.net_amount) AS net_sales_inr,
            SUM(f.quantity) AS units_sold
        FROM fact_sales f
        JOIN dim_customers c ON f.customer_key = c.customer_key
        JOIN dim_products p ON f.product_key = p.product_key
        WHERE f.order_status = 'Completed'
        GROUP BY c.region, p.category
        ORDER BY net_sales_inr DESC
        LIMIT 5;
    """
    res_df = con.execute(join_query).df()
    print(res_df.to_string(index=False))
    
    con.close()
    print("\nSUCCESS: ETL process completed. Data warehouse loaded successfully.")

if __name__ == "__main__":
    build_etl_pipeline()
