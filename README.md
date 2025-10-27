# HEDIS Quality Measures Dashboard 📊

**Interactive NCQA compliance tracking for quality teams**

## Overview

This project provides a comprehensive HEDIS (Healthcare Effectiveness Data and Information Set) quality measures dashboard for tracking NCQA compliance and gap closure analytics. The dashboard demonstrates quality score improvement from **85% → 92%** across all measures.

---

## 🚀 Deployment Status

### ✅ ALL SYSTEMS OPERATIONAL

- **📊 Dashboard**: https://hedis-quality-dashboard-984752964297111.11.azure.databricksapps.com
- **🗄️ Data Catalog**: `humana_quality`
- **📈 Quality Score**: 92% (up from 85%)
- **⭐ Stars Rating**: 4.5 Stars
- **📊 Total Members**: 10,000
- **🎯 Gap Closure Rate**: 75%

---

## 📊 Dashboard Features

### 1. Overview Tab
- Overall quality score trend (85% → 92%)
- Compliance rate tracking
- Stars rating (4.5⭐)
- NCQA percentile ranking (85th)
- Gap closure metrics

### 2. Measure Performance
- Individual HEDIS measure compliance rates
- BCS (Breast Cancer Screening): 92%
- CDC (Comprehensive Diabetes Care): 89%
- CBP (Controlling High Blood Pressure): 88%
- COL (Colorectal Cancer Screening): 85%
- Detailed performance metrics by measure

### 3. Gap Analysis
- Total gaps identified and closed
- Gap closure rate by measure
- Average days to close gaps
- Current open gaps table
- Priority-based filtering (High/Medium/Low)

### 4. Member Insights
- Member quality distribution
- Risk level stratification
- At-risk members (compliance < 70%)
- Compliance rate histogram
- Member demographics

### 5. Member Lookup
- Search by Member ID, name
- Individual member quality metrics
- Open gaps for specific members
- Action tracking and assignment

---

## 🏗️ Architecture

### Medallion Data Pipeline

#### 🥉 Bronze Layer (`humana_quality.hedis_bronze`)
- **members_raw**: Raw member enrollment data (10,000 members)
- **clinical_measures_raw**: HEDIS measure records (3 years)
- **gap_tracking_raw**: Gap closure tracking
- **quality_scores_raw**: Aggregate quality scores

#### 🥈 Silver Layer (`humana_quality.hedis_silver`)
- **members**: Cleaned and deduplicated member data
- **clinical_measures**: Validated HEDIS measures
- **gap_tracking**: Cleaned gap records
- **quality_scores**: Validated quality trends

#### 🥇 Gold Layer (`humana_quality.hedis_gold`)
- **member_quality_summary**: Member-level quality metrics
- **measure_performance**: HEDIS measure trends by year
- **gap_closure_analytics**: Gap closure rates and metrics
- **quality_trends**: Year-over-year quality improvements
- **open_gaps_dashboard**: Current open gaps for intervention

---

## 🔧 Unity Catalog Functions (MCP-Ready)

The project includes 6 UC functions for natural language queries:

1. **`lookup_member(member_id)`** - Get member demographics and quality summary
2. **`lookup_member_measures(member_id)`** - Get all measures for a member
3. **`lookup_member_gaps(member_id)`** - Get open gaps for a member
4. **`members_with_gap(measure_code)`** - Find members with specific gap (e.g., 'BCS')
5. **`lookup_measure_performance(measure_code)`** - Get performance trends by measure
6. **`members_at_risk()`** - Get members with low compliance (<70%)

**Example Queries:**
```sql
-- Get member details
SELECT * FROM humana_quality.hedis_gold.lookup_member('M000001');

-- Find all members missing breast cancer screening
SELECT * FROM humana_quality.hedis_gold.members_with_gap('BCS');

-- Get at-risk members for outreach
SELECT * FROM humana_quality.hedis_gold.members_at_risk();
```

---

## 📚 Knowledge Documents

Four comprehensive knowledge documents uploaded to `/Volumes/humana_quality/hedis_gold/knowledge_docs/`:

1. **hedis_measures_guide.txt** - HEDIS specifications, compliance criteria, Stars ratings
2. **ncqa_quality_guidelines.txt** - NCQA audit requirements, quality improvement strategies
3. **gap_closure_protocols.txt** - Standard operating procedures for gap closure
4. **quality_team_communications.txt** - FAQs, contact information, quick reference

---

## 🎯 Key Metrics & Improvements

### Quality Performance
- **2 years ago**: 85% compliance, 3.5 Stars
- **1 year ago**: 90% compliance, 4.0 Stars
- **Current**: 92% compliance, 4.5 Stars
- **NCQA Percentile**: 85th (top performers)

### Gap Closure
- **Total Gaps Identified**: ~2,500
- **Gaps Closed**: ~1,875
- **Overall Closure Rate**: 75%
- **Average Time to Close**: 45-60 days

### High-Impact Measures
- ✅ BCS (Breast Cancer Screening): 92%
- ✅ CDC (Diabetes Care): 89%
- ✅ CBP (Blood Pressure Control): 88%
- ✅ COL (Colorectal Screening): 85%

---

## 📁 Project Structure

