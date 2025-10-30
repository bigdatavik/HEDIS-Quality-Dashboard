# Databricks notebook source
# MAGIC %md
# MAGIC # 07 - Claims Cost Analysis
# MAGIC
# MAGIC **Purpose:** Generate synthetic medical claims and calculate Total Cost of Care (TCOC)
# MAGIC
# MAGIC **Data Generated:**
# MAGIC - ER visits and hospitalizations
# MAGIC - Office visits and outpatient procedures
# MAGIC - Lab tests and diagnostic imaging
# MAGIC - Pharmacy claims
# MAGIC - Total Cost of Care (TCOC) by member
# MAGIC
# MAGIC **Use Case:** ROI calculations for gap closure initiatives
# MAGIC - Identify preventable ER visits/hospitalizations
# MAGIC - Calculate cost savings from closing quality gaps
# MAGIC - Predict future costs based on current gaps

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Imports
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window
from datetime import datetime, timedelta
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
# MAGIC ## Get Member Data

# COMMAND ----------

# Get active members with quality and SDOH data
members_df = spark.sql(f"""
    SELECT
        m.member_id,
        m.age,
        m.gender,
        m.risk_level AS clinical_risk_level,
        m.zip_code,
        
        -- Quality metrics
        mq.total_measures,
        mq.compliant_measures,
        mq.open_gaps,
        mq.compliance_rate,
        
        -- SDOH if available
        COALESCE(ms.sdoh_risk_classification, 'Unknown') AS sdoh_risk,
        COALESCE(ms.composite_risk_score, 50) AS sdoh_risk_score,
        COALESCE(ms.vulnerability_level, 'Unknown') AS vulnerability_level
        
    FROM {CATALOG}.{SILVER_SCHEMA}.members m
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_quality_summary mq
        ON m.member_id = mq.member_id
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched ms
        ON m.member_id = ms.member_id
    WHERE m.is_active = true
""")

total_members = members_df.count()
print(f"Found {total_members:,} active members")

# Convert to Pandas for easier synthetic data generation
members_pd = members_df.toPandas()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Medical Claims Data
# MAGIC
# MAGIC Claims types:
# MAGIC - ER visits (preventable vs non-preventable)
# MAGIC - Inpatient hospitalizations
# MAGIC - Office visits (PCP, specialist)
# MAGIC - Outpatient procedures
# MAGIC - Lab tests
# MAGIC - Diagnostic imaging

# COMMAND ----------

claims_data = []
claim_id = 1

