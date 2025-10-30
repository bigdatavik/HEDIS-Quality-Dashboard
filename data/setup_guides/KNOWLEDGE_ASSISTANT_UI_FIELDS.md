# Knowledge Assistant Setup Guide

**Complete step-by-step instructions for creating a Knowledge Assistant endpoint**

Based on: [Microsoft Databricks Knowledge Assistant Documentation](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-bricks/knowledge-assistant)

---

## Prerequisites ✅

Before starting, ensure:
- ✅ Knowledge documents uploaded to volume: `/Volumes/humana_quality/hedis_gold/knowledge_docs/`
- ✅ Mosaic AI Agent Bricks Preview (Beta) enabled in workspace
- ✅ Serverless compute enabled
- ✅ Unity Catalog enabled
- ✅ Workspace region: centralus, eastus, eastus2, northcentralus, southcentralus, westus, or westus2

---

## Step 1: Navigate to Knowledge Assistant Creation

1. Open Databricks workspace
2. Go to: **Agents** (left navigation pane)
3. Click **Knowledge Assistant**
4. This opens the Knowledge Assistant configuration screen

---

## Step 2: Configure Basic Info

### 📝 Name Field

**Enter:**
```
hedis_quality_knowledge_assistant
```

**Rule:** Only letters, numbers, and dashes are allowed

---

### 📝 Description Field

**Enter:**
```
Answers questions about HEDIS quality measures, NCQA compliance requirements, gap closure procedures, and quality improvement guidelines. Provides policy interpretations, measure specifications, and operational best practices for the quality analytics team working with Medicare Advantage Star Ratings.
```

**Purpose:** This description helps users understand what the agent can do. It appears in the agent overview and helps stakeholders know when to use this knowledge assistant.

---

## Step 3: Configure Knowledge Sources

### 📝 Knowledge Source Configuration

**Type:** UC Files

**Source:**
- Click the **folder icon** in the Source field
- Navigate to: `/Volumes/humana_quality/hedis_gold/knowledge_docs`
- Select the volume path

**Name (Optional):**
```
HEDIS Quality Documentation
```

---

### 📝 "Describe the content" Field ⚠️ CRITICAL

**This field is the most important for search quality!**

Paste this entire block:

```
This knowledge base contains comprehensive documentation for HEDIS quality measures and Medicare Advantage Star Ratings:

1. Gap Closure Protocols (7.3 KB) - Complete standard operating procedures for gap closure workflows including:
   - Phase-based gap closure workflow (identification, intervention, tracking)
   - Priority matrix for member stratification (critical/high/medium/low)
   - Intervention protocols by priority level (care management, intensive outreach, standard outreach, automated)
   - Standard phone call scripts and member outreach templates
   - Medical record review processes and chart abstraction procedures
   - Gap closure incentive programs (member and provider)
   - Common barriers and solutions (transportation, cost, language, health literacy)
   - Technology tools (automated dialers, EHR integration, reporting dashboards)
   - Success metrics (process, outcome, and financial KPIs)
   - Annual timeline and continuous improvement strategies

2. HEDIS Measures Guide (4.6 KB) - Reference guide for all HEDIS quality measures including:
   - BCS (Breast Cancer Screening) - Women 50-74, mammogram within 24 months
   - CDC (Comprehensive Diabetes Care) - HbA1c testing, eye exams, nephropathy care, BP control
   - CBP (Controlling High Blood Pressure) - BP < 140/90 for adults 18-85
   - COL (Colorectal Cancer Screening) - FOBT, sigmoidoscopy, or colonoscopy
   - CIS (Childhood Immunization Status) - Complete vaccine series by age 2
   - W15 (Well-Child Visits) - Six or more visits in first 15 months
   - AWC (Adolescent Well-Care Visits) - Annual comprehensive visit ages 12-21
   - PPC (Prenatal and Postpartum Care) - First trimester prenatal and 7-84 day postpartum visits
   - Stars rating methodology and thresholds (1-5 stars)
   - Gap closure best practices and quality improvement targets

3. NCQA Quality Guidelines (5.1 KB) - National Committee for Quality Assurance compliance requirements:
   - Data collection methods (administrative claims, medical record review, EHR integration)
   - Continuous enrollment requirements and allowable gaps
   - Measurement year vs reporting year definitions
   - HEDIS audit requirements and pass/fail criteria (≥95% reportability)
   - Quality improvement strategies (risk stratification, care coordination, provider partnerships)
   - Member engagement approaches (outreach campaigns, barrier removal, health education)
   - Stars rating impact on revenue (5-star: +5% bonus, 4-star: +3% bonus)
   - High-impact measures (CDC and CBP are triple-weighted, BCS and COL are double-weighted)
   - Compliance best practices (early gap identification, continuous monitoring, cross-functional collaboration)
   - Common pitfalls to avoid and technology enablement strategies

4. Quality Team Communications (8.8 KB) - Comprehensive FAQ document covering:
   - General HEDIS questions (what is HEDIS, why it matters, compliance vs Stars ratings)
   - Gap closure questions (what is a gap, update frequency, gap closure targets, retroactive closures)
   - Dashboard usage questions (how to use each tab, quality score calculation, data refresh timing, export capabilities)
   - Member outreach questions (prioritization criteria, handling member refusals, addressing barriers)
   - Provider engagement questions (gap list distribution, quality incentives, claim processing issues)
   - Reporting questions (NCQA submission deadlines, audit processes, national benchmarking)
   - System/technical questions (troubleshooting, custom reports, access controls)
   - Contact information for quality department, technical support, and provider services
   - Quick reference table of measure codes and eligible populations

Use this knowledge base to answer questions about: HEDIS measure specifications, NCQA compliance requirements, gap closure standard operating procedures, Medicare Stars rating methodology, member outreach protocols, provider engagement strategies, quality improvement tactics, revenue impact calculations, documentation standards, audit preparedness, and operational troubleshooting. The agent should cite specific protocols, procedures, and guidelines from these documents when responding to queries.
```

