# Databricks notebook source
# MAGIC %md
# MAGIC # 08 - Geospatial Enrichment
# MAGIC
# MAGIC **Purpose:** Add geographic coordinates and create ZIP-level aggregations for maps
# MAGIC
# MAGIC **Data Generated:**
# MAGIC - Member geocoding (lat/long by ZIP)
# MAGIC - ZIP-level quality aggregations
# MAGIC - Geographic clustering of gaps
# MAGIC - Distance calculations
# MAGIC
# MAGIC **Use Case:** Heat maps, geographic targeting, mobile clinic planning

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Imports
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window
from datetime import datetime
import random
import math

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
# MAGIC ## Generate Geographic Coordinates
# MAGIC
# MAGIC In production, would use:
# MAGIC - Google Maps Geocoding API
# MAGIC - Census Geocoder
# MAGIC - ESRI ArcGIS
# MAGIC
# MAGIC For demo: Generate synthetic but realistic coordinates

# COMMAND ----------

# Get unique ZIP codes
zip_codes_df = spark.sql(f"""
    SELECT DISTINCT zip_code
    FROM {CATALOG}.{SILVER_SCHEMA}.members
    WHERE zip_code IS NOT NULL
""")

zip_codes = [row.zip_code for row in zip_codes_df.collect()]
print(f"Found {len(zip_codes)} unique ZIP codes to geocode")

# COMMAND ----------

# Generate synthetic geocoordinates
# Simulating a metropolitan area (Phoenix, AZ region as example)
geocode_data = []

for zip_code in zip_codes:
    # Use ZIP code as seed for consistency
    seed = int(zip_code) % 1000
    random.seed(seed)
    
    # Base coordinates (Phoenix metro area: 33.4484° N, 112.0740° W)
    base_lat = 33.4484
    base_lon = -112.0740
    
    # Spread ZIPs across ~50 mile radius
    # 1 degree latitude ≈ 69 miles
    # 1 degree longitude ≈ 54 miles (at this latitude)
    lat_offset = random.uniform(-0.7, 0.7)  # ±48 miles
    lon_offset = random.uniform(-0.9, 0.9)  # ±48 miles
    
    latitude = round(base_lat + lat_offset, 6)
    longitude = round(base_lon + lon_offset, 6)
    
    # City name (simulated)
    if abs(lat_offset) < 0.2 and abs(lon_offset) < 0.2:
        city = 'Phoenix'
    elif lat_offset > 0.4:
        city = random.choice(['Scottsdale', 'Paradise Valley'])
    elif lat_offset < -0.4:
        city = random.choice(['Tempe', 'Mesa', 'Chandler'])
    elif lon_offset > 0.4:
        city = random.choice(['Glendale', 'Peoria'])
    else:
        city = random.choice(['Phoenix', 'Tempe', 'Mesa'])
    
    # State
    state = 'AZ'
    
    geocode_data.append({
        'zip_code': zip_code,
        'city': city,
        'state': state,
        'latitude': latitude,
        'longitude': longitude,
        'geocoding_accuracy': 'ZIP Centroid',
        'geocoded_at': datetime.now(),
        'source_system': 'GEOCODING_SERVICE'
    })

geocode_schema = StructType([
    StructField("zip_code", StringType(), False),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("geocoding_accuracy", StringType(), True),
    StructField("geocoded_at", TimestampType(), True),
    StructField("source_system", StringType(), True)
])

geocode_df = spark.createDataFrame(geocode_data, schema=geocode_schema)
print(f"✅ Generated geocoding data for {geocode_df.count()} ZIP codes")
geocode_df.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze Layer - Raw Geocoding

# COMMAND ----------

geocode_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{BRONZE_SCHEMA}.zip_geocoding_raw")

print(f"✅ Created bronze table: {CATALOG}.{BRONZE_SCHEMA}.zip_geocoding_raw")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Layer - Validated Geocoding

# COMMAND ----------

geocode_silver_df = spark.sql(f"""
    SELECT
        zip_code,
        city,
        state,
        latitude,
        longitude,
        geocoding_accuracy,
        CURRENT_TIMESTAMP() AS processed_at
    FROM {CATALOG}.{BRONZE_SCHEMA}.zip_geocoding_raw
    WHERE zip_code IS NOT NULL
        AND latitude IS NOT NULL
        AND longitude IS NOT NULL
        AND latitude BETWEEN -90 AND 90
        AND longitude BETWEEN -180 AND 180
""")

