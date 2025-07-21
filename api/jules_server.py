from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import datetime, json
import os
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

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
    return {"service": "A2A Jules API", "status": "running", "endpoints": ["/health", "/tasks", "/add_task"]}

@app.route("/health")
def health():
    redis_status = "connected"
    if redis_client:
        try:
            redis_client.ping()
        except:
            redis_status = "disconnected"
    else:
        redis_status = "not configured"
    
    return {
        "status": "ok",
        "server_time": _now(),
        "redis": redis_status,
        "storage": "redis" if redis_client else "file"
    }

@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.get_json(force=True)
    task = data.get("task", "").strip()
    assigned_to = data.get("assigned_to", "").strip()
    if not task:
        return {"error": "task field required"}, 400

    task_id = _get_task_id()
    task_entry = {
        "id": task_id,
        "task": task,
        "created": _now(),
        "assigned_to": assigned_to
    }
    
    if redis_client:
        try:
            # Store in Redis
            redis_client.lpush("a2a:tasks", json.dumps(task_entry))
            
            # Store in agent-specific list if assigned
            if assigned_to:
                redis_client.lpush(f"a2a:agent_tasks:{assigned_to}", json.dumps(task_entry))
            
            total_tasks = redis_client.llen("a2a:tasks")
            return {"message": f"queued {task!r}", "id": task_id, "total_tasks": total_tasks, "assigned_to": assigned_to}, 201
        except:
            # Fall through to file storage
            pass
    
    # File-based storage (fallback)
    tasks = json.loads(TASKS_FILE.read_text()) if TASKS_FILE.exists() else []
    if assigned_to:
        task_entry["assigned_to"] = assigned_to
    tasks.append(task_entry)
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    
    # Add to agent-specific tasks if assigned
    if assigned_to:
        agent_tasks = json.loads(AGENT_TASKS_FILE.read_text()) if AGENT_TASKS_FILE.exists() else {}
        if assigned_to not in agent_tasks:
            agent_tasks[assigned_to] = []
        agent_tasks[assigned_to].append({
            "id": task_id,
            "task": task,
            "created": _now(),
            "status": "pending"
        })
        AGENT_TASKS_FILE.write_text(json.dumps(agent_tasks, indent=2))
    
    return {"message": f"queued {task!r}", "id": task_id, "total_tasks": len(tasks), "assigned_to": assigned_to}, 201

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
    return {"message": "Task acknowledged"}, 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', os.environ.get('A2A_JULES_PORT', '5000')))
    app.run(host="0.0.0.0", port=port)