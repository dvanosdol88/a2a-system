#!/usr/bin/env python3
"""
Jules Ultimate Fix - Use existing virtual environment
This uses the already-working virtual environment with Flask installed
"""

import subprocess
import sys
import os
from pathlib import Path

def start_jules_with_venv():
    """Start Jules using the existing virtual environment"""
    
    print("🎯 JULES ULTIMATE FIX")
    print("=" * 25)
    
    # Navigate to A2A directory
    a2a_dir = Path("/mnt/c/Users/david/projects-master/a2a-system")
    if not a2a_dir.exists():
        print(f"❌ A2A directory not found: {a2a_dir}")
        return False
    
    os.chdir(a2a_dir)
    print(f"✅ Working directory: {os.getcwd()}")
    
    # Check if virtual environment exists
    venv_dir = a2a_dir / "a2a-env"
    if not venv_dir.exists():
        print("❌ Virtual environment not found")
        return False
    
    print("✅ Virtual environment found")
    
    # Use virtual environment Python directly
    venv_python = venv_dir / "bin" / "python"
    if not venv_python.exists():
        print("❌ Virtual environment Python not found")
        return False
    
    print(f"✅ Using Python: {venv_python}")
    
    # Test Flask in virtual environment
    try:
        result = subprocess.run([
            str(venv_python), "-c", "import flask; print('Flask version:', flask.__version__)"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Flask test: {result.stdout.strip()}")
        else:
            print(f"❌ Flask test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Flask test timed out")
        return False
    except Exception as e:
        print(f"❌ Flask test error: {e}")
        return False
    
    # Start the server using virtual environment Python
    print("\n🚀 Starting Jules API Server...")
    print("🌐 Server URL: http://127.0.0.1:5006")
    print("❤️ Health Check: http://127.0.0.1:5006/health")
    print("📝 Add Task: POST http://127.0.0.1:5006/add_task")
    print("📋 List Tasks: GET http://127.0.0.1:5006/tasks")
    print("\nPress Ctrl+C to stop")
    print("-" * 40)
    
    try:
        # Create a small server script that uses port 5006
        server_script = '''
import sys
sys.path.insert(0, "/mnt/c/Users/david/projects-master/a2a-system")
from api.jules_server import app
print("🎉 Jules API Server starting on port 5006...")
app.run(host="0.0.0.0", port=5006, debug=False)
'''
        
        # Run the server using virtual environment Python
        process = subprocess.run([
            str(venv_python), "-c", server_script
        ], text=True)
        
        print("\n✅ Server stopped")
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return False

if __name__ == "__main__":
    success = start_jules_with_venv()
    if success:
        print("✅ Jules server session complete")
    else:
        print("❌ Jules server failed to start")
        sys.exit(1)