geocode_silver_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.zip_geocoding")

print(f"✅ Created silver table: {CATALOG}.{SILVER_SCHEMA}.zip_geocoding")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer - Geographic Analytics

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. ZIP-Level Quality & SDOH Summary with Geocoding

# COMMAND ----------

zip_geographic_summary_df = spark.sql(f"""
    SELECT
        g.zip_code,
        g.city,
        g.state,
        g.latitude,
        g.longitude,
        
        -- Member counts
        COUNT(DISTINCT m.member_id) AS total_members,
        COUNT(DISTINCT CASE WHEN m.is_active THEN m.member_id END) AS active_members,
        
        -- Demographics
        AVG(m.age) AS avg_age,
        SUM(CASE WHEN m.gender = 'M' THEN 1 ELSE 0 END) AS male_count,
        SUM(CASE WHEN m.gender = 'F' THEN 1 ELSE 0 END) AS female_count,
        
        -- Risk distribution
        SUM(CASE WHEN m.risk_level = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
        SUM(CASE WHEN m.risk_level = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_count,
        SUM(CASE WHEN m.risk_level = 'Low' THEN 1 ELSE 0 END) AS low_risk_count,
        
        -- Quality metrics (from member quality summary)
        AVG(mq.compliance_rate) AS avg_compliance_rate,
        SUM(mq.open_gaps) AS total_open_gaps,
        AVG(mq.open_gaps) AS avg_gaps_per_member,
        
        -- SDOH factors (from ZIP SDOH summary)
        MAX(z.median_household_income) AS median_income,
        MAX(z.poverty_rate) AS poverty_rate,
        MAX(z.overall_svi_score) AS svi_score,
        MAX(z.svi_percentile) AS svi_percentile,
        MAX(z.vulnerability_level) AS vulnerability_level,
        MAX(z.adi_score) AS adi_score,
        MAX(z.sdoh_risk_classification) AS sdoh_risk_classification,
        MAX(z.is_food_desert) AS is_food_desert,
        MAX(z.is_provider_desert) AS is_provider_desert,
        MAX(z.pcp_per_1000_residents) AS pcp_per_1000,
        
        -- Cost data (from TCOC)
        AVG(t.total_cost_12m) AS avg_cost_per_member,
        SUM(t.preventable_cost) AS total_preventable_cost,
        AVG(t.preventable_cost) AS avg_preventable_cost,
        SUM(t.preventable_er_visits) AS total_preventable_er,
        SUM(t.preventable_hospitalizations) AS total_preventable_hosp,
        
        -- Gap concentration score (for targeting mobile clinics)
        CAST(
            (SUM(mq.open_gaps) / NULLIF(COUNT(DISTINCT m.member_id), 0)) * 100
        AS INT) AS gap_concentration_score,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{SILVER_SCHEMA}.zip_geocoding g
    LEFT JOIN {CATALOG}.{SILVER_SCHEMA}.members m
        ON g.zip_code = m.zip_code
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_quality_summary mq
        ON m.member_id = mq.member_id
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary z
        ON g.zip_code = z.zip_code
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.tcoc_by_member t
        ON m.member_id = t.member_id
    GROUP BY g.zip_code, g.city, g.state, g.latitude, g.longitude
    HAVING COUNT(DISTINCT m.member_id) > 0
""")

zip_geographic_summary_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.zip_geographic_summary")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.zip_geographic_summary")

