#!/usr/bin/env python3
"""
Standalone Jules Server - Pure Python Solution
No shell scripts, no virtual environment complications
"""

import sys
import os
import importlib.util
from pathlib import Path

def check_and_install_flask():
    """Check if Flask is available, install if needed"""
    
    print("🔍 Checking Flask availability...")
    
    # Try to import Flask
    try:
        import flask
        print(f"✅ Flask already available: {flask.__version__}")
        return True
    except ImportError:
        print("❌ Flask not found, attempting installation...")
    
    # Try to install from wheels
    wheels_dir = Path(__file__).parent / "wheels"
    if not wheels_dir.exists():
        print("❌ Wheels directory not found")
        return False
    
    # Install using pip programmatically
    try:
        import subprocess
        import sys
        
        # Get wheel files
        flask_wheel = wheels_dir / "flask-3.1.1-py3-none-any.whl"
        click_wheel = wheels_dir / "click-8.2.1-py3-none-any.whl"
        werkzeug_wheel = wheels_dir / "werkzeug-3.1.3-py3-none-any.whl"
        jinja2_wheel = wheels_dir / "jinja2-3.1.6-py3-none-any.whl"
        itsdangerous_wheel = wheels_dir / "itsdangerous-2.2.0-py3-none-any.whl"
        markupsafe_wheel = wheels_dir / "MarkupSafe-3.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
        blinker_wheel = wheels_dir / "blinker-1.9.0-py3-none-any.whl"
        
        wheels = [markupsafe_wheel, itsdangerous_wheel, click_wheel, blinker_wheel, werkzeug_wheel, jinja2_wheel, flask_wheel]
        
        for wheel in wheels:
            if wheel.exists():
                print(f"📦 Installing {wheel.name}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "--user", str(wheel)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"⚠️ Warning installing {wheel.name}: {result.stderr}")
        
        # Try importing again
        import flask
        print(f"✅ Flask successfully installed: {flask.__version__}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to install Flask: {e}")
        return False

def start_jules_server():
    """Start the Jules server using pure Python"""
    
    print("🚀 JULES STANDALONE SERVER")
    print("=" * 30)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Navigate to A2A system directory
    a2a_dir = Path("/mnt/c/Users/david/projects-master/a2a-system")
    if not a2a_dir.exists():
        print(f"❌ A2A directory not found: {a2a_dir}")
        return False
    
    # Change to A2A directory
    os.chdir(a2a_dir)
    print(f"✅ Changed to: {os.getcwd()}")
    
    # Add the directory to Python path
    if str(a2a_dir) not in sys.path:
        sys.path.insert(0, str(a2a_dir))
    
    # Check Flask
    if not check_and_install_flask():
        print("❌ Cannot proceed without Flask")
        return False
    
    # Import and start the server
    try:
        print("🔧 Importing Jules server...")
        
        # Import the server module
        spec = importlib.util.spec_from_file_location("jules_server", a2a_dir / "api" / "jules_server.py")
        jules_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(jules_module)
        
        print("✅ Jules server module loaded successfully")
        
        # Get the Flask app
        app = jules_module.app
        
        print("🌐 Starting server on http://127.0.0.1:5003...")
        print("🔗 Health check: http://127.0.0.1:5003/health")
        print("📝 Add task: POST to http://127.0.0.1:5003/add_task")
        print("📋 List tasks: GET http://127.0.0.1:5003/tasks")
        print("\nPress Ctrl+C to stop the server")
        
        # Start the server
        app.run(host="0.0.0.0", port=5003, debug=False)
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = start_jules_server()
    if not success:
        print("\n❌ Server startup failed")
        sys.exit(1)
    else:
        print("\n✅ Server stopped gracefully")
        sys.exit(0)