# Example: Weekly Sales Report

This example loads a local CSV file of sales transactions into DuckDB and generates a styled HTML report.

## Files

- `pipeline.yaml` — the JakeFSD pipeline manifest
- `data/sales.csv` — sample sales data

## Run

From this directory:

```bash
jakefsd run pipeline.yaml
```

The pipeline will:
1. Read `data/sales.csv`
2. Load it into `data/sales.duckdb` table `sales`
3. Write `reports/sales_report.html`

## Schedule

Run every Monday at 9am:

```bash
jakefsd schedule pipeline.yaml
```

## Preview a stage

```bash
jakefsd preview pipeline.yaml --stage source
```
