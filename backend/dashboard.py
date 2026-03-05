#!/usr/bin/env python3
"""
Backend Status Dashboard
Real-time monitoring of both servers
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def check_endpoint(url: str, timeout: int = 2) -> Dict[str, Any]:
    """Check if an endpoint is healthy"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            try:
                data = response.json()
                return {"status": "healthy", "data": data}
            except:
                return {"status": "healthy", "data": response.text[:50]}
        else:
            return {"status": "error", "code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"status": "offline"}
    except requests.exceptions.Timeout:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_mcp_tools() -> Optional[list]:
    """Get list of available tools"""
    try:
        response = requests.get("http://localhost:8000/api/tools", timeout=2)
        if response.status_code == 200:
            tools = response.json()
            if isinstance(tools, list):
                return tools
    except:
        pass
    return None

def format_status(status: str) -> str:
    """Format status with color"""
    if status == "healthy" or status == "running":
        return f"{Colors.GREEN}✓ {status.upper()}{Colors.END}"
    elif status == "offline":
        return f"{Colors.RED}✗ OFFLINE{Colors.END}"
    elif status == "timeout":
        return f"{Colors.YELLOW}⚠ TIMEOUT{Colors.END}"
    else:
        return f"{Colors.RED}✗ ERROR{Colors.END}"

def main():
    """Main dashboard function"""
    clear = lambda: os.system('clear')
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔" + "="*68 + "╗")
    print("║  NO-CODE SQL BACKEND - STATUS DASHBOARD                         ║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.END}\n")
    
    # MCP Server Status
    print_header("MCP SERVER (Port 8001)")
    mcp_status = check_endpoint("http://localhost:8001/health")
    mcp_root = check_endpoint("http://localhost:8001/")
    
    print(f"MCP Server: {format_status(mcp_status['status'])}")
    if mcp_status['status'] == "healthy":
        print(f"  Server: {mcp_status.get('data', {}).get('server', 'N/A')}")
        print(f"  Version: {mcp_status.get('data', {}).get('version', 'N/A')}")
    
    # FastAPI Status
    print_header("FastAPI BACKEND (Port 8000)")
    fastapi_status = check_endpoint("http://localhost:8000/api/health")
    
    print(f"FastAPI: {format_status(fastapi_status['status'])}")
    if fastapi_status['status'] == "healthy":
        data = fastapi_status.get('data', {})
        print(f"  Status: {data.get('status', 'N/A')}")
        print(f"  FastAPI Connected: {Colors.GREEN if data.get('fastapi_connected') else Colors.RED}{data.get('fastapi_connected')}{Colors.END}")
        print(f"  MCP Connected: {Colors.GREEN if data.get('mcp_connected') else Colors.RED}{data.get('mcp_connected')}{Colors.END}")
    
    # Available Tools
    print_header("AVAILABLE TOOLS")
    tools = get_mcp_tools()
    if tools:
        print(f"Total Tools: {Colors.BOLD}{len(tools)}{Colors.END}\n")
        for i, tool in enumerate(tools, 1):
            name = tool.get('name', 'Unknown')
            desc = tool.get('description', '')[:50]
            print(f"  {i}. {Colors.CYAN}{name}{Colors.END}")
            if desc:
                print(f"     {desc}...")
    else:
        print(f"{Colors.YELLOW}Could not retrieve tools{Colors.END}")
    
    # Connection Test
    print_header("CONNECTION TEST")
    try:
        response = requests.post(
            "http://localhost:8000/api/execute-tool",
            json={"name": "health_check", "input": {}},
            timeout=5
        )
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ Tool execution working{Colors.END}")
            print(f"  Response: {json.dumps(response.json(), indent=2)[:100]}...")
        else:
            print(f"{Colors.RED}✗ Tool execution failed{Colors.END}")
            print(f"  Status: {response.status_code}")
    except Exception as e:
        print(f"{Colors.RED}✗ Connection error: {str(e)}{Colors.END}")
    
    # Summary
    print_header("SUMMARY")
    
    mcp_ok = mcp_status['status'] in ['healthy', 'running']
    fastapi_ok = fastapi_status['status'] in ['healthy', 'running']
    
    if mcp_ok and fastapi_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL SYSTEMS OPERATIONAL{Colors.END}\n")
        print("Backend is ready for:")
        print("  • Testing with curl")
        print("  • Frontend integration")
        print("  • Database operations")
        print(f"\n{Colors.CYAN}API Base URL: http://localhost:8000{Colors.END}")
        print(f"{Colors.CYAN}API Docs: http://localhost:8000/docs (if available){Colors.END}\n")
    elif mcp_ok:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Partial System Status{Colors.END}\n")
        print(f"  MCP Server: {Colors.GREEN}OK{Colors.END}")
        print(f"  FastAPI Backend: {Colors.RED}OFFLINE{Colors.END}")
        print("\nStart FastAPI Backend in Terminal 2")
    elif fastapi_ok:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Partial System Status{Colors.END}\n")
        print(f"  MCP Server: {Colors.RED}OFFLINE{Colors.END}")
        print(f"  FastAPI Backend: {Colors.GREEN}OK{Colors.END}")
        print("\nStart MCP Server in Terminal 1")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ ALL SYSTEMS OFFLINE{Colors.END}\n")
        print("Start both servers:")
        print("  Terminal 1: python mcp_server/run.py")
        print("  Terminal 2: python main.py")
    
    print("")

if __name__ == "__main__":
    import os
    try:
        main()
        
        # Optional: continuous monitoring
        if len(sys.argv) > 1 and sys.argv[1] == "--watch":
            print(f"\n{Colors.YELLOW}Watching for changes (Ctrl+C to exit)...{Colors.END}\n")
            while True:
                time.sleep(3)
                os.system('clear')
                print(f"{Colors.BOLD}{Colors.CYAN}")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Status Check")
                print(f"{Colors.END}\n")
                
                mcp_status = check_endpoint("http://localhost:8001/health")
                fastapi_status = check_endpoint("http://localhost:8000/api/health")
                
                print(f"MCP Server: {format_status(mcp_status['status'])}")
                print(f"FastAPI: {format_status(fastapi_status['status'])}")
                
                if mcp_status['status'] in ['healthy', 'running'] and fastapi_status['status'] in ['healthy', 'running']:
                    print(f"\n{Colors.GREEN}✓ All systems healthy{Colors.END}")
                else:
                    print(f"\n{Colors.RED}✗ System check needed{Colors.END}")
                
                print(f"\n{Colors.YELLOW}Next check in 3 seconds...{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Dashboard closed{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}\n")
        sys.exit(1)
