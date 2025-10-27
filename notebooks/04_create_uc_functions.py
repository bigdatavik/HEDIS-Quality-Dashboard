# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Create Unity Catalog Functions for MCP
# MAGIC
# MAGIC **Purpose:** Create UC functions for natural language queries via MCP
# MAGIC
# MAGIC **Functions Created:**
# MAGIC - `lookup_member` - Get member demographics and quality summary
# MAGIC - `lookup_member_measures` - Get all measures for a member
# MAGIC - `lookup_member_gaps` - Get open gaps for a member
# MAGIC - `members_with_gap` - Find members with specific gap
# MAGIC - `lookup_measure_performance` - Get performance by measure
# MAGIC - `members_at_risk` - Get members with low compliance

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Configuration
CATALOG = "humana_quality"
GOLD_SCHEMA = "hedis_gold"
SILVER_SCHEMA = "hedis_silver"

# Set current catalog
spark.sql(f"USE CATALOG {CATALOG}")
print(f"✅ Using catalog: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Drop Existing Functions (for clean redeployment)

# COMMAND ----------

functions_to_drop = [
    "lookup_member",
    "lookup_member_measures",
    "lookup_member_gaps",
    "members_with_gap",
    "lookup_measure_performance",
    "members_at_risk"
]

for func in functions_to_drop:
    try:
        spark.sql(f"DROP FUNCTION IF EXISTS {CATALOG}.{GOLD_SCHEMA}.{func}")
        print(f"✅ Dropped function: {func}")
    except Exception as e:
        print(f"⚠️ Could not drop {func}: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 1: lookup_member
# MAGIC Get member demographics and quality summary

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.lookup_member(input_member_id STRING)
RETURNS TABLE(
  member_id STRING,
  first_name STRING,
  last_name STRING,
  age INT,
  gender STRING,
  risk_level STRING,
  is_active BOOLEAN,
  total_measures INT,
  compliant_measures INT,
  open_gaps INT,
  compliance_rate DOUBLE
)
COMMENT 'Lookup member demographics and quality summary. Use this to get details about a specific member by ID.'
RETURN 
  SELECT 
    member_id,
    first_name,
    last_name,
    age,
    gender,
    risk_level,
    is_active,
    total_measures,
    compliant_measures,
    open_gaps,
    compliance_rate
  FROM {CATALOG}.{GOLD_SCHEMA}.member_quality_summary
  WHERE member_id = input_member_id;
""")

# Test
print("Testing lookup_member...")
test_result = spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.lookup_member('M000001')").collect()
if test_result:
    print(f"✅ lookup_member working: {test_result[0]['first_name']} {test_result[0]['last_name']}")
else:
    print("⚠️ No results from lookup_member test")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 2: lookup_member_measures
# MAGIC Get all clinical measures for a member

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.lookup_member_measures(input_member_id STRING)
RETURNS TABLE(
  measure_id STRING,
  measure_code STRING,
  measure_name STRING,
  measurement_year INT,
  is_compliant BOOLEAN,
  service_date DATE,
  has_gap BOOLEAN
)
COMMENT 'Get all clinical quality measures for a specific member. Shows compliance status and gaps.'
RETURN 
  SELECT 
    measure_id,
    measure_code,
    measure_name,
    measurement_year,
    is_compliant,
    service_date,
    has_gap
  FROM {CATALOG}.{SILVER_SCHEMA}.clinical_measures
  WHERE member_id = input_member_id
  ORDER BY measurement_year DESC, measure_code;
""")

# Test
print("Testing lookup_member_measures...")
test_result = spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.lookup_member_measures('M000001')").collect()
print(f"✅ lookup_member_measures working: {len(test_result)} measures found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 3: lookup_member_gaps
# MAGIC Get open gaps for a member

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.lookup_member_gaps(input_member_id STRING)
RETURNS TABLE(
  gap_id STRING,
  measure_code STRING,
  measure_name STRING,
  priority STRING,
  intervention_type STRING,
  num_attempts INT,
  identified_date DATE,
  assigned_to STRING
)
COMMENT 'Get open gaps in care for a specific member. Use this to see what quality measures need attention.'
RETURN 
  SELECT 
    gap_id,
    measure_code,
    measure_name,
    priority,
    intervention_type,
    num_attempts,
    identified_date,
    assigned_to
  FROM {CATALOG}.{GOLD_SCHEMA}.open_gaps_dashboard
  WHERE member_id = input_member_id
  ORDER BY 
    CASE 
      WHEN priority = 'High' THEN 1
      WHEN priority = 'Medium' THEN 2
      ELSE 3
    END,
    identified_date DESC;
""")

# Test
print("Testing lookup_member_gaps...")
test_result = spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.lookup_member_gaps('M000001')").collect()
print(f"✅ lookup_member_gaps working: {len(test_result)} open gaps")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 4: members_with_gap
# MAGIC Find members with a specific gap

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.members_with_gap(input_measure_code STRING)
RETURNS TABLE(
  member_id STRING,
  first_name STRING,
  last_name STRING,
  age INT,
  risk_level STRING,
  measure_name STRING,
  priority STRING,
  num_attempts INT
)
COMMENT 'Find all members with an open gap for a specific HEDIS measure (e.g., BCS, CDC, CBP).'
RETURN 
  SELECT 
    member_id,
    first_name,
    last_name,
    age,
    risk_level,
    measure_name,
    priority,
    num_attempts
  FROM {CATALOG}.{GOLD_SCHEMA}.open_gaps_dashboard
  WHERE measure_code = input_measure_code
  ORDER BY 
    CASE 
      WHEN priority = 'High' THEN 1
      WHEN priority = 'Medium' THEN 2
      ELSE 3
    END,
    last_name, first_name;
""")

# Test
print("Testing members_with_gap...")
test_result = spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.members_with_gap('BCS')").collect()
print(f"✅ members_with_gap working: {len(test_result)} members with BCS gap")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 5: lookup_measure_performance
# MAGIC Get performance metrics by measure

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.lookup_measure_performance(input_measure_code STRING)
RETURNS TABLE(
  measure_code STRING,
  measure_name STRING,
  measurement_year INT,
  denominator BIGINT,
  numerator BIGINT,
  compliance_rate DOUBLE,
  gaps_identified BIGINT,
  gaps_closed BIGINT,
  gap_closure_rate DOUBLE
)
COMMENT 'Get performance trends for a specific HEDIS measure across years.'
RETURN 
  SELECT 
    measure_code,
    measure_name,
    measurement_year,
    denominator,
    numerator,
    compliance_rate,
    gaps_identified,
    gaps_closed,
    gap_closure_rate
  FROM {CATALOG}.{GOLD_SCHEMA}.measure_performance
  WHERE measure_code = input_measure_code
  ORDER BY measurement_year DESC;
""")

# Test
print("Testing lookup_measure_performance...")
test_result = spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.lookup_measure_performance('CDC')").collect()
print(f"✅ lookup_measure_performance working: {len(test_result)} years of data")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 6: members_at_risk
# MAGIC Get members with low compliance rates

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.members_at_risk()
RETURNS TABLE(
  member_id STRING,
  first_name STRING,
  last_name STRING,
  age INT,
  risk_level STRING,
  total_measures INT,
  compliant_measures INT,
  open_gaps INT,
  compliance_rate DOUBLE
)
COMMENT 'Get members with low quality compliance rates (< 70%). Use for outreach prioritization.'
RETURN 
  SELECT 
    member_id,
    first_name,
    last_name,
    age,
    risk_level,
    total_measures,
    compliant_measures,
    open_gaps,
    compliance_rate
  FROM {CATALOG}.{GOLD_SCHEMA}.member_quality_summary
  WHERE compliance_rate < 0.70 AND total_measures > 0
  ORDER BY compliance_rate ASC, open_gaps DESC
  LIMIT 100;
""")

