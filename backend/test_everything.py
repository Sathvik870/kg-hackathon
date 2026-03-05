#!/usr/bin/env python3
"""
Complete Backend Testing Script
Tests all endpoints and verifies the system is working correctly
"""

import requests
import json
import time
import sys

# Colors for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Configuration
MCP_URL = "http://localhost:8001"
FASTAPI_URL = "http://localhost:8000"

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}  {text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def test_endpoint(method, url, name, data=None):
    """Test an HTTP endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return False
        
        if response.status_code == 200:
            print(f"{GREEN}✓ {name}{RESET}")
            print(f"  Status: {response.status_code}")
            try:
                print(f"  Response: {json.dumps(response.json(), indent=2)[:200]}...")
            except:
                print(f"  Response: {str(response.text)[:200]}...")
            return True
        else:
            print(f"{RED}✗ {name}{RESET}")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"{RED}✗ {name} - Connection refused{RESET}")
        return False
    except Exception as e:
        print(f"{RED}✗ {name} - {str(e)}{RESET}")
        return False

def main():
    """Run all tests"""
    print(f"\n{BOLD}{BLUE}")
    print("╔" + "="*68 + "╗")
    print("║  NO-CODE SQL BACKEND - COMPLETE TEST SUITE                        ║")
    print("╚" + "="*68 + "╝")
    print(f"{RESET}\n")
    
    tests_passed = 0
    tests_failed = 0
    
    # === Test MCP Server ===
    print_header("Testing MCP Server (Port 8001)")
    
    if test_endpoint("GET", f"{MCP_URL}/", "MCP Server Root", None):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", f"{MCP_URL}/health", "MCP Server Health", None):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Wait for FastAPI to connect
    time.sleep(1)
    
    # === Test FastAPI Backend ===
    print_header("Testing FastAPI Backend (Port 8000)")
    
    if test_endpoint("GET", f"{FASTAPI_URL}/", "FastAPI Root", None):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", f"{FASTAPI_URL}/api/health", "FastAPI Health Check", None):
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_endpoint("GET", f"{FASTAPI_URL}/api/mcp-status", "MCP Connection Status", None):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # === Test Tool Discovery ===
    print_header("Testing Tool Discovery")
    
    if test_endpoint("GET", f"{FASTAPI_URL}/api/tools", "Get Available Tools", None):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # === Test Tool Execution ===
    print_header("Testing Tool Execution")
    
    # Test 1: health_check
    tool_data = {
        "name": "health_check",
        "input": {}
    }
    if test_endpoint("POST", f"{FASTAPI_URL}/api/execute-tool", "Execute: health_check", tool_data):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 2: list_databases
    tool_data = {
        "name": "list_databases",
        "input": {}
    }
    if test_endpoint("POST", f"{FASTAPI_URL}/api/execute-tool", "Execute: list_databases", tool_data):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 3: list_tables
    tool_data = {
        "name": "list_tables",
        "input": {"database": "postgres"}
    }
    if test_endpoint("POST", f"{FASTAPI_URL}/api/execute-tool", "Execute: list_tables", tool_data):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # === Test Results ===
    print_header("Test Results Summary")
    
    total = tests_passed + tests_failed
    passed_pct = (tests_passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {GREEN}{tests_passed}{RESET}")
    print(f"Failed: {RED}{tests_failed}{RESET}")
    print(f"Success Rate: {passed_pct:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED! Backend is working correctly.{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ {tests_failed} test(s) failed. See details above.{RESET}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}\n")
        sys.exit(1)
