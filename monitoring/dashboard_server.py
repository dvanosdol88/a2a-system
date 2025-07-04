"""
A2A Monitoring Dashboard Server
Real-time monitoring and mission control interface for Jules
"""

from flask import Flask, render_template, jsonify, request
import json
import time
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests
from typing import Dict, List, Any, Optional
import statistics

from shared.message_types import A2AMessage, MessageType


class A2AMonitor:
    """Real-time A2A system monitoring"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5000"):
        self.api_base_url = api_base_url
        self.metrics_history = []
        self.alerts = []
        self.system_status = {
            "status": "unknown",
            "last_check": None,
            "uptime_start": None,
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0.0
        }
        self.performance_data = {
            "response_times": [],
            "request_counts": [],
            "error_rates": [],
            "timestamps": []
        }
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start continuous monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("📊 A2A monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️ A2A monitoring stopped")
    
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                self._collect_metrics()
                self._check_alerts()
                time.sleep(10)  # Monitor every 10 seconds
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(30)  # Longer delay on error
    
    def _collect_metrics(self):
        """Collect system metrics"""
        timestamp = datetime.now(timezone.utc)
        
        try:
            # Health check
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Update system status
                if self.system_status["uptime_start"] is None:
                    self.system_status["uptime_start"] = timestamp
                
                self.system_status.update({
                    "status": "healthy",
                    "last_check": timestamp,
                    "server_time": health_data.get("server_time"),
                })
                
                # Collect task metrics
                task_response = requests.get(f"{self.api_base_url}/tasks", timeout=5)
                if task_response.status_code == 200:
                    tasks = task_response.json()
                    task_count = len(tasks)
                else:
                    task_count = 0
                
                # Store metrics
                metric = {
                    "timestamp": timestamp.isoformat(),
                    "response_time": response_time,
                    "task_count": task_count,
                    "status": "healthy",
                    "server_time": health_data.get("server_time")
                }
                
                self.metrics_history.append(metric)
                
                # Update performance data
                self.performance_data["response_times"].append(response_time)
                self.performance_data["request_counts"].append(task_count)
                self.performance_data["error_rates"].append(0)
                self.performance_data["timestamps"].append(timestamp.isoformat())
                
                # Keep only last 100 data points
                for key in self.performance_data:
                    if len(self.performance_data[key]) > 100:
                        self.performance_data[key] = self.performance_data[key][-100:]
                
                # Update averages
                if self.performance_data["response_times"]:
                    self.system_status["avg_response_time"] = statistics.mean(
                        self.performance_data["response_times"][-10:]  # Last 10 measurements
                    )
                
            else:
                self._record_error(timestamp, f"HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self._record_error(timestamp, f"Connection error: {str(e)}")
        except Exception as e:
            self._record_error(timestamp, f"Monitoring error: {str(e)}")
    
    def _record_error(self, timestamp: datetime, error: str):
        """Record system error"""
        self.system_status.update({
            "status": "error",
            "last_check": timestamp,
            "last_error": error
        })
        
        self.system_status["total_errors"] += 1
        
        # Add error metric
        metric = {
            "timestamp": timestamp.isoformat(),
            "response_time": None,
            "task_count": None,
            "status": "error",
            "error": error
        }
        self.metrics_history.append(metric)
        
        # Update performance data
        self.performance_data["error_rates"].append(1)
        self.performance_data["timestamps"].append(timestamp.isoformat())
        
        # Create alert
        self._create_alert("error", f"System error: {error}", timestamp)
    
    def _check_alerts(self):
        """Check for alert conditions"""
        if not self.performance_data["response_times"]:
            return
        
        current_time = datetime.now(timezone.utc)
        
        # Check response time
        recent_response_times = self.performance_data["response_times"][-5:]  # Last 5 measurements
        if recent_response_times:
            avg_response_time = statistics.mean(recent_response_times)
            if avg_response_time > 1000:  # > 1 second
                self._create_alert(
                    "warning",
                    f"High response time: {avg_response_time:.0f}ms",
                    current_time
                )
        
        # Check error rate
        recent_errors = self.performance_data["error_rates"][-10:]  # Last 10 measurements
        if recent_errors:
            error_rate = sum(recent_errors) / len(recent_errors) * 100
            if error_rate > 10:  # > 10% error rate
                self._create_alert(
                    "critical",
                    f"High error rate: {error_rate:.1f}%",
                    current_time
                )
    
    def _create_alert(self, severity: str, message: str, timestamp: datetime):
        """Create system alert"""
        alert = {
            "id": len(self.alerts) + 1,
            "severity": severity,
            "message": message,
            "timestamp": timestamp.isoformat(),
            "acknowledged": False
        }
        self.alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
        
        print(f"🚨 ALERT [{severity.upper()}]: {message}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        current_time = datetime.now(timezone.utc)
        
        # Calculate uptime
        uptime_seconds = 0
        if self.system_status["uptime_start"]:
            uptime_delta = current_time - self.system_status["uptime_start"]
            uptime_seconds = uptime_delta.total_seconds()
        
        # Get recent metrics
        recent_metrics = self.metrics_history[-10:] if self.metrics_history else []
        
        # Calculate statistics
        response_times = [m["response_time"] for m in recent_metrics if m["response_time"] is not None]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Get unacknowledged alerts
        active_alerts = [a for a in self.alerts if not a["acknowledged"]]
        
        return {
            "system_status": {
                **self.system_status,
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": self._format_uptime(uptime_seconds),
                "current_time": current_time.isoformat()
            },
            "performance_metrics": {
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "min_response_time": min_response_time,
                "total_metrics": len(self.metrics_history),
                "healthy_metrics": len([m for m in self.metrics_history if m["status"] == "healthy"])
            },
            "performance_data": self.performance_data,
            "recent_metrics": recent_metrics,
            "alerts": {
                "total": len(self.alerts),
                "active": len(active_alerts),
                "recent": self.alerts[-5:] if self.alerts else []
            }
        }
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                return True
        return False
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}d {hours}h"


# Flask Dashboard App
app = Flask(__name__)
monitor = A2AMonitor()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard-data')
def dashboard_data():
    """Get dashboard data API"""
    return jsonify(monitor.get_dashboard_data())

@app.route('/api/system-status')
def system_status():
    """Get system status API"""
    return jsonify(monitor.system_status)

@app.route('/api/alerts')
def alerts():
    """Get alerts API"""
    return jsonify(monitor.alerts)

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge alert API"""
    success = monitor.acknowledge_alert(alert_id)
    return jsonify({"success": success})

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start monitoring API"""
    monitor.start_monitoring()
    return jsonify({"message": "Monitoring started"})

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring API"""
    monitor.stop_monitoring()
    return jsonify({"message": "Monitoring stopped"})

