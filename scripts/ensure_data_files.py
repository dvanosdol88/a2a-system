#!/usr/bin/env python3
"""
Ensure required data files exist for A2A system
"""
from pathlib import Path
import json

# Get the base directory
BASE_DIR = Path(__file__).parent.parent
SHARED_DIR = BASE_DIR / "shared"

# Ensure shared directory exists
SHARED_DIR.mkdir(exist_ok=True)

# Ensure tasks.json exists
tasks_file = SHARED_DIR / "tasks.json"
if not tasks_file.exists():
    tasks_file.write_text("[]")
    print(f"Created {tasks_file}")

# Ensure agent_tasks.json exists
agent_tasks_file = SHARED_DIR / "agent_tasks.json"
if not agent_tasks_file.exists():
    agent_tasks_file.write_text("{}")
    print(f"Created {agent_tasks_file}")

print("Data files ready")