# 🚨 URGENT: Jules Python Environment Fix

## The Problem
Jules can't run Python scripts because **Flask is not installed**. The scripts timeout because they can't import required modules.

## The Solution (Do This First!)

### Step 1: Run Setup Script
```bash
cd /mnt/c/Users/david/projects-master/a2a-system
./scripts/setup-offline.sh
```

### Step 2: Activate Virtual Environment  
```bash
source a2a-env/bin/activate
```

### Step 3: Verify Installation
```bash
python --version
python -c "import flask; print('Flask installed:', flask.__version__)"
```

### Step 4: Start Jules API Server
```bash
python api/jules_server.py
```

## Why This Happened
- Python 3.12.3 is installed system-wide ✅
- Flask and dependencies are NOT installed system-wide ❌
- Jules needs to use the virtual environment with all dependencies

## Quick Test
Before running any Python scripts, always:
1. Check if `a2a-env/` directory exists
2. If not, run `./scripts/setup-offline.sh`
3. Always run `source a2a-env/bin/activate` first
4. Then run Python scripts

## Verification Commands
```bash
# Test basic Python (should work)
python3 -c "print('Hello World')"

# Test Flask import (will fail without venv)
python3 -c "import flask"

# Test Flask import (should work in venv)
source a2a-env/bin/activate
python -c "import flask; print('Flask working!')"
```

---
**This is the same environment setup issue we solved before. Jules just needs to activate the virtual environment!** 🔧