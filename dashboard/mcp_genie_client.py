"""
Genie MCP Server Integration - HEDIS Quality Dashboard

This module provides integration with Databricks Genie via Model Context Protocol (MCP).
It allows the AI agent to query HEDIS quality data using natural language.
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class GenieQueryInput(BaseModel):
    query: str = Field(description="Natural language query for Genie space")

class GenieMCPClient:
    """Client for interacting with Genie managed MCP server"""
    
    def __init__(self, workspace_hostname: str, genie_space_id: str, workspace_client: WorkspaceClient):
        """
        Initialize Genie MCP client
        
        Args:
            workspace_hostname: Databricks workspace hostname
            genie_space_id: Genie space ID
            workspace_client: WorkspaceClient instance
        """
        self.workspace_hostname = workspace_hostname
        self.genie_space_id = genie_space_id
        self.workspace_client = workspace_client
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/genie/{genie_space_id}"
        
        # Initialize MCP client
        self.mcp_client = None
        self._initialize_mcp_client()
    
    def _initialize_mcp_client(self):
        """Initialize the MCP client connection"""
        try:
            self.mcp_client = DatabricksMCPClient(
                server_url=self.mcp_url,
                workspace_client=self.workspace_client
            )
            # Successfully connected to Genie MCP
            pass
        except Exception as e:
            st.error(f"❌ Failed to connect to Genie MCP server: {e}")
            self.mcp_client = None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from Genie MCP server"""
        if not self.mcp_client:
            return []
        
        try:
            tools = self.mcp_client.list_tools()
            return [{"name": tool.name, "description": tool.description} for tool in tools]
        except Exception as e:
            # Known issue: Genie MCP may not support list_tools() reliably
            # Return a default tool definition instead
            st.warning(f"⚠️ Could not list Genie tools (known limitation): {e}")
            return [{"name": "genie_query", "description": "Query data using natural language through Genie"}]
    
    def query_genie(self, query: str) -> Dict[str, Any]:
        """
        Query Genie space using natural language via MCP protocol
        
        Args:
            query: Natural language query for Genie
            
        Returns:
            Dictionary containing query results
        """
        if not self.mcp_client:
            return {
                "success": False,
                "error": "MCP client not initialized",
                "query": query,
                "tool_used": "Genie MCP"
            }
        
        try:
            # Use the genie_query tool from MCP server
            result = self.mcp_client.call_tool("genie_query", {"query": query})
            
            return {
                "success": True,
                "query": query,
                "result": result.content if hasattr(result, 'content') else str(result),
                "tool_used": "Genie MCP"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "tool_used": "Genie MCP"
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status of Genie MCP connection"""
        try:
            # Check if MCP client is initialized (connection successful)
            if self.mcp_client:
                # Don't rely on list_tools() for health check due to known async issues
                return {
                    "status": "healthy",
                    "mcp_url": self.mcp_url,
                    "tools_count": 1,
                    "tools": ["genie_query"]
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "MCP client not initialized",
                    "mcp_url": self.mcp_url,
                    "tools_count": 0,
                    "tools": []
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "mcp_url": self.mcp_url,
                "tools_count": 0,
                "tools": []
            }

def create_genie_tool_for_langchain(genie_client: GenieMCPClient):
    """
    Create a LangChain tool wrapper for Genie MCP client
    
    Args:
        genie_client: Initialized GenieMCPClient instance
        
    Returns:
        LangChain tool for Genie queries
    """
    class GenieMCPTool(BaseTool):
        name: str = Field(default="genie_mcp_query")
        description: str = Field(default="""Query structured data using natural language through Genie MCP server. 
        Use this tool to analyze HEDIS quality data, get insights, and answer questions about structured data tables.
        This tool connects to the managed Genie MCP server for advanced data analysis.""")
        args_schema: type[BaseModel] = GenieQueryInput
        
        def _run(self, query: str) -> str:
            """Execute Genie query through MCP server"""
            result = genie_client.query_genie(query)
            
            if result["success"]:
                return f"Genie Analysis:\n{result['result']}"
            else:
                return f"Error querying Genie: {result['error']}"
    
    return GenieMCPTool()
