import uvicorn
import asyncpg
import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- New Imports for Copilot Runtime ---
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# --- Models ---
class ConnectionDetails(BaseModel):
    host: str
    port: str
    user: str
    password: str
    database: str = "postgres"
    ssl: bool = False

# --- Global State ---
current_connection: Optional[ConnectionDetails] = None

# --- FastAPI App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Helpers ---
async def get_db_connection(db_name: str = None):
    global current_connection
    if not current_connection:
        raise HTTPException(status_code=400, detail="Not connected")
    
    target_db = db_name if db_name else current_connection.database
    
    try:
        return await asyncpg.connect(
            user=current_connection.user,
            password=current_connection.password,
            host=current_connection.host,
            port=current_connection.port,
            database=target_db,
            ssl="require" if current_connection.ssl else "disable"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Define Tools for the AI (Using LangChain/Copilot format) ---

@tool
async def list_databases() -> str:
    """List all available databases on the server."""
    # We must handle the connection check inside the tool
    if not current_connection: return "Error: Database not connected."
    
    try:
        conn = await get_db_connection("postgres")
        rows = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
        await conn.close()
        return "\n".join([r['datname'] for r in rows])
    except Exception as e:
        return f"Error: {str(e)}"

@tool
async def get_table_schema(database: str, table_name: str) -> str:
    """Get the schema/columns for a specific table in a specific database."""
    try:
        conn = await get_db_connection(database)
        rows = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = $1
        """, table_name)
        await conn.close()
        return "\n".join([f"{r['column_name']}: {r['data_type']}" for r in rows])
    except Exception as e:
        return f"Error: {str(e)}"

@tool
async def run_sql_query(database: str, query: str) -> str:
    """Execute a read-only SQL query on a specific database."""
    if "DROP" in query.upper() or "DELETE" in query.upper() or "UPDATE" in query.upper():
        return "Unsafe queries are disabled."
        
    try:
        conn = await get_db_connection(database)
        rows = await conn.fetch(query)
        await conn.close()
        if not rows: return "No results."
        return str([dict(row) for row in rows])
    except Exception as e:
        return f"Error executing query: {str(e)}"

# --- REST Endpoints (For UI Sidebar/Connect) ---

@app.post("/api/connect")
async def connect_db(details: ConnectionDetails):
    global current_connection
    try:
        conn = await asyncpg.connect(
            user=details.user,
            password=details.password,
            host=details.host,
            port=details.port,
            database=details.database or "postgres",
             ssl="require" if details.ssl else "disable"
        )
        await conn.close()
        current_connection = details
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/structure")
async def get_structure():
    if not current_connection:
        raise HTTPException(status_code=400, detail="Not connected")
    
    conn = await get_db_connection("postgres")
    dbs = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
    await conn.close()
    
    structure = []
    for db_row in dbs:
        db_name = db_row['datname']
        structure.append({"name": db_name, "type": "database", "children": []})

    return structure

@app.post("/api/preview")
async def preview_table(db: str = Body(...), table: str = Body(...)):
    conn = await get_db_connection(db)
    try:
        rows = await conn.fetch(f'SELECT * FROM "{table}" LIMIT 50')
        return [dict(row) for row in rows]
    finally:
        await conn.close()

# --- Initialize CopilotKit Runtime ---
# This makes the backend act as the "Brain" using OpenAI
sdk = CopilotKitSDK(
    actions=[
        list_databases, 
        get_table_schema, 
        run_sql_query
    ],
)

# Add the /copilotkit endpoint
add_fastapi_endpoint(app, sdk, "/copilotkit")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)