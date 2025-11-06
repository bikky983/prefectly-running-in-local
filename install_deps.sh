#!/bin/bash

# Nepali News Summarizer - Dependency Installation Script
# This script sets up the Python environment and installs all required dependencies

set -e  # Exit on any error

echo "🚀 Setting up Nepali News Summarizer..."

# Check if Python 3.10+ is available
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+' || echo "0.0")
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Optional: Create virtual environment (recommended)
read -p "Create a virtual environment? (y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo "✅ Virtual environment created and activated"
else
    echo "⚠️  Installing globally (virtual environment recommended)"
fi

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if playwright is uncommented in requirements.txt
if grep -q "^playwright" requirements.txt; then
    echo "🎭 Installing Playwright browsers..."
    playwright install
    echo "✅ Playwright browsers installed"
else
    echo "ℹ️  Playwright not enabled. To use browser automation, uncomment playwright in requirements.txt and run 'playwright install'"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.sample to .env: cp .env.sample .env"
echo "2. Edit .env and add your API keys"
echo "3. Run tests: pytest --maxfail=1 -q"
echo ""
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "💡 To activate the virtual environment in future sessions:"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "   source venv/Scripts/activate"
    else
        echo "   source venv/bin/activate"
    fi
fi