# Generate claims for each member over past 12 months
for idx, member in members_pd.iterrows():
    member_id = member['member_id']
    age = member['age']
    gender = member['gender']
    clinical_risk = member['clinical_risk_level']
    sdoh_risk = member['sdoh_risk']
    open_gaps = member['open_gaps']
    compliance_rate = member['compliance_rate']
    
    # Set seed for reproducibility based on member_id
    seed = int(member_id.replace('M', ''))
    random.seed(seed)
    
    # Base utilization rates (adjust by risk level)
    if clinical_risk == 'High':
        er_rate = random.uniform(1.5, 3.0)
        hospital_rate = random.uniform(0.3, 0.8)
        office_visit_rate = random.uniform(8, 15)
    elif clinical_risk == 'Medium':
        er_rate = random.uniform(0.5, 1.5)
        hospital_rate = random.uniform(0.1, 0.3)
        office_visit_rate = random.uniform(4, 8)
    else:  # Low risk
        er_rate = random.uniform(0.1, 0.5)
        hospital_rate = random.uniform(0.0, 0.1)
        office_visit_rate = random.uniform(2, 5)
    
    # Adjust for quality gaps (more gaps = more utilization)
    gap_multiplier = 1.0 + (open_gaps * 0.05)  # 5% more per gap
    er_rate *= gap_multiplier
    hospital_rate *= gap_multiplier
    
    # Adjust for SDOH risk
    if 'High' in sdoh_risk:
        er_rate *= 1.3
        hospital_rate *= 1.2
    
    # Generate ER visits
    num_er_visits = int(er_rate)
    if random.random() < (er_rate - num_er_visits):
        num_er_visits += 1
    
    for _ in range(num_er_visits):
        service_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        # Determine if preventable (higher if gaps exist)
        is_preventable = random.random() < (0.3 + (open_gaps * 0.05))
        
        # Cost varies by preventability
        if is_preventable:
            cost = random.uniform(800, 2500)  # Lower cost, minor issues
            diagnosis = random.choice([
                'Uncontrolled diabetes', 'Hypertensive urgency', 
                'Asthma exacerbation', 'COPD exacerbation',
                'Chest pain (cardiac workup)', 'Medication non-adherence'
            ])
        else:
            cost = random.uniform(1500, 5000)  # Higher cost, genuine emergencies
            diagnosis = random.choice([
                'Fracture', 'Acute infection', 'Severe pain',
                'Chest pain (MI)', 'Stroke', 'Trauma'
            ])
        
        claims_data.append({
            'claim_id': f'CLM{claim_id:09d}',
            'member_id': member_id,
            'service_date': service_date,
            'claim_type': 'ER Visit',
            'service_category': 'Emergency',
            'diagnosis_description': diagnosis,
            'is_preventable': is_preventable,
            'cost': round(cost, 2),
            'provider_type': 'Hospital',
            'created_at': datetime.now()
        })
        claim_id += 1
    
    # Generate hospitalizations
    num_hospitalizations = int(hospital_rate)
    if random.random() < (hospital_rate - num_hospitalizations):
        num_hospitalizations += 1
    
    for _ in range(num_hospitalizations):
        service_date = datetime.now() - timedelta(days=random.randint(1, 365))
        length_of_stay = random.randint(1, 7)
        
        # Preventable if chronic condition could have been managed
        is_preventable = random.random() < (0.4 + (open_gaps * 0.08))
        
        if is_preventable:
            cost = random.uniform(8000, 25000)
            diagnosis = random.choice([
                'Diabetic ketoacidosis', 'Heart failure exacerbation',
                'COPD exacerbation', 'Sepsis (UTI)', 
                'Uncontrolled hypertension', 'Diabetic complications'
            ])
        else:
            cost = random.uniform(15000, 50000)
            diagnosis = random.choice([
                'Surgical procedure', 'Cancer treatment',
                'Stroke', 'Heart attack', 'Major trauma'
            ])
        
        claims_data.append({
            'claim_id': f'CLM{claim_id:09d}',
            'member_id': member_id,
            'service_date': service_date,
            'claim_type': 'Inpatient Hospitalization',
            'service_category': 'Inpatient',
            'diagnosis_description': diagnosis,
            'is_preventable': is_preventable,
            'cost': round(cost, 2),
            'provider_type': 'Hospital',
            'length_of_stay': length_of_stay,
            'created_at': datetime.now()
        })
        claim_id += 1
    
    # Generate office visits (PCP and specialist)
    num_office_visits = int(office_visit_rate)
    for _ in range(num_office_visits):
        service_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        # 60% PCP, 40% specialist
        if random.random() < 0.6:
            provider_type = 'PCP'
            cost = random.uniform(100, 250)
        else:
            provider_type = 'Specialist'
            cost = random.uniform(150, 400)
        
        claims_data.append({
            'claim_id': f'CLM{claim_id:09d}',
            'member_id': member_id,
            'service_date': service_date,
            'claim_type': 'Office Visit',
            'service_category': 'Outpatient',
            'diagnosis_description': 'Routine care',
            'is_preventable': False,
            'cost': round(cost, 2),
            'provider_type': provider_type,
            'created_at': datetime.now()
        })
        claim_id += 1
    
    # Generate lab tests and imaging (correlated with office visits)
    num_labs = int(office_visit_rate * 0.6)
    for _ in range(num_labs):
        service_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        test_type = random.choice(['Lab Test', 'X-Ray', 'CT Scan', 'MRI', 'Ultrasound'])
        
        if test_type == 'Lab Test':
            cost = random.uniform(50, 300)
        elif test_type == 'X-Ray':
            cost = random.uniform(100, 400)
        elif test_type == 'CT Scan':
            cost = random.uniform(500, 1500)
        elif test_type == 'MRI':
            cost = random.uniform(1000, 3000)
        else:  # Ultrasound
            cost = random.uniform(200, 600)
        
        claims_data.append({
            'claim_id': f'CLM{claim_id:09d}',
            'member_id': member_id,
            'service_date': service_date,
            'claim_type': test_type,
            'service_category': 'Diagnostic',
            'diagnosis_description': 'Diagnostic test',
            'is_preventable': False,
            'cost': round(cost, 2),
            'provider_type': 'Hospital/Lab',
            'created_at': datetime.now()
        })
        claim_id += 1

print(f"✅ Generated {len(claims_data):,} medical claims")

# COMMAND ----------

