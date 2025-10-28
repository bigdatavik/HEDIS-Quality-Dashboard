# Knowledge Assistant - UI Field Values

## Copy-Paste These Values When Creating Knowledge Assistant Endpoint

---

### 📝 Name Field:
```
hedis_quality_knowledge_assistant
```

---

### 📝 Description Field:
```
Answers questions about HEDIS quality measures, NCQA compliance requirements, gap closure procedures, and quality improvement guidelines. Provides policy interpretations, measure specifications, and operational best practices for the quality analytics team.
```

---

### 📝 Source Field:
**Type:** UC Files

**Path:** Click folder icon and navigate to:
```
/Volumes/humana_quality/hedis_gold/knowledge_docs
```

---

### 📝 "Describe the content" Field (CRITICAL - Paste this entire block):

```
This knowledge base contains comprehensive documentation for HEDIS quality measures analytics:

1. Agent Knowledge Source Guide - Explains which data sources (Genie, UC Functions, Knowledge Assistant) to use for different types of questions. Includes decision trees and best practices for selecting the right tool based on query type.

2. Knowledge Source Descriptions - Detailed documentation of each Unity Catalog Function with parameters, return values, example use cases, and performance characteristics. Explains when to use Genie Space versus UC Functions for different analytical needs.

3. HEDIS Policies and Guidelines - Complete specifications for all HEDIS measures including BCS (Breast Cancer Screening), CDC (Comprehensive Diabetes Care), CBP (Controlling Blood Pressure), COL (Colorectal Cancer Screening), and OMW (Osteoporosis Management). Covers measure definitions, target populations, compliance requirements, exclusion criteria, gap closure procedures, NCQA compliance standards, star rating calculations, and revenue impact methodology.

4. FAQ Documentation - Common questions and answers about member lookups, measure performance queries, gap closure procedures, compliance rate calculations, data refresh timing, and troubleshooting common issues.

Use this knowledge base to answer questions about: HEDIS measure specifications, NCQA requirements, gap closure procedures, compliance thresholds, star rating calculations, documentation standards, quality improvement strategies, revenue impact analysis, and operational best practices.
```

---

### 📝 Advanced Settings (Optional):
- **Embedding model:** Default (keep as-is)
- **Chunk size:** 512 (default)
- **Chunk overlap:** 50 (default)

---

## ✅ After Creating Endpoint:

1. Wait 5-10 minutes for status to change from PROVISIONING → READY
2. Copy the **Endpoint ID** (format: `ka-XXXXX-endpoint`)
3. Save the Endpoint ID for MCP integration

---

## 🔐 IMPORTANT: Grant Permissions After Creation

After the endpoint is READY, run this Python script to grant permissions:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Your endpoint name
endpoint_name = "hedis_quality_knowledge_assistant"

# Get endpoint UUID
endpoint = w.serving_endpoints.get(endpoint_name)
endpoint_id = endpoint.id

# Grant CAN_QUERY permission to all users
w.api_client.do(
    "PATCH",
    f"/api/2.0/permissions/serving-endpoints/{endpoint_id}",
    body={
        "access_control_list": [
            {
                "group_name": "users",
                "permission_level": "CAN_QUERY"
            }
        ]
    }
)

print(f"✅ Permissions granted to endpoint: {endpoint_name}")
```

---

## 📋 Testing the Endpoint

After creation and permission grant, test with:

```python
from databricks.sdk import WorkspaceClient
import time

w = WorkspaceClient()

# Generate token
token = w.tokens.create(
    comment=f"knowledge-assistant-test-{time.time_ns()}",
    lifetime_seconds=3600
)

# Create OpenAI client
from openai import OpenAI
client = OpenAI(
    api_key=token.token_value,
    base_url=f"{w.config.host}/serving-endpoints"
)

# Test query
response = client.responses.create(
    model="hedis_quality_knowledge_assistant",
    input=[{"role": "user", "content": "What is the BCS measure?"}]
)

print(response.output[0].content[0].text)
```

Expected response: Detailed explanation of Breast Cancer Screening measure with requirements and target population.

