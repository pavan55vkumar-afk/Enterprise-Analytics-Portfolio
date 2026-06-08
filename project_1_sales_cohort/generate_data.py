import csv
import random
import os
from datetime import datetime, timedelta

def generate_cohort_data():
    random.seed(42)
    print("Generating synthetic e-commerce data for Project 1...")
    
    # Target dates: past 6 months
    end_date = datetime(2026, 6, 1)
    start_date = datetime(2025, 12, 1)
    
    # 1. Generate Customers
    num_customers = 500
    customers = []
    
    # Domains for realistic emails
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    first_names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohan", "Neha", "Arjun", "Kajal", "Sandeep", "Deepa", "Vijay", "Swati", "Rajesh", "Pooja"]
    last_names = ["Sharma", "Verma", "Sen", "Nair", "Patel", "Reddy", "Rao", "Joshi", "Gupta", "Kumar", "Singh", "Das", "Mehta", "Iyer", "Choudhury"]

    for customer_id in range(1, num_customers + 1):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@{random.choice(domains)}"
        
        # Acquisition date (when they first signed up)
        signup_days = random.randint(0, 180)
        signup_date = start_date + timedelta(days=signup_days)
        
        customers.append({
            "customer_id": customer_id,
            "name": f"{fn} {ln}",
            "email": email,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
            "region": random.choice(["North", "South", "East", "West"])
        })
        
    # Write Customers to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    customers_path = os.path.join(script_dir, "customers.csv")
    with open(customers_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id", "name", "email", "signup_date", "region"])
        writer.writeheader()
        writer.writerows(customers)
    print(f"- Saved {customers_path} (500 records)")

    # 2. Generate Orders
    orders = []
    order_id = 10001
    
    # Products catalog
    products = [
        {"name": "Wireless Mouse", "category": "Electronics", "price": 1200},
        {"name": "Mechanical Keyboard", "category": "Electronics", "price": 4500},
        {"name": "Noise Cancelling Headphones", "category": "Electronics", "price": 8500},
        {"name": "Ergonomic Office Chair", "category": "Furniture", "price": 12500},
        {"name": "LED Desk Lamp", "category": "Furniture", "price": 2200},
        {"name": "Water Bottle 1L", "category": "Fitness", "price": 800},
        {"name": "Yoga Mat", "category": "Fitness", "price": 1500},
        {"name": "Resistance Bands Set", "category": "Fitness", "price": 950},
        {"name": "Leather Notebook", "category": "Stationery", "price": 600},
        {"name": "Gel Pen Pack of 10", "category": "Stationery", "price": 250}
    ]

    for cust in customers:
        signup_dt = datetime.strptime(cust["signup_date"], "%Y-%m-%d")
        
        # Determine if they make orders
        # 80% make at least 1 order (the acquisition order)
        if random.random() < 0.8:
            # First order usually happens on signup date or shortly after (within 3 days)
            first_order_date = signup_dt + timedelta(days=random.randint(0, 3))
            prod = random.choice(products)
            qty = random.randint(1, 2)
            orders.append({
                "order_id": order_id,
                "customer_id": cust["customer_id"],
                "order_date": first_order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "product_name": prod["name"],
                "category": prod["category"],
                "amount": prod["price"] * qty,
                "status": "Completed" if random.random() < 0.95 else "Returned"
            })
            order_id += 1
            
            # Repeat orders: generate subsequent orders over the next months
            # Higher chance of repeat orders if they signed up early
            num_repeat = random.randint(0, 5)
            curr_order_date = first_order_date
            for _ in range(num_repeat):
                # Next order happens 10 to 60 days later
                gap = random.randint(10, 60)
                curr_order_date = curr_order_date + timedelta(days=gap)
                if curr_order_date > end_date:
                    break
                
                prod = random.choice(products)
                qty = random.randint(1, 3)
                orders.append({
                    "order_id": order_id,
                    "customer_id": cust["customer_id"],
                    "order_date": curr_order_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "product_name": prod["name"],
                    "category": prod["category"],
                    "amount": prod["price"] * qty,
                    "status": "Completed" if random.random() < 0.95 else "Returned"
                })
                order_id += 1

    # Write Orders to CSV
    orders_path = os.path.join(script_dir, "orders.csv")
    with open(orders_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "order_date", "product_name", "category", "amount", "status"])
        writer.writeheader()
        writer.writerows(orders)
    print(f"- Saved {orders_path} ({len(orders)} records)")
    print("E-commerce sales cohort data generation complete!\n")

if __name__ == "__main__":
    generate_cohort_data()