```
hedis-quality-dashboard/
├── databricks.yml              # Bundle configuration
├── requirements.txt            # Heavy dependencies (PySpark, notebooks)
├── notebooks/                  # Databricks notebooks (.py format)
│   ├── 01_ingest_to_bronze.py         # Raw data ingestion
│   ├── 02_bronze_to_silver.py         # Cleaning & validation
│   ├── 03_silver_to_gold.py           # Business aggregates
│   ├── 04_create_uc_functions.py      # UC Functions
│   └── 05_upload_knowledge_docs.py    # Knowledge docs
├── src/                        # Shared Python modules
│   ├── data_generators/
│   │   └── hedis_generator.py         # Synthetic HEDIS data generator
│   └── utils/
│       ├── dataframe_validation.py    # DataFrame validation utilities
│       └── table_helpers.py           # Unity Catalog helpers
├── dashboard/                  # Self-contained app folder
│   ├── app.yaml                       # App runtime config
│   ├── requirements.txt               # Lightweight app dependencies
│   └── hedis_quality_dashboard.py     # Main Streamlit app
├── mcp_clients/                # MCP integration (dormant until activated)
│   ├── config.py               # MCP configuration
│   ├── mcp_genie_client.py
│   ├── mcp_uc_functions_client.py
│   └── mcp_knowledge_assistant_client.py
└── MY_ENVIRONMENT.md           # Standard environment config
```

---

## 🚀 Quick Start

### Access the Dashboard (Recommended)

**🌐 Live Dashboard URL:**  
https://hedis-quality-dashboard-984752964297111.11.azure.databricksapps.com

- ✅ Already deployed and running
- ✅ Enterprise authentication
- ✅ Share with stakeholders immediately
- ✅ No local setup needed

### Test Locally (Optional)

```bash
cd /Users/vik.malhotra/risk-adjustment-630
streamlit run dashboard/hedis_quality_dashboard.py
```

Access at: http://localhost:8501

---

## 🔄 Data Refresh

Data is refreshed automatically through Databricks jobs:

```bash
# Run all jobs in sequence
databricks bundle run bronze_ingestion_job --profile DEFAULT
databricks bundle run silver_transformation_job --profile DEFAULT
databricks bundle run gold_aggregation_job --profile DEFAULT
databricks bundle run uc_functions_job --profile DEFAULT
databricks bundle run knowledge_docs_job --profile DEFAULT
```

---

## 🔌 Add MCP Integration (Optional)

To enable AI-powered natural language search:

### Step 1: Create Genie Space (5 minutes)
1. Navigate to **Data Intelligence → Genie** in Databricks
2. Click **"Create Genie Space"**
3. Select catalog: `humana_quality` schema: `hedis_gold`
4. Name: `hedis_quality_genie`
5. Copy the **Genie Space ID** from URL

### Step 2: Create Knowledge Assistant Endpoint (10 minutes) - Optional
1. Navigate to **Machine Learning → Serving**
2. Click **"Create Serving Endpoint"**
3. Select **"Knowledge Assistant"** type
4. Source: `/Volumes/humana_quality/hedis_gold/knowledge_docs`
5. Name: `hedis_quality_knowledge_assistant`
6. Copy the **Endpoint ID**

### Step 3: Activate MCP
Simply say: **"Add MCP to my project"**

I will automatically:
- ✅ Update `mcp_clients/config.py` with your IDs
- ✅ Modify dashboard to add MCP Search tab
- ✅ Update `dashboard/app.yaml` with MCP environment variables
- ✅ Redeploy the app
- ✅ Provide updated workspace URL

---

## 📊 HEDIS Measures Included

| Code | Measure Name | Eligible Population | Current Rate |
|------|-------------|---------------------|--------------|
| BCS | Breast Cancer Screening | Women 50-74 | 92% |
| CDC | Comprehensive Diabetes Care | Adults 18-75 with diabetes | 89% |
| CBP | Controlling High Blood Pressure | Adults 18-85 with hypertension | 88% |
| COL | Colorectal Cancer Screening | Adults 50-75 | 85% |
| CIS | Childhood Immunization Status | Children age 2 | 90% |
| W15 | Well-Child Visits (First 15 Months) | Children <15 months | 88% |
| AWC | Adolescent Well-Care Visits | Adolescents 12-21 | 79% |
| PPC | Prenatal and Postpartum Care | Women with deliveries | 87% |

---

## 🎯 Use Cases

### For Quality Teams
- Track NCQA compliance across all measures
- Monitor year-over-year improvement
- Identify gaps and prioritize interventions
- Generate reports for leadership

### For Care Coordinators
- Find at-risk members needing outreach
- View member-specific gaps and history
- Track gap closure progress
- Coordinate with providers

### For Executives
- Monitor Stars rating performance
- Track quality improvement initiatives
- Benchmark against NCQA percentiles
- Demonstrate value to stakeholders

---

## 🛠️ Technology Stack

- **Platform**: Databricks (Azure)
- **Data**: Unity Catalog (Delta Lake)
- **Compute**: Databricks SQL Warehouse
- **Dashboard**: Streamlit
- **Orchestration**: Databricks Asset Bundles (DAB)
- **Language**: Python 3.9+, PySpark, SQL

---

## 📞 Support

For questions or issues:
- **Dashboard URL**: https://hedis-quality-dashboard-984752964297111.11.azure.databricksapps.com
- **Databricks Workspace**: https://adb-984752964297111.11.azuredatabricks.net
- **Catalog**: `humana_quality`
- **Schema**: `hedis_gold`

---

## ✨ Next Steps

1. ✅ **Access the dashboard** - Open the URL above
2. ✅ **Explore quality metrics** - Navigate through all 5 tabs
3. ✅ **Test member lookup** - Search for specific members
4. ✅ **Review gap analysis** - Identify high-priority gaps
5. 🔜 **Optional**: Add MCP for AI-powered search

---

**Built with ❤️ for healthcare quality teams**