# Create DataFrame
claims_schema = StructType([
    StructField("claim_id", StringType(), False),
    StructField("member_id", StringType(), False),
    StructField("service_date", TimestampType(), True),
    StructField("claim_type", StringType(), True),
    StructField("service_category", StringType(), True),
    StructField("diagnosis_description", StringType(), True),
    StructField("is_preventable", BooleanType(), True),
    StructField("cost", DoubleType(), True),
    StructField("provider_type", StringType(), True),
    StructField("length_of_stay", IntegerType(), True),
    StructField("created_at", TimestampType(), True)
])

claims_df = spark.createDataFrame(claims_data, schema=claims_schema)
print(f"Claims DataFrame created with {claims_df.count():,} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze Layer - Raw Claims

# COMMAND ----------

claims_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{BRONZE_SCHEMA}.medical_claims_raw")

print(f"✅ Created bronze table: {CATALOG}.{BRONZE_SCHEMA}.medical_claims_raw")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Layer - Validated Claims

# COMMAND ----------

claims_silver_df = spark.sql(f"""
    SELECT
        claim_id,
        member_id,
        service_date,
        YEAR(service_date) AS service_year,
        MONTH(service_date) AS service_month,
        claim_type,
        service_category,
        diagnosis_description,
        is_preventable,
        cost,
        provider_type,
        length_of_stay,
        CURRENT_TIMESTAMP() AS processed_at
    FROM {CATALOG}.{BRONZE_SCHEMA}.medical_claims_raw
    WHERE claim_id IS NOT NULL
        AND member_id IS NOT NULL
        AND cost > 0
""")

claims_silver_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.medical_claims")

print(f"✅ Created silver table: {CATALOG}.{SILVER_SCHEMA}.medical_claims")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer - Cost Analytics Tables

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. Total Cost of Care (TCOC) by Member

# COMMAND ----------

tcoc_by_member_df = spark.sql(f"""
    SELECT
        c.member_id,
        
        -- Total cost
        SUM(c.cost) AS total_cost_12m,
        ROUND(SUM(c.cost) / 12, 2) AS avg_monthly_cost,
        
        -- Preventable costs
        SUM(CASE WHEN c.is_preventable THEN c.cost ELSE 0 END) AS preventable_cost,
        ROUND(SUM(CASE WHEN c.is_preventable THEN c.cost ELSE 0 END) / NULLIF(SUM(c.cost), 0), 3) AS pct_preventable_cost,
        
        -- Cost by category
        SUM(CASE WHEN c.claim_type = 'ER Visit' THEN c.cost ELSE 0 END) AS er_cost,
        SUM(CASE WHEN c.claim_type = 'Inpatient Hospitalization' THEN c.cost ELSE 0 END) AS inpatient_cost,
        SUM(CASE WHEN c.claim_type = 'Office Visit' THEN c.cost ELSE 0 END) AS office_visit_cost,
        SUM(CASE WHEN c.service_category = 'Diagnostic' THEN c.cost ELSE 0 END) AS diagnostic_cost,
        
        -- Utilization counts
        COUNT(DISTINCT CASE WHEN c.claim_type = 'ER Visit' THEN c.claim_id END) AS er_visits_count,
        COUNT(DISTINCT CASE WHEN c.claim_type = 'Inpatient Hospitalization' THEN c.claim_id END) AS hospitalizations_count,
        COUNT(DISTINCT CASE WHEN c.claim_type = 'Office Visit' THEN c.claim_id END) AS office_visits_count,
        
        -- Preventable utilization
        COUNT(DISTINCT CASE WHEN c.claim_type = 'ER Visit' AND c.is_preventable THEN c.claim_id END) AS preventable_er_visits,
        COUNT(DISTINCT CASE WHEN c.claim_type = 'Inpatient Hospitalization' AND c.is_preventable THEN c.claim_id END) AS preventable_hospitalizations,
        
        -- Quality metrics (join to member data)
        MAX(mq.open_gaps) AS open_gaps,
        MAX(mq.compliance_rate) AS compliance_rate,
        MAX(m.risk_level) AS clinical_risk_level,
        MAX(COALESCE(ms.sdoh_risk_classification, 'Unknown')) AS sdoh_risk,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{SILVER_SCHEMA}.medical_claims c
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_quality_summary mq
        ON c.member_id = mq.member_id
    LEFT JOIN {CATALOG}.{SILVER_SCHEMA}.members m
        ON c.member_id = m.member_id
    LEFT JOIN {CATALOG}.{GOLD_SCHEMA}.member_sdoh_enriched ms
        ON c.member_id = ms.member_id
    GROUP BY c.member_id
""")

tcoc_by_member_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.tcoc_by_member")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.tcoc_by_member")

