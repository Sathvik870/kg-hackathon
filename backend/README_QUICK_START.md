# 🚀 NO-CODE SQL BACKEND - Quick Start Guide

## 📌 What You Have

A complete backend system with:
- **MCP Server** (Port 8001) - True Model Context Protocol implementation
- **FastAPI Backend** (Port 8000) - HTTP API with 9 endpoints
- **PostgreSQL Database** - Data persistence layer
- **7 MCP Tools** - Database operations via proper MCP protocol

## ⚡ Quick Start (30 seconds)

### Option A: Fully Automated
```bash
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
bash startup.sh
```
This starts everything and runs tests automatically.

### Option B: Manual (Recommended for Learning)

**Terminal 1: Start MCP Server**
```bash
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
source venv/bin/activate
python mcp_server/run.py
```
Expected: `Uvicorn running on http://0.0.0.0:8001`

**Terminal 2: Start FastAPI Backend**
```bash
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
source venv/bin/activate
python main.py
```
Expected: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 3: Run Tests**
```bash
cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend
python3 test_everything.py
```
Expected: `✓ ALL TESTS PASSED!`

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [BACKEND_GUIDE.md](BACKEND_GUIDE.md) | Complete setup & troubleshooting guide |
| [MCP_GUIDE.md](MCP_GUIDE.md) | MCP protocol explanation |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture & flow |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.com) | Frontend integration instructions |

## 🧪 Available Tools

The backend exposes **7 MCP tools** for database operations:

1. **health_check** - Test server connectivity
2. **list_databases** - Get all available databases
3. **list_tables** - Get tables in a database
4. **get_table_schema** - Get column definitions
5. **execute_query** - Run SELECT queries
6. **update_data** - Update records
7. **preview_table** - Get first N rows

## 📡 API Endpoints

```
GET    /                           - Server root info
GET    /api/health                 - Health check
GET    /api/mcp-status             - MCP connection status
GET    /api/tools                  - List all tools
POST   /api/execute-tool           - Execute single tool
POST   /api/execute-tools          - Execute multiple tools
POST   /api/structure              - Get database structure
POST   /api/preview                - Preview table data
GET    /api/schema/{db}/{table}    - Get table schema
```

## 🔧 System Check

Run this to verify everything is ready:
```bash
bash check_system.sh
```

## 📊 Architecture

```
React Frontend (localhost:3000)
         ↓
FastAPI Backend (localhost:8000)
         ↓
HTTP Client (mcp_client.py)
         ↓
MCP Server (localhost:8001)
         ↓
PostgreSQL Database
```

## ✅ Testing

### Automated Tests
```bash
python3 test_everything.py
```
Runs 9 tests covering all endpoints and tools.

### Manual curl Tests
```bash
# Test MCP Server
curl http://localhost:8001/health

# Test FastAPI
curl http://localhost:8000/api/health

# List databases
curl -X POST http://localhost:8000/api/execute-tool \
  -H "Content-Type: application/json" \
  -d '{"name": "list_databases", "input": {}}'
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
pkill -f "main.py"
pkill -f "mcp_server/run.py"
```

### PostgreSQL Not Running
```bash
# Check if running
psql -U postgres -c "SELECT 1;"

# Or start with Docker
docker-compose up -d postgres
```

### Connection Errors
1. Ensure MCP Server started first (Terminal 1)
2. Wait 2 seconds before starting FastAPI (Terminal 2)
3. Check `.env` file has correct database credentials

## 🎯 Next Steps

1. ✅ Start both servers (completed above)
2. ✅ Run tests to verify endpoints
3. 🔄 Connect React frontend (see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md))
4. 🔄 Test database operations end-to-end
5. 🔄 Deploy to production

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| "Address already in use" | `pkill -f main.py && pkill -f mcp_server` |
| "Connection refused" | Ensure MCP Server (Terminal 1) is running |
| "ModuleNotFoundError" | `source venv/bin/activate` in Terminal 2 |
| PostgreSQL error | `docker-compose up -d postgres` |

## 🎓 Understanding the System

The backend implements **true MCP protocol** (Model Context Protocol):

- **MCP Server (Port 8001)**: Standalone Starlette app with 7 tools defined
- **MCP Tools**: Database operations exposed via `@mcp.tool()` decorators
- **FastAPI Router (Port 8000)**: HTTP gateway for frontend requests
- **HTTP Client**: Bridges FastAPI and MCP Server via direct HTTP calls

This is **NOT** a simple tool wrapper - it's a proper MCP implementation that can be:
- Connected to Claude API
- Used by multiple clients
- Scaled horizontally
- Integrated with MCP ecosystem tools

---

**Backend Ready!** 🎉

Start with "Option A: Fully Automated" above if this is your first time.
