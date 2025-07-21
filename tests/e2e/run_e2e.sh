#!/usr/bin/env bash
set -e
pytest tests/e2e/test_full_workflow.py --maxfail=1 --disable-warnings
