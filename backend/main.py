"""
FastAPI Backend for No-Code SQL Frontend with MCP Integration
Architecture:
1. React Frontend → /api/copilotkit (CopilotKit SDK)
2. FastAPI receives query and sends to Azure OpenAI (GPT-4.5)
3. Azure OpenAI responds with tool calls
4. FastAPI forwards tool calls to MCP Server via SSE
5. MCP Server connects to PostgreSQL and returns data
6. FastAPI streams response back to React Frontend
"""
import logging
import json
import os
import httpx
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Local imports
from config import get_settings
from mcp_client import initialize_mcp_client, close_mcp_client, get_mcp_client
from db_utils import DatabaseConnection, DatabaseOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Settings ---
settings = get_settings()

# --- Pydantic Models ---
class ConnectionDetails(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str = "postgres"
    ssl: bool = False


class ToolCall(BaseModel):
    name: str
    input: Dict[str, Any]


class ToolExecutionRequest(BaseModel):
    tools: List[ToolCall]


class DBConnectRequest(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
    ssl: bool = False


class CopilotChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# --- Global State ---
mcp_connected: bool = False


# --- Lifecycle Events ---
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifecycle.
    Initialize MCP client on startup, close on shutdown.
    """
    # Startup
    global mcp_connected
    logger.info("Starting FastAPI application...")
    
    try:
        # Initialize MCP client connection
        mcp_server_url = f"http://{settings.fastapi_host}:8001"
        mcp_connected = await initialize_mcp_client(mcp_server_url)
        
        if mcp_connected:
            logger.info(f"✓ Connected to MCP server at {mcp_server_url}")
        else:
            logger.warning(f"✗ Could not connect to MCP server at {mcp_server_url}")
            logger.info("Make sure MCP server is running: python mcp_server/run.py")
    
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    try:
        await close_mcp_client()
        logger.info("Closed MCP client connection")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# --- FastAPI App ---
app = FastAPI(
    title="No-Code SQL Backend with MCP",
    description="FastAPI backend for SQL database operations with proper MCP integration",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Connection Management ---
async def ensure_mcp_connected():
    """Ensure MCP server is connected"""
    if not mcp_connected:
        raise HTTPException(
            status_code=503,
            detail="MCP server not connected. Please start MCP server: python mcp_server/run.py"
        )


# --- REST Endpoints ---

@app.post("/api/connect")
async def connect_db(details: ConnectionDetails):
    """
    Configuration endpoint - stores PostgreSQL connection info in environment.
    MCP server uses these environment variables.
    """
    await ensure_mcp_connected()
    
    try:
        logger.info(f"Connection info received for {details.database} at {details.host}:{details.port}")
        
        return {
            "status": "configured",
            "message": "PostgreSQL connection configured for MCP server",
            "host": details.host,
            "database": details.database,
            "note": "Ensure MCP server is running with these same credentials"
        }
    
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Configuration failed: {str(e)}")


@app.post("/api/db-tables")
async def get_db_tables(request: DBConnectRequest):
    """
    Connects to the given database and returns a list of table names.
    Used by frontend before CopilotKit cycle starts.
    """
    try:
        db_conn = DatabaseConnection(
            host=request.host,
            port=request.port,
            user=request.user,
            password=request.password,
            database=request.database,
            ssl=request.ssl
        )
        db_ops = DatabaseOperations(db_conn)
        tables = await db_ops.list_tables(request.database)
        return {"status": "success", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DB connection failed: {str(e)}")


@app.get("/api/tools")
async def get_available_tools():
    """
    Get list of available tools from MCP server.
    These tools are discovered via MCP protocol.
    """
    await ensure_mcp_connected()
    
    try:
        mcp_client = await get_mcp_client()
        tools = await mcp_client.get_tools()
        
        if not tools:
            raise HTTPException(
                status_code=503,
                detail="Could not retrieve tools from MCP server"
            )
        
        return {
            "status": "success",
            "tools": tools,
            "count": len(tools),
            "source": "MCP Server"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute-tool")
async def execute_tool_sse(request: ToolCall):
    """
    Execute a single tool via MCP Server using SSE.
    Streams execution progress back to client.
    """
    await ensure_mcp_connected()
    
    tool_name = request.name
    tool_input = request.input
    
    logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
    
    mcp_client = await get_mcp_client()
    
    # Stream tool execution
    async def generate():
        async for event in mcp_client.call_tool_streaming(tool_name, tool_input):
            yield f"data: {event}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/execute-tools")
async def execute_tools_batch(request: ToolExecutionRequest):
    """
    Execute multiple tools via MCP Server in sequence.
    """
    await ensure_mcp_connected()
    
    mcp_client = await get_mcp_client()
    
    # Stream batch execution
    async def generate():
        for tool_call in request.tools:
            async for event in mcp_client.call_tool_streaming(tool_call.name, tool_call.input):
                yield f"data: {event}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/structure")
async def get_database_structure():
    """
    Get database structure (databases and tables).
    Calls MCP server's list_databases and list_tables tools.
    """
    await ensure_mcp_connected()
    
    try:
        mcp_client = await get_mcp_client()
        
        # Get list of databases
        databases_result = await mcp_client.call_tool("list_databases", {})
        databases = [db.strip() for db in databases_result.split("\n") if db.strip()]
        
        structure = []
        
        # For each database, get its tables
        for db_name in databases:
            try:
                tables_result = await mcp_client.call_tool("list_tables", {"database": db_name})
                tables = [table.strip() for table in tables_result.split("\n") if table.strip()]
                
                structure.append({
                    "name": db_name,
                    "type": "database",
                    "children": [{"name": table, "type": "table"} for table in tables]
                })
            except Exception as e:
                logger.warning(f"Could not list tables in {db_name}: {e}")
                structure.append({
                    "name": db_name,
                    "type": "database",
                    "children": []
                })
        
        return {
            "status": "success",
            "structure": structure
        }
    
    except Exception as e:
        logger.error(f"Error getting structure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/preview")
async def preview_table(db: str = Body(...), table: str = Body(...)):
    """
    Preview table data using MCP server's preview_table tool.
    """
    await ensure_mcp_connected()
    
    try:
        mcp_client = await get_mcp_client()
        result = await mcp_client.call_tool(
            "preview_table",
            {"database": db, "table": table, "limit": 50}
        )
        
        # Parse the result (it's formatted as strings)
        rows = []
        for line in result.split("\n"):
            if line.strip().startswith("Row"):
                # Parse "Row N: {...}" format
                try:
                    import ast
                    data_str = line.split(": ", 1)[1]
                    row_data = ast.literal_eval(data_str)
                    rows.append(row_data)
                except:
                    pass
        
        return {
            "status": "success",
            "data": rows,
            "count": len(rows)
        }
    
    except Exception as e:
        logger.error(f"Error previewing table: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schema/{database}/{table}")
async def get_table_schema_endpoint(database: str, table: str):
    """
    Get schema for a specific table using MCP server.
    """
    await ensure_mcp_connected()
    
    try:
        mcp_client = await get_mcp_client()
        schema_result = await mcp_client.call_tool(
            "get_table_schema",
            {"database": database, "table_name": table}
        )
        
        # Parse schema result
        schema = {}
        for line in schema_result.split("\n"):
            if ": " in line:
                col_name, col_type = line.split(": ", 1)
                schema[col_name.strip()] = col_type.strip()
        
        return {
            "status": "success",
            "database": database,
            "table": table,
            "schema": schema
        }
    
    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/copilotkit")
async def copilotkit_chat(request: CopilotChatRequest):
    """
    Main chat endpoint for CopilotKit frontend. Accepts a user message, sends it to OpenAI, parses tool calls, executes tools via MCP, and streams results.
    """
    # 1. Send user message to OpenAI
    openai_api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
    openai_model = settings.openai_model or "gpt-4-turbo"
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured.")

    user_message = request.message
    session_id = request.session_id or "default"
    context = request.context or {}

    # Compose OpenAI API payload (ChatCompletion)
    openai_url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {openai_api_key}"}
    payload = {
        "model": openai_model,
        "messages": [
            {"role": "system", "content": "You are a helpful SQL assistant. Use tool calls for database actions."},
            {"role": "user", "content": user_message}
        ],
        "stream": True,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "execute_sql_query",
                    "description": "Execute SQL query on the connected database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL query to execute."}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    }

    async def chat_stream():
        # 2. Stream OpenAI response
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", openai_url, headers=headers, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    # Parse OpenAI response chunk
                    try:
                        chunk = json.loads(data)
                    except Exception:
                        continue
                    # If tool call is present, execute tool via MCP
                    choices = chunk.get("choices", [])
                    for choice in choices:
                        if "delta" in choice and "tool_calls" in choice["delta"]:
                            tool_calls = choice["delta"]["tool_calls"]
                            for tool_call in tool_calls:
                                tool_name = tool_call["function"]["name"]
                                tool_args = tool_call["function"].get("arguments", {})
                                # Call MCP tool and stream result
                                mcp_client = await get_mcp_client()
                                async for event in mcp_client.call_tool_streaming(tool_name, tool_args):
                                    yield event
                        elif "delta" in choice and "content" in choice["delta"]:
                            # Stream normal LLM content
                            yield f"data: {json.dumps({'type': 'llm_content', 'content': choice['delta']['content']})}\n\n"

    return StreamingResponse(chat_stream(), media_type="text/event-stream")


@app.get("/api/mcp-status")
async def mcp_status():
    """
    Check MCP server status and connection.
    """
    try:
        mcp_client = await get_mcp_client()
        is_connected = await mcp_client.is_connected()
        
        tools = []
        if is_connected:
            tools = await mcp_client.get_tools()
        
        return {
            "status": "connected" if is_connected else "disconnected",
            "mcp_server": "http://localhost:8001",
            "tools_available": len(tools),
            "mcp_enabled": True
        }
    
    except Exception as e:
        logger.error(f"Error checking MCP status: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "mcp_enabled": True
        }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    try:
        mcp_client = await get_mcp_client()
        is_connected = await mcp_client.is_connected()
        
        return {
            "status": "healthy" if is_connected else "degraded",
            "fastapi_connected": True,
            "mcp_connected": is_connected
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/")
async def root():
    """
    Root endpoint with API documentation.
    """
    return {
        "name": "No-Code SQL Backend (MCP v2)",
        "version": "2.0.0",
        "architecture": "FastAPI + MCP Server",
        "mcp_server_running": mcp_connected,
        "endpoints": {
            "health": "GET /api/health",
            "mcp_status": "GET /api/mcp-status",
            "connect": "POST /api/connect",
            "get_tools": "GET /api/tools",
            "execute_tool": "POST /api/execute-tool",
            "execute_tools": "POST /api/execute-tools",
            "get_structure": "GET /api/structure",
            "preview_table": "POST /api/preview",
            "get_schema": "GET /api/schema/{database}/{table}",
            "copilotkit": "POST /api/copilotkit"
        },
        "note": "Ensure MCP server is running: python mcp_server/run.py"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload
    )