**Why this is critical:** This detailed description helps the AI understand the content structure and when to use each document. The more specific you are, the better the search results.

---

## Step 4: (Optional) Add Instructions

In the **Instructions** field, you can add guidelines for how the agent should respond:

```
When answering questions:
- Always cite the specific document and section you're referencing
- Provide concrete examples when explaining procedures
- Include relevant measure codes (BCS, CDC, CBP, etc.)
- Reference specific compliance thresholds and targets
- Explain the "why" behind policies and procedures
- If a question requires data analysis, suggest using Genie or UC Functions instead
- For member-specific queries, direct users to UC Functions like lookup_member()
```

---

## Step 5: Create the Agent

1. Review all fields are filled correctly
2. Click **Create Agent**
3. Wait 5-10 minutes for provisioning
4. Status will change: **PROVISIONING** → **READY**
5. Once READY, copy the **Endpoint ID** (format: `ka-XXXXX-endpoint`)

---

## Step 6: Grant Permissions ⚠️ REQUIRED

**After the endpoint is READY, you MUST grant permissions or users will get "Permission denied" errors.**

Run this script in a Python environment with Databricks SDK:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()  # Uses DEFAULT profile from ~/.databrickscfg

# Configuration
endpoint_name = "hedis_quality_knowledge_assistant"

# Get endpoint UUID (required for permissions API)
endpoint = w.serving_endpoints.get(endpoint_name)
endpoint_id = endpoint.id  # This is the UUID, not the name

print(f"📋 Endpoint: {endpoint.name}")
print(f"🆔 UUID: {endpoint_id}")
print(f"📊 State: {endpoint.state.ready.value if endpoint.state else 'UNKNOWN'}")

# Grant CAN_QUERY permission to all users
response = w.api_client.do(
    "PATCH",
    f"/api/2.0/permissions/serving-endpoints/{endpoint_id}",  # Use UUID!
    body={
        "access_control_list": [
            {
                "group_name": "users",
                "permission_level": "CAN_QUERY"
            }
        ]
    }
)

print(f"✅ Permissions granted!")

# Verify permissions
perms = w.api_client.do("GET", f"/api/2.0/permissions/serving-endpoints/{endpoint_id}")
print("\n📋 Current permissions:")
for acl in perms.get('access_control_list', []):
    principal = acl.get('group_name') or acl.get('user_name')
    permissions = [p['permission_level'] for p in acl['all_permissions']]
    print(f"   - {principal}: {permissions}")
```

**Common error:** Using endpoint name instead of UUID will fail. Always get the UUID first with `w.serving_endpoints.get()`.

---

## Step 7: Test the Endpoint

After granting permissions, test the endpoint:

```python
from databricks.sdk import WorkspaceClient
import time
from openai import OpenAI

