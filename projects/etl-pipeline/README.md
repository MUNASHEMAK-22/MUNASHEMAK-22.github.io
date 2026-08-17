# Automated ETL Pipeline for Business Reporting

Extracts messy raw sales data from CSV, cleans and validates it, and loads it into a SQLite database ready for Power BI reporting.

## Why

Raw exports from order systems are never clean: inconsistent date formats, mixed currency formatting, inconsistent casing, missing fields, and accidental duplicate rows. This pipeline removes the need to fix any of that by hand every reporting cycle.

## Structure

```
etl-pipeline/
├── data/
│   ├── generate_raw_data.py   # generates the synthetic raw dataset (messy, on purpose)
│   ├── raw_sales_data.csv     # raw input
│   └── sales.db               # cleaned output (created by etl_pipeline.py)
├── etl_pipeline.py            # the actual ETL script
└── README.md
```

## Running it

```bash
# 1. (Optional) regenerate the raw sample data
python data/generate_raw_data.py

# 2. Run the pipeline
python etl_pipeline.py
```

Output is logged to the console and written to `data/sales.db`. Re-running the script is safe — the load step is idempotent, so it never creates duplicate data on repeated runs.

## What it handles

- Three inconsistent date formats → normalized to ISO 8601
- Mixed currency formatting (`$149.99` vs `149.99`) → normalized to float
- Inconsistent region casing/whitespace (` EAST `, `east`) → normalized to title case
- Missing sales-rep values → filled with `Unassigned`
- Exact-duplicate rows from the raw export → detected and dropped

## Next steps

- Schedule via cron / a cloud function instead of manual runs
- Move from SQLite to a hosted Postgres database
- Add automated data-quality tests (e.g. with `pytest` + `great_expectations`)
