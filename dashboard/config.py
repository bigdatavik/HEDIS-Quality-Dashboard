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
CATALOG = "humana_quality"
SCHEMA = "hedis_gold"

# MCP Service IDs (configured for HEDIS Quality Dashboard)
GENIE_SPACE_ID = "01f0b223e0e31cb0b4b093ef8578bcf8"
KNOWLEDGE_ASSISTANT_ENDPOINT_ID = "ka-0bbaf97e-endpoint"

# AI Model configuration - Foundation Model Endpoint
# Use 8b model for faster responses and lower cost
AI_MODEL_NAME = "databricks-meta-llama-3-1-8b-instruct"
# Alternative: "databricks-meta-llama-3-1-70b-instruct" (larger, more capable)

# SQL Warehouse for Genie queries
SQL_WAREHOUSE_ID = "148ccb90800933a1"

