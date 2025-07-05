#!/usr/bin/env python3
"""
Comprehensive environment diagnostic for Jules
This script will help identify why Jules' environment differs from Claude's
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def run_diagnostic():
    """Run comprehensive environment diagnostic"""
    
    print("🔍 JULES ENVIRONMENT DIAGNOSTIC")
    print("=" * 50)
    
    # Basic system info
    print("\n📊 SYSTEM INFORMATION:")
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"User: {os.environ.get('USER', 'unknown')}")
    print(f"Home directory: {os.environ.get('HOME', 'unknown')}")
    
    # Path information
    print("\n🛤️  PATH INFORMATION:")
    print(f"Python path: {sys.path}")
    print(f"PATH environment: {os.environ.get('PATH', 'not set')}")
    
    # File system access
    print("\n📁 FILE SYSTEM ACCESS:")
    current_dir = Path.cwd()
    print(f"Current directory exists: {current_dir.exists()}")
    print(f"Current directory is writable: {os.access(current_dir, os.W_OK)}")
    
    # Check A2A system directory
    a2a_dir = Path("/mnt/c/Users/david/projects-master/a2a-system")
    print(f"A2A directory exists: {a2a_dir.exists()}")
    if a2a_dir.exists():
        print(f"A2A directory is readable: {os.access(a2a_dir, os.R_OK)}")
        print(f"A2A directory is writable: {os.access(a2a_dir, os.W_OK)}")
        print(f"A2A directory contents: {list(a2a_dir.iterdir())[:10]}")  # First 10 items
    
    # Python import test
    print("\n🐍 PYTHON IMPORT TESTS:")
    try:
        import json
        print("✅ json module: OK")
    except ImportError as e:
        print(f"❌ json module: {e}")
    
    try:
        import pathlib
        print("✅ pathlib module: OK")
    except ImportError as e:
        print(f"❌ pathlib module: {e}")
    
    # Virtual environment check
    print("\n🔧 VIRTUAL ENVIRONMENT:")
    venv_path = Path("a2a-env")
    print(f"Virtual environment exists: {venv_path.exists()}")
    if venv_path.exists():
        print(f"Virtual environment structure: {list(venv_path.iterdir())}")
        
        # Check if activate script exists
        activate_script = venv_path / "bin" / "activate"
        print(f"Activate script exists: {activate_script.exists()}")
        
        # Try to get Python version from venv
        venv_python = venv_path / "bin" / "python"
        print(f"Virtual env Python exists: {venv_python.exists()}")
    
    # Command execution test
    print("\n⚡ COMMAND EXECUTION TESTS:")
    
    # Test 1: Simple command
    try:
        result = subprocess.run(["pwd"], capture_output=True, text=True, timeout=5)
        print(f"✅ pwd command: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ pwd command failed: {e}")
    
    # Test 2: Python version
    try:
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True, timeout=5)
        print(f"✅ python3 --version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ python3 --version failed: {e}")
    
    # Test 3: Which python
    try:
        result = subprocess.run(["which", "python3"], capture_output=True, text=True, timeout=5)
        print(f"✅ which python3: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ which python3 failed: {e}")
    
    # Environment variables
    print("\n🌍 ENVIRONMENT VARIABLES:")
    important_vars = ["PATH", "PYTHONPATH", "HOME", "USER", "SHELL", "TERM"]
    for var in important_vars:
        value = os.environ.get(var, "NOT SET")
        print(f"{var}: {value}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC COMPLETE")
    print("Please share this output to help identify the environment differences.")

if __name__ == "__main__":
    run_diagnostic()