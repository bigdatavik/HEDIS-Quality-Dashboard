# My Standard Databricks Environment

**Use this as shorthand: Just say "Use MY_ENVIRONMENT" in your prompts!**

## 🔧 Infrastructure (Always the Same)

```yaml
Platform: Databricks (Azure)
Workspace: https://adb-984752964297111.11.azuredatabricks.net
Auth: ~/.databrickscfg profile "DEFAULT"
Cluster: 0304-162117-qgsi1x04 (always use this for jobs)
SQL Warehouse: /sql/1.0/warehouses/148ccb90800933a1 (for Streamlit dashboards)
```

## 🎯 Standard Execution Preferences

```yaml
Development: Build locally in Cursor
Deployment: Databricks Asset Bundles (DAB)
Automation: FULL END-TO-END - deploy, run jobs, deploy & run apps
Execution: Run all Databricks jobs + Deploy app to workspace automatically
Testing: App is LIVE in workspace, you can also test locally
Error Handling: Auto-fix everything, don't ask + Use validation utilities
Format: Dual (.py and .ipynb notebooks)
Dashboard: Streamlit (local + Databricks Apps compatible)
Data Quality: Always validate DataFrames, explicit joins, no duplicates
Cleanup: 3 options - Databricks only, Local only, or Both
```

## ⚡ What I Do Automatically

When you give me a prompt, I will:
1. ✅ Build all notebooks and source code
2. ✅ Create Streamlit dashboard with `app.yaml` for Databricks Apps **using OFFICIAL authentication pattern**
3. ✅ Add app configuration to `databricks.yml` for workspace deployment
4. ✅ Deploy to Databricks via DAB (notebooks + jobs + apps)
5. ✅ **RUN all jobs to create catalogs, schemas, and tables**
6. ✅ **Create project-specific UC Functions** (e.g., lookup functions for your tables)
7. ✅ **Generate project-specific knowledge documents and upload to volume**
8. ✅ **Include MCP client files** (dormant until you run "add MCP")
9. ✅ **DEPLOY and RUN the app in Databricks workspace**
10. ✅ **Grant app service principal permissions to catalog** (for data access)
11. ✅ Generate all data and analytics
12. ✅ Create complete documentation
13. ✅ **Provide workspace URL for immediate access**
14. ⏸️ **YOU can test locally OR use the workspace URL I provide**

**You don't need to do ANYTHING - I handle 100% end-to-end!**

### 🔐 Dashboard Authentication Pattern (MANDATORY)

**ALWAYS use this exact pattern - from [Official Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/tutorial-streamlit):**

```python
from databricks.sdk.core import Config
cfg = Config()  # Reads DATABRICKS_HOST from app.yaml
sql.connect(
    server_hostname=cfg.host,
    http_path=f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}",
    credentials_provider=lambda: cfg.authenticate,
)
```

**Required in app.yaml:**
```yaml
env:
  - name: 'DATABRICKS_HOST'
    value: 'adb-984752964297111.11.azuredatabricks.net'
```

**This is the ONLY pattern that works reliably in both local dev and Databricks Apps!**

## 📦 Standard Stack

```yaml
Core: PySpark, Delta Lake, Unity Catalog
Languages: Python 3.9+, SQL
Dashboard: Streamlit with Databricks SQL Connector (NOT Databricks Connect)
Documentation: README + BUILD_PLAN + deployment docs
Testing: Table verification after runs
```

## 📁 Standard Project Structure

**ALWAYS use this file structure for Databricks projects:**

```
your-project/
├── databricks.yml            # Bundle configuration
├── requirements.txt          # Heavy dependencies (PySpark, notebooks)
├── notebooks/                # Databricks notebooks (.py format) - Medallion Architecture
│   ├── 01_ingest_to_bronze.py         # Raw data ingestion
│   ├── 02_bronze_to_silver.py         # Cleaning & validation
│   ├── 03_silver_to_gold.py           # Business aggregates
│   ├── 04_create_uc_functions.py      # UC Functions ✅
│   └── 05_upload_knowledge_docs.py    # Knowledge docs ✅
├── src/                      # Shared Python modules
│   ├── __init__.py
│   ├── data_generators/
│   ├── analytics/
│   └── utils/
│       ├── databricks_client.py
│       ├── table_helpers.py
│       └── dataframe_validation.py  # Validation utilities ✅
├── dashboard/                # Self-contained app folder ✅
│   ├── app.yaml             # App runtime config
│   ├── requirements.txt     # Lightweight app dependencies
│   └── your_dashboard.py    # Main Streamlit app (MCP-ready)
├── mcp_clients/              # MCP integration (dormant until "add MCP") ✅
│   ├── config.py             # Auto-configured with project settings
│   ├── mcp_genie_client.py
│   ├── mcp_uc_functions_client.py
│   └── mcp_knowledge_assistant_client.py
└── data/                     # Knowledge Assistant documents ✅
    ├── agent_knowledge_source_guide.txt
    ├── customer_service_communications.txt
    ├── knowledge_source_descriptions.txt
    └── prior_authorization_documents.txt
```

**Key principle: Dashboard folder is SELF-CONTAINED**
- All 3 files (`app.yaml`, `requirements.txt`, `your_dashboard.py`) in same folder
- Databricks uploads entire `dashboard/` folder as the app
- Finds `requirements.txt` automatically in uploaded folder root
- Portable and easy to share

**MCP Infrastructure (Always Created, Dormant Until Activated):**
- ✅ UC Functions: Project-specific lookup functions based on your tables
- ✅ Knowledge Documents: Project-specific documentation tailored to your domain
- ✅ MCP Client Files: Included but not used until you run "add MCP"
- ✅ App is MCP-ready: Works without MCP, enhances when activated

**Examples of UC Functions by Project Type:**
- Risk Adjustment: `lookup_member`, `lookup_hcc_codes`, `lookup_raf_scores`, `lookup_diagnoses`, `members_with_hcc`
- Pharmacy: `lookup_prescriptions`, `lookup_formulary`, `lookup_drug_interactions`, `lookup_drug_utilization`
- Quality Measures: `lookup_hedis_measures`, `lookup_gaps_in_care`, `lookup_quality_scores`, `members_with_gap`
- Claims: `lookup_member`, `lookup_claims`, `lookup_providers`, `lookup_claim_history`, `claims_by_provider`

**See:** "Designing UC Functions for MCP" section below for comprehensive guide

**Examples of Knowledge Documents by Project Type:**
- Risk Adjustment: HCC coding guidelines, CMS-HCC model docs, RAF calculation rules
- Pharmacy: Formulary policies, prior authorization requirements, drug interaction warnings
- Quality Measures: HEDIS specifications, NCQA guidelines, quality improvement protocols
- Claims: Claims processing policies, billing code references, denial reasons

**Two separate requirements.txt files:**
- 📦 **Root `requirements.txt`**: Heavy (PySpark, notebooks, data generation)
- 📊 **`dashboard/requirements.txt`**: Lightweight (Streamlit, SQL connector only)

**Reference:** [Databricks Apps Structure Best Practices](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-runtime)

---

## 🏅 Medallion Architecture (Bronze/Silver/Gold)

**ALWAYS use medallion architecture for data organization:**

### **Architecture Overview:**

```
catalog.bronze/          # 🥉 Raw data, minimal processing
├── source1_raw         # Exactly as received
├── source2_raw         # No transformations
└── reference_data      # Static reference tables

catalog.silver/          # 🥈 Cleaned, validated, conformed
├── table1              # Deduplicated
├── table2              # Type-corrected
└── table3              # Validated schema

catalog.gold/            # 🥇 Business-ready, aggregated
├── analytics_table1    # Aggregated metrics
├── analytics_table2    # Business KPIs
└── dashboard_views     # Optimized for consumption
```

### **Layer Definitions:**

**🥉 BRONZE Layer (Raw Zone)**
- Purpose: Land raw data exactly as received
- Transformations: None (or minimal)
- Quality: As-is from source
- Schema: Flexible
- Who uses: Data engineers for debugging
- Retention: Long-term

**🥈 SILVER Layer (Curated Zone)**
- Purpose: Clean, validate, and conform data
- Transformations: Deduplication, type casting, validation
- Quality: High - enforced constraints
- Schema: Well-defined, standardized
- Who uses: Data engineers, analysts
- Retention: Medium-term

**🥇 GOLD Layer (Consumption Zone)**
- Purpose: Business-ready aggregates
- Transformations: Aggregations, joins, calculations
- Quality: Production-ready
- Schema: Optimized for consumption
- Who uses: Dashboards, ML models, reports
- Retention: Short-term (rebuilt from silver)

### **Example: HCC Risk Adjustment**

```
humana_risk.hcc_bronze/
├── members_raw
├── diagnoses_raw
└── hcc_mapping_ref

humana_risk.hcc_silver/
├── members
├── diagnoses
└── hcc_mapping

humana_risk.hcc_gold/
├── raf_scores
└── revenue_opportunity
```

### **Benefits:**
- ✅ Separation of concerns
- ✅ Data quality at each layer
- ✅ Performance optimization
- ✅ Easy debugging (preserve raw)
- ✅ Different access controls per layer

### **Dashboard Configuration:**
```python
# Dashboard ALWAYS reads from GOLD layer only
CATALOG = "your_catalog"
SCHEMA = "your_gold"  # Gold for business consumption
```

---

**ALWAYS follow these practices to avoid notebook failures:**

### 1. **Use Validation Utilities**
```python
from src.utils.dataframe_validation import (
    validate_dataframe,
    assert_no_duplicate_columns,
    assert_required_columns,
    safe_join,
    ensure_schema_for_union
)

# Validate inputs
members_df = validate_dataframe(
    members_df,
    expected_cols=["member_id", "age", "sex"],
    df_name="members"
)
```

### 2. **Explicit Column Selection in Joins**
```python
# ❌ Wrong - causes duplicate columns
df = members_df.join(other_df, on="member_id")

# ✅ Correct - explicit selection
df = members_df.alias("m").join(
    other_df.alias("o"),
    col("m.member_id") == col("o.member_id")
).select(
    col("m.member_id"),
    col("m.age"),
    col("o.value")
)

# ✅ Even better - use safe_join utility
df = safe_join(
    members_df, other_df,
    on_condition=col("l.member_id") == col("r.member_id"),
    select_cols=["l.member_id", "l.age", "r.value"]
)
```

### 3. **Schema Validation Before Unions**
```python
# ❌ Wrong - assumes schemas match
result = df1.union(df2)  # Fails if different schemas

# ✅ Correct - ensure schemas match
df1, df2 = ensure_schema_for_union(df1, df2, fill_value=lit(False))
result = df1.unionByName(df2)
```

### 4. **Import All Functions Upfront**
```python
# ✅ Always import all functions at notebook start
from pyspark.sql.functions import (
    col, lit, when, coalesce,  # All needed functions
    avg, sum as sql_sum, count, countDistinct,
    desc, round as sql_round, concat_ws,
    collect_set, collect_list  # ← Don't forget aggregation functions!
)
```

**Common missing imports:**
- `collect_set` - for aggregating unique values into a list
- `collect_list` - for aggregating all values into a list
- `explode` - for flattening arrays
- `array` - for creating arrays
- `struct` - for creating structs

### 4.5. **Dynamic Path for Notebook Imports** ⭐ NEW
```python
# ✅ BEST - Dynamic path based on actual bundle location
import sys
import os

# Get current user from workspace context
username = spark.conf.get("spark.databricks.workspaceUrl").split("@")[0]
bundle_name = "your_bundle_name"  # e.g., "high_risk_outreach"
target = "dev"

# Construct dynamic path
src_path = f"/Workspace/Users/{username}/.bundle/{bundle_name}/{target}/files/src"
sys.path.append(src_path)

# Now imports will work
from utils.table_helpers import write_table
```

```python
# ⚠️ ACCEPTABLE - Hardcoded path (but must match actual user)
import sys
sys.path.append("/Workspace/Users/vik.malhotra@databricks.com/.bundle/high_risk_outreach/dev/files/src")

# ❌ WRONG - Wrong username will cause ModuleNotFoundError
sys.path.append("/Workspace/Users/wrong.user@example.com/.bundle/...")
```

**Why this matters:**
- Bundle deploys to `/Workspace/Users/{actual_user}/.bundle/...`
- Wrong username → `ModuleNotFoundError: No module named 'utils'`
- Dynamic path works for any user deploying the bundle
- Hardcoded path must match actual deployment user

### 4.6. **Always Set Catalog Context for UC Functions** ⭐ CRITICAL
```python
# ✅ CORRECT - Set catalog before creating functions
# Configuration
CATALOG = "your_catalog"
SCHEMA = "your_schema"

# Set current catalog FIRST
spark.sql(f"USE CATALOG {CATALOG}")
print(f"✅ Using catalog: {CATALOG}")

# Now create functions - they will be in the correct catalog context
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.your_function(param STRING)
RETURNS TABLE(...)
COMMENT 'Your function description'
RETURN SELECT ... FROM {CATALOG}.{SCHEMA}.table
""")
```

```python
# ❌ WRONG - Missing USE CATALOG
# Configuration
CATALOG = "your_catalog"
SCHEMA = "your_schema"

# Directly trying to create function without setting catalog
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.your_function(param STRING)
...
""")
# ERROR: AnalysisException: Fail to execute the command as the target schema 
# `your_catalog.your_schema` is not in the current catalog.
```

**Why this matters:**
- UC Functions notebooks need catalog context set BEFORE creating functions
- Without `USE CATALOG`, Spark doesn't know which catalog to use
- Even with fully qualified names (catalog.schema.function), you need to set context
- Also applies to `SHOW USER FUNCTIONS IN schema` queries

**Common scenarios requiring USE CATALOG:**
- Creating UC Functions
- Listing functions in a schema
- Creating views that reference functions
- Any cross-catalog operations

### 5. **Explicit Type Casting**
```python
# ❌ Wrong - let Spark infer
data = {"bmi": 28.5}

# ✅ Correct - explicit casting
data = {"bmi": float(round(28.5, 1))}
df = df.withColumn("bmi", col("bmi").cast("float"))
```

### 6. **Handle None Values in Aggregations**
```python
# ❌ Wrong - can cause TypeError if result is None
total = df.agg(sql_sum("amount")).collect()[0][0]
print(f"Total: ${total:,.2f}")  # Fails if no rows!

# ✅ Correct - always check for None from aggregations
total = df.agg(sql_sum("amount")).collect()[0][0]
total = total if total is not None else 0.0
print(f"Total: ${total:,.2f}")

# ✅ Even better - use coalesce in the query
total = df.agg(coalesce(sql_sum("amount"), lit(0.0))).collect()[0][0]
print(f"Total: ${total:,.2f}")
```

**Why this matters:**
- Aggregations on empty DataFrames return `None`
- Formatting `None` with f-strings causes `TypeError`
- Always provide default values for aggregations

### 7. **Handle Column Ambiguity in Joins**

```python
# ❌ Wrong - Column ambiguity after join
diagnoses.join(hcc_mapping, "code", "left").select(
    "diagnosis_id",
    "source_system"  # Which source_system? Ambiguous!
)

# ✅ Correct - Explicit aliases for disambiguation
diagnoses.alias("d").join(hcc_mapping.alias("h"), "code", "left").select(
    col("d.diagnosis_id"),
    col("d.source_system"),  # Clear: from diagnoses
    col("h.hcc_code")
)
```

**Why this matters:**
- Medallion architecture uses similar audit columns across layers (`source_system`, `created_at`, etc.)
- Reference data joins (silver to silver) create name collisions
- Spark cannot resolve ambiguous column references
- DataFrame variable names don't work as aliases in `.select()`

**Common collision columns:**
- `source_system` (from bronze and reference tables)
- `created_at`, `updated_at` (audit timestamps)
- `data_quality`, `status` (metadata fields)

### 8. **The Golden Rules**
- ✅ **Be Explicit**: Column selection, types, schemas, **ALIASES IN JOINS**
- ✅ **Validate Early**: Check inputs before processing
- ✅ **Use Aliases**: Always alias DataFrames in joins (e.g., `.alias("d")`)
- ✅ **Use col() with Aliases**: Reference columns as `col("alias.column_name")`
- ✅ **Import Complete**: All functions at top
- ✅ **Handle Nulls**: Check aggregation results for None
- ✅ **Handle Errors**: Try-catch with context
- ✅ **Verify Results**: Check outputs after writes
- ✅ **Design for Demo**: Ensure test data demonstrates the use case
- ✅ **Set Catalog First**: Always `USE CATALOG` before creating UC Functions

### 9. **Demo Data Design Considerations**

When generating synthetic data for demos, ensure data distribution supports your story:

```python
# ❌ Wrong - All members properly coded (no revenue opportunity to show)
num_diagnoses = random.randint(3, 7)  # Everyone gets many diagnoses

# ✅ Correct - Intentionally create variation for demo
if random.random() < 0.3:
    num_diagnoses = random.randint(1, 2)  # 30% undercoded (shows opportunity)
else:
    num_diagnoses = random.randint(3, 7)  # 70% properly coded
```

**Why this matters:**
- Demo data must demonstrate the problem you're solving
- If analyzing "undercoded members", ensure some ARE undercoded
- If showing "high-risk members", ensure some ARE high-risk
- Random data generation may accidentally eliminate your use case

**Example Issue:** Revenue opportunity table was empty because ALL members had multiple HCC codes. Adding intentional variation (30% with 1-2 codes) created ~30 undercoded members with measurable revenue opportunity.

### 10. **Uploading Files to Unity Catalog Volumes**

When uploading files to volumes in Databricks notebooks:

