# Databricks notebook source
# DBTITLE 1,Cell 1
from pyspark.sql.functions import to_date, col, lit

# COMMAND ----------

selected_trips = spark.read.table("samples.nyctaxi.trips").select(
    to_date(col("tpep_pickup_datetime")).alias("pickup_date"),
    to_date(col("tpep_dropoff_datetime")).alias("dropoff_date"),
    "trip_distance",
    "fare_amount",
    "pickup_zip",
    "dropoff_zip",
)

# COMMAND ----------

# DBTITLE 1,Cell 3
filtered_trips = selected_trips.filter(
    (col("pickup_zip") != col("dropoff_zip"))
    & (col("pickup_zip") != 0)
    & (col("dropoff_zip") != 0)
)

# COMMAND ----------

# Add a ride_bonus_amount column: 4% of the fare_amount as a bonus surcharge
filtered_trips_new = filtered_trips.withColumn(
    "ride_bonus_amount", col("fare_amount") * 0.04
)

# Group by pickup and dropoff zip codes and aggregate fare, distance, and bonus
aggregated_trips = (
    filtered_trips_new.groupBy("pickup_zip", "dropoff_zip")
    .agg({"fare_amount": "avg", "trip_distance": "avg", "ride_bonus_amount": "avg"})
    .withColumnRenamed("avg(fare_amount)", "avg_fare_amount")
    .withColumnRenamed("avg(trip_distance)", "avg_trip_distance")
    .withColumnRenamed("avg(ride_bonus_amount)", "avg_ride_bonus_amount")
)

# COMMAND ----------

grouped_trips = filtered_trips_new.groupBy("pickup_zip", "dropoff_zip").agg(
    {"fare_amount": "avg", "trip_distance": "avg"}
)

# COMMAND ----------

ordered_trips = grouped_trips.orderBy(
    "avg(fare_amount)", "avg(trip_distance)", ascending=False
)

# COMMAND ----------

ordered_trips.show(10)

# COMMAND ----------

total_rows = ordered_trips.count()
print("Total rows: ", total_rows)

# COMMAND ----------

local_data = ordered_trips.collect()

for row in local_data:
    print(row["pickup_zip"])

# COMMAND ----------

filtered_trips_new.createOrReplaceTempView("trips")

# COMMAND ----------

# MAGIC %sql
# MAGIC select
# MAGIC   *
# MAGIC from
# MAGIC   filtered_trips_new
# MAGIC where
# MAGIC   pickup_zip = 10028
# MAGIC   and trip_distance > 10