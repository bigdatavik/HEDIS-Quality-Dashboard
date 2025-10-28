# ⚡ Quick Setup Guide - MCP Knowledge Documents

## 🎯 What's In This Folder

This folder contains **EVERYTHING** you need to set up MCP for the HEDIS Quality Dashboard:

✅ **4 knowledge documents** → Upload to Unity Catalog volume
✅ **UI setup guides** → Copy-paste into Databricks UI  
✅ **Complete instructions** → Step-by-step setup

---

## 🚀 3-Step Setup (15 minutes total)

### Step 1: Upload Documents (5 minutes) ⭐ AUTOMATED

**Run this notebook:**
```bash
notebooks/05_upload_knowledge_docs.py
```

**What it does:**
- Reads 4 `.txt` files from this `data/` folder
- Uploads to `/Volumes/humana_quality/hedis_gold/knowledge_docs`
- Creates volume if needed

**Result:** ✅ Knowledge documents ready in Unity Catalog

---

### Step 2: Create Knowledge Assistant (5 minutes)

**Open:** `KNOWLEDGE_ASSISTANT_UI_FIELDS.md` (in this folder)

**Do this:**
1. Go to: **Machine Learning → Serving** in Databricks
2. Click: **"Create Serving Endpoint"**
3. Select: **"Knowledge Assistant"**
4. **Copy-paste** all fields from `KNOWLEDGE_ASSISTANT_UI_FIELDS.md`:
   - Name: `hedis_quality_knowledge_assistant`
   - Description: [paste from file]
   - Source: `/Volumes/humana_quality/hedis_gold/knowledge_docs`
   - "Describe the content": [paste comprehensive description]
5. Click: **"Create Agent"**
6. Wait: 5-10 minutes for READY status
7. Run: Permission granting script (in the file)
8. Copy: Endpoint ID (format: `ka-XXXXX-endpoint`)

**Result:** ✅ Knowledge Assistant endpoint ready

---

### Step 3: Create Genie Space (5 minutes)

**Open:** `GENIE_INSTRUCTIONS.md` (in this folder)

**Do this:**
1. Go to: **Data Intelligence → Genie** in Databricks
2. Click: **"Create Genie Space"**
3. Select: Catalog `humana_quality`, Schema `hedis_gold`
4. Name: `hedis_quality_genie`
5. Click: **"Instructions"** tab
6. **Copy-paste** General Instructions from `GENIE_INSTRUCTIONS.md`
7. Click: **"SQL Expressions"** tab
8. Add: All 8 SQL examples (copy one-by-one from file)
9. Test: Sample queries from file
10. Copy: Genie Space ID from URL

**Result:** ✅ Genie Space configured

---

## 🎉 You're Done! Now Add MCP

Run: **"Add MCP to my project"**

I will ask for:
1. Genie Space ID (from Step 3)
2. Knowledge Assistant Endpoint ID (from Step 2)

Then I will:
- ✅ Configure MCP clients
- ✅ Add MCP Search tab to dashboard
- ✅ Deploy automatically
- ✅ Provide workspace URL

**Total time: ~20 minutes** (including 10 min wait for KA provisioning)

---

## 📂 Files Explained

### Knowledge Documents (Upload to Volume)
1. **`agent_knowledge_source_guide.txt`** (4,800 words)
   - Decision trees: When to use Genie vs UC Functions vs KA
   - Best practices and error handling

2. **`knowledge_source_descriptions.txt`** (3,200 words)
   - Complete UC Function documentation
   - Genie Space capabilities

3. **`hedis_policies.txt`** (6,500 words)
   - HEDIS measure specifications (BCS, CDC, CBP, COL, OMW)
   - Gap closure procedures, NCQA requirements, star ratings

4. **`faq_documentation.txt`** (5,000 words)
   - Common questions: member lookups, gaps, compliance, data

