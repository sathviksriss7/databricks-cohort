# ABTalks Databricks Cohort

A 31-day hands-on journey through the Databricks Lakehouse platform. This repository tracks daily progress — from workspace basics and Unity Catalog to data pipelines, analytics, and machine learning. Each day includes a notebook and detailed notes documenting what was learned.

## Daily Progress

| Day | Title | Status | Topics Covered |
| --- | --- | --- | --- |
| 1 | Hello Lakehouse | ✅ Complete | Workspace navigation, compute, notebooks, PySpark & SQL basics, `%sql` magic |
| 2 | Catalog & Schema Setup | ✅ Complete | Unity Catalog, `USE CATALOG`/`USE SCHEMA`, medallion architecture, `SHOW SCHEMAS`/`SHOW VOLUMES` |
| 3 | Spark DataFrame Basics | ✅ Complete | `spark.read.table`, `select`/`filter`/`withColumn`, `groupBy`/`agg`, `orderBy`, `show`/`count`/`collect`, temp views, SQL interop |
| 4 | Generate Claims Data | ✅ Complete | Synthetic healthcare claims generation (Faker), raw CSV landing zone, data dictionary, medallion plan |
| 5 | Delta Lake Fundamentals | ✅ Complete | CSV to Delta, `DESCRIBE HISTORY`/`DESCRIBE DETAIL`, time travel (`VERSION AS OF`), schema enforcement vs. `mergeSchema` |
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

### Day 4 — Generate Claims Data

Built a synthetic healthcare-claims dataset with `faker` and landed it in the raw volume.

- Generated 5 entities: plans (20), providers (805), members (5,010), claims (50,015), claim lines (~224k)
- Injected intentional data quality issues: duplicates, nulls, mixed-case states, bad dates, implausible ages, null FKs
- Wrote CSVs to `/Volumes/health_claims/bronze/raw/` — claims split into 3 dated files for incremental-load practice
- Created `docs/data_dictionary.md` (column-level reference) and `docs/medallion_plan.md` (raw → bronze → silver → gold plan)
- Fixed an f-string syntax error: `f'{9920{0+i%5}'` → `f'9920{i%5}'`

**Key takeaway**: Synthetic data with controlled quality issues lets us practice real data engineering pipelines without needing actual PII — and documenting the schema first makes the downstream cleaning steps clear.

### Day 5 — Delta Lake Fundamentals

Got hands-on with Delta Lake — the storage layer that powers the Lakehouse.

- Read a raw CSV from the UC Volume and wrote it as a Delta table (`health_claims.bronze.delta_demo`)
- Inspected table history and metadata with `DESCRIBE HISTORY` and `DESCRIBE DETAIL`
- Practiced time travel with `VERSION AS OF 0` to read the table before an append
- Demonstrated schema enforcement (blocked mismatched write) vs. `mergeSchema=true` (allowed schema evolution)
- Fixed 3 bugs: DBFS path (`/mnt/` → `/Volumes/`), SQL-in-Python (`%sql` magic), Spark Connect type inference (`schema=` param)

**Key takeaway**: Delta Lake gives you ACID transactions, automatic versioning, time travel, and schema enforcement for free — `saveAsTable` is all it takes to get a governed, queryable, history-aware table.

## Repository Structure

```
databricks-cohort/
├── README.md                      # This file — cohort summary
├── docs/
│   ├── data_dictionary.md         # Column-level data dictionary for all entities
│   └── medallion_plan.md          # Raw -> Bronze -> Silver -> Gold architecture plan
├── daily notes/
│   ├── Day1.md                    # Day 1 detailed notes
│   ├── Day2.md                    # Day 2 detailed notes
│   ├── Day3.md                    # Day 3 detailed notes
│   ├── Day4.md                    # Day 4 detailed notes
│   └── Day5.md                    # Day 5 detailed notes
└── notebooks/
    ├── day01_hello_lakehouse.py   # Day 1 notebook
    ├── day02_setup_catalog.py     # Day 2 notebook
    ├── day03_spark_basics.py      # Day 3 notebook
    ├── day04_generate_claims.py   # Day 4 notebook
    └── day05_delta_fundamentals.py # Day 5 notebook
```

## What's Next

- Ingest all raw CSVs into bronze Delta tables using `COPY INTO` and Auto Loader
- Transform bronze data into silver with cleaning and deduplication
- Build gold-layer aggregate tables for analytics and reporting
- Explore Delta optimization: `OPTIMIZE`, `ZORDER`, `VACUUM`

---
*Follow along as we build on the Lakehouse, one day at a time!* 🚀