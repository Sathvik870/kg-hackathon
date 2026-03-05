# Backend Setup & Verification Guide

This document provides complete step-by-step instructions to start and verify the no-code SQL backend with proper MCP implementation.

## 📋 System Overview

The backend consists of two servers:

1. **MCP Server** (Port 8001) - Starlette app with FastMCP framework
   - Handles database operations using MCP protocol
   - Connects directly to PostgreSQL
   - 7 available tools for database operations

2. **FastAPI Backend** (Port 8000) - HTTP API router
   - Routes requests from React frontend to MCP Server
   - Provides REST API endpoints
   - Manages SSE (Server-Sent Events) streaming
   - Handles CORS for frontend

**Architecture Flow:**
```
Frontend (React) → FastAPI (8000) → HTTP Client → MCP Server (8001) → PostgreSQL
```

## 🚀 Quick Start (One-Command)

```bash
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
bash startup.sh
```

This will:
- Kill any existing processes
- Start both servers with proper sequencing
- Run automated tests
- Show connection status

## 📖 Manual Startup (Recommended for Learning)

### Prerequisites

1. **Verify Python Environment**
   ```bash
   cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
   python3 --version  # Should be 3.8+
   ```

2. **Verify Virtual Environment**
   ```bash
   ls -la venv/bin/python
   # Should exist
   ```

3. **Verify PostgreSQL is Running**
   ```bash
   psql -U postgres -c "SELECT version();"
   # Should output PostgreSQL version
   ```

### Step 1: Terminal 1 - Start MCP Server

```bash
# Navigate to backend
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend

# Activate virtual environment
source venv/bin/activate

# Start MCP Server
python mcp_server/run.py
```

**Expected Output:**
```
🚀 MCP PostgreSQL Server Starting
Port: 8001
Debug Mode: False

Available Tools (MCP Protocol):
  1. list_databases
     Description: List all available databases
  2. list_tables
     Description: List all tables in a database
  3. get_table_schema
     Description: Get the column schema for a table
  4. execute_query
     Description: Execute a SELECT query
  5. update_data
     Description: Update data in a table
  6. preview_table
     Description: Preview first N rows of a table
  7. health_check
     Description: Check server health

[timestamp] INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

✅ **When you see this output, MCP Server is ready!**

**Common Issues:**
- `OSError: [Errno 98] Address already in use`
  - Solution: `pkill -f "mcp_server/run.py"` then retry
  
- `ModuleNotFoundError: No module named 'mcp'`
  - Solution: Verify venv activated: `which python` should show `.../venv/bin/python`

### Step 2: Terminal 2 - Start FastAPI Backend

Open a new terminal:

```bash
# Navigate to backend
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend

# Activate virtual environment
source venv/bin/activate

# Start FastAPI Backend
python main.py
```

**Expected Output:**
```
INFO:main:🔌 MCP Client initializing...
INFO:main:✓ Connected to MCP server at http://localhost:8001
INFO:main:📦 Loaded 7 tools from MCP server:
INFO:main:  - list_databases
INFO:main:  - list_tables
INFO:main:  - get_table_schema
INFO:main:  - execute_query
INFO:main:  - update_data
INFO:main:  - preview_table
INFO:main:  - health_check
INFO:main:✨ FastAPI Backend Ready!

[timestamp] INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **When you see this output, FastAPI Backend is ready!**

**Common Issues:**
- `ConnectionError: Cannot connect to MCP server`
  - Solution: Ensure MCP Server in Terminal 1 is running

- `OSError: [Errno 98] Address already in use`
  - Solution: `pkill -f "main.py"` then retry

## ✅ Verification Tests

### Terminal 3 - Test Everything

```bash
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
python3 test_everything.py
```

This runs 9 automated tests:
1. MCP Server root endpoint
2. MCP Server health check
3. FastAPI root endpoint
4. FastAPI health check
5. MCP connection status
6. Tool discovery (list all available tools)
7. Tool execution: health_check
8. Tool execution: list_databases
9. Tool execution: list_tables

**Expected Output:**
```
======================================================================
  Testing MCP Server (Port 8001)
======================================================================

✓ MCP Server Root
  Status: 200
  Response: {"status": "running", "server": "NLTOSQL MCP Server", ...}

✓ MCP Server Health
  Status: 200
  Response: {"status": "healthy", "server": "NLTOSQL-Database-Server", ...}

======================================================================
  Testing FastAPI Backend (Port 8000)
======================================================================

✓ FastAPI Root
  Status: 200
✓ FastAPI Health Check
  Status: 200
✓ MCP Connection Status
  Status: 200

[... more tests ...]

======================================================================
  Test Results Summary
======================================================================

Total Tests: 9
Passed: 9
Failed: 0
Success Rate: 100.0%

✓ ALL TESTS PASSED! Backend is working correctly.
```

