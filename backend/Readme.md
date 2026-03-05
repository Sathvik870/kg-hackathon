# No-Code SQL Backend with FastAPI & CopilotKit

## Architecture Overview

This FastAPI backend implements a sophisticated workflow for natural language SQL database queries:

```
┌─────────────────┐
│ React Frontend  │
│   (CopilotKit)  │
└────────┬────────┘
         │
         ├─────────────────────────────────────────────────────────┐
         │                                                         │
         v                                                         │
┌──────────────────────────────────────────────────────────────────┤
│ FastAPI Backend (/api/copilotkit)                                │
│ - CopilotKit SDK running                                         │
│ - Receives user query                                            │
└──────────────────────────────────────────────────────────────────┤
         │                                                         │
         ├─────────────────────────────────────────────────────────┤
         │                                                         │
         v                                                         │
┌──────────────────────────────────────────────────────────────────┤
│ Azure OpenAI (GPT-4.5)                                            │
│ - Analyzes user query                                            │
│ - Decides which tools to use                                     │
│ - Returns tool calls                                             │
└──────────────────────────────────────────────────────────────────┤
         │                                                         │
         └─────────────────────────────────────────────────────────┤
         │                                                         │
         v                                                         │
┌──────────────────────────────────────────────────────────────────┤
│ FastAPI Tool Execution (SSE: /api/execute-tool)                   │
│ - Validates tool requests                                        │
│ - Streams execution via Server-Sent Events                       │
└──────────────────────────────────────────────────────────────────┤
         │                                                         │
         ├─────────────────────────────────────────────────────────┤
         │                                                         │
         v                                                         │
┌──────────────────────────────────────────────────────────────────┤
│ PostgreSQL Database                                               │
│ - Execute queries                                                │
│ - Read/Write operations                                          │
│ - Schema inspection                                              │
└──────────────────────────────────────────────────────────────────┤
         │                                                         │
         └─────────────────────────────────────────────────────────┤
         │                                                         │
         v                                                         │
        Data → FastAPI → Azure OpenAI → Format Response → SSE Stream
```

## Setup Instructions

### 1. Create Virtual Environment

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_NAME=postgres
DATABASE_SSL=false

OPENAI_API_KEY=your_azure_openai_key
OPENAI_MODEL=gpt-4-turbo

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Run the Backend

```bash
python main.py
```

The backend will start at `http://localhost:8000`

---

## API Endpoints

### 1. Database Connection

**POST** `/api/connect`

Connect to a PostgreSQL database.

```json
{
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "password",
  "database": "postgres",
  "ssl": false
}
```

### 2. Get Available Tools

**GET** `/api/tools`

Retrieve list of available database operation tools.

**Response:**
```json
{
  "status": "success",
  "tools": [...],
  "count": 5
}
```

### 3. Execute Single Tool (SSE)

**POST** `/api/execute-tool`

Execute a single database tool via Server-Sent Events.

```json
{
  "name": "execute_query",
  "input": {
    "database": "mydb",
    "query": "SELECT * FROM users LIMIT 10"
  }
}
```

### 4. Execute Multiple Tools (SSE)

**POST** `/api/execute-tools`

Execute multiple tools in sequence via Server-Sent Events.

```json
{
  "tools": [
    {
      "name": "list_tables",
      "input": {"database": "mydb"}
    },
    {
      "name": "get_table_schema",
      "input": {"database": "mydb", "table_name": "users"}
    }
  ]
}
```

### 5. Get Database Structure

**GET** `/api/structure`

Get all databases and their tables.

**Response:**
```json
{
  "status": "success",
  "structure": [
    {
      "name": "mydb",
      "type": "database",
      "children": [
        {"name": "users", "type": "table"},
        {"name": "orders", "type": "table"}
      ]
    }
  ]
}
```

### 6. Preview Table

**POST** `/api/preview`

Preview first 50 rows of a table.

```json
{
  "db": "mydb",
  "table": "users"
}
```

### 7. Get Table Schema

**GET** `/api/schema/{database}/{table}`

Get detailed schema for a specific table.

---

## Available Database Tools

### 1. **list_tables**
Lists all tables in a database.

**Input:**
- `database` (string): Database name