```python
# ❌ Wrong - Trying to read from filesystem paths that don't exist
source_path = f"{workspace_root}/data/{filename}"
with open(source_path, 'r') as f:
    content = f.read()

# ✅ Correct - Embed content directly in notebook or use proper paths
content = """Your document content here"""
dbutils.fs.put(f"/Volumes/{catalog}/{schema}/{volume}/{filename}", content, overwrite=True)
```

**Why this matters:**
- Bundle deployment uploads notebooks but NOT arbitrary data files
- Local `data/` folder files aren't accessible in Databricks workspace
- Either embed content in notebooks OR use workspace-accessible paths
- Use `dbutils.fs.put()` to write directly to volumes

**Example Issue:** Knowledge documents weren't uploaded because notebook tried to read from non-existent workspace paths. Embedding documents in notebook fixed the issue.

**See: `NOTEBOOK_BEST_PRACTICES.md` for complete guide**

## 📊 Streamlit Dashboard Standards

**⚠️ CRITICAL: ALWAYS use this EXACT pattern - Official Databricks Documentation**

### ✅ CORRECT Configuration (OFFICIAL DATABRICKS PATTERN)

**Reference:** [Databricks Apps Streamlit Tutorial](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/tutorial-streamlit)

```python
# ✅ CORRECT - Official Databricks pattern for Streamlit apps
from databricks import sql
from databricks.sdk.core import Config
import streamlit as st
import os

# Configuration from environment variables (with defaults for local testing)
CATALOG = os.getenv("CATALOG_NAME", "humana_quality")
SCHEMA = os.getenv("SCHEMA_NAME", "hedis_gold")
SQL_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")

@st.cache_resource
def get_databricks_connection():
    """Create Databricks SQL connection using official Databricks pattern"""
    try:
        # Config() reads from DATABRICKS_HOST env var (set in app.yaml for Databricks Apps)
        # For local: reads from ~/.databrickscfg DEFAULT profile
        cfg = Config()
        
        return sql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}",
            credentials_provider=lambda: cfg.authenticate,
        )
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def read_table(table_name: str) -> pd.DataFrame:
    """Read table from Databricks using SQL Connector"""
    conn = get_databricks_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {CATALOG}.{SCHEMA}.{table_name}")
            return cursor.fetchall_arrow().to_pandas()
    except Exception as e:
        st.error(f"Error reading {table_name}: {e}")
        return pd.DataFrame()
```

**⚠️ CRITICAL: Key Requirements**
- ✅ Use `Config()` - it reads from `DATABRICKS_HOST` env var in Databricks Apps
- ✅ Use `cfg.host` directly (no need to strip "https://")
- ✅ Use `credentials_provider=lambda: cfg.authenticate` (exact pattern from docs)
- ✅ SQL_WAREHOUSE_ID must have a default value (not None)
- ✅ All environment variables should have fallback defaults

**❌ WRONG Patterns - DO NOT USE:**

```python
# ❌ WRONG - Don't use WorkspaceClient
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()  # NO!

# ❌ WRONG - Don't manually strip protocol
host = cfg.host.replace("https://", "")  # NO! Use cfg.host directly

# ❌ WRONG - Don't use w.config.authenticate
credentials_provider=w.config.authenticate  # NO! Use cfg.authenticate

# ❌ WRONG - Don't use Databricks Connect for dashboards
from databricks.connect import DatabricksSession
spark = DatabricksSession.builder...  # NO!
```

**Why This Pattern?**
- ✅ Official Databricks documentation
- ✅ Works in both local development and Databricks Apps
- ✅ Automatic authentication (local: ~/.databrickscfg, app: service principal OAuth)
- ✅ Lightweight - just SQL queries
- ✅ Uses SQL Warehouse (faster, cheaper than cluster)

**Reference:** https://docs.databricks.com/aws/en/dev-tools/databricks-apps/tutorial-streamlit

---

### 🔧 Common Local Dashboard Issues & Fixes

#### Issue 1: "MALFORMED_REQUEST: Path /sql/1.0/warehouses/None"
**Problem:** SQL_WAREHOUSE_ID environment variable is None when running locally

**Fix:**
```python
# ❌ Wrong - No default value
SQL_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")

# ✅ Correct - Provide default for local testing
SQL_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")
```

#### Issue 2: "Failed to establish new connection" or DNS errors
**Problem:** Host URL contains "https://" protocol which causes malformed requests

**Fix:**
```python
# ❌ Wrong - Using cfg.host directly
server_hostname=cfg.host

# ✅ Correct - Strip protocol
host = cfg.host
if host.startswith("https://"):
    host = host.replace("https://", "")
server_hostname=host
```

#### Issue 3: Dashboard shows "No data loaded"
**Problem:** Environment variables not set when running locally

**Solution:** Always provide defaults in your dashboard code:
```python
CATALOG = os.getenv("CATALOG_NAME", "your_catalog")
SCHEMA = os.getenv("SCHEMA_NAME", "your_gold")
SQL_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")
```

**Testing Checklist:**
- [ ] Test dashboard locally: `streamlit run dashboard/your_dashboard.py`
- [ ] Verify it connects to Databricks
- [ ] Check data loads correctly
- [ ] Then deploy to Databricks Apps

---

### 🚨 If App Works Locally But Not in Databricks Apps

**Problem:** Dashboard runs fine locally but returns "Connection error: Error during request to server" when deployed to Databricks Apps

**Root Causes & Solutions:**

#### 1. Missing Catalog Permissions (MOST COMMON)

The app service principal needs explicit permissions to access Unity Catalog:

```bash
# Get app service principal ID
databricks apps get your-app-name --profile DEFAULT | grep service_principal_client_id

# Grant catalog permissions (replace with your service principal ID and catalog name)
databricks grants update catalog your_catalog_name --json '{
  "changes": [{
    "principal": "your-service-principal-id",
    "add": ["USE_CATALOG", "USE_SCHEMA", "SELECT"]
  }]
}' --profile DEFAULT

# Restart app
databricks apps stop your-app-name --profile DEFAULT
databricks apps start your-app-name --profile DEFAULT
```

**This is REQUIRED after every new deployment!** The service principal doesn't inherit your user permissions.

#### 2. Wrong Authentication Pattern

Make sure you're using the **OFFICIAL Databricks pattern** (see Streamlit Dashboard Standards section above):

```python
# ✅ CORRECT
from databricks.sdk.core import Config
cfg = Config()
sql.connect(
    server_hostname=cfg.host,
    http_path=f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}",
    credentials_provider=lambda: cfg.authenticate,
)
```

#### 3. Missing DATABRICKS_HOST Environment Variable

Ensure `app.yaml` includes:

```yaml
env:
  - name: 'DATABRICKS_HOST'
    value: 'adb-984752964297111.11.azuredatabricks.net'
```

**Redeploy if needed:**

```bash
cd /path/to/your/project
databricks bundle deploy --profile DEFAULT
databricks apps stop your-app-name --profile DEFAULT
databricks apps start your-app-name --profile DEFAULT
```

**Why This Happens:**
- Databricks Apps caches the deployed code and environment
- If you deploy with broken config (e.g., SQL_WAREHOUSE_ID=None), it stays broken
- The app shows as "RUNNING" but actually fails on connection attempts
- Simply restarting the app doesn't help - you need to redeploy with fixed code

**Prevention Checklist:**
1. ✅ **Always test locally first** - Run `streamlit run dashboard/your_dashboard.py`
2. ✅ **Verify defaults are set** - Check all `os.getenv()` have fallback values
3. ✅ **Clean host URLs** - Strip "https://" from cfg.host before using
4. ✅ **Deploy only after local test passes**

**Quick Diagnostic:**
```bash
# Check app status
databricks apps get your-app-name --profile DEFAULT

# If it shows RUNNING but doesn't work, redeploy:
databricks bundle deploy --profile DEFAULT
databricks bundle run your_dashboard_app --profile DEFAULT
```

---

**Root requirements.txt must include (for notebooks):**
```
# Root requirements.txt - for Databricks notebooks/jobs
databricks-sdk>=0.18.0
databricks-cli>=0.18.0
pyspark>=3.4.0
pandas>=2.0.0
# ... other heavy dependencies
```

### 📄 Dashboard Folder Structure (Self-Contained)

**ALWAYS create a self-contained dashboard folder with these files:**

```
dashboard/
├── app.yaml              # App runtime configuration
├── requirements.txt      # App-specific dependencies (lightweight)
└── your_dashboard.py     # Main Streamlit app
```

**dashboard/app.yaml:**
```yaml
# dashboard/app.yaml
# IMPORTANT: Keep command simple - Databricks handles port/server config automatically
# Reference: https://docs.databricks.com/aws/en/dev-tools/databricks-apps/tutorial-streamlit
command: ['streamlit', 'run', 'your_dashboard.py']

env:
  # Databricks Configuration (CRITICAL - needed for Config() to work in Databricks Apps)
  - name: 'DATABRICKS_HOST'
    value: 'adb-984752964297111.11.azuredatabricks.net'
  
  # SQL Warehouse Configuration
  - name: 'DATABRICKS_WAREHOUSE_ID'
    value: '148ccb90800933a1'
  
  # Unity Catalog Configuration (from environment, not hardcoded!)
  - name: 'CATALOG_NAME'
    value: 'your_catalog'
  - name: 'SCHEMA_NAME'
    value: 'your_gold'  # Always point to gold layer for dashboards
  
  # Streamlit Configuration
  - name: 'STREAMLIT_GATHER_USAGE_STATS'
    value: 'false'
```

**⚠️ CRITICAL: Do NOT add --server.port or --server.enableCORS to the command!**
- Databricks automatically configures server settings
- Extra parameters will cause "App Not Available" errors
- Keep the command simple as shown above

**✅ Best Practice: Use Environment Variables**
Never hardcode catalog/schema names in your dashboard code. Always use `os.getenv()`:

```python
import os

# ✅ CORRECT - Read from environment variables
CATALOG = os.getenv("CATALOG_NAME", "default_catalog")
SCHEMA = os.getenv("SCHEMA_NAME", "default_schema")
SQL_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")

# ❌ WRONG - Hardcoded values
CATALOG = "humana_risk"  # Don't do this!
SCHEMA = "hcc_gold"      # Don't do this!
```

**Why use environment variables:**
- ✅ Easy to change without code modifications
- ✅ Different values for dev/staging/prod
- ✅ Follows 12-factor app principles
- ✅ Single source of truth (app.yaml)

**dashboard/requirements.txt (lightweight - app only):**
```
# Dashboard dependencies only - lightweight!
databricks-sql-connector>=3.0.0
databricks-sdk>=0.18.0
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
```

**Critical: Why self-contained dashboard folder?**
- ✅ Databricks uploads `dashboard/` folder as-is
- ✅ Finds `app.yaml` in root of uploaded folder
- ✅ Finds `requirements.txt` in root of uploaded folder
- ✅ Portable (can share dashboard folder independently)
- ✅ Lightweight (no PySpark, faster startup)
- ✅ Clean separation (notebook deps ≠ app deps)

**Two requirements.txt files explained:**
- 📦 **Root**: Heavy (PySpark, notebooks, data gen) - ~500MB
- 📊 **Dashboard**: Light (Streamlit, SQL only) - ~50MB
- Result: **10x faster app deployment!**

**Why app.yaml?**
- ✅ Enables deployment to Databricks Apps (hosted in workspace)
- ✅ Sets SQL Warehouse ID as environment variable
- ✅ Configures Streamlit runtime settings
- ✅ Works seamlessly - local dev + Databricks deployment

**Reference:** https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/app-runtime#example-appyaml-for-a-streamlit-app

**Dual deployment approach:**
- 🏠 **Local testing**: `streamlit run dashboard/app.py` (uses .databrickscfg)
- ☁️ **Databricks Apps**: Deploys with `app.yaml` (hosted in workspace)

### 🚀 Deploy Streamlit Apps to Databricks Workspace

**ALWAYS add app configuration to `databricks.yml` for workspace deployment:**

```yaml
# databricks.yml
bundle:
  name: your_project_name

resources:
  # Databricks jobs for data processing
  jobs:
    data_generation_job:
      name: "[Project] 01 - Data Generation"
      # ... job configuration ...
  
  # Databricks Apps for interactive dashboards
  apps:
    your_dashboard_app:
      name: 'your-dashboard-app'
      description: 'Interactive analytics dashboard'
      source_code_path: ./dashboard  # Path to dashboard folder with app.yaml

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://adb-984752964297111.11.azuredatabricks.net
  
  prod:
    mode: production
    workspace:
      host: https://adb-984752964297111.11.azuredatabricks.net
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: ${workspace.current_user.userName}
        level: CAN_MANAGE
```

**Deployment commands:**

```bash
# Validate configuration
databricks bundle validate

# Deploy to dev workspace (default)
databricks bundle deploy

# Deploy and run the app in workspace
databricks bundle run your_dashboard_app

# Get app URL in workspace
databricks bundle summary

# Deploy to production
databricks bundle deploy -t prod
databricks bundle run your_dashboard_app -t prod
```

**Why deploy to Databricks Apps?**
- ✅ Share dashboards with stakeholders (no local install needed)
- ✅ Enterprise authentication and permissions
- ✅ Hosted in workspace - always available
- ✅ Auto-connects to SQL Warehouse
- ✅ Single deployment command

**Reference:** https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/apps-tutorial#deploy-the-app-to-the-workspace-using-bundles

**Complete workflow:**
1. 🏗️ **Develop locally** - Build and test with `streamlit run`
2. 🧪 **Debug locally** - Use `databricks apps run-local --debug`
3. 🚀 **Deploy to workspace** - **I DO THIS AUTOMATICALLY**
4. 🔐 **Grant permissions** - **I DO THIS AUTOMATICALLY**
5. 🌐 **Run in workspace** - **I DO THIS AUTOMATICALLY**
6. 📊 **Share URL** - **I PROVIDE THIS TO YOU**
7. ✅ **You just open the URL!**

---

## 🔧 Designing Unity Catalog Functions for MCP

**Critical for MCP Success:** UC Functions determine what questions Genie can answer about your data.

### **CRITICAL: Always Set Catalog Context First** ⚠️

Before creating any UC Functions, you MUST set the catalog context:

```python
# Configuration
CATALOG = "your_catalog"
SCHEMA = "your_schema"

# ⭐ CRITICAL: Set catalog context FIRST
spark.sql(f"USE CATALOG {CATALOG}")
print(f"✅ Using catalog: {CATALOG}")

# Now you can create functions
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.your_function(...)
...
""")
```

**Why this is critical:**
- Without `USE CATALOG`, you'll get: `AnalysisException: schema not in current catalog`
- Even fully qualified names (catalog.schema.function) require catalog context
- Applies to ALL UC Function operations: CREATE, DROP, SHOW, etc.

### **The UC Function Design Framework**

When creating UC functions for any project, follow this systematic approach to ensure 95%+ question coverage.

---

### **Step 1: Identify Your Business Entities**

List the core entities in your domain:

**Healthcare Examples:**
- Members/Patients
- Providers  
- Claims
- Diagnoses
- Medications
- Quality Measures
- Episodes of Care

**Other Domains:**
- Finance: Accounts, Transactions, Customers
- Retail: Products, Orders, Customers, Inventory
- Manufacturing: Parts, Orders, Suppliers, Production Runs

---

### **Step 2: Map Questions to Function Types**

For each entity, you need **4 types of functions**:

#### **Type 1: Single Record Lookup** (lookup_*)
- **Purpose:** Get details for one specific record
- **Pattern:** `lookup_{entity}(id) → entity details`
- **Example:** `lookup_member('M001')` → member demographics

#### **Type 2: Related Records** (lookup_{entity}_{related})
- **Purpose:** Get child/related records for a parent entity
- **Pattern:** `lookup_{entity}_{related}(parent_id) → related records`
- **Example:** `lookup_member_claims('M001')` → all claims for member

#### **Type 3: Search by Criteria** ({entity}_with_{criteria})
- **Purpose:** Find entities matching specific conditions
- **Pattern:** `{entities}_with_{criteria}(criteria_value) → matching entities`
- **Example:** `members_with_hcc('HCC_85')` → members with CHF

#### **Type 4: Aggregations** (get_{entity}_{metric})
- **Purpose:** Get calculated metrics/summaries
- **Pattern:** `get_{entity}_{metric}(id) → calculated value`
- **Example:** `get_member_total_cost('M001')` → total claims cost

---

### **Step 3: Coverage Analysis Checklist**

For each entity, verify you can answer:

**✅ Individual Lookups**
- [ ] Can I get a single record by ID?
- [ ] Can I get related/child records?
- [ ] Can I get the most recent related record?

**✅ Search & Filter**
- [ ] Can I find records by key attributes?
- [ ] Can I search by date range?
- [ ] Can I filter by status/category?

**✅ Aggregations**
- [ ] Can I get counts/totals?
- [ ] Can I get averages/metrics?
- [ ] Can I get rankings/top N?

**✅ Relationships**
- [ ] Can I navigate parent → child?
- [ ] Can I navigate child → parent?
- [ ] Can I find related entities?

---

### **Step 4: Function Placement Strategy**

**Where to create functions:** Choose the appropriate layer

```
🥉 BRONZE Functions: ❌ NEVER
   - Raw data, not for consumption

🥈 SILVER Functions: ⚠️ DETAILED LOOKUPS ONLY
   - Individual record detail
   - Full history/audit trail
   - When you need ALL fields

🥇 GOLD Functions: ✅ MOST FUNCTIONS HERE
   - Business metrics
   - Aggregated data
   - Dashboard-ready
   - Optimized for queries
```

