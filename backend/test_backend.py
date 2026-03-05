#!/usr/bin/env python3
"""
Test script for No-Code SQL Backend
Allows testing of all endpoints without frontend
"""

import sys
import aiohttp
import asyncio
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def test_health():
    """Test health check endpoint"""
    print(f"\n{Colors.CYAN}Testing: GET /api/health{Colors.END}")
    
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/api/health"
        async with session.get(url) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return resp.status == 200


async def test_connect(host: str, port: int, user: str, password: str, database: str):
    """Test database connection"""
    print(f"\n{Colors.CYAN}Testing: POST /api/connect{Colors.END}")
    
    payload = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "ssl": False
    }
    
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/api/connect"
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return resp.status == 200


async def test_tools():
    """Test get available tools"""
    print(f"\n{Colors.CYAN}Testing: GET /api/tools{Colors.END}")
    
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/api/tools"
        async with session.get(url) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return resp.status == 200


async def test_structure():
    """Test get database structure"""
    print(f"\n{Colors.CYAN}Testing: GET /api/structure{Colors.END}")
    
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/api/structure"
        async with session.get(url) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return resp.status == 200


async def test_execute_tool(tool_name: str, tool_input: dict):
    """Test tool execution with SSE"""
    print(f"\n{Colors.CYAN}Testing: POST /api/execute-tool{Colors.END}")
    print(f"Tool: {tool_name}")
    print(f"Input: {json.dumps(tool_input, indent=2)}")
    
    payload = {
        "name": tool_name,
        "input": tool_input
    }
    
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/api/execute-tool"
        async with session.post(url, json=payload) as resp:
            print(f"\nStatus: {resp.status}")
            print(f"Content-Type: {resp.headers.get('content-type')}")
            
            # Read SSE stream
            print(f"\n{Colors.YELLOW}SSE Stream:{Colors.END}")
            async for line in resp.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        try:
                            event = json.loads(line_str[6:])
                            print(f"  {Colors.GREEN}✓{Colors.END} {event.get('type')}: {json.dumps(event, indent=4)}")
                        except json.JSONDecodeError:
                            print(f"  {line_str}")
            
            return resp.status == 200


async def main():
    """Main test runner"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}No-Code SQL Backend - Test Suite{Colors.END}\n")
    
    # Database credentials (modify as needed)
    db_host = "localhost"
    db_port = 5432
    db_user = "postgres"
    db_password = "postgres"  # Change this to your actual password
    db_name = "postgres"
    
    tests = []
    
    # Test 1: Health check
    print(f"{Colors.BOLD}Test 1: Health Check{Colors.END}")
    try:
        result = await test_health()
        tests.append(("Health Check", result))
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        tests.append(("Health Check", False))
        print(f"\n{Colors.RED}❌ Cannot connect to backend at {BASE_URL}{Colors.END}")
        print(f"Make sure the backend is running: {Colors.BLUE}python main.py{Colors.END}")
        return
    
    # Test 2: Connect to database
    print(f"\n{Colors.BOLD}Test 2: Database Connection{Colors.END}")
    try:
        result = await test_connect(db_host, db_port, db_user, db_password, db_name)
        tests.append(("Database Connection", result))
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        tests.append(("Database Connection", False))
    
    # Test 3: Get available tools
    print(f"\n{Colors.BOLD}Test 3: Get Tools{Colors.END}")
    try:
        result = await test_tools()
        tests.append(("Get Tools", result))
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        tests.append(("Get Tools", False))
    
    # Test 4: Get database structure
    print(f"\n{Colors.BOLD}Test 4: Get Structure{Colors.END}")
    try:
        result = await test_structure()
        tests.append(("Get Structure", result))
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        tests.append(("Get Structure", False))
    
    # Test 5: Execute tool - list_databases
    print(f"\n{Colors.BOLD}Test 5: Execute Tool - list_databases{Colors.END}")
    try:
        result = await test_execute_tool("list_databases", {})
        tests.append(("Execute Tool - list_databases", result))
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        tests.append(("Execute Tool - list_databases", False))
    
    # Test 6: Execute tool - list_tables
    print(f"\n{Colors.BOLD}Test 6: Execute Tool - list_tables{Colors.END}")
    try:
        result = await test_execute_tool("list_tables", {"database": db_name})
        tests.append(("Execute Tool - list_tables", result))
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        tests.append(("Execute Tool - list_tables", False))
    
    # Summary
    print(f"\n\n{Colors.BOLD}{Colors.HEADER}Test Summary{Colors.END}")
    print("=" * 50)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {test_name}")
    
    print("=" * 50)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.GREEN}🎉 All tests passed! Backend is ready!{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check the output above.{Colors.END}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}\n")
        sys.exit(1)