### Setup Guides (Copy-Paste)
5. **`KNOWLEDGE_ASSISTANT_UI_FIELDS.md`**
   - Ready-to-paste values for KA endpoint creation
   - Permission granting script

6. **`GENIE_INSTRUCTIONS.md`**
   - Ready-to-paste instructions for Genie
   - 8 SQL expression examples

### Documentation
7. **`README.md`**
   - Comprehensive guide to all files
   - Usage workflow, best practices

8. **`QUICK_SETUP_GUIDE.md`** (this file)
   - Fast-track setup instructions

---

## ✅ Verification Checklist

After setup, verify:

- [ ] All 4 `.txt` files uploaded to volume:
  ```
  /Volumes/humana_quality/hedis_gold/knowledge_docs/
  ```

- [ ] Knowledge Assistant endpoint:
  - Status: READY ✅
  - Permissions granted ✅
  - Test query works ✅

- [ ] Genie Space:
  - Instructions added ✅
  - SQL examples added ✅
  - Test queries work ✅
  - Genie Space ID copied ✅

- [ ] MCP Integration:
  - Config updated with IDs ✅
  - Dashboard has MCP Search tab ✅
  - All 8 tools available ✅

---

## 🎯 What Each Component Does

**Knowledge Documents → Knowledge Assistant:**
- Answers "what is" questions (definitions)
- Answers "how to" questions (procedures)
- Provides policy interpretations
- Cites HEDIS specifications

**Genie Instructions → Genie Space:**
- Understands HEDIS terminology
- Translates natural language to SQL
- Provides aggregate analytics
- Creates trend reports

**UC Functions → MCP Agent:**
- Precise member lookups
- Gap identification
- Measure performance
- Proactive risk identification

**Combined → AI Agent:**
- Answers ANY question about HEDIS quality
- Uses the right tool automatically
- Combines data with knowledge
- Provides actionable insights

---

## 🔥 Quick Test Queries (After Setup)

**Test Knowledge Assistant:**
- "What is the BCS measure?"
- "What are the exclusion criteria for CDC?"
- "How do I close a gap?"

**Test Genie Space:**
- "What is our overall compliance rate?"
- "Show me BCS performance"
- "Which measures have the most gaps?"

**Test MCP Agent (After Integration):**
- "Show me member M000001's gaps"
- "Which members have BCS gaps?"
- "Explain the CDC measure and show me our performance"

---

## 📊 Content Summary

| Component | Lines | Words | Purpose |
|-----------|-------|-------|---------|
| Agent Guide | 220 | 4,800 | Tool selection logic |
| Source Descriptions | 170 | 3,200 | Function documentation |
| HEDIS Policies | 340 | 6,500 | Measure specs & procedures |
| FAQ Documentation | 280 | 5,000 | Common questions |
| **Total** | **1,010** | **19,500** | **Complete knowledge base** |

---

## 🆘 Having Issues?

**Knowledge Assistant not working?**
→ Check: `KNOWLEDGE_ASSISTANT_UI_FIELDS.md` for troubleshooting

**Genie not understanding queries?**
→ Check: `GENIE_INSTRUCTIONS.md` for correct instruction format

**General MCP issues?**
→ See: `../MY_ENVIRONMENT.md` (MCP Implementation Pattern section)

---

## 🎓 Want to Learn More?

- **Complete MCP Guide**: `../MY_ENVIRONMENT.md` (lines 1651-2500)
- **Code Templates**: `../MY_ENVIRONMENT.md` (MCP Code Templates section)
- **Test Notebook**: `../test_notebooks/test_hedis_mcp_agent.ipynb`
- **Dashboard Code**: `../dashboard/hedis_agent.py`

---

## 🚀 Ready to Start?

1. Open `KNOWLEDGE_ASSISTANT_UI_FIELDS.md`
2. Open `GENIE_INSTRUCTIONS.md`
3. Follow the 3 steps above
4. Run "Add MCP to my project"

**You'll have a fully functional AI-powered HEDIS quality analytics agent in ~20 minutes!**

