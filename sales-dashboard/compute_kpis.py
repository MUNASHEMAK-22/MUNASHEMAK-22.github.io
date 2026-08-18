"""
Computes the KPI measures a Power BI data model would define via DAX:
Total Revenue, Profit Margin %, and Year-over-Year Growth %, sliced by
region, product, and quarter. Exports the aggregates as JSON so the
web dashboard can render real, verifiable numbers instead of placeholders.

Equivalent DAX (documented here since Power BI itself can't run inside
a static GitHub Pages site):

    Total Revenue = SUM(sales[revenue])
    Total Profit  = SUM(sales[profit])
    Profit Margin % = DIVIDE([Total Profit], [Total Revenue], 0)
    YoY Growth % =
        VAR CurrentYear = [Total Revenue]
        VAR PriorYear =
            CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(sales[order_date]))
        RETURN DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
"""
import csv
import json
from collections import defaultdict

rows = list(csv.DictReader(open("/home/claude/portfolio/projects/sales-dashboard/data/sales_2yr.csv")))
for r in rows:
    r["revenue"] = float(r["revenue"])
    r["cost"] = float(r["cost"])
    r["profit"] = float(r["profit"])
    r["quantity"] = int(r["quantity"])
    r["year"] = int(r["year"])


def revenue_of(subset):
    return round(sum(r["revenue"] for r in subset), 2)

def profit_margin_of(subset):
    rev = sum(r["revenue"] for r in subset)
    prof = sum(r["profit"] for r in subset)
    return round((prof / rev * 100), 1) if rev else 0

def yoy(subset_2025, subset_2024):
    r25 = sum(r["revenue"] for r in subset_2025)
    r24 = sum(r["revenue"] for r in subset_2024)
    return round(((r25 - r24) / r24 * 100), 1) if r24 else 0


rows_2025 = [r for r in rows if r["year"] == 2025]
rows_2024 = [r for r in rows if r["year"] == 2024]

# Overall KPIs (2025 vs 2024)
overall = {
    "totalRevenue2025": revenue_of(rows_2025),
    "totalRevenue2024": revenue_of(rows_2024),
    "profitMargin2025": profit_margin_of(rows_2025),
    "yoyGrowth": yoy(rows_2025, rows_2024),
}

# By region (2025)
by_region = {}
for region in ["North", "South", "East", "West"]:
    r25 = [r for r in rows_2025 if r["region"] == region]
    r24 = [r for r in rows_2024 if r["region"] == region]
    by_region[region] = {
        "revenue": revenue_of(r25),
        "margin": profit_margin_of(r25),
        "yoy": yoy(r25, r24),
    }

# By region by quarter (2025) - for the Q3 dip chart
by_region_quarter = defaultdict(dict)
for region in ["North", "South", "East", "West"]:
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        subset = [r for r in rows_2025 if r["region"] == region and r["quarter"] == q]
        by_region_quarter[region][q] = revenue_of(subset)

# By product (2025) - top performers
products = sorted(set(r["product"] for r in rows))
by_product = []
for p in products:
    subset = [r for r in rows_2025 if r["product"] == p]
    by_product.append({
        "product": p,
        "revenue": revenue_of(subset),
        "margin": profit_margin_of(subset),
        "units": sum(r["quantity"] for r in subset),
    })
by_product.sort(key=lambda x: -x["revenue"])

output = {
    "overall": overall,
    "byRegion": by_region,
    "byRegionQuarter": dict(by_region_quarter),
    "byProduct": by_product,
}

with open("/home/claude/portfolio/projects/sales-dashboard/data/dashboard_data.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(overall, indent=2))
print("\nWest region 2025:", by_region["West"])
