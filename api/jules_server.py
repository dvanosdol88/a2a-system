from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pathlib import Path
import datetime, json
import os
import redis
import uuid
from redis.exceptions import ConnectionError as RedisConnectionError
try:
    from .metrics import (
        tasks_total, tasks_processed_total, tasks_acknowledged_total,
        active_tasks, redis_connection_status, track_request_time, get_metrics
    )
except ImportError:
    from metrics import (
        tasks_total, tasks_processed_total, tasks_acknowledged_total,
        active_tasks, redis_connection_status, track_request_time, get_metrics
    )

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Initialize Redis client
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_DB = int(os.environ.get('REDIS_DB', '0'))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except RedisConnectionError:
    print(f"Warning: Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}")
    print("Falling back to file-based storage")
    redis_client = None

# Fallback file storage (kept for compatibility)
BASE = Path(__file__).parent.parent
TASKS_FILE = BASE / "shared" / "tasks.json"
AGENT_TASKS_FILE = BASE / "shared" / "agent_tasks.json"

def _now():
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

def _get_task_id():
    """Get next task ID from Redis counter or file"""
    if redis_client:
        try:
            return redis_client.incr("a2a:task_counter")
        except:
            pass
    # Fallback to file-based counting
    tasks = json.loads(TASKS_FILE.read_text()) if TASKS_FILE.exists() else []
    return len(tasks) + 1

@app.route("/")
def index():
    return {"service": "A2A Jules API", "status": "running", "endpoints": ["/health", "/tasks", "/add_task", "/metrics"]}

@app.route("/health")
@track_request_time("/health")
def health():
    redis_status = "connected"
    if redis_client:
        try:
            redis_client.ping()
            redis_connection_status.set(1)
        except:
            redis_status = "disconnected"
            redis_connection_status.set(0)
    else:
        redis_status = "not configured"
        redis_connection_status.set(0)
    
    return {
        "status": "ok",
        "server_time": _now(),
        "redis": redis_status,
        "storage": "redis" if redis_client else "file"
    }

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(force=True)
    if not data or 'task' not in data:
        return jsonify({"error": "Invalid payload"}), 400

    task_id = str(uuid.uuid4())

    # For simplicity, we'll just store the update in a new hash
    redis_client.hset(f"task:{task_id}", mapping=data)

    # Add task data to a stream
    redis_client.xadd('a2a_stream', {"task_id": task_id})

    return jsonify({"task_id": task_id}), 201


@app.route("/tasks/<string:id>", methods=["PUT"])
def update_task(id):
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    # For simplicity, we'll just store the update in a new hash
    redis_client.hset(f"task:{id}", mapping=data)
    
    return jsonify({"message": "Task updated"}), 200


@app.route("/tasks/<string:id>/complete", methods=["POST"])
def complete_task(id):
    data = request.get_json(force=True)
    if not data or 'result' not in data:
        return jsonify({"error": "Invalid payload"}), 400

    redis_client.hset(f"task:{id}", mapping={"status": "completed", "result": json.dumps(data['result'])})
    
    return jsonify({"message": "Task marked as complete"}), 200


@app.route("/tasks/unassigned", methods=["GET"])
def get_unassigned_tasks():
    # This is a conceptual example. A real implementation would need a more robust way to track assignments.
    # For now, we'll return all tasks that don't have an "assigned_to" field.
    tasks = []
    for key in redis_client.scan_iter("task:*"):
        task_data = redis_client.hgetall(key)
        if b'assigned_to' not in task_data:
            tasks.append({
                "task_id": key.decode('utf-8').split(':')[1],
                "data": {k.decode('utf-8'): v.decode('utf-8') for k, v in task_data.items()}
            })
    return jsonify(tasks)


@app.route("/tasks/<string:id>", methods=["GET"])
def get_task(id):
    task_data = redis_client.hgetall(f"task:{id}")
    if not task_data:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify({
        "task_id": id,
        "data": {k.decode('utf-8'): v.decode('utf-8') for k, v in task_data.items()}
    })

@app.route("/tasks")
def list_tasks():
    if redis_client:
        try:
            # Get tasks from Redis (newest first)
            tasks_json = redis_client.lrange("a2a:tasks", 0, -1)
            tasks = [json.loads(task) for task in tasks_json]
            return jsonify(tasks)
        except:
            # Fall through to file storage
            pass
    
    # File-based storage (fallback)
    tasks = json.loads(TASKS_FILE.read_text()) if TASKS_FILE.exists() else []
    return jsonify(tasks)

