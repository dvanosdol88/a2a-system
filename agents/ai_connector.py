import os
import logging
import time
import threading
from typing import Any, Dict
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

import redis

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
STREAM_NAME = "a2a_stream"
RESULT_STREAM = "a2a_stream_results"
GROUP_NAME = "ai_group"
CONSUMER_NAME = "ai_connector"
HEALTH_PORT = int(os.environ.get("HEALTH_PORT", 8080))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AI-Connector] %(message)s",
)

# Global health status
health_status = {
    "status": "starting",
    "redis_connected": False,
    "last_task_time": None,
    "tasks_processed": 0,
    "errors": 0,
    "uptime_seconds": 0
}
start_time = time.time()


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            health_status["uptime_seconds"] = int(time.time() - start_time)
            
            # Determine overall status
            if health_status["redis_connected"]:
                health_status["status"] = "healthy"
            else:
                health_status["status"] = "unhealthy"
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health_status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP server logging
        pass


def run_health_server():
    server = HTTPServer(('0.0.0.0', HEALTH_PORT), HealthHandler)
    logging.info(f"Health endpoint listening on port {HEALTH_PORT}")
    server.serve_forever()


def get_client() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def ensure_group(client: redis.Redis) -> None:
    try:
        client.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
        logging.info("Consumer group created")
    except redis.exceptions.ResponseError as exc:
        if "BUSYGROUP" in str(exc):
            logging.info("Consumer group already exists")
        else:
            raise


def process_task(
    entry: Dict[str, Any],
    client: redis.Redis,
    message_id: str,
) -> None:
    task = entry.get("task")
    logging.info(f"Processing task: {task}")
    result = {"status": "completed", "result": task}
    client.xack(STREAM_NAME, GROUP_NAME, message_id)
    client.xadd(RESULT_STREAM, result)
    
    # Update health metrics
    health_status["tasks_processed"] += 1
    health_status["last_task_time"] = time.time()


def main() -> None:
    # Start health endpoint in separate thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    client = None
    while client is None:
        try:
            client = get_client()
            ensure_group(client)
            logging.info(f"Connected to Redis {REDIS_HOST}:{REDIS_PORT}")
            health_status["redis_connected"] = True
        except redis.ConnectionError:
            logging.info("Redis connection failed, retrying...")
            health_status["redis_connected"] = False
            health_status["errors"] += 1
            time.sleep(1)

    while True:
        try:
            resp = client.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_NAME: ">"},
                count=1,
                block=5000,
            )
        except redis.ConnectionError:
            logging.info("Lost Redis connection, retrying...")
            health_status["redis_connected"] = False
            health_status["errors"] += 1
            time.sleep(1)
            client = None
            while client is None:
                try:
                    client = get_client()
                    ensure_group(client)
                    health_status["redis_connected"] = True
                except redis.ConnectionError:
                    logging.info("Redis reconnect failed, retrying...")
                    time.sleep(1)
            continue

        if not resp:
            continue

        for _stream, messages in resp:
            for message_id, entry in messages:
                try:
                    process_task(entry, client, message_id)
                except Exception as e:
                    logging.error(f"Error processing task: {e}")
                    health_status["errors"] += 1


if __name__ == "__main__":
    main()