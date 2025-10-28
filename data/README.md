# HEDIS Quality Dashboard - Knowledge Documents

This folder contains all knowledge documents for the HEDIS Quality Measures AI Agent.

## 📂 Files Overview

### 🤖 Agent Knowledge Documents (Uploaded to Unity Catalog Volume)

These 4 files are uploaded to `/Volumes/humana_quality/hedis_gold/knowledge_docs` by the `05_upload_knowledge_docs.py` notebook:

1. **`agent_knowledge_source_guide.txt`** (4,800 words)
   - What data sources are available (Genie, UC Functions, Knowledge Assistant)
   - Decision trees for selecting the right tool
   - Best practices and error handling
   - Response formatting guidelines

2. **`knowledge_source_descriptions.txt`** (3,200 words)
   - Detailed documentation of each UC Function
   - Parameters, return values, use cases
   - Genie Space capabilities
   - Knowledge Assistant coverage
   - Performance characteristics

3. **`hedis_policies.txt`** (6,500 words)
   - Complete HEDIS measure specifications (BCS, CDC, CBP, COL, OMW)
   - Gap closure procedures (step-by-step)
   - NCQA compliance requirements
   - Star rating calculations
   - Revenue impact methodology
   - Common scenarios and resolutions

4. **`faq_documentation.txt`** (5,000 words)
   - Member-level questions (lookups, gaps, status)
   - Measure-level questions (performance, codes)
   - Gap closure questions (timing, procedures)
   - Compliance questions (rates, benchmarks)
   - Data questions (refresh, troubleshooting)
   - Operational questions (prioritization, ROI)

**Total: ~19,500 words of comprehensive documentation**

---

### 📋 UI Setup Guides (For Manual Configuration)

These 2 files contain ready-to-paste content for Databricks UI:

5. **`KNOWLEDGE_ASSISTANT_UI_FIELDS.md`**
   - Copy-paste values for Knowledge Assistant endpoint creation
   - Name field: `hedis_quality_knowledge_assistant`
   - Description field (for UI)
   - "Describe the content" field (CRITICAL - comprehensive description)
   - Permission granting script
   - Testing script

6. **`GENIE_INSTRUCTIONS.md`**
   - Copy-paste content for Genie "Instructions" tab
   - General instructions (abbreviations, terminology, calculation methods)
   - SQL Expression examples (8 examples)
   - Testing queries
   - Tips for using Genie effectively

---

## 🚀 Usage Workflow

### Step 1: Upload Knowledge Documents to Volume

Run notebook: `notebooks/05_upload_knowledge_docs.py`

This notebook:
- Reads all 4 `.txt` files from this folder
- Uploads them to `/Volumes/humana_quality/hedis_gold/knowledge_docs`
- Creates the volume if it doesn't exist

**Important:** Documents are saved locally first (this folder) for version control!

---

### Step 2: Create Knowledge Assistant Endpoint

1. Navigate to: **Machine Learning → Serving** in Databricks UI
2. Click **"Create Serving Endpoint"**
3. Select **"Knowledge Assistant"** type
4. Open `KNOWLEDGE_ASSISTANT_UI_FIELDS.md` in this folder
5. Copy-paste the values from the file into the UI fields:
   - Name: `hedis_quality_knowledge_assistant`
   - Description: [paste from file]
   - Source: `/Volumes/humana_quality/hedis_gold/knowledge_docs`
   - "Describe the content": [paste comprehensive description from file]
6. Click **"Create Agent"**
7. Wait 5-10 minutes for READY status
8. Run the permission granting script from the file
9. Copy the Endpoint ID (format: `ka-XXXXX-endpoint`)

---

### Step 3: Create Genie Space

1. Navigate to: **Data Intelligence → Genie** in Databricks UI
2. Click **"Create Genie Space"**
3. Select catalog: `humana_quality`, schema: `hedis_gold`
4. Name: `hedis_quality_genie`
5. Click **"Instructions"** tab
6. Open `GENIE_INSTRUCTIONS.md` in this folder
7. Copy-paste the General Instructions into the Text tab
8. Click **"SQL Expressions"** tab
9. Add each SQL example from the file (8 examples)
10. Test with sample queries
11. Copy the Genie Space ID from URL (format: `01f06a3...`)

