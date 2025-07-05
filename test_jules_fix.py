#!/usr/bin/env python3
"""
Quick validation test for Jules environment fix
"""

import sys
import subprocess
import time
import requests
from pathlib import Path

def test_environment():
    """Test if Jules environment is working"""
    
    print("🧪 Testing Jules Environment Fix")
    print("="*40)
    
    # Test 1: Check if virtual environment exists
    venv_path = Path("a2a-env")
    if venv_path.exists():
        print("✅ Virtual environment exists")
    else:
        print("❌ Virtual environment missing")
        return False
    
    # Test 2: Test Flask import
    try:
        result = subprocess.run([
            "bash", "-c", 
            "source a2a-env/bin/activate && python -c 'import flask; print(flask.__version__)'"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Flask import successful: {result.stdout.strip()}")
        else:
            print(f"❌ Flask import failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Flask test timed out")
        return False
    
    # Test 3: Check if server can start (just import test)
    try:
        result = subprocess.run([
            "bash", "-c", 
            "source a2a-env/bin/activate && python -c 'from api.jules_server import app; print(\"Server import successful\")'"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Jules server import successful")
        else:
            print(f"❌ Jules server import failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Server import test timed out")
        return False
    
    print("\n🎉 ALL TESTS PASSED! Jules environment is working!")
    return True

def main():
    """Run validation tests"""
    success = test_environment()
    
    if success:
        print("\n📋 Next Steps for Jules:")
        print("1. Run: ./start_jules.sh")
        print("2. Server will start on http://127.0.0.1:5002")
        print("3. Test with: curl http://127.0.0.1:5002/health")
        return 0
    else:
        print("\n❌ Environment still has issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())