# MCP Setup Guides

This folder contains **UI configuration instructions** for setting up Genie Space and Knowledge Assistant in the Databricks workspace.

## 📋 Files in This Folder

All files contain copy-paste ready content for Databricks UI configuration:

1. **QUICK_SETUP_GUIDE.md** - Fast-track 3-step setup (15 minutes)
2. **KNOWLEDGE_ASSISTANT_UI_FIELDS.md** - What to paste in Knowledge Assistant creation UI
3. **GENIE_INSTRUCTIONS.md** - What to paste in Genie Space Instructions tab

---

## 🎯 Purpose

These guides contain the exact text you copy/paste into Databricks UI fields to configure:
- Genie Space instructions (teaching Genie about your domain)
- Knowledge Assistant descriptions (what content is indexed)
- Complete setup workflow (end-to-end instructions)

**These are NOT uploaded anywhere - they're instructions you follow!**

---

## 🚀 Quick Start (15 minutes)

### Step 1: Create Genie Space (5 minutes)
1. Open **GENIE_INSTRUCTIONS.md**
2. Navigate to: **Data Intelligence → Genie → Create Genie Space**
3. Select catalog: `humana_quality` and schema: `hedis_gold`
4. After creation, click **Instructions** tab
5. Copy/paste the **entire content** from GENIE_INSTRUCTIONS.md
6. Save

**What it does:** Teaches Genie about HEDIS terminology, measure codes, and how to format responses.

---

### Step 2: Create Knowledge Assistant (5 minutes)
1. Open **KNOWLEDGE_ASSISTANT_UI_FIELDS.md**
2. Navigate to: **Machine Learning → Serving → Create Serving Endpoint → Knowledge Assistant**
3. Follow the step-by-step instructions in the file
4. Copy/paste the provided content into each UI field
5. Wait ~5-10 minutes for endpoint to provision

**What it does:** Indexes your knowledge documents and makes them searchable via natural language.

---

### Step 3: Update MCP Configuration (5 minutes)
1. Get Genie Space ID from URL (32-character hex string)
2. Get Knowledge Assistant Endpoint ID (format: `ka-XXXXX-endpoint`)
3. Update `/dashboard/config.py`:
   ```python
   GENIE_SPACE_ID = "your-genie-space-id"
   KNOWLEDGE_ASSISTANT_ENDPOINT_ID = "ka-XXXXX-endpoint"
   ```
4. Redeploy app:
   ```bash
   databricks bundle deploy --profile DEFAULT
   databricks bundle run hedis_quality_dashboard_app --profile DEFAULT
   ```

**Done!** Your MCP integration is live. 🎉

---

## 📖 File Details

### QUICK_SETUP_GUIDE.md
**Purpose:** Complete end-to-end setup instructions

**Contains:**
- Pre-requisites checklist
- 3-step setup workflow
- Troubleshooting tips
- Verification steps

**Use when:** Setting up MCP for the first time

---

### GENIE_INSTRUCTIONS.md
**Purpose:** Content to paste in Genie Space → Instructions tab

**Contains:**
- Domain terminology definitions (HEDIS, BCS, CDC, etc.)
- Measure code mappings
- How to format responses
- Example queries and expected outputs

**Use when:** 
- Creating new Genie Space
- Updating Genie with new terminology
- Teaching Genie better response formats

**Where to paste:**
```
Databricks UI → Data Intelligence → Genie → Your Space → Instructions Tab
```

---

### KNOWLEDGE_ASSISTANT_UI_FIELDS.md
**Purpose:** Field-by-field instructions for Knowledge Assistant UI

**Contains:**
- Name field template
- Description field (what to paste)
- "Describe the content" field (CRITICAL - detailed content description)
- Source volume path
- Configuration settings

**Use when:**
- Creating Knowledge Assistant endpoint
- Updating endpoint description
- Troubleshooting poor search results

**Where to use:**
```
Databricks UI → Machine Learning → Serving → Create Serving Endpoint → Knowledge Assistant
```

---

## 🔄 Updating Configurations

### When to Update Genie Instructions

Update **GENIE_INSTRUCTIONS.md** and re-paste into Genie UI when:
- ✅ Adding new measure codes
- ✅ Changing terminology
- ✅ Improving response quality
- ✅ Adding new examples
- ✅ Fixing common misconceptions

### When to Update Knowledge Assistant Configuration

Update **KNOWLEDGE_ASSISTANT_UI_FIELDS.md** and endpoint settings when:
- ✅ Adding new document types to volume
- ✅ Changing content structure
- ✅ Improving search relevance
- ✅ Updating domain focus

### When to Update Quick Setup Guide

Update **QUICK_SETUP_GUIDE.md** when:
- ✅ Process changes (new Databricks UI)
- ✅ Adding best practices learned
- ✅ Simplifying steps
- ✅ Adding troubleshooting tips

---

## ✅ Verification After Setup

