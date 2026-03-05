#!/usr/bin/env bash
# Quick Verification Script for MCP Backend
# Tests all components and verifies proper setup

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  No-Code SQL Backend with MCP - Verification Script           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check service
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -m 2 "${url}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} ${name}: ${url}"
        return 0
    else
        echo -e "${RED}✗${NC} ${name}: ${url}"
        return 1
    fi
}

# Function to test endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo -e "\n${BLUE}Testing: ${description}${NC}"
    echo -e "  ${YELLOW}${method} ${url}${NC}"
    
    if [ -z "$data" ]; then
        response=$(curl -s -X "${method}" "${url}")
    else
        response=$(curl -s -X "${method}" "${url}" \
            -H "Content-Type: application/json" \
            -d "${data}")
    fi
    
    echo -e "  Response: ${response:0:100}..."
    
    if echo "$response" | grep -iq "error\|fail"; then
        echo -e "  ${RED}⚠️  Possible error in response${NC}"
        return 1
    else
        echo -e "  ${GREEN}✓ OK${NC}"
        return 0
    fi
}

echo -e "${BLUE}1. Checking Services...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

services_ok=true

if ! check_service "http://localhost:8001/health" "MCP Server"; then
    services_ok=false
fi

if ! check_service "http://localhost:8000/api/health" "FastAPI Backend"; then
    services_ok=false
fi

if [ "$services_ok" = false ]; then
    echo ""
    echo -e "${RED}❌ Services not running!${NC}"
    echo -e "Start servers with: ${YELLOW}bash start_all.sh${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Both services are running!${NC}"

# Test API Endpoints
echo ""
echo -e "${BLUE}2. Testing API Endpoints...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "GET" "http://localhost:8000/" "" "Root endpoint"
test_endpoint "GET" "http://localhost:8000/api/health" "" "Health check"
test_endpoint "GET" "http://localhost:8000/api/mcp-status" "" "MCP Status"
test_endpoint "GET" "http://localhost:8000/api/tools" "" "Get tools"

# Test MCP Server Health
echo ""
echo -e "${BLUE}3. Testing MCP Server Health...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

response=$(curl -s http://localhost:8001/health)
echo -e "  Response: ${response}"

if echo "$response" | grep -q "healthy\|NLTOSQL"; then
    echo -e "  ${GREEN}✓ MCP Server is healthy${NC}"
else
    echo -e "  ${RED}⚠️  MCP Server response unclear${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Summary                                                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "🌐 FastAPI Backend:      http://localhost:8000"
echo "🛠️  MCP Server:           http://localhost:8001"
echo ""
echo "📍 Key Endpoints:"
echo "   API Tools:             GET  /api/tools"
echo "   MCP Status:            GET  /api/mcp-status"
echo "   Execute Tool:          POST /api/execute-tool"
echo "   Get Structure:         GET  /api/structure"
echo ""
echo "📚 Documentation:"
echo "   MCP Architecture:      MCP_GUIDE.md"
echo "   Full Documentation:    Readme.md"
echo "   API Integration:       INTEGRATION_GUIDE.md"
echo ""
echo -e "${GREEN}✅ Verification complete!${NC}"
echo ""
