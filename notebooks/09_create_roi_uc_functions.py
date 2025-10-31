# Databricks notebook source
# MAGIC %md
# MAGIC # 09 - Create ROI & SDOH UC Functions
# MAGIC
# MAGIC **Purpose:** Create Unity Catalog functions for ROI calculations, SDOH queries, and cost analysis
# MAGIC
# MAGIC **Functions Created:**
# MAGIC 1. `calculate_gap_cost_impact` - Financial impact of member's gaps
# MAGIC 2. `identify_high_roi_members` - Best targets for gap closure
# MAGIC 3. `get_sdoh_risk_factors` - SDOH factors by ZIP code
# MAGIC 4. `members_in_high_risk_zips` - Members in high SDOH risk areas
# MAGIC 5. `calculate_roi_projection` - ROI for gap closure initiative
# MAGIC 6. `get_preventable_cost_by_zip` - Preventable costs by geography

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
    "calculate_gap_cost_impact",
    "identify_high_roi_members",
    "get_sdoh_risk_factors",
    "members_in_high_risk_zips",
    "calculate_roi_projection",
    "get_preventable_cost_by_zip"
]

for func in functions_to_drop:
    try:
        spark.sql(f"DROP FUNCTION IF EXISTS {CATALOG}.{GOLD_SCHEMA}.{func}")
        print(f"✅ Dropped function: {func}")
    except Exception as e:
        print(f"⚠️ Could not drop {func}: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 1: calculate_gap_cost_impact
# MAGIC Calculate financial impact of a member's open gaps

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.calculate_gap_cost_impact(input_member_id STRING)
RETURNS TABLE(
  member_id STRING,
  total_open_gaps INT,
  preventable_cost DOUBLE,
  preventable_er_visits INT,
  preventable_hospitalizations INT,
  avg_cost_per_event DOUBLE,
  potential_savings_if_closed DOUBLE,
  intervention_priority_score INT,
  intervention_priority_tier STRING
)
COMMENT 'Calculate financial impact of closing a member\\'s quality gaps. Returns preventable costs and ROI potential.'
RETURN 
  SELECT
    member_id,
    open_gaps AS total_open_gaps,
    preventable_cost,
    preventable_er_visits,
    preventable_hospitalizations,
    avg_cost_per_preventable_event AS avg_cost_per_event,
    potential_savings_if_gaps_closed,
    intervention_priority_score,
    intervention_priority_tier
  FROM {CATALOG}.{GOLD_SCHEMA}.preventable_cost_opportunity
  WHERE member_id = input_member_id;
""")

# Test
print("Testing calculate_gap_cost_impact...")
test_result = spark.sql(f"""
    SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.calculate_gap_cost_impact('M000001')
""").collect()
if test_result:
    row = test_result[0]
    print(f"✅ Function working: Member M000001 has {row['total_open_gaps']} gaps, ${row['preventable_cost']:.2f} preventable cost")
else:
    print("✅ Function created (no data for M000001)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 2: identify_high_roi_members
# MAGIC Find members where gap closure has highest financial impact

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.identify_high_roi_members()
RETURNS TABLE(
  member_id STRING,
  total_open_gaps INT,
  preventable_cost DOUBLE,
  potential_savings DOUBLE,
  intervention_priority_score INT,
  intervention_priority_tier STRING,
  clinical_risk_level STRING,
  sdoh_risk STRING
)
COMMENT 'Identify top members for gap closure interventions based on ROI potential. Returns members with highest preventable costs and intervention priority.'
RETURN 
  SELECT
    member_id,
    open_gaps AS total_open_gaps,
    preventable_cost,
    potential_savings_if_gaps_closed AS potential_savings,
    intervention_priority_score,
    intervention_priority_tier,
    clinical_risk_level,
    sdoh_risk
  FROM {CATALOG}.{GOLD_SCHEMA}.preventable_cost_opportunity
  WHERE intervention_priority_tier IN ('Critical', 'High')
  ORDER BY intervention_priority_score DESC
  LIMIT 100;
""")

