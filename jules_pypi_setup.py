#!/usr/bin/env python3
"""
Jules PyPI Setup - Create environment and install Flask from PyPI
This is the fallback solution when wheels directory isn't available
"""

import subprocess
import sys
import os
from pathlib import Path

def setup_jules_environment():
    """Set up Jules environment using PyPI packages"""
    
    print("🔧 JULES PYPI SETUP")
    print("=" * 20)
    
    # Navigate to A2A directory
    a2a_dir = Path("/mnt/c/Users/david/projects-master/a2a-system")
    if not a2a_dir.exists():
        a2a_dir = Path.cwd()  # Use current directory if path doesn't exist
    
    os.chdir(a2a_dir)
    print(f"✅ Working directory: {os.getcwd()}")
    
    # Step 1: Create virtual environment
    venv_dir = Path("a2a-env")
    if venv_dir.exists():
        print("✅ Virtual environment already exists")
    else:
        print("📦 Creating virtual environment...")
        try:
            result = subprocess.run([sys.executable, "-m", "venv", "a2a-env"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Virtual environment created successfully")
            else:
                print(f"❌ Failed to create virtual environment: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Virtual environment creation timed out")
            return False
        except Exception as e:
            print(f"❌ Error creating virtual environment: {e}")
            return False
    
    # Step 2: Check virtual environment Python
    venv_python = venv_dir / "bin" / "python"
    if not venv_python.exists():
        print("❌ Virtual environment Python not found")
        return False
    
    print(f"✅ Virtual environment Python: {venv_python}")
    
    # Step 3: Upgrade pip in virtual environment
    print("🔄 Upgrading pip...")
    try:
        result = subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Pip upgraded successfully")
        else:
            print(f"⚠️ Pip upgrade warning: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Pip upgrade timed out")
        return False
    except Exception as e:
        print(f"❌ Pip upgrade error: {e}")
        return False
    
    # Step 4: Install Flask from PyPI
    print("🌶️ Installing Flask from PyPI...")
    try:
        result = subprocess.run([str(venv_python), "-m", "pip", "install", "flask==3.1.1"], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Flask installed successfully from PyPI")
        else:
            print(f"❌ Flask installation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Flask installation timed out")
        return False
    except Exception as e:
        print(f"❌ Flask installation error: {e}")
        return False
    
    # Step 5: Test Flask installation
    print("🧪 Testing Flask installation...")
    try:
        result = subprocess.run([str(venv_python), "-c", "import flask; print('Flask version:', flask.__version__)"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Flask test successful: {result.stdout.strip()}")
        else:
            print(f"❌ Flask test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Flask test timed out")
        return False
    except Exception as e:
        print(f"❌ Flask test error: {e}")
        return False
    
    # Step 6: Create shared directory and tasks.json if needed
    shared_dir = Path("shared")
    if not shared_dir.exists():
        shared_dir.mkdir()
        print("✅ Created shared directory")
    
    tasks_file = shared_dir / "tasks.json"
    if not tasks_file.exists():
        tasks_file.write_text("[]")
        print("✅ Created tasks.json file")
    
    print("\n🎉 SETUP COMPLETE!")
    print("✅ Virtual environment ready")
    print("✅ Flask installed and tested")
    print("✅ Required directories created")
    print("\n🚀 Ready to run: python3 jules_ultimate_fix.py")
    
    return True

if __name__ == "__main__":
    success = setup_jules_environment()
    if success:
        print("\n✅ Jules environment setup successful!")
    else:
        print("\n❌ Jules environment setup failed")
        sys.exit(1)