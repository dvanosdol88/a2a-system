# Offline Dependencies for A2A System

This directory contains pre-downloaded Python package wheels for offline installation in restricted environments like CODEX.

## Contents (17 packages)

### Core Dependencies
- `flask-3.1.1-py3-none-any.whl` - Main web framework
- `requests-2.32.4-py3-none-any.whl` - HTTP client library
- `pytest-8.4.1-py3-none-any.whl` - Testing framework

### Flask Dependencies
- `blinker-1.9.0-py3-none-any.whl`
- `click-8.2.1-py3-none-any.whl`
- `itsdangerous-2.2.0-py3-none-any.whl`
- `jinja2-3.1.6-py3-none-any.whl`
- `MarkupSafe-3.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`
- `werkzeug-3.1.3-py3-none-any.whl`

### Requests Dependencies
- `certifi-2025.6.15-py3-none-any.whl`
- `charset_normalizer-3.4.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`
- `idna-3.10-py3-none-any.whl`
- `urllib3-2.5.0-py3-none-any.whl`

### Pytest Dependencies
- `iniconfig-2.1.0-py3-none-any.whl`
- `packaging-25.0-py3-none-any.whl`
- `pluggy-1.6.0-py3-none-any.whl`
- `pygments-2.19.2-py3-none-any.whl`

## Installation

### Automatic
```bash
./setup-a2a-offline.sh
```

### Manual
```bash
python3 -m venv a2a-env
source a2a-env/bin/activate
pip install --no-index --find-links wheels/ Flask requests pytest
```

## Regenerating Wheels

If you need to update dependencies:
```bash
pip download Flask requests pytest --dest wheels/
```

## Purpose

Enables A2A system deployment in environments without internet access by providing all required dependencies as local wheel files.

---
**Created**: 2025-07-04  
**Total Size**: ~2.7MB  
**Python Version**: 3.12+ compatible