@app.route("/agent/<agent_id>/tasks")
def get_agent_tasks(agent_id):
    """Get pending tasks for a specific agent"""
    if redis_client:
        try:
            # Get agent tasks from Redis
            tasks_json = redis_client.lrange(f"a2a:agent_tasks:{agent_id}", 0, -1)
            tasks = [json.loads(task) for task in tasks_json]
            # Filter pending tasks (all tasks in Redis are pending by default)
            pending_tasks = [task for task in tasks if task.get("status", "pending") == "pending"]
            return jsonify(pending_tasks)
        except:
            # Fall through to file storage
            pass
    
    # File-based storage (fallback)
    agent_tasks = json.loads(AGENT_TASKS_FILE.read_text()) if AGENT_TASKS_FILE.exists() else {}
    agent_queue = agent_tasks.get(agent_id, [])
    pending_tasks = [task for task in agent_queue if task["status"] == "pending"]
    return jsonify(pending_tasks)

@app.route("/agent/<agent_id>/tasks/<int:task_id>/complete", methods=["POST"])
def complete_agent_task(agent_id, task_id):
    """Mark an agent task as completed"""
    data = request.get_json(force=True) if request.is_json else {}
    response = data.get("response", "Task completed")
    
    if redis_client:
        try:
            # Remove from agent's task list
            tasks_json = redis_client.lrange(f"a2a:agent_tasks:{agent_id}", 0, -1)
            for i, task_json in enumerate(tasks_json):
                task = json.loads(task_json)
                if task["id"] == task_id:
                    # Remove from agent's list
                    redis_client.lrem(f"a2a:agent_tasks:{agent_id}", 1, task_json)
                    
                    # Add completion record
                    completion = {
                        "task_id": task_id,
                        "agent_id": agent_id,
                        "completed": _now(),
                        "response": response
                    }
                    redis_client.lpush("a2a:completed_tasks", json.dumps(completion))
                    
                    # Also add response as new task
                    new_task = {
                        "id": _get_task_id(),
                        "task": f"[{agent_id}] {response}",
                        "created": _now()
                    }
                    redis_client.lpush("a2a:tasks", json.dumps(new_task))
                    
                    # Track metrics
                    tasks_processed_total.labels(agent=agent_id).inc()
                    active_tasks.labels(agent=agent_id).dec()
                    return {"message": "Task completed", "response": response}, 200
            
            return {"error": "Task not found"}, 404
        except:
            # Fall through to file storage
            pass
    
    # File-based storage (fallback)
    agent_tasks = json.loads(AGENT_TASKS_FILE.read_text()) if AGENT_TASKS_FILE.exists() else {}
    if agent_id not in agent_tasks:
        return {"error": "Agent not found"}, 404
    
    # Find and update the task
    for task in agent_tasks[agent_id]:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed"] = _now()
            task["response"] = response
            break
    else:
        return {"error": "Task not found"}, 404
    
    AGENT_TASKS_FILE.write_text(json.dumps(agent_tasks, indent=2))
    
    # Also add the response as a new general task
    tasks = json.loads(TASKS_FILE.read_text()) if TASKS_FILE.exists() else []
    tasks.append({"task": f"[{agent_id}] {response}", "created": _now()})
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    
    return {"message": "Task completed", "response": response}, 200

@app.route("/agent/<agent_id>/tasks/<int:task_id>/acknowledge", methods=["POST"])
def acknowledge_agent_task(agent_id, task_id):
    """Agent acknowledges receiving a task"""
    if redis_client:
        try:
            # Store acknowledgment in Redis
            ack = {
                "task_id": task_id,
                "agent_id": agent_id,
                "acknowledged": _now()
            }
            redis_client.hset(f"a2a:task_acks", f"{agent_id}:{task_id}", json.dumps(ack))
            # Track metrics
            tasks_acknowledged_total.labels(agent=agent_id).inc()
            return {"message": "Task acknowledged"}, 200
        except:
            # Fall through to file storage
            pass
    
    # File-based storage (fallback)
    agent_tasks = json.loads(AGENT_TASKS_FILE.read_text()) if AGENT_TASKS_FILE.exists() else {}
    if agent_id not in agent_tasks:
        return {"error": "Agent not found"}, 404
    
    for task in agent_tasks[agent_id]:
        if task["id"] == task_id:
            task["status"] = "acknowledged"
            task["acknowledged"] = _now()
            break
    else:
        return {"error": "Task not found"}, 404
    
    AGENT_TASKS_FILE.write_text(json.dumps(agent_tasks, indent=2))
    # Track metrics
    tasks_acknowledged_total.labels(agent=agent_id).inc()
    return {"message": "Task acknowledged"}, 200

@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(get_metrics(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', os.environ.get('A2A_JULES_PORT', '5000')))
    app.run(host="0.0.0.0", port=port)