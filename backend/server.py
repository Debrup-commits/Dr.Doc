#!/usr/bin/env python3
"""
Server module for uAgent integration

This module provides the server interface expected by the uagents-adapter.
It wraps the MCP server to provide the required list_tools and call_tool methods.

Author: Dr.Doc Team
"""

import asyncio
import logging
from typing import List, Dict, Any

# Import the MCP server
from mcp_server import mcp
from rag_initializer import initialize_rag_system, get_rag_system, get_metta_kb

logger = logging.getLogger(__name__)

# Initialize RAG system for the server wrapper
def initialize_server_rag():
    """Initialize RAG system for the server wrapper"""
    try:
        logger.info("Initializing RAG system for server wrapper...")
        rag_system = initialize_rag_system()
        
        # Update the global RAG system in mcp_server
        import mcp_server
        mcp_server.rag_system = rag_system
        mcp_server.metta_kb = get_metta_kb()
        
        logger.info("RAG system initialized for server wrapper")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        return False

# Initialize RAG system when server wrapper is created
initialize_server_rag()

class MCPServerWrapper:
    """Wrapper for MCP server to provide uAgent-compatible interface"""
    
    def __init__(self):
        self.mcp_server = mcp
        logger.info("MCP Server wrapper initialized")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server"""
        try:
            # Get tools from the MCP server
            tools = []
            
            # Add process_documents tool
            tools.append({
                "name": "process_documents",
                "description": "Process documents from a directory path (idempotent)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "docs_dir_path": {
                            "type": "string",
                            "description": "Path to the directory containing documents to process"
                        }
                    },
                    "required": ["docs_dir_path"]
                }
            })
            
            # Add ask_dr_doc tool
            tools.append({
                "name": "ask_dr_doc",
                "description": "Ask questions to Dr.Doc agent with RAG and MeTTa integration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask Dr.Doc"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional session ID for conversation continuity",
                            "default": "default_session"
                        }
                    },
                    "required": ["question"]
                }
            })
            
            logger.info(f"Listed {len(tools)} tools")
            return tools
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            if name == "process_documents":
                docs_dir_path = arguments.get("docs_dir_path", "")
                result = await mcp.call_tool("process_documents", {"docs_dir_path": docs_dir_path})
                return {
                    "success": True,
                    "result": result,
                    "tool": name
                }
            
            elif name == "ask_dr_doc":
                question = arguments.get("question", "")
                session_id = arguments.get("session_id", "default_session")
                result = await mcp.call_tool("ask_dr_doc", {
                    "question": question,
                    "session_id": session_id
                })
                return {
                    "success": True,
                    "result": result,
                    "tool": name
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {name}",
                    "tool": name
                }
                
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": name
            }

# Create the server instance
server = MCPServerWrapper()

# Export the MCP server instance for the adapter
mcp = mcp
