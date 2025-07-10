# A2A System - Agent-to-Agent Communication Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A production-ready multi-agent communication system enabling seamless collaboration between AI agents.

## 🚀 Features

- **Multi-Agent Architecture**: Coordinate Claude, CODEX, Jules, and custom agents
- **RESTful API**: Simple HTTP endpoints for agent communication
- **Real-time Dashboard**: Monitor agent activity and message flow
- **Flexible Storage**: Support for SQLite and PostgreSQL
- **Security Built-in**: API authentication, rate limiting, and secure tokens
- **Docker Ready**: Full containerization with docker-compose
- **Production Ready**: Logging, monitoring, and deployment configurations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    A2A Communication System                  │
├─────────────────────────────────────────────────────────────┤
│  User → Claude → CODEX → Jules → GitHub/Computer/Internet   │
│         ↓         ↓        ↓                                │
│    Coordination  Tasks   Storage                            │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/a2a-system.git
cd a2a-system

# Copy environment configuration
cp .env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database.db_manager import db; db.init_database()"

# Start Jules API server
python api/jules_server.py
```

## 🌐 API Endpoints

### Jules API (Port 5006)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/add_task` | POST | Add new task |
| `/tasks` | GET | List all tasks |
| `/api/v1/agents/status` | GET | Agent status |

### Example Usage

```python
import requests

# Add task
response = requests.post("http://localhost:5006/add_task", 
    json={"task": "Hello from my agent!"},
    headers={"X-API-Key": "your-api-key"}  # If auth enabled
)

# Get tasks
tasks = requests.get("http://localhost:5006/tasks").json()
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# Security
A2A_SECRET_KEY=your-secret-key-here
A2A_ENABLE_AUTH=true  # Enable in production

# Database
A2A_DB_TYPE=postgresql  # or sqlite
A2A_DATABASE_URL=postgresql://user:pass@localhost/a2a

# GitHub Integration
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=your-username

# Monitoring
A2A_LOG_LEVEL=INFO
A2A_ENVIRONMENT=production
```

## 🚀 Deployment

### Cloud Platforms

- **Render**: One-click deploy with `render.yaml`
- **Heroku**: Buildpack ready
- **AWS/GCP**: Docker images available
- **Kubernetes**: Helm charts in `/k8s`

### Production Checklist

- [ ] Change default secrets
- [ ] Enable authentication
- [ ] Configure SSL/TLS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review rate limits

## 🛡️ Security

- API key authentication
- Rate limiting per key/IP
- Secure token generation
- Environment-based configuration
- SQL injection protection

## 📊 Monitoring

Access the dashboard at `http://localhost:5003` for:
- Real-time agent status
- Message flow visualization
- System metrics
- Performance analytics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for multi-agent AI collaboration
- Inspired by modern microservice architectures
- Designed for extensibility and scale

## 📞 Support

- 📧 Email: support@your-domain.com
- 💬 Discord: [Join our community](https://discord.gg/your-invite)
- 📖 Docs: [Full documentation](https://docs.your-domain.com)

---

Made with ❤️ by the A2A Team