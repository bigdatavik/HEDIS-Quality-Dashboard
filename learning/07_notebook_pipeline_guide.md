# HEDIS Quality Dashboard - Notebook Pipeline Guide

## Overview

The HEDIS Quality Dashboard uses a **9-notebook data pipeline** following the **Medallion Architecture** (Bronze → Silver → Gold) to transform raw healthcare data into actionable analytics for Medicare Advantage quality improvement.

**Pipeline Stages:**
1. **Notebooks 01-03:** Core HEDIS data (Members, Clinical Measures, Quality Scores)
2. **Notebook 04:** UC Functions for HEDIS queries
3. **Notebook 05:** Knowledge documents for MCP/AI
4. **Notebooks 06-08:** SDOH + ROI + Geospatial enhancement
5. **Notebook 09:** UC Functions for ROI/SDOH queries

**Total Output:**
- **50+ Delta tables** across Bronze, Silver, and Gold layers
- **12 Unity Catalog functions** for natural language queries
- **8 knowledge documents** (~68 KB) for AI context

---

## Medallion Architecture

### Bronze Layer (Raw Data)
- **Purpose:** Store raw, unprocessed data exactly as received
- **Characteristics:** 
  - Immutable
  - Full history
  - Minimal validation
- **Tables:** 15 total
- **Retention:** Long-term (source of truth)

### Silver Layer (Cleaned & Validated)
- **Purpose:** Clean, deduplicate, and validate data
- **Characteristics:**
  - Data quality rules applied
  - Schema enforcement
  - Business keys validated
- **Tables:** 10 total
- **Retention:** Medium-term (queryable clean data)

### Gold Layer (Business-Ready Analytics)
- **Purpose:** Aggregated, denormalized tables for analytics
- **Characteristics:**
  - Optimized for queries
  - Pre-calculated metrics
  - Dashboard-ready
- **Tables:** 25+ total
- **Retention:** Short-term (can be rebuilt)

---