**Best Practice:** Create functions in **gold schema**, query from appropriate layer:
```sql
-- Function lives in gold, but queries silver for detail
CREATE FUNCTION catalog.gold_schema.lookup_diagnoses(input_id STRING)
RETURN SELECT * FROM catalog.silver_schema.diagnoses WHERE member_id = input_id;
```

---

### **Step 5: Function Naming Conventions**

**Pattern:** `{action}_{entity}_{optional_qualifier}`

**Actions:**
- `lookup_` → Single record by ID
- `{entity}_with_` → Search/filter (returns multiple)
- `get_` → Calculated metric/aggregation
- `list_` → Get collection (optionally filtered)

**Examples:**
```sql
✅ lookup_member(id)              -- Single member
✅ lookup_member_claims(id)       -- Claims for a member
✅ members_with_hcc(hcc_code)     -- Members having specific HCC
✅ get_member_total_cost(id)      -- Calculated metric
✅ list_high_risk_members()       -- Filtered collection
```

**Anti-Patterns:**
```sql
❌ get_member(id)                 -- Use 'lookup_' for single record
❌ member_hcc_lookup(id)          -- Action should come first
❌ findMembersWithHCC(code)       -- Use snake_case, not camelCase
```

---

### **Complete Function Set Examples**

#### **Risk Adjustment (HCC) - Complete Set**

```sql
-- Type 1: Single Record Lookups
CREATE FUNCTION lookup_member(id STRING)                    -- Demographics
CREATE FUNCTION lookup_hcc_codes(id STRING)                 -- HCC codes & RAF
CREATE FUNCTION lookup_raf_scores(id STRING)                -- RAF breakdown

-- Type 2: Related Records
CREATE FUNCTION lookup_diagnoses(id STRING)                 -- All diagnoses for member
CREATE FUNCTION lookup_member_history(id STRING)            -- Historical RAF scores

-- Type 3: Search by Criteria
CREATE FUNCTION members_with_hcc(hcc_code STRING)          -- Members with specific HCC
CREATE FUNCTION members_with_raf_above(threshold DOUBLE)   -- High RAF members
CREATE FUNCTION undercoded_members()                        -- Members with ≤1 HCC

-- Type 4: Aggregations
CREATE FUNCTION get_member_revenue_opportunity(id STRING)  -- Revenue gap
CREATE FUNCTION get_hcc_member_count(hcc_code STRING)      -- Count per HCC
```

**Coverage:** ✅ Can answer member-specific, cohort, and metric questions

---

### **Function Design Worksheet Template**

Use this template for any new project:

```markdown
## UC Functions Design - [PROJECT NAME]

### Business Entities
1. [Entity 1] - [Description]
2. [Entity 2] - [Description]

### Function Matrix

| Entity | Lookup | Related | Search | Metrics |
|--------|--------|---------|--------|---------|
| Members | lookup_member(id) | lookup_member_claims(id) | members_with_condition() | get_member_total_cost() |

### Coverage Checklist
- [ ] Can get individual records by ID
- [ ] Can get related/child records
- [ ] Can search by key attributes
- [ ] Can get aggregated metrics

### Test Questions
1. "Show me [entity] details for [ID]" → lookup function
2. "Which [entities] have [criteria]?" → search function
3. "What's the total [metric]?" → aggregation function
```

---

### **Gap Detection Process**

After creating functions, test coverage:

#### **Business Question Test**
Ask 20-30 typical business questions and mark:
- ✅ Can answer directly
- ⚠️ Can answer but awkward
- ❌ Cannot answer

**Target: >80% should be ✅**

#### **Example Gap Analysis**

```
✅ "What's total revenue?"                    → Genie on gold tables
✅ "Show member M001 details"                 → lookup_member('M001')
❌ "Show all diagnoses for M001"              → MISSING: lookup_diagnoses()
⚠️ "Which members have diabetes?"             → AWKWARD: String search on hcc_codes
```

**Solution:** Add `lookup_diagnoses()` and `members_with_condition()` functions

---

### **Best Practices Summary**

✅ **DO:**
- Create 4 function types for each core entity
- Use consistent naming conventions (`lookup_`, `{entity}_with_`, `get_`)
- Place functions in gold schema
- Query from appropriate layer (gold/silver)
- Test coverage with 20+ business questions
- Document each function's purpose

❌ **DON'T:**
- Create functions in bronze layer
- Use inconsistent naming
- Skip the coverage analysis
- Forget related records functions
- Only create lookup functions (need all 4 types!)

---

### **Function Template**

```sql
-- Template for any UC function
CREATE OR REPLACE FUNCTION catalog.gold_schema.{function_name}({param} {type})
RETURNS TABLE(
  column1 TYPE,
  column2 TYPE
)
COMMENT '{What this function does and when to use it}'
RETURN 
  SELECT column1, column2
  FROM catalog.{layer}.{table}
  WHERE {condition};

-- Test immediately
SELECT * FROM catalog.gold_schema.{function_name}({test_value});
```

---

**With this framework, create complete UC function sets for any use case!** 🎯

See: `MCP_QUESTION_COVERAGE_ANALYSIS.md` for detailed example using HCC Risk Adjustment



---

## 🔧 Troubleshooting Databricks Apps

### "App Not Available" Error

If you see "App Not Available" even though the app shows as RUNNING:

**Issue 1: Incorrect app.yaml configuration**

❌ **Wrong** (causes app to fail):
```yaml
command: ['streamlit', 'run', 'app.py', '--server.port=8080', '--server.enableCORS=false']
```

✅ **Correct** (follows Microsoft docs):
```yaml
command: ['streamlit', 'run', 'app.py']
```

**Why:** Databricks automatically configures port and server settings. Extra parameters interfere with the app runtime.

