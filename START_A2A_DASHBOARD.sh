#!/bin/bash
# Created by: UC (Ubuntu Claude)
# Date: 2025-07-22 10:38
# Purpose: Quick start script for a2a monitoring dashboard
# Task/Context: Minimal manual intervention to monitor agents

echo "🚀 Starting a2a Monitoring Dashboard..."

cd /mnt/c/Users/david/projects-master/a2a-system

# Activate venv if needed
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

# Kill any existing dashboard
pkill -f "a2a_monitor.py" 2>/dev/null

# Start dashboard
python dashboard/a2a_monitor.py &

echo ""
echo "✅ Dashboard started!"
echo "📊 Open in browser: http://localhost:8888"
echo ""
echo "Features:"
echo "- Monitor Jules API, AI Connector, Redis status"
echo "- Submit tasks directly from web interface"
echo "- View task queue and processing metrics"
echo "- Real-time updates every 2 seconds"
echo ""
echo "To stop: pkill -f a2a_monitor.py"