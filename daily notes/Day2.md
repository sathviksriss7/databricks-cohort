# Day 2 — ABTalks Databricks Cohort

## Overview

Day 2 was all about Unity Catalog — setting up our data environment, navigating catalogs and schemas, and getting hands-on with the `health_claims` catalog using SQL.

## What We Did

### 1. Explored the Catalog Explorer

- Reviewed the three-level namespace in Unity Catalog: **catalog → schema → table/volume**.
- Discovered the catalogs available in our workspace: `dbacademy`, `health_claims`, `samples`, `system`, and `workspace`.
- Learned that each catalog can contain multiple schemas, and each schema can contain tables and volumes.

### 2. Set Catalog and Schema Context with SQL

- Used `USE CATALOG health_claims;` to switch to the health_claims catalog.
- Used `USE SCHEMA bronze;` to set the active schema to the bronze layer.
- Learned that `USE` statements persist for the duration of the notebook session, so all subsequent queries run against the selected catalog and schema.

### 3. Discovered the Medallion Architecture

- Ran `SHOW SCHEMAS;` and found the health_claims catalog follows a **medallion architecture**:
  - **bronze** — raw, ingested data
  - **silver** — cleaned and transformed data
  - **gold** — business-level aggregates and curated datasets
- Ran `SHOW VOLUMES;` on the bronze schema and found a volume called **`raw`** — a storage area for landing raw files before they are loaded into Delta tables.

### 4. Created the Day 2 Notebook

- Created `day02_setup_catalog.py` with a SQL cell to explore the catalog structure.
- Practiced writing multi-statement SQL cells with semicolons separating each command.
- Learned that `SHOW SCHEMAS` lists schemas in the current catalog and `SHOW VOLUMES` lists volumes in the current schema.

## Key Takeaways

- Unity Catalog uses a three-level namespace (catalog.schema.table) to organize and govern data.
- `USE CATALOG` and `USE SCHEMA` set the active context so you don't need to fully qualify every table name.
- The medallion architecture (bronze → silver → gold) is a common pattern for structuring data pipelines in Databricks.
- Volumes provide managed storage for non-tabular files (CSV, JSON, Parquet) alongside Delta tables in the same schema.

## Next Steps

- Load raw data into the bronze layer using Auto Loader or `COPY INTO`.
- Transform bronze data into the silver layer with cleaning and deduplication.
- Build gold-layer aggregate tables for analytics and reporting.

---
*Day 2 complete — the catalog is set up and ready for data!* 📂