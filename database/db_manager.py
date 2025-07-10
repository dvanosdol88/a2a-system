"""Database Manager for A2A System
Supports both PostgreSQL and SQLite for flexibility
"""

import os
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class DatabaseManager:
    """Manages database connections and operations for A2A system"""
    
    def __init__(self):
        self.db_type = os.environ.get('A2A_DB_TYPE', 'sqlite').lower()
        self.db_url = os.environ.get('A2A_DATABASE_URL', 'a2a_system.db')
        
        if self.db_type == 'postgresql' and not POSTGRES_AVAILABLE:
            print("Warning: PostgreSQL requested but psycopg2 not available. Falling back to SQLite.")
            self.db_type = 'sqlite'
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        if self.db_type == 'postgresql':
            conn = psycopg2.connect(self.db_url)
            try:
                yield conn
            finally:
                conn.close()
        else:  # sqlite
            conn = sqlite3.connect(self.db_url)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def init_database(self):
        """Initialize database with schema"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Adapt schema for SQLite if needed
        if self.db_type == 'sqlite':
            schema = schema.replace('SERIAL', 'INTEGER')
            schema = schema.replace('JSONB', 'TEXT')
            schema = schema.replace('TIMESTAMP', 'TEXT')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(schema) if self.db_type == 'sqlite' else cursor.execute(schema)
            conn.commit()
    
    # Task Management
    def add_task(self, task: str, assigned_to: Optional[str] = None) -> int:
        """Add a new task"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if self.db_type == 'postgresql':
                cursor.execute(
                    "INSERT INTO tasks (task, assigned_to) VALUES (%s, %s) RETURNING id",
                    (task, assigned_to)
                )
                task_id = cursor.fetchone()[0]
            else:
                cursor.execute(
                    "INSERT INTO tasks (task, assigned_to, created) VALUES (?, ?, ?)",
                    (task, assigned_to, datetime.utcnow().isoformat())
                )
                task_id = cursor.lastrowid
            conn.commit()
            return task_id
    
    def get_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks with optional status filter"""
        with self.get_connection() as conn:
            if self.db_type == 'postgresql':
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            if status:
                query = "SELECT * FROM tasks WHERE status = %s ORDER BY created DESC"
                params = (status,) if self.db_type == 'postgresql' else (status,)
            else:
                query = "SELECT * FROM tasks ORDER BY created DESC"
                params = None
            
            cursor.execute(query, params) if params else cursor.execute(query)
            
            if self.db_type == 'sqlite':
                # Convert sqlite3.Row to dict
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                return cursor.fetchall()
    
    # API Key Management
    def create_api_key(self, name: str, permissions: Optional[Dict] = None) -> str:
        """Create a new API key"""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            permissions_json = json.dumps(permissions or {})
            
            if self.db_type == 'postgresql':
                cursor.execute(
                    "INSERT INTO api_keys (key_hash, name, permissions) VALUES (%s, %s, %s)",
                    (key_hash, name, permissions_json)
                )
            else:
                cursor.execute(
                    "INSERT INTO api_keys (key_hash, name, permissions, created) VALUES (?, ?, ?, ?)",
                    (key_hash, name, permissions_json, datetime.utcnow().isoformat())
                )
            conn.commit()
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return key info if valid"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM api_keys WHERE key_hash = %s AND is_active = %s",
                (key_hash, True) if self.db_type == 'postgresql' else (key_hash, 1)
            )
            
            if self.db_type == 'sqlite':
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
            else:
                return cursor.fetchone()
        
        return None
    
    # Request Logging
    def log_request(self, api_key_id: Optional[int], endpoint: str, method: str,
                   ip_address: str, response_code: int, response_time_ms: int):
        """Log API request for monitoring and rate limiting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.db_type == 'postgresql':
                cursor.execute(
                    """INSERT INTO request_logs 
                    (api_key_id, endpoint, method, ip_address, response_code, response_time_ms) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (api_key_id, endpoint, method, ip_address, response_code, response_time_ms)
                )
            else:
                cursor.execute(
                    """INSERT INTO request_logs 
                    (api_key_id, endpoint, method, ip_address, timestamp, response_code, response_time_ms) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (api_key_id, endpoint, method, ip_address, datetime.utcnow().isoformat(),
                     response_code, response_time_ms)
                )
            conn.commit()
    
    # Migration helper
    def migrate_from_json(self, json_file_path: str):
        """Migrate tasks from JSON file to database"""
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                tasks = json.load(f)
            
            for task in tasks:
                self.add_task(
                    task.get('task', ''),
                    task.get('assigned_to')
                )
            
            print(f"Migrated {len(tasks)} tasks from {json_file_path}")


# Singleton instance
db = DatabaseManager()