# Show sample
spark.sql(f"""
    SELECT member_id, total_cost_12m, preventable_cost, pct_preventable_cost,
           er_visits_count, preventable_er_visits, hospitalizations_count, preventable_hospitalizations,
           open_gaps, compliance_rate
    FROM {CATALOG}.{GOLD_SCHEMA}.tcoc_by_member
    ORDER BY preventable_cost DESC
    LIMIT 10
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Preventable Cost Opportunity

# COMMAND ----------

preventable_cost_opportunity_df = spark.sql(f"""
    SELECT
        t.member_id,
        t.total_cost_12m,
        t.preventable_cost,
        t.pct_preventable_cost,
        t.preventable_er_visits,
        t.preventable_hospitalizations,
        t.open_gaps,
        t.compliance_rate,
        t.clinical_risk_level,
        t.sdoh_risk,
        
        -- Average cost per preventable event
        CASE WHEN t.preventable_er_visits > 0 
            THEN ROUND(t.preventable_cost / (t.preventable_er_visits + t.preventable_hospitalizations), 2)
            ELSE 0 
        END AS avg_cost_per_preventable_event,
        
        -- Gap closure impact estimate
        -- Assume closing gaps prevents 50% of preventable events
        ROUND(t.preventable_cost * 0.50, 2) AS potential_savings_if_gaps_closed,
        
        -- Priority score for intervention (higher = more opportunity)
        CAST(
            (t.preventable_cost / 1000) * 0.40 +  -- 40% weight on preventable cost
            (t.open_gaps * 100) * 0.30 +           -- 30% weight on number of gaps
            (1 - t.compliance_rate) * 100 * 0.20 + -- 20% weight on compliance rate
            (t.preventable_er_visits + t.preventable_hospitalizations) * 50 * 0.10  -- 10% weight on utilization
        AS INT) AS intervention_priority_score,
        
        -- Priority tier
        CASE
            WHEN (
                (t.preventable_cost / 1000) * 0.40 +
                (t.open_gaps * 100) * 0.30 +
                (1 - t.compliance_rate) * 100 * 0.20 +
                (t.preventable_er_visits + t.preventable_hospitalizations) * 50 * 0.10
            ) >= 300 THEN 'Critical'
            WHEN (
                (t.preventable_cost / 1000) * 0.40 +
                (t.open_gaps * 100) * 0.30 +
                (1 - t.compliance_rate) * 100 * 0.20 +
                (t.preventable_er_visits + t.preventable_hospitalizations) * 50 * 0.10
            ) >= 200 THEN 'High'
            WHEN (
                (t.preventable_cost / 1000) * 0.40 +
                (t.open_gaps * 100) * 0.30 +
                (1 - t.compliance_rate) * 100 * 0.20 +
                (t.preventable_er_visits + t.preventable_hospitalizations) * 50 * 0.10
            ) >= 100 THEN 'Medium'
            ELSE 'Low'
        END AS intervention_priority_tier,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{GOLD_SCHEMA}.tcoc_by_member t
    WHERE t.preventable_cost > 0
""")

preventable_cost_opportunity_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.preventable_cost_opportunity")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.preventable_cost_opportunity")

# Show top opportunities
spark.sql(f"""
    SELECT member_id, preventable_cost, potential_savings_if_gaps_closed,
           open_gaps, preventable_er_visits, preventable_hospitalizations,
           intervention_priority_score, intervention_priority_tier
    FROM {CATALOG}.{GOLD_SCHEMA}.preventable_cost_opportunity
    ORDER BY intervention_priority_score DESC
    LIMIT 10
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3. Cost Analytics by Risk Segment

# COMMAND ----------

cost_by_risk_segment_df = spark.sql(f"""
    SELECT
        clinical_risk_level,
        sdoh_risk,
        
        -- Member counts
        COUNT(DISTINCT member_id) AS total_members,
        
        -- Average costs
        AVG(total_cost_12m) AS avg_total_cost,
        AVG(preventable_cost) AS avg_preventable_cost,
        AVG(pct_preventable_cost) AS avg_pct_preventable,
        
        -- Total costs (population level)
        SUM(total_cost_12m) AS total_population_cost,
        SUM(preventable_cost) AS total_preventable_cost,
        
        -- Utilization
        AVG(er_visits_count) AS avg_er_visits,
        AVG(preventable_er_visits) AS avg_preventable_er_visits,
        AVG(hospitalizations_count) AS avg_hospitalizations,
        AVG(preventable_hospitalizations) AS avg_preventable_hospitalizations,
        
        -- Quality metrics
        AVG(open_gaps) AS avg_open_gaps,
        AVG(compliance_rate) AS avg_compliance_rate,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{GOLD_SCHEMA}.tcoc_by_member
    GROUP BY clinical_risk_level, sdoh_risk
    ORDER BY avg_total_cost DESC
""")

cost_by_risk_segment_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.cost_by_risk_segment")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.cost_by_risk_segment")

