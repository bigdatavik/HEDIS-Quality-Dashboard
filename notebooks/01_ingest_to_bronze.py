# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze Layer: Ingest HEDIS Quality Data
# MAGIC
# MAGIC **Purpose:** Raw data ingestion for HEDIS quality measures
# MAGIC
# MAGIC **Creates:**
# MAGIC - `humana_quality.hedis_bronze.members_raw`
# MAGIC - `humana_quality.hedis_bronze.clinical_measures_raw`
# MAGIC - `humana_quality.hedis_bronze.gap_tracking_raw`
# MAGIC - `humana_quality.hedis_bronze.quality_scores_raw`

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

from pyspark.sql.functions import col, lit, current_timestamp
from datetime import datetime

from utils.table_helpers import (
    create_catalog_if_not_exists,
    create_schema_if_not_exists,
    write_table,
    verify_table
)
from data_generators.hedis_generator import HEDISDataGenerator

# COMMAND ----------

# Configuration
CATALOG = "humana_quality"
BRONZE_SCHEMA = "hedis_bronze"

# Data size (MEDIUM = 10K members)
NUM_MEMBERS = 10000

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Catalog and Schema

# COMMAND ----------

create_catalog_if_not_exists(spark, CATALOG)
create_schema_if_not_exists(spark, CATALOG, BRONZE_SCHEMA)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Synthetic HEDIS Data

# COMMAND ----------

print(f"🔄 Generating HEDIS data for {NUM_MEMBERS:,} members...")

generator = HEDISDataGenerator(num_members=NUM_MEMBERS, seed=42)

# Generate all data
print("  📊 Generating members...")
members = generator.generate_members()

print("  📊 Generating clinical measures...")
clinical_measures = generator.generate_clinical_measures(members)

print("  📊 Generating gap tracking...")
gap_tracking = generator.generate_gap_tracking(clinical_measures)

print("  📊 Generating quality scores...")
quality_scores = generator.generate_quality_scores()

print(f"✅ Generated:")
print(f"   - {len(members):,} members")
print(f"   - {len(clinical_measures):,} clinical measures")
print(f"   - {len(gap_tracking):,} gap records")
print(f"   - {len(quality_scores):,} quality score records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Bronze Tables

# COMMAND ----------

# Members
members_df = spark.createDataFrame(members)
write_table(members_df, CATALOG, BRONZE_SCHEMA, "members_raw")

# Clinical measures
measures_df = spark.createDataFrame(clinical_measures)
write_table(measures_df, CATALOG, BRONZE_SCHEMA, "clinical_measures_raw")

# Gap tracking
gaps_df = spark.createDataFrame(gap_tracking)
write_table(gaps_df, CATALOG, BRONZE_SCHEMA, "gap_tracking_raw")

# Quality scores
scores_df = spark.createDataFrame(quality_scores)
write_table(scores_df, CATALOG, BRONZE_SCHEMA, "quality_scores_raw")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Bronze Tables

# COMMAND ----------

verify_table(spark, CATALOG, BRONZE_SCHEMA, "members_raw")
verify_table(spark, CATALOG, BRONZE_SCHEMA, "clinical_measures_raw")
verify_table(spark, CATALOG, BRONZE_SCHEMA, "gap_tracking_raw")
verify_table(spark, CATALOG, BRONZE_SCHEMA, "quality_scores_raw")

print("✅ Bronze layer ingestion complete!")

