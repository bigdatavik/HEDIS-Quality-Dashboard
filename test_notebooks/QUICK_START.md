# Quick Start: Testing HEDIS MCP Agent

**NEW!** You can now test the HEDIS MCP Agent interactively without the Streamlit UI!

## 🚀 How to Use

### Option 1: Jupyter Notebook (Recommended)

```bash
# Navigate to test_notebooks folder
cd test_notebooks

# Start Jupyter
jupyter notebook

# Open test_hedis_mcp_agent.ipynb
```

### Option 2: VS Code

```bash
# Open in VS Code
code test_hedis_mcp_agent.ipynb
```

### Option 3: JupyterLab

```bash
cd test_notebooks
jupyter lab
```

---

## 📖 What's in the Notebook?

### **Section 1-3: Setup** (Run these first)
- Adds dashboard folder to Python path
- Imports required libraries
- Sets configuration

### **Section 4: System Status**
- Check if all MCP components are working
- Shows LLM, Genie, UC Functions, Knowledge Assistant status

### **Section 5: Test Member Query**
- Pre-configured query: "Show me member M000001's quality metrics"
- Tests UC Functions

### **Section 6: Interactive Testing** ⭐ USE THIS!
- **Modify the query and re-run**
- Test your own questions
- Quick iteration

### **Section 7: Quick Reference**
- List of example queries to try
- Copy-paste examples

---

## 💡 Quick Testing Workflow

1. **Run cells 1-8** (setup and initialize agent) - **DO THIS ONCE**
2. **Jump to cell 14** (Section 6 - Interactive Testing)
3. **Change `your_query` variable**
4. **Re-run cell 14**
5. **Repeat steps 3-4** for different queries

**Example:**
```python
# Cell 14 - Change this line:
your_query = "Which members have gaps in diabetes care?"

# Run the cell (Shift+Enter)
# See the response immediately!
```

---

## 🎯 Common Use Cases

### Quick Testing
```python
# After running setup (cells 1-8), just modify and run cell 14:
your_query = "Show me member M000050's gaps"
# Run cell → See result → Change query → Run again
```

### Debugging
```python
# Add debug prints in cell 14:
response = agent.chat(your_query, [])
print(f"Response type: {type(response)}")
print(f"Response length: {len(response)}")
print(response)
```

### Performance Testing
```python
# Add timing in cell 14:
import time
start = time.time()
response = agent.chat(your_query, [])
print(f"⏱️ Time: {time.time() - start:.2f}s")
print(response)
```

---

## 📚 Example Queries

**Copy any of these to cell 14:**

### Member Queries (UC Functions)
```python
your_query = "Show me member M000001's quality metrics"
your_query = "What are M000100's open gaps?"
your_query = "Get all measures for member M000050"
```

### Gap Analysis (UC Functions)
```python
your_query = "Which members have open BCS gaps?"
your_query = "Show members with gaps in diabetes care"
your_query = "List all at-risk members"
```

### Analytics (Genie MCP)
```python
your_query = "What's the performance trend for CDC measure?"
your_query = "Show quality scores by year"
your_query = "What's the total member enrollment?"
```

### Knowledge (Knowledge Assistant)
```python
your_query = "What are the HEDIS compliance requirements?"
your_query = "Explain the gap closure protocol"
your_query = "What is the NCQA audit process?"
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'hedis_agent'"

**Solution:** Run cell 2 first (adds dashboard to path)

### Issue: Agent initialization fails

**Solution:** 
1. Check configuration in cell 5
2. Verify Databricks workspace is accessible
3. Check `~/.databrickscfg` has DEFAULT profile

### Issue: "No module named 'databricks_mcp'"

**Solution:** Install dependencies:
```bash
cd ../dashboard
pip install -r requirements.txt
```

---

## 📊 Benefits vs Streamlit Dashboard

| Aspect | Streamlit | Test Notebook |
|--------|-----------|---------------|
| **Speed** | Slower | Faster ⚡ |
| **Iteration** | Restart app | Re-run cell ⚡ |
| **Debugging** | Limited | Full Python debugging ⚡ |
| **Experimentation** | Limited | Unlimited ⚡ |
| **Setup** | Need deployment | Just run cells ⚡ |

---

## 🔗 Key Points

✅ **Same code as production** - Imports `dashboard/hedis_agent.py`  
✅ **No deployment needed** - Run locally  
✅ **Fast iteration** - Change query, re-run cell  
✅ **Great for learning** - See how the agent works  
✅ **Perfect for debugging** - Add print statements anywhere  

---

## 📁 Files Created

```
test_notebooks/
├── test_hedis_mcp_agent.ipynb   ← Main test notebook
├── README.md                     ← Detailed documentation
└── QUICK_START.md                ← This file
```

---

**Ready to test?** Open `test_hedis_mcp_agent.ipynb` and run cells 1-8, then jump to cell 14!

🎯 **Pro tip:** Keep cell 14 open and just modify the query - fastest way to test! ⚡

