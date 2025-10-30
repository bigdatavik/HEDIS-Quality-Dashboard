# Data & Setup Resources

This folder contains all the knowledge content and setup instructions for MCP (Model Context Protocol) integration in the HEDIS Quality Dashboard.

## 📁 Folder Structure

```
data/
├── knowledge_content/          # Knowledge documents uploaded to volume
│   ├── gap_closure_protocols.txt
│   ├── hedis_measures_guide.txt
│   ├── ncqa_quality_guidelines.txt
│   ├── quality_team_communications.txt
│   └── README.md
│
├── setup_guides/               # UI configuration instructions
│   ├── QUICK_SETUP_GUIDE.md
│   ├── KNOWLEDGE_ASSISTANT_UI_FIELDS.md
│   ├── GENIE_INSTRUCTIONS.md
│   └── README.md
│
└── README.md                   # This file
```

---

## 🎯 Quick Start

### For Complete MCP Setup (15 minutes):
1. **Upload Knowledge Files** → See `knowledge_content/README.md` (2 min)
2. **Create Knowledge Assistant** → See `setup_guides/KNOWLEDGE_ASSISTANT_UI_FIELDS.md` (10 min)
3. **Create Genie Space** → See `setup_guides/GENIE_INSTRUCTIONS.md` (5 min)
4. **Add MCP to Dashboard** → Run "Add MCP to my project" command (5 min)

### Just Need One Thing?

| I need to... | Go to... |
|-------------|----------|
| Upload knowledge documents | `knowledge_content/README.md` |
| Create Knowledge Assistant endpoint | `setup_guides/KNOWLEDGE_ASSISTANT_UI_FIELDS.md` |
| Configure Genie Space | `setup_guides/GENIE_INSTRUCTIONS.md` |
| Complete setup from scratch | `setup_guides/QUICK_SETUP_GUIDE.md` |
| Understand MCP architecture | `/MY_ENVIRONMENT.md` (MCP sections) |

---

## 📂 What's in Each Folder?

### 📄 `knowledge_content/` 
**Knowledge documents uploaded to Unity Catalog Volume**

Contains 4 text files (~26 KB total) with HEDIS domain knowledge:

| File | Size | Content |
|------|------|---------|
| `gap_closure_protocols.txt` | 7.3 KB | Gap closure SOPs, intervention protocols, outreach scripts, barriers/solutions |
| `hedis_measures_guide.txt` | 4.6 KB | HEDIS measure specifications (BCS, CDC, CBP, COL, CIS, W15, AWC, PPC), Stars ratings |
| `ncqa_quality_guidelines.txt` | 5.1 KB | NCQA compliance requirements, audit standards, Stars methodology |
| `quality_team_communications.txt` | 8.8 KB | Comprehensive FAQs for dashboard, outreach, reporting, troubleshooting |

**Upload destination:** `/Volumes/humana_quality/hedis_gold/knowledge_docs/`

**Upload method:**
```bash
# Automated via notebook
databricks bundle run knowledge_docs_job --profile DEFAULT
```

→ See `knowledge_content/README.md` for detailed upload instructions

---

### 📋 `setup_guides/`
**UI configuration instructions (copy/paste ready)**

Contains 4 markdown files with step-by-step setup instructions:

| File | Purpose | Time |
|------|---------|------|
| `QUICK_SETUP_GUIDE.md` | Complete 3-step setup workflow with test queries | 15 min read |
| `KNOWLEDGE_ASSISTANT_UI_FIELDS.md` | Detailed KA endpoint creation with copy-paste fields | 10 min setup |
| `GENIE_INSTRUCTIONS.md` | Complete Genie configuration with SQL examples | 5 min setup |
| `README.md` | Detailed guide for all setup files | Reference |

**These are instructions you follow, NOT files you upload**

→ See `setup_guides/README.md` for detailed usage

---

## 🚀 Complete Setup Workflow

### Prerequisites ✅
Already completed by the project:
- Unity Catalog tables created (`humana_quality.hedis_gold.*`)
- UC Functions deployed (6 lookup functions)
- Dashboard deployed and running
- Knowledge documents ready to upload

### Step 1: Upload Knowledge Documents (2 minutes) ⚡ AUTOMATED

