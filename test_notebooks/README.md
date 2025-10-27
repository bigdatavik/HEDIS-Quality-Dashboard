# Test Notebooks

**Purpose:** Notebooks for testing and experimentation - separate from production pipeline notebooks.

## 📁 Organization

```
test_notebooks/          ← Testing notebooks (this folder)
└── test_hedis_mcp_agent.ipynb

notebooks/               ← Production pipeline notebooks
├── 01_ingest_to_bronze.py
├── 02_bronze_to_silver.py
├── 03_silver_to_gold.py
├── 04_create_uc_functions.py
└── 05_upload_knowledge_docs.py
```

## 🧪 Available Test Notebooks

### `test_hedis_mcp_agent.ipynb`

**Test the HEDIS MCP Agent interactively without Streamlit UI**

**Use cases:**
- Quick agent testing
- Debugging MCP components
- Experimenting with queries
- Performance testing
- Learning how the agent works

**What it tests:**
1. ✅ System status check
2. ✅ Member queries (UC Functions)
3. ✅ Gap analysis queries (UC Functions)
4. ✅ Genie analytics queries
5. ✅ Knowledge Assistant queries
6. ✅ Conversation history
7. ✅ Individual MCP client testing
8. ✅ Performance benchmarking

**How to use:**
```bash
# Option 1: Open in Jupyter
cd test_notebooks
jupyter notebook test_hedis_mcp_agent.ipynb

# Option 2: Open in VS Code
code test_hedis_mcp_agent.ipynb

# Option 3: Open in JupyterLab
jupyter lab test_hedis_mcp_agent.ipynb
```

## 🚀 Quick Start

1. **Install Jupyter** (if not already installed):
```bash
pip install jupyter notebook
```

2. **Navigate to test_notebooks**:
```bash
cd test_notebooks
```

3. **Start Jupyter**:
```bash
jupyter notebook
```

4. **Open `test_hedis_mcp_agent.ipynb`** and run cells sequentially

## 📋 Prerequisites

- Databricks workspace configured (uses `~/.databrickscfg`)
- HEDIS project deployed with MCP components
- Python environment with required packages

## 🔧 Configuration

Update these values in the notebook to match your environment:
```python
GENIE_SPACE_ID = "your-genie-space-id"
CATALOG = "your_catalog"
SCHEMA = "your_schema"
KNOWLEDGE_ASSISTANT_ENDPOINT_ID = "your-ka-endpoint"
```

## ⚠️ Important Notes

**These notebooks are for testing only:**
- ✅ Use for development and debugging
- ✅ Use for learning and experimentation
- ❌ Not included in Databricks bundle deployment
- ❌ Not run by CI/CD pipelines

**The notebooks import production code:**
- Imports `hedis_agent.py` from `dashboard/` folder
- Tests the **same code** used in production
- Changes to agent code are immediately reflected

## 🎯 Benefits

| Aspect | Streamlit Dashboard | Test Notebook |
|--------|---------------------|---------------|
| **Speed** | Slower (UI + agent) | Faster (agent only) |
| **Debugging** | Limited | Full Python debugging |
| **Iteration** | Restart app | Re-run cells |
| **Experimentation** | Limited | Unlimited |
| **Access** | Needs deployment | Local or Databricks |

## 💡 Tips

**Quick testing workflow:**
1. Open `test_hedis_mcp_agent.ipynb`
2. Run setup cells (1-3)
3. Run initialization (4)
4. Jump to specific test section
5. Modify queries and re-run

**Debugging workflow:**
1. Test fails in Streamlit dashboard
2. Open test notebook
3. Run same query in notebook
4. Add print statements
5. Debug issue
6. Fix in `hedis_agent.py`
7. Re-run notebook cell to verify

## 🔗 Related Files

- **Agent code:** `../dashboard/hedis_agent.py`
- **MCP clients:** `../dashboard/mcp_*.py`
- **Configuration:** `../dashboard/config.py`
- **Production app:** `../dashboard/hedis_quality_dashboard.py`

## 📚 Additional Resources

- **MY_ENVIRONMENT.md** - Complete MCP implementation pattern
- **MCP_IMPLEMENTATION_SUMMARY.md** - Working pattern summary
- **GitHub reference:** https://github.com/bigdatavik/healthcare-payor-ai-mcp.git

---

**Last Updated:** October 26, 2025
**Status:** Production-ready testing notebooks ✅