## Execution Order & Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXECUTION SEQUENCE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  01: Bronze Ingestion (8 min)                                   │
│      └─> Creates members, clinical measures, gaps, scores       │
│          │                                                       │
│          ▼                                                       │
│  02: Silver Transformation (<1 min)                             │
│      └─> Cleans and validates bronze data                       │
│          │                                                       │
│          ▼                                                       │
│  03: Gold Aggregation (<1 min)                                  │
│      └─> Creates analytics tables                               │
│          │                                                       │
│          ├──────────────────────────┬──────────────────────┐    │
│          ▼                          ▼                      ▼    │
│  04: UC Functions     06: SDOH Integration    05: Knowledge     │
│      (<1 min)             (1 min)                 Docs Upload   │
│      └─> HEDIS         └─> Census, SVI, ADI      (<1 min)      │
│          lookups           │                     └─> MCP docs   │
│                           ▼                                     │
│                   07: Claims Cost (1 min)                       │
│                       └─> Medical claims, TCOC, ROI             │
│                           │                                     │
│                           ├──────────────────┐                  │
│                           ▼                  ▼                  │
│                   08: Geospatial     09: ROI UC Functions       │
│                       (1 min)            (<1 min)               │
│                       └─> Geocoding    └─> ROI/SDOH            │
│                           Heat maps         queries             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Total Pipeline Runtime: ~12 minutes
```

**Dependency Rules:**
- **Linear:** 01 → 02 → 03 must run sequentially
- **Parallel:** After 03 completes, notebooks 04, 05, and 06 can run in parallel
- **Sequential:** 06 → 07 → 08 → 09 must run in order

---

## Detailed Notebook Explanations

### Notebook 01: Bronze Layer Ingestion
**File:** `notebooks/01_ingest_to_bronze.py`

**Purpose:** Generate synthetic HEDIS member and clinical quality data for demonstration purposes.

**What It Does:**
- Creates 5,000 synthetic members with realistic demographics
- Generates 40,000+ clinical measures across 8 HEDIS measures
- Simulates quality scores and gap tracking over time
- Produces realistic data distributions for demo/testing

**Tables Created (Bronze):**
| Table | Rows | Description |
|-------|------|-------------|
| `members_raw` | 5,000 | Member demographics and enrollment |
| `clinical_measures_raw` | ~40,000 | HEDIS measure results by member |
| `gap_tracking_raw` | ~15,000 | Open and closed gaps history |
| `quality_scores_raw` | 12 | Yearly quality score trends |

**Key Features:**
- Realistic age/gender distributions
- Risk stratification (High/Medium/Low)
- Measure codes: BCS, CDC, CBP, COL, CIS, W15, AWC, PPC
- Compliance rates: 70-95% by measure

**Runtime:** ~8 minutes (generates large synthetic dataset)

**Dependencies:** None (first notebook to run)

**When to Run:**
- Initial project setup
- Data refresh (quarterly or annual)
- Testing new features with fresh data

---

### Notebook 02: Silver Transformation
**File:** `notebooks/02_bronze_to_silver.py`

**Purpose:** Clean, validate, and standardize raw data for analytics consumption.

**What It Does:**
- Removes duplicates and invalid records
- Standardizes date formats and codes
- Applies data quality rules
- Creates validated, query-ready tables

**Tables Created (Silver):**
| Table | Description |
|-------|-------------|
| `members` | Validated members with data quality checks |
| `clinical_measures` | Cleaned measure results with valid codes |
| `measure_definitions` | Reference table for HEDIS measures |
| `gap_tracking` | Validated gap status and closures |
| `quality_scores` | Verified quality score trends |

**Data Quality Rules Applied:**
- Age validation (must be 0-120)
- Date validation (enrollment before today)
- Code validation (only valid HEDIS codes)
- Duplicate removal (by member_id + measure_code + date)

**Runtime:** <1 minute

**Dependencies:** Notebook 01 (needs bronze tables)

**When to Run:**
- After bronze ingestion
- When bronze data changes
- During data quality audits

---

### Notebook 03: Gold Aggregation
**File:** `notebooks/03_silver_to_gold.py`

**Purpose:** Create business-ready analytics tables optimized for dashboard queries and reporting.

**What It Does:**
- Aggregates data to member, measure, and time-period levels
- Pre-calculates key metrics (compliance rates, gap counts)
- Creates denormalized tables for fast queries
- Generates dashboard-ready data

**Tables Created (Gold):**
| Table | Description | Use Case |
|-------|-------------|----------|
| `member_quality_summary` | Per-member metrics | Member lookup, quality profiles |
| `measure_performance` | Per-measure compliance | Measure comparison, trends |
| `open_gaps_dashboard` | Current open gaps | Gap closure prioritization |
| `gap_closure_analytics` | Gap closure trends | Performance tracking |
| `quality_trends` | Year-over-year trends | Executive reporting |
| `ncqa_percentile_scores` | NCQA benchmarking | Star Rating projections |
| `provider_performance` | Provider-level metrics | Provider scorecards |

**Key Metrics Calculated:**
- Overall quality score (0-100)
- Compliance rate (% measures met)
- Gap closure rate (% gaps closed)
- Stars rating projection (1-5)
- NCQA percentile rank

**Runtime:** <1 minute

**Dependencies:** Notebook 02 (needs silver tables)

**When to Run:**
- After silver transformation
- Before accessing dashboard
- When updating analytics

---

### Notebook 04: UC Functions (Original HEDIS)
**File:** `notebooks/04_create_uc_functions.py`

**Purpose:** Create Unity Catalog functions to enable natural language queries via Genie and MCP.

**What It Does:**
- Creates reusable SQL functions in Unity Catalog
- Enables "lookup" pattern for common queries
- Powers natural language search in dashboard
- Supports MCP (Model Context Protocol) integration

**UC Functions Created (6):**

1. **`lookup_member(member_id)`**
   - Returns: Member demographics and quality summary
   - Example: "Show me member M000123"

2. **`lookup_open_gaps(member_id)`**
   - Returns: All open gaps for a member
   - Example: "What gaps does member M000123 have?"

3. **`lookup_closed_gaps(member_id)`**
   - Returns: Recently closed gaps
   - Example: "Show closed gaps for member M000123"

4. **`members_with_measure_gaps(measure_code)`**
   - Returns: All members with gaps for specific measure
   - Example: "Who has open BCS gaps?"

5. **`get_measure_performance(measure_code)`**
   - Returns: Performance metrics for a measure
   - Example: "How are we doing on diabetes care?"

6. **`list_high_risk_members()`**
   - Returns: Members in High risk category
   - Example: "Show me high risk members"

**Schema:** `humana_quality.hedis_gold`

**Runtime:** <1 minute

**Dependencies:** Notebook 03 (needs gold tables)

**When to Run:**
- After gold aggregation
- When adding new query patterns
- Before enabling MCP search

---

### Notebook 05: Knowledge Docs Upload
**File:** `notebooks/05_upload_knowledge_docs.py`

**Purpose:** Upload knowledge documents to Unity Catalog Volume for AI/MCP context.

**What It Does:**
- Copies knowledge documents from bundle to UC Volume
- Makes documents available to Knowledge Assistant
- Provides context for natural language queries
- Supports MCP integration

**Documents Uploaded (8 total, ~68 KB):**

**Original 4 Documents:**
1. **gap_closure_protocols.txt** (7.5 KB)
   - Gap closure workflows and procedures
   - Outreach strategies
   - Care coordination best practices

2. **hedis_measures_guide.txt** (4.7 KB)
   - HEDIS measure definitions
   - Specifications and codes
   - Compliance requirements

3. **ncqa_quality_guidelines.txt** (5.3 KB)
   - NCQA accreditation standards
   - Quality improvement protocols
   - Audit requirements

4. **quality_team_communications.txt** (9.0 KB)
   - Common questions and answers
   - Team procedures
   - Communication templates

**NEW 4 Documents (SDOH + ROI):**
5. **cms_health_equity_guidelines.txt** (9.6 KB)
   - CMS Framework for Health Equity 2022-2032
   - Health equity measures in Star Ratings
   - Social needs screening protocols
   - Disparity measurement methods
   - CMS bonus payments for equity

6. **value_based_care_best_practices.txt** (10.0 KB)
   - VBC contract structures
   - Quality measure optimization
   - Provider engagement strategies
   - Shared savings calculations
   - ROI of VBC programs

7. **social_needs_screening.txt** (10.8 KB)
   - Validated screening tools (PRAPARE, AHC-HRSN)
   - 5 core domains (food, housing, transport, utilities, safety)
   - Implementation workflows
   - Intervention strategies
   - Community partnerships

8. **roi_calculation_methods.txt** (10.7 KB)
   - ROI formulas and components
   - Avoided medical cost calculations
   - Star Rating revenue impact
   - NPV and payback period
   - Sensitivity analysis

**UC Volume Path:** `/Volumes/humana_quality/hedis_gold/knowledge_docs`

**Runtime:** <1 minute

**Dependencies:** None (standalone)

**When to Run:**
- After deploying bundle (files must be in workspace)
- When adding new knowledge documents
- Before creating Knowledge Assistant endpoint

**Note:** Uses dual-method upload (dbutils.fs.cp with fallback to read/write) for reliability.

---

### Notebook 06: SDOH Integration
**File:** `notebooks/06_integrate_sdoh_data.py`

**Purpose:** Enrich member data with Social Determinants of Health (SDOH) factors to identify non-medical barriers to care.

**What It Does:**
- Generates synthetic SDOH data by ZIP code
- Simulates Census demographics, CDC SVI, ADI data
- Identifies food deserts, provider deserts, transportation barriers
- Links SDOH risk to quality performance
- Creates composite risk scores

**Data Sources Simulated:**
- **Census Bureau:** Income, poverty, education, housing
- **CDC Social Vulnerability Index (SVI):** 4-theme vulnerability scoring
- **Area Deprivation Index (ADI):** Neighborhood disadvantage (1-100)
- **USDA/HRSA:** Food deserts, provider access

**Tables Created (11 total):**

**Bronze (4 tables):**
- `census_demographics_raw` - Raw census data
- `cdc_svi_raw` - Social vulnerability scores
- `adi_raw` - Area deprivation scores
- `access_barriers_raw` - Food/provider deserts

**Silver (4 tables):**
- `census_demographics` - Validated census
- `cdc_svi` - Validated SVI
- `adi` - Validated ADI
- `access_barriers` - Validated barriers

**Gold (3 tables):**
- `zip_sdoh_summary` - Composite SDOH by ZIP
- `member_sdoh_enriched` - Members + SDOH factors
- `quality_by_sdoh_risk` - Quality metrics by SDOH risk level

**Key Metrics Generated:**
- Median household income by ZIP
- Poverty rate (0-0.45)
- SVI percentile (0-100, higher = more vulnerable)
- ADI score (1-100, higher = more disadvantaged)
- Composite risk score (0-100, combines all factors)
- Risk classification: Very Low, Low, Moderate Risk, High Risk

**Use Cases Enabled:**
- Health equity analysis
- Disparity identification
- Targeted outreach planning
- CMS health equity bonus eligibility

**Runtime:** ~1 minute

**Dependencies:** Notebook 02 (needs members table for ZIP codes)

**When to Run:**
- After silver transformation
- When analyzing health equity
- Before claims cost analysis

---

### Notebook 07: Claims Cost Analysis
**File:** `notebooks/07_claims_cost_analysis.py`

**Purpose:** Generate synthetic medical claims and calculate Total Cost of Care (TCOC) to quantify ROI for gap closure initiatives.

**What It Does:**
- Generates realistic medical claims (ER, hospitalizations, office visits, labs)
- Flags preventable events linked to quality gaps
- Calculates TCOC per member
- Projects ROI at different gap closure rates
- Identifies high-ROI intervention targets

**Claims Generated (~50K-100K total):**
- **ER Visits:** 800-1,200 annually (30-40% preventable)
- **Hospitalizations:** 150-250 annually (40-50% preventable)
- **Office Visits:** 15,000-25,000 annually
- **Diagnostic Tests:** 8,000-12,000 annually

**Preventability Logic:**
- Diabetes gaps → Higher risk of diabetic ER visits
- BP gaps → Higher risk of hypertensive crisis
- Screening gaps → Late-stage cancer diagnosis
- Compliance rate affects event probability

**Tables Created (5 total):**

**Bronze (1 table):**
- `medical_claims_raw` - Raw claims with cost

**Silver (1 table):**
- `medical_claims` - Validated claims

**Gold (4 tables):**
1. **`tcoc_by_member`** - Total cost of care per member
   - 12-month cost summary
   - Preventable vs non-preventable split
   - Utilization counts

2. **`preventable_cost_opportunity`** - ROI targets
   - Preventable cost by member
   - Intervention priority score
   - Projected savings if gaps closed

3. **`cost_by_risk_segment`** - Costs by risk level
   - Average costs by clinical + SDOH risk
   - Population-level totals

4. **`gap_closure_roi_projections`** - ROI scenarios
   - Savings at 30%, 50%, 70% closure rates
   - Average savings per gap closed

**Key Insights Generated:**
- Total preventable cost: **$2-4M annually** (for 5K members)
- Average cost per preventable event: $8,000-15,000
- Average savings per gap closed: $200-400
- ROI projections:
  - 30% closure: $890K saved
  - 50% closure: $1.48M saved
  - 70% closure: $2.07M saved

**Use Cases Enabled:**
- ROI calculation for gap closure initiatives
- Budget justification for quality programs
- Member prioritization (highest cost opportunity)
- Executive reporting

**Runtime:** <1 minute

**Dependencies:** Notebooks 03, 06 (needs quality summary and SDOH data)

**When to Run:**
- After SDOH integration
- When calculating ROI
- Before geospatial analysis

---

### Notebook 08: Geospatial Enrichment
**File:** `notebooks/08_geospatial_enrichment.py`

**Purpose:** Add geographic coordinates and create heat maps for mobile clinic deployment and geographic targeting.

**What It Does:**
- Geocodes all ZIP codes (latitude/longitude)
- Creates member geographic enrichment
- Identifies gap hotspots for targeted interventions
- Generates measure-specific geography
- Calculates mobile clinic priority scores

**Geocoding:**
- Simulates Phoenix, AZ metro area (~50 mile radius)
- 58 unique ZIP codes geocoded
- Realistic city assignments (Phoenix, Scottsdale, Tempe, Mesa, etc.)

**Tables Created (4 total):**

**Bronze (1 table):**
- `zip_geocoding_raw` - Raw geocoding data

**Silver (1 table):**
- `zip_geocoding` - Validated lat/long

**Gold (2 tables):**
1. **`zip_geographic_summary`** - Quality + SDOH + Cost by ZIP
   - Member counts by ZIP
   - Average compliance rate
   - Total open gaps
   - SDOH risk factors
   - Preventable costs
   - Gap concentration score

2. **`member_geographic`** - Geocoded members
   - Every member with lat/long
   - Quality + SDOH + Cost joined

3. **`gap_hotspots`** - Mobile clinic priorities
   - ZIP-level gap concentrations
   - Mobile clinic priority score (0-500)
   - Priority tiers: Critical, High, Medium, Low
   - SDOH barriers by ZIP

4. **`measure_gap_geography`** - Measure-specific heat maps
   - Gap clustering by HEDIS measure
   - Example: BCS (mammography) gaps by ZIP

**Mobile Clinic Priority Score Formula:**
```
Priority = (Total Gaps / 10) × 0.30 +
           (Gap Concentration) × 0.25 +
           (High SDOH Risk) × 0.20 +
           (Preventable Cost / 1000) × 0.15 +
           (Provider Desert) × 0.10
