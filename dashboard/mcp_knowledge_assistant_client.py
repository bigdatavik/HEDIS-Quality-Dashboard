"""
Knowledge Assistant Integration - HEDIS Quality Dashboard

This module provides integration with Databricks Knowledge Assistant.
It enables semantic search over HEDIS documentation with automatic citations.
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
import streamlit as st
from openai import OpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class KnowledgeAssistantQueryInput(BaseModel):
    query: str = Field(description="Natural language query for knowledge base search")

class KnowledgeAssistantMCPClient:
    """Client for Knowledge Assistant functionality"""
    
    def __init__(self, knowledge_assistant_endpoint_id: str, workspace_client: WorkspaceClient):
        """
        Initialize Knowledge Assistant client
        
        Args:
            knowledge_assistant_endpoint_id: Knowledge Assistant endpoint ID
            workspace_client: Databricks workspace client
        """
        self.knowledge_assistant_endpoint_id = knowledge_assistant_endpoint_id
        self.workspace_client = workspace_client
        self.knowledge_client = None
        self._setup_knowledge_client()
    
    def _setup_knowledge_client(self):
        """Setup the Knowledge Assistant client using token generation"""
        try:
            # Generate a token using the Databricks client
            import time
            token = self.workspace_client.tokens.create(
                comment=f"knowledge-assistant-{time.time_ns()}", 
                lifetime_seconds=3600
            )
            
            # Get workspace hostname
            workspace_hostname = self.workspace_client.config.host
            
            # Initialize OpenAI client for Knowledge Assistant
            self.knowledge_client = OpenAI(
                api_key=token.token_value,
                base_url=f"{workspace_hostname}/serving-endpoints"
            )
            
            # Store token info for cleanup
            self._token_info = token.token_info
            # Successfully initialized Knowledge Assistant client
            
        except Exception as e:
            st.warning(f"⚠️ Failed to setup Knowledge Assistant client: {e}")
            self.knowledge_client = None
    
    def query_knowledge(self, query: str) -> Dict[str, Any]:
        """
        Query Knowledge Assistant for unstructured text analysis
        
        Args:
            query: Natural language query for knowledge analysis
            
        Returns:
            Dictionary containing query results
        """
        if not self.knowledge_client:
            return {
                "success": False,
                "error": "Knowledge Assistant client not initialized",
                "query": query,
                "tool_used": "Knowledge Assistant"
            }
        
        try:
            # Use the OpenAI client to query the Knowledge Assistant
            response = self.knowledge_client.responses.create(
                model=self.knowledge_assistant_endpoint_id,
                input=[
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            )
            
            if response.output and len(response.output) > 0:
                return {
                    "success": True,
                    "query": query,
                    "result": response.output[0].content[0].text,
                    "tool_used": "Knowledge Assistant"
                }
            else:
                return {
                    "success": False,
                    "error": "No response from Knowledge Assistant",
                    "query": query,
                    "tool_used": "Knowledge Assistant"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "tool_used": "Knowledge Assistant"
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status of Knowledge Assistant connection"""
        try:
            return {
                "status": "healthy" if self.knowledge_client else "unhealthy",
                "endpoint": self.knowledge_assistant_endpoint_id,
                "client_initialized": self.knowledge_client is not None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "endpoint": self.knowledge_assistant_endpoint_id
            }

def create_knowledge_assistant_tool_for_langchain(knowledge_client: KnowledgeAssistantMCPClient):
    """
    Create a LangChain tool wrapper for Knowledge Assistant
    
    Args:
        knowledge_client: Initialized KnowledgeAssistantMCPClient instance
        
    Returns:
        LangChain tool for Knowledge Assistant queries
    """
    class KnowledgeAssistantMCPTool(BaseTool):
        name: str = Field(default="knowledge_assistant_query")
        description: str = Field(default="""Search and retrieve information from the HEDIS knowledge base.
        Use this tool to answer questions about HEDIS compliance requirements, NCQA guidelines, 
        gap closure protocols, and quality improvement processes.
        It provides answers with citations from the relevant knowledge documents.""")
        args_schema: type[BaseModel] = KnowledgeAssistantQueryInput
        
        def _run(self, query: str) -> str:
            """Execute Knowledge Assistant query"""
            result = knowledge_client.query_knowledge(query)
            
            if result["success"]:
                return f"Knowledge Assistant Result:\n{result['result']}"
            else:
                return f"Error querying Knowledge Assistant: {result['error']}"
    
    return KnowledgeAssistantMCPTool()
