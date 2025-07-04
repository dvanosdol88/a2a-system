# A2A System Setup Guide

## Prerequisites

- Python 3.12+
- bash shell environment

## Offline Installation (Recommended)

For environments with limited internet access (like CODEX):

```bash
# Run automated setup
./scripts/setup-offline.sh

# Activate environment
source a2a-env/bin/activate

# Start Jules API server
python api/jules_server.py
```

## Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv a2a-env

# Activate environment
source a2a-env/bin/activate

# Install dependencies offline
pip install --no-index --find-links wheels/ Flask requests pytest

# Start server
python api/jules_server.py
```

## Verification

Test the system is working:

```bash
# Health check
curl http://127.0.0.1:5000/health

# Add test task
curl -X POST -H "Content-Type: application/json" \
     -d '{"task": "Test from setup"}' \
     http://127.0.0.1:5000/add_task

# List tasks
curl http://127.0.0.1:5000/tasks

# Run test suite
pytest tests/
```

## Directory Structure

```
a2a-system/
├── api/jules_server.py    # Main API server
├── shared/tasks.json      # Task storage
├── tests/                 # Test suite
├── wheels/                # Offline dependencies
└── a2a-env/              # Virtual environment
```

## Next Steps

1. Complete setup verification
2. Review [API Reference](api-reference.md)
3. Run enhanced test suite
4. Begin agent coordination

## Troubleshooting

**Server won't start:**
- Check Python version: `python --version`
- Verify Flask installation: `python -c "import flask"`
- Check port availability: `lsof -i :5000`

**Tests failing:**
- Ensure server is running
- Check task file permissions
- Verify all dependencies installed

---
**Created**: July 4, 2025  
**Repository**: a2a-system