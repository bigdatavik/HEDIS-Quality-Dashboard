# ⚡ Quick Setup Guide - HEDIS Quality MCP Integration

**Get your AI-powered HEDIS quality analytics agent running in ~15 minutes**

---

## 🎯 What You're Setting Up

This guide helps you set up **MCP (Model Context Protocol)** integration for the HEDIS Quality Dashboard, enabling:

✅ **Natural language queries** over your HEDIS data (via Genie)  
✅ **Precise member/gap lookups** (via UC Functions)  
✅ **Policy & specification search** (via Knowledge Assistant)  
✅ **AI-powered agent** that automatically chooses the right tool

---

## 📋 Prerequisites (Already Done!)

These are automatically handled by the project:

- ✅ Unity Catalog tables created (`humana_quality.hedis_gold.*`)
- ✅ UC Functions deployed (6 lookup functions)
- ✅ Knowledge documents ready (`/data/knowledge_content/`)
- ✅ Dashboard deployed and running
- ✅ Databricks workspace with Serverless compute enabled

**You just need to configure Genie Space and Knowledge Assistant!**

---

## 🚀 3-Step Setup (15 minutes)

### Step 1: Upload Knowledge Documents (AUTOMATED - 2 minutes)

**Run the knowledge docs job:**
```bash
cd /Users/vik.malhotra/HEDIS-Quality-Dashboard
databricks bundle run knowledge_docs_job --profile DEFAULT
```

**Or via UI:**
1. Go to **Workflows** in Databricks workspace
2. Find job: **"[HEDIS Quality] 05 - Knowledge Docs Upload"**
3. Click **Run now**
4. Wait ~1-2 minutes for completion

**What it uploads:**
- `gap_closure_protocols.txt` (7.3 KB) - Gap closure SOPs and workflows
- `hedis_measures_guide.txt` (4.6 KB) - HEDIS measure specifications
- `ncqa_quality_guidelines.txt` (5.1 KB) - NCQA compliance requirements
- `quality_team_communications.txt` (8.8 KB) - Comprehensive FAQs

**Uploads to:** `/Volumes/humana_quality/hedis_gold/knowledge_docs/`

✅ **Result:** Knowledge documents ready in Unity Catalog Volume

---

### Step 2: Create Knowledge Assistant (10 minutes)

**Open the detailed guide:** [`KNOWLEDGE_ASSISTANT_UI_FIELDS.md`](./KNOWLEDGE_ASSISTANT_UI_FIELDS.md)

**Quick summary:**

1. **Navigate:** Databricks → **Agents** (left nav) → **Knowledge Assistant**

2. **Configure Basic Info:**
   - **Name:** `hedis_quality_knowledge_assistant`
   - **Description:** Copy from guide (explains what the agent can do)

3. **Configure Knowledge Source:**
   - **Type:** UC Files
   - **Source:** `/Volumes/humana_quality/hedis_gold/knowledge_docs`
   - **Describe the content:** ⚠️ **CRITICAL** - Copy the detailed description from guide (this determines search quality!)

4. **Create & Wait:**
   - Click **Create Agent**
   - Wait 5-10 minutes for **PROVISIONING** → **READY**
   - Copy **Endpoint ID** (format: `ka-XXXXX-endpoint`)

5. **Grant Permissions:** ⚠️ **REQUIRED**
   - Run the Python permission script from the guide
   - Without this, users will get "Permission denied" errors

6. **Test:**
   - Try in AI Playground
   - Test query: "What are the BCS measure requirements?"

✅ **Result:** Knowledge Assistant endpoint ready with proper permissions

**Full step-by-step instructions:** See [`KNOWLEDGE_ASSISTANT_UI_FIELDS.md`](./KNOWLEDGE_ASSISTANT_UI_FIELDS.md)

---

### Step 3: Create Genie Space (5 minutes)

**Open the instructions:** [`GENIE_INSTRUCTIONS.md`](./GENIE_INSTRUCTIONS.md)

**Quick summary:**

1. **Navigate:** Databricks → **Data Intelligence** → **Genie** → **Create Genie Space**