# Test
print("Testing members_at_risk...")
test_result = spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.members_at_risk()").collect()
print(f"✅ members_at_risk working: {len(test_result)} at-risk members")

# COMMAND ----------

# MAGIC %md
# MAGIC ## List All Functions

# COMMAND ----------

functions_df = spark.sql(f"""
  SHOW USER FUNCTIONS IN {GOLD_SCHEMA}
""")

print("✅ Created UC Functions:")
for row in functions_df.collect():
    print(f"   - {row['function']}")

print("\n✅ All UC functions created successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Grant EXECUTE Permissions to All Users
# MAGIC
# MAGIC **⚠️ CRITICAL for MCP Integration:**
# MAGIC - MCP agents need EXECUTE permissions to call UC Functions
# MAGIC - Without this, queries will fail with "Permission denied" errors
# MAGIC - Grants to 'account users' group (includes all users and service principals)

# COMMAND ----------

print("🔧 Granting EXECUTE permissions on UC Functions...")

function_names = [
    "lookup_member",
    "lookup_member_measures",
    "lookup_member_gaps",
    "members_with_gap",
    "lookup_measure_performance",
    "members_at_risk"
]

for func_name in function_names:
    full_name = f"{CATALOG}.{GOLD_SCHEMA}.{func_name}"
    
    try:
        # Grant EXECUTE to all users
        spark.sql(f"GRANT EXECUTE ON FUNCTION {full_name} TO `account users`")
        print(f"✅ {func_name}: Granted EXECUTE to 'account users'")
    except Exception as e:
        print(f"⚠️ {func_name}: {e}")

print("\n✅ All UC Functions have EXECUTE permissions!")
print("✅ MCP agents can now call these functions without permission errors!")