# Display sample
spark.sql(f"""
    SELECT zip_code, city, latitude, longitude, active_members, 
           total_open_gaps, avg_compliance_rate, avg_preventable_cost,
           sdoh_risk_classification, gap_concentration_score
    FROM {CATALOG}.{GOLD_SCHEMA}.zip_geographic_summary
    ORDER BY total_open_gaps DESC
    LIMIT 10
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Member Geographic Enrichment

# COMMAND ----------

member_geographic_df = spark.sql(f"""
    SELECT
        m.member_id,
        m.first_name,
        m.last_name,
        m.age,
        m.gender,
        m.zip_code,
        
        -- Geographic coordinates
        g.city,
        g.state,
        g.latitude,
        g.longitude,
        
        -- Quality metrics
        mq.compliance_rate,
        mq.open_gaps,
        mq.total_measures,
        
        -- SDOH
        ms.sdoh_risk_classification,
        ms.vulnerability_level,
        ms.is_food_desert,
        ms.is_provider_desert,
        
        -- Cost
        t.preventable_cost,
        t.preventable_er_visits,
        t.preventable_hospitalizations,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{SILVER_SCHEMA}.members m
    LEFT JOIN {CATALOG}.{SILVER_SCHEMA}.zip_geocoding g
        ON m.zip_code = g.zip_code
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_quality_summary mq
        ON m.member_id = mq.member_id
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched ms
        ON m.member_id = ms.member_id
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.tcoc_by_member t
        ON m.member_id = t.member_id
    WHERE m.is_active = true
        AND g.latitude IS NOT NULL
""")

member_geographic_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.member_geographic")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.member_geographic")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3. Gap Hotspots (for Mobile Clinic Planning)

# COMMAND ----------

gap_hotspots_df = spark.sql(f"""
    SELECT
        zip_code,
        city,
        state,
        latitude,
        longitude,
        active_members,
        total_open_gaps,
        gap_concentration_score,
        
        -- Prioritization factors
        avg_compliance_rate,
        avg_preventable_cost,
        total_preventable_cost,
        total_preventable_er,
        total_preventable_hosp,
        
        -- Barriers
        vulnerability_level,
        sdoh_risk_classification,
        is_food_desert,
        is_provider_desert,
        poverty_rate,
        pcp_per_1000,
        
        -- Priority score for mobile clinic (higher = better target)
        CAST(
            (total_open_gaps / 10) * 0.30 +                                    -- 30% weight on gap volume
            (gap_concentration_score) * 0.25 +                                  -- 25% weight on concentration
            (CASE WHEN sdoh_risk_classification = 'High Risk' THEN 100 ELSE 0 END) * 0.20 +  -- 20% weight on SDOH
            (total_preventable_cost / 1000) * 0.15 +                           -- 15% weight on cost opportunity
            (CASE WHEN is_provider_desert THEN 100 ELSE 0 END) * 0.10         -- 10% weight on access barriers
        AS INT) AS mobile_clinic_priority_score,
        
        -- Priority tier
        CASE
            WHEN (
                (total_open_gaps / 10) * 0.30 +
                (gap_concentration_score) * 0.25 +
                (CASE WHEN sdoh_risk_classification = 'High Risk' THEN 100 ELSE 0 END) * 0.20 +
                (total_preventable_cost / 1000) * 0.15 +
                (CASE WHEN is_provider_desert THEN 100 ELSE 0 END) * 0.10
            ) >= 300 THEN 'Critical - Deploy First'
            WHEN (
                (total_open_gaps / 10) * 0.30 +
                (gap_concentration_score) * 0.25 +
                (CASE WHEN sdoh_risk_classification = 'High Risk' THEN 100 ELSE 0 END) * 0.20 +
                (total_preventable_cost / 1000) * 0.15 +
                (CASE WHEN is_provider_desert THEN 100 ELSE 0 END) * 0.10
            ) >= 200 THEN 'High Priority'
            WHEN (
                (total_open_gaps / 10) * 0.30 +
                (gap_concentration_score) * 0.25 +
                (CASE WHEN sdoh_risk_classification = 'High Risk' THEN 100 ELSE 0 END) * 0.20 +
                (total_preventable_cost / 1000) * 0.15 +
                (CASE WHEN is_provider_desert THEN 100 ELSE 0 END) * 0.10
            ) >= 100 THEN 'Medium Priority'
            ELSE 'Low Priority'
        END AS mobile_clinic_priority_tier,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{GOLD_SCHEMA}.zip_geographic_summary
    WHERE total_open_gaps > 0
    ORDER BY mobile_clinic_priority_score DESC
""")

gap_hotspots_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.gap_hotspots")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.gap_hotspots")

# Display top hotspots
spark.sql(f"""
    SELECT zip_code, city, active_members, total_open_gaps, 
           avg_compliance_rate, total_preventable_cost,
           sdoh_risk_classification, is_provider_desert,
           mobile_clinic_priority_score, mobile_clinic_priority_tier
    FROM {CATALOG}.{GOLD_SCHEMA}.gap_hotspots
    ORDER BY mobile_clinic_priority_score DESC
    LIMIT 15
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4. Measure-Specific Gap Geography

# COMMAND ----------

# Get open gaps by measure and ZIP
measure_gap_geography_df = spark.sql(f"""
    SELECT
        g.zip_code,
        g.city,
        g.state,
        g.latitude,
        g.longitude,
        og.measure_code,
        og.measure_name,
        
        -- Gap counts
        COUNT(DISTINCT og.member_id) AS members_with_gap,
        
        -- Member characteristics
        AVG(m.age) AS avg_age,
        
        -- SDOH
        MAX(z.sdoh_risk_classification) AS sdoh_risk,
        MAX(z.vulnerability_level) AS vulnerability_level,
        MAX(z.poverty_rate) AS poverty_rate,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{GOLD_SCHEMA}.open_gaps_dashboard og
    INNER JOIN {CATALOG}.{SILVER_SCHEMA}.members m
        ON og.member_id = m.member_id
    INNER JOIN {CATALOG}.{SILVER_SCHEMA}.zip_geocoding g
        ON m.zip_code = g.zip_code
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.zip_sdoh_summary z
        ON g.zip_code = z.zip_code
    GROUP BY g.zip_code, g.city, g.state, g.latitude, g.longitude, 
             og.measure_code, og.measure_name
""")

measure_gap_geography_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.measure_gap_geography")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.measure_gap_geography")

