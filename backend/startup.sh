#!/bin/bash
# Complete Backend Startup Script
# This script manages both the MCP Server and FastAPI Backend

set -e

REPO_DIR="/home/vikash/Projects/kg_hackthon/kg-hackathon"
BACKEND_DIR="$REPO_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${BLUE}║  NO-CODE SQL BACKEND - STARTUP MANAGER                         ║${RESET}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════╝${RESET}\n"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${RESET}"
    pkill -f "mcp_server/run.py" 2>/dev/null || true
    pkill -f "main.py" 2>/dev/null || true
    sleep 1
}

# Set trap for cleanup
trap cleanup EXIT

# Step 1: Kill existing processes
echo -e "${YELLOW}[1/4] Killing existing processes...${RESET}"
pkill -f "main.py" 2>/dev/null || true
pkill -f "mcp_server/run.py" 2>/dev/null || true
sleep 2

# Check ports
echo -e "${YELLOW}Checking ports...${RESET}"
lsof -i :8000 2>/dev/null && {
    echo -e "${RED}Port 8000 is in use. Waiting...${RESET}"
    sleep 3
} || true

lsof -i :8001 2>/dev/null && {
    echo -e "${RED}Port 8001 is in use. Waiting...${RESET}"
    sleep 3
} || true

echo -e "${GREEN}✓ Ports are clear${RESET}\n"

# Step 2: Setup environment
echo -e "${YELLOW}[2/4] Setting up environment...${RESET}"
cd "$BACKEND_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${RESET}"
    python3 -m venv venv
fi

source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${RESET}\n"

# Step 3: Start MCP Server
echo -e "${YELLOW}[3/4] Starting MCP Server (port 8001)...${RESET}"
echo -e "${BLUE}Run this in Terminal 1:${RESET}"
echo -e "  cd $BACKEND_DIR"
echo -e "  source venv/bin/activate"
echo -e "  ${BOLD}python mcp_server/run.py${RESET}\n"

echo -e "${YELLOW}Press Enter when MCP Server is running...${RESET}"
read

# Step 4: Start FastAPI Backend
echo -e "${YELLOW}[4/4] Starting FastAPI Backend (port 8000)...${RESET}"
echo -e "${BLUE}Run this in Terminal 2:${RESET}"
echo -e "  cd $BACKEND_DIR"
echo -e "  source venv/bin/activate"
echo -e "  ${BOLD}python main.py${RESET}\n"

echo -e "${YELLOW}Press Enter when FastAPI Backend is running...${RESET}"
read

# Step 5: Run tests
echo -e "\n${YELLOW}[BONUS] Running test suite...${RESET}"
cd "$BACKEND_DIR"
python3 test_everything.py

echo -e "\n${GREEN}${BOLD}✓ Backend startup complete!${RESET}"
echo -e "${BLUE}MCP Server: http://localhost:8001${RESET}"
echo -e "${BLUE}FastAPI: http://localhost:8000${RESET}\n"

# Keep script running
echo -e "${YELLOW}Press Ctrl+C to stop...${RESET}"
wait
