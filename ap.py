from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from mcp.server import Server
import uvicorn
import os
import asyncpg
from dotenv import load_dotenv
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global, mutable database connection settings that can be updated at runtime
DB_SETTINGS = {
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASS", "sathvik2004"),
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
}

# Initialize FastMCP server for Weather, GitHub, and Indian Rail tools (SSE)
mcp = FastMCP("NLTOSQL")

# Postgres MCP
async def connect(db_name: str) -> asyncpg.Connection:
    try:
        conn = await asyncpg.connect(
            database=db_name,
            user=DB_SETTINGS["user"],
            password=DB_SETTINGS["password"],
            host=DB_SETTINGS["host"],
            port=DB_SETTINGS["port"],
        )
        logger.info(f"Connected to database: {db_name}")
        return conn
    except Exception as e:
        logger.error(f"Connection error: {e}")
        raise

@mcp.tool(name="list_databases", description="List all PostgreSQL databases")
async def list_databases() -> str:
    """List all available PostgreSQL databases."""
    try:
        conn = await connect("postgres")
        rows = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
        await conn.close()
        return "\n".join(row["datname"] for row in rows) if rows else "No databases found."
    except Exception as e:
        logger.error(f"Error listing databases: {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="list_tables", description="List all public tables in a PostgreSQL database")
async def list_tables(db_name: str) -> str:
    """List all tables in the specified database."""
    try:
        conn = await connect(db_name)
        rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        await conn.close()
        return "\n".join(row["table_name"] for row in rows) if rows else f"No public tables found in '{db_name}'."
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="table_schema", description="Get column names and types of a table")
async def table_schema(db_name: str, table: str) -> str:
    """Get schema information for a specific table."""
    try:
        conn = await connect(db_name)
        rows = await conn.fetch(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1;",
            table
        )
        await conn.close()
        return "\n".join(f"{row['column_name']}: {row['data_type']}" for row in rows) if rows else f"No schema found for table '{table}'."
    except Exception as e:
        logger.error(f"Error retrieving schema: {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="view_table", description="Show first 10 rows of a table")
async def view_table(db_name: str, table: str) -> str:
    """View the first 10 rows of a table."""
    try:
        conn = await connect(db_name)
        # Use proper identifier quoting
        rows = await conn.fetch(f'SELECT * FROM "{table}" LIMIT 10;')
        await conn.close()
        
        if not rows:
            return f"No rows found in '{table}'."
        
        # Format results nicely
        result_lines = []
        for row in rows:
            row_dict = dict(row)
            result_lines.append(str(row_dict))
            
        return "\n".join(result_lines)
    except Exception as e:
        logger.error(f"Error viewing table '{table}': {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="execute_query", description="Execute a custom SQL query")
async def execute_query(db_name: str, query: str) -> str:
    """Execute a custom SQL query and return results."""
    try:
        conn = await connect(db_name)
        
        # Determine if this is a query that returns results
        query_type = query.strip().upper().split()[0]
        
        if query_type in ("SELECT", "WITH", "SHOW", "EXPLAIN"):
            rows = await conn.fetch(query)
            await conn.close()
            
            if not rows:
                return "Query executed successfully. No results returned."
            
            # Format results
            result_lines = []
            for row in rows:
                row_dict = dict(row)
                result_lines.append(str(row_dict))
                
            return "\n".join(result_lines)
        else:
            # For non-SELECT queries
            status = await conn.execute(query)
            await conn.close()
            return f"Query executed successfully. Status: {status}"
            
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return f"Error executing query: {str(e)}"

@mcp.tool(name="hello_postgres", description="Test connection to the server")
async def hello_postgres(name: str = "World") -> str:
    """Simple test function."""
    logger.info(f"Hello function called with name: {name}")
    return f"Hello from the Postgres Explorer, {name}!"


# --- Starlette App ---

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def configure_db(request: Request):
        """
        Simple JSON API to configure Postgres connection settings at runtime.
        Expected payload:
        {
          "host": "localhost",
          "port": "5432",
          "user": "postgres",
          "password": "secret"
        }
        """
        try:
            payload = await request.json()
        except Exception:
            return JSONResponse({"ok": False, "error": "Invalid JSON body"}, status_code=400)

        # Update the global DB_SETTINGS, falling back to existing values when keys are missing
        DB_SETTINGS["host"] = str(payload.get("host") or DB_SETTINGS["host"])
        DB_SETTINGS["port"] = str(payload.get("port") or DB_SETTINGS["port"])
        DB_SETTINGS["user"] = str(payload.get("user") or DB_SETTINGS["user"])
        DB_SETTINGS["password"] = str(payload.get("password") or DB_SETTINGS["password"])

        # Optionally test the connection using the default "postgres" database
        try:
            conn = await connect("postgres")
            await conn.close()
            return JSONResponse(
                {
                    "ok": True,
                    "message": "Database configuration updated and connection successful.",
                    "settings": {
                        "host": DB_SETTINGS["host"],
                        "port": DB_SETTINGS["port"],
                        "user": DB_SETTINGS["user"],
                    },
                }
            )
        except Exception as e:
            logger.error(f"Error testing DB connection after config update: {e}")
            return JSONResponse(
                {
                    "ok": False,
                    "error": f"Failed to connect with provided settings: {str(e)}",
                    "settings": {
                        "host": DB_SETTINGS["host"],
                        "port": DB_SETTINGS["port"],
                        "user": DB_SETTINGS["user"],
                    },
                },
                status_code=400,
            )

    async def list_databases_http(request: Request):
        """HTTP wrapper around the list_databases MCP tool for the UI."""
        try:
            conn = await connect("postgres")
            rows = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
            await conn.close()
            databases = [row["datname"] for row in rows] if rows else []
            return JSONResponse({"ok": True, "databases": databases})
        except Exception as e:
            logger.error(f"HTTP error listing databases: {e}")
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    async def list_tables_http(request: Request):
        """List public tables for a given database (HTTP)."""
        db_name = request.path_params.get("db_name")
        if not db_name:
            return JSONResponse({"ok": False, "error": "Missing db_name"}, status_code=400)

        try:
            conn = await connect(db_name)
            rows = await conn.fetch(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
            )
            await conn.close()
            tables = [row["table_name"] for row in rows] if rows else []
            return JSONResponse({"ok": True, "db": db_name, "tables": tables})
        except Exception as e:
            logger.error(f"HTTP error listing tables for {db_name}: {e}")
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    async def table_rows_http(request: Request):
        """Return up to 50 rows from a given table (HTTP)."""
        db_name = request.path_params.get("db_name")
        table_name = request.path_params.get("table_name")

        if not db_name or not table_name:
            return JSONResponse({"ok": False, "error": "Missing db_name or table_name"}, status_code=400)

        # Clamp limit to a reasonable range, default 50
        try:
            limit = int(request.query_params.get("limit", "50"))
        except ValueError:
            limit = 50
        limit = max(1, min(limit, 200))

        try:
            conn = await connect(db_name)
            # NOTE: table_name comes from our own table list; still quote it defensively
            query = f'SELECT * FROM "{table_name}" LIMIT {limit};'
            rows = await conn.fetch(query)
            await conn.close()

            data = [dict(row) for row in rows]

            return JSONResponse(
                {
                    "ok": True,
                    "db": db_name,
                    "table": table_name,
                    "limit": limit,
                    "rowCount": len(data),
                    "rows": data,
                }
            )
        except Exception as e:
            logger.error(f"HTTP error fetching rows for {db_name}.{table_name}: {e}")
            # Instead of surfacing an internal error to the UI as a 500,
            # respond with a successful status and a "nodata" marker so the
            # frontend can display an empty state gracefully.
            return JSONResponse(
                {
                    "ok": False,
                    "error": "nodata",
                    "db": db_name,
                    "table": table_name,
                    "rowCount": 0,
                    "rows": [],
                },
                status_code=200,
            )
    
    async def handle_sse(request: Request):
        try:
            logger.info("SSE connection initiated")
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as (read_stream, write_stream):
                logger.info("SSE connection established, starting MCP server")
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
        except Exception as e:
            logger.error(f"Error in SSE handler: {e}")
            raise
    
    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
            Route("/api/db-config", endpoint=configure_db, methods=["POST"]),
            Route("/api/databases", endpoint=list_databases_http, methods=["GET"]),
            Route("/api/databases/{db_name}/tables", endpoint=list_tables_http, methods=["GET"]),
            Route(
                "/api/databases/{db_name}/tables/{table_name}/rows",
                endpoint=table_rows_http,
                methods=["GET"],
            ),
        ],
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ],
    )

if __name__ == "__main__":
    # Get the MCP server instance
    mcp_server = mcp._mcp_server
    
    import argparse
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()
    
    print("Available tools:")
    print("Weather tools: get_alerts, get_forecast")
    print("GitHub tools (read-only): get_github_user, get_github_repos, get_github_repo_info, get_github_issues, search_github_repos, get_github_commits")
    print("Indian Rail tools: station_name_to_code, get_train_schedule_indian_rail, get_all_trains_on_station")
    
    # if not GITHUB_TOKEN:
    #     print("Note: No GITHUB_TOKEN set. Using public API with lower rate limits.")
    # else:
    #     print("Note: GITHUB_TOKEN found. Using authenticated API with higher rate limits.")
    
    # if not INDIAN_RAIL_API_KEY:
    #     print("Note: INDIAN_RAIL_API_KEY not set. Indian Rail tools will not work.")
    # else:
    #     print("Note: INDIAN_RAIL_API_KEY found. Indian Rail tools are available.")
    
    # Create the Starlette app
    starlette_app = create_starlette_app(mcp_server, debug=True)
    
    # Run the server
    try:
        uvicorn.run(starlette_app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise