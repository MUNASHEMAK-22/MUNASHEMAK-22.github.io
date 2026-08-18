[README.md](https://github.com/user-attachments/files/31176512/README.md)
# Financial Performance & Sales Analytics Dashboard

Data model and DAX measures for a sales KPI dashboard, covering Total Revenue, Profit Margin %, and Year-over-Year Growth %.

## Structure

```
sales-dashboard/
├── generate_sales_data.py   # generates 2 years of synthetic sales data
├── compute_kpis.py          # computes the DAX-equivalent measures, exports dashboard_data.json
└── sales_2yr.csv            # raw generated data (4,175 rows, 2024–2025)
```

## Running it

```bash
python generate_sales_data.py   # creates sales_2yr.csv
python compute_kpis.py          # creates dashboard_data.json, prints headline KPIs
```

## DAX measures (as they'd be defined in Power BI)

```
Total Revenue = SUM(sales[revenue])
Total Profit  = SUM(sales[profit])

Profit Margin % =
    DIVIDE([Total Profit], [Total Revenue], 0)

YoY Growth % =
    VAR CurrentYear = [Total Revenue]
    VAR PriorYear =
        CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(sales[order_date]))
    RETURN
        DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
```

`compute_kpis.py` implements the same logic in plain Python so the numbers on the live web dashboard (`projects/sales-dashboard.html`) are real, reproducible output — not hardcoded placeholders.

## Headline finding

Overall revenue grew 1.4% year-over-year, but that average hides a real regional problem: West declined 12.2% while North and East both grew. The dip is concentrated in Q3 — invisible in the company-wide total, visible immediately once sliced by region.

## Next steps

- Add a drill-through view for rep- and product-level detail within a region/quarter
- Bring in a budget/target table to measure variance, not just period-over-period change
- Publish to Power BI Service and embed the live report
