# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold Layer: Business-Ready HEDIS Analytics
# MAGIC
# MAGIC **Purpose:** Create aggregated, business-ready analytics tables
# MAGIC
# MAGIC **Creates:**
# MAGIC - `humana_quality.hedis_gold.member_quality_summary`
# MAGIC - `humana_quality.hedis_gold.measure_performance`
# MAGIC - `humana_quality.hedis_gold.gap_closure_analytics`
# MAGIC - `humana_quality.hedis_gold.quality_trends`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

import sys
import os

# Get current user dynamically
username = spark.conf.get("spark.databricks.workspaceUrl").split("@")[0] if "@" in spark.conf.get("spark.databricks.workspaceUrl") else "vik.malhotra@databricks.com"
bundle_name = "hedis_quality_dashboard"
target = "dev"

# Construct dynamic path
src_path = f"/Workspace/Users/{username}/.bundle/{bundle_name}/{target}/files/src"
sys.path.append(src_path)

print(f"✅ Added to path: {src_path}")

# COMMAND ----------

from pyspark.sql.functions import (
    col, lit, when, coalesce, current_timestamp,
    avg, sum as sql_sum, count, countDistinct,
    round as sql_round, desc, concat_ws,
    collect_list, struct, first, last, max as sql_max, min as sql_min
)
from pyspark.sql.window import Window

from utils.table_helpers import (
    create_schema_if_not_exists,
    write_table,
    verify_table
)

# COMMAND ----------

# Configuration
CATALOG = "humana_quality"
SILVER_SCHEMA = "hedis_silver"
GOLD_SCHEMA = "hedis_gold"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Gold Schema

# COMMAND ----------

create_schema_if_not_exists(spark, CATALOG, GOLD_SCHEMA)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Member Quality Summary

# COMMAND ----------

members = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.members")
measures = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.clinical_measures")

# Get current year measures
from datetime import datetime
current_year = datetime.now().year

current_measures = measures.filter(col("measurement_year") == current_year)

# Aggregate by member
member_summary = current_measures.groupBy("member_id").agg(
    count("*").alias("total_measures"),
    sql_sum(when(col("is_compliant"), 1).otherwise(0)).alias("compliant_measures"),
    sql_sum(when(col("has_gap"), 1).otherwise(0)).alias("open_gaps"),
    sql_sum(when(col("gap_closed"), 1).otherwise(0)).alias("closed_gaps"),
    collect_list(
        when(col("has_gap") & ~col("gap_closed"), 
             struct(col("measure_code"), col("measure_name"))
        )
    ).alias("gap_list")
)

# Calculate compliance rate
member_summary = member_summary.withColumn(
    "compliance_rate",
    sql_round(col("compliant_measures") / col("total_measures"), 3)
)

# Join with member demographics
member_quality = members.alias("m").join(
    member_summary.alias("s"),
    col("m.member_id") == col("s.member_id"),
    "left"
).select(
    col("m.member_id"),
    col("m.first_name"),
    col("m.last_name"),
    col("m.age"),
    col("m.gender"),
    col("m.risk_level"),
    col("m.is_active"),
    coalesce(col("s.total_measures"), lit(0)).alias("total_measures"),
    coalesce(col("s.compliant_measures"), lit(0)).alias("compliant_measures"),
    coalesce(col("s.open_gaps"), lit(0)).alias("open_gaps"),
    coalesce(col("s.closed_gaps"), lit(0)).alias("closed_gaps"),
    coalesce(col("s.compliance_rate"), lit(0.0)).alias("compliance_rate"),
    col("s.gap_list"),
    current_timestamp().alias("updated_at")
)

write_table(member_quality, CATALOG, GOLD_SCHEMA, "member_quality_summary")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Measure Performance Analytics

# COMMAND ----------

# Aggregate by measure and year
measure_performance = measures.groupBy("measure_code", "measure_name", "measurement_year").agg(
    count("*").alias("denominator"),
    sql_sum(col("numerator")).alias("numerator"),
    sql_sum(when(col("has_gap"), 1).otherwise(0)).alias("gaps_identified"),
    sql_sum(when(col("gap_closed"), 1).otherwise(0)).alias("gaps_closed")
)