@app.route('/health')
def health():
    """Dashboard health check"""
    return jsonify({
        "status": "ok",
        "service": "a2a_dashboard",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "monitoring_active": monitor.monitoring_active
    })


# Create templates directory and basic template
def create_dashboard_template():
    """Create basic dashboard HTML template"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A2A System Dashboard - Mission Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #2a2a2a; border-radius: 8px; padding: 20px; border-left: 4px solid #4CAF50; }
        .card.warning { border-left-color: #FF9800; }
        .card.error { border-left-color: #f44336; }
        .metric { font-size: 2em; font-weight: bold; color: #4CAF50; }
        .label { color: #bbb; font-size: 0.9em; }
        .status-healthy { color: #4CAF50; }
        .status-error { color: #f44336; }
        .alert { padding: 10px; margin: 5px 0; border-radius: 4px; background: #333; }
        .alert.warning { background: #FF9800; color: #000; }
        .alert.critical { background: #f44336; }
        h1 { text-align: center; margin-bottom: 30px; }
        h2 { border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .refresh-btn { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .refresh-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>🎮 A2A System Dashboard - Mission Control</h1>
    
    <div style="text-align: center; margin-bottom: 20px;">
        <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh Dashboard</button>
        <button class="refresh-btn" onclick="startMonitoring()">▶️ Start Monitoring</button>
        <button class="refresh-btn" onclick="stopMonitoring()">⏹️ Stop Monitoring</button>
    </div>
    
    <div class="dashboard">
        <div class="card">
            <h2>System Status</h2>
            <div class="metric" id="system-status">Loading...</div>
            <div class="label">Current Status</div>
            <div id="uptime">Uptime: Loading...</div>
            <div id="last-check">Last Check: Loading...</div>
        </div>
        
        <div class="card">
            <h2>Performance Metrics</h2>
            <div class="metric" id="avg-response-time">Loading...</div>
            <div class="label">Average Response Time (ms)</div>
            <div id="response-range">Range: Loading...</div>
        </div>
        
        <div class="card">
            <h2>Task Queue</h2>
            <div class="metric" id="task-count">Loading...</div>
            <div class="label">Current Tasks</div>
        </div>
        
        <div class="card">
            <h2>Alert Status</h2>
            <div class="metric" id="alert-count">Loading...</div>
            <div class="label">Active Alerts</div>
            <div id="recent-alerts">Loading...</div>
        </div>
    </div>
    
    <div class="card" style="margin-top: 20px;">
        <h2>Recent System Activity</h2>
        <div id="recent-activity">Loading...</div>
    </div>

    <script>
        function refreshDashboard() {
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Dashboard refresh error:', error));
        }
        
        function updateDashboard(data) {
            // Update system status
            const status = data.system_status.status;
            document.getElementById('system-status').textContent = status.toUpperCase();
            document.getElementById('system-status').className = 'metric status-' + status;
            document.getElementById('uptime').textContent = 'Uptime: ' + data.system_status.uptime_formatted;
            document.getElementById('last-check').textContent = 'Last Check: ' + new Date(data.system_status.last_check).toLocaleTimeString();
            
            // Update performance metrics
            document.getElementById('avg-response-time').textContent = Math.round(data.performance_metrics.avg_response_time) + 'ms';
            document.getElementById('response-range').textContent = 
                'Range: ' + Math.round(data.performance_metrics.min_response_time) + 
                'ms - ' + Math.round(data.performance_metrics.max_response_time) + 'ms';
            
            // Update alerts
            document.getElementById('alert-count').textContent = data.alerts.active;
            const alertsHtml = data.alerts.recent.map(alert => 
                '<div class="alert ' + alert.severity + '">' + alert.message + '</div>'
            ).join('');
            document.getElementById('recent-alerts').innerHTML = alertsHtml || 'No recent alerts';
            
            // Update recent activity
            const activityHtml = data.recent_metrics.map(metric => 
                '<div>' + new Date(metric.timestamp).toLocaleTimeString() + 
                ' - Status: ' + metric.status + 
                (metric.response_time ? ' - Response: ' + Math.round(metric.response_time) + 'ms' : '') +
                '</div>'
            ).join('');
            document.getElementById('recent-activity').innerHTML = activityHtml || 'No recent activity';
        }
        
        function startMonitoring() {
            fetch('/api/monitoring/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => console.log('Monitoring started:', data))
                .catch(error => console.error('Start monitoring error:', error));
        }
        
        function stopMonitoring() {
            fetch('/api/monitoring/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => console.log('Monitoring stopped:', data))
                .catch(error => console.error('Stop monitoring error:', error));
        }
        
        // Auto-refresh every 5 seconds
        setInterval(refreshDashboard, 5000);
        
        // Initial load
        refreshDashboard();
    </script>
</body>
</html>"""
    
    (templates_dir / "dashboard.html").write_text(dashboard_html)


if __name__ == "__main__":
    print("🎮 A2A Monitoring Dashboard")
    print("=" * 50)
    
    # Create dashboard template
    create_dashboard_template()
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        print("🚀 Starting dashboard server on http://127.0.0.1:5001")
        print("📊 Dashboard URL: http://127.0.0.1:5001")
        print("🔧 API Health: http://127.0.0.1:5001/health")
        print("📋 Dashboard Data: http://127.0.0.1:5001/api/dashboard-data")
        print("\nPress Ctrl+C to stop...")
        
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping dashboard server...")
        monitor.stop_monitoring()
        print("✅ Dashboard server stopped")