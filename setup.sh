#!/bin/bash
# Setup script for AI Healthcare Assistant Chatbot
# This script sets up the virtual environment and installs dependencies

echo "=========================================="
echo "AI Healthcare Assistant Chatbot Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "Error: Python is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment (instructions for different OS)
echo ""
echo "Virtual environment created successfully!"
echo ""
echo "To activate the virtual environment:"
echo "  Windows (PowerShell): venv\\Scripts\\Activate.ps1"
echo "  Windows (CMD): venv\\Scripts\\activate.bat"
echo "  Linux/Mac: source venv/bin/activate"
echo ""

# For Windows PowerShell execution
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Activating virtual environment (Windows)..."
    source venv/Scripts/activate
else
    echo "Activating virtual environment (Unix)..."
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Add your Gemini API key to .env"
echo "3. Run: python backend/main.py"
echo ""
