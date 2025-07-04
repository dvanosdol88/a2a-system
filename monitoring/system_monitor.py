"""
A2A System Monitor
Comprehensive system monitoring and health tracking
"""

import time
import json
import psutil
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import statistics

from shared.message_types import A2AMessage, validate_message_schema


class SystemMonitor:
    """Comprehensive A2A system monitoring"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5000"):
        self.api_base_url = api_base_url
        self.monitoring_active = False
        self.metrics_file = Path("monitoring/system_metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
        
        self.current_metrics = {
            "timestamp": None,
            "api_health": {},
            "system_resources": {},
            "performance": {},
            "errors": []
        }
        
        self.metrics_history = []
        self.max_history = 1000  # Keep last 1000 measurements
        
    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous monitoring"""
        print(f"🔍 Starting system monitoring (interval: {interval_seconds}s)")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                self.collect_metrics()
                self.save_metrics()
                self.analyze_trends()
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        print("⏹️ System monitoring stopped")
    
    def collect_metrics(self):
        """Collect comprehensive system metrics"""
        timestamp = datetime.now(timezone.utc)
        
        metrics = {
            "timestamp": timestamp.isoformat(),
            "api_health": self._check_api_health(),
            "system_resources": self._get_system_resources(),
            "performance": self._measure_performance(),
            "task_queue": self._check_task_queue(),
            "errors": []
        }
        
        # Store current metrics
        self.current_metrics = metrics
        
        # Add to history
        self.metrics_history.append(metrics)
        
        # Limit history size
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
        
        # Print summary
        self._print_metrics_summary(metrics)
        
        return metrics
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check API server health"""
        health_data = {
            "status": "unknown",
            "response_time": None,
            "server_time": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                api_data = response.json()
                health_data.update({
                    "status": "healthy",
                    "response_time": response_time,
                    "server_time": api_data.get("server_time"),
                    "status_code": response.status_code
                })
            else:
                health_data.update({
                    "status": "error",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.RequestException as e:
            health_data.update({
                "status": "error",
                "error": str(e)
            })
        
        return health_data
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource utilization"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent,
                    "used": psutil.disk_usage('/').used
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv,
                    "packets_sent": psutil.net_io_counters().packets_sent,
                    "packets_recv": psutil.net_io_counters().packets_recv
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _measure_performance(self) -> Dict[str, Any]:
        """Measure API performance"""
        performance = {
            "health_check": self._measure_endpoint_performance("/health"),
            "task_list": self._measure_endpoint_performance("/tasks"),
            "task_creation": self._measure_task_creation_performance()
        }
        
        return performance
    
    def _measure_endpoint_performance(self, endpoint: str) -> Dict[str, Any]:
        """Measure specific endpoint performance"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "response_time": response_time,
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "response_time": None,
                "status_code": None,
                "success": False,
                "error": str(e)
            }
    
    def _measure_task_creation_performance(self) -> Dict[str, Any]:
        """Measure task creation performance"""
        test_task = {
            "task": f"Performance test task - {datetime.now(timezone.utc).isoformat()}"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base_url}/add_task",
                json=test_task,
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "response_time": response_time,
                "status_code": response.status_code,
                "success": response.status_code == 201
            }
        except Exception as e:
            return {
                "response_time": None,
                "status_code": None,
                "success": False,
                "error": str(e)
            }
    
    def _check_task_queue(self) -> Dict[str, Any]:
        """Check task queue status"""
        try:
            response = requests.get(f"{self.api_base_url}/tasks", timeout=10)
            
            if response.status_code == 200:
                tasks = response.json()
                return {
                    "total_tasks": len(tasks),
                    "recent_tasks": len([
                        t for t in tasks
                        if self._is_recent_task(t.get("created", ""))
                    ]),
                    "oldest_task": tasks[0].get("created") if tasks else None,
                    "newest_task": tasks[-1].get("created") if tasks else None
                }
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "total_tasks": None
                }
        except Exception as e:
            return {
                "error": str(e),
                "total_tasks": None
            }
    
    def _is_recent_task(self, created_time: str) -> bool:
        """Check if task was created recently (last hour)"""
        try:
            task_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            return (current_time - task_time).total_seconds() < 3600  # 1 hour
        except:
            return False
    
    def analyze_trends(self):
        """Analyze performance trends"""
        if len(self.metrics_history) < 5:
            return  # Need at least 5 data points
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        
        # Analyze response time trends
        response_times = [
            m["api_health"]["response_time"]
            for m in recent_metrics
            if m["api_health"]["response_time"] is not None
        ]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            if avg_response_time > 1000:  # > 1 second
                print(f"⚠️ HIGH RESPONSE TIME: {avg_response_time:.0f}ms average")
        
        # Analyze error trends
        error_count = sum(
            1 for m in recent_metrics
            if m["api_health"]["status"] == "error"
        )
        
        if error_count > len(recent_metrics) * 0.5:  # > 50% errors
            print(f"🚨 HIGH ERROR RATE: {error_count}/{len(recent_metrics)} failed checks")
        
        # Analyze resource trends
        cpu_values = [
            m["system_resources"]["cpu_percent"]
            for m in recent_metrics
            if "cpu_percent" in m.get("system_resources", {})
        ]
        
        if cpu_values:
            avg_cpu = statistics.mean(cpu_values)
            if avg_cpu > 80:  # > 80% CPU
                print(f"⚠️ HIGH CPU USAGE: {avg_cpu:.1f}% average")
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            # Save current metrics
            with open(self.metrics_file, 'w') as f:
                json.dump(self.current_metrics, f, indent=2, default=str)
            
            # Save metrics history (separate file)
            history_file = self.metrics_file.parent / "metrics_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2, default=str)
                
        except Exception as e:
            print(f"❌ Failed to save metrics: {e}")
    
    def load_metrics_history(self):
        """Load metrics history from file"""
        try:
            history_file = self.metrics_file.parent / "metrics_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.metrics_history = json.load(f)
                print(f"📊 Loaded {len(self.metrics_history)} historical metrics")
        except Exception as e:
            print(f"⚠️ Failed to load metrics history: {e}")
    
    def _print_metrics_summary(self, metrics: Dict[str, Any]):
        """Print metrics summary"""
        timestamp = datetime.fromisoformat(metrics["timestamp"]).strftime("%H:%M:%S")
        
        # API Health
        api_status = metrics["api_health"]["status"]
        status_icon = "✅" if api_status == "healthy" else "❌"
        response_time = metrics["api_health"].get("response_time")
        
        print(f"\n📊 {timestamp} | {status_icon} API: {api_status}", end="")
        if response_time:
            print(f" ({response_time:.0f}ms)", end="")
        
        # System Resources
        if "cpu_percent" in metrics["system_resources"]:
            cpu = metrics["system_resources"]["cpu_percent"]
            memory = metrics["system_resources"]["memory"]["percent"]
            print(f" | 💻 CPU: {cpu:.1f}% | 🧠 Memory: {memory:.1f}%", end="")
        
        # Task Queue
        if "total_tasks" in metrics["task_queue"]:
            tasks = metrics["task_queue"]["total_tasks"]
            print(f" | 📋 Tasks: {tasks}", end="")
        
        print()  # New line
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "monitoring_active": self.monitoring_active,
            "current_metrics": self.current_metrics,
            "history_size": len(self.metrics_history),
            "last_update": self.current_metrics.get("timestamp")
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        if not self.metrics_history:
            return {"error": "No metrics data available"}
        
        recent_metrics = self.metrics_history[-24:]  # Last 24 measurements
        
        # Calculate statistics
        response_times = [
            m["api_health"]["response_time"]
            for m in recent_metrics
            if m["api_health"]["response_time"] is not None
        ]
        
        healthy_checks = [
            m for m in recent_metrics
            if m["api_health"]["status"] == "healthy"
        ]
        
        report = {
            "report_generated": datetime.now(timezone.utc).isoformat(),
            "monitoring_period": {
                "start": recent_metrics[0]["timestamp"] if recent_metrics else None,
                "end": recent_metrics[-1]["timestamp"] if recent_metrics else None,
                "total_checks": len(recent_metrics)
            },
            "availability": {
                "healthy_checks": len(healthy_checks),
                "total_checks": len(recent_metrics),
                "uptime_percentage": (len(healthy_checks) / len(recent_metrics)) * 100 if recent_metrics else 0
            },
            "performance": {
                "avg_response_time": statistics.mean(response_times) if response_times else None,
                "max_response_time": max(response_times) if response_times else None,
                "min_response_time": min(response_times) if response_times else None,
                "response_time_std": statistics.stdev(response_times) if len(response_times) > 1 else None
            },
            "current_status": self.current_metrics
        }
        
        return report


if __name__ == "__main__":
    print("🔍 A2A System Monitor")
    print("=" * 50)
    
    monitor = SystemMonitor()
    
    # Load historical data
    monitor.load_metrics_history()
    
    try:
        # Start monitoring
        monitor.start_monitoring(interval_seconds=30)
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
        
        # Generate final report
        print("\n📋 Generating final report...")
        report = monitor.generate_report()
        
        report_file = Path("monitoring/final_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Report saved to {report_file}")
        print("✅ System monitor shutdown complete")