```

**Priority Tiers:**
- **Critical - Deploy First:** Score ≥300 (8-12 ZIPs)
- **High Priority:** Score 200-299 (15-20 ZIPs)
- **Medium Priority:** Score 100-199
- **Low Priority:** Score <100

**Use Cases Enabled:**
- Mobile clinic deployment planning
- Geographic targeting for outreach
- Heat map visualizations
- Resource allocation by geography
- Transportation barrier identification

**Runtime:** <1 minute

**Dependencies:** Notebooks 02, 03, 06 (needs members, quality, SDOH)

**When to Run:**
- After claims cost analysis
- When planning mobile clinics
- Before creating ROI UC functions

---

### Notebook 09: ROI UC Functions
**File:** `notebooks/09_create_roi_uc_functions.py`

**Purpose:** Create Unity Catalog functions for ROI analysis, SDOH queries, and cost calculations to enable natural language MCP queries.

**What It Does:**
- Creates SQL functions in Unity Catalog
- Enables ROI and SDOH queries via Genie/MCP
- Powers advanced analytics in dashboard
- Supports scenario planning

**UC Functions Created (6):**

1. **`calculate_gap_cost_impact(member_id)`**
   - **Returns:** Preventable costs, events, savings potential for a member
   - **Use Case:** Individual ROI analysis
   - **Example Query:** "What's the cost impact for member M000123?"
   - **Output:** Open gaps, preventable cost, ER visits, hospitalizations, potential savings

2. **`identify_high_roi_members()`**
   - **Returns:** Top 100 members for gap closure (Critical/High priority)
   - **Use Case:** Target list generation
   - **Example Query:** "Who should we prioritize for outreach?"
   - **Output:** Members sorted by intervention priority score

3. **`get_sdoh_risk_factors(zip_code)`**
   - **Returns:** Full SDOH profile for a ZIP code
   - **Use Case:** Understanding neighborhood context
   - **Example Query:** "What are the SDOH factors for ZIP 85001?"
   - **Output:** Poverty, SVI, ADI, barriers, risk classification

4. **`members_in_high_risk_zips()`**
   - **Returns:** All members in High SDOH risk areas
   - **Use Case:** Health equity targeting
   - **Example Query:** "Show members in high-risk neighborhoods"
   - **Output:** Members with SDOH barriers

5. **`calculate_roi_projection(closure_rate_pct)`**
   - **Returns:** Projected savings at any closure rate (0.0-1.0)
   - **Use Case:** Scenario planning
   - **Example Query:** "What's the ROI if we close 65% of gaps?"
   - **Output:** Gaps closed, projected savings, avg savings per gap

6. **`get_preventable_cost_by_zip()`**
   - **Returns:** Preventable costs and mobile clinic priorities by ZIP
   - **Use Case:** Geographic targeting
   - **Example Query:** "Which ZIPs should we deploy mobile clinics to?"
   - **Output:** ZIPs sorted by mobile clinic priority score

**Example Usage:**

```sql
-- High-ROI members
SELECT * FROM humana_quality.hedis_gold.identify_high_roi_members();