**Output:**
```json
{
  "status": "success",
  "data": ["users", "orders", "products"],
  "message": "Found 3 tables in database 'mydb'"
}
```

### 2. **get_table_schema**
Get column names, types, and constraints.

**Input:**
- `database` (string): Database name
- `table_name` (string): Table name

**Output:**
```json
{
  "status": "success",
  "data": {
    "id": "integer (NOT NULL)",
    "name": "varchar (NOT NULL)",
    "email": "varchar (NULL)"
  },
  "message": "Schema for table 'users' in database 'mydb'"
}
```

### 3. **execute_query**
Execute SELECT queries to retrieve data.

**Input:**
- `database` (string): Database name
- `query` (string): SQL SELECT query

**Output:**
```json
{
  "status": "success",
  "data": [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "Jane", "email": "jane@example.com"}
  ],
  "message": "Query executed successfully. Found 2 rows."
}
```

### 4. **update_data**
Update records in a table.

**Input:**
- `database` (string): Database name
- `table` (string): Table name
- `set_clause` (object): Columns to update (e.g., `{"status": "active"}`)
- `where_clause` (string): WHERE condition (e.g., `"id = 5"`)

**Output:**
```json
{
  "status": "success",
  "data": {"affected_rows": 1},
  "message": "Updated 1 row(s) in table 'users'"
}
```

### 5. **list_databases**
List all databases on the server.

**Input:** None

**Output:**
```json
{
  "status": "success",
  "data": ["postgres", "mydb", "testdb"],
  "message": "Found 3 databases"
}
```

---

## File Structure

```
backend/
├── main.py                 # FastAPI application
├── db_utils.py            # Database connection & operations
├── mcp_tools.py           # MCP tools definitions
├── sse_executor.py        # SSE execution engine
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── package.json          # Node.js dependencies (if needed)
└── Readme.md             # This file
```

---

## Module Descriptions

### `main.py`
Main FastAPI application with all endpoints and middleware setup.

**Key Components:**
- CORS middleware for frontend communication
- Database connection management
- Tool registry and validation
- SSE streaming endpoints
- Health check endpoint

### `db_utils.py`
Database operations wrapper for PostgreSQL.

**Key Classes:**
- `DatabaseConnection`: Connection management with context managers
- `DatabaseOperations`: CRUD operations and schema inspection

### `mcp_tools.py`
MCP (Model Context Protocol) tool definitions.

**Key Functions:**
- `handle_tool_call()`: Routes tool execution requests
- Tool definitions with input schemas
- Error handling and response formatting

### `sse_executor.py`
Server-Sent Events execution engine.

**Key Classes:**
- `ToolExecutor`: Handles SSE streaming of tool execution
- `ToolRegistry`: Manages available tools and validation

### `config.py`
Configuration management from environment variables.

**Key Class:**
- `Settings`: Pydantic-based configuration with defaults

---

## Security Considerations

1. **Query Safety**: Dangerous keywords (DROP, DELETE, TRUNCATE) are blocked
2. **Input Validation**: All tool inputs are validated against schemas
3. **Connection Security**: Supports SSL/TLS for database connections
4. **CORS Control**: Configure CORS origins in `.env`
5. **Environment Variables**: Sensitive data stored in `.env`, never committed

---

## Troubleshooting

### Connection Issues

```bash
# Test PostgreSQL connectivity
psql -h localhost -U postgres -d postgres -c "SELECT 1"
```

### Port Already in Use

```bash
# Change port in .env
FASTAPI_PORT=8001
```

### Module Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS Errors

Update `CORS_ORIGINS` in `.env` with your frontend URL.

---

## Development Notes

- **Hot Reload**: Set `FASTAPI_RELOAD=true` in `.env` for development
- **Logging**: Configure `LOG_LEVEL` in `.env` (INFO, DEBUG, etc.)
- **Async Operations**: All DB operations use async/await for performance
- **Connection Pooling**: Consider adding asyncpg connection pools for production

---

## Next Steps

1. Set up PostgreSQL database
2. Configure `.env` with database credentials
3. Run the backend with `python main.py`
4. Test endpoints using Postman or curl
5. Integrate with React frontend using the CopilotKit SDK 