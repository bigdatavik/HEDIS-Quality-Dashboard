# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver Layer: Clean and Validate HEDIS Data
# MAGIC
# MAGIC **Purpose:** Clean, deduplicate, and validate quality measures data
# MAGIC
# MAGIC **Creates:**
# MAGIC - `humana_quality.hedis_silver.members`
# MAGIC - `humana_quality.hedis_silver.clinical_measures`
# MAGIC - `humana_quality.hedis_silver.gap_tracking`
# MAGIC - `humana_quality.hedis_silver.quality_scores`

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
    trim, upper, lower, regexp_replace,
    row_number, desc, datediff
)
from pyspark.sql.window import Window

from utils.table_helpers import (
    create_schema_if_not_exists,
    write_table,
    verify_table
)
from utils.dataframe_validation import (
    validate_dataframe,
    assert_no_duplicate_columns
)

# COMMAND ----------

# Configuration
CATALOG = "humana_quality"
BRONZE_SCHEMA = "hedis_bronze"
SILVER_SCHEMA = "hedis_silver"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Silver Schema

# COMMAND ----------

create_schema_if_not_exists(spark, CATALOG, SILVER_SCHEMA)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clean Members Data

# COMMAND ----------

members_raw = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.members_raw")
print(f"📊 Bronze members: {members_raw.count():,} rows")

# Clean and standardize
members_clean = members_raw.select(
    col("member_id"),
    trim(col("first_name")).alias("first_name"),
    trim(col("last_name")).alias("last_name"),
    col("date_of_birth"),
    col("age"),
    upper(col("gender")).alias("gender"),
    col("enrollment_date"),
    col("is_active"),
    col("risk_level"),
    trim(col("address")).alias("address"),
    trim(col("city")).alias("city"),
    upper(col("state")).alias("state"),
    regexp_replace(col("zip_code"), "[^0-9]", "").alias("zip_code"),
    regexp_replace(col("phone"), "[^0-9]", "").alias("phone"),
    lower(trim(col("email"))).alias("email"),
    current_timestamp().alias("updated_at"),
    col("source_system")
)

# Deduplicate (keep most recent)
window_spec = Window.partitionBy("member_id").orderBy(desc("updated_at"))
members_clean = members_clean.withColumn("row_num", row_number().over(window_spec))
members_clean = members_clean.filter(col("row_num") == 1).drop("row_num")

# Validate
validate_dataframe(
    members_clean,
    expected_cols=["member_id", "first_name", "last_name", "age"],
    df_name="members_clean"
)

write_table(members_clean, CATALOG, SILVER_SCHEMA, "members")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clean Clinical Measures Data

# COMMAND ----------

measures_raw = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.clinical_measures_raw")
print(f"📊 Bronze measures: {measures_raw.count():,} rows")

# Clean and standardize
measures_clean = measures_raw.select(
    col("measure_id"),
    col("member_id"),
    upper(trim(col("measure_code"))).alias("measure_code"),
    trim(col("measure_name")).alias("measure_name"),
    col("measurement_year"),
    col("is_compliant").cast("boolean"),
    col("service_date"),
    col("has_gap").cast("boolean"),
    col("gap_closed").cast("boolean"),
    col("gap_closure_date"),
    col("numerator").cast("int"),
    col("denominator").cast("int"),
    current_timestamp().alias("updated_at"),
    col("source_system")
)

# Deduplicate
window_spec = Window.partitionBy("measure_id").orderBy(desc("updated_at"))
measures_clean = measures_clean.withColumn("row_num", row_number().over(window_spec))
measures_clean = measures_clean.filter(col("row_num") == 1).drop("row_num")

# Validate
validate_dataframe(
    measures_clean,
    expected_cols=["measure_id", "member_id", "measure_code"],
    df_name="measures_clean"
)

write_table(measures_clean, CATALOG, SILVER_SCHEMA, "clinical_measures")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clean Gap Tracking Data

# COMMAND ----------

gaps_raw = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.gap_tracking_raw")
print(f"📊 Bronze gaps: {gaps_raw.count():,} rows")

# Clean and standardize
gaps_clean = gaps_raw.select(
    col("gap_id"),
    col("member_id"),
    upper(trim(col("measure_code"))).alias("measure_code"),
    trim(col("measure_name")).alias("measure_name"),
    col("measurement_year"),
    col("identified_date"),
    col("priority"),
    trim(col("intervention_type")).alias("intervention_type"),
    col("num_attempts").cast("int"),
    col("is_closed").cast("boolean"),
    col("closure_date"),
    col("days_to_close").cast("int"),
    trim(col("assigned_to")).alias("assigned_to"),
    trim(col("notes")).alias("notes"),
    current_timestamp().alias("updated_at"),
    col("source_system")
)

# Deduplicate
window_spec = Window.partitionBy("gap_id").orderBy(desc("updated_at"))
gaps_clean = gaps_clean.withColumn("row_num", row_number().over(window_spec))
gaps_clean = gaps_clean.filter(col("row_num") == 1).drop("row_num")

# Validate
validate_dataframe(
    gaps_clean,
    expected_cols=["gap_id", "member_id", "measure_code"],
    df_name="gaps_clean"
)

write_table(gaps_clean, CATALOG, SILVER_SCHEMA, "gap_tracking")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clean Quality Scores Data

# COMMAND ----------

scores_raw = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.quality_scores_raw")
print(f"📊 Bronze scores: {scores_raw.count():,} rows")

# Clean and standardize
scores_clean = scores_raw.select(
    col("measurement_year"),
    col("overall_compliance_rate").cast("double"),
    col("quality_score").cast("double"),
    col("stars_rating").cast("double"),
    col("total_measures").cast("int"),
    col("members_compliant").cast("int"),
    col("total_members").cast("int"),
    col("gap_closure_rate").cast("double"),
    col("ncqa_percentile").cast("int"),
    current_timestamp().alias("updated_at")
)

# Deduplicate
window_spec = Window.partitionBy("measurement_year").orderBy(desc("updated_at"))
scores_clean = scores_clean.withColumn("row_num", row_number().over(window_spec))
scores_clean = scores_clean.filter(col("row_num") == 1).drop("row_num")

# Validate
validate_dataframe(
    scores_clean,
    expected_cols=["measurement_year", "overall_compliance_rate"],
    df_name="scores_clean"
)

write_table(scores_clean, CATALOG, SILVER_SCHEMA, "quality_scores")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Silver Tables

# COMMAND ----------

verify_table(spark, CATALOG, SILVER_SCHEMA, "members")
verify_table(spark, CATALOG, SILVER_SCHEMA, "clinical_measures")
verify_table(spark, CATALOG, SILVER_SCHEMA, "gap_tracking")
verify_table(spark, CATALOG, SILVER_SCHEMA, "quality_scores")

print("✅ Silver layer transformation complete!")