-- SDOH factors for a ZIP
SELECT * FROM humana_quality.hedis_gold.get_sdoh_risk_factors('85001');

-- ROI projection at 70% closure
SELECT * FROM humana_quality.hedis_gold.calculate_roi_projection(0.70);

-- Top 10 ZIPs for mobile clinics
SELECT * FROM humana_quality.hedis_gold.get_preventable_cost_by_zip()
ORDER BY mobile_clinic_priority_score DESC LIMIT 10;
```

**Schema:** `humana_quality.hedis_gold`

**Runtime:** <1 minute

**Dependencies:** Notebooks 06, 07, 08 (needs SDOH, cost, geo tables)

**When to Run:**
- After geospatial enrichment
- When enabling MCP queries
- Before dashboard deployment

---

## Tables Summary

### Complete Table Inventory

**Bronze Layer (15 tables):**
- Core HEDIS: `members_raw`, `clinical_measures_raw`, `gap_tracking_raw`, `quality_scores_raw`
- SDOH: `census_demographics_raw`, `cdc_svi_raw`, `adi_raw`, `access_barriers_raw`
- Cost: `medical_claims_raw`
- Geospatial: `zip_geocoding_raw`

**Silver Layer (10 tables):**
- Core HEDIS: `members`, `clinical_measures`, `measure_definitions`, `gap_tracking`, `quality_scores`
- SDOH: `census_demographics`, `cdc_svi`, `adi`, `access_barriers`
- Cost: `medical_claims`
- Geospatial: `zip_geocoding`

**Gold Layer (25+ tables):**
- Core HEDIS: `member_quality_summary`, `measure_performance`, `open_gaps_dashboard`, `gap_closure_analytics`, `quality_trends`, `ncqa_percentile_scores`, `provider_performance`
- SDOH: `zip_sdoh_summary`, `member_sdoh_enriched`, `quality_by_sdoh_risk`
- Cost: `tcoc_by_member`, `preventable_cost_opportunity`, `cost_by_risk_segment`, `gap_closure_roi_projections`
- Geospatial: `zip_geographic_summary`, `member_geographic`, `gap_hotspots`, `measure_gap_geography`

**Total: 50+ tables**

### Data Volume Estimates

| Layer | Tables | Approx Rows | Storage |
|-------|--------|-------------|---------|
| Bronze | 15 | ~110K | ~50 MB |
| Silver | 10 | ~70K | ~30 MB |
| Gold | 25+ | ~30K | ~20 MB |
| **Total** | **50+** | **~210K** | **~100 MB** |

*For 5,000 member population. Scales linearly.*

---

## UC Functions Summary

### All 12 Functions

**HEDIS Functions (from Notebook 04):**
1. `lookup_member(member_id)`
2. `lookup_open_gaps(member_id)`
3. `lookup_closed_gaps(member_id)`
4. `members_with_measure_gaps(measure_code)`
5. `get_measure_performance(measure_code)`
6. `list_high_risk_members()`

**ROI/SDOH Functions (from Notebook 09):**
7. `calculate_gap_cost_impact(member_id)`
8. `identify_high_roi_members()`
9. `get_sdoh_risk_factors(zip_code)`
10. `members_in_high_risk_zips()`
11. `calculate_roi_projection(closure_rate_pct)`
12. `get_preventable_cost_by_zip()`

**Schema:** `humana_quality.hedis_gold`

**Purpose:** Enable natural language queries via Genie and MCP (Model Context Protocol)

---

## Use Cases by Notebook

### Notebook 01: Bronze Ingestion
**Enables:**
- Data foundation for entire pipeline
- Realistic testing and demos
- Training and onboarding
- Data refresh workflows

### Notebook 02: Silver Transformation
**Enables:**
- Clean data for analytics
- Data quality assurance
- Consistent business rules
- Queryable source of truth

### Notebook 03: Gold Aggregation
**Enables:**
- Dashboard visualizations
- Executive reporting
- Quality scorecards
- Trend analysis
- Star Rating projections

### Notebook 04: UC Functions
**Enables:**
- Natural language queries ("Show me member M000123")
- Genie Space integration
- MCP search in dashboard
- Ad-hoc analysis

### Notebook 05: Knowledge Docs
**Enables:**
- AI-powered question answering
- Knowledge Assistant queries
- Contextual help for quality team
- Policy and procedure lookup

### Notebook 06: SDOH Integration
**Enables:**
- Health equity analysis
- Disparity identification
- CMS health equity bonus eligibility
- Targeted interventions by SDOH risk
- Root cause analysis

### Notebook 07: Claims Cost Analysis
**Enables:**
- ROI calculation for gap closure
- Budget justification ($2-4M opportunity)
- Cost-benefit analysis
- Executive presentations
- Preventable event identification

### Notebook 08: Geospatial Enrichment
**Enables:**
- Mobile clinic deployment planning
- Geographic heat maps
- Transportation barrier analysis
- Resource allocation by ZIP
- Targeted outreach campaigns

### Notebook 09: ROI UC Functions
**Enables:**
- ROI queries via natural language
- Scenario planning (closure rates)
- Member prioritization
- Geographic targeting
- SDOH-aware analytics

---

## Running the Pipeline

### Full Pipeline Execution

```bash
# Deploy bundle
databricks bundle deploy --profile DEFAULT