**Option A: Via command line (recommended)**
```bash
cd /Users/vik.malhotra/HEDIS-Quality-Dashboard
databricks bundle run knowledge_docs_job --profile DEFAULT
```

**Option B: Via Databricks UI**
1. Go to **Workflows** in workspace
2. Find: **"[HEDIS Quality] 05 - Knowledge Docs Upload"**
3. Click **Run now**
4. Wait 1-2 minutes for completion

**What it does:**
- Reads 4 `.txt` files from `data/knowledge_content/`
- Creates volume if needed: `humana_quality.hedis_gold.knowledge_docs`
- Uploads all files to volume
- Verifies upload with file list

✅ **Result:** Knowledge documents ready for Knowledge Assistant indexing

---

### Step 2: Create Knowledge Assistant Endpoint (10 minutes)

**Follow:** `setup_guides/KNOWLEDGE_ASSISTANT_UI_FIELDS.md`

**Quick summary:**
1. Navigate: **Agents** → **Knowledge Assistant**
2. Configure basic info (name, description)
3. Add knowledge source (UC Files from volume)
4. **Critical:** Add detailed "Describe the content" field (from guide)
5. Create and wait for READY status (5-10 min)
6. **Required:** Grant permissions (Python script in guide)
7. Test in AI Playground
8. Copy Endpoint ID (format: `ka-XXXXX-endpoint`)

✅ **Result:** Knowledge Assistant endpoint ready with proper permissions

---

### Step 3: Configure Genie Space (5 minutes)

**Follow:** `setup_guides/GENIE_INSTRUCTIONS.md`

**Quick summary:**
1. Navigate: **Data Intelligence** → **Genie** → **Create Genie Space**
2. Select catalog `humana_quality`, schema `hedis_gold`
3. Add Instructions (copy entire content from guide)
4. (Optional) Add SQL expression examples
5. Test with sample queries
6. Copy Genie Space ID from URL (32-character hex)

✅ **Result:** Genie Space configured with HEDIS terminology

---

### Step 4: Add MCP Integration (5 minutes) ⚡ AUTOMATED

**Command:** Tell me "Add MCP to my project"

**I will:**
1. Ask for your Genie Space ID and Knowledge Assistant Endpoint ID
2. Update `/dashboard/config.py` with IDs
3. Add MCP Search tab to dashboard
4. Update `/dashboard/app.yaml` with environment variables
5. Create test notebook for fast iteration
6. Redeploy app automatically
7. Provide workspace URL

✅ **Result:** Dashboard with AI-powered MCP Search tab

**Total Setup Time: ~20 minutes** (including 10 min wait for KA provisioning)

---

## 🔧 Maintenance & Updates

### Updating Knowledge Documents

**When:** Policies change, new procedures added, FAQs updated

**How:**
1. Edit `.txt` files in `knowledge_content/` folder
2. Test changes locally (review content)
3. Commit to git (version control)
4. Re-run upload notebook:
   ```bash
   databricks bundle run knowledge_docs_job --profile DEFAULT
   ```
5. Knowledge Assistant automatically re-indexes (no restart needed)
6. Test queries to verify changes

**Tip:** Keep local files as source of truth, always edit locally first

---

### Updating Genie Instructions

**When:** Adding new terminology, improving query understanding, fixing misinterpretations

**How:**
1. Edit `setup_guides/GENIE_INSTRUCTIONS.md`
2. Test changes (validate instructions work)
3. Go to Genie Space → **Instructions** tab in Databricks UI
4. Copy/paste updated content
5. Save
6. Test with sample queries to verify improvements

**Tip:** Add concrete examples for better Genie understanding

---

### Updating Knowledge Assistant Configuration

**When:** Changing endpoint description, updating content descriptions

**How:**
1. Edit `setup_guides/KNOWLEDGE_ASSISTANT_UI_FIELDS.md`
2. Go to Knowledge Assistant endpoint in Databricks
3. Update description fields
4. Save changes
5. Test with sample questions

**Note:** Endpoint name and source path cannot be changed after creation

---

## 📖 Related Documentation

### In This Repository

