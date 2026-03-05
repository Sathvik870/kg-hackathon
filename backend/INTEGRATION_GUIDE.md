"""
Frontend-Backend Integration Guide for No-Code SQL

This file provides examples of how the React Frontend should interact with the FastAPI Backend.
"""

# ============================================================================
# 1. INITIAL CONNECTION
# ============================================================================

# Frontend should call this first to establish database connection
POST /api/connect
{
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "your_password",
  "database": "your_database",
  "ssl": false
}

Response:
{
  "status": "connected",
  "message": "Successfully connected to your_database",
  "host": "localhost",
  "database": "your_database"
}


# ============================================================================
# 2. GET AVAILABLE TOOLS (For Frontend Display)
# ============================================================================

GET /api/tools

Response:
{
  "status": "success",
  "tools": [
    {
      "name": "list_tables",
      "description": "List all tables in a PostgreSQL database",
      "inputSchema": {
        "type": "object",
        "properties": {
          "database": {
            "type": "string",
            "description": "Database name (defaults to 'postgres')"
          }
        }
      }
    },
    {
      "name": "get_table_schema",
      "description": "Get the schema (column names and types) of a specific table",
      "inputSchema": {
        "type": "object",
        "properties": {
          "database": {"type": "string", "description": "Database name"},
          "table_name": {"type": "string", "description": "Name of the table"}
        },
        "required": ["database", "table_name"]
      }
    },
    {
      "name": "execute_query",
      "description": "Execute a SELECT query against a PostgreSQL database",
      "inputSchema": {
        "type": "object",
        "properties": {
          "database": {"type": "string", "description": "Database name"},
          "query": {"type": "string", "description": "SQL SELECT query to execute"}
        },
        "required": ["database", "query"]
      }
    },
    {
      "name": "update_data",
      "description": "Update data in a table",
      "inputSchema": {
        "type": "object",
        "properties": {
          "database": {"type": "string"},
          "table": {"type": "string"},
          "set_clause": {"type": "object", "description": "Dict of column: value pairs"},
          "where_clause": {"type": "string", "description": "WHERE condition"}
        },
        "required": ["database", "table", "set_clause", "where_clause"]
      }
    },
    {
      "name": "list_databases",
      "description": "List all available databases on the PostgreSQL server",
      "inputSchema": {"type": "object", "properties": {}}
    }
  ],
  "count": 5
}


# ============================================================================
# 3. GET DATABASE STRUCTURE (For Sidebar Navigation)
# ============================================================================

GET /api/structure

Response:
{
  "status": "success",
  "structure": [
    {
      "name": "mydb",
      "type": "database",
      "children": [
        {"name": "users", "type": "table"},
        {"name": "orders", "type": "table"},
        {"name": "products", "type": "table"}
      ]
    },
    {
      "name": "testdb",
      "type": "database",
      "children": [
        {"name": "test_table", "type": "table"}
      ]
    }
  ]
}


# ============================================================================
# 4. PREVIEW TABLE DATA (For Sidebar)
# ============================================================================

POST /api/preview
{
  "db": "mydb",
  "table": "users"
}

Response:
{
  "status": "success",
  "data": [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
  ],
  "count": 3
}


# ============================================================================
# 5. GET TABLE SCHEMA (For Data Grid Headers)
# ============================================================================

GET /api/schema/mydb/users

Response:
{
  "status": "success",
  "database": "mydb",
  "table": "users",
  "schema": {
    "id": "integer (NOT NULL)",
    "name": "character varying (NOT NULL)",
    "email": "character varying (NULL)",
    "created_at": "timestamp (NOT NULL)"
  }
}


# ============================================================================
# 6. EXECUTE SINGLE TOOL (For Direct User Commands)
# ============================================================================

POST /api/execute-tool
{
  "name": "list_tables",
  "input": {
    "database": "mydb"
  }
}

Response (SSE Stream - Server-Sent Events):
data: {"type": "tool_start", "tool": "list_tables"}

data: {"type": "tool_result", "tool": "list_tables", "result": {
  "status": "success",
  "data": ["users", "orders", "products"],
  "message": "Found 3 tables in database 'mydb'"
}}

data: {"type": "tool_complete", "tool": "list_tables"}


# ============================================================================
# 7. EXECUTE MULTIPLE TOOLS (For Complex Queries)
# ============================================================================

POST /api/execute-tools
{
  "tools": [
    {
      "name": "get_table_schema",
      "input": {"database": "mydb", "table_name": "users"}
    },
    {
      "name": "execute_query",
      "input": {
        "database": "mydb",
        "query": "SELECT id, name, email FROM users WHERE created_at > NOW() - INTERVAL '7 days' LIMIT 10"
      }
    }
  ]
}

Response (SSE Stream):
First Tool (get_table_schema):
---
data: {"type": "tool_start", "tool": "get_table_schema"}

data: {"type": "tool_result", "tool": "get_table_schema", "result": {
  "status": "success",
  "data": {
    "id": "integer (NOT NULL)",
    "name": "character varying (NOT NULL)",
    "email": "character varying (NULL)"
  }
}}

data: {"type": "tool_complete", "tool": "get_table_schema"}

---
Second Tool (execute_query):
---
data: {"type": "tool_start", "tool": "execute_query"}

data: {"type": "tool_result", "tool": "execute_query", "result": {
  "status": "success",
  "data": [
    {"id": 5, "name": "Alice", "email": "alice@example.com"},
    {"id": 6, "name": "Charlie", "email": "charlie@example.com"}
  ],
  "message": "Query executed successfully. Found 2 rows."
}}

data: {"type": "tool_complete", "tool": "execute_query"}


# ============================================================================
# 8. UPDATE DATA
# ============================================================================

POST /api/execute-tool
{
  "name": "update_data",
  "input": {
    "database": "mydb",
    "table": "users",
    "set_clause": {
      "email": "newemail@example.com",
      "status": "active"
    },
    "where_clause": "id = 5"
  }
}

Response (SSE Stream):
data: {"type": "tool_start", "tool": "update_data"}

data: {"type": "tool_result", "tool": "update_data", "result": {
  "status": "success",
  "data": {"affected_rows": 1},
  "message": "Updated 1 row(s) in table 'users'"
}}

data: {"type": "tool_complete", "tool": "update_data"}


# ============================================================================
# 9. HEALTH CHECK
# ============================================================================

GET /api/health

Response:
{
  "status": "healthy" or "disconnected",
  "database_connected": true or false
}


# ============================================================================
# FRONTEND IMPLEMENTATION EXAMPLE (TypeScript/React)
# ============================================================================

// Handling SSE Responses
async function executeToolWithSSE(toolName: string, toolInput: object) {
  const response = await fetch('http://localhost:8000/api/execute-tool', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: toolName,
      input: toolInput
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    const lines = text.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const event = JSON.parse(line.slice(6));
          console.log('Received event:', event);

          if (event.type === 'tool_start') {
            // Show loading state
            console.log(`Tool ${event.tool} started...`);
          } else if (event.type === 'tool_result') {
            // Process result
            console.log(`Tool ${event.tool} result:`, event.result);
          } else if (event.type === 'tool_complete') {
            // Hide loading state
            console.log(`Tool ${event.tool} completed`);
          } else if (event.type === 'tool_error') {
            // Handle error
            console.error(`Tool ${event.tool} error:`, event.error);
          }
        } catch (e) {
          // Ignore malformed lines
        }
      }
    }
  }
}

// Usage
await executeToolWithSSE('list_tables', { database: 'mydb' });
