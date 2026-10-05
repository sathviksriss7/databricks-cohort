# Day 5 — ABTalks Databricks Cohort

## Overview

Day 5 introduced Delta Lake fundamentals — the storage layer that powers the Lakehouse. We read a raw CSV from the UC Volume into a Delta table, inspected its history and metadata with `DESCRIBE HISTORY` / `DESCRIBE DETAIL`, practiced time travel with `VERSION AS OF`, and demonstrated schema enforcement vs. `mergeSchema`. Along the way we hit and fixed three real issues: a DBFS path error, SQL-in-Python syntax error, and a Spark Connect type-inference failure.

## What We Did

### 1. Read a Raw CSV and Wrote a Delta Table

- Read `/Volumes/health_claims/bronze/raw/claims_20130929_to_20310921.csv` (the largest of the 3 dated claims files) with `spark.read.option("header", True).option("inferSchema", True).csv()`.
- Wrote it to Unity Catalog as `health_claims.bronze.delta_demo` using `.format("delta").mode("overwrite").saveAsTable()`.
- 49,980 rows, 16 columns — dates inferred as `date`, amounts as `double`.
- **Fix**: The original path was `/mnt/raw/claims/claims.csv` (a DBFS mount). DBFS is disabled on serverless compute — only UC Volume paths (`/Volumes/...`) are accessible. Changed to the actual volume path.

### 2. Inspected Delta Table History and Metadata

- Ran `DESCRIBE HISTORY health_claims.bronze.delta_demo` to see the commit log (version, timestamp, operation, operation parameters).
- Ran `DESCRIBE DETAIL health_claims.bronze.delta_demo` to inspect table-level metadata: format (Delta), 1 file, ~1.3 MB, created today, deletion vectors enabled, table features (`appendOnly`, `deletionVectors`, `invariants`).
- **Fix**: The cell contained bare SQL statements (`DESCRIBE HISTORY;`) in a Python cell. Python couldn't parse the SQL keywords, causing a `SyntaxError`. Added `%sql` magic prefix and the table name to both statements.

### 3. Appended a Row and Time-Traveled to Version 0

- Created a single all-null row with `spark.createDataFrame([Row(**{c: None for c in raw_df.columns})], schema=raw_df.schema)` and appended it to the Delta table with `.mode("append")`.
- Queried the table at version 0 with `spark.sql("SELECT * FROM health_claims.bronze.delta_demo VERSION AS OF 0")` — returned the original 49,980 rows (before the append).
- **Fix**: `spark.createDataFrame` with an all-null row failed on Spark Connect with `CANNOT_DETERMINE_TYPE` — Spark can't infer types from all-null data. Adding `schema=raw_df.schema` bypasses inference by passing the known schema explicitly.
- **Key concept**: Delta Lake automatically versions every write. `VERSION AS OF 0` reads the table as it existed after the first commit, before subsequent appends — no manual snapshotting needed.

### 4. Schema Enforcement and mergeSchema

- Built a `mismatched_df` with an extra column (`extra_column`) not present in the target table, using `raw_df.schema.add("extra_column", "string")`.
- **Attempt 1** — appended without `mergeSchema`: Delta blocked the write with a schema mismatch error, confirming that Delta enforces schema by default.
- **Attempt 2** — retried with `.option("mergeSchema", "true")`: the append succeeded, and the `extra_column` was added to the table schema.
- Verified the new column is now part of the table with `SELECT * FROM health_claims.bronze.delta_demo`.
- **Key concept**: Delta's schema enforcement prevents accidental column additions. `mergeSchema=true` overrides this for controlled schema evolution — useful when intentionally adding new columns to a growing table.

## Bugs Fixed

| # | Error | Cause | Fix |
| --- | --- | --- | --- |
| 1 | `[DBFS_DISABLED]` on `/mnt/raw/claims/claims.csv` | DBFS mounts disabled on serverless; only UC Volumes accessible | Changed path to `/Volumes/health_claims/bronze/raw/claims_20130929_to_20310921.csv` |
| 2 | `SyntaxError: invalid syntax` on `DESCRIBE HISTORY;` | SQL statements in a Python cell without `%sql` magic | Added `%sql` prefix and table name to both `DESCRIBE` statements |
| 3 | `PySparkValueError: [CANNOT_DETERMINE_TYPE]` on `createDataFrame` | All-null row — Spark Connect can't infer types from `None` values | Added `schema=raw_df.schema` to `createDataFrame` to bypass inference |

## Key Takeaways

- **Delta Lake is the default storage format** on Databricks — `saveAsTable` creates a managed Delta table in Unity Catalog with ACID transactions, schema enforcement, and time travel built in.
- **`DESCRIBE HISTORY`** shows the commit log (every version, operation, and timestamp); **`DESCRIBE DETAIL`** shows table-level metadata (file count, size, features, partition columns).
- **Time travel** (`VERSION AS OF N` or `TIMESTAMP AS OF ...`) reads a past version of the table without restoring it — Delta keeps a history of all changes automatically.
- **Schema enforcement** blocks writes with mismatched columns by default; `mergeSchema=true` allows controlled schema evolution when you intentionally add columns.
- **Serverless compute** does not support DBFS mounts (`/mnt/`) — always use UC Volume paths (`/Volumes/catalog/schema/volume/...`) for file I/O.
- **Spark Connect** (serverless) has stricter type inference than classic Spark — `createDataFrame` with all-null rows needs an explicit `schema=` parameter.

## Files Created

| File | Description |
| --- | --- |
| `notebooks/day05_delta_fundamentals` | Delta Lake fundamentals notebook (4 cells) |

---
*Day 5 complete — Delta Lake tables created, inspected, time-traveled, and schema-evolved!* 🏥