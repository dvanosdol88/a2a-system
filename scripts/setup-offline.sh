#!/bin/bash
# A2A Offline Environment Setup Script
# Created: 2025-07-04
# Purpose: Configure dependencies for CODEX offline environment

set -e

echo "🚀 Setting up A2A Environment (Offline Mode)..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.12+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "a2a-env" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv a2a-env
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source a2a-env/bin/activate

# Install dependencies from local wheels
echo "📥 Installing A2A dependencies from local wheels..."
pip install --no-index --find-links wheels/ Flask requests pytest

# Verify installation
echo "✅ Verifying installation..."
python -c "import flask; print(f'Flask {flask.__version__} installed')"
python -c "import requests; print(f'Requests {requests.__version__} installed')"
python -c "import pytest; print(f'Pytest {pytest.__version__} installed')"

echo "🎯 A2A Offline Environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  source a2a-env/bin/activate"
echo ""
echo "To start Jules API server:"
echo "  python api/jules_server.py"
echo ""
echo "To run tests:"
echo "  pytest tests/"
echo ""
echo "📦 All dependencies are now available offline!"