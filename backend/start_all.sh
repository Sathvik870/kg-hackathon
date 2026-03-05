#!/usr/bin/env bash
# Startup script for No-Code SQL Backend with MCP Server
# Runs both FastAPI backend and MCP server in proper order

set -e

echo "🚀 No-Code SQL Backend with MCP - Startup Script"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env with your database credentials${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}✅ Environment ready!${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Starting MCP Server and FastAPI Backend...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Start MCP Server in background (process substitution to avoid subshell)
echo -e "${BLUE}Starting MCP Server on port 8001...${NC}"
python mcp_server/run.py --host 0.0.0.0 --port 8001 &
MCP_PID=$!
echo -e "${GREEN}✓ MCP Server PID: $MCP_PID${NC}"

# Give MCP server time to start
sleep 2

# Start FastAPI backend
echo ""
echo -e "${BLUE}Starting FastAPI Backend on port 8000...${NC}"
python main.py &
FASTAPI_PID=$!
echo -e "${GREEN}✓ FastAPI Backend PID: $FASTAPI_PID${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Both servers starting...${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 API Endpoints:"
echo "   FastAPI Backend: http://localhost:8000"
echo "   MCP Server:      http://localhost:8001"
echo ""
echo "🛠️  Management:"
echo "   Press Ctrl+C to stop all servers"
echo "   Or kill manually:"
echo "     kill $MCP_PID   # Stop MCP Server"
echo "     kill $FASTAPI_PID  # Stop FastAPI Backend"
echo ""

# Wait for both processes
wait
