#!/bin/bash

# VnExpress News Scraper - Startup Script

echo "=== VnExpress News Scraper Setup ==="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python3 -c "from database import Base, engine; Base.metadata.create_all(bind=engine); print('Database initialized')"

echo "=== Setup Complete ==="
echo ""
echo "To start the API server:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "To use the CLI tool:"
echo "  source venv/bin/activate"  
echo "  python cli.py --help"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"