# Test
print("Testing identify_high_roi_members...")
test_result = spark.sql(f"""
    SELECT COUNT(*) as count FROM {CATALOG}.{GOLD_SCHEMA}.identify_high_roi_members()
""").collect()
print(f"✅ Function working: Found {test_result[0]['count']} high-ROI members")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 3: get_sdoh_risk_factors
# MAGIC Get social determinants of health factors for a ZIP code

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.get_sdoh_risk_factors(input_zip_code STRING)
RETURNS TABLE(
  zip_code STRING,
  median_household_income INT,
  poverty_rate DOUBLE,
  unemployment_rate DOUBLE,
  overall_svi_score DOUBLE,
  svi_percentile INT,
  vulnerability_level STRING,
  adi_score INT,
  disadvantage_level STRING,
  is_food_desert BOOLEAN,
  is_provider_desert BOOLEAN,
  has_public_transport BOOLEAN,
  pcp_per_1000_residents DOUBLE,
  composite_risk_score INT,
  sdoh_risk_classification STRING
)
COMMENT 'Get social determinants of health (SDOH) risk factors for a ZIP code. Includes poverty, SVI, ADI, and access barriers.'
RETURN 
  SELECT
    zip_code,
    median_household_income,
    poverty_rate,
    unemployment_rate,
    overall_svi_score,
    svi_percentile,
    vulnerability_level,
    adi_score,
    disadvantage_level,
    is_food_desert,
    is_provider_desert,
    has_public_transport,
    pcp_per_1000_residents,
    composite_risk_score,
    sdoh_risk_classification
  FROM {CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary
  WHERE zip_code = input_zip_code;
""")

# Test - get a ZIP from members table
test_zip = spark.sql(f"SELECT zip_code FROM {CATALOG}.{SILVER_SCHEMA}.members LIMIT 1").collect()[0]['zip_code']
print(f"Testing get_sdoh_risk_factors with ZIP: {test_zip}...")
test_result = spark.sql(f"""
    SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.get_sdoh_risk_factors('{test_zip}')
""").collect()
if test_result:
    row = test_result[0]
    print(f"✅ Function working: ZIP {test_zip} has SVI {row['svi_percentile']}th percentile, {row['sdoh_risk_classification']}")
else:
    print("✅ Function created (no SDOH data for test ZIP)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 4: members_in_high_risk_zips
# MAGIC Find members living in high SDOH risk areas

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.members_in_high_risk_zips()
RETURNS TABLE(
  member_id STRING,
  first_name STRING,
  last_name STRING,
  zip_code STRING,
  sdoh_risk_classification STRING,
  vulnerability_level STRING,
  poverty_rate DOUBLE,
  is_food_desert BOOLEAN,
  is_provider_desert BOOLEAN,
  open_gaps INT,
  compliance_rate DOUBLE
)
COMMENT 'Find members living in high SDOH risk areas. Useful for targeted outreach and mobile clinic planning.'
RETURN 
  SELECT
    member_id,
    first_name,
    last_name,
    zip_code,
    sdoh_risk_classification,
    vulnerability_level,
    poverty_rate,
    is_food_desert,
    is_provider_desert,
    open_gaps,
    compliance_rate
  FROM {CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched
  WHERE sdoh_risk_classification = 'High Risk'
  ORDER BY open_gaps DESC;
""")

# Test
print("Testing members_in_high_risk_zips...")
test_result = spark.sql(f"""
    SELECT COUNT(*) as count FROM {CATALOG}.{GOLD_SCHEMA}.members_in_high_risk_zips()
""").collect()
print(f"✅ Function working: Found {test_result[0]['count']} members in high-risk ZIPs")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 5: calculate_roi_projection
# MAGIC Calculate ROI for a gap closure initiative

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.calculate_roi_projection(
  closure_rate_pct DOUBLE
)
RETURNS TABLE(
  closure_rate_pct DOUBLE,
  total_open_gaps INT,
  projected_gaps_closed INT,
  projected_savings DOUBLE,
  avg_savings_per_gap DOUBLE
)
COMMENT 'Calculate ROI projection for gap closure initiative at different closure rates. Input closure_rate_pct as decimal (e.g., 0.70 for 70%).'
RETURN 
  SELECT
    closure_rate_pct,
    total_open_gaps,
    CAST(total_open_gaps * closure_rate_pct AS INT) AS projected_gaps_closed,
    CASE 
      WHEN closure_rate_pct >= 0.70 THEN projected_savings_70pct_closure
      WHEN closure_rate_pct >= 0.50 THEN projected_savings_50pct_closure
      WHEN closure_rate_pct >= 0.30 THEN projected_savings_30pct_closure
      ELSE projected_savings_30pct_closure * (closure_rate_pct / 0.30)
    END AS projected_savings,
    avg_savings_per_gap_closed AS avg_savings_per_gap
  FROM {CATALOG}.{GOLD_SCHEMA}.gap_closure_roi_projections;
""")

# Test
print("Testing calculate_roi_projection...")
test_result = spark.sql(f"""
    SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.calculate_roi_projection(0.70)
""").collect()
if test_result:
    row = test_result[0]
    print(f"✅ Function working: 70% closure = {row['projected_gaps_closed']} gaps, ${row['projected_savings']:,.2f} savings")
else:
    print("✅ Function created (no projection data)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Function 6: get_preventable_cost_by_zip
# MAGIC Get preventable costs aggregated by ZIP code

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{GOLD_SCHEMA}.get_preventable_cost_by_zip()
RETURNS TABLE(
  zip_code STRING,
  city STRING,
  latitude DOUBLE,
  longitude DOUBLE,
  active_members INT,
  total_open_gaps INT,
  total_preventable_cost DOUBLE,
  avg_preventable_cost_per_member DOUBLE,
  sdoh_risk_classification STRING,
  mobile_clinic_priority_score INT,
  mobile_clinic_priority_tier STRING
)
COMMENT 'Get preventable costs by ZIP code for geographic targeting. Returns hotspots for mobile clinic deployment.'
RETURN 
  SELECT
    zip_code,
    city,
    latitude,
    longitude,
    active_members,
    total_open_gaps,
    total_preventable_cost,
    ROUND(total_preventable_cost / NULLIF(active_members, 0), 2) AS avg_preventable_cost_per_member,
    sdoh_risk_classification,
    mobile_clinic_priority_score,
    mobile_clinic_priority_tier
  FROM {CATALOG}.{GOLD_SCHEMA}.gap_hotspots
  ORDER BY mobile_clinic_priority_score DESC;
""")

