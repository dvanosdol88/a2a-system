#!/usr/bin/env python3
"""
Simple Prometheus-style metrics dashboard for P3.3
"""
import requests
import time
import json
import sys
from datetime import datetime
from collections import defaultdict

class MetricsCollector:
    def __init__(self, targets):
        self.targets = targets
        self.metrics_history = defaultdict(list)
        
    def scrape(self):
        """Scrape metrics from all targets"""
        for target in self.targets:
            try:
                resp = requests.get(f"http://{target}/metrics", timeout=5)
                if resp.status_code == 200:
                    self._parse_metrics(target, resp.text)
            except Exception as e:
                print(f"Error scraping {target}: {e}")
    
    def _parse_metrics(self, target, text):
        """Parse Prometheus metrics format"""
        timestamp = datetime.now()
        for line in text.split('\n'):
            if line and not line.startswith('#'):
                if 'a2a_tasks_total' in line:
                    # Extract metric value
                    parts = line.split(' ')
                    if len(parts) >= 2:
                        try:
                            value = float(parts[1])
                            metric_name = parts[0]
                            self.metrics_history[metric_name].append({
                                'timestamp': timestamp,
                                'value': value,
                                'target': target
                            })
                        except ValueError:
                            pass
    
    def collect_for_duration(self, duration_seconds=60, interval=5):
        """Collect metrics for specified duration"""
        print(f"Collecting metrics for {duration_seconds} seconds...")
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            self.scrape()
            print(f"Scraped at {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(interval)
        
        return self.metrics_history
    
    def get_json_output(self):
        """Return metrics as JSON-serializable data"""
        serializable_data = {}
        for metric, points in self.metrics_history.items():
            serializable_data[metric] = [
                {
                    'timestamp': p['timestamp'].isoformat(),
                    'value': p['value'],
                    'target': p['target']
                }
                for p in points
            ]
        return serializable_data

def simulate_load():
    """Add some tasks to generate metrics"""
    base_url = "http://localhost:5001"
    for i in range(5):
        try:
            requests.post(f"{base_url}/add_task", 
                         json={"task": f"Load test task {i+1}", "assigned_to": "test_agent"},
                         timeout=2)
            time.sleep(2)
        except:
            pass

if __name__ == "__main__":
    # Check for --format=json argument
    output_json = "--format=json" in sys.argv
    
    # Targets to scrape - only the running instance
    targets = ["localhost:5001"]
    
    collector = MetricsCollector(targets)
    
    # Start collecting in background
    import threading
    load_thread = threading.Thread(target=simulate_load)
    load_thread.daemon = True
    load_thread.start()
    
    # Collect metrics for 10 seconds (shorter for testing)
    collector.collect_for_duration(10, interval=2)
    
    # Get JSON output
    metrics_data = collector.get_json_output()
    
    if output_json:
        # Output to stdout for piping
        print(json.dumps(metrics_data, indent=2))
    else:
        # Save to file
        with open('metrics_data.json', 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        print("Metrics collection complete!")
        print(f"Total metrics collected: {sum(len(v) for v in collector.metrics_history.values())}")