# Mamaearth Returns & Growth Intelligence Pipeline

## Project Overview

This project implements an end-to-end analytics pipeline for Mamaearth, connecting three layers:

1. **SQL** — relational data storage and reporting
2. **Python/Pandas** — data cleaning, EDA, reconciliation, and visualization
3. **GenAI** — verified business insights using Gemini and an offline SCR fallback

The pipeline uses the raw CSV files in `data/` without modifying the source data.

---

## Repository Structure

```text
<repo>/
├── README.md
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    └── generate_narrative.py
```

---

## 1. SQL Relational Layer

Use **SQLite** or another SQL engine compatible with the provided SQL syntax.

Run the files in this order:

```text
sql/schema.sql
sql/seed_data.sql
sql/reports.sql
```

### SQLite

```bash
sqlite3 mamaearth.db
```

Then execute:

```sql
.read sql/schema.sql
.read sql/seed_data.sql
.read sql/reports.sql
```

The seed data should load:

* 45 customers
* 16 products
* 180 orders

`reports.sql` contains the required reporting queries and expected validation outputs.

---

## 2. Python Analysis & Visualization

Run both scripts from the **repository root**, in this order:

```bash
python analysis/clean_and_eda.py
```

Then:

```bash
python analysis/visualize.py
```

`clean_and_eda.py`:

* Loads the three raw CSV files
* Standardizes payment-method casing
* Removes duplicate orders
* Imputes missing values
* Merges orders, customers, and products
* Calculates order values
* Performs outlier, return-rate, segmentation, correlation, and time-series analysis
* Writes the verified Part 3 input to:

```text
narrator/findings.json
```

`visualize.py` generates:

```text
visualizations/return_rate_by_payment.png
visualizations/monthly_revenue_trend.png
```

Both scripts are designed to be re-runnable from the raw CSV files.

---

## 3. GenAI Narrative Layer

Run:

```bash
python narrator/generate_narrative.py
```

### With Gemini API Key

Set `GOOGLE_API_KEY` as an environment variable.

**Windows PowerShell:**

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
python narrator/generate_narrative.py
```

**macOS/Linux:**

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
python narrator/generate_narrative.py
```

The script generates a three-section **Situation–Complication–Resolution (SCR)** narrative using the verified values in `narrator/findings.json`.

### Without an API Key

No environment configuration is required:

```bash
python narrator/generate_narrative.py
```

When `GOOGLE_API_KEY` is unavailable, the script uses the deterministic **offline fallback**. This path requires no network access or API quota.

---

## End-to-End Execution

```bash
# SQL
sqlite3 mamaearth.db
.read sql/schema.sql
.read sql/seed_data.sql
.read sql/reports.sql

# Python
python analysis/clean_and_eda.py
python analysis/visualize.py

# GenAI / Offline
python narrator/generate_narrative.py
```

All reported figures are derived from the supplied raw data and flow from one pipeline layer to the next.