2. **Select Data:**
   - **Catalog:** `humana_quality`
   - **Schema:** `hedis_gold`
   - **Name:** `hedis_quality_genie`

3. **Add Instructions:**
   - Click **Instructions** tab
   - Copy-paste **entire content** from `GENIE_INSTRUCTIONS.md`
   - This teaches Genie about HEDIS terminology, measure codes, and response formatting

4. **(Optional) Add SQL Expressions:**
   - Click **SQL Expressions** tab
   - Add example queries from the guide
   - Helps Genie learn query patterns

5. **Get Genie Space ID:**
   - Look at the URL in your browser
   - Copy the 32-character hex string: `01f0b223e0e31cb0b4b093ef8578bcf8`

6. **Test:**
   - Ask: "What is the average quality score?"
   - Ask: "Show me BCS compliance rate"
   - Verify Genie understands HEDIS terminology

✅ **Result:** Genie Space configured with HEDIS domain knowledge

**Full instructions with examples:** See [`GENIE_INSTRUCTIONS.md`](./GENIE_INSTRUCTIONS.md)

---

## 🎉 Integration Complete! Now Connect to Dashboard

You have:
- ✅ Knowledge Assistant Endpoint ID: `ka-XXXXX-endpoint`
- ✅ Genie Space ID: `01f0b223e0e31cb0...`

**To add MCP to your dashboard, tell me:**
```
Add MCP to my project
```

I will:
1. Ask for your Genie Space ID and Knowledge Assistant Endpoint ID
2. Update `/dashboard/config.py` with your IDs
3. Add MCP Search tab to the dashboard
4. Update `dashboard/app.yaml` with environment variables
5. Create test notebook for fast iteration
6. Redeploy the app automatically
7. Provide workspace URL

**Your dashboard will then have:**
- 🔍 **MCP Search tab** with natural language query interface
- 🤖 **AI Agent** that automatically picks the right tool
- 📊 **8 tools available** (Genie + 6 UC Functions + Knowledge Assistant)
- 💬 **Chat interface** with conversation history

**Total setup time:** ~15 minutes (including 10 min wait for Knowledge Assistant provisioning)

---

## 📂 Knowledge Documents Overview

These 4 documents are indexed by Knowledge Assistant:

| File | Size | Content | Use Cases |
|------|------|---------|-----------|
| **gap_closure_protocols.txt** | 7.3 KB | Gap closure SOPs, intervention protocols, phone scripts, barriers/solutions, technology tools, success metrics, annual timeline | "How do I prioritize outreach?", "What's the standard phone script?", "How to handle transportation barriers?" |
| **hedis_measures_guide.txt** | 4.6 KB | All HEDIS measure specifications (BCS, CDC, CBP, COL, CIS, W15, AWC, PPC), Stars ratings, gap closure best practices | "What is the BCS measure?", "CDC compliance criteria?", "Stars rating thresholds?" |
| **ncqa_quality_guidelines.txt** | 5.1 KB | NCQA compliance requirements, data collection methods, audit requirements, quality improvement strategies, Stars impact | "What are NCQA audit requirements?", "How are Stars calculated?", "What data collection methods are acceptable?" |
| **quality_team_communications.txt** | 8.8 KB | Comprehensive FAQs covering dashboard usage, member outreach, provider engagement, reporting, system/technical questions | "How often is dashboard updated?", "How to export data?", "Who has access to the dashboard?" |

**Total:** ~26 KB of HEDIS domain knowledge

---

## 🎯 What Each Component Does

### Knowledge Assistant (Policy & Specifications)
**Answers:**
- "What is" questions → Definitions and specifications
- "How to" questions → Procedures and workflows
- "Explain" questions → Policy interpretations
- "What are the requirements" → Compliance criteria

**Example queries:**
- "What is the BCS measure?"
- "How do I close a gap in care?"
- "What are NCQA audit requirements?"
- "Explain the gap prioritization matrix"

---

### Genie Space (Data Analytics)
**Answers:**
- Aggregate statistics → "What's our overall compliance rate?"
- Trend analysis → "How has performance changed over time?"
- Comparisons → "Which measures have the most gaps?"
- Rankings → "Top 10 performers"

