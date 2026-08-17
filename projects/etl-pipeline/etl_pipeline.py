"""
Automated ETL Pipeline for Business Reporting
-----------------------------------------------
Extracts raw sales data from CSV, cleans and validates it, and loads it
into a SQL database ready for BI reporting.

Usage:
    python etl_pipeline.py
"""
import csv
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("etl")

RAW_PATH = Path(__file__).parent / "data" / "raw_sales_data.csv"
DB_PATH = Path(__file__).parent / "data" / "sales.db"

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]


def parse_date(raw: str) -> str:
    """Normalize inconsistent date formats to ISO 8601 (YYYY-MM-DD)."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {raw}")


def clean_price(raw: str) -> float:
    """Strip currency symbols and whitespace, return a float."""
    return float(raw.replace("$", "").strip())


def extract(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    log.info("Extracted %d raw rows from %s", len(rows), path.name)
    return rows


def transform(rows: list[dict]) -> list[dict]:
    seen = set()
    cleaned = []
    dropped_duplicates = 0
    dropped_invalid = 0

    for row in rows:
        # Deduplicate exact repeat orders (common raw-export artifact)
        key = tuple(row.values())
        if key in seen:
            dropped_duplicates += 1
            continue
        seen.add(key)

        try:
            order_date = parse_date(row["order_date"])
            region = row["region"].strip().title()
            product = row["product"].strip()
            unit_price = clean_price(row["unit_price"])
            quantity = int(row["quantity"])
            revenue = round(unit_price * quantity, 2)
            sales_rep = row["sales_rep"].strip() or "Unassigned"
        except (ValueError, KeyError):
            dropped_invalid += 1
            continue

        cleaned.append({
            "order_date": order_date,
            "region": region,
            "product": product,
            "unit_price": unit_price,
            "quantity": quantity,
            "revenue": revenue,
            "sales_rep": sales_rep,
        })

    log.info("Transform complete: %d clean rows, %d duplicates removed, %d invalid rows dropped",
              len(cleaned), dropped_duplicates, dropped_invalid)
    return cleaned


def load(rows: list[dict], db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT NOT NULL,
            region TEXT NOT NULL,
            product TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            revenue REAL NOT NULL,
            sales_rep TEXT NOT NULL
        )
    """)
    cur.execute("DELETE FROM sales")  # idempotent reload
    cur.executemany("""
        INSERT INTO sales (order_date, region, product, unit_price, quantity, revenue, sales_rep)
        VALUES (:order_date, :region, :product, :unit_price, :quantity, :revenue, :sales_rep)
    """, rows)
    conn.commit()
    conn.close()
    log.info("Loaded %d rows into %s", len(rows), db_path.name)


def run():
    raw_rows = extract(RAW_PATH)
    clean_rows = transform(raw_rows)
    load(clean_rows, DB_PATH)
    log.info("Pipeline finished successfully.")


if __name__ == "__main__":
    run()