**Code Implementation:**
- `/dashboard/config.py` - MCP configuration (IDs, models)
- `/dashboard/mcp_genie_client.py` - Genie MCP client
- `/dashboard/mcp_uc_functions_client.py` - UC Functions MCP client
- `/dashboard/mcp_knowledge_assistant_client.py` - Knowledge Assistant client
- `/dashboard/hedis_agent.py` - AI agent orchestration

**Notebooks:**
- `/notebooks/04_create_uc_functions.py` - UC Functions creation with permissions
- `/notebooks/05_upload_knowledge_docs.py` - Knowledge document upload

**Configuration:**
- `/databricks.yml` - Bundle configuration
- `/dashboard/app.yaml` - Databricks App configuration

**Complete Guide:**
- `/MY_ENVIRONMENT.md` - MCP patterns, troubleshooting, code templates (lines 1651-3690)

---

### External Resources

**Official Documentation:**
- [Knowledge Assistant](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-bricks/knowledge-assistant) - Microsoft official docs
- [Genie Spaces](https://docs.databricks.com/en/genie/index.html) - Databricks documentation
- [Unity Catalog Functions](https://docs.databricks.com/en/sql/language-manual/sql-ref-functions-udf-uc.html) - UC Functions reference

**GitHub Repository:**
- **Live Code:** https://github.com/bigdatavik/HEDIS-Quality-Dashboard
- **Local Path:** `/Users/vik.malhotra/HEDIS-Quality-Dashboard/`

---

## 💡 Best Practices

### Version Control
✅ **DO:** Keep all knowledge documents in git  
✅ **DO:** Document customizations in comments  
✅ **DO:** Share configurations across team  
✅ **DO:** Use meaningful commit messages when updating content  

❌ **DON'T:** Edit directly in volume (always edit local files first)  
❌ **DON'T:** Skip testing after updates  

---

### Content Management
✅ **DO:** Review knowledge content quarterly (or when policies change)  
✅ **DO:** Update Genie instructions as terminology evolves  
✅ **DO:** Test after every update (verify queries still work)  
✅ **DO:** Keep content concise and well-organized  

❌ **DON'T:** Add sensitive information (PHI, credentials) to knowledge docs  
❌ **DON'T:** Make content too verbose (focus on actionable information)  

---

### Security & Compliance
✅ **DO:** Review content for sensitive information before committing  
✅ **DO:** Use appropriate Unity Catalog permissions (grant CAN_QUERY to specific groups)  
✅ **DO:** Audit Knowledge Assistant access logs regularly  
✅ **DO:** Follow organization's data governance policies  

❌ **DON'T:** Share endpoint IDs publicly  
❌ **DON'T:** Grant overly broad permissions  

---

### Testing & Validation
✅ **DO:** Test Knowledge Assistant with representative queries before deploying  
✅ **DO:** Verify Genie understands HEDIS terminology  
✅ **DO:** Test UC Functions individually before MCP integration  
✅ **DO:** Use the test notebook for fast iteration  

❌ **DON'T:** Skip testing after configuration changes  
❌ **DON'T:** Assume Genie will understand new terminology without examples  

---

## 🎓 Learning Path

### New to MCP?
Follow this order for best results:

1. **Read `setup_guides/QUICK_SETUP_GUIDE.md`** (10 min)
   - Get the big picture
   - Understand what each component does
   - See example test queries

2. **Browse `knowledge_content/` files** (15 min)
   - Understand content structure
   - Review HEDIS domain knowledge
   - See what Knowledge Assistant will index

3. **Follow Step 1: Upload documents** (2 min)
   - Run the automated job
   - Verify files in volume

4. **Follow Step 2: `setup_guides/KNOWLEDGE_ASSISTANT_UI_FIELDS.md`** (10 min)
   - Create Knowledge Assistant endpoint
   - Grant permissions
   - Test with queries

5. **Follow Step 3: `setup_guides/GENIE_INSTRUCTIONS.md`** (5 min)
   - Configure Genie Space
   - Add instructions
   - Test with queries

6. **Add MCP Integration** (5 min)
   - Run "Add MCP" command
   - Get workspace URL
   - Test complete system

7. **Review `/MY_ENVIRONMENT.md` MCP sections** (1 hour)
   - Deep dive into code patterns
   - Understand agent orchestration
   - Learn troubleshooting techniques

**Total learning + setup time: ~2 hours**

---

### Already Set Up?
Use as reference:

- **`setup_guides/`** - When updating Genie or Knowledge Assistant configurations
- **`knowledge_content/`** - When refreshing domain knowledge
- **This README** - Quick lookup for paths, commands, and workflows
- **`QUICK_SETUP_GUIDE.md`** - Test query examples and troubleshooting

---

## ❓ Troubleshooting

### Knowledge Assistant Issues

**Problem:** Not returning relevant results  
**Check:**
- [ ] Files uploaded correctly to `/Volumes/humana_quality/hedis_gold/knowledge_docs/`
- [ ] "Describe the content" field is detailed (from `KNOWLEDGE_ASSISTANT_UI_FIELDS.md`)
- [ ] Endpoint status is READY (not PROVISIONING)

**Solution:** Re-upload documents, verify content description is comprehensive

---

**Problem:** "Permission denied" error  
**Check:**
- [ ] Permission granting script was run (in `KNOWLEDGE_ASSISTANT_UI_FIELDS.md`)
- [ ] Used endpoint UUID (not name) in permissions API

**Solution:** Run permission script with correct endpoint UUID

---

### Genie Space Issues

**Problem:** Doesn't understand HEDIS terminology (BCS, CDC, etc.)  
**Check:**
- [ ] Instructions pasted into **Instructions** tab (not description)
- [ ] Instructions include measure code definitions

**Solution:** Re-paste instructions from `GENIE_INSTRUCTIONS.md`, add more examples

---

**Problem:** Gives wrong answers or queries wrong tables  
**Check:**
- [ ] SQL expression examples added
- [ ] Genie has access to correct schema (`hedis_gold`)

**Solution:** Add specific SQL examples showing correct queries

---

### MCP Integration Issues

**Problem:** "0 functions found" or missing UC Functions  
**Check:**
- [ ] UC Functions job completed successfully
- [ ] EXECUTE permissions granted on all functions
- [ ] Catalog context set with `USE CATALOG`

**Solution:** Re-run UC Functions job (notebook 04), verify permissions

---

**Problem:** Agent not using the right tool  
**Check:**
- [ ] Query is specific enough (include member ID for lookups)
- [ ] Knowledge Assistant and Genie are working individually

**Solution:** Rephrase query to be more specific, test components separately

---

### Upload Issues

**Problem:** Files not appearing in volume  
**Check:**
- [ ] Volume exists: `/Volumes/humana_quality/hedis_gold/knowledge_docs/`
- [ ] Job completed without errors
- [ ] File names match: `gap_closure_protocols.txt`, `hedis_measures_guide.txt`, etc.

**Solution:** Check job logs, verify volume path, re-run upload job

---

**Need more help?**
→ See `/MY_ENVIRONMENT.md` - MCP Troubleshooting Guide (lines 3896-4268)  
→ Check `setup_guides/README.md` for detailed troubleshooting by component

---

## 🤝 Contributing

Found improvements? Have suggestions?

1. **Update the relevant file** (knowledge content or setup guide)
2. **Test your changes** (verify queries work, instructions are clear)
3. **Commit to git** with descriptive message:
   ```bash
   git add data/
   git commit -m "Update: Improved BCS measure description in hedis_measures_guide.txt"
   ```
4. **Share with team** (PR or direct share)

**Types of contributions:**
- 📝 Improving knowledge document accuracy
- 🎨 Clarifying setup instructions
- 🐛 Fixing broken examples or queries
- ✨ Adding new HEDIS measures or procedures
- 📚 Enhancing documentation

---

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| **Total Knowledge Documents** | 4 files |
| **Total Knowledge Size** | ~26 KB |
| **Setup Time** | ~15 minutes |
| **Components** | 3 (Genie + UC Functions + Knowledge Assistant) |
| **Total Tools Available** | 8 (1 Genie + 6 UC Functions + 1 Knowledge Assistant) |
| **UC Functions** | 6 (member lookups, gap queries, measure performance) |

---

**Ready to get started? Head to `setup_guides/QUICK_SETUP_GUIDE.md`!** 🚀

**Questions? Check the troubleshooting section above or see `/MY_ENVIRONMENT.md` for comprehensive guidance.**
