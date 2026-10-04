# ABTalks Databricks Cohort

A 31-day hands-on journey through the Databricks Lakehouse platform. This repository tracks daily progress — from workspace basics and Unity Catalog to data pipelines, analytics, and machine learning. Each day includes a notebook and detailed notes documenting what was learned.

## Daily Progress

| Day | Title | Status | Topics Covered |
| --- | --- | --- | --- |
| 1 | Hello Lakehouse | ✅ Complete | Workspace navigation, compute, notebooks, PySpark & SQL basics, `%sql` magic |
| 2 | Catalog & Schema Setup | ✅ Complete | Unity Catalog, `USE CATALOG`/`USE SCHEMA`, medallion architecture, `SHOW SCHEMAS`/`SHOW VOLUMES` |
| 3 | Spark DataFrame Basics | ✅ Complete | `spark.read.table`, `select`/`filter`/`withColumn`, `groupBy`/`agg`, `orderBy`, `show`/`count`/`collect`, temp views, SQL interop |
| 4 | — | ⬜ Upcoming | — |
| 5 | — | ⬜ Upcoming | — |
| 6 | — | ⬜ Upcoming | — |
| 7 | — | ⬜ Upcoming | — |
| 8 | — | ⬜ Upcoming | — |
| 9 | — | ⬜ Upcoming | — |
| 10 | — | ⬜ Upcoming | — |
| 11 | — | ⬜ Upcoming | — |
| 12 | — | ⬜ Upcoming | — |
| 13 | — | ⬜ Upcoming | — |
| 14 | — | ⬜ Upcoming | — |
| 15 | — | ⬜ Upcoming | — |
| 16 | — | ⬜ Upcoming | — |
| 17 | — | ⬜ Upcoming | — |
| 18 | — | ⬜ Upcoming | — |
| 19 | — | ⬜ Upcoming | — |
| 20 | — | ⬜ Upcoming | — |
| 21 | — | ⬜ Upcoming | — |
| 22 | — | ⬜ Upcoming | — |
| 23 | — | ⬜ Upcoming | — |
| 24 | — | ⬜ Upcoming | — |
| 25 | — | ⬜ Upcoming | — |
| 26 | — | ⬜ Upcoming | — |
| 27 | — | ⬜ Upcoming | — |
| 28 | — | ⬜ Upcoming | — |
| 29 | — | ⬜ Upcoming | — |
| 30 | — | ⬜ Upcoming | — |
| 31 | — | ⬜ Upcoming | — |

### Day 1 — Hello Lakehouse

Got comfortable with the Databricks platform and created our first notebook.

- Explored the workspace layout, compute, and notebook interface
- Ran `print("Hello, Databricks!")` in a Python cell and attached it to a cluster
- Tested PySpark (`spark.range(10)`) and SQL (`SELECT * FROM range(10)`) side by side
- Learned that Python and SQL cells can be mixed using `%sql` magic commands
- Got a brief overview of Unity Catalog's role in data governance

**Key takeaway**: Databricks unifies data engineering, analytics, and ML in one workspace where Spark DataFrames and SQL are first-class citizens.

### Day 2 — Catalog & Schema Setup

Dove into Unity Catalog — set up the data environment and explored the `health_claims` catalog.

- Discovered workspace catalogs: `dbacademy`, `health_claims`, `samples`, `system`, `workspace`
- Used `USE CATALOG health_claims;` and `USE SCHEMA bronze;` to set context via SQL
- Found a **medallion architecture** in `health_claims` (bronze → silver → gold)
- Ran `SHOW SCHEMAS` and `SHOW VOLUMES` to explore the bronze schema's `raw` volume
- Practiced writing multi-statement SQL cells with semicolons

**Key takeaway**: Unity Catalog's three-level namespace (catalog.schema.table) organizes and governs data, while the medallion architecture structures pipelines from raw to curated.

### Day 3 — Spark DataFrame Basics

Got hands-on with PySpark DataFrames using the NYC taxi trips sample dataset.

- Loaded `samples.nyctaxi.trips` with `spark.read.table()` and projected columns with `select()` + `to_date()`
- Filtered rows with `filter()` and added a derived column with `withColumn()`
- Aggregated with `groupBy()`/`agg()` and sorted with `orderBy()`
- Ran actions — `show()`, `count()`, `collect()` — and iterated over `Row` objects
- Exposed a DataFrame to SQL via `createOrReplaceTempView()` and queried it with `%sql`

**Key takeaway**: PySpark DataFrames are lazy — transformations build a plan, actions execute it — and they interoperate with SQL through temp views.

## Repository Structure

```
databricks-cohort/
├── README.md                      # This file — cohort summary
├── daily notes/
│   ├── Day1.md                    # Day 1 detailed notes
│   ├── Day2.md                    # Day 2 detailed notes
│   └── Day3.md                    # Day 3 detailed notes
└── notebooks/
    ├── day01_hello_lakehouse.py   # Day 1 notebook
    ├── day02_setup_catalog.py     # Day 2 notebook
    └── day03_spark_basics.py      # Day 3 notebook
```

## What's Next

- Load raw data into the bronze layer using Auto Loader or `COPY INTO`
- Transform bronze data into silver with cleaning and deduplication
- Build gold-layer aggregate tables for analytics and reporting
- Dive deeper into Delta Lake and PySpark within notebooks

---
*Follow along as we build on the Lakehouse, one day at a time!* 🚀