**Reference:** [Microsoft Databricks App Runtime Documentation](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/app-runtime#example-appyaml-for-a-streamlit-app)

**Issue 2: Missing catalog permissions**

The app service principal needs explicit permissions to read Unity Catalog tables.

**Fix:**
```bash
# Get app info to find service principal ID
databricks apps get <app-name> --profile DEFAULT

# Grant permissions using the service_principal_client_id
databricks grants update catalog <catalog_name> --json '{
  "changes": [{
    "principal": "<service_principal_client_id>",
    "add": ["SELECT", "USE_CATALOG", "USE_SCHEMA"]
  }]
}' --profile DEFAULT

# Restart app
databricks apps stop <app-name> --profile DEFAULT
databricks apps start <app-name> --profile DEFAULT
```

**Note:** I handle this automatically now, but if you manually create apps, remember to grant permissions!

---

## ✅ What You Still Need to Specify

Just tell me:
1. **What to build** (Risk adjustment? Quality measures? Provider network?)
2. **Who it's for** (Which stakeholders?)
3. **What data/metrics** (HCC codes? Stars? Claims?)
4. **Catalog/Schema names** (Will create if needed)
5. **Dataset size** (Optional: LOW/MEDIUM/LARGE - defaults to MEDIUM)

---

## 🚀 Quick Prompt Format

**Copy this template and fill it in:**

```
USE: MY_ENVIRONMENT

BUILD: [What to build in one line]
FOR: [Stakeholder names and roles]
SHOW: [Key metrics/value to demonstrate]
DATA: [Catalog.schema names to use]
TABLES: [What data to generate and analyze]
SIZE: [LOW | MEDIUM | LARGE]
GO! 🚀
```

### 📊 Dataset Sizes (for quick turnaround)

```yaml
LOW:     # Fast (~2-5 min) - Quick demos, testing
  Members: 100
  Claims: 500
  Total rows: ~1K

MEDIUM:  # Balanced (~5-15 min) - Standard demos  [DEFAULT]
  Members: 10K
  Claims: 50K
  Total rows: ~100K

LARGE:   # Production-like (~15-30 min) - Realistic scale
  Members: 100K
  Claims: 2M
  Total rows: ~5M
```

**When to use:**
- 🏃 **LOW**: You're in a hurry, just need proof of concept
- ⚖️ **MEDIUM**: Standard demo, balanced speed/realism (default)
- 🏋️ **LARGE**: Need production scale, performance testing

---

## 💡 Example Quick Prompts

**Copy any example below and modify as needed:**

---

### Example 1: Risk Adjustment (Quick Demo - 3 minutes)

```
USE: MY_ENVIRONMENT

BUILD: HCC Risk Adjustment Analytics
FOR: Dalia Powers (SVP) - wants RAF score optimization
SHOW: $12M revenue opportunity from better HCC coding
DATA: humana_risk.hcc_analytics
TABLES: Members with diagnosis codes, CMS HCC V28 mappings, RAF scores and revenue impact
SIZE: LOW
GO! 🚀
```

---

### Example 2: Quality Measures (Standard Demo - 10 minutes)

```
USE: MY_ENVIRONMENT

BUILD: HEDIS Quality Measures Dashboard
FOR: Quality team - needs NCQA compliance tracking
SHOW: 85% -> 92% quality score improvement
DATA: humana_quality.hedis_metrics
TABLES: Member eligibility and enrollment, Clinical measures (BCS, CDC, CBP), Gap closure tracking
SIZE: MEDIUM
GO! 🚀
```

---

### Example 3: Provider Network (Production Scale - 20 minutes)

```
USE: MY_ENVIRONMENT

BUILD: Provider Network Analytics
FOR: Network management team
SHOW: $8M savings from high-value provider identification
DATA: humana_network.provider_analytics
TABLES: Provider directory and contracts, Utilization and cost per provider, Quality metrics by provider
SIZE: LARGE
GO! 🚀
```

---

### Example 4: Member Outreach Campaign

```
USE: MY_ENVIRONMENT

BUILD: High-Risk Member Outreach Analytics
FOR: Care management team
SHOW: 25% reduction in ER visits through targeted outreach
DATA: humana_outreach.member_engagement
TABLES: High-risk member list, Outreach history, Engagement metrics, Cost avoidance
SIZE: LOW
GO! 🚀
```

---

### Example 5: Pharmacy Cost Management

```
USE: MY_ENVIRONMENT

BUILD: Pharmacy Cost Optimization Dashboard
FOR: Pharmacy benefit team
SHOW: $20M savings from generic substitution opportunities
DATA: humana_pharmacy.cost_optimization
TABLES: Drug utilization, Generic alternatives, Cost comparison, Savings opportunities
SIZE: MEDIUM
GO! 🚀
```

---

### Example 6: With MCP Integration (Advanced)

```
USE: MY_ENVIRONMENT

BUILD: HCC Risk Adjustment Analytics
FOR: Clinical coding team
SHOW: $12M revenue opportunity from better HCC coding
DATA: humana_risk.hcc_analytics
TABLES: Members, diagnosis codes, HCC mappings, RAF scores
SIZE: MEDIUM
GO! 🚀
```

**After deployment**: Follow "Add MCP Integration" guide for AI-powered search

---

## 🎯 Time Savings

**Before (full template):** 5-10 minutes to write complete prompt  
**After (with MY_ENVIRONMENT):** 30 seconds to write quick prompt

**Net savings: 4.5-9.5 minutes per project** 🚀

---

## 🧪 Testing Workflow

After I complete automation, **EVERYTHING IS READY**:

### ✅ What's Automatically Done:
- 📊 All Databricks jobs executed (data created)
- 🚀 App deployed to Databricks workspace
- 🌐 App running and accessible via URL
- 📝 Workspace URL provided to you

### 🎯 Your Options for Access:

#### Option 1: Use Workspace URL (Recommended - Already Running!)
```
✅ App is LIVE at: https://your-app-id.databricksapps.com
```
**Just open the URL I provide!**
- No commands needed
- Share with stakeholders immediately
- Enterprise auth and permissions
- Always available

#### Option 2: Test Locally (Optional)
```bash
cd ~/risk-adjustment-630  # or wherever project is
streamlit run dashboard/your_dashboard.py
```
**Access at:** http://localhost:8501
- Good for: Development, quick changes

### 📋 Manual Deployment Commands (Only if needed)

You usually don't need these, but if you want to redeploy manually:

```bash
# Validate
databricks bundle validate

# Deploy everything
databricks bundle deploy

# Run app in workspace
databricks bundle run your_dashboard_app

# Get URL
databricks bundle summary
```

**Dashboard automatically:**
- ✅ Connects to SQL Warehouse (148ccb90800933a1)
- ✅ Loads data from Unity Catalog tables
- ✅ Shows success message when data loads
- ✅ Fallback to demo data if connection fails

**You NEVER need to:**
- ❌ Manually run Databricks jobs
- ❌ Create catalogs or schemas
- ❌ Generate data
- ❌ Deploy the app
- ❌ Run the app
- ❌ Configure anything

**I handle 100% of automation:**
- ✅ All Databricks jobs run automatically
- ✅ All tables created with data
- ✅ App deployed and running in workspace
- ✅ Workspace URL provided to you
- ✅ You just open the URL and share it!

---

## 🧹 Project Cleanup & Reset

**Need a clean slate? Choose your cleanup option!**

⚠️ **Important**: These cleanup options work when you have an active project. They help you selectively clean Databricks or local files. For a brand new project after cleanup, just use the standard build process.

### Option 1: Clean Databricks Only (Keep Local Files)
**Use when:** You want to redeploy from local or just clean up workspace

**Command:** "Clean Databricks workspace" or "Destroy Databricks only"

**What happens:**
1. Runs `databricks bundle destroy --profile DEFAULT --auto-approve` (removes app, jobs)
2. **Automatically drops catalog** using Databricks SDK with DEFAULT profile ✨
3. Confirms all workspace resources deleted

**Deletes:**
- ❌ Drop catalog and all schemas/tables (AUTOMATED) ✨
- ❌ Delete Databricks App
- ❌ Delete all jobs
- ❌ Delete bundle deployment

**Catalog Cleanup (Automated):**
```python
# Automated via Databricks SDK (DEFAULT profile)
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEFAULT")

# Method 1: Using Catalogs API (preferred)
w.catalogs.delete(name=catalog_name, force=True)

# Method 2: Using SQL Statement Execution API (fallback)
w.statement_execution.execute_statement(
    warehouse_id="148ccb90800933a1",
    statement=f"DROP CATALOG IF EXISTS {catalog_name} CASCADE",
    wait_timeout="30s"
)
```

**Manual Alternatives (if automation fails):**
```bash
# Via SQL Editor in workspace UI
# Go to: SQL Editor → Run: DROP CATALOG IF EXISTS {catalog_name} CASCADE

# Via Data Explorer UI
# Go to: Data → Catalogs → Select catalog → Delete
```

**Keeps:**
- ✅ All local files (notebooks, src, dashboard, docs)
- ✅ Can redeploy immediately with `databricks bundle deploy`

**Good for:** Testing redeployment, workspace cleanup, cost savings

**Note**: If local files were previously deleted, this only cleans Databricks.

---

### Option 2: Clean Local Only (Keep Databricks)
**Use when:** You want fresh local code but keep data/apps running

**Command:** "Clean local files" or "Destroy local only"

**What happens:**
1. Deletes all project files (except MY_ENVIRONMENT.md)
2. Preserves .git, .databricks folders
3. Confirms local cleanup complete

**Deletes:**
- ❌ All notebooks
- ❌ All source code (src/)
- ❌ Dashboard folder
- ❌ All documentation files
- ❌ databricks.yml, requirements.txt

**Keeps:**
- ✅ MY_ENVIRONMENT.md
- ✅ All Databricks data (catalog, tables, jobs, app)
- ✅ App still running in workspace
- ✅ .git folder (version control)

**Good for:** Fresh start on code, rebuild from scratch

**Note**: If Databricks was previously cleaned, this only cleans local files.

---

### Option 3: Clean Both (Complete Reset)
**Use when:** You want a complete clean slate for a new project

**Command:** "Clean slate - destroy everything" or "Reset project completely"

**What happens:**
1. Runs `databricks bundle destroy --profile DEFAULT --auto-approve`
2. **Automatically drops catalog** using Databricks SDK with DEFAULT profile ✨
3. Deletes all local files except MY_ENVIRONMENT.md
4. Confirms complete cleanup

**Deletes:**
- ❌ Everything in Databricks (catalog, app, jobs) - AUTOMATED ✨
- ❌ Everything local (except MY_ENVIRONMENT.md)

**Catalog Cleanup (Automated):**
```python
# Same automated cleanup as Option 1
# Uses Databricks SDK with DEFAULT profile
w = WorkspaceClient(profile="DEFAULT")
w.catalogs.delete(name=catalog_name, force=True)
```

**Keeps:**
- ✅ MY_ENVIRONMENT.md only
- ✅ .git folder (if committed)
- ✅ .gitignore (recreated)

**Good for:** Starting a brand new project, complete reset

---

### 🎯 Quick Reference Commands

| What You Say | What Gets Deleted | What Stays | When to Use |
|--------------|-------------------|------------|-------------|
| "Clean Databricks only" | ☁️ Workspace only | 💻 Local files | Redeploy from local |
| "Clean local only" | 💻 Local files only | ☁️ Workspace | Rebuild code, keep data |
| "Clean everything" | ☁️💻 Both | MY_ENVIRONMENT.md | Fresh project start |

### ⚠️ Important Notes:
- **These are independent operations**: Each cleanup option checks what exists and cleans accordingly
- **If both already deleted**: That's fine! You're ready for a new project
- **If one is already clean**: The command will only clean what's left
- **Example**: If you previously did "Clean everything" and then say "Clean Databricks only", it will just confirm Databricks is already clean

### Safety Features:
- ✅ Always confirms before deletion
- ✅ Shows exactly what will be deleted
- ✅ MY_ENVIRONMENT.md always protected
- ✅ Checks what exists before attempting deletion
- ✅ Git history preserved (if committed)
- ✅ Graceful handling if already cleaned

---

**Just reference this file and focus on WHAT to build, not HOW to deploy!**

---

## 🔌 Add MCP Integration (Separate Command)

**Use this AFTER your project is deployed and working!**

MCP (Model Context Protocol) adds AI-powered search capabilities to your app using Databricks managed services. The infrastructure is already in place - you just need to configure it.

### 📋 Quick Navigation - Complete MCP Documentation

This comprehensive guide contains EVERYTHING you need for MCP:

1. **📚 Knowledge Documents** (scroll down ~50 lines)
   - 4 complete content templates (agent guide, source descriptions, policies, FAQ)
   - Save locally in `data/` folder before uploading to volumes
   - Project-specific examples for HEDIS, HCC, Pharmacy

2. **🎯 Knowledge Assistant Setup** (scroll down ~600 lines)
   - Step-by-step UI instructions
   - Description field templates for each project type
   - "Describe the content" field templates (CRITICAL!)

3. **🎨 Genie Space Setup** (scroll down ~650 lines)
   - Instructions tab templates (CRITICAL!)
   - SQL Expressions examples
   - How to get Genie Space ID

4. **🔧 Complete MCP Code Templates** (scroll to MCP Implementation Pattern section)
   - `config.py` - Complete configuration
   - `mcp_genie_client.py` - Full client code
   - `mcp_uc_functions_client.py` - Full client code
   - `mcp_knowledge_assistant_client.py` - Full client code

### Prerequisites (Already Done Automatically)

✅ **UC Functions created**: Project-specific functions (e.g., `lookup_member`, `lookup_claims`, `lookup_providers`)  
✅ **Knowledge documents uploaded**: Project-specific docs in `/Volumes/{catalog}/{schema}/knowledge_docs/`  
✅ **MCP client files included**: `mcp_clients/` folder (dormant)  
✅ **Standard app deployed**: Working in Databricks workspace

**Note**: UC functions and knowledge documents are tailored to your specific project type and data model.

**MCP Components**:
- **Required**: Genie Space + UC Functions (core MCP functionality)
- **Optional**: Knowledge Assistant (document search - only if endpoint available)

---

## 📋 Knowledge Documents - Content Templates & Best Practices

**CRITICAL: Always save knowledge documents locally in `data/` folder BEFORE uploading to volumes!**

### File Structure:
```
your-project/
├── data/                                    # ⭐ LOCAL knowledge documents
│   ├── agent_knowledge_source_guide.txt    # What data sources are available
│   ├── knowledge_source_descriptions.txt   # How to use each data source
│   ├── domain_policies.txt                 # Domain-specific policies/rules
│   └── faq_documentation.txt               # Common questions and answers
```

**Why save locally first:**
- ✅ Version control with git
- ✅ Easy to update and redeploy
- ✅ Can be embedded in notebook `05_upload_knowledge_docs.py`
- ✅ Portable across environments

---

### Template 1: Agent Knowledge Source Guide

**File:** `data/agent_knowledge_source_guide.txt`

**Purpose:** Tells the AI agent what data sources and tools are available

**Template (HEDIS Quality Example):**
```
HEDIS Quality Measures Agent - Knowledge Source Guide

=== AVAILABLE DATA SOURCES ===

1. GENIE SPACE (Natural Language SQL)
   - Purpose: Query structured data tables using natural language
   - Use when: User asks about aggregate data, trends, or statistics
   - Example queries:
     * "What is the average quality score?"
     * "Show me compliance rates by measure"
     * "How many members closed gaps this year?"

2. UC FUNCTIONS (Structured Lookups)
   - Purpose: Precise lookups for specific members, measures, or gaps
   - Available functions:
     * lookup_member(member_id) - Get member demographics and quality status
     * lookup_member_measures(member_id) - Get all quality measures for a member
     * lookup_member_gaps(member_id) - Get open gaps in care for a member
     * members_with_gap(measure_code) - Find all members with specific gap
     * lookup_measure_performance(measure_code) - Get overall measure performance
     * members_at_risk(measure_code) - Find members at risk for a measure
   - Use when: User asks about specific member ID or measure code

3. KNOWLEDGE ASSISTANT (Document Search)
   - Purpose: Answer questions about policies, guidelines, and definitions
   - Use when: User asks "what is", "how to", or "explain"
   - Topics covered:
     * HEDIS measure definitions and specifications
     * NCQA compliance requirements
     * Gap closure procedures
     * Quality improvement guidelines

=== DECISION TREE ===

If user asks about a SPECIFIC MEMBER (e.g., "Show me M000001's gaps"):
  → Use UC Functions (lookup_member, lookup_member_gaps)

If user asks AGGREGATE questions (e.g., "What's our average score?"):
  → Use Genie Space

If user asks DEFINITION questions (e.g., "What is BCS?"):
  → Use Knowledge Assistant

If user asks WHO HAS questions (e.g., "Which members have BCS gaps?"):
  → Use UC Functions (members_with_gap)

=== BEST PRACTICES ===

1. Always use member_id for member lookups (format: M000001, M000002, etc.)
2. Use standard HEDIS measure codes (BCS, CDC, CBP, etc.)
3. When data is not found, suggest alternative queries
4. Combine multiple tools for complex questions
5. Always cite the data source in your response
```

**Template (Risk Adjustment/HCC Example):**
```
HCC Risk Adjustment Agent - Knowledge Source Guide

=== AVAILABLE DATA SOURCES ===

1. GENIE SPACE (Natural Language SQL)
   - Purpose: Query member RAF scores, HCC distribution, revenue data
   - Use when: User asks about aggregate analytics
   - Example queries:
     * "What is our average RAF score?"
     * "Show me revenue opportunity by HCC category"
     * "How many members have RAF > 2.0?"

2. UC FUNCTIONS (Structured Lookups)
   - Available functions:
     * lookup_member(member_id) - Member demographics and RAF
     * lookup_hcc_codes(member_id) - All HCC codes for a member
     * lookup_raf_scores(member_id) - RAF score breakdown
     * lookup_diagnoses(member_id) - Diagnosis history
     * members_with_hcc(hcc_code) - Members with specific HCC
     * get_member_revenue_opportunity(member_id) - Revenue gap calculation
   - Use when: User asks about specific member or HCC code

3. KNOWLEDGE ASSISTANT (Document Search)
   - Topics covered:
     * CMS-HCC V28 model documentation
     * HCC coding guidelines and rules
     * RAF score calculation methodology
     * Revenue optimization strategies

=== DECISION TREE ===

If user asks about SPECIFIC MEMBER:
  → Use lookup_member or lookup_hcc_codes

If user asks about SPECIFIC HCC CODE (e.g., "Who has HCC 85?"):
  → Use members_with_hcc

If user asks REVENUE questions:
  → Use Genie Space for aggregates, or get_member_revenue_opportunity for specific member

If user asks CODING RULES (e.g., "What qualifies for HCC 19?"):
  → Use Knowledge Assistant
```

---

### Template 2: Knowledge Source Descriptions

**File:** `data/knowledge_source_descriptions.txt`

**Purpose:** Detailed descriptions of each data source for the agent

**Template:**
```
DATA SOURCE DESCRIPTIONS - HEDIS Quality Measures

=== GENIE SPACE ===
The Genie Space provides natural language access to structured HEDIS quality data tables:

Tables available:
- quality_summary: Overall quality performance metrics
- measure_performance: Performance by individual HEDIS measure
- member_measures: Member-level measure compliance
- gap_closure_tracking: Gap in care status and closure dates

The Genie Space should be used for:
- Aggregate statistics and trends
- Cross-measure analysis
- Time-series queries
- Cohort identification

Example use cases:
- "What percentage of members closed BCS gaps in Q4?"
- "Compare CDC performance across age groups"
- "Show me top 10 measures by gap count"

=== UC FUNCTIONS ===
Unity Catalog Functions provide fast, indexed lookups:

lookup_member(member_id STRING)
  Returns: Member demographics, enrollment, current quality status
  Use when: Need basic member information
  Example: lookup_member('M000001')

lookup_member_measures(member_id STRING)
  Returns: All HEDIS measures applicable to member with compliance status
  Use when: Need complete quality profile for a member
  Example: lookup_member_measures('M000001')

lookup_member_gaps(member_id STRING)
  Returns: All open gaps in care with recommended actions
  Use when: Care management needs gap closure list
  Example: lookup_member_gaps('M000001')

members_with_gap(measure_code STRING)
  Returns: All members with open gap for specific measure
  Use when: Need to identify outreach cohort
  Example: members_with_gap('BCS')

lookup_measure_performance(measure_code STRING)
  Returns: Overall performance statistics for a measure
  Use when: Need measure-level summary
  Example: lookup_measure_performance('CDC')

members_at_risk(measure_code STRING)
  Returns: Members at risk of missing measure requirements
  Use when: Proactive outreach planning
  Example: members_at_risk('CBP')

=== KNOWLEDGE ASSISTANT ===
Document search covering HEDIS specifications and policies:

Documents indexed:
1. HEDIS measure specifications (technical definitions)
2. NCQA compliance requirements (regulatory requirements)
3. Gap closure procedures (operational guidelines)
4. Quality improvement protocols (best practices)

The Knowledge Assistant should be used for:
- "What is" questions (definitions)
- "How to" questions (procedures)
- Policy interpretation
- Regulatory compliance questions

Example use cases:
- "What are the exclusion criteria for BCS?"
- "How do I document gap closure?"
- "What is the NCQA requirement for CDC testing frequency?"
```

---

### Template 3: Domain-Specific Policies

**File:** `data/domain_policies.txt`

**Purpose:** Business rules, policies, and domain knowledge

**Template (HEDIS Quality):**
```
HEDIS QUALITY MEASURES - POLICIES AND GUIDELINES

=== MEASURE DEFINITIONS ===

BCS (Breast Cancer Screening)
- Target Population: Women ages 50-74
- Requirement: Mammogram within 27 months
- Compliance Rate: Goal ≥ 75%
- Gap Closure Window: Must complete by 12/31 for current year credit
- Exclusions: Bilateral mastectomy, advanced illness

CDC (Comprehensive Diabetes Care)
- Target Population: Members ages 18-75 with Type 1 or Type 2 diabetes
- Requirements:
  * HbA1c test (at least one per year)
  * Eye exam (retinal) within 24 months
  * Medical attention for nephropathy
- Compliance Rate: Goal ≥ 80% for HbA1c testing
- Exclusions: Advanced illness, palliative care

CBP (Controlling High Blood Pressure)
- Target Population: Adults ages 18-85 with hypertension diagnosis
- Requirement: BP < 140/90 at most recent reading
- Compliance Rate: Goal ≥ 70%
- Gap Closure: Requires in-person visit with BP measurement

=== GAP CLOSURE PROCEDURES ===

Step 1: Identify Open Gaps
- Run members_with_gap('MEASURE_CODE') to get list
- Prioritize by: Risk score, past engagement, measure weight

Step 2: Member Outreach
- Phone call or letter with measure explanation
- Schedule appointment if needed
- Provide educational materials

Step 3: Service Delivery
- Complete required screening/test
- Document in medical record with CPT code
- Ensure claims submission within 30 days

Step 4: Verification
- Confirm claim received and processed
- Update gap status in tracking system
- Calculate updated compliance rate

=== NCQA COMPLIANCE REQUIREMENTS ===

Documentation Standards:
- All services must have valid CPT/HCPCS codes
- Date of service must be within measurement year
- Provider must be in network (or authorized out-of-network)
- Medical records must be available for audit

Reporting Timeline:
- Data collection period: January 1 - December 31
- Supplemental data deadline: March 31
- Final submission: June 30
- NCQA audit: August - October

Quality Thresholds (5-Star Rating):
- 5 Stars: ≥ 90% compliance
- 4 Stars: 80-89% compliance
- 3 Stars: 70-79% compliance
- 2 Stars: 60-69% compliance
- 1 Star: < 60% compliance

=== MEASURE WEIGHTS (STAR RATING) ===

High Impact (3x weight):
- CDC (Comprehensive Diabetes Care)
- CBP (Controlling Blood Pressure)
- COL (Colorectal Cancer Screening)

Medium Impact (2x weight):
- BCS (Breast Cancer Screening)
- OMW (Osteoporosis Management in Women)

Standard Impact (1x weight):
- All other HEDIS measures

=== REVENUE IMPACT ===

Star Rating Impact on Revenue:
- 5 Stars: 5% bonus payment
- 4 Stars: 3% bonus payment
- 3 Stars: Base payment (no bonus)
- 2 Stars: -2% penalty
- 1 Star: -5% penalty

Per-Member-Per-Month (PMPM) Impact:
- Each 0.1 star improvement ≈ $1.50 PMPM
- For 100,000 members: 0.5 star improvement = $9M annual revenue

Gap Closure Value:
- High-weight measure gap closed = ~$150 revenue impact
- Medium-weight measure gap closed = ~$100 revenue impact
- Standard measure gap closed = ~$50 revenue impact
```

**Template (HCC Risk Adjustment):**
```
HCC RISK ADJUSTMENT - POLICIES AND GUIDELINES

=== CMS-HCC V28 MODEL OVERVIEW ===

Purpose: Predict healthcare costs based on member demographics and diagnoses

Model Components:
1. Demographic factors (age, sex)
2. Diagnosis-based HCCs (Hierarchical Condition Categories)
3. Interaction terms (disease interactions, disability status)

RAF Score Calculation:
RAF Score = Sum of all coefficient values
Average RAF = 1.0 (population average)
RAF > 1.0 = Higher expected cost than average
RAF < 1.0 = Lower expected cost than average

=== HCC CATEGORIES AND COEFFICIENTS ===

High-Value HCCs (RAF coefficient > 0.5):
- HCC 85: Congestive Heart Failure (0.368)
- HCC 18: Diabetes with Chronic Complications (0.318)
- HCC 111: Chronic Obstructive Pulmonary Disease (0.328)
- HCC 134: Dialysis Status (1.498)

Medium-Value HCCs (RAF coefficient 0.2-0.5):
- HCC 19: Diabetes without Complication (0.104)
- HCC 108: Vascular Disease (0.288)
- HCC 161: Chronic Kidney Disease Stage 4 (0.237)

=== CODING GUIDELINES ===

Documentation Requirements:
1. Diagnosis must be documented by a qualified provider
2. Must be documented at least once per calendar year
3. Must represent current, active condition (not history)
4. Must be supported by clinical evidence and treatment

Specificity Rules:
- Use most specific ICD-10 code available
- Unspecified codes (e.g., E11.9) have lower capture rates
- Include laterality, severity, and complications when applicable

Acceptable Documentation:
✅ "Patient has CHF, currently managed with Lasix"
✅ "COPD with acute exacerbation, prescribed prednisone"
✅ "CKD Stage 4, GFR 22, nephrology follow-up scheduled"

Unacceptable Documentation:
❌ "History of CHF" (not current)
❌ "Rule out COPD" (not confirmed diagnosis)
❌ "Chronic kidney disease" (missing stage/specificity)

=== HIERARCHIES ===

Only the highest HCC in a hierarchy is counted:

Diabetes Hierarchy:
- HCC 17: Diabetes with Acute Complications → counts
- HCC 18: Diabetes with Chronic Complications → counts
- HCC 19: Diabetes without Complication → drops if 17 or 18 present

CKD Hierarchy:
- HCC 134: Dialysis Status → counts
- HCC 135: Acute Renal Failure → counts
- HCC 136: CKD Stage 4 → drops if 134 or 135 present
- HCC 137: CKD Stage 3 → drops if any above present

=== REVENUE OPPORTUNITY IDENTIFICATION ===

Undercoded Member Criteria:
- Has ≤ 2 HCC codes but high utilization
- Chronic conditions documented but not coded
- Speciality visits without associated diagnoses
- Gap between expected and actual RAF score

Coding Opportunity Workflow:
1. Identify undercoded members (≤ 1 HCC with chronic conditions)
2. Review medical records for documented conditions
3. Engage provider to confirm current active status
4. Submit recapture claim or coordinate visit
5. Monitor for claim acceptance and RAF update

Revenue Calculation:
- Revenue per member = RAF score × Base rate
- Base rate (example): $800/month
- Member with RAF 0.8 → $640/month revenue
- Member with RAF 1.5 → $1,200/month revenue
- Coding gap of 0.7 RAF = $560/month = $6,720/year per member

=== RISK ADJUSTMENT AUDIT PREPAREDNESS ===

CMS RADV Audit Requirements:
- Medical records must support all HCC codes submitted
- Documentation must meet CMS guidelines
- Provider signature and credentials required
- Service date must be within measurement year

Common Audit Failures:
❌ Diagnosis documented but no treatment plan
❌ Copy-forward documentation without updates
❌ Missing provider signature or credentials
❌ Diagnosis contradicts other clinical findings

Audit Success Strategies:
✅ Quarterly documentation reviews
✅ Provider education on specificity
✅ Real-time coding validation
✅ Medical record completeness checks
```

---

### Template 4: FAQ Documentation

**File:** `data/faq_documentation.txt`

**Purpose:** Common questions and answers

**Template:**
```
FREQUENTLY ASKED QUESTIONS - HEDIS QUALITY MEASURES

=== MEMBER-LEVEL QUESTIONS ===

Q: How do I look up a specific member's quality status?
A: Use lookup_member('MEMBER_ID') for basic info, or lookup_member_measures('MEMBER_ID') for complete quality profile.

Q: How do I find all open gaps for a member?
A: Use lookup_member_gaps('MEMBER_ID') - this returns all open gaps with recommended actions.

Q: What if a member ID is not found?
A: Verify the member ID format (should be M000001, M000002, etc.). Check if member is currently enrolled.

=== MEASURE-LEVEL QUESTIONS ===

Q: How do I see overall performance for a measure?
A: Use lookup_measure_performance('MEASURE_CODE') - returns compliance rate, gap count, and trends.

Q: Which members have a specific gap?
A: Use members_with_gap('MEASURE_CODE') - returns list of members with that open gap.

Q: What are the valid measure codes?
A: BCS (Breast Cancer Screening), CDC (Diabetes Care), CBP (Blood Pressure), COL (Colorectal Screening), OMW (Osteoporosis), and others.

=== GAP CLOSURE QUESTIONS ===

Q: How is a gap marked as closed?
A: When a claim is received with the required CPT code and service date within the measurement year.

Q: Can gaps be closed retroactively?
A: Yes, if the service was performed in the measurement year but claim was delayed. Supplemental data deadline is March 31.

Q: What if a member refuses the screening?
A: Document refusal in medical record. This does NOT close the gap for HEDIS purposes, but documents the outreach attempt.

=== COMPLIANCE QUESTIONS ===

Q: What is our current compliance rate?
A: Ask "What is our overall compliance rate?" or use Genie Space for aggregate statistics.

Q: How many stars are we projected to achieve?
A: Depends on final compliance rates. Use revenue_opportunity table to see projection.

Q: Which measures have the biggest impact on star rating?
A: High-weight measures: CDC, CBP, COL (3x weight). Focus gap closure efforts here first.

=== DATA QUESTIONS ===

Q: How often is data refreshed?
A: Quality tables are updated nightly. Claims typically process within 7-14 days of service.

Q: Why might a member show an open gap when I know the service was completed?
A: Possible reasons: (1) Claim not yet processed, (2) Wrong CPT code used, (3) Service date outside measurement year, (4) Provider not in network.

Q: Can I see historical data?
A: Yes, Genie Space can query historical compliance rates and trends over time.
```

---

## 🎯 Knowledge Assistant Setup Guide (Step-by-Step)

**After running `05_upload_knowledge_docs.py` notebook and documents are in the volume:**

### Step 1: Navigate to Knowledge Assistant Creation

1. Open Databricks Workspace
2. Go to: **Machine Learning → Serving**
3. Click **"Create Serving Endpoint"**
4. Select **"Knowledge Assistant"** as endpoint type

### Step 2: Fill in Basic Info

**Name field:**
```
[project_name]_knowledge_assistant
```
Examples:
- `hedis_quality_knowledge_assistant`
- `hcc_risk_knowledge_assistant`
- `pharmacy_benefits_knowledge_assistant`

**Description field (fill this in the UI):**

**For HEDIS Quality Project:**
```
Answers questions about HEDIS quality measures, NCQA compliance requirements, gap closure procedures, and quality improvement guidelines. Provides policy interpretations, measure specifications, and operational best practices for the quality analytics team.
```

**For HCC Risk Adjustment Project:**
```
Answers questions about CMS-HCC V28 model, HCC coding guidelines, RAF score calculations, and revenue optimization strategies. Provides coding rules, documentation requirements, and audit preparedness guidance for the risk adjustment team.
```

**For Pharmacy Benefits Project:**
```
Answers questions about formulary policies, prior authorization requirements, drug utilization management, and pharmacy benefits administration. Provides medication guidelines, drug interaction warnings, and cost optimization strategies for the pharmacy team.
```

### Step 3: Configure Knowledge Source

**Type:** UC Files

**Source:** Click folder icon and navigate to:
```
/Volumes/[catalog_name]/[schema_name]/knowledge_docs
```

**Name field:** Leave blank (optional)

**"Describe the content" field (CRITICAL - fill this in detail):**

**For HEDIS Quality Project:**
```
This knowledge base contains comprehensive documentation for HEDIS quality measures analytics:

1. Agent Knowledge Source Guide - Explains which data sources (Genie, UC Functions, Knowledge Assistant) to use for different types of questions. Includes decision trees and best practices.

2. Knowledge Source Descriptions - Detailed documentation of each UC Function with parameters, return values, and example use cases. Explains when to use Genie Space vs UC Functions.

3. HEDIS Policies and Guidelines - Complete specifications for all HEDIS measures including BCS, CDC, CBP, and COL. Covers measure definitions, target populations, compliance requirements, exclusion criteria, gap closure procedures, NCQA compliance standards, and revenue impact calculations.

4. FAQ Documentation - Common questions and answers about member lookups, measure performance, gap closure, compliance rates, and data refresh timing.

Use this knowledge base to answer questions about: HEDIS measure specifications, NCQA requirements, gap closure procedures, compliance thresholds, star rating calculations, documentation standards, and quality improvement strategies.
```

**For HCC Risk Adjustment Project:**
```
This knowledge base contains comprehensive documentation for HCC risk adjustment analytics:

1. Agent Knowledge Source Guide - Explains when to use Genie Space (aggregate analytics), UC Functions (member/HCC lookups), or Knowledge Assistant (coding rules) with specific decision trees.

2. Knowledge Source Descriptions - Complete documentation of all risk adjustment UC Functions including lookup_member, lookup_hcc_codes, lookup_raf_scores, members_with_hcc, and get_member_revenue_opportunity with examples.

3. HCC Risk Adjustment Policies - CMS-HCC V28 model documentation, HCC categories and coefficients, coding guidelines, documentation requirements, hierarchy rules, revenue opportunity identification, and RADV audit preparedness strategies.

4. FAQ Documentation - Common questions about RAF score calculation, undercoded member identification, coding guidelines, documentation requirements, and revenue impact.

Use this knowledge base to answer questions about: CMS-HCC V28 model, HCC coding rules, RAF calculation methodology, documentation requirements, hierarchy logic, revenue optimization, and audit compliance.
```

### Step 4: Advanced Settings (Optional)

- **Embedding model:** Default (recommended)
- **Chunk size:** 512 (default)
- **Chunk overlap:** 50 (default)

### Step 5: Create and Wait

1. Click **"Create Agent"** button
2. Wait 5-10 minutes for endpoint provisioning
3. Status will change: PROVISIONING → READY
4. Once READY, copy the **Endpoint ID** (format: `ka-XXXXX-endpoint`)

---

## 🎨 Genie Space Setup Guide (Step-by-Step)

### Step 1: Create Genie Space

1. Open Databricks Workspace
2. Navigate to: **Data Intelligence → Genie**
3. Click **"Create Genie Space"**
4. Select your **catalog** and **schema** (from your project)
5. Name: `[project_name]_genie`
   - Example: `hedis_quality_genie`, `hcc_risk_genie`
6. Genie automatically discovers your UC functions
7. **Copy the Genie Space ID** from the URL
   - Format: `01f06a3068a81406a386e8eaefc74545`
   - URL looks like: `.../genie/spaces/01f06a3068a8...`

### Step 2: Add Genie Instructions (CRITICAL!)

After creating the Genie Space, click on the **"Instructions"** tab and add general instructions:

**For HEDIS Quality Project:**
```
Examples:
* "HEDIS" stands for Healthcare Effectiveness Data and Information Set
* BCS = Breast Cancer Screening, CDC = Comprehensive Diabetes Care, CBP = Controlling Blood Pressure, COL = Colorectal Cancer Screening
* Member IDs are in format M000001, M000002, etc.
* Measure codes use standard HEDIS abbreviations (BCS, CDC, CBP, COL, OMW)
* Compliance rate is calculated as: (members_compliant / total_eligible_members) * 100
* Gap in care means a member is eligible for a measure but has not completed the required screening/test
* Quality score ranges from 0-100%, where higher is better
* Star rating ranges from 1-5 stars based on compliance thresholds
* When a user asks for performance, show compliance rate percentage
* When a user asks about gaps, show count of members with open gaps
* Always include the measurement period (year) in results

(You can use markdown text)
```

**For HCC Risk Adjustment Project:**
```
Examples:
* HCC stands for Hierarchical Condition Category
* RAF stands for Risk Adjustment Factor (average = 1.0)
* Member IDs are in format M000001, M000002, etc.
* HCC codes are in format HCC_85, HCC_19, HCC_108, etc.
* RAF scores above 1.0 indicate higher than average expected costs
* RAF scores below 1.0 indicate lower than average expected costs
* Revenue opportunity = (potential_raf - current_raf) * base_rate * 12 months
* Undercoded members typically have ≤ 1 HCC code despite having chronic conditions
* When user asks about revenue, show both current revenue and opportunity
* When user asks about specific HCC, include the HCC description and coefficient
* Always show RAF score to 2 decimal places
* CMS-HCC V28 is the current risk adjustment model

(You can use markdown text)
```

**For Pharmacy Benefits Project:**
```
Examples:
* NDC stands for National Drug Code (11-digit identifier)
* Prior authorization (PA) is required for certain high-cost medications
* Generic substitution can save 70-90% compared to brand name
* Member IDs are in format M000001, M000002, etc.
* Drug utilization is measured in days supply, not quantity
* Cost is total plan paid amount plus member copay
* When user asks about savings, show generic vs brand comparison
* When user asks about utilization, show total days supply and fill count
* Always include drug class or therapeutic category in results
* Formulary tier affects member copay: Tier 1 (lowest) to Tier 4 (highest)

(You can use markdown text)
```

### Step 3: Add SQL Expression Instructions (Optional but Recommended)

Click on the **"SQL Expressions"** tab to teach Genie specific patterns:

**For HEDIS Quality Project:**
```sql
-- Example: Calculate compliance rate
SELECT 
  measure_code,
  COUNT(DISTINCT CASE WHEN is_compliant THEN member_id END) * 100.0 / 
  COUNT(DISTINCT member_id) as compliance_rate_pct
FROM member_measures
GROUP BY measure_code

-- Example: Find open gaps
SELECT member_id, measure_code, gap_closure_action
FROM member_measures
WHERE is_compliant = FALSE

-- Example: Top performers
SELECT measure_code, compliance_rate_pct
FROM measure_performance
ORDER BY compliance_rate_pct DESC
LIMIT 10
```

**For HCC Risk Adjustment Project:**
```sql
-- Example: Calculate average RAF by member
SELECT 
  member_id,
  SUM(hcc_coefficient) as total_raf_score,
  COUNT(DISTINCT hcc_code) as hcc_count
FROM member_hcc_codes
GROUP BY member_id

-- Example: Revenue opportunity
SELECT 
  member_id,
  current_raf,
  expected_raf,
  (expected_raf - current_raf) * 800 * 12 as annual_revenue_opportunity
FROM revenue_opportunity
WHERE expected_raf > current_raf

-- Example: Members by HCC
SELECT member_id, hcc_code, hcc_description
FROM member_hcc_codes
WHERE hcc_code = 'HCC_85'
```

### Step 4: Copy Genie Space ID

1. Navigate back to Genie Spaces list
2. Open your newly created Genie Space
3. **Copy the Genie Space ID from the URL**
   - URL format: `https://...databricks.net/.../genie/spaces/01f06a3068a8...`
   - ID format: `01f06a3068a81406a386e8eaefc74545` (32 characters)
4. Save this ID - you'll need it for MCP integration

---

### Step 5: Create Knowledge Assistant Endpoint (10 minutes) - **OPTIONAL**

**Skip this step if Knowledge Assistant endpoint is not available in your workspace.**

**Note**: Refer to the detailed "Knowledge Assistant Setup Guide" section above for complete instructions on filling in the description and content description fields.

**Quick summary:**
1. Navigate to: **Machine Learning → Serving**
2. Click **"Create Serving Endpoint"**
3. Select **"Knowledge Assistant"** type
4. Fill in description (see templates above in Knowledge Assistant Setup Guide)
5. **Source**: Point to volume `/Volumes/{catalog}/{schema}/knowledge_docs`
6. Fill in "Describe the content" field (see templates above - CRITICAL!)
7. Name: `[project_name]_knowledge_assistant`
8. Wait for endpoint to be "Ready" (~5-10 min)
9. **Copy the Endpoint ID**
   - Format: `ka-d0808962-endpoint`
   - Found in endpoint details

**Note**: MCP will work without Knowledge Assistant - you'll still have Genie queries and UC Functions.

---

### Step 6: Run "Add MCP" Command

Simply say:

```
Add MCP to my project
```

I will:
1. ✅ Ask you for the Genie Space ID (required)
2. ✅ Ask you for the Knowledge Assistant Endpoint ID (optional - press Enter to skip)
3. ✅ Update `mcp_clients/config.py` with your IDs
4. ✅ Modify `dashboard/your_dashboard.py` to add MCP Search tab
5. ✅ Update `dashboard/requirements.txt` with MCP dependencies
6. ✅ **Update `dashboard/app.yaml` with MCP environment variables**
7. ✅ **Create test notebook in `test_notebooks/` for agent testing** ⭐ NEW
8. ✅ Redeploy the app automatically
9. ✅ Provide updated workspace URL

---

### Step 7: Verify MCP Integration

After redeployment:
1. Open app in Databricks workspace
2. **New tab appears**: "🔍 MCP Search"
3. **Clean UI** with single status line at top ⭐ NEW
   - Shows: "✅ AI Agent Ready | 8 tools available"
   - All detailed connectivity info in collapsible dropdown
4. Test query: "Show me member 1001's claims"
5. If KA configured: Try knowledge query: "What is the prior authorization policy?"

**Clean MCP Search UI:** ⭐ NEW
- **Main screen**: Single status indicator, search box, example queries
- **Dropdown**: "🔧 System Status & Connectivity Details" (collapsed by default)
  - Core Services: AI Model, Genie MCP, UC Functions MCP (with server URLs)
  - Optional Services: Knowledge Assistant
  - Shows function lists, server URLs, and detailed health info
- **No clutter**: All initialization messages removed from UI
- **Focus**: Search-first interface, troubleshooting details when needed

**Test Notebook Created:** ⭐ NEW
- Location: `test_notebooks/test_{project}_mcp_agent.ipynb`
- Purpose: Interactive testing and debugging of the MCP agent
- **24-36x faster** than testing through Streamlit UI
- See `test_notebooks/QUICK_START.md` for usage guide

### What Gets Modified

**Files Updated:**
- `mcp_clients/config.py` - Add your Genie ID (required) and optionally KA ID
- `dashboard/your_dashboard.py` - Add MCP Search tab
- `dashboard/requirements.txt` - Add `databricks-mcp`, `langchain`
- **`dashboard/app.yaml` - Add MCP environment variables** ⭐ NEW

**Files Created:** ⭐ NEW
- `test_notebooks/test_{project}_mcp_agent.ipynb` - Interactive test notebook
- `test_notebooks/README.md` - Documentation
- `test_notebooks/QUICK_START.md` - Quick start guide
- `.gitignore` updated to include `test_notebooks/`

**app.yaml MCP Configuration:**
```yaml
env:
  # ... existing SQL Warehouse and Catalog config ...
  
  # MCP Configuration (added when you run "Add MCP")
  - name: 'GENIE_SPACE_ID'
    value: '01f06a3068a81406a386e8eaefc74545'  # From Step 1
  
  - name: 'KNOWLEDGE_ASSISTANT_ENDPOINT_ID'
    value: 'ka-d0808962-endpoint'  # From Step 2 (optional)
  
  - name: 'AI_MODEL_NAME'
    value: 'databricks-meta-llama-3-1-70b-instruct'  # Default model
```

**Files Unchanged:**
- All notebooks remain the same
- All data and UC functions unchanged
- Original app tabs/features unchanged

### MCP Features Added

**🔍 MCP Search Tab:**
- Natural language queries over structured data (via Genie) ✅ Required
- Member/claims/provider lookup (via UC Functions) ✅ Required
- Document search and policy questions (via Knowledge Assistant) ⚠️ Optional
- Conversation history and context

**System Status:**
- Real-time MCP service health monitoring
- Connection status: Genie (required), UC Functions (required), Knowledge Assistant (optional)
- Available tools/functions listing

**🧪 Test Notebook:** ⭐ NEW
- Interactive Jupyter notebook for agent testing
- **24-36x faster** iteration than Streamlit UI
- Full debugging capabilities
- Test individual MCP clients or complete agent
- Perfect for development and troubleshooting
- Location: `test_notebooks/test_{project}_mcp_agent.ipynb`

### Time Required

- **Manual setup (minimum)**: 5 minutes (Genie only)
- **Manual setup (full)**: 15 minutes (Genie + Knowledge Assistant)
- **"Add MCP" command**: 2-3 minutes (automated)
- **Total**: ~8-18 minutes depending on whether you include Knowledge Assistant

### Rollback

If you want to remove MCP features:

```
Remove MCP from my project
```

This will:
- Restore original app (remove MCP tab)
- Keep UC functions and knowledge docs (still useful)
- Keep MCP client files (can re-add later)

---

## ⭐ MCP Implementation Pattern (PROVEN WORKING)

**Use this exact pattern for ALL MCP integrations to avoid common errors!**

This pattern has been tested and verified to work correctly. Following this ensures successful MCP deployment.

---

## 🎯 Quick Reference - MCP Implementation

**For bulletproof MCP implementation, follow this exact order:**

1. **📁 Folder Structure** → All MCP files go in `dashboard/` folder (NOT separate `mcp_clients/` folder)
2. **📋 Copy Templates** → Use COMPLETE code templates from section 10 below (copy-paste ready)
3. **⚙️ Configure** → Update `config.py` with your catalog, schema, Genie ID
4. **✅ Checklist** → Follow step-by-step checklist in section 10.5
5. **🔧 Critical Patterns:**
   - Use `Field(default="...")` for ALL BaseTool definitions (Pydantic v2)
   - Use 8B AI model (not 70B)
   - Grant EXECUTE permissions on UC Functions
   - Keep all files in `dashboard/` folder

**Jump to:**
- [Folder Structure](#-mcp-folder-structure-critical---do-not-deviate) - Section below
- [Complete Code Templates](#10-complete-mcp-code-templates-) - Section 10
- [Implementation Checklist](#105-mcp-implementation-checklist-) - Section 10.5

---

## 📁 MCP Folder Structure (CRITICAL - DO NOT DEVIATE!)

**⚠️ CRITICAL: MCP client files MUST be in the dashboard/ folder, NOT a separate mcp_clients/ folder!**

```
your-project/
├── dashboard/                          # Self-contained app folder
│   ├── app.yaml                       # App configuration
│   ├── requirements.txt               # App dependencies
│   ├── your_dashboard.py              # Main Streamlit app
│   ├── config.py                      # MCP configuration ✅
│   ├── mcp_genie_client.py           # Genie MCP client ✅
│   ├── mcp_uc_functions_client.py    # UC Functions MCP client ✅
│   ├── mcp_knowledge_assistant_client.py  # Knowledge Assistant client ✅
│   └── your_agent.py                  # MCP Agent ✅
```

**❌ WRONG - DO NOT CREATE SEPARATE FOLDER:**
```
your-project/
├── dashboard/
│   └── your_dashboard.py
├── mcp_clients/                       # ❌ NO! Don't do this!
│   ├── config.py
│   ├── mcp_genie_client.py
│   └── ...
```

**Why dashboard folder?**
- ✅ Databricks uploads entire `dashboard/` folder as the app
- ✅ All imports work without path manipulation
- ✅ Self-contained and portable
- ❌ Separate folder causes import errors in Databricks Apps

---

### 1. **Foundation Model Configuration** ⚠️ CRITICAL

**Always use the 8B model for MCP agents:**

```python
# ✅ CORRECT - Use 8B model (exists as Foundation Model endpoint)
AI_MODEL_NAME = "databricks-meta-llama-3-1-8b-instruct"

# ❌ WRONG - 70B model doesn't exist as Foundation Model endpoint
AI_MODEL_NAME = "databricks-meta-llama-3-1-70b-instruct"  # ERROR: ENDPOINT_NOT_FOUND
```

**Why 8B model?**
- ✅ Available as Foundation Model endpoint in Databricks
- ✅ Faster response times
- ✅ Lower cost
- ✅ Sufficient for most MCP agent tasks
- ❌ 70B model is NOT available as a Foundation Model endpoint

---

### 1.5. **LangChain BaseTool Pydantic v2 Compatibility** ⚠️ CRITICAL

**ALWAYS use Field() for tool definitions to ensure Pydantic v2 compatibility:**

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# ✅ CORRECT - Pydantic v2 compatible (use Field())
class GenieMCPTool(BaseTool):
    name: str = Field(default="genie_mcp_query")
    description: str = Field(default="Query structured data using natural language")
    args_schema: type[BaseModel] = GenieQueryInput
    
    def _run(self, query: str) -> str:
        # Implementation
        pass
```

```python
# ❌ WRONG - Pydantic v2 error: field overridden by non-annotated attribute
class GenieMCPTool(BaseTool):
    name: str = "genie_mcp_query"  # NO! Direct assignment not allowed
    description: str = "Query structured data"  # NO!
    args_schema: type[BaseModel] = GenieQueryInput
```

**Why this is critical:**
- ❌ Without Field(): "Field 'name' defined on a base class was overridden by a non-annotated attribute"
- ✅ With Field(): Pydantic v2 properly handles field inheritance
- LangChain BaseTool uses Pydantic models internally
- Pydantic v2 is stricter about field definitions in inherited classes

**This applies to ALL tool definitions:**
- Genie MCP tools
- UC Functions MCP tools
- Knowledge Assistant MCP tools
- Any custom LangChain tools you create

---

### 2. **Use Databricks OpenAI Client** ⚠️ CRITICAL

**Always use the native Databricks SDK client, NOT LangChain's ChatOpenAI:**

```python
# ✅ CORRECT - Use Databricks native OpenAI client
from databricks.sdk import WorkspaceClient

workspace_client = WorkspaceClient()
llm_client = workspace_client.serving_endpoints.get_open_ai_client()

# Now use llm_client for chat completions
response = llm_client.chat.completions.create(
    model="databricks-meta-llama-3-1-8b-instruct",
    messages=messages,
    tools=openai_tools,
    tool_choice="auto"
)
```

```python
# ❌ WRONG - Don't use LangChain's ChatOpenAI
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model=AI_MODEL_NAME,
    openai_api_key="DUMMY_KEY",  # Doesn't work properly
    openai_api_base=f"{workspace_client.config.host}/serving-endpoints"
)
```

**Why Databricks native client?**
- ✅ Automatically authenticated with workspace
- ✅ Correct endpoint configuration
- ✅ Works with Foundation Models
- ✅ No API key confusion
- ✅ Better error messages

---

### 3. **Manual Tool Calling Pattern** ⚠️ CRITICAL

**Use manual tool execution, NOT LangChain AgentExecutor:**

```python
# ✅ CORRECT - Manual tool calling pattern
def chat(self, user_input: str, chat_history: List[Dict[str, str]]) -> str:
    """Chat with manual tool execution"""
    
    # 1. Convert tools to OpenAI format
    openai_tools = []
    for tool in self.tools:
        tool_spec = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.model_json_schema()
            }
        }
        openai_tools.append(tool_spec)
    
    # 2. Build messages with history
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history[-10:])  # Last 10 messages
    messages.append({"role": "user", "content": user_input})
    
    # 3. Call LLM with tools
    response = self.llm_client.chat.completions.create(
        model=self.ai_model_name,
        messages=messages,
        tools=openai_tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    # 4. Execute tool calls if present
    if message.tool_calls:
        tool_results = []
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Execute tool
            if tool_name in self.tool_map:
                tool = self.tool_map[tool_name]
                result = tool._run(**tool_args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": str(result)
                })
        
        # 5. Add tool results and get final response
        messages.extend(tool_results)
        final_response = self.llm_client.chat.completions.create(
            model=self.ai_model_name,
            messages=messages
        )
        return final_response.choices[0].message.content
    else:
        # Direct response without tools
        return message.content
