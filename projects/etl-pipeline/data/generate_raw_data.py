"""
Generates messy, realistic raw sales data for the ETL pipeline portfolio project.
Deliberately injects the kinds of problems a real ETL pipeline has to solve:
duplicates, inconsistent formatting, missing values, and mixed date formats.
Also engineers a genuine Q3 dip in the West region so the downstream
insight is backed by real (synthetic) data, not invented.
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

regions = ["North", "South", "East", "West"]
products = [
    ("Wireless Mouse", 24.99), ("Mechanical Keyboard", 89.99),
    ("USB-C Hub", 34.50), ("Monitor Stand", 45.00),
    ("Webcam HD", 59.99), ("Desk Lamp", 29.95),
    ("Laptop Sleeve", 19.99), ("Bluetooth Speaker", 74.99),
    ("Noise Cancelling Headphones", 149.99), ("Ergonomic Chair Cushion", 39.99),
]
reps = ["J. Alvarez", "M. Kowalski", "T. Nguyen", "S. Osei", "R. Fischer", "L. Dubois"]

date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]

rows = []
start = date(2025, 1, 1)
for day_offset in range(273):  # Jan 1 - Sep 30 2025 (Q1-Q3)
    current_date = start + timedelta(days=day_offset)
    n_orders = random.randint(2, 6)
    for _ in range(n_orders):
        region = random.choice(regions)
        product, base_price = random.choice(products)
        qty = random.randint(1, 8)

        # Engineer a real Q3 dip in the West region (~35% volume drop)
        if region == "West" and current_date.month in (7, 8, 9):
            if random.random() < 0.35:
                continue  # order simply didn't happen

        price = base_price
        revenue = round(price * qty, 2)

        # Inject messiness
        fmt = random.choice(date_formats)
        date_str = current_date.strftime(fmt)
        region_str = random.choice([region, region.upper(), region.lower(), f" {region} "])
        rep = random.choice(reps)
        if random.random() < 0.04:
            rep = ""  # missing sales rep
        price_str = f"${price:.2f}" if random.random() < 0.3 else f"{price:.2f}"

        rows.append({
            "order_date": date_str,
            "region": region_str,
            "product": product,
            "unit_price": price_str,
            "quantity": qty,
            "revenue": revenue,
            "sales_rep": rep,
        })

        # ~3% chance of an accidental duplicate row (common raw-export issue)
        if random.random() < 0.03:
            rows.append(dict(rows[-1]))

random.shuffle(rows)

with open("/home/claude/portfolio/projects/etl-pipeline/data/raw_sales_data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} raw rows (with intentional duplicates/messiness).")
