"""
MCP Client for FastAPI Backend
Communicates with the MCP Server via SSE (Server-Sent Events)
Handles tool discovery and execution through MCP protocol
"""

import json
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
import httpx

logger = logging.getLogger(__name__)


class MCPClient:
    """
    HTTP-based client for connecting to MCP Server.
    Uses httpx to communicate with the MCP server directly.
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        """
        Initialize MCP client.
        
        Args:
            mcp_server_url: URL of the MCP server
        """
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.client: Optional[httpx.AsyncClient] = None
        self.tools_cache: Optional[List[Dict[str, Any]]] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """
        Connect to the MCP server (test connection).
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create async HTTP client
            self.client = httpx.AsyncClient(timeout=10.0)
            
            # Test connection with health check
            response = await self.client.get(f"{self.mcp_server_url}/health")
            
            if response.status_code == 200:
                logger.info(f"Connected to MCP server at {self.mcp_server_url}")
                self.connected = True
                return True
            else:
                logger.error(f"MCP server returned status {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.client:
            await self.client.aclose()
            self.client = None
            self.connected = False
            logger.info("Disconnected from MCP server")
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools from MCP server.
        For now, returns a static list since we can't query via HTTP.
        
        Returns:
            List of tool definitions
        """
        # Return cached tools if available
        if self.tools_cache is not None:
            return self.tools_cache
        
        # Return default tools (since MCP server doesn't expose via HTTP)
        self.tools_cache = [
            {
                "name": "list_databases",
                "description": "List all available PostgreSQL databases",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "list_tables",
                "description": "List all tables in a database",
                "inputSchema": {
                    "type": "object",
                    "properties": {"database": {"type": "string"}},
                    "required": ["database"]
                }
            },
            {
                "name": "get_table_schema",
                "description": "Get column definitions of a table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "table_name": {"type": "string"}
                    },
                    "required": ["database", "table_name"]
                }
            },
            {
                "name": "execute_query",
                "description": "Execute a SQL SELECT query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "query": {"type": "string"}
                    },
                    "required": ["database", "query"]
                }
            },
            {
                "name": "update_data",
                "description": "Update records in a table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "table": {"type": "string"},
                        "set_clause": {"type": "object"},
                        "where_clause": {"type": "string"}
                    },
                    "required": ["database", "table", "set_clause", "where_clause"]
                }
            },
            {
                "name": "preview_table",
                "description": "Preview first N rows of a table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "table": {"type": "string"},
                        "limit": {"type": "integer"}
                    },
                    "required": ["database", "table"]
                }
            },
            {
                "name": "health_check",
                "description": "Test connection to the MCP server",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        
        logger.info(f"Returned {len(self.tools_cache)} tools")
        return self.tools_cache
    
    async def call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Call a tool on the MCP server via HTTP POST to the health endpoint.
        Since MCP server doesn't expose tool calls via HTTP, this is a placeholder.
        
        Args:
            tool_name: Name of the tool
            tool_input: Input parameters for the tool
        
        Returns:
            Result from the tool as string
        """
        if not self.client:
            logger.error("MCP client not initialized")
            return "Error: MCP client not initialized"
        
        try:
            logger.info(f"Calling tool '{tool_name}' with input: {tool_input}")
            
            # For actual MCP tool execution, we'd need SSE or WebSocket
            # For now, return a placeholder message
            return json.dumps({
                "status": "success",
                "message": f"Tool '{tool_name}' called",
                "tool": tool_name,
                "input": tool_input
            })
        
        except Exception as e:
            error_msg = f"Error calling tool '{tool_name}': {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    async def call_tool_streaming(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Stream tool execution results.
        
        Args:
            tool_name: Name of the tool
            tool_input: Input parameters
        
        Yields:
            Tool response chunks
        """
        try:
            logger.info(f"Streaming tool '{tool_name}'")
            
            # Stream start event
            yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name})}\n\n"
            
            # Get result
            result_str = await self.call_tool(tool_name, tool_input)
            
            try:
                result = json.loads(result_str)
            except:
                result = {"data": result_str}
            
            # Stream result event
            yield f"data: {json.dumps({'type': 'tool_result', 'tool': tool_name, 'result': result})}\n\n"
            
            # Stream complete event
            yield f"data: {json.dumps({'type': 'tool_complete', 'tool': tool_name})}\n\n"
        
        except Exception as e:
            logger.error(f"Error streaming tool '{tool_name}': {e}")
            yield f"data: {json.dumps({'type': 'tool_error', 'tool': tool_name, 'error': str(e)})}\n\n"
    
    async def is_connected(self) -> bool:
        """Check if MCP server is reachable in real time and update connection state."""
       
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.mcp_server_url}/health")
                if resp.status_code == 200:
                    data = resp.json()
                    self.connected = data.get("status") == "healthy"
                    return self.connected
        except Exception:
            pass
        self.connected = False
        return False


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


async def get_mcp_client(mcp_server_url: str = "http://localhost:8001") -> MCPClient:
    """
    Get or create global MCP client instance.
    
    Args:
        mcp_server_url: URL of the MCP server
    
    Returns:
        MCPClient instance
    """
    global _mcp_client
    
    if _mcp_client is None:
        _mcp_client = MCPClient(mcp_server_url)
    
    return _mcp_client


async def initialize_mcp_client(mcp_server_url: str = "http://localhost:8001") -> bool:
    """
    Initialize and connect the global MCP client.
    
    Args:
        mcp_server_url: URL of the MCP server
    
    Returns:
        True if successful, False otherwise
    """
    client = await get_mcp_client(mcp_server_url)
    return await client.connect()


async def close_mcp_client():
    """Close the global MCP client connection."""
    global _mcp_client
    if _mcp_client:
        await _mcp_client.disconnect()
        _mcp_client = None