w = WorkspaceClient()

# Generate temporary token
token = w.tokens.create(
    comment=f"knowledge-assistant-test-{time.time_ns()}",
    lifetime_seconds=3600
)

# Create OpenAI client
client = OpenAI(
    api_key=token.token_value,
    base_url=f"{w.config.host}/serving-endpoints"
)

# Test query
print("🧪 Testing Knowledge Assistant...\n")

response = client.responses.create(
    model="hedis_quality_knowledge_assistant",
    input=[{"role": "user", "content": "What are the HEDIS BCS measure requirements?"}]
)

print("📝 Response:")
print(response.output[0].content[0].text)
```

**Expected response:** Detailed explanation of Breast Cancer Screening measure including:
- Target population (women 50-74)
- Compliance criteria (mammogram within 24 months)
- NCQA target (≥70%)
- Current performance (92%)
- Why it matters

---

## Step 8: Try in AI Playground

1. In the Knowledge Assistant configuration page, find **Deployed agent** in the right panel
2. Click **Try in Playground**
3. This opens AI Playground with your endpoint connected
4. Test queries:
   - "What is the gap closure workflow?"
   - "How do I prioritize member outreach?"
   - "What are NCQA compliance requirements?"
   - "Explain the Stars rating methodology"

---

## Common Issues & Troubleshooting

### Issue: "Permission denied" error
**Solution:** Run the permissions grant script in Step 6. Use the endpoint UUID, not the name.

### Issue: "Endpoint not found"
**Solution:** Verify the endpoint name is correct: `hedis_quality_knowledge_assistant`

### Issue: Poor search results
**Solution:** The "Describe the content" field needs more detail. Add specific topics, measure codes, and use cases.

### Issue: Files not indexed
**Solution:** 
- Verify files are in the volume: `/Volumes/humana_quality/hedis_gold/knowledge_docs/`
- Check files are supported formats (.txt)
- Ensure files are under 50MB each
- Wait 5-10 minutes for indexing to complete

---

## Knowledge Source Files

The endpoint indexes these 4 documents from the volume:

| File | Size | Content |
|------|------|---------|
| `gap_closure_protocols.txt` | 7.3 KB | SOPs for gap closure workflows, intervention protocols, outreach scripts |
| `hedis_measures_guide.txt` | 4.6 KB | Specifications for all HEDIS measures (BCS, CDC, CBP, COL, etc.) |
| `ncqa_quality_guidelines.txt` | 5.1 KB | NCQA compliance requirements, audit standards, Stars methodology |
| `quality_team_communications.txt` | 8.8 KB | Comprehensive FAQ covering dashboard, outreach, reporting, troubleshooting |

**Total:** ~26 KB of domain knowledge

---

## Verification Checklist

After setup, verify:

- [ ] Endpoint status shows **READY**
- [ ] Endpoint ID copied (format: `ka-XXXXX-endpoint`)
- [ ] Permissions granted to `users` group (CAN_QUERY)
- [ ] Test query in Python returns expected response
- [ ] AI Playground shows responses with relevant content
- [ ] Citations reference correct documents
- [ ] Endpoint ID saved in `/dashboard/config.py`:
  ```python
  KNOWLEDGE_ASSISTANT_ENDPOINT_ID = "ka-XXXXX-endpoint"
  ```

---

## Next Steps

1. ✅ **Save the Endpoint ID** - You'll need it for MCP integration
2. ✅ **Configure Genie Space** - See `GENIE_INSTRUCTIONS.md`
3. ✅ **Update dashboard config** - Add endpoint ID to `/dashboard/config.py`
4. ✅ **Deploy MCP integration** - Run "Add MCP" command

---

## Additional Resources

- **Microsoft Documentation:** https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-bricks/knowledge-assistant
- **Knowledge Documents:** `/data/knowledge_content/`
- **Upload Notebook:** `/notebooks/05_upload_knowledge_docs.py`
- **MCP Client:** `/dashboard/mcp_knowledge_assistant_client.py`
- **Complete Setup Guide:** `/data/setup_guides/QUICK_SETUP_GUIDE.md`

---

**Estimated Time:** 15-20 minutes (including endpoint provisioning)

**Cost:** Serverless compute charges apply during endpoint uptime. Endpoints scale to zero after 3 days of inactivity.
