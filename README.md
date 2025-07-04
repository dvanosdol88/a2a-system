# A2A System - Agent-to-Agent Communication

**Clean, dedicated repository for Claude-Jules communication system**

## Overview

The A2A (Agent-to-Agent) system enables seamless communication between AI agents through a robust Flask API server with offline deployment capabilities.

## Quick Start

```bash
# Setup offline environment
./scripts/setup-offline.sh

# Start Jules API server
source a2a-env/bin/activate
python api/jules_server.py

# Run tests
pytest tests/
```

## Repository Structure

```
a2a-system/
├── api/           # API server and endpoints
├── shared/        # Communication utilities and protocols
├── tests/         # Comprehensive test suite
├── docs/          # Documentation and guides
├── scripts/       # Setup and deployment scripts
├── config/        # Configuration files
├── wheels/        # Offline dependencies
└── README.md      # This file
```

## Features

- **Offline Deployment**: Zero internet dependency
- **Rich Messaging**: JSON-based communication protocols
- **Session Management**: Persistent state tracking
- **Comprehensive Testing**: Interactive test scenarios
- **Monitoring**: Real-time system health checks

## Documentation

- [Setup Guide](docs/setup-guide.md)
- [API Reference](docs/api-reference.md)
- [Testing Guide](docs/testing-guide.md)
- [Architecture](docs/architecture.md)

## Status

✅ **Phase 1 Complete**: Basic communication operational  
🚧 **Phase 2 Active**: Enhanced testing framework  
📋 **Phase 3 Planned**: Monitoring and orchestration  

---
**Created**: July 4, 2025  
**Purpose**: Clean A2A system development