**Example queries:**
- "What is our average quality score?"
- "Show me BCS performance"
- "How many members have open gaps?"
- "Compare CDC and CBP compliance rates"

---

### UC Functions (Precise Lookups)
**Answers:**
- Member-specific → "Show member M000001's gaps"
- Cohort identification → "Which members have BCS gaps?"
- Individual measure performance → "Show me CDC measure details"
- Risk identification → "Members at risk for CBP"

**Available functions:**
- `lookup_member(member_id)` - Member demographics and status
- `lookup_member_measures(member_id)` - All measures for a member
- `lookup_member_gaps(member_id)` - Open gaps for a member
- `members_with_gap(measure_code)` - All members with specific gap
- `lookup_measure_performance(measure_code)` - Overall measure stats
- `members_at_risk(measure_code)` - Members at risk for a measure

---

### MCP Agent (Intelligent Orchestration)
**Combines all three:**
- Automatically selects the right tool(s) for each question
- Can use multiple tools in sequence
- Provides comprehensive answers with citations
- Maintains conversation context

**Example complex query:**
"Show me member M000001's gaps, explain why BCS is important, and tell me our overall BCS performance"

**Agent will:**
1. Use `lookup_member_gaps('M000001')` for member's gaps
2. Use Knowledge Assistant to explain BCS importance
3. Use Genie to query overall BCS performance
4. Synthesize into one comprehensive answer

---

## ✅ Verification Checklist

After setup, verify each component:

### Knowledge Documents
- [ ] All 4 files visible in volume at `/Volumes/humana_quality/hedis_gold/knowledge_docs/`
- [ ] File sizes match: gap_closure (7.3 KB), measures_guide (4.6 KB), ncqa_guidelines (5.1 KB), communications (8.8 KB)

### Knowledge Assistant
- [ ] Endpoint status: **READY** (not PROVISIONING)
- [ ] Endpoint ID copied (format: `ka-XXXXX-endpoint`)
- [ ] Permissions granted (`users` group has `CAN_QUERY`)
- [ ] Test query works: "What is the BCS measure?"
- [ ] Response includes citations and relevant content

### Genie Space
- [ ] Instructions pasted into **Instructions** tab
- [ ] (Optional) SQL expressions added
- [ ] Genie Space ID copied from URL (32-character hex)
- [ ] Test query works: "What is our average quality score?"
- [ ] Genie understands HEDIS terminology (BCS, CDC, etc.)

### MCP Integration (After "Add MCP" command)
- [ ] `/dashboard/config.py` updated with IDs
- [ ] Dashboard has **🔍 MCP Search** tab
- [ ] Status shows: "✅ AI Agent Ready | 8 tools available"
- [ ] Member query works: "Show me member M000001's gaps"
- [ ] Analytics query works: "What's our compliance rate?"
- [ ] Knowledge query works: "What are BCS requirements?"

---

## 🔥 Test Queries (After Full Setup)

Try these queries in the MCP Search tab:

### Knowledge Queries
```
What is the BCS measure?
What are the exclusion criteria for CDC?
How do I prioritize member outreach?
Explain the gap closure workflow
What are NCQA audit requirements?
```

### Analytics Queries
```
What is our overall compliance rate?
Show me BCS performance
Which measures have the most gaps?
How many members closed gaps this quarter?
Compare CDC and CBP compliance rates
```

### Member Queries
```
Show me member M000001's gaps
Which members have BCS gaps?
Find members at risk for CDC
Show me measure performance for COL
```

### Combined Queries
```
Show me member M000001's gaps and explain why BCS is important
Which members have BCS gaps and what's our overall BCS performance?
What is CDC measure and how many members have CDC gaps?
```

---

## 🆘 Troubleshooting

### Knowledge Assistant Issues

**Problem:** "Permission denied" error  
**Solution:** Run the permission granting script in `KNOWLEDGE_ASSISTANT_UI_FIELDS.md` (Step 6)