# Display results
spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.cost_by_risk_segment ORDER BY avg_total_cost DESC").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4. Gap Closure ROI Projections

# COMMAND ----------

gap_closure_roi_df = spark.sql(f"""
    SELECT
        -- Aggregate all members with gaps
        COUNT(DISTINCT member_id) AS members_with_gaps,
        SUM(open_gaps) AS total_open_gaps,
        
        -- Current state costs
        SUM(preventable_cost) AS total_preventable_cost,
        AVG(preventable_cost) AS avg_preventable_cost_per_member,
        
        -- Utilization
        SUM(preventable_er_visits) AS total_preventable_er_visits,
        SUM(preventable_hospitalizations) AS total_preventable_hospitalizations,
        
        -- ROI projections (if we close 70% of gaps)
        ROUND(SUM(preventable_cost) * 0.70 * 0.50, 2) AS projected_savings_70pct_closure,
        ROUND(SUM(preventable_cost) * 0.50 * 0.50, 2) AS projected_savings_50pct_closure,
        ROUND(SUM(preventable_cost) * 0.30 * 0.50, 2) AS projected_savings_30pct_closure,
        
        -- Average cost per gap closed
        ROUND(SUM(preventable_cost) / NULLIF(SUM(open_gaps), 0), 2) AS avg_savings_per_gap_closed,
        
        CURRENT_TIMESTAMP() AS created_at
        
    FROM {CATALOG}.{GOLD_SCHEMA}.preventable_cost_opportunity
    WHERE open_gaps > 0
""")

gap_closure_roi_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.gap_closure_roi_projections")

print(f"✅ Created gold table: {CATALOG}.{GOLD_SCHEMA}.gap_closure_roi_projections")

# Display projections
spark.sql(f"SELECT * FROM {CATALOG}.{GOLD_SCHEMA}.gap_closure_roi_projections").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("="*80)
print("CLAIMS COST ANALYSIS COMPLETE")
print("="*80)

# Aggregate stats
total_claims = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.medical_claims").count()
total_members_with_claims = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.tcoc_by_member").count()

# Cost summary
cost_summary = spark.sql(f"""
    SELECT
        SUM(total_cost_12m) / 1000000 AS total_cost_millions,
        SUM(preventable_cost) / 1000000 AS preventable_cost_millions,
        AVG(total_cost_12m) AS avg_cost_per_member,
        SUM(preventable_er_visits) AS total_preventable_er,
        SUM(preventable_hospitalizations) AS total_preventable_hosp
    FROM {CATALOG}.{GOLD_SCHEMA}.tcoc_by_member
""").collect()[0]

# ROI projection
roi_projection = spark.sql(f"""
    SELECT
        projected_savings_70pct_closure / 1000000 AS savings_70pct_millions,
        projected_savings_50pct_closure / 1000000 AS savings_50pct_millions,
        avg_savings_per_gap_closed
    FROM {CATALOG}.{GOLD_SCHEMA}.gap_closure_roi_projections
""").collect()[0]

print(f"\n📊 CLAIMS DATA:")
print(f"   • Total claims generated: {total_claims:,}")
print(f"   • Members with claims: {total_members_with_claims:,}")

print(f"\n💰 COST SUMMARY:")
print(f"   • Total cost (12 months): ${cost_summary['total_cost_millions']:.2f}M")
print(f"   • Preventable cost: ${cost_summary['preventable_cost_millions']:.2f}M")
print(f"   • Avg cost per member: ${cost_summary['avg_cost_per_member']:,.2f}")

print(f"\n🚨 PREVENTABLE UTILIZATION:")
print(f"   • Preventable ER visits: {cost_summary['total_preventable_er']:,}")
print(f"   • Preventable hospitalizations: {cost_summary['total_preventable_hosp']:,}")

print(f"\n📈 ROI PROJECTIONS:")
print(f"   • If 70% gap closure: ${roi_projection['savings_70pct_millions']:.2f}M saved")
print(f"   • If 50% gap closure: ${roi_projection['savings_50pct_millions']:.2f}M saved")
print(f"   • Avg savings per gap closed: ${roi_projection['avg_savings_per_gap_closed']:,.2f}")

print(f"\n✅ Ready for ROI calculator!")
print("="*80)