# Test
print("Testing get_preventable_cost_by_zip...")
test_result = spark.sql(f"""
    SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.get_preventable_cost_by_zip() LIMIT 5
""")
count = test_result.count()
print(f"✅ Function working: Found {count} ZIPs with preventable costs")
if count > 0:
    test_result.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify All Functions

# COMMAND ----------

# List all functions in schema
functions_df = spark.sql(f"""
    SELECT routine_name, routine_type, routine_definition
    FROM information_schema.routines
    WHERE routine_catalog = '{CATALOG}'
        AND routine_schema = '{GOLD_SCHEMA}'
        AND routine_name IN (
            'calculate_gap_cost_impact',
            'identify_high_roi_members',
            'get_sdoh_risk_factors',
            'members_in_high_risk_zips',
            'calculate_roi_projection',
            'get_preventable_cost_by_zip'
        )
    ORDER BY routine_name
""")

print("="*80)
print("ROI & SDOH UC FUNCTIONS CREATED")
print("="*80)
print(f"\n✅ Created {functions_df.count()} UC Functions in {CATALOG}.{GOLD_SCHEMA}:")
print("")
functions_df.select("routine_name").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Usage Examples

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 1: Find High-ROI Members

# COMMAND ----------

print("Example 1: Top 10 members for gap closure (highest ROI)")
spark.sql(f"""
    SELECT 
        member_id, 
        total_open_gaps,
        preventable_cost,
        potential_savings,
        intervention_priority_tier
    FROM {CATALOG}.{GOLD_SCHEMA}.identify_high_roi_members()
    LIMIT 10
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 2: Get SDOH Risk Factors for a ZIP

# COMMAND ----------

# Get a sample ZIP
sample_zip = spark.sql(f"""
    SELECT zip_code 
    FROM {CATALOG}.{GOLD_SCHEMA}.gap_hotspots 
    ORDER BY mobile_clinic_priority_score DESC 
    LIMIT 1
""").collect()[0]['zip_code']

print(f"Example 2: SDOH Risk Factors for ZIP {sample_zip} (highest priority hotspot)")
spark.sql(f"""
    SELECT 
        zip_code,
        poverty_rate,
        svi_percentile,
        vulnerability_level,
        is_food_desert,
        is_provider_desert,
        sdoh_risk_classification
    FROM {CATALOG}.{GOLD_SCHEMA}.get_sdoh_risk_factors('{sample_zip}')
""").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 3: Calculate ROI at Different Closure Rates

# COMMAND ----------

print("Example 3: ROI Projections at 30%, 50%, 70% closure rates")
spark.sql(f"""
    SELECT 
        CAST(closure_rate_pct * 100 AS INT) AS closure_rate_pct,
        projected_gaps_closed,
        ROUND(projected_savings, 2) AS projected_savings,
        ROUND(avg_savings_per_gap, 2) AS avg_savings_per_gap
    FROM {CATALOG}.{GOLD_SCHEMA}.calculate_roi_projection(0.30)
    UNION ALL
    SELECT 
        CAST(closure_rate_pct * 100 AS INT),
        projected_gaps_closed,
        ROUND(projected_savings, 2),
        ROUND(avg_savings_per_gap, 2)
    FROM {CATALOG}.{GOLD_SCHEMA}.calculate_roi_projection(0.50)
    UNION ALL
    SELECT 
        CAST(closure_rate_pct * 100 AS INT),
        projected_gaps_closed,
        ROUND(projected_savings, 2),
        ROUND(avg_savings_per_gap, 2)
    FROM {CATALOG}.{GOLD_SCHEMA}.calculate_roi_projection(0.70)
    ORDER BY closure_rate_pct
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 4: Top Geographic Hotspots

# COMMAND ----------

print("Example 4: Top 10 ZIPs for mobile clinic deployment")
spark.sql(f"""
    SELECT 
        zip_code,
        city,
        active_members,
        total_open_gaps,
        total_preventable_cost,
        mobile_clinic_priority_tier
    FROM {CATALOG}.{GOLD_SCHEMA}.get_preventable_cost_by_zip()
    LIMIT 10
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("="*80)
print("✅ ALL ROI & SDOH UC FUNCTIONS CREATED AND TESTED")
print("="*80)
print("\nFunctions available for MCP integration:")
print("  1. calculate_gap_cost_impact(member_id)")
print("  2. identify_high_roi_members()")
print("  3. get_sdoh_risk_factors(zip_code)")
print("  4. members_in_high_risk_zips()")
print("  5. calculate_roi_projection(closure_rate_pct)")
print("  6. get_preventable_cost_by_zip()")
print("\n✅ Ready for Genie Space and MCP integration!")
print("="*80)