---

### Step 4: Integrate with MCP

After completing Steps 1-3, you have:
- ✅ Knowledge documents uploaded to volume
- ✅ Knowledge Assistant endpoint created and configured
- ✅ Genie Space created with instructions

Now run: **"Add MCP to my project"**

I will:
1. Ask for Genie Space ID (from Step 3)
2. Ask for Knowledge Assistant Endpoint ID (from Step 2)
3. Update `dashboard/config.py` with these IDs
4. Add MCP Search tab to dashboard
5. Update dependencies
6. Redeploy automatically

---

## 📊 Document Statistics

| File | Size | Words | Purpose |
|------|------|-------|---------|
| agent_knowledge_source_guide.txt | ~24 KB | 4,800 | Tool selection & decision trees |
| knowledge_source_descriptions.txt | ~16 KB | 3,200 | Detailed function documentation |
| hedis_policies.txt | ~33 KB | 6,500 | Measure specs & procedures |
| faq_documentation.txt | ~25 KB | 5,000 | Common questions & answers |
| **Total** | **~98 KB** | **19,500** | **Complete knowledge base** |

---

## 🔄 Updating Documents

When you need to update the knowledge base:

1. **Edit files locally** in this folder (version controlled)
2. **Commit changes** to git
3. **Redeploy**: Run `notebooks/05_upload_knowledge_docs.py` to upload updated files
4. **Refresh Knowledge Assistant**: 
   - Delete old endpoint
   - Create new endpoint pointing to updated files
   - OR wait 24 hours for automatic refresh

---

## ✅ Best Practices

1. **Always edit locally first** - Files in this folder are version controlled
2. **Keep documents current** - Update when HEDIS specifications change
3. **Test after updates** - Verify Knowledge Assistant returns correct information
4. **Document changes** - Add notes about what was updated and why
5. **Annual review** - HEDIS specs update January 1 each year

---

## 🎯 Coverage Checklist

Our knowledge base covers:

- ✅ All 5 major HEDIS measures (BCS, CDC, CBP, COL, OMW)
- ✅ Complete gap closure procedures
- ✅ NCQA compliance requirements
- ✅ Star rating calculations
- ✅ Revenue impact methodology
- ✅ All 6 UC Functions with examples
- ✅ Genie Space usage patterns
- ✅ Common troubleshooting scenarios
- ✅ Operational best practices
- ✅ Performance benchmarks

---

## 📚 Related Documentation

- **Notebooks**: `../notebooks/05_upload_knowledge_docs.py` - Upload script
- **Dashboard**: `../dashboard/mcp_knowledge_assistant_client.py` - Client code
- **Environment Guide**: `../MY_ENVIRONMENT.md` - Complete MCP setup guide
- **Test Notebook**: `../test_notebooks/test_hedis_mcp_agent.ipynb` - Agent testing

---

## 🆘 Troubleshooting

**Issue: Knowledge Assistant returns "No results found"**
- Verify documents are uploaded to volume: Check `/Volumes/humana_quality/hedis_gold/knowledge_docs`
- Rephrase question with simpler terms
- Check endpoint status is READY

**Issue: Knowledge Assistant gives incorrect information**
- Review and update the relevant `.txt` file
- Redeploy with updated documents
- May need to recreate endpoint for immediate refresh

**Issue: Can't find specific information**
- Search within the 4 `.txt` files locally
- Information may need to be added
- Consider adding to FAQ if commonly asked

---

## 📞 Questions?

For questions about:
- **Document content**: Review the `.txt` files in this folder
- **Upload process**: See `notebooks/05_upload_knowledge_docs.py`
- **MCP integration**: See `MY_ENVIRONMENT.md` (MCP section)
- **Agent behavior**: See `dashboard/hedis_agent.py`

