#!/usr/bin/env bash
# Quick Start Script for No-Code SQL Backend
# Automates environment setup and startup

set -e  # Exit on error

echo "🚀 No-Code SQL Backend - Quick Start"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
echo "✅ Pip upgraded"

echo ""

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your database credentials"
    echo ""
    exit 0
else
    echo "✅ .env file found"
fi

echo ""

# Final summary
echo "⚡ Setup Complete!"
echo "=================================="
echo "To start the backend, run:"
echo ""
echo "  source venv/bin/activate    # Activate virtual environment"
echo "  python main.py              # Start the server"
echo ""
echo "The backend will be available at http://localhost:8000"
echo ""
