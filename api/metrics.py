"""
Prometheus metrics for A2A system
Created: 2025-07-21
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
import time

# Define metrics
tasks_total = Counter('a2a_tasks_total', 'Total number of tasks created', ['assigned_to'])
tasks_processed_total = Counter('a2a_tasks_processed_total', 'Total number of tasks processed', ['agent'])
tasks_acknowledged_total = Counter('a2a_tasks_acknowledged_total', 'Total number of tasks acknowledged', ['agent'])
active_tasks = Gauge('a2a_active_tasks', 'Number of active tasks', ['agent'])
redis_connection_status = Gauge('a2a_redis_connection_status', 'Redis connection status (1=connected, 0=disconnected)')
api_request_duration = Histogram('a2a_api_request_duration_seconds', 'API request duration', ['endpoint', 'method'])

# Helper decorators
def track_request_time(endpoint):
    """Decorator to track request processing time"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            api_request_duration.labels(endpoint=endpoint, method='GET').observe(duration)
            return result
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

def get_metrics():
    """Generate Prometheus metrics in text format"""
    return generate_latest()