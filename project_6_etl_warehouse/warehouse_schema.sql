-- Star Schema Data Warehouse Schema Definition

-- 1. Dimension: Customers (dim_customers)
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_key INTEGER PRIMARY KEY,
    customer_id INTEGER UNIQUE,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    region VARCHAR(50),
    signup_date DATE,
    is_active INTEGER,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Dimension: Products (dim_products)
CREATE TABLE IF NOT EXISTS dim_products (
    product_key INTEGER PRIMARY KEY,
    product_name VARCHAR(100) UNIQUE,
    category VARCHAR(50),
    unit_price_inr DECIMAL(10,2),
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Dimension: Date (dim_date)
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    calendar_date DATE UNIQUE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend INTEGER
);

-- 4. Fact: Sales Transactions (fact_sales)
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key INTEGER PRIMARY KEY,
    order_id INTEGER,
    customer_key INTEGER,
    product_key INTEGER,
    date_key INTEGER,
    quantity INTEGER,
    gross_amount DECIMAL(12,2),
    returned_amount DECIMAL(12,2),
    net_amount DECIMAL(12,2),
    order_status VARCHAR(20),
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_key) REFERENCES dim_customers(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_products(product_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);
