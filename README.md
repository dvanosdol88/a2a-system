# 🤖 A2A System - Agent-to-Agent Communication Platform

A sophisticated multi-agent system enabling seamless communication and coordination between AI agents (Claude, Jules, and CODEX).

## 🎯 Project Status: OPERATIONAL ✅

- **Jules API Server**: ✅ Running on port 5006
- **A2A Communication**: ✅ Hello World tests passed
- **Environment Setup**: ✅ Complete with virtual environment
- **Next Phase**: 🔧 CODEX orchestration layer development

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    A2A Communication System                 │
├─────────────────────────────────────────────────────────────┤
│  Claude (Monitor)    Jules (API Server)    CODEX (Router)  │
│      ↓                     ↓                     ↓         │
│  Monitoring &         Task Processing      Orchestration    │
│  Coordination           & Storage           & Routing       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12.3+
- Git

### Setup & Run
```bash
# Clone repository
git clone https://github.com/dvanosdol88/a2a-system.git
cd a2a-system

# Setup environment and start Jules server (single command)
python3 jules_pypi_setup.py

# Test communication (in separate terminal)
python3 test_hello_world.py
```

## 📁 Repository Structure

```
a2a-system/
├── api/                    # Jules API server
│   └── jules_server.py     # Main Flask API server
├── orchestration/          # CODEX coordination layer [In Development]
├── monitoring/             # System monitoring & analytics
│   ├── dashboard_server.py # Real-time monitoring dashboard
│   └── advanced_analytics.py # Performance analysis
├── shared/                 # Shared utilities & data
│   ├── message_types.py    # A2A message definitions
│   └── tasks.json          # Task storage
├── scripts/                # Setup & deployment
│   ├── production_readiness_check.py # Production validation
│   └── deploy_automation.py # Automated deployment
├── tests/                  # Test suites
│   ├── test_hello_world.py # Basic A2A communication test
│   └── integration_test_suite.py # Comprehensive testing
├── docs/                   # Documentation
└── wheels/                 # Python dependencies (offline installation)
```

## 🔧 Agent Setup Guides

### For Jules
```bash
# Single command setup and server start
python3 jules_pypi_setup.py
# Server starts automatically on http://127.0.0.1:5006
```

### For CODEX
See `CODEX_PROJECT_BRIEFING.md` for detailed setup and objectives.

### For Claude
Complete monitoring and coordination tools available in `monitoring/` directory.

## 🌐 API Endpoints

### Jules Server (Port 5006)
- **Health Check**: `GET /health`
- **Add Task**: `POST /add_task`
- **List Tasks**: `GET /tasks`

### Example Usage
```python
import requests

# Send task to Jules
response = requests.post("http://127.0.0.1:5006/add_task", 
                        json={"task": "Hello from agent!"})

# Get all tasks
tasks = requests.get("http://127.0.0.1:5006/tasks").json()
```

## 🧪 Testing

### Hello World Test
```bash
python3 test_hello_world.py
```

Expected output:
```
🧪 A2A HELLO WORLD MESSAGE TEST
✅ Jules server healthy
✅ Message sent successfully
✅ Retrieved 8 messages
🎯 A2A Hello World Test: SUCCESS! 🎉
```

### Comprehensive Testing
```bash
python3 tests/integration_test_suite.py
python3 scripts/production_readiness_check.py
```

## 📊 Current Capabilities

### ✅ Working Features
- **Agent Communication**: Bidirectional messaging between agents
- **Task Persistence**: Messages stored and retrievable
- **Health Monitoring**: Server status and performance tracking
- **Virtual Environment**: Complete dependency isolation
- **Production Tools**: Deployment and validation scripts

### 🔧 In Development
- **Orchestration Layer**: CODEX intelligent task routing
- **Advanced Workflows**: Multi-agent coordination patterns
- **Performance Optimization**: System tuning and scaling

## 🚨 Important Notes

### Environment Setup
This repository includes complete environment setup with offline wheel dependencies to ensure consistent installations across different systems.

### Server Management
Jules server runs on port 5006 to avoid conflicts. The server includes automatic health checking and graceful error handling.

### Agent Coordination
Each agent has specific responsibilities:
- **Claude**: System monitoring, development, and coordination
- **Jules**: Task processing and API services
- **CODEX**: Orchestration and intelligent routing

## 📋 Development Status

### Completed ✅
- [x] Jules API server implementation
- [x] Virtual environment setup with Flask
- [x] A2A communication protocol
- [x] Hello World message testing
- [x] Production readiness tools
- [x] Comprehensive documentation

### In Progress 🔧
- [ ] CODEX orchestration layer
- [ ] Advanced workflow management
- [ ] Performance optimization

### Planned 📅
- [ ] Web-based monitoring dashboard
- [ ] Advanced analytics and reporting
- [ ] Production deployment automation
- [ ] Multi-environment support

## 🤝 Contributing

This is a multi-agent development project. Each agent contributes to their specialized areas:

- **Jules**: API development and task processing
- **CODEX**: Orchestration and coordination logic
- **Claude**: System integration and monitoring

## 📞 Support

For questions about specific components:
- **API Issues**: See `JULES_DEFINITIVE_SOLUTION.md`
- **Setup Problems**: Run `diagnose_jules_environment.py`
- **Orchestration**: See `CODEX_PROJECT_BRIEFING.md`

---

**Status**: Active development | **Last Updated**: July 2025 | **Version**: 1.0.0-beta