```

```python
# ❌ WRONG - Don't use LangChain AgentExecutor
from langchain.agents import create_tool_calling_agent, AgentExecutor

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
result = agent_executor.invoke({"input": user_input})  # Causes errors
```

**Why manual tool calling?**
- ✅ Full control over tool execution
- ✅ Better error handling
- ✅ Works reliably with Databricks Foundation Models
- ✅ Simpler debugging
- ✅ No AgentExecutor complexity

---

### 4. **UC Functions Permissions** ⚠️ CRITICAL

**Always grant EXECUTE permissions after creating UC Functions:**

**Add to `notebooks/04_create_uc_functions.py` at the END:**

```python
# COMMAND ----------

# MAGIC %md
# MAGIC ## Grant EXECUTE Permissions to All Users

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
```

**Why this is critical:**
- ❌ Without permissions: "User does not have permission to run function"
- ✅ With permissions: MCP agent can call all UC Functions
- ✅ Applies to ALL users (including app service principals)
- ✅ Automated in notebook (no manual steps needed)

**Verification after job runs:**

```python
# Check permissions granted
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
result = w.statement_execution.execute_statement(
    warehouse_id="148ccb90800933a1",
    statement=f"SHOW GRANTS ON FUNCTION {CATALOG}.{SCHEMA}.lookup_member"
)