# Calculate rates
measure_performance = measure_performance.withColumn(
    "compliance_rate",
    sql_round(col("numerator") / col("denominator"), 3)
).withColumn(
    "gap_closure_rate",
    sql_round(
        when(col("gaps_identified") > 0, col("gaps_closed") / col("gaps_identified"))
        .otherwise(lit(0.0)),
        3
    )
).withColumn(
    "updated_at",
    current_timestamp()
).orderBy("measure_code", "measurement_year")

write_table(measure_performance, CATALOG, GOLD_SCHEMA, "measure_performance")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gap Closure Analytics

# COMMAND ----------

gaps = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.gap_tracking")

# Overall gap analytics
gap_analytics = gaps.groupBy("measure_code", "measure_name", "priority").agg(
    count("*").alias("total_gaps"),
    sql_sum(when(col("is_closed"), 1).otherwise(0)).alias("closed_gaps"),
    avg(when(col("is_closed"), col("days_to_close"))).alias("avg_days_to_close"),
    avg(col("num_attempts")).alias("avg_attempts"),
    sql_max(col("identified_date")).alias("most_recent_gap_date")
)

# Calculate closure rate
gap_analytics = gap_analytics.withColumn(
    "closure_rate",
    sql_round(col("closed_gaps") / col("total_gaps"), 3)
).withColumn(
    "avg_days_to_close",
    sql_round(col("avg_days_to_close"), 1)
).withColumn(
    "avg_attempts",
    sql_round(col("avg_attempts"), 1)
).withColumn(
    "updated_at",
    current_timestamp()
).orderBy(desc("total_gaps"))

write_table(gap_analytics, CATALOG, GOLD_SCHEMA, "gap_closure_analytics")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Quality Trends

# COMMAND ----------

scores = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.quality_scores")

# Enrich with year-over-year changes
window_spec = Window.orderBy("measurement_year")

quality_trends = scores.withColumn(
    "yoy_compliance_change",
    sql_round(
        col("overall_compliance_rate") - 
        coalesce(
            first(col("overall_compliance_rate")).over(
                window_spec.rowsBetween(Window.unboundedPreceding, Window.currentRow - 1)
            ),
            col("overall_compliance_rate")
        ),
        3
    )
).withColumn(
    "yoy_score_change",
    sql_round(
        col("quality_score") - 
        coalesce(
            first(col("quality_score")).over(
                window_spec.rowsBetween(Window.unboundedPreceding, Window.currentRow - 1)
            ),
            col("quality_score")
        ),
        1
    )
)

write_table(quality_trends, CATALOG, GOLD_SCHEMA, "quality_trends")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Open Gaps Dashboard View

# COMMAND ----------

# Create a view of current open gaps for dashboard
open_gaps_view = gaps.filter(
    (col("measurement_year") == current_year) & 
    ~col("is_closed")
)

# Join with member info
open_gaps_enriched = open_gaps_view.alias("g").join(
    members.alias("m"),
    col("g.member_id") == col("m.member_id")
).select(
    col("g.gap_id"),
    col("g.member_id"),
    col("m.first_name"),
    col("m.last_name"),
    col("m.age"),
    col("m.risk_level"),
    col("g.measure_code"),
    col("g.measure_name"),
    col("g.priority"),
    col("g.intervention_type"),
    col("g.num_attempts"),
    col("g.identified_date"),
    col("g.assigned_to"),
    col("g.notes"),
    current_timestamp().alias("updated_at")
).orderBy(
    when(col("g.priority") == "High", 1)
    .when(col("g.priority") == "Medium", 2)
    .otherwise(3),
    desc("g.identified_date")
)

write_table(open_gaps_enriched, CATALOG, GOLD_SCHEMA, "open_gaps_dashboard")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Gold Tables

# COMMAND ----------

verify_table(spark, CATALOG, GOLD_SCHEMA, "member_quality_summary")
verify_table(spark, CATALOG, GOLD_SCHEMA, "measure_performance")
verify_table(spark, CATALOG, GOLD_SCHEMA, "gap_closure_analytics")
verify_table(spark, CATALOG, GOLD_SCHEMA, "quality_trends")
verify_table(spark, CATALOG, GOLD_SCHEMA, "open_gaps_dashboard")

print("✅ Gold layer aggregation complete!")