### Test Genie Space
```
1. Open Genie Space
2. Ask: "What is the average quality score?"
3. Expected: Should return aggregate data from quality_trends table
4. Ask: "Show me BCS compliance rate"
5. Expected: Should understand BCS = Breast Cancer Screening
```

### Test Knowledge Assistant
```
1. Open Knowledge Assistant endpoint
2. Ask: "What are the HEDIS BCS requirements?"
3. Expected: Should return measure specifications from hedis_policies.txt
4. Ask: "How do I close a gap in care?"
5. Expected: Should return step-by-step procedure
```

### Test MCP Integration in App
```
1. Open dashboard → MCP Search tab
2. Ask: "Show me member M000001's gaps"
3. Expected: Uses UC Functions to lookup member
4. Ask: "What's our average quality score?"
5. Expected: Uses Genie to query aggregate data
6. Ask: "What are NCQA requirements?"
7. Expected: Uses Knowledge Assistant to search docs
```

---

## 🎨 Customization for New Domains

Adapting these guides for HCC, Pharmacy, or other domains?

### GENIE_INSTRUCTIONS.md
```markdown
Replace:
- HEDIS → HCC / Pharmacy / Claims
- BCS, CDC, CBP → HCC_85, RAF score, Drug utilization
- Member quality metrics → RAF scores / Drug costs / Claim amounts

Keep:
- Format (Examples: * ... bullets)
- Structure (definitions → formatting → examples)
- Markdown syntax
```

### KNOWLEDGE_ASSISTANT_UI_FIELDS.md
```markdown
Replace:
- HEDIS policies → HCC coding guidelines / Formulary policies
- NCQA compliance → CMS-HCC V28 model / Prior authorization rules
- Quality measures → RAF calculations / Drug interactions

Keep:
- Field structure (Description, Describe the content)
- Level of detail in descriptions
- Organization (numbered lists, clear sections)
```

### QUICK_SETUP_GUIDE.md
```markdown
Replace:
- HEDIS-specific examples with domain examples
- humana_quality → your_catalog
- hedis_gold → your_schema

Keep:
- 3-step structure
- Time estimates
- Verification steps
```

---

## 💡 Best Practices

### Content Organization
✅ **DO**: Keep one topic per file  
✅ **DO**: Use descriptive file names  
✅ **DO**: Include version/date in headers  
✅ **DO**: Format for easy copy/paste  

### Maintenance
✅ **DO**: Test after every update  
✅ **DO**: Version control all changes  
✅ **DO**: Document why changes were made  
✅ **DO**: Share updates with team  

### Quality
✅ **DO**: Use concrete examples  
✅ **DO**: Be specific with terminology  
✅ **DO**: Include expected behaviors  
✅ **DO**: Proofread before pasting to UI  

---

## 🔗 Related Resources

### Knowledge Content (What Gets Uploaded)
- Actual content files: `../knowledge_content/`
- Upload instructions: `../knowledge_content/README.md`

### Code Implementation
- MCP client code: `/dashboard/mcp_*_client.py`
- Configuration: `/dashboard/config.py`
- Agent implementation: `/dashboard/hedis_agent.py`

### Documentation
- Complete MCP patterns: `/MY_ENVIRONMENT.md` (sections on Genie, Knowledge Assistant, MCP)
- Main data README: `../README.md`

---

## 🆘 Troubleshooting

### Genie not understanding queries?
→ Check GENIE_INSTRUCTIONS.md has been pasted to Instructions tab  
→ Add more examples for common query patterns  
→ Verify terminology definitions are clear  

### Knowledge Assistant returning wrong results?
→ Verify "Describe the content" field is detailed (from KNOWLEDGE_ASSISTANT_UI_FIELDS.md)  
→ Check volume path is correct  
→ Ensure knowledge files are uploaded to volume  

### Setup taking too long?
→ Follow QUICK_SETUP_GUIDE.md in order  
→ Skip optional steps on first pass  
→ Knowledge Assistant provisioning takes 5-10 min (expected)  

---

## 📅 Maintenance Schedule

### Monthly
- Review Genie query logs for new patterns
- Update instructions if users frequently ask unclear questions

### Quarterly
- Audit Knowledge Assistant relevance
- Update examples in guides
- Refresh screenshots if UI changed

### Annually
- Complete guide review
- Incorporate lessons learned
- Update for Databricks platform changes

---

## 🎓 Learning Path

**New to MCP setup?** Follow this order:

1. **Read QUICK_SETUP_GUIDE.md** - Get the overview (10 min)
2. **Follow Step 1** - Set up Genie (5 min)
3. **Follow Step 2** - Set up Knowledge Assistant (5 min)
4. **Test everything** - Verify it works (5 min)
5. **Deep dive** - Read MY_ENVIRONMENT.md MCP section (30 min)

**Setting up for a team?**
- Share QUICK_SETUP_GUIDE.md as onboarding doc
- Provide filled-in KNOWLEDGE_ASSISTANT_UI_FIELDS.md with your IDs
- Walk through Genie setup together
- Document any customizations

---

**Ready to set up MCP? Start with QUICK_SETUP_GUIDE.md!** 🚀
