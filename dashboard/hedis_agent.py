"""
HEDIS Quality Agent - Using Working MCP Pattern

This agent follows the proven pattern from healthcare-payor-ai-mcp-1.
Uses manual tool calling with OpenAI client instead of LangChain AgentExecutor.
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
import streamlit as st

# Import MCP clients
from mcp_genie_client import GenieMCPClient, create_genie_tool_for_langchain
from mcp_uc_functions_client import UCFunctionsMCPClient, create_uc_functions_tools_for_langchain
from mcp_knowledge_assistant_client import KnowledgeAssistantMCPClient, create_knowledge_assistant_tool_for_langchain


class HEDISQualityAgent:
    """HEDIS Quality Agent using Manual Tool Calling Pattern"""
    
    def __init__(
        self,
        genie_space_id: str,
        catalog: str,
        schema: str,
        knowledge_assistant_endpoint_id: Optional[str] = None,
        ai_model_name: str = "databricks-meta-llama-3-1-8b-instruct"
    ):
        """
        Initialize HEDIS Quality Agent
        
        Args:
            genie_space_id: Genie Space ID
            catalog: Unity Catalog name
            schema: Schema name (hedis_gold)
            knowledge_assistant_endpoint_id: Optional Knowledge Assistant endpoint ID
            ai_model_name: AI model name for the agent
        """
        self.genie_space_id = genie_space_id
        self.catalog = catalog
        self.schema = schema
        self.knowledge_assistant_endpoint_id = knowledge_assistant_endpoint_id
        self.ai_model_name = ai_model_name
        
        # Initialize clients
        self.workspace_client = None
        self.genie_client = None
        self.uc_functions_client = None
        self.knowledge_assistant_client = None
        self.tools = []
        self.llm_client = None
        self.memory = []
        
        # Setup
        self._setup_clients()
        self._setup_tools()
        self._setup_llm()
    
    def _setup_clients(self):
        """Setup MCP clients"""
        try:
            # Initialize workspace client
            self.workspace_client = WorkspaceClient()
            
            # Get workspace hostname
            workspace_host = self.workspace_client.config.host
            if workspace_host.startswith("https://"):
                workspace_host = workspace_host.replace("https://", "")
            
            # Initialize Genie MCP client
            self.genie_client = GenieMCPClient(
                workspace_hostname=workspace_host,
                genie_space_id=self.genie_space_id,
                workspace_client=self.workspace_client
            )
            
            # Initialize UC Functions MCP client
            self.uc_functions_client = UCFunctionsMCPClient(
                workspace_hostname=workspace_host,
                catalog=self.catalog,
                schema=self.schema,
                workspace_client=self.workspace_client
            )
            
            # Initialize Knowledge Assistant client (if endpoint provided)
            if self.knowledge_assistant_endpoint_id:
                self.knowledge_assistant_client = KnowledgeAssistantMCPClient(
                    knowledge_assistant_endpoint_id=self.knowledge_assistant_endpoint_id,
                    workspace_client=self.workspace_client
                )
            
        except Exception as e:
            print(f"❌ Failed to setup MCP clients: {e}")
            raise
    
    def _setup_tools(self):
        """Setup tools from MCP servers"""
        self.tools = []
        
        try:
            # Add Genie MCP tool
            if self.genie_client and self.genie_client.mcp_client:
                genie_tool = create_genie_tool_for_langchain(self.genie_client)
                self.tools.append(genie_tool)
            
            # Add UC Functions MCP tools
            if self.uc_functions_client and self.uc_functions_client.mcp_client:
                uc_tools = create_uc_functions_tools_for_langchain(self.uc_functions_client)
                self.tools.extend(uc_tools)
            
            # Add Knowledge Assistant tool
            if self.knowledge_assistant_client and self.knowledge_assistant_client.knowledge_client:
                knowledge_tool = create_knowledge_assistant_tool_for_langchain(self.knowledge_assistant_client)
                self.tools.append(knowledge_tool)
                
        except Exception as e:
            st.error(f"❌ Failed to setup tools: {e}")
    
    def _setup_llm(self):
        """Setup LLM client using Databricks Serving Endpoints"""
        try:
            # Use the OpenAI-compatible client from Databricks SDK
            self.llm_client = self.workspace_client.serving_endpoints.get_open_ai_client()
            
            # Create tool mapping
            self.tool_map = {tool.name: tool for tool in self.tools}
            
        except Exception as e:
            st.error(f"❌ Failed to setup LLM: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    def chat(self, user_input: str, chat_history: List[Dict[str, str]]) -> str:
        """
        Chat with the agent using manual tool calling pattern
        
        Args:
            user_input: User's query
            chat_history: Previous conversation history
            
        Returns:
            Agent's response
        """
        try:
            if not self.llm_client:
                return "❌ Agent not initialized - LLM client is unavailable."
            
            # Convert tools to OpenAI format
            openai_tools = []
            for tool in self.tools:
                tool_spec = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.args_schema.model_json_schema() if hasattr(tool.args_schema, 'model_json_schema') else {}
                    }
                }
                openai_tools.append(tool_spec)
            
            # Prepare system message
            system_prompt = """You are a Healthcare Quality Measures Assistant for HEDIS compliance tracking.
            
