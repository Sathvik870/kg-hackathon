#!/usr/bin/env python3
"""
Interactive Backend Setup Guide
Shows step-by-step instructions with pretty formatting
"""

import os
import subprocess
import sys

class Style:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_title(text):
    """Print main title"""
    print(f"\n{Style.BOLD}{Style.CYAN}")
    print("╔" + "="*68 + "╗")
    print(f"║  {text:<64}  ║")
    print("╚" + "="*68 + "╝")
    print(f"{Style.END}\n")

def print_section(num, title):
    """Print section header"""
    print(f"{Style.BOLD}{Style.BLUE}[{num}] {title}{Style.END}\n")

def print_command(cmd, description=""):
    """Print a command to run"""
    print(f"{Style.YELLOW}Command:{Style.END}")
    print(f"  {Style.BOLD}{cmd}{Style.END}")
    if description:
        print(f"\n{Style.CYAN}Info:{Style.END}")
        print(f"  {description}")
    print()

def print_expected(output):
    """Print expected output"""
    print(f"{Style.GREEN}Expected Output:{Style.END}")
    for line in output.split("\n"):
        print(f"  {line}")
    print()

def print_tip(tip):
    """Print a tip"""
    print(f"{Style.YELLOW}💡 Tip:{Style.END} {tip}\n")

def print_warning(warning):
    """Print a warning"""
    print(f"{Style.RED}⚠️  Warning:{Style.END} {warning}\n")

def print_step(text):
    """Print a simple step"""
    print(f"{Style.GREEN}✓{Style.END} {text}")