# Display BCS (mammography) gaps by ZIP
spark.sql(f"""
    SELECT zip_code, city, latitude, longitude, members_with_gap, avg_age,
           sdoh_risk, vulnerability_level, poverty_rate
    FROM {CATALOG}.{GOLD_SCHEMA}.measure_gap_geography
    WHERE measure_code = 'BCS'
    ORDER BY members_with_gap DESC
    LIMIT 10
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("="*80)
print("GEOSPATIAL ENRICHMENT COMPLETE")
print("="*80)

# Count records
geocoded_zips = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.zip_geocoding").count()
geo_summary = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.zip_geographic_summary").count()
member_geo = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.member_geographic").count()
hotspots = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.gap_hotspots").count()
measure_geo = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.measure_gap_geography").count()

# Geographic spread
geo_stats = spark.sql(f"""
    SELECT
        COUNT(DISTINCT zip_code) AS total_zips,
        COUNT(DISTINCT city) AS total_cities,
        MIN(latitude) AS min_lat,
        MAX(latitude) AS max_lat,
        MIN(longitude) AS min_lon,
        MAX(longitude) AS max_lon,
        SUM(active_members) AS total_members,
        SUM(total_open_gaps) AS total_gaps
    FROM {CATALOG}.{GOLD_SCHEMA}.zip_geographic_summary
""").collect()[0]

# Top hotspots
top_hotspots = spark.sql(f"""
    SELECT
        COUNT(*) AS critical_hotspots
    FROM {CATALOG}.{GOLD_SCHEMA}.gap_hotspots
    WHERE mobile_clinic_priority_tier = 'Critical - Deploy First'
""").collect()[0]['critical_hotspots']

print(f"\n📊 GEOCODING:")
print(f"   • ZIP codes geocoded: {geocoded_zips}")
print(f"   • Cities covered: {geo_stats['total_cities']}")

print(f"\n🗺️ GEOGRAPHIC SUMMARY:")
print(f"   • ZIPs with members: {geo_summary}")
print(f"   • Members geocoded: {member_geo:,}")
print(f"   • Latitude range: {geo_stats['min_lat']:.4f} to {geo_stats['max_lat']:.4f}")
print(f"   • Longitude range: {geo_stats['min_lon']:.4f} to {geo_stats['max_lon']:.4f}")

print(f"\n🎯 GAP HOTSPOTS:")
print(f"   • Total hotspots: {hotspots}")
print(f"   • Critical priority (deploy first): {top_hotspots}")
print(f"   • Measure-specific geographies: {measure_geo}")

print(f"\n📈 TOTALS:")
print(f"   • Members: {geo_stats['total_members']:,}")
print(f"   • Open gaps: {geo_stats['total_gaps']:,}")

print(f"\n✅ Ready for heat map visualization!")
print("="*80)

