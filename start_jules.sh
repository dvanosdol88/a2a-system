#!/bin/bash
# Simple Jules startup script
# Fixes the environment issue by bypassing the problematic setup script

echo "🚀 Starting Jules API Server..."
echo "================================"

# Navigate to the correct directory
cd /mnt/c/Users/david/projects-master/a2a-system

# Check if virtual environment exists
if [ ! -d "a2a-env" ]; then
    echo "❌ Virtual environment not found. Creating it..."
    python3 -m venv a2a-env
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and start server
echo "🔧 Activating virtual environment..."
source a2a-env/bin/activate

echo "🧪 Testing Flask..."
python -c "import flask; print('✅ Flask is ready:', flask.__version__)" || {
    echo "❌ Flask not found, installing..."
    pip install wheels/flask-3.1.1-py3-none-any.whl wheels/click-8.2.1-py3-none-any.whl wheels/werkzeug-3.1.3-py3-none-any.whl wheels/jinja2-3.1.6-py3-none-any.whl wheels/itsdangerous-2.2.0-py3-none-any.whl wheels/MarkupSafe-3.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl wheels/blinker-1.9.0-py3-none-any.whl
    echo "✅ Flask installed"
}

echo "🌐 Starting Jules API Server on port 5002..."
python -c "
from api.jules_server import app
app.run(host='0.0.0.0', port=5002, debug=False)
"