# Run all jobs in order
databricks bundle run bronze_ingestion_job --profile DEFAULT           # ~8 min
databricks bundle run silver_transformation_job --profile DEFAULT      # <1 min
databricks bundle run gold_aggregation_job --profile DEFAULT           # <1 min

# Parallel execution (can run simultaneously after gold)
databricks bundle run uc_functions_job --profile DEFAULT               # <1 min
databricks bundle run knowledge_docs_job --profile DEFAULT             # <1 min
databricks bundle run sdoh_integration_job --profile DEFAULT           # ~1 min

# Sequential execution (must run in order)
databricks bundle run claims_cost_analysis_job --profile DEFAULT       # <1 min
databricks bundle run geospatial_enrichment_job --profile DEFAULT      # <1 min
databricks bundle run roi_uc_functions_job --profile DEFAULT           # <1 min

# Total runtime: ~12 minutes
```

### Incremental Updates

**Refresh Core Data Only:**
```bash
databricks bundle run bronze_ingestion_job --profile DEFAULT
databricks bundle run silver_transformation_job --profile DEFAULT
databricks bundle run gold_aggregation_job --profile DEFAULT
# Runtime: ~9 minutes
```

**Update Knowledge Docs Only:**
```bash
databricks bundle run knowledge_docs_job --profile DEFAULT
# Runtime: <1 minute
```

**Rebuild Analytics Only:**
```bash
databricks bundle run gold_aggregation_job --profile DEFAULT
# Runtime: <1 minute
```

---

## Troubleshooting

### Common Issues

**Issue:** Notebook 01 times out
- **Cause:** Generating large synthetic dataset
- **Fix:** Reduce member count in notebook or use larger cluster

**Issue:** Notebook 05 fails to upload new documents
- **Cause:** Files not accessible in deployed bundle workspace
- **Fix:** Ensure files are in `data/knowledge_content/` and bundle is redeployed

**Issue:** Notebook 07 fails with column not found
- **Cause:** Missing SDOH tables
- **Fix:** Run Notebook 06 first

**Issue:** UC Functions return empty results
- **Cause:** Tables not populated
- **Fix:** Run Notebooks 01-03 to populate base tables

### Verification Queries

**Check table counts:**
```sql
-- Bronze
SELECT COUNT(*) FROM humana_quality.hedis_bronze.members_raw;

