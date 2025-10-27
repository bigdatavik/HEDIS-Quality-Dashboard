"""
Unity Catalog Functions MCP Server Integration - HEDIS Quality Dashboard

This module provides integration with Unity Catalog Functions via Model Context Protocol (MCP).
It allows the AI agent to call custom SQL functions defined in Unity Catalog.
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, create_model

class UCFunctionsMCPClient:
    """Client for interacting with Unity Catalog Functions managed MCP server"""
    
    def __init__(self, workspace_hostname: str, catalog: str, schema: str, workspace_client: WorkspaceClient):
        """
        Initialize UC Functions MCP client
        
        Args:
            workspace_hostname: Databricks workspace hostname
            catalog: Unity Catalog name
            schema: Schema name containing UC functions
            workspace_client: WorkspaceClient instance
        """
        self.workspace_hostname = workspace_hostname
        self.catalog = catalog
        self.schema = schema
        self.workspace_client = workspace_client
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/functions/{catalog}/{schema}"
        
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
            # Successfully connected to UC Functions MCP
            pass
        except Exception as e:
            st.error(f"❌ Failed to connect to UC Functions MCP server: {e}")
            self.mcp_client = None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available UC functions from MCP server"""
        if not self.mcp_client:
            return []
        
        try:
            tools = self.mcp_client.list_tools()
            return [{"name": tool.name, "description": tool.description, "parameters": tool.inputSchema.get("properties", {}) if hasattr(tool, 'inputSchema') else {}} for tool in tools]
        except Exception as e:
            st.error(f"❌ Failed to list UC Functions tools: {e}")
            return []
    
    def call_uc_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a UC Function through MCP server
        
        Args:
            function_name: Name of the UC function to call
            **kwargs: Arguments for the function
            
        Returns:
            Dictionary containing function results
        """
        if not self.mcp_client:
            return {
                "success": False,
                "error": "MCP client not initialized",
                "function_name": function_name,
                "parameters": kwargs,
                "tool_used": "UC Functions MCP"
            }
        
        try:
            result = self.mcp_client.call_tool(function_name, kwargs)
            
            return {
                "success": True,
                "function_name": function_name,
                "parameters": kwargs,
                "result": result.content if hasattr(result, 'content') else str(result),
                "tool_used": "UC Functions MCP"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "function_name": function_name,
                "parameters": kwargs,
                "tool_used": "UC Functions MCP"
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status of UC Functions MCP connection"""
        try:
            tools = self.list_tools()
            return {
                "status": "healthy" if tools else "unhealthy",
                "mcp_url": self.mcp_url,
                "tools_count": len(tools),
                "tools": [tool["name"] for tool in tools]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "mcp_url": self.mcp_url,
                "tools_count": 0,
                "tools": []
            }

def create_uc_functions_tools_for_langchain(uc_functions_client: UCFunctionsMCPClient) -> List[BaseTool]:
    """
    Create LangChain tool wrappers for all discovered UC Functions.
    
    Args:
        uc_functions_client: Initialized UCFunctionsMCPClient instance
        
    Returns:
        List of LangChain tools for UC functions
    """
    tools = []
    for func_info in uc_functions_client.list_tools():
        func_name = func_info['name']
        func_description = func_info['description']
        func_parameters = func_info.get('parameters', {})
        
        # Dynamically create Pydantic model for function arguments
        if func_parameters:
            fields = {
                param_name: (str, Field(description=details.get('description', '')))
                for param_name, details in func_parameters.items()
            }
            DynamicInputModel = create_model(f"{func_name.replace('-', '_').capitalize()}Input", **fields)
        else:
            # No parameters - use empty model
            DynamicInputModel = create_model(f"{func_name.replace('-', '_').capitalize()}Input")
        
        class UCFuncTool(BaseTool):
            name: str = func_name
            description: str = func_description
            args_schema: type[BaseModel] = DynamicInputModel
            
            def _run(self, **kwargs) -> str:
                """Execute the UC Function through MCP server"""
                result = uc_functions_client.call_uc_function(self.name, **kwargs)
                if result["success"]:
                    return f"UC Function '{self.name}' Result:\n{result['result']}"
                else:
                    return f"Error calling UC Function '{self.name}': {result['error']}"
        
        tools.append(UCFuncTool())
    
    return tools
