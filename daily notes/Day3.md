# Day 3 — ABTalks Databricks Cohort

## Overview

Day 3 was all about PySpark DataFrames — reading tables, transforming with `select`/`filter`/`withColumn`, aggregating with `groupBy`/`agg`, sorting with `orderBy`, and mixing DataFrames with SQL through temp views. We worked entirely with the NYC taxi trips sample dataset (`samples.nyctaxi.trips`).

## What We Did

### 1. Loaded a Table into a DataFrame

- Read a Unity Catalog table with `spark.read.table("samples.nyctaxi.trips")`.
- Projected and renamed columns in one step: `.select(to_date(col("tpep_pickup_datetime")).alias("pickup_date"), ...)`.
- Learned that `to_date`, `col`, and `lit` live in `pyspark.sql.functions`, while methods like `select` and `withColumn` are called **on the DataFrame**.

### 2. Filtered Rows

- Used `.filter()` with `col()` comparisons combined with `&`:
  `(col("pickup_zip") != col("dropoff_zip")) & (col("pickup_zip") != 0) & (col("dropoff_zip") != 0)`.
- Each condition needs its own parentheses when combining with `&` / `|`.

### 3. Added a Derived Column

- Used `.withColumn("ride_bonus_amount", col("fare_amount") * 0.04)` to add a 4% bonus surcharge.
- Learned that `withColumn` is a DataFrame method — not something you import (a bug we hit and fixed).

### 4. Aggregated and Sorted

- Grouped with `.groupBy("pickup_zip", "dropoff_zip").agg({"fare_amount": "avg", "trip_distance": "avg"})` using the dict shorthand.
- Renamed auto-generated columns like `avg(fare_amount)` with `.withColumnRenamed(...)` for cleaner names.
- Sorted results with `.orderBy("avg(fare_amount)", ascending=False)`.

### 5. Ran Actions and Accessed Rows

- Actions trigger execution: `.show(10)`, `.count()`, and `.collect()`.
- `collect()` pulls the results to the driver as a list of `Row` objects — each field is accessed like `row["pickup_zip"]`.
- Our aggregated dataset had 3,270 pickup/dropoff zip combinations.

### 6. Bridged DataFrames and SQL

- Registered a DataFrame for SQL with `.createOrReplaceTempView("trips")`.
- Queried it in a SQL cell with `%sql select * from trips where ...`.
- Big lesson learned: `.show()` returns `None` — never chain it onto the end of an assignment (`df = ....show(10)` stores `None`, not a DataFrame).

## Key Takeaways

- PySpark DataFrames are **lazy** — transformations (`select`, `filter`, `withColumn`, `groupBy`) only build a plan; actions (`show`, `count`, `collect`) actually execute it.
- DataFrame methods are called on the DataFrame object; column expressions (`col`, `lit`, `to_date`) come from `pyspark.sql.functions`.
- `show()`, `count()`, and `collect()` are actions — and `show()` returns `None`, so it belongs on its own line.
- Temp views (`createOrReplaceTempView`) let SQL and DataFrame code operate on the same data in one notebook.

---
*Day 3 complete — DataFrames read, transformed, aggregated, and queried with SQL!* 🚕