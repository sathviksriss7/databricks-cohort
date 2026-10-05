# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# Read one raw claims file and write it as a Delta table
raw_claims_path = "/Volumes/health_claims/bronze/raw/claims_20130929_to_20310921.csv"

raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(raw_claims_path)
)

# Write to Unity Catalog as a Delta table
(
    raw_df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("health_claims.bronze.delta_demo")
)

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY health_claims.bronze.delta_demo;
# MAGIC DESCRIBE DETAIL health_claims.bronze.delta_demo

# COMMAND ----------

# Append a few rows to the Delta table, then time-travel back to version 0
from pyspark.sql import Row

new_rows = spark.createDataFrame([
    Row(**{c: None for c in raw_df.columns})  
], schema=raw_df.schema)

(
    new_rows.write
    .format("delta")
    .mode("append")
    .saveAsTable("health_claims.bronze.delta_demo")
)

# Query the table as it was at version 0 (before the append)
spark.sql("SELECT * FROM health_claims.bronze.delta_demo VERSION AS OF 0").display()

# COMMAND ----------

# Schema enforcement: try appending a row with a MISMATCHED schema.
# Delta blocks this by default, then we retry with mergeSchema=true.

# Build a DataFrame with an extra column that doesn't exist in the target table
mismatched_df = spark.createDataFrame(
    [{c: None for c in raw_df.columns} | {"extra_column": "surprise"}],
    schema=raw_df.schema.add("extra_column", "string")
)

# --- Attempt 1: append without mergeSchema (expect a schema mismatch error) ---
print("Attempting append with mismatched schema (should fail)...")
try:
    (
        mismatched_df.write
        .format("delta")
        .mode("append")
        .saveAsTable("health_claims.bronze.delta_demo")
    )
    print("Unexpected: write succeeded without mergeSchema!")
except Exception as e:
    print(f"Expected schema enforcement error:\n{e}\n")

# --- Attempt 2: retry with mergeSchema=true (should succeed) ---
print("Retrying append with mergeSchema=true...")
(
    mismatched_df.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable("health_claims.bronze.delta_demo")
)
print("Append succeeded with mergeSchema=true!")

# Verify the new column is now part of the table schema
spark.sql("SELECT * FROM health_claims.bronze.delta_demo").display()