for row in result.result.data_array:
    print(f"✅ {row[0]}: {row[1]}")  # principal: permission_level
```

---

### 5. **MCP Client Implementation Pattern**

**All three MCP clients follow the same pattern:**

#### **Genie MCP Client:**

```python
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient

class GenieMCPClient:
    def __init__(self, workspace_hostname: str, genie_space_id: str, workspace_client: WorkspaceClient):
        self.workspace_client = workspace_client
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/genie/{genie_space_id}"
        
        # Initialize MCP client
        self.mcp_client = DatabricksMCPClient(
            server_url=self.mcp_url,
            workspace_client=self.workspace_client
        )
    
    def query_genie(self, query: str) -> Dict[str, Any]:
        """Query via MCP protocol"""
        result = self.mcp_client.call_tool("genie_query", {"query": query})
        return {"success": True, "result": result.content}
```

#### **UC Functions MCP Client:**

```python
class UCFunctionsMCPClient:
    def __init__(self, workspace_hostname: str, catalog: str, schema: str, workspace_client: WorkspaceClient):
        self.workspace_client = workspace_client
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/functions/{catalog}/{schema}"
        
        # Initialize MCP client
        self.mcp_client = DatabricksMCPClient(
            server_url=self.mcp_url,
            workspace_client=self.workspace_client
        )
    
    def call_uc_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Call UC Function via MCP"""
        result = self.mcp_client.call_tool(function_name, kwargs)
        return {"success": True, "result": result.content}
```

#### **Knowledge Assistant Client:**

```python
class KnowledgeAssistantMCPClient:
    def __init__(self, knowledge_assistant_endpoint_id: str, workspace_client: WorkspaceClient):
        self.workspace_client = workspace_client
        self.knowledge_client = self._setup_knowledge_client()
    
    def _setup_knowledge_client(self):
        """Setup using token generation"""
        import time
        from openai import OpenAI
        
        # Generate token
        token = self.workspace_client.tokens.create(
            comment=f"knowledge-assistant-{time.time_ns()}", 
            lifetime_seconds=3600
        )
        
        # Use OpenAI client with token
        return OpenAI(
            api_key=token.token_value,
            base_url=f"{self.workspace_client.config.host}/serving-endpoints"
        )
    
    def query_knowledge(self, query: str) -> Dict[str, Any]:
        """Query Knowledge Assistant"""
        response = self.knowledge_client.responses.create(
            model=self.knowledge_assistant_endpoint_id,
            input=[{"role": "user", "content": query}]
        )
        return {"success": True, "result": response.output[0].content[0].text}
```

---

### 6. **Agent Architecture**

```python
class HEDISQualityAgent:
    """MCP Agent using proven working pattern"""
    
    def __init__(self, genie_space_id, catalog, schema, knowledge_assistant_endpoint_id, ai_model_name):
        self.workspace_client = WorkspaceClient()
        
        # 1. Setup MCP clients
        workspace_host = self.workspace_client.config.host.replace("https://", "")
        self.genie_client = GenieMCPClient(workspace_host, genie_space_id, self.workspace_client)
        self.uc_functions_client = UCFunctionsMCPClient(workspace_host, catalog, schema, self.workspace_client)
        self.knowledge_assistant_client = KnowledgeAssistantMCPClient(knowledge_assistant_endpoint_id, self.workspace_client)
        
        # 2. Create LangChain tools from MCP clients
        self.tools = []
        self.tools.append(create_genie_tool_for_langchain(self.genie_client))
        self.tools.extend(create_uc_functions_tools_for_langchain(self.uc_functions_client))
        self.tools.append(create_knowledge_assistant_tool_for_langchain(self.knowledge_assistant_client))
        
        # 3. Setup LLM using Databricks native client
        self.llm_client = self.workspace_client.serving_endpoints.get_open_ai_client()
        
        # 4. Create tool mapping
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def chat(self, user_input: str, chat_history: List[Dict[str, str]]) -> str:
        """Chat using manual tool calling pattern (see section 3 above)"""
        # Implementation as shown in section 3
        pass
```

---

### 7. **Complete Checklist for MCP Integration**

**Before deploying MCP:**

- [ ] ✅ Use `databricks-meta-llama-3-1-8b-instruct` model (not 70B)
- [ ] ✅ Update both `config.py` AND `app.yaml` with model name
- [ ] ✅ Use `workspace_client.serving_endpoints.get_open_ai_client()`
- [ ] ✅ Implement manual tool calling pattern (not AgentExecutor)
- [ ] ✅ **Use Field() in all BaseTool definitions** (Pydantic v2 compatibility)
- [ ] ✅ Add permission granting to UC Functions notebook
- [ ] ✅ Run UC Functions job to create functions AND grant permissions
- [ ] ✅ Verify UC functions exist: `SELECT * FROM information_schema.routines`
- [ ] ✅ Grant Knowledge Assistant permissions (if using KA)
- [ ] ✅ Test each MCP client individually before integration

**After deploying MCP:**

- [ ] ✅ Verify "🤖 MCP Search" tab appears
- [ ] ✅ Check AI Agent Status sidebar shows all components as Ready
- [ ] ✅ Test member query: "Show me member M000001's quality metrics"
- [ ] ✅ Test gap query: "Which members have open BCS gaps?"
- [ ] ✅ Test knowledge query: "What are the HEDIS compliance requirements?"

---

### 8. **Common Errors and Prevention**

| Error | Cause | Prevention |
|-------|-------|------------|
| ENDPOINT_NOT_FOUND | Using 70B model | Always use 8B model |
| "Agent not initialized" | Wrong LLM client setup | Use `get_open_ai_client()` |
| "TypeError: chat() missing arguments" | Using AgentExecutor | Use manual tool calling |
| "Permission denied to run function" | Missing EXECUTE grants | Add permission granting to UC Functions notebook |
| "0 functions found" | Permissions not granted | Verify grants after UC Functions job completes |
| "Field 'name' defined on a base class was overridden" | Not using Field() in BaseTool | Use `name: str = Field(default="...")` pattern |

---

### 9. **File Checklist**

When implementing MCP, ensure these files follow the pattern:

**`dashboard/config.py`:**
```python
AI_MODEL_NAME = "databricks-meta-llama-3-1-8b-instruct"  # ✅ 8B model
```

**`dashboard/app.yaml`:**
```yaml
env:
  - name: 'AI_MODEL_NAME'
    value: 'databricks-meta-llama-3-1-8b-instruct'  # ✅ 8B model
```

**`dashboard/hedis_agent.py`:**
```python
# ✅ Use Databricks native OpenAI client
self.llm_client = self.workspace_client.serving_endpoints.get_open_ai_client()

# ✅ Manual tool calling in chat() method
response = self.llm_client.chat.completions.create(...)
```

**`notebooks/04_create_uc_functions.py`:**
```python
# ✅ Add permission granting at the end
for func_name in function_names:
    spark.sql(f"GRANT EXECUTE ON FUNCTION {CATALOG}.{SCHEMA}.{func_name} TO `account users`")
```

---

### 10. **COMPLETE MCP Code Templates** 📋

**Use these EXACT templates for bulletproof MCP implementation. Copy-paste and adapt for your project.**

#### dashboard/config.py (MCP Configuration)

```python
"""
Configuration for MCP (Model Context Protocol) Integration

MCP provides AI-powered natural language search across:
- Structured data (via Genie + UC Functions)
- Unstructured documents (via Knowledge Assistant)
"""

# Databricks workspace configuration
DATABRICKS_HOST = "https://adb-984752964297111.11.azuredatabricks.net"
DATABRICKS_CLUSTER_ID = "0304-162117-qgsi1x04"

# Unity Catalog configuration
CATALOG = "your_catalog"  # Update for your project
SCHEMA = "your_gold"      # Update for your project

# MCP Service IDs (set after creating Genie Space and Knowledge Assistant)
GENIE_SPACE_ID = "your-genie-space-id"  # From Genie Space creation
KNOWLEDGE_ASSISTANT_ENDPOINT_ID = "your-ka-endpoint-id"  # Optional

# AI Model configuration - Foundation Model Endpoint
# ⚠️ CRITICAL: Always use 8B model
AI_MODEL_NAME = "databricks-meta-llama-3-1-8b-instruct"

# SQL Warehouse for Genie queries
SQL_WAREHOUSE_ID = "148ccb90800933a1"
```

#### dashboard/mcp_genie_client.py (Genie MCP Client)

```python
"""
Genie MCP Server Integration

This module provides integration with Databricks Genie via Model Context Protocol (MCP).
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class GenieQueryInput(BaseModel):
    query: str = Field(description="Natural language query for Genie space")

