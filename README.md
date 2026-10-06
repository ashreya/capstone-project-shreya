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

Create a database in mysql worbench and select it.

Run the files in this order:

```text
sql/schema.sql
sql/seed_data.sql
sql/reports.sql
```

### SQLite

```bash
crate database my_db;
use my_db;
```

Then import the below fles into mysql workbench and execute:

```sql
sql/schema.sql
sql/seed_data.sql
sql/reports.sql
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

Set `GOOGLE_API_KEY` as an environment variable or create a .env file with GOOGLE_API_KEY= `<your API key>`.

The script generates a three-section **Situation–Complication–Resolution (SCR)** narrative using the verified values in `narrator/findings.json`.

### Without an API Key

No environment configuration is required:

```bash
python narrator/generate_narrative.py
```

When `GOOGLE_API_KEY` is unavailable, the script uses the deterministic **offline fallback**. This path requires no network access or API quota.
Also there is funvtion in `generate_narrative.py` named `validate_numbers` that verifies the Numeric accuracy.

---
All reported figures are derived from the supplied raw data and flow from one pipeline layer to the next.
