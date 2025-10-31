# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - Upload Knowledge Documents for MCP
# MAGIC
# MAGIC **Purpose:** Upload HEDIS knowledge documents from bundle to Unity Catalog volume
# MAGIC
# MAGIC **Creates:**
# MAGIC - Volume: `humana_quality.hedis_gold.knowledge_docs`
# MAGIC - Uploads 4 knowledge documents for Knowledge Assistant

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

import sys
import os

# Get current user dynamically
username = spark.conf.get("spark.databricks.workspaceUrl").split("@")[0] if "@" in spark.conf.get("spark.databricks.workspaceUrl") else "vik.malhotra@databricks.com"
bundle_name = "hedis_quality_dashboard"
target = "dev"

# Construct dynamic paths
src_path = f"/Workspace/Users/{username}/.bundle/{bundle_name}/{target}/files/src"
data_path = f"/Workspace/Users/{username}/.bundle/{bundle_name}/{target}/files/data/knowledge_content"

sys.path.append(src_path)

print(f"✅ Source path: {src_path}")
print(f"✅ Knowledge content path: {data_path}")

# COMMAND ----------

from utils.table_helpers import create_volume_if_not_exists

# Configuration
CATALOG = "humana_quality"
SCHEMA = "hedis_gold"
VOLUME = "knowledge_docs"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Volume

# COMMAND ----------

create_volume_if_not_exists(spark, CATALOG, SCHEMA, VOLUME)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Upload Knowledge Documents

# COMMAND ----------

# Volume path
volume_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

# List of knowledge files to upload (all 8 documents)
knowledge_files = [
    # Original 4 documents
    "gap_closure_protocols.txt",
    "hedis_measures_guide.txt",
    "ncqa_quality_guidelines.txt",
    "quality_team_communications.txt",
    # New 4 documents (SDOH + ROI enhancement)
    "cms_health_equity_guidelines.txt",
    "value_based_care_best_practices.txt",
    "social_needs_screening.txt",
    "roi_calculation_methods.txt"
]

print(f"📤 Uploading knowledge documents to: {volume_path}\n")

# Upload each file
for filename in knowledge_files:
    try:
        # Read file content from bundle workspace location
        source_path = f"{data_path}/{filename}"
        content = dbutils.fs.head(source_path, maxBytes=10000000)  # 10MB max
        
        # Write to volume
        target_path = f"{volume_path}/{filename}"
        dbutils.fs.put(target_path, content, overwrite=True)
        
        print(f"✅ Uploaded: {filename}")
    except Exception as e:
        print(f"❌ Error uploading {filename}: {e}")

print("\n✅ Knowledge documents upload complete!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Uploads

# COMMAND ----------

# List all files in volume
files = dbutils.fs.ls(volume_path)

print(f"\n📂 Files in {volume_path}:\n")
for file in files:
    size_kb = file.size / 1024
    print(f"  ✓ {file.name} ({size_kb:.1f} KB)")

print(f"\n✅ Total files uploaded: {len(files)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC Now that knowledge documents are uploaded to the UC Volume:
# MAGIC
# MAGIC 1. **Create Knowledge Assistant Endpoint** - See `data/setup_guides/KNOWLEDGE_ASSISTANT_UI_FIELDS.md`
# MAGIC 2. **Configure Genie Space** - See `data/setup_guides/GENIE_INSTRUCTIONS.md`
# MAGIC 3. **Update MCP Config** - Update `/dashboard/config.py` with endpoint IDs
# MAGIC 4. **Test Integration** - Test MCP Search in the dashboard
# MAGIC
# MAGIC Full setup guide: `data/setup_guides/QUICK_SETUP_GUIDE.md`
