#!/bin/bash
# FlowForge Startup Script
# Starts all components for operational FlowForge system

echo "🎨 Starting FlowForge A2A System"
echo "================================="

# Activate virtual environment
source a2a-env/bin/activate

# Start Jules API server (if not running)
if ! pgrep -f "jules_server.py" > /dev/null; then
    echo "🚀 Starting Jules API server..."
    nohup python api/jules_server.py > server.log 2>&1 &
    sleep 2
fi

# Start Dashboard (if not running)
if ! pgrep -f "dashboard_server.py" > /dev/null; then
    echo "📊 Starting monitoring dashboard..."
    nohup python monitoring/dashboard_server.py > dashboard.log 2>&1 &
    sleep 2
fi

# Start FlowForge UI (if not running)
if ! pgrep -f "ui/flowforge/server.py" > /dev/null; then
    echo "🎨 Starting FlowForge UI..."
    nohup python ui/flowforge/server.py > ui/flowforge/server.log 2>&1 &
    sleep 2
fi

# Start CODEX agent (if not running)
if ! pgrep -f "codex_agent.py" > /dev/null; then
    echo "🤖 Starting CODEX agent..."
    cd agents
    nohup python codex_agent.py > codex_agent.log 2>&1 &
    cd ..
    sleep 2
fi

echo ""
echo "✅ FlowForge System Status:"
echo "   📡 Jules API:      http://localhost:5000"
echo "   📊 Dashboard:      http://localhost:5001" 
echo "   🎨 FlowForge UI:   http://localhost:5002"
echo "   🤖 CODEX Agent:    Running"
echo ""
echo "🎯 Users can now submit tasks at: http://localhost:5002"
echo "📱 Share this URL for non-technical users to access FlowForge"
echo ""
echo "Press Ctrl+C to stop all services..."

# Keep script running
while true; do
    sleep 30
done