### Manual Testing with curl

If you prefer to test manually:

```bash
# Test MCP Server Root
curl http://localhost:8001/
# Expected: {"status": "running", "server": "NLTOSQL MCP Server", ...}

# Test MCP Server Health
curl http://localhost:8001/health
# Expected: {"status": "healthy", "server": "NLTOSQL-Database-Server", ...}

# Test FastAPI Root
curl http://localhost:8000/
# Expected: JSON with API documentation

# Test FastAPI Health
curl http://localhost:8000/api/health
# Expected: {"status": "healthy", "fastapi_connected": true, "mcp_connected": true}

# Test Get Tools
curl http://localhost:8000/api/tools
# Expected: Array of 7 tools with schemas

# Test Tool Execution (health_check)
curl -X POST http://localhost:8000/api/execute-tool \
  -H "Content-Type: application/json" \
  -d '{"name": "health_check", "input": {}}'
# Expected: {"status": "healthy", ...}

# Test Tool Execution (list_databases)
curl -X POST http://localhost:8000/api/execute-tool \
  -H "Content-Type: application/json" \
  -d '{"name": "list_databases", "input": {}}'
# Expected: Array of database names
```

## 🔍 Troubleshooting

### Issue: "Address already in use" on Port 8000 or 8001

**Solution:**
```bash
# Find and kill processes
lsof -i :8000
lsof -i :8001

# Kill by PID
kill -9 <PID>

# Or force kill by command
pkill -f "main.py"
pkill -f "mcp_server/run.py"
```

### Issue: "Connection refused" errors in FastAPI

**Solution:**
1. Ensure MCP Server started first before FastAPI
2. Check MCP Server is actually running: `curl http://localhost:8001/health`
3. Check logs in Terminal 1 for errors

### Issue: "ModuleNotFoundError" for dependencies

**Solution:**
```bash
# Reinstall dependencies
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: PostgreSQL connection errors

**Solution:**
1. Verify PostgreSQL is running: `psql -U postgres -c "SELECT 1;"`
2. Check `.env` file has correct database credentials
3. Verify PostgreSQL is on port 5432: `netstat -tulpn | grep 5432`

## 📊 Monitoring

### Check Server Status

```bash
# Terminal 3 - Monitor both servers
watch -n 1 'echo "MCP Server:" && curl -s http://localhost:8001/health | jq . && echo "" && echo "FastAPI:" && curl -s http://localhost:8000/api/health | jq .'
```

### View Logs

The servers output logs to the terminal where they're running. Key information logged:
- Server startup notifications
- Connection events
- Tool execution requests
- Errors and exceptions

## 🧪 Integration Testing

After verifying endpoints work, test the full flow:

```bash
python3 << 'EOF'
import requests
import json

# Test 1: List databases
response = requests.post(
    "http://localhost:8000/api/execute-tool",
    json={"name": "list_databases", "input": {}}
)
print("Databases:", response.json())

# Test 2: List tables in a database
response = requests.post(
    "http://localhost:8000/api/execute-tool",
    json={"name": "list_tables", "input": {"database": "postgres"}}
)
print("Tables:", response.json())

# Test 3: Get schema for a table
response = requests.post(
    "http://localhost:8000/api/execute-tool",
    json={
        "name": "get_table_schema",
        "input": {"database": "postgres", "table_name": "pg_tables"}
    }
)
print("Schema:", response.json())
EOF
```

## 🎯 Next Steps

Once the backend is verified and working:

1. **Frontend Integration** - Connect React CopilotKit to the backend
2. **Database Operations** - Test full CRUD operations
3. **Production Deployment** - Use Docker and proper environment management
4. **Performance Testing** - Load test with concurrent requests

## 📝 API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root info |
| `/api/health` | GET | Server health status |
| `/api/tools` | GET | List available tools |
| `/api/execute-tool` | POST | Execute a single tool |
| `/api/execute-tools` | POST | Execute multiple tools |
| `/api/structure` | POST | Get database structure |
| `/api/preview` | POST | Preview table data |
| `/api/schema/{db}/{table}` | GET | Get table schema |
| `/api/mcp-status` | GET | MCP server connection status |

## 📚 Documentation Files

- [main.py](main.py) - FastAPI backend server
- [mcp_server/run.py](mcp_server/run.py) - MCP server entry point
- [mcp_server/server.py](mcp_server/server.py) - Tool definitions
- [mcp_client.py](mcp_client.py) - HTTP client for MCP server
- [config.py](config.py) - Configuration management