**Problem:** Poor search results  
**Solution:** Verify the "Describe the content" field has the detailed description from the guide

**Problem:** Endpoint not found  
**Solution:** Check endpoint name is exactly: `hedis_quality_knowledge_assistant`

### Genie Space Issues

**Problem:** Genie doesn't understand measure codes  
**Solution:** Verify instructions were pasted into the **Instructions** tab

**Problem:** Genie gives wrong answers  
**Solution:** Add more specific examples in instructions or SQL expressions tab

### MCP Integration Issues

**Problem:** "0 functions found"  
**Solution:** Verify UC Functions job completed successfully and permissions are granted

**Problem:** Agent not using right tool  
**Solution:** Rephrase your query to be more specific (e.g., "Show member M000001" vs "Tell me about members")

---

## 📚 Additional Resources

### Setup Guides (This Folder)
- **KNOWLEDGE_ASSISTANT_UI_FIELDS.md** - Complete KA setup with copy-paste fields
- **GENIE_INSTRUCTIONS.md** - Complete Genie configuration with examples
- **README.md** - Overview of all resources and maintenance guide

### Documentation (Parent Folder)
- **../MY_ENVIRONMENT.md** - Complete MCP patterns, troubleshooting, code templates
- **../README.md** - Project overview and deployment guide

### Code & Notebooks
- **../notebooks/05_upload_knowledge_docs.py** - Knowledge document upload notebook
- **../dashboard/mcp_*_client.py** - MCP client implementations
- **../dashboard/hedis_agent.py** - AI agent orchestration logic
- **../test_notebooks/test_hedis_mcp_agent.ipynb** - Interactive testing notebook

### Microsoft Documentation
- [Knowledge Assistant Official Docs](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-bricks/knowledge-assistant)
- [Genie Spaces Documentation](https://docs.databricks.com/en/genie/index.html)
- [Unity Catalog Functions](https://docs.databricks.com/en/sql/language-manual/sql-ref-functions-udf-uc.html)

---

## 💡 Pro Tips

1. **Test locally first:** Before deploying MCP, test Knowledge Assistant and Genie separately
2. **Start simple:** Test with basic queries before trying complex multi-tool queries
3. **Use test notebook:** The test notebook (`test_notebooks/`) is 24-36x faster than testing through UI
4. **Monitor costs:** Knowledge Assistant and Genie use serverless compute - monitor usage
5. **Iterate on instructions:** If Genie doesn't understand, add more examples to instructions
6. **Update knowledge docs:** When policies change, update the .txt files and re-upload

---

## 🎓 Learning Path

**New to MCP?** Follow this order:

1. **Read this guide** - Get the big picture (10 min)
2. **Upload documents** - Run the knowledge docs job (2 min)
3. **Create Knowledge Assistant** - Follow `KNOWLEDGE_ASSISTANT_UI_FIELDS.md` (10 min)
4. **Create Genie Space** - Follow `GENIE_INSTRUCTIONS.md` (5 min)
5. **Test separately** - Verify each component works independently (5 min)
6. **Add MCP integration** - Run "Add MCP" command (5 min)
7. **Test together** - Try complex queries in dashboard (5 min)
8. **Review code** - Study `../dashboard/hedis_agent.py` to understand orchestration (30 min)
9. **Deep dive** - Read `../MY_ENVIRONMENT.md` MCP sections (1 hour)

**Already set up?** Use as reference:
- Quick test queries section for examples
- Troubleshooting section when issues arise
- Additional resources for deep dives

---

## 🚀 Ready to Start?

**Right now:**
1. Run knowledge docs upload job (2 min)
2. Open `KNOWLEDGE_ASSISTANT_UI_FIELDS.md` in this folder
3. Open `GENIE_INSTRUCTIONS.md` in this folder
4. Follow Step 2 and Step 3 above

**Then tell me:**
```
Add MCP to my project
```

**And you'll have a fully functional AI-powered HEDIS quality analytics agent!** 🎉

---

**Questions? Issues? See the troubleshooting section above or check `../MY_ENVIRONMENT.md` for comprehensive guidance.**
