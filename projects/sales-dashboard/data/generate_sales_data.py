"""
Generates 2 years of sales data (2024 baseline, 2025 current) with per-unit
costs, for the Financial Performance & Sales Analytics Dashboard project.
Reuses the same Q3 West regional dip pattern as the ETL project so the
whole portfolio tells one consistent, verifiable data story.
"""
import csv
import random
from datetime import date, timedelta

random.seed(7)

regions = ["North", "South", "East", "West"]
# (product, unit_price, unit_cost)
products = [
    ("Wireless Mouse", 24.99, 11.20),
    ("Mechanical Keyboard", 89.99, 42.50),
    ("USB-C Hub", 34.50, 15.80),
    ("Monitor Stand", 45.00, 19.90),
    ("Webcam HD", 59.99, 27.30),
    ("Desk Lamp", 29.95, 13.40),
    ("Laptop Sleeve", 19.99, 7.60),
    ("Bluetooth Speaker", 74.99, 33.10),
    ("Noise Cancelling Headphones", 149.99, 68.00),
    ("Ergonomic Chair Cushion", 39.99, 17.20),
]

rows = []

def gen_year(year, west_dip=False):
    start = date(year, 1, 1)
    for day_offset in range(365):
        d = start + timedelta(days=day_offset)
        n_orders = random.randint(3, 8)
        # mild seasonal lift in Nov/Dec
        if d.month in (11, 12):
            n_orders += random.randint(1, 3)
        for _ in range(n_orders):
            region = random.choice(regions)
            product, price, cost = random.choice(products)
            qty = random.randint(1, 8)

            if west_dip and region == "West" and d.month in (7, 8, 9):
                if random.random() < 0.35:
                    continue

            revenue = round(price * qty, 2)
            total_cost = round(cost * qty, 2)
            profit = round(revenue - total_cost, 2)

            rows.append({
                "order_date": d.isoformat(),
                "year": year,
                "quarter": f"Q{(d.month-1)//3 + 1}",
                "region": region,
                "product": product,
                "unit_price": price,
                "quantity": qty,
                "revenue": revenue,
                "cost": total_cost,
                "profit": profit,
            })

gen_year(2024, west_dip=False)
gen_year(2025, west_dip=True)

with open("/home/claude/portfolio/projects/sales-dashboard/data/sales_2yr.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} rows across 2024-2025.")