def main():
    print_title("NO-CODE SQL BACKEND - SETUP GUIDE")
    
    # Prerequisites
    print_section("0", "Prerequisites Check")
    print("Before starting, run this to verify everything is ready:\n")
    print_command(
        "cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend && bash check_system.sh",
        "This will check Python, virtual environment, and PostgreSQL"
    )
    
    input(f"{Style.BOLD}Press Enter to continue...{Style.END}\n")
    
    # Option A
    print_title("OPTION A: Fully Automated (Recommended for First Time)")
    
    print_section("A1", "One Command Setup")
    print("This does everything automatically:\n")
    print_command(
        "cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend && bash startup.sh",
        "This will:\n  • Kill any existing processes\n  • Start MCP Server\n  • Start FastAPI Backend\n  • Run tests automatically"
    )
    print_tip("This is the easiest way to get started!")
    input(f"{Style.BOLD}Press Enter to continue...{Style.END}\n")
    
    # Option B
    print_title("OPTION B: Manual Setup (Recommended for Learning)")
    
    print_section("B1", "Terminal 1 - Start MCP Server")
    print("Open a new terminal and run:\n")
    print_command(
        "cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend && source venv/bin/activate && python mcp_server/run.py",
        "This starts the MCP server on port 8001"
    )
    print_expected("""Uvicorn running on http://0.0.0.0:8001
Available Tools (MCP Protocol):
  1. list_databases
  2. list_tables
  ... (7 total tools)""")
    print_tip("Wait for 'Uvicorn running' message before proceeding to Terminal 2")
    
    input(f"{Style.BOLD}Press Enter when MCP Server is running...{Style.END}\n")
    
    print_section("B2", "Terminal 2 - Start FastAPI Backend")
    print("Open another new terminal and run:\n")
    print_command(
        "cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend && source venv/bin/activate && python main.py",
        "This starts the FastAPI backend on port 8000"
    )
    print_expected("""✓ Connected to MCP server at http://localhost:8001
📦 Loaded 7 tools from MCP server
Uvicorn running on http://0.0.0.0:8000""")
    print_tip("Wait for 'Uvicorn running' message before proceeding to Terminal 3")
    print_warning("Make sure Terminal 1 is still running!")
    
    input(f"{Style.BOLD}Press Enter when FastAPI is running...{Style.END}\n")
    
    print_section("B3", "Terminal 3 - Run Tests")
    print("Open a third terminal and run:\n")
    print_command(
        "cd /home/vikash/Projects/kg_hackthon/kg-hackathon/backend && python3 test_everything.py",
        "This runs 9 automated tests to verify everything works"
    )
    print_expected("""
======================================================================
  Test Results Summary
======================================================================

Total Tests: 9
Passed: 9
Failed: 0
Success Rate: 100.0%

✓ ALL TESTS PASSED! Backend is working correctly.""")
    
    input(f"{Style.BOLD}Press Enter to continue...{Style.END}\n")
    
    # Troubleshooting
    print_title("TROUBLESHOOTING QUICK REFERENCE")
    
    print_section("T1", "Port Already in Use")
    print_command(
        "pkill -f 'main.py' && pkill -f 'mcp_server/run.py' && sleep 2",
        "Kills any existing processes and waits 2 seconds"
    )
    
    print_section("T2", "PostgreSQL Not Running")
    print_command(
        "docker-compose up -d postgres",
        "Starts PostgreSQL database with Docker"
    )
    
    print_section("T3", "Virtual Environment Issues")
    print_command(
        "source venv/bin/activate && pip install -r requirements.txt",
        "Reinstalls all dependencies"
    )
    
    # Quick Test Commands
    print_title("QUICK TEST COMMANDS")
    
    print_section("Q1", "Test MCP Server")
    print_command("curl http://localhost:8001/health")
    print("Should return JSON with status: healthy\n")
    
    print_section("Q2", "Test FastAPI")
    print_command("curl http://localhost:8000/api/health")
    print("Should return JSON with status: healthy\n")
    
    print_section("Q3", "List Available Tools")
    print_command("curl http://localhost:8000/api/tools")
    print("Should return JSON array with 7 tools\n")
    
    print_section("Q4", "Execute a Tool")
    print_command(
        """curl -X POST http://localhost:8000/api/execute-tool \\
  -H "Content-Type: application/json" \\
  -d '{"name": "list_databases", "input": {}}'""",
        "Executes the list_databases tool"
    )
    
    # Dashboard
    print_title("REAL-TIME MONITORING")
    
    print_section("M1", "Status Dashboard")
    print_command(
        "python3 dashboard.py",
        "Shows real-time status of both servers"
    )
    print_command(
        "python3 dashboard.py --watch",
        "Continuous monitoring mode (refreshes every 3 seconds)"
    )
    
    # Documentation
    print_title("FULL DOCUMENTATION")
    
    print("\nFor more detailed information, see these files:\n")
    docs = [
        ("README_QUICK_START.md", "5-minute quick start guide"),
        ("BACKEND_GUIDE.md", "Complete setup & troubleshooting"),
        ("IMPLEMENTATION_COMPLETE.md", "What was delivered"),
        ("test_everything.py", "Automated test suite"),
    ]
    
    for filename, description in docs:
        print(f"  📄 {Style.CYAN}{filename}{Style.END}")
        print(f"     └─ {description}")
    
    # Final Steps
    print_title("YOU'RE READY TO START!")
    
    print(f"{Style.GREEN}")
    print("✅ Backend is fully implemented")
    print("✅ All files are in place")
    print("✅ Testing scripts ready")
    print(f"{Style.END}")
    
    print(f"\n{Style.BOLD}Choose one:{Style.END}\n")
    print(f"  {Style.BOLD}A){Style.END} Run: {Style.YELLOW}bash startup.sh{Style.END} (fully automated)")
    print(f"  {Style.BOLD}B){Style.END} Follow manual steps in Terminal 1, 2, 3")
    print(f"  {Style.BOLD}C){Style.END} Run: {Style.YELLOW}python3 dashboard.py{Style.END} (check status first)\n")

if __name__ == "__main__":
    try:
        main()
        print(f"\n{Style.GREEN}Setup guide complete!{Style.END}\n")
    except KeyboardInterrupt:
        print(f"\n{Style.YELLOW}Guide interrupted{Style.END}\n")
        sys.exit(0)
