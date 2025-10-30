# Databricks notebook source
# MAGIC %md
# MAGIC # 06 - Integrate SDOH (Social Determinants of Health) Data
# MAGIC
# MAGIC **Purpose:** Enrich member data with social determinants of health factors
# MAGIC
# MAGIC **Data Sources:**
# MAGIC - Census demographics by ZIP code
# MAGIC - CDC Social Vulnerability Index (SVI)
# MAGIC - Area Deprivation Index (ADI)
# MAGIC - Food desert indicators
# MAGIC - Provider density
# MAGIC
# MAGIC **Medallion Architecture:**
# MAGIC - Bronze: Raw SDOH data by ZIP
# MAGIC - Silver: Validated and enriched SDOH
# MAGIC - Gold: Member-level SDOH enrichment + ZIP aggregations

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Imports
from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import datetime
import random

# Configuration
CATALOG = "humana_quality"
BRONZE_SCHEMA = "hedis_bronze"
SILVER_SCHEMA = "hedis_silver"
GOLD_SCHEMA = "hedis_gold"

# Set catalog
spark.sql(f"USE CATALOG {CATALOG}")
print(f"✅ Using catalog: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Synthetic SDOH Data
# MAGIC
# MAGIC Simulating data that would come from:
# MAGIC - Census Bureau API
# MAGIC - CDC Social Vulnerability Index
# MAGIC - University of Wisconsin Area Deprivation Index

# COMMAND ----------

# Get unique ZIP codes from existing member data
zip_codes_df = spark.sql(f"""
    SELECT DISTINCT zip_code
    FROM {CATALOG}.{SILVER_SCHEMA}.members
    WHERE zip_code IS NOT NULL
""")

zip_codes = [row.zip_code for row in zip_codes_df.collect()]
print(f"Found {len(zip_codes)} unique ZIP codes")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Census Demographics Data

# COMMAND ----------

# Generate synthetic census data
census_data = []

for zip_code in zip_codes:
    # Base demographics on ZIP code (deterministic based on ZIP)
    seed = int(zip_code) % 1000
    random.seed(seed)
    
    # Population metrics
    total_population = random.randint(5000, 50000)
    population_65_plus = int(total_population * random.uniform(0.12, 0.25))
    
    # Economic metrics
    median_household_income = random.randint(30000, 150000)
    poverty_rate = max(0.05, min(0.45, 0.50 - (median_household_income / 300000)))
    unemployment_rate = max(0.03, min(0.20, 0.25 - (median_household_income / 400000)))
    
    # Education
    high_school_grad_rate = max(0.70, min(0.98, 0.60 + (median_household_income / 250000)))
    bachelors_degree_rate = max(0.10, min(0.60, 0.05 + (median_household_income / 200000)))
    
    # Housing
    median_home_value = median_household_income * random.uniform(2.5, 4.0)
    renter_occupied_pct = max(0.20, min(0.70, 0.80 - (median_household_income / 200000)))
    
    census_data.append({
        'zip_code': zip_code,
        'total_population': total_population,
        'population_65_plus': population_65_plus,
        'median_household_income': median_household_income,
        'poverty_rate': round(poverty_rate, 3),
        'unemployment_rate': round(unemployment_rate, 3),
        'high_school_grad_rate': round(high_school_grad_rate, 3),
        'bachelors_degree_rate': round(bachelors_degree_rate, 3),
        'median_home_value': int(median_home_value),
        'renter_occupied_pct': round(renter_occupied_pct, 3),
        'data_year': 2023,
        'created_at': datetime.now(),
        'source_system': 'CENSUS_BUREAU_API'
    })

census_schema = StructType([
    StructField("zip_code", StringType(), False),
    StructField("total_population", IntegerType(), True),
    StructField("population_65_plus", IntegerType(), True),
    StructField("median_household_income", IntegerType(), True),
    StructField("poverty_rate", DoubleType(), True),
    StructField("unemployment_rate", DoubleType(), True),
    StructField("high_school_grad_rate", DoubleType(), True),
    StructField("bachelors_degree_rate", DoubleType(), True),
    StructField("median_home_value", IntegerType(), True),
    StructField("renter_occupied_pct", DoubleType(), True),
    StructField("data_year", IntegerType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("source_system", StringType(), True)
])

census_df = spark.createDataFrame(census_data, schema=census_schema)
print(f"✅ Generated census data for {census_df.count()} ZIP codes")
census_df.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate CDC Social Vulnerability Index (SVI)

# COMMAND ----------

# CDC SVI: Composite score from 15 social factors
svi_data = []

for zip_code in zip_codes:
    seed = int(zip_code) % 1000
    random.seed(seed)
    
    # Get census data for this ZIP
    census_row = [c for c in census_data if c['zip_code'] == zip_code][0]
    
    # SVI Theme 1: Socioeconomic Status (poverty, unemployment, income, education)
    theme1_score = (
        census_row['poverty_rate'] * 0.4 +
        census_row['unemployment_rate'] * 0.3 +
        (1 - census_row['high_school_grad_rate']) * 0.3
    )
    
    # SVI Theme 2: Household Composition (age, disability, single parent)
    theme2_score = random.uniform(0.2, 0.7)
    
    # SVI Theme 3: Minority Status & Language (minority %, limited English)
    theme3_score = random.uniform(0.1, 0.6)
    
    # SVI Theme 4: Housing Type & Transportation (multi-unit, mobile homes, crowding, no vehicle)
    theme4_score = (
        census_row['renter_occupied_pct'] * 0.5 +
        random.uniform(0.1, 0.4) * 0.5
    )
    
    # Overall SVI (0-1, higher = more vulnerable)
    overall_svi = (theme1_score + theme2_score + theme3_score + theme4_score) / 4
    
    # Percentile rank (0-100, higher = more vulnerable)
    svi_percentile = int(overall_svi * 100)
    
    # Classification
    if svi_percentile >= 75:
        vulnerability_level = 'High'
    elif svi_percentile >= 50:
        vulnerability_level = 'Moderate'
    elif svi_percentile >= 25:
        vulnerability_level = 'Low'
    else:
        vulnerability_level = 'Very Low'
    
    svi_data.append({
        'zip_code': zip_code,
        'overall_svi_score': round(overall_svi, 3),
        'svi_percentile': svi_percentile,
        'vulnerability_level': vulnerability_level,
        'theme1_socioeconomic': round(theme1_score, 3),
        'theme2_household': round(theme2_score, 3),
        'theme3_minority_language': round(theme3_score, 3),
        'theme4_housing_transport': round(theme4_score, 3),
        'data_year': 2023,
        'created_at': datetime.now(),
        'source_system': 'CDC_SVI_API'
    })

svi_schema = StructType([
    StructField("zip_code", StringType(), False),
    StructField("overall_svi_score", DoubleType(), True),
    StructField("svi_percentile", IntegerType(), True),
    StructField("vulnerability_level", StringType(), True),
    StructField("theme1_socioeconomic", DoubleType(), True),
    StructField("theme2_household", DoubleType(), True),
    StructField("theme3_minority_language", DoubleType(), True),
    StructField("theme4_housing_transport", DoubleType(), True),
    StructField("data_year", IntegerType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("source_system", StringType(), True)
])

svi_df = spark.createDataFrame(svi_data, schema=svi_schema)
print(f"✅ Generated SVI data for {svi_df.count()} ZIP codes")
svi_df.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Area Deprivation Index (ADI)

# COMMAND ----------

# ADI: Neighborhood disadvantage score (1-100, higher = more disadvantaged)
adi_data = []

for zip_code in zip_codes:
    seed = int(zip_code) % 1000
    random.seed(seed)
    
    # Get census and SVI data
    census_row = [c for c in census_data if c['zip_code'] == zip_code][0]
    svi_row = [s for s in svi_data if s['zip_code'] == zip_code][0]
    
    # ADI correlates with income, education, housing
    adi_score = int(
        census_row['poverty_rate'] * 40 +
        (1 - census_row['high_school_grad_rate']) * 30 +
        svi_row['overall_svi_score'] * 30
    )
    adi_score = max(1, min(100, adi_score))
    
    # National percentile
    adi_national_percentile = adi_score
    
    # State decile (1-10, 10 = most disadvantaged)
    adi_state_decile = max(1, min(10, (adi_score // 10) + 1))
    
    # Classification
    if adi_score >= 80:
        disadvantage_level = 'High'
    elif adi_score >= 60:
        disadvantage_level = 'Moderate'
    elif adi_score >= 40:
        disadvantage_level = 'Low'
    else:
        disadvantage_level = 'Very Low'
    
    adi_data.append({
        'zip_code': zip_code,
        'adi_score': adi_score,
        'adi_national_percentile': adi_national_percentile,
        'adi_state_decile': adi_state_decile,
        'disadvantage_level': disadvantage_level,
        'data_year': 2023,
        'created_at': datetime.now(),
        'source_system': 'UNIV_WISCONSIN_ADI'
    })

adi_schema = StructType([
    StructField("zip_code", StringType(), False),
    StructField("adi_score", IntegerType(), True),
    StructField("adi_national_percentile", IntegerType(), True),
    StructField("adi_state_decile", IntegerType(), True),
    StructField("disadvantage_level", StringType(), True),
    StructField("data_year", IntegerType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("source_system", StringType(), True)
])

adi_df = spark.createDataFrame(adi_data, schema=adi_schema)
print(f"✅ Generated ADI data for {adi_df.count()} ZIP codes")
adi_df.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Access Barriers Data

# COMMAND ----------

# Food deserts, transportation, provider access
access_data = []

for zip_code in zip_codes:
    seed = int(zip_code) % 1000
    random.seed(seed)
    
    # Get SVI data
    svi_row = [s for s in svi_data if s['zip_code'] == zip_code][0]
    
    # Food desert (no grocery within 5 miles for rural, 1 mile for urban)
    is_food_desert = random.random() < (svi_row['overall_svi_score'] * 0.4)
    nearest_grocery_miles = random.uniform(0.5, 15.0) if is_food_desert else random.uniform(0.2, 2.0)
    
    # Public transportation availability
    public_transport_score = max(0.0, min(1.0, 1.0 - svi_row['theme4_housing_transport']))
    has_public_transport = public_transport_score > 0.5
    
    # Healthcare provider access
    pcp_per_1000_residents = random.uniform(0.3, 2.5)
    specialist_per_1000_residents = random.uniform(0.1, 1.2)
    hospital_distance_miles = random.uniform(1.0, 30.0)
    pharmacy_distance_miles = random.uniform(0.5, 10.0)
    
    # Provider desert classification
    is_provider_desert = pcp_per_1000_residents < 0.6
    
    access_data.append({
        'zip_code': zip_code,
        'is_food_desert': is_food_desert,
        'nearest_grocery_miles': round(nearest_grocery_miles, 1),
        'has_public_transport': has_public_transport,
        'public_transport_score': round(public_transport_score, 2),
        'pcp_per_1000_residents': round(pcp_per_1000_residents, 2),
        'specialist_per_1000_residents': round(specialist_per_1000_residents, 2),
        'is_provider_desert': is_provider_desert,
        'hospital_distance_miles': round(hospital_distance_miles, 1),
        'pharmacy_distance_miles': round(pharmacy_distance_miles, 1),
        'data_year': 2023,
        'created_at': datetime.now(),
        'source_system': 'USDA_HRSA_COMBINED'
    })

access_schema = StructType([
    StructField("zip_code", StringType(), False),
    StructField("is_food_desert", BooleanType(), True),
    StructField("nearest_grocery_miles", DoubleType(), True),
    StructField("has_public_transport", BooleanType(), True),
    StructField("public_transport_score", DoubleType(), True),
    StructField("pcp_per_1000_residents", DoubleType(), True),
    StructField("specialist_per_1000_residents", DoubleType(), True),
    StructField("is_provider_desert", BooleanType(), True),
    StructField("hospital_distance_miles", DoubleType(), True),
    StructField("pharmacy_distance_miles", DoubleType(), True),
    StructField("data_year", IntegerType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("source_system", StringType(), True)
])

access_df = spark.createDataFrame(access_data, schema=access_schema)
print(f"✅ Generated access barriers data for {access_df.count()} ZIP codes")
access_df.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze Layer - Raw SDOH Data

# COMMAND ----------

# Write census data to bronze
census_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{BRONZE_SCHEMA}.census_demographics_raw")

print(f"✅ Created bronze table: {CATALOG}.{BRONZE_SCHEMA}.census_demographics_raw")

# Write SVI data to bronze
svi_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{BRONZE_SCHEMA}.cdc_svi_raw")

print(f"✅ Created bronze table: {CATALOG}.{BRONZE_SCHEMA}.cdc_svi_raw")

# Write ADI data to bronze
adi_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{BRONZE_SCHEMA}.adi_raw")

print(f"✅ Created bronze table: {CATALOG}.{BRONZE_SCHEMA}.adi_raw")

# Write access barriers to bronze
access_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{BRONZE_SCHEMA}.access_barriers_raw")

print(f"✅ Created bronze table: {CATALOG}.{BRONZE_SCHEMA}.access_barriers_raw")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Layer - Validated SDOH Data

# COMMAND ----------

# Census - cleaned and validated
census_silver_df = spark.sql(f"""
    SELECT
        zip_code,
        total_population,
        population_65_plus,
        CAST(population_65_plus AS DOUBLE) / NULLIF(total_population, 0) AS pct_65_plus,
        median_household_income,
        poverty_rate,
        unemployment_rate,
        high_school_grad_rate,
        bachelors_degree_rate,
        median_home_value,
        renter_occupied_pct,
        data_year,
        source_system,
        CURRENT_TIMESTAMP() AS processed_at
    FROM {CATALOG}.{BRONZE_SCHEMA}.census_demographics_raw
    WHERE zip_code IS NOT NULL
        AND total_population > 0
""")

census_silver_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.census_demographics")

print(f"✅ Created silver table: {CATALOG}.{SILVER_SCHEMA}.census_demographics")

# COMMAND ----------

# SVI - cleaned and validated
svi_silver_df = spark.sql(f"""
    SELECT
        zip_code,
        overall_svi_score,
        svi_percentile,
        vulnerability_level,
        theme1_socioeconomic,
        theme2_household,
        theme3_minority_language,
        theme4_housing_transport,
        data_year,
        source_system,
        CURRENT_TIMESTAMP() AS processed_at
    FROM {CATALOG}.{BRONZE_SCHEMA}.cdc_svi_raw
    WHERE zip_code IS NOT NULL
        AND overall_svi_score BETWEEN 0 AND 1
        AND svi_percentile BETWEEN 0 AND 100
""")

svi_silver_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.cdc_svi")

print(f"✅ Created silver table: {CATALOG}.{SILVER_SCHEMA}.cdc_svi")

# COMMAND ----------

# ADI - cleaned and validated
adi_silver_df = spark.sql(f"""
    SELECT
        zip_code,
        adi_score,
        adi_national_percentile,
        adi_state_decile,
        disadvantage_level,
        data_year,
        source_system,
        CURRENT_TIMESTAMP() AS processed_at
    FROM {CATALOG}.{BRONZE_SCHEMA}.adi_raw
    WHERE zip_code IS NOT NULL
        AND adi_score BETWEEN 1 AND 100
        AND adi_state_decile BETWEEN 1 AND 10
""")

adi_silver_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.adi")

print(f"✅ Created silver table: {CATALOG}.{SILVER_SCHEMA}.adi")

# COMMAND ----------

# Access barriers - cleaned and validated
access_silver_df = spark.sql(f"""
    SELECT
        zip_code,
        is_food_desert,
        nearest_grocery_miles,
        has_public_transport,
        public_transport_score,
        pcp_per_1000_residents,
        specialist_per_1000_residents,
        is_provider_desert,
        hospital_distance_miles,
        pharmacy_distance_miles,
        data_year,
        source_system,
        CURRENT_TIMESTAMP() AS processed_at
    FROM {CATALOG}.{BRONZE_SCHEMA}.access_barriers_raw
    WHERE zip_code IS NOT NULL
        AND pcp_per_1000_residents >= 0
""")

access_silver_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.access_barriers")

print(f"✅ Created silver table: {CATALOG}.{SILVER_SCHEMA}.access_barriers")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer - Business-Ready SDOH Tables

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. ZIP-Level SDOH Summary

# COMMAND ----------

zip_sdoh_summary_df = spark.sql(f"""
    SELECT
        c.zip_code,
        
        -- Census demographics
        c.total_population,
        c.population_65_plus,
        c.pct_65_plus,
        c.median_household_income,
        c.poverty_rate,
        c.unemployment_rate,
        c.high_school_grad_rate,
        c.bachelors_degree_rate,
        c.median_home_value,
        c.renter_occupied_pct,
        
        -- Social vulnerability
        s.overall_svi_score,
        s.svi_percentile,
        s.vulnerability_level,
        s.theme1_socioeconomic AS svi_socioeconomic,
        s.theme2_household AS svi_household,
        s.theme3_minority_language AS svi_minority_language,
        s.theme4_housing_transport AS svi_housing_transport,
        
        -- Area deprivation
        a.adi_score,
        a.adi_national_percentile,
        a.adi_state_decile,
        a.disadvantage_level,
        
        -- Access barriers
        ab.is_food_desert,
        ab.nearest_grocery_miles,
        ab.has_public_transport,
        ab.public_transport_score,
        ab.pcp_per_1000_residents,
        ab.specialist_per_1000_residents,
        ab.is_provider_desert,
        ab.hospital_distance_miles,
        ab.pharmacy_distance_miles,
        
        -- Composite risk score (0-100, higher = more at risk)
        CAST(
            (s.overall_svi_score * 40) +
            (a.adi_score * 0.30) +
            (CASE WHEN ab.is_provider_desert THEN 15 ELSE 0 END) +
            (CASE WHEN ab.is_food_desert THEN 10 ELSE 0 END) +
            (CASE WHEN NOT ab.has_public_transport THEN 5 ELSE 0 END)
        AS INT) AS composite_risk_score,
        
        -- Risk classification
        CASE
            WHEN (
                (s.overall_svi_score * 40) +
                (a.adi_score * 0.30) +
                (CASE WHEN ab.is_provider_desert THEN 15 ELSE 0 END) +
                (CASE WHEN ab.is_food_desert THEN 10 ELSE 0 END) +
                (CASE WHEN NOT ab.has_public_transport THEN 5 ELSE 0 END)
            ) >= 70 THEN 'High Risk'
            WHEN (
                (s.overall_svi_score * 40) +
                (a.adi_score * 0.30) +
                (CASE WHEN ab.is_provider_desert THEN 15 ELSE 0 END) +
                (CASE WHEN ab.is_food_desert THEN 10 ELSE 0 END) +
                (CASE WHEN NOT ab.has_public_transport THEN 5 ELSE 0 END)
            ) >= 50 THEN 'Moderate Risk'
            WHEN (
                (s.overall_svi_score * 40) +
                (a.adi_score * 0.30) +
                (CASE WHEN ab.is_provider_desert THEN 15 ELSE 0 END) +
                (CASE WHEN ab.is_food_desert THEN 10 ELSE 0 END) +
                (CASE WHEN NOT ab.has_public_transport THEN 5 ELSE 0 END)
            ) >= 30 THEN 'Low Risk'
            ELSE 'Very Low Risk'
        END AS sdoh_risk_classification,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{SILVER_SCHEMA}.census_demographics c
    INNER JOIN {CATALOG}.{SILVER_SCHEMA}.cdc_svi s
        ON c.zip_code = s.zip_code
    INNER JOIN {CATALOG}.{SILVER_SCHEMA}.adi a
        ON c.zip_code = a.zip_code
    INNER JOIN {CATALOG}.{SILVER_SCHEMA}.access_barriers ab
        ON c.zip_code = ab.zip_code
""")

zip_sdoh_summary_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary")

# Display sample
spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary LIMIT 10").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Member-Level SDOH Enrichment

# COMMAND ----------

member_sdoh_enriched_df = spark.sql(f"""
    SELECT
        m.member_id,
        m.first_name,
        m.last_name,
        m.age,
        m.gender,
        m.zip_code,
        m.risk_level AS clinical_risk_level,
        
        -- SDOH factors from ZIP
        z.median_household_income,
        z.poverty_rate,
        z.unemployment_rate,
        z.overall_svi_score,
        z.svi_percentile,
        z.vulnerability_level,
        z.adi_score,
        z.adi_national_percentile,
        z.disadvantage_level,
        z.is_food_desert,
        z.is_provider_desert,
        z.has_public_transport,
        z.pcp_per_1000_residents,
        z.composite_risk_score AS sdoh_risk_score,
        z.sdoh_risk_classification,
        
        -- Quality metrics from member summary
        mq.total_measures,
        mq.compliant_measures,
        mq.open_gaps,
        mq.compliance_rate,
        
        -- Combined risk assessment
        CASE
            WHEN m.risk_level = 'High' AND z.sdoh_risk_classification = 'High Risk' THEN 'Critical'
            WHEN m.risk_level = 'High' OR z.sdoh_risk_classification = 'High Risk' THEN 'High'
            WHEN m.risk_level = 'Medium' AND z.sdoh_risk_classification IN ('Moderate Risk', 'High Risk') THEN 'High'
            WHEN m.risk_level = 'Medium' OR z.sdoh_risk_classification = 'Moderate Risk' THEN 'Medium'
            ELSE 'Low'
        END AS combined_risk_level,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{SILVER_SCHEMA}.members m
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary z
        ON m.zip_code = z.zip_code
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_quality_summary mq
        ON m.member_id = mq.member_id
    WHERE m.is_active = true
""")

member_sdoh_enriched_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched")

# Display sample
spark.sql(f"""
    SELECT member_id, first_name, last_name, zip_code, 
           sdoh_risk_classification, clinical_risk_level, combined_risk_level,
           compliance_rate, open_gaps
    FROM {CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched 
    LIMIT 10
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3. Quality Performance by SDOH Risk

# COMMAND ----------

quality_by_sdoh_df = spark.sql(f"""
    SELECT
        sdoh_risk_classification,
        vulnerability_level,
        
        -- Member counts
        COUNT(DISTINCT member_id) AS total_members,
        
        -- Quality metrics
        AVG(compliance_rate) AS avg_compliance_rate,
        AVG(open_gaps) AS avg_open_gaps,
        SUM(open_gaps) AS total_open_gaps,
        
        -- Barrier prevalence
        SUM(CASE WHEN is_food_desert THEN 1 ELSE 0 END) AS members_in_food_deserts,
        SUM(CASE WHEN is_provider_desert THEN 1 ELSE 0 END) AS members_in_provider_deserts,
        SUM(CASE WHEN NOT has_public_transport THEN 1 ELSE 0 END) AS members_no_transport,
        
        -- Economic factors
        AVG(median_household_income) AS avg_income,
        AVG(poverty_rate) AS avg_poverty_rate,
        AVG(unemployment_rate) AS avg_unemployment_rate,
        
        -- Vulnerability scores
        AVG(overall_svi_score) AS avg_svi_score,
        AVG(adi_score) AS avg_adi_score,
        AVG(sdoh_risk_score) AS avg_sdoh_risk_score,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched
    WHERE sdoh_risk_classification IS NOT NULL
    GROUP BY sdoh_risk_classification, vulnerability_level
    ORDER BY avg_sdoh_risk_score DESC
""")

quality_by_sdoh_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.quality_by_sdoh_risk")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.quality_by_sdoh_risk")

# Display results
spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.quality_by_sdoh_risk ORDER BY avg_sdoh_risk_score DESC").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("="*80)
print("SDOH DATA INTEGRATION COMPLETE")
print("="*80)

# Count records
bronze_census = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.census_demographics_raw").count()
bronze_svi = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.cdc_svi_raw").count()
bronze_adi = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.adi_raw").count()
bronze_access = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.access_barriers_raw").count()

silver_census = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.census_demographics").count()
silver_svi = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.cdc_svi").count()
silver_adi = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.adi").count()
silver_access = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.access_barriers").count()

gold_zip_summary = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary").count()
gold_member_enriched = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched").count()
gold_quality_by_sdoh = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.quality_by_sdoh_risk").count()

print(f"\n📊 BRONZE LAYER:")
print(f"   • census_demographics_raw: {bronze_census:,} ZIP codes")
print(f"   • cdc_svi_raw: {bronze_svi:,} ZIP codes")
print(f"   • adi_raw: {bronze_adi:,} ZIP codes")
print(f"   • access_barriers_raw: {bronze_access:,} ZIP codes")

print(f"\n📊 SILVER LAYER:")
print(f"   • census_demographics: {silver_census:,} ZIP codes")
print(f"   • cdc_svi: {silver_svi:,} ZIP codes")
print(f"   • adi: {silver_adi:,} ZIP codes")
print(f"   • access_barriers: {silver_access:,} ZIP codes")

print(f"\n📊 GOLD LAYER:")
print(f"   • zip_sdoh_summary: {gold_zip_summary:,} ZIP codes")
print(f"   • member_sdoh_enriched: {gold_member_enriched:,} members")
print(f"   • quality_by_sdoh_risk: {gold_quality_by_sdoh:,} risk segments")

print(f"\n✅ Ready for dashboard visualization!")
print("="*80)

