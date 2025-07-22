#!/usr/bin/env python3
"""
Created by: UC (Ubuntu Claude) - completing DC's delegated task
Date: 2025-07-22 10:20
Purpose: Command Line Interface for Jules API and a2a system
Task/Context: Creating jack_cli.py since DC listener not active
"""

import argparse
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from shared.claude_to_jules_helper import JulesAPIClient
    import redis
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're in the a2a-system directory with dependencies installed")
    sys.exit(1)

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class JackCLI:
    """Command line interface for the a2a system"""
    
    def __init__(self):
        self.jules_client = JulesAPIClient()
        self.redis_client = None
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis for stream operations"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )
            self.redis_client.ping()
        except Exception as e:
            print(f"{YELLOW}⚠️  Redis connection failed: {e}{RESET}")
            self.redis_client = None
    
    def add_task(self, task_description):
        """Submit a task to Jules API"""
        print(f"{BLUE}📤 Submitting task...{RESET}")
        result = self.jules_client.add_task(task_description)
        
        if 'error' in result:
            print(f"{RED}❌ Error: {result['error']}{RESET}")
            return False
        
        task_id = result.get('id', 'Unknown')
        print(f"{GREEN}✅ Task submitted successfully!{RESET}")
        print(f"   ID: {BOLD}{task_id}{RESET}")
        print(f"   Status: Queued")
        print(f"   Total tasks: {result.get('total_tasks', 'Unknown')}")
        return True
    
    def list_tasks(self, limit=10):
        """List all tasks from Jules API"""
        print(f"{BLUE}📋 Fetching tasks...{RESET}")
        tasks = self.jules_client.list_tasks()
        
        if isinstance(tasks, dict) and 'error' in tasks:
            print(f"{RED}❌ Error: {tasks['error']}{RESET}")
            return
        
        if not tasks:
            print(f"{YELLOW}📭 No tasks found{RESET}")
            return
        
        print(f"\n{BOLD}Recent Tasks:{RESET}")
        print("-" * 60)
        
        for i, task in enumerate(tasks[:limit]):
            task_id = task.get('id', 'Unknown')
            created = task.get('created', 'Unknown')
            description = task.get('task', 'No description')
            assigned = task.get('assigned_to', '')
            
            status_icon = "⏳" if not assigned else "👤"
            print(f"{status_icon} Task #{task_id}")
            print(f"   Created: {created}")
            print(f"   Description: {description[:80]}...")
            if assigned:
                print(f"   Assigned to: {assigned}")
            print()
        
        if len(tasks) > limit:
            print(f"... and {len(tasks) - limit} more tasks")
    
    def check_task_status(self, task_id):
        """Check status of a specific task"""
        print(f"{BLUE}🔍 Checking task #{task_id}...{RESET}")
        tasks = self.jules_client.list_tasks()
        
        if isinstance(tasks, dict) and 'error' in tasks:
            print(f"{RED}❌ Error: {tasks['error']}{RESET}")
            return
        
        # Find the specific task
        task = None
        for t in tasks:
            if str(t.get('id')) == str(task_id):
                task = t
                break
        
        if not task:
            print(f"{RED}❌ Task #{task_id} not found{RESET}")
            return
        
        print(f"\n{BOLD}Task Details:{RESET}")
        print(f"ID: {task.get('id')}")
        print(f"Created: {task.get('created')}")
        print(f"Description: {task.get('task')}")
        print(f"Assigned to: {task.get('assigned_to', 'Unassigned')}")
        
        # Check for results in Redis if available
        if self.redis_client:
            self._check_redis_results(task_id)
    
    def check_health(self):
        """Check Jules API health status"""
        print(f"{BLUE}🏥 Checking system health...{RESET}")
        health = self.jules_client.health_check()
        
        if health.get('status') == 'ok':
            print(f"{GREEN}✅ Jules API: Healthy{RESET}")
            print(f"   Storage: {health.get('storage', 'Unknown')}")
            print(f"   Redis: {health.get('redis', 'Unknown')}")
            print(f"   Server time: {health.get('server_time', 'Unknown')}")
        else:
            print(f"{RED}❌ Jules API: Unhealthy{RESET}")
            print(f"   Error: {health.get('message', 'Unknown error')}")
        
        # Check AI Connector health
        try:
            import requests
            ai_health = requests.get('http://localhost:8080/health', timeout=2).json()
            print(f"\n{GREEN}✅ AI Connector: Healthy{RESET}")
            print(f"   Tasks processed: {ai_health.get('tasks_processed', 0)}")
            print(f"   Uptime: {ai_health.get('uptime_seconds', 0)} seconds")
        except:
            print(f"\n{YELLOW}⚠️  AI Connector: Not responding{RESET}")
    
    def check_results(self, limit=5):
        """Check processed results from Redis stream"""
        if not self.redis_client:
            print(f"{RED}❌ Redis not connected{RESET}")
            return
        
        print(f"{BLUE}📊 Checking processed results...{RESET}")
        
        try:
            # Read last N results from stream
            results = self.redis_client.xrevrange('a2a_stream_results', count=limit)
            
            if not results:
                print(f"{YELLOW}📭 No results found{RESET}")
                return
            
            print(f"\n{BOLD}Recent Results:{RESET}")
            print("-" * 60)
            
            for msg_id, data in results:
                timestamp = datetime.fromtimestamp(int(msg_id.split('-')[0]) / 1000)
                status = data.get('status', 'unknown')
                result = data.get('result', 'No result')
                
                icon = "✅" if status == "completed" else "❌"
                print(f"{icon} Result ID: {msg_id}")
                print(f"   Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Status: {status}")
                print(f"   Result: {result[:100]}...")
                print()
                
        except Exception as e:
            print(f"{RED}❌ Error reading results: {e}{RESET}")
    
    def _check_redis_results(self, task_id):
        """Check if task has results in Redis"""
        if not self.redis_client:
            return
        
        try:
            # Search for results containing the task description
            results = self.redis_client.xrange('a2a_stream_results')
            for msg_id, data in results:
                if str(task_id) in str(data.get('result', '')):
                    print(f"\n{GREEN}✅ Result found in Redis:{RESET}")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Result: {data.get('result')}")
                    break
        except:
            pass

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Jack CLI - Command line interface for Jules API and a2a system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --add-task "Analyze this document for key insights"
  %(prog)s --tasks
  %(prog)s --task-status 42
  %(prog)s --health
  %(prog)s --results
        """
    )
    
    parser.add_argument('--add-task', '-a', 
                       help='Submit a new task to Jules')
    parser.add_argument('--tasks', '-t', action='store_true',
                       help='List all tasks')
    parser.add_argument('--task-status', '-s', 
                       help='Check status of a specific task by ID')
    parser.add_argument('--health', '-H', action='store_true',
                       help='Check system health status')
    parser.add_argument('--results', '-r', action='store_true',
                       help='Check processed results from Redis')
    parser.add_argument('--limit', '-l', type=int, default=10,
                       help='Limit number of items to display (default: 10)')
    
    args = parser.parse_args()
    
    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = JackCLI()
    
    # Execute commands
    if args.add_task:
        cli.add_task(args.add_task)
    elif args.tasks:
        cli.list_tasks(args.limit)
    elif args.task_status:
        cli.check_task_status(args.task_status)
    elif args.health:
        cli.check_health()
    elif args.results:
        cli.check_results(args.limit)

if __name__ == '__main__':
    main()