Your role:
1. Help the Quality team track NCQA compliance and improve HEDIS scores
2. Provide accurate, concise, and actionable information
3. Present data in clear, readable formats
4. Use appropriate tools for different types of queries

Available tools:
- genie_mcp_query: For data analysis, trends, and aggregated metrics from structured data
- UC Functions (lookup_member, lookup_member_measures, lookup_member_gaps, etc.): For specific member/measure lookups
- knowledge_assistant_query: For HEDIS compliance requirements, NCQA guidelines, and policies

Guidelines:
- Use the most specific tool first
- For member-specific queries, use UC Functions
- For data analysis and trends, use Genie
- For policy/guideline questions, use Knowledge Assistant
- Present results clearly without technical jargon
- Be helpful and professional"""
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 10 messages)
            for msg in chat_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_input})
            
            # Call LLM with tools
            response = self.llm_client.chat.completions.create(
                model=self.ai_model_name,
                messages=messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None
            )
            
            message = response.choices[0].message
            
            # Handle tool calls
            if message.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if tool_name in self.tool_map:
                        try:
                            tool = self.tool_map[tool_name]
                            result = tool._run(**tool_args)
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_name,
                                "content": str(result)
                            })
                        except Exception as e:
                            # User-friendly error messages
                            if "genie" in tool_name.lower():
                                error_msg = f"Genie analysis temporarily unavailable. Please try rephrasing your query."
                            elif "lookup" in tool_name.lower() or "uc" in tool_name.lower():
                                error_msg = f"Unable to retrieve data from UC Functions. The data may not exist or is temporarily unavailable."
                            elif "knowledge" in tool_name.lower():
                                error_msg = f"Knowledge Assistant search unavailable. Please try a different query."
                            else:
                                error_msg = f"Tool temporarily unavailable: {str(e)}"
                            
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_name,
                                "content": error_msg
                            })
                    else:
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": f"Tool {tool_name} not found"
                        })
                
                # Add tool results to conversation
                messages.extend(tool_results)
                
                # Get final response
                final_response = self.llm_client.chat.completions.create(
                    model=self.ai_model_name,
                    messages=messages
                )
                
                return final_response.choices[0].message.content or "No response generated."
            else:
                # Direct response without tool calls
                return message.content or "No response generated."
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"❌ Error processing query: {str(e)}\n\nDetails:\n{error_details}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the health status of all integrated MCP components"""
        status = {
            "llm_ready": self.llm_client is not None,
            "tools_count": len(self.tools),
            "genie": self.genie_client.get_health_status() if self.genie_client else {"status": "not_configured"},
            "uc_functions": self.uc_functions_client.get_health_status() if self.uc_functions_client else {"status": "not_configured"},
            "knowledge_assistant": self.knowledge_assistant_client.get_health_status() if self.knowledge_assistant_client else {"status": "not_configured"}
        }
        return status