-- Silver
SELECT COUNT(*) FROM humana_quality.hedis_silver.members;

-- Gold
SELECT COUNT(*) FROM humana_quality.hedis_gold.member_quality_summary;
```

**Test UC Functions:**
```sql
-- HEDIS function
SELECT * FROM humana_quality.hedis_gold.lookup_member('M000001');

-- ROI function
SELECT * FROM humana_quality.hedis_gold.identify_high_roi_members() LIMIT 5;
```

**Check Knowledge Docs:**
```sql
-- List files in volume
LIST '/Volumes/humana_quality/hedis_gold/knowledge_docs';
```

---

## Related Documentation

- **[01_star_ratings_explained.md](01_star_ratings_explained.md)** - Why Star Ratings matter, financial impact
- **[02_gap_closure_initiatives.md](02_gap_closure_initiatives.md)** - ROI of gap closure programs
- **[03_hedis_measures_overview.md](03_hedis_measures_overview.md)** - HEDIS measure specifications
- **[04_project_enhancement_options.md](04_project_enhancement_options.md)** - Strategic enhancement options
- **[05_roi_and_business_case.md](05_roi_and_business_case.md)** - Financial modeling and ROI
- **[06_payer_industry_context.md](06_payer_industry_context.md)** - Medicare Advantage market landscape
- **[README.md](README.md)** - Learning library index

---

## Summary

The 9-notebook pipeline transforms raw HEDIS data into comprehensive analytics covering:
- ✅ Core quality measures and gap tracking
- ✅ Social determinants of health
- ✅ Medical claims and cost analysis
- ✅ Geographic intelligence and heat maps
- ✅ ROI calculations and projections
- ✅ Natural language query capabilities
- ✅ AI-powered knowledge assistance

**Total Output:** 50+ tables, 12 UC functions, 8 knowledge documents

**Total Runtime:** ~12 minutes for full pipeline

**Use Cases:** Gap closure prioritization, ROI analysis, mobile clinic planning, health equity tracking, Star Rating improvement, executive reporting

---

*Last Updated: October 31, 2025*
*Pipeline Version: 2.0 (SDOH + ROI + Geospatial Enhancement)*

