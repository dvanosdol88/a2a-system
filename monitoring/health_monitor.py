#!/usr/bin/env python3
"""
A2A System Health Monitor
Checks service health and sends alerts
"""
import requests
import json
import os
from datetime import datetime
from pathlib import Path

class A2AHealthMonitor:
    def __init__(self):
        self.services = {
            "jules_api": {
                "url": os.environ.get("JULES_API_URL", "https://a2a-jules.onrender.com"),
                "health_endpoint": "/health",
                "name": "Jules API"
            },
            "dashboard": {
                "url": os.environ.get("DASHBOARD_URL", "https://a2a-dashboard.onrender.com"),
                "health_endpoint": "/api/health",
                "name": "A2A Dashboard"
            }
        }
        self.log_file = Path(__file__).parent / "health_checks.log"
        
    def check_service_health(self, service_id):
        """Check if a service is healthy"""
        service = self.services[service_id]
        url = service["url"] + service["health_endpoint"]
        
        try:
            response = requests.get(url, timeout=10)
            is_healthy = response.status_code == 200
            
            return {
                "service": service["name"],
                "url": url,
                "status_code": response.status_code,
                "healthy": is_healthy,
                "response_time": response.elapsed.total_seconds(),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            return {
                "service": service["name"],
                "url": url,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    def check_all_services(self):
        """Check health of all services"""
        results = {}
        for service_id in self.services:
            results[service_id] = self.check_service_health(service_id)
        return results
    
    def log_health_status(self, results):
        """Log health check results"""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(results) + "\n")
    
    def get_summary(self, results):
        """Get a summary of health check results"""
        all_healthy = all(r["healthy"] for r in results.values())
        unhealthy_services = [r["service"] for r in results.values() if not r["healthy"]]
        
        return {
            "all_healthy": all_healthy,
            "unhealthy_services": unhealthy_services,
            "checked_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def send_alert(self, summary, results):
        """Send alert if services are unhealthy"""
        if not summary["all_healthy"]:
            print(f"⚠️ ALERT: Services unhealthy - {summary['unhealthy_services']}")
            # In production, this would send emails, Slack messages, etc.
            
    def run_health_check(self):
        """Run a complete health check cycle"""
        results = self.check_all_services()
        summary = self.get_summary(results)
        
        # Log results
        self.log_health_status(results)
        
        # Send alerts if needed
        self.send_alert(summary, results)
        
        # Print summary
        print(f"\n🏥 A2A Health Check - {summary['checked_at']}")
        for service_id, result in results.items():
            status = "✅" if result["healthy"] else "❌"
            print(f"{status} {result['service']}: {result.get('status_code', 'ERROR')}")
            if "response_time" in result:
                print(f"   Response time: {result['response_time']:.2f}s")
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        return summary

if __name__ == "__main__":
    monitor = A2AHealthMonitor()
    monitor.run_health_check()