#!/bin/bash
# Quick Start Checklist for Backend

RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${BLUE}║  NO-CODE SQL BACKEND - QUICK START CHECKLIST                   ║${RESET}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════╝${RESET}\n"

# Check Python
echo -e "${YELLOW}Checking Python...${RESET}"
python3 --version
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python installed${RESET}\n"
else
    echo -e "${RED}✗ Python not found${RESET}\n"
    exit 1
fi

# Check venv
echo -e "${YELLOW}Checking Virtual Environment...${RESET}"
BACKEND_DIR="/home/vikash/Projects/kg_hackthon/kg-hackathon/backend"
if [ -d "$BACKEND_DIR/venv" ]; then
    echo -e "${GREEN}✓ Virtual environment exists${RESET}\n"
else
    echo -e "${RED}✗ Virtual environment not found${RESET}\n"
    echo "Creating venv..."
    python3 -m venv "$BACKEND_DIR/venv"
    source "$BACKEND_DIR/venv/bin/activate"
    pip install -r "$BACKEND_DIR/requirements.txt"
fi

# Check PostgreSQL
echo -e "${YELLOW}Checking PostgreSQL...${RESET}"
psql -U postgres -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL is running${RESET}\n"
else
    echo -e "${RED}✗ PostgreSQL not running${RESET}"
    echo -e "${YELLOW}Start PostgreSQL: docker-compose up -d postgres${RESET}\n"
fi

# Check ports
echo -e "${YELLOW}Checking Ports...${RESET}"
lsof -i :8000 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠ Port 8000 is in use${RESET}"
else
    echo -e "${GREEN}✓ Port 8000 is available${RESET}"
fi

lsof -i :8001 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠ Port 8001 is in use${RESET}"
else
    echo -e "${GREEN}✓ Port 8001 is available${RESET}"
fi
echo ""

# Display Next Steps
echo -e "${BOLD}${BLUE}Next Steps:${RESET}\n"
echo -e "${YELLOW}1. Terminal 1 - Start MCP Server:${RESET}"
echo -e "   cd $BACKEND_DIR"
echo -e "   source venv/bin/activate"
echo -e "   ${BOLD}python mcp_server/run.py${RESET}\n"

echo -e "${YELLOW}2. Terminal 2 - Start FastAPI:${RESET}"
echo -e "   cd $BACKEND_DIR"
echo -e "   source venv/bin/activate"
echo -e "   ${BOLD}python main.py${RESET}\n"

echo -e "${YELLOW}3. Terminal 3 - Run Tests:${RESET}"
echo -e "   cd $BACKEND_DIR"
echo -e "   ${BOLD}python3 test_everything.py${RESET}\n"

echo -e "${GREEN}${BOLD}System is ready to start!${RESET}\n"
