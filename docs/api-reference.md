# A2A System API Reference

## Base URL
```
http://127.0.0.1:5000
```

## Endpoints

### Health Check
**GET** `/health`

Returns server health and timestamp.

**Response:**
```json
{
  "status": "ok",
  "server_time": "2025-07-04T14:30:00Z"
}
```

### Add Task
**POST** `/add_task`

Adds a new task to the queue.

**Request:**
```json
{
  "task": "Task description"
}
```

**Response:**
```json
{
  "message": "queued 'Task description'",
  "total_tasks": 1
}
```

**Error Response:**
```json
{
  "error": "task field required"
}
```

### List Tasks
**GET** `/tasks`

Returns all tasks in the queue.

**Response:**
```json
[
  {
    "task": "Task description",
    "created": "2025-07-04T14:30:00Z"
  }
]
```

## Communication Protocol

### Message Format
- **Content-Type**: `application/json`
- **Encoding**: UTF-8
- **Timestamps**: UTC ISO format with 'Z' suffix

### Error Handling
- **400**: Bad request (missing/invalid data)
- **500**: Internal server error
- **200**: Success
- **201**: Created (for task creation)

### Task Storage
- **File**: `shared/tasks.json`
- **Format**: JSON array of task objects
- **Persistence**: Automatic file-based storage

## Usage Examples

### cURL Examples
```bash
# Health check
curl http://127.0.0.1:5000/health

# Add task
curl -X POST -H "Content-Type: application/json" \
     -d '{"task": "Hello from Claude"}' \
     http://127.0.0.1:5000/add_task

# List tasks
curl http://127.0.0.1:5000/tasks
```

### Python Client
```python
import requests

client = requests.Session()
client.headers.update({"Content-Type": "application/json"})

# Health check
response = client.get("http://127.0.0.1:5000/health")
print(response.json())

# Add task
response = client.post("http://127.0.0.1:5000/add_task", 
                      json={"task": "Hello from Python"})
print(response.json())
```

---
**Created**: July 4, 2025  
**Repository**: a2a-system