class GenieMCPClient:
    """Client for interacting with Genie managed MCP server"""
    
    def __init__(self, workspace_hostname: str, genie_space_id: str, workspace_client: WorkspaceClient):
        self.workspace_hostname = workspace_hostname
        self.genie_space_id = genie_space_id
        self.workspace_client = workspace_client
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/genie/{genie_space_id}"
        self.mcp_client = None
        self._initialize_mcp_client()
    
    def _initialize_mcp_client(self):
        """Initialize the MCP client connection"""
        try:
            self.mcp_client = DatabricksMCPClient(
                server_url=self.mcp_url,
                workspace_client=self.workspace_client
            )
        except Exception as e:
            st.error(f"Failed to connect to Genie MCP: {e}")
    
    def query_genie(self, query: str) -> Dict[str, Any]:
        """Query Genie via MCP protocol"""
        if not self.mcp_client:
            return {"success": False, "error": "MCP client not initialized"}
        
        try:
            result = self.mcp_client.call_tool("genie_query", {"query": query})
            return {
                "success": True,
                "query": query,
                "result": result.content if hasattr(result, 'content') else str(result)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status of Genie MCP connection"""
        if self.mcp_client:
            return {
                "status": "healthy",
                "mcp_url": self.mcp_url,
                "tools": ["genie_query"]
            }
        return {"status": "unhealthy", "error": "MCP client not initialized"}

def create_genie_tool_for_langchain(genie_client: GenieMCPClient):
    """Create a LangChain tool wrapper for Genie MCP client"""
    
    class GenieMCPTool(BaseTool):
        name: str = Field(default="genie_mcp_query")  # ⚠️ CRITICAL: Use Field()
        description: str = Field(default="""Query structured data using natural language through Genie MCP server. 
        Use this tool to analyze data, get insights, and answer questions about structured data tables.""")
        args_schema: type[BaseModel] = GenieQueryInput
        
        def _run(self, query: str) -> str:
            result = genie_client.query_genie(query)
            if result["success"]:
                return f"Genie Analysis:\n{result['result']}"
            else:
                return f"Error querying Genie: {result['error']}"
    
    return GenieMCPTool()
```

#### dashboard/mcp_uc_functions_client.py (UC Functions MCP Client)

```python
"""
UC Functions MCP Server Integration

This module provides integration with Unity Catalog Functions via MCP.
"""

from typing import Dict, List, Any
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
from databricks.sdk.service.sql import StatementState
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, create_model

class UCFunctionsMCPClient:
    """Client for interacting with UC Functions managed MCP server"""
    
    def __init__(self, workspace_hostname: str, catalog: str, schema: str, workspace_client: WorkspaceClient):
        self.workspace_hostname = workspace_hostname
        self.catalog = catalog
        self.schema = schema
        self.workspace_client = workspace_client
        self.warehouse_id = "148ccb90800933a1"
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/functions/{catalog}/{schema}"
        self.mcp_client = None
        self._initialize_mcp_client()
    
    def _initialize_mcp_client(self):
        """Initialize the MCP client connection"""
        try:
            self.mcp_client = DatabricksMCPClient(
                server_url=self.mcp_url,
                workspace_client=self.workspace_client
            )
        except Exception as e:
            st.error(f"Failed to connect to UC Functions MCP: {e}")
    
    def call_uc_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Call a UC Function via MCP"""
        if not self.mcp_client:
            return {"success": False, "error": "MCP client not initialized"}
        
        try:
            result = self.mcp_client.call_tool(function_name, kwargs)
            return {
                "success": True,
                "function_name": function_name,
                "result": result.content if hasattr(result, 'content') else str(result)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_functions(self) -> list:
        """List all available UC Functions"""
        try:
            statement = self.workspace_client.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=f"""
                    SELECT routine_name, routine_definition 
                    FROM {self.catalog}.information_schema.routines 
                    WHERE routine_schema = '{self.schema}'
                    AND routine_type = 'FUNCTION'
                """,
                wait_timeout="30s"
            )
            
            if statement.status.state == StatementState.SUCCEEDED and statement.result:
                functions = []
                for row in statement.result.data_array or []:
                    if row and len(row) > 0:
                        functions.append({
                            'name': row[0],
                            'full_name': f"{self.catalog}.{self.schema}.{row[0]}"
                        })
                return functions
            return []
        except Exception as e:
            st.error(f"Error listing UC functions: {e}")
            return []
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status"""
        functions = self.list_functions()
        if self.mcp_client and functions:
            return {
                "status": "healthy",
                "mcp_url": self.mcp_url,
                "tools_count": len(functions),
                "tools": [f['name'] for f in functions]
            }
        return {"status": "unhealthy", "tools_count": 0}

def create_uc_functions_tools_for_langchain(uc_functions_client: UCFunctionsMCPClient):
    """Create LangChain tools for each UC Function"""
    
    functions = uc_functions_client.list_functions()
    tools = []
    
    for func in functions:
        func_name = func['name']
        func_description = f"Call UC Function: {func_name}"
        
        # Create dynamic input model (simplified - no parameters)
        DynamicInputModel = create_model(f"{func_name.replace('-', '_').capitalize()}Input")
        
        # ⚠️ CRITICAL: Use Field() for Pydantic v2 compatibility
        class UCFuncTool(BaseTool):
            name: str = Field(default=func_name)
            description: str = Field(default=func_description)
            args_schema: type[BaseModel] = DynamicInputModel
            
            def _run(self, **kwargs) -> str:
                result = uc_functions_client.call_uc_function(func_name, **kwargs)
                if result["success"]:
                    return f"UC Function '{func_name}' Result:\n{result['result']}"
                else:
                    return f"Error: {result['error']}"
        
        tools.append(UCFuncTool())
    
    return tools
```

#### dashboard/mcp_knowledge_assistant_client.py (Knowledge Assistant Client)

```python
"""
Knowledge Assistant MCP Integration

This module provides integration with Databricks Knowledge Assistant.
"""

from typing import Dict, Any
from databricks.sdk import WorkspaceClient
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class KnowledgeAssistantQueryInput(BaseModel):
    query: str = Field(description="Question to search in knowledge base")

class KnowledgeAssistantMCPClient:
    """Client for Knowledge Assistant endpoint"""
    
    def __init__(self, endpoint_id: str, workspace_client: WorkspaceClient):
        self.endpoint_id = endpoint_id
        self.workspace_client = workspace_client
        self.knowledge_client = self._setup_knowledge_client()
    
    def _setup_knowledge_client(self):
        """Setup Knowledge Assistant client using token"""
        try:
            import time
            from openai import OpenAI
            
            token = self.workspace_client.tokens.create(
                comment=f"knowledge-assistant-{time.time_ns()}",
                lifetime_seconds=3600
            )
            
            return OpenAI(
                api_key=token.token_value,
                base_url=f"{self.workspace_client.config.host}/serving-endpoints"
            )
        except Exception as e:
            st.error(f"Failed to setup Knowledge Assistant: {e}")
            return None
    
    def query_knowledge(self, query: str) -> Dict[str, Any]:
        """Query Knowledge Assistant"""
        if not self.knowledge_client:
            return {"success": False, "error": "Knowledge client not initialized"}
        
        try:
            response = self.knowledge_client.responses.create(
                model=self.endpoint_id,
                input=[{"role": "user", "content": query}]
            )
            return {
                "success": True,
                "result": response.output[0].content[0].text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_endpoint_status(self) -> dict:
        """Get endpoint status"""
        try:
            endpoint = self.workspace_client.serving_endpoints.get(name=self.endpoint_id)
            state = endpoint.state.ready.value if endpoint.state and endpoint.state.ready else 'UNKNOWN'
            return {"name": endpoint.name, "state": state, "endpoint_id": self.endpoint_id}
        except Exception as e:
            return {"name": self.endpoint_id, "state": "ERROR", "error": str(e)}

def create_knowledge_assistant_tool_for_langchain(knowledge_client: KnowledgeAssistantMCPClient):
    """Create LangChain tool for Knowledge Assistant"""
    
    class KnowledgeAssistantMCPTool(BaseTool):
        name: str = Field(default="knowledge_assistant_query")  # ⚠️ CRITICAL: Use Field()
        description: str = Field(default="""Search and retrieve information from the knowledge base.
        Use this tool to answer questions about policies, guidelines, and documentation.""")
        args_schema: type[BaseModel] = KnowledgeAssistantQueryInput
        
        def _run(self, query: str) -> str:
            result = knowledge_client.query_knowledge(query)
            if result["success"]:
                return f"Knowledge Base Answer:\n{result['result']}"
            else:
                return f"Error: {result['error']}"
    
    return KnowledgeAssistantMCPTool()
```

---

### 10.5. **MCP Implementation Checklist** ✅

**Follow this checklist EXACTLY for every MCP project:**

- [ ] **Step 1**: Create `dashboard/config.py` with catalog, schema, Genie ID, AI model (copy template above)
- [ ] **Step 2**: Create `dashboard/mcp_genie_client.py` (copy complete template above)
- [ ] **Step 3**: Create `dashboard/mcp_uc_functions_client.py` (copy complete template above)
- [ ] **Step 4**: Create `dashboard/mcp_knowledge_assistant_client.py` (copy complete template above - OPTIONAL)
- [ ] **Step 5**: Verify ALL files are in `dashboard/` folder (NOT separate `mcp_clients/` folder)
- [ ] **Step 6**: Verify ALL BaseTool classes use `Field(default="...")` pattern
- [ ] **Step 7**: Update `config.py` with your project's catalog, schema, and Genie Space ID
- [ ] **Step 8**: Add MCP dependencies to `dashboard/requirements.txt`:
  ```
  databricks-mcp>=0.1.0
  langchain>=0.1.0
  langchain-community>=0.0.1
  openai>=1.0.0
  ```
- [ ] **Step 9**: Create agent class that uses these clients (see agent pattern in section 3)
- [ ] **Step 10**: Add MCP Search tab to your dashboard
- [ ] **Step 11**: Deploy and test

**Common Mistakes to Avoid:**
- ❌ Creating separate `mcp_clients/` folder → Keep in `dashboard/`
- ❌ Using `name: str = "value"` → Use `name: str = Field(default="value")`
- ❌ Using 70B model → Use 8B model
- ❌ Forgetting UC function permissions → Grant EXECUTE to `account users`
- ❌ Not testing locally first → Always test locally before deploying

---

### 11. **Testing Your MCP Implementation**

**Quick validation script:**

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# 1. Check UC Functions exist
print("1️⃣ Checking UC Functions...")
result = w.statement_execution.execute_statement(
    warehouse_id="148ccb90800933a1",
    statement="SELECT routine_name FROM humana_quality.information_schema.routines WHERE routine_schema = 'hedis_gold'"
)
print(f"   ✅ Found {len(result.result.data_array)} functions")

# 2. Check UC Functions permissions
print("\n2️⃣ Checking UC Functions permissions...")
result = w.statement_execution.execute_statement(
    warehouse_id="148ccb90800933a1",
    statement="SHOW GRANTS ON FUNCTION humana_quality.hedis_gold.lookup_member"
)
print(f"   ✅ Permissions: {[row[0] for row in result.result.data_array]}")

# 3. Check Genie Space exists
print("\n3️⃣ Checking Genie Space...")
spaces = w.genie.list_spaces()
print(f"   ✅ Found {len(list(spaces))} Genie spaces")

# 4. Check Knowledge Assistant endpoint
print("\n4️⃣ Checking Knowledge Assistant...")
try:
    endpoint = w.serving_endpoints.get("ka-0bbaf97e-endpoint")
    print(f"   ✅ Endpoint: {endpoint.name} - State: {endpoint.state.ready.value}")
except:
    print("   ⚠️ Knowledge Assistant not configured (optional)")

print("\n✅ All MCP components validated!")
```

---

### 11. **Reference Implementation Location** 📁

**The proven working code is in this public GitHub repository:**

🔗 **https://github.com/bigdatavik/HEDIS-Quality-Dashboard.git**

**This repository contains the complete working HEDIS Quality Dashboard with MCP integration:**

#### **Core Application Files:**
- ✅ `dashboard/hedis_quality_dashboard.py` - Streamlit app with MCP Search tab
- ✅ `dashboard/hedis_agent.py` - Complete MCP agent with manual tool calling
- ✅ `dashboard/mcp_genie_client.py` - Genie MCP client (Pydantic v2 compatible)
- ✅ `dashboard/mcp_uc_functions_client.py` - UC Functions MCP client
- ✅ `dashboard/mcp_knowledge_assistant_client.py` - Knowledge Assistant client
- ✅ `dashboard/config.py` - Configuration with 8B model
- ✅ `dashboard/app.yaml` - Databricks Apps configuration with DATABRICKS_HOST

#### **Data Pipeline (Medallion Architecture):**
- ✅ `notebooks/01_ingest_to_bronze.py` - Raw data ingestion
- ✅ `notebooks/02_bronze_to_silver.py` - Data cleaning and validation
- ✅ `notebooks/03_silver_to_gold.py` - Business aggregations
- ✅ `notebooks/04_create_uc_functions.py` - UC Functions with EXECUTE grants
- ✅ `notebooks/05_upload_knowledge_docs.py` - Knowledge document upload

#### **Knowledge Documents (Ready to Use):**
- ✅ `data/agent_knowledge_source_guide.txt` (4,800 words)
- ✅ `data/knowledge_source_descriptions.txt` (3,200 words)
- ✅ `data/hedis_policies.txt` (6,500 words)
- ✅ `data/faq_documentation.txt` (5,000 words)
- ✅ `data/KNOWLEDGE_ASSISTANT_UI_FIELDS.md` - Copy-paste setup guide
- ✅ `data/GENIE_INSTRUCTIONS.md` - Copy-paste Genie instructions
- ✅ `data/QUICK_SETUP_GUIDE.md` - 15-minute setup

#### **Supporting Files:**
- ✅ `src/data_generators/hedis_generator.py` - Synthetic data generation
- ✅ `src/utils/` - Table helpers and DataFrame validation
- ✅ `databricks.yml` - DAB configuration
- ✅ `MY_ENVIRONMENT.md` - This complete guide (4,100+ lines)

**This is the TEMPLATE for all future healthcare payor projects!**

---

### 🎯 How to Use This Reference:

**When creating new projects, I will:**

1. **Start with MY_ENVIRONMENT.md** (this file)
   - Get patterns, templates, and best practices
   - Understand architecture and standards

2. **Reference working code in GitHub repo**
   - See exact implementation: https://github.com/bigdatavik/HEDIS-Quality-Dashboard.git
   - Copy proven patterns (authentication, MCP, deployment)
   - Verify technical details

3. **Adapt for new domain**
   - Keep technical patterns identical (authentication, MCP, folder structure)
   - Adapt business logic (UC Functions, knowledge documents, data model)
   - Use templates from MY_ENVIRONMENT.md as starting point

4. **Result: 90-98% first-time success rate** ✅

---

### 📋 Quick Access Links:

**Main Branch (Stable):**
- Browse code: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/tree/main
- Dashboard folder: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/tree/main/dashboard
- Notebooks: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/tree/main/notebooks
- Knowledge docs: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/tree/main/data

**Key Files (Direct Links):**
- Complete app: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/dashboard/hedis_quality_dashboard.py
- MCP Agent: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/dashboard/hedis_agent.py
- Genie Client: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/dashboard/mcp_genie_client.py
- UC Functions Client: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/dashboard/mcp_uc_functions_client.py
- Knowledge Assistant: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/dashboard/mcp_knowledge_assistant_client.py
- Config: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/dashboard/config.py
- App YAML: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/dashboard/app.yaml
- UC Functions notebook: https://github.com/bigdatavik/HEDIS-Quality-Dashboard/blob/main/notebooks/04_create_uc_functions.py

**Clone for new project:**
```bash
git clone https://github.com/bigdatavik/HEDIS-Quality-Dashboard.git
cd HEDIS-Quality-Dashboard
# Review code, adapt for your domain, deploy!
```

---

### 💡 Why GitHub Repo + MY_ENVIRONMENT.md = Perfect Combo:

| Component | What It Provides | When to Use |
|-----------|------------------|-------------|
| **MY_ENVIRONMENT.md** | Patterns, templates, checklists, explanations | First reference - understand WHY and HOW |
| **GitHub Repo** | Working code, proven patterns, complete examples | Second reference - see EXACT implementation |
| **Together** | Best practices + working code = 98% success rate | Always use both for new projects |

**Benefits:**
- ✅ **MY_ENVIRONMENT.md**: Learn patterns, avoid mistakes, understand decisions
- ✅ **GitHub code**: Copy exact implementation, verify syntax, see it working
- ✅ **No guessing**: Every pattern documented AND demonstrated
- ✅ **Version controlled**: Both evolve together, always in sync
- ✅ **Permanent**: Won't get deleted, always accessible

---

### 🚀 Example: Building New HCC Risk Adjustment Project:

**Step 1:** Read MY_ENVIRONMENT.md
- Lines 1782-1826: HCC knowledge document templates
- Lines 2342-2359: HCC Genie instructions
- Lines 2404-2427: HCC SQL examples

**Step 2:** Look at GitHub repo
- Copy `dashboard/` folder structure exactly
- Copy `dashboard/mcp_*.py` files (already Pydantic v2 compatible)
- Copy `dashboard/app.yaml` (has DATABRICKS_HOST)
- Copy authentication pattern from `hedis_quality_dashboard.py`

**Step 3:** Adapt for HCC domain
- Create HCC-specific UC Functions (using template from MY_ENVIRONMENT.md)
- Create HCC knowledge documents (using templates from MY_ENVIRONMENT.md)
- Update Genie instructions (using HCC template from MY_ENVIRONMENT.md)
- Generate HCC synthetic data (adapt `src/data_generators/hedis_generator.py`)

**Step 4:** Deploy
- All technical patterns identical (authentication, MCP, deployment)
- Business logic adapted for HCC domain
- Expected success rate: 90%+ first time

---

### 🎓 Best Practice: Always Use Both Resources

**When I build new projects, I will:**
1. ✅ Read MY_ENVIRONMENT.md for patterns and templates
2. ✅ Reference GitHub repo for exact working code
3. ✅ Copy technical patterns 100% (no changes)
4. ✅ Adapt business logic using templates
5. ✅ Result: Reliable, proven, working solution

**You get:**
- **Documentation** (why and how) in MY_ENVIRONMENT.md
- **Implementation** (exact code) in GitHub repo
- **Templates** (adapt for new domains) in both
- **Confidence** (proven patterns) from both sources working together

---

### 12. **Clean MCP Search UI Implementation** ⭐ CRITICAL

**ALWAYS implement MCP Search tab with a clean, uncluttered interface:**

#### ❌ Wrong Approach - Cluttered UI:
```python
# Don't show all status messages during initialization
st.success("✅ Connected to Genie MCP server")
st.success("✅ UC Functions MCP tools loaded (6 tools)")
st.success("✅ Knowledge Assistant client initialized")
st.success("✅ Genie MCP tool loaded")
st.success("✅ Total tools loaded: 8")
st.success("✅ LLM client initialized")

# Don't put detailed status in sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Agent Status")
    # ... 8 separate status items ...
```

**Result:** Main screen cluttered with 8+ green status boxes before user can search.

#### ✅ Correct Approach - Clean UI:

**1. Remove all status messages from initialization:**
```python
# In mcp_genie_client.py, mcp_uc_functions_client.py, mcp_knowledge_assistant_client.py
def _initialize_mcp_client(self):
    try:
        self.mcp_client = DatabricksMCPClient(...)
        # ✅ No st.success() calls here!
        # Silently initialize
    except Exception as e:
        st.error(f"❌ Failed to connect: {e}")  # Only show errors

# In hedis_agent.py
def _setup_tools(self):
    # ✅ No st.success() or st.warning() calls
    # Just set up tools silently
    pass
```

**2. Show single status line at top:**
```python
# Get system status
system_status = agent.get_system_status()

# Quick status indicator
genie_status = system_status.get('genie', {})
uc_status = system_status.get('uc_functions', {})

all_healthy = (
    system_status.get('llm_ready') and
    genie_status.get('status') == 'healthy' and
    uc_status.get('status') == 'healthy'
)

if all_healthy:
    st.success(f"✅ **AI Agent Ready** | {system_status.get('tools_count', 0)} tools available")
else:
    st.warning("⚠️ **AI Agent Partially Ready** | Some services may be unavailable")
```

**3. Put detailed status in collapsible expander:**
```python
# Detailed connectivity in expandable section (collapsed by default)
with st.expander("🔧 System Status & Connectivity Details", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Core Services")
        
        # AI Model Status
        st.markdown("**🧠 AI Model**")
        if system_status.get('llm_ready'):
            st.success("✅ Ready")
        
        # Genie MCP Status
        st.markdown("**🔮 Genie MCP**")
        if genie_status.get('status') == 'healthy':
            st.success("✅ Connected")
            st.caption(f"Server: {genie_status.get('mcp_url', 'N/A')}")
        
        # UC Functions Status
        st.markdown("**⚙️ UC Functions MCP**")
        if uc_status.get('status') == 'healthy':
            st.success(f"✅ Connected ({uc_status.get('tools_count', 0)} functions)")
            st.caption(f"Server: {uc_status.get('mcp_url', 'N/A')}")
            # Show function list directly (no nested expanders!)
            if uc_status.get('tools'):
                st.markdown("**Available Functions:**")
                for tool in uc_status.get('tools', [])[:6]:
                    st.markdown(f"- `{tool}`")
    
    with col2:
        st.markdown("#### Optional Services")
        
        # Knowledge Assistant Status
        st.markdown("**📚 Knowledge Assistant**")
        ka_status = system_status.get('knowledge_assistant', {})
        if ka_status.get('status') == 'healthy':
            st.success("✅ Ready")
            st.caption(f"Endpoint: {ka_status.get('endpoint_id', 'N/A')}")
        elif ka_status.get('status') == 'not_configured':
            st.info("ℹ️ Not configured (optional)")
        
        st.markdown("---")
        st.markdown(f"**📊 Total Tools Available:** {system_status.get('tools_count', 0)}")
```

**4. Main screen focuses on search:**
```python
# Query Interface immediately after status
query_text = st.text_input(
    "Ask a question:",
    placeholder="e.g., Show me member M000001's gaps, or Which members have open BCS gaps?",
    key="mcp_query"
)

st.markdown("*The AI agent will automatically choose the best tool(s) to answer your question.*")

# Example queries
with st.expander("💡 Example Queries"):
    st.markdown("""
    **Member Queries:**
    - Show me member M000001's quality metrics
    
    **Gap Queries:**
    - Which members have open BCS gaps?
    
    **Knowledge Queries:**
    - What are the HEDIS compliance requirements?
    """)
```

#### 🎯 Result - Clean UI:

**What user sees (collapsed by default):**
```
✅ AI Agent Ready | 8 tools available

[🔧 System Status & Connectivity Details] ▶

Ask a question:
[________________________________]

💡 Example Queries ▶
```

**What user sees when they click dropdown:**
```
✅ AI Agent Ready | 8 tools available

🔧 System Status & Connectivity Details ▼
┌─────────────────────────────────────────────┐
│ Core Services          │ Optional Services  │
│ 🧠 AI Model            │ 📚 Knowledge       │
│ ✅ Ready               │ ✅ Ready           │
│                        │ Endpoint: ka-...   │
│ 🔮 Genie MCP          │                    │
│ ✅ Connected          │ 📊 Total: 8 tools  │
│ Server: https://...   │                    │
│                        │                    │
│ ⚙️ UC Functions MCP   │                    │
│ ✅ Connected (6)      │                    │
│ Available Functions:   │                    │
│ - lookup_member       │                    │
│ - lookup_member_gaps  │                    │
└─────────────────────────────────────────────┘

Ask a question:
[________________________________]
```

#### 🚨 Critical Implementation Rules:

1. **✅ Silent Initialization**: No `st.success()` calls in MCP client `__init__` or setup methods
2. **✅ Single Status Line**: One line showing overall readiness at top of page
3. **✅ Collapsed Details**: All detailed connectivity in `st.expander(..., expanded=False)`
4. **✅ No Nested Expanders**: Show function lists directly, not in nested expanders
5. **✅ Search First**: Query input immediately visible, not buried below status
6. **✅ Two Columns**: Core Services (required) vs Optional Services (KA)
7. **✅ Show URLs**: Include MCP server URLs in detailed view for troubleshooting
8. **✅ Tool Counts**: Show number of available tools in status

#### 📋 Checklist for Clean MCP UI:

- [ ] Removed all `st.success()`, `st.warning()` from MCP client initialization
- [ ] Removed all status messages from `hedis_agent.py` setup methods
- [ ] Single status line showing "✅ AI Agent Ready | X tools available"
- [ ] Detailed status in `st.expander("🔧 System Status...", expanded=False)`
- [ ] Two-column layout: Core Services | Optional Services
- [ ] Function lists shown directly (no nested expanders)
- [ ] MCP server URLs shown with `st.caption()` for troubleshooting
- [ ] Query input immediately visible on main screen
- [ ] Example queries in separate expander
- [ ] Tested: Syntax validation with `python3 -m py_compile`

**Benefits:**
- ✅ **Professional**: Clean, focused UI
- ✅ **Fast**: User can start searching immediately
- ✅ **Flexible**: Details available when needed for troubleshooting
- ✅ **Scalable**: Works with any number of tools/services
- ✅ **User-friendly**: Search-first design

---

### 13. **Reference Implementation Location** 📁 (Duplicate - see 11 above)

---

## 🔧 MCP Troubleshooting Guide

**Common issues when integrating MCP and how to fix them:**

### Issue 1: UC Functions Shows "0 functions" or "No functions found"

**Problem:** The `SHOW USER FUNCTIONS IN schema` command fails in Databricks, even though functions exist.

**Symptom:** Dashboard shows "⚠️ No functions found (check catalog/schema)" but functions are actually present.

**Root Cause:** `SHOW USER FUNCTIONS` query has reliability issues in some Databricks environments.

**Solution:** Query `information_schema.routines` instead.

**Fix in `mcp_uc_functions_client.py`:**

```python
# ❌ WRONG - Unreliable query
def list_functions(self) -> list:
    statement = self.client.statement_execution.execute_statement(
        warehouse_id=self.warehouse_id,
        statement=f"SHOW USER FUNCTIONS IN {self.catalog}.{self.schema}",
        wait_timeout="30s"
    )
```

```python
# ✅ CORRECT - Reliable query using information_schema
def list_functions(self) -> list:
    """List all available UC Functions in the schema"""
    try:
        # Query information_schema for functions (more reliable than SHOW FUNCTIONS)
        statement = self.client.statement_execution.execute_statement(
            warehouse_id=self.warehouse_id,
            statement=f"""
                SELECT routine_name, routine_definition 
                FROM {self.catalog}.information_schema.routines 
                WHERE routine_schema = '{self.schema}'
                AND routine_type = 'FUNCTION'
            """,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED and statement.result:
            functions = []
            for row in statement.result.data_array or []:
                if row and len(row) > 0:
                    functions.append({
                        'name': row[0],  # routine_name
                        'full_name': f"{self.catalog}.{self.schema}.{row[0]}"
                    })
            return functions
        
        return []
        
    except Exception as e:
        print(f"Error listing UC functions: {e}")
        return []
```

**Verification:**
```python
# Check functions exist using information_schema
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
result = w.statement_execution.execute_statement(
    warehouse_id="148ccb90800933a1",
    statement="SELECT routine_name FROM your_catalog.information_schema.routines WHERE routine_schema = 'your_schema'",
    wait_timeout="30s"
)
print(f"Found {len(result.result.data_array)} functions")
```

---

### Issue 2: Knowledge Assistant Shows "User does not have permission 'View'"

**Problem:** Knowledge Assistant endpoint exists but users/app don't have permissions to query it.

**Symptom:** Dashboard shows "❌ User does not have permission 'View' on Endpoint k"

**Root Cause:** Knowledge Assistant endpoints require explicit `CAN_QUERY` permission grants.

**Solution:** Grant permissions using Databricks SDK.

**Critical: Use Endpoint ID (UUID), Not Name**

The permissions API requires the endpoint's UUID (not the endpoint name):

```python
# ❌ WRONG - Using endpoint name
endpoint_name = "ka-0bbaf97e-endpoint"
response = w.api_client.do("PATCH", f"/api/2.0/permissions/serving-endpoints/{endpoint_name}", ...)
# ERROR: 'ka-0bbaf97e-endpoint' is not a valid Inference Endpoint ID

# ✅ CORRECT - Get and use endpoint UUID
endpoint = w.serving_endpoints.get("ka-0bbaf97e-endpoint")
endpoint_id = endpoint.id  # e.g., "b0a808b8157b4bf0a765af1d9dbfe3b8"
response = w.api_client.do("PATCH", f"/api/2.0/permissions/serving-endpoints/{endpoint_id}", ...)
```

**Fix Script (run in local terminal or Databricks notebook):**

```python
"""Grant Knowledge Assistant permissions to all users"""
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()  # Uses DEFAULT profile from ~/.databrickscfg

# Configuration
KNOWLEDGE_ASSISTANT_ENDPOINT_NAME = "ka-0bbaf97e-endpoint"  # Your endpoint name

try:
    # Step 1: Get endpoint to retrieve UUID
    endpoint = w.serving_endpoints.get(KNOWLEDGE_ASSISTANT_ENDPOINT_NAME)
    endpoint_id = endpoint.id  # This is the UUID we need
    
    print(f"✅ Found endpoint: {endpoint.name}")
    print(f"   UUID: {endpoint_id}")
    
    # Step 2: Grant CAN_QUERY permission to all users using UUID
    response = w.api_client.do(
        "PATCH",
        f"/api/2.0/permissions/serving-endpoints/{endpoint_id}",  # Use UUID here!
        body={
            "access_control_list": [
                {
                    "group_name": "users",
                    "permission_level": "CAN_QUERY"
                }
            ]
        }
    )
    
    print("✅ SUCCESS! Permissions granted.")
    print(f"   Response: {response}")
    
    # Step 3: Verify permissions
    perms = w.api_client.do("GET", f"/api/2.0/permissions/serving-endpoints/{endpoint_id}")
    print("\n📋 Current permissions:")
    for acl in perms.get('access_control_list', []):
        principal = acl.get('group_name') or acl.get('user_name')
        print(f"   - {principal}: {[p['permission_level'] for p in acl['all_permissions']]}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
```

**Alternative: Grant to specific service principal (for app-specific access):**

```python
# Get app service principal
apps = w.apps.list()
for app in apps:
    if 'your-app-name' in app.name.lower():
        sp_name = app.service_principal_name
        print(f"App service principal: {sp_name}")

# Grant permission
endpoint = w.serving_endpoints.get(KNOWLEDGE_ASSISTANT_ENDPOINT_NAME)
w.api_client.do(
    "PATCH",
    f"/api/2.0/permissions/serving-endpoints/{endpoint.id}",
    body={
        "access_control_list": [
            {
                "service_principal_name": sp_name,
                "permission_level": "CAN_QUERY"
            }
        ]
    }
)
```

**When to run:** After creating Knowledge Assistant endpoint, before deploying MCP integration.

---

### Issue 3: Knowledge Assistant Shows Enum Value Instead of "Ready"

**Problem:** Status displays as "EndpointStateReady.READY" instead of "✅ Ready"

**Symptom:** Dashboard shows "⚠️ EndpointStateReady.READY" (yellow warning) instead of green checkmark.

**Root Cause:** Databricks SDK returns enum objects, not string values.

**Solution:** Convert enum to string value using `.value` attribute.

**Fix in `mcp_knowledge_assistant_client.py`:**

```python
# ❌ WRONG - Returns enum object
def get_endpoint_status(self) -> dict:
    try:
        endpoint = self.client.serving_endpoints.get(name=self.endpoint_id)
        
        return {
            'name': endpoint.name,
            'state': endpoint.state.ready,  # Returns enum: EndpointStateReady.READY
            'endpoint_id': self.endpoint_id
        }
    except Exception as e:
        return {'state': 'ERROR', 'error': str(e)}
```

```python
# ✅ CORRECT - Converts enum to string
def get_endpoint_status(self) -> dict:
    """Get endpoint status"""
    try:
        endpoint = self.client.serving_endpoints.get(name=self.endpoint_id)
        
        # Convert enum to string value
        state = endpoint.state.ready.value if endpoint.state and endpoint.state.ready else 'UNKNOWN'
        
        return {
            'name': endpoint.name,
            'state': state,  # Now returns string: 'READY'
            'endpoint_id': self.endpoint_id
        }
    except Exception as e:
        return {
            'name': self.endpoint_id,
            'state': 'ERROR',
            'error': str(e)
        }
```

**Dashboard status check (in `hedis_quality_dashboard.py`):**

```python
# Knowledge Assistant Status
st.markdown("**Knowledge Assistant**")
if clients['ka']:
    try:
        status = clients['ka'].get_endpoint_status()
        if status.get('state') == 'READY':  # Now correctly matches string 'READY'
            st.success("✅ Ready")
        elif 'error' in status:
            st.error(f"❌ {status.get('error', 'Unknown error')[:50]}")
        else:
            st.warning(f"⚠️ {status.get('state', 'Unknown')}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)[:50]}")
else:
    st.info("ℹ️ Not configured")
```

---

### Complete MCP Integration Checklist

When adding MCP to a project, follow these steps to avoid issues:

#### ✅ Step 1: Verify UC Functions (After creating them)

```python
# Run this check after UC Functions job completes
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
result = w.statement_execution.execute_statement(
    warehouse_id="148ccb90800933a1",
    statement="SELECT routine_name FROM your_catalog.information_schema.routines WHERE routine_schema = 'your_gold_schema'",
    wait_timeout="30s"
)

print(f"✅ Found {len(result.result.data_array)} UC Functions")
for row in result.result.data_array:
    print(f"   - {row[0]}")
```

Expected output: List of 6+ functions (e.g., `lookup_member`, `lookup_member_measures`, etc.)

#### ✅ Step 2: Grant Knowledge Assistant Permissions (Before MCP integration)

```python
# Run this BEFORE adding MCP integration
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
endpoint_name = "ka-XXXXX-endpoint"  # Your KA endpoint name

# Get endpoint UUID and grant permissions
endpoint = w.serving_endpoints.get(endpoint_name)
w.api_client.do(
    "PATCH",
    f"/api/2.0/permissions/serving-endpoints/{endpoint.id}",
    body={"access_control_list": [{"group_name": "users", "permission_level": "CAN_QUERY"}]}
)

print(f"✅ Granted permissions to {endpoint_name}")
```

#### ✅ Step 3: Deploy MCP Integration

```bash
# Update config with Genie and KA IDs
# Then deploy
databricks bundle deploy --profile DEFAULT
databricks bundle run your_dashboard_app --profile DEFAULT
```

#### ✅ Step 4: Verify MCP Status

Check dashboard sidebar shows:
- ✅ Genie MCP: Connected
- ✅ UC Functions: 6 functions (or your expected count)
- ✅ Knowledge Assistant: Ready

---

### Quick Diagnostic Commands

**Check if functions exist:**
```sql
-- Run in SQL Editor
SELECT routine_name 
FROM your_catalog.information_schema.routines 
WHERE routine_schema = 'your_gold_schema' 
AND routine_type = 'FUNCTION';
```

**Check Knowledge Assistant endpoint:**
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

# Get endpoint
endpoint = w.serving_endpoints.get("ka-XXXXX-endpoint")
print(f"Name: {endpoint.name}")
print(f"State: {endpoint.state.ready.value}")
print(f"UUID: {endpoint.id}")

# Check permissions
perms = w.api_client.do("GET", f"/api/2.0/permissions/serving-endpoints/{endpoint.id}")
for acl in perms['access_control_list']:
    print(f"{acl.get('group_name')}: {[p['permission_level'] for p in acl['all_permissions']]}")
```

**Check Genie Space:**
```bash
# List Genie spaces
databricks workspace list /genie/spaces --profile DEFAULT
```

---

### Common Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "No functions found (check catalog/schema)" | `SHOW USER FUNCTIONS` query fails | Use `information_schema.routines` query (see Issue 1) |
| "User does not have permission 'View'" | Missing CAN_QUERY permission | Grant permissions using endpoint UUID (see Issue 2) |
| "EndpointStateReady.READY" showing as warning | Enum not converted to string | Use `.value` on enum (see Issue 3) |
| "'endpoint_name' is not a valid Inference Endpoint ID" | Using endpoint name instead of UUID for permissions | Get endpoint UUID first with `w.serving_endpoints.get()` (see Issue 2) |
| "❌ 0 functions" | Functions might not exist | Run UC Functions job, verify with `information_schema` query |

---

### Prevention Checklist

Before deploying MCP integration:
- [ ] Verify UC Functions exist using `information_schema.routines`
- [ ] Grant Knowledge Assistant permissions using endpoint UUID
- [ ] Test each MCP client individually before integration
- [ ] Use `.value` on enum objects for status strings
- [ ] Always use endpoint UUID for permissions API calls

---

