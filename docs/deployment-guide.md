# A2A System Deployment Guide

## Overview

The A2A (Agent-to-Agent) System is a production-ready multi-agent communication platform. This guide covers deployment options from local development to cloud production environments.

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.12+ (for native deployment)
- PostgreSQL (optional, for production database)
- GitHub account (for agent integrations)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/a2a-system.git
cd a2a-system
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

Required configuration:
- `A2A_SECRET_KEY` - Change from default for production
- `GITHUB_TOKEN` - For GitHub integrations
- `GITHUB_OWNER` - Your GitHub username

### 3. Deploy with Docker Compose

```bash
# Development deployment
docker-compose up -d

# Production deployment with PostgreSQL
docker-compose --profile postgres up -d
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

Perfect for single-server deployments.

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services exposed:
- Jules API: http://localhost:5006
- Dashboard: http://localhost:5003
- FlowForge UI: http://localhost:5002

### Option 2: Kubernetes

For scalable cloud deployments.

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a2a-jules
spec:
  replicas: 3
  selector:
    matchLabels:
      app: a2a-jules
  template:
    metadata:
      labels:
        app: a2a-jules
    spec:
      containers:
      - name: jules
        image: a2a-system:latest
        ports:
        - containerPort: 5006
        env:
        - name: A2A_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: a2a-secrets
              key: database-url
```

### Option 3: Cloud Platforms

#### Render.com

1. Connect GitHub repository
2. Create Web Services for each component
3. Set environment variables
4. Deploy

#### Heroku

```bash
# Create apps
heroku create a2a-jules
heroku create a2a-dashboard

# Set buildpacks
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

#### AWS ECS

Use provided `ecs-task-definition.json` for AWS deployment.

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `A2A_SECRET_KEY` | Secret key for security | dev-secret-key | Yes (production) |
| `A2A_ENABLE_AUTH` | Enable API authentication | false | Yes (production) |
| `A2A_DB_TYPE` | Database type (sqlite/postgresql) | sqlite | No |
| `A2A_DATABASE_URL` | Database connection string | a2a_system.db | No |
| `GITHUB_TOKEN` | GitHub API token | - | For GitHub features |
| `GITHUB_OWNER` | GitHub username | - | For GitHub features |

### Database Setup

#### SQLite (Default)
No setup required - database created automatically.

#### PostgreSQL (Production)

```bash
# Create database
createdb a2a_system

# Run migrations
python -c "from database.db_manager import db; db.init_database()"
```

### SSL/TLS Configuration

For production, use a reverse proxy (nginx/Caddy) with SSL:

```nginx
server {
    listen 443 ssl;
    server_name a2a.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5006;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Considerations

1. **Change Default Secrets**: Always change `A2A_SECRET_KEY` in production
2. **Enable Authentication**: Set `A2A_ENABLE_AUTH=true`
3. **Use HTTPS**: Deploy behind SSL/TLS termination
4. **Rate Limiting**: Enable with `A2A_RATE_LIMIT_ENABLED=true`
5. **Network Security**: Use firewalls to restrict access

## Monitoring

### Health Checks

All services expose health endpoints:

```bash
# Check Jules API
curl http://localhost:5006/health

# Check Dashboard
curl http://localhost:5003/health
```

### Logging

Logs are stored in:
- Container: `/app/logs/`
- Host: `./logs/`

View logs:
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs jules

# Follow logs
docker-compose logs -f
```

### Metrics

System metrics available at:
- Dashboard: http://localhost:5003
- Metrics endpoint: `/metrics` (when enabled)

## Backup & Recovery

### Database Backup

```bash
# SQLite
cp data/a2a_system.db backups/a2a_system_$(date +%Y%m%d).db

# PostgreSQL
pg_dump a2a_system > backups/a2a_system_$(date +%Y%m%d).sql
```

### Restore

```bash
# SQLite
cp backups/a2a_system_20240710.db data/a2a_system.db

# PostgreSQL
psql a2a_system < backups/a2a_system_20240710.sql
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Change ports in docker-compose.yml or .env
   A2A_JULES_PORT=5106
   ```

2. **Database connection errors**
   ```bash
   # Check database URL
   echo $A2A_DATABASE_URL
   
   # Test connection
   python -c "from database.db_manager import db; print(db.get_connection())"
   ```

3. **Authentication failures**
   ```bash
   # Create new API key
   python -c "from database.db_manager import db; print(db.create_api_key('test'))"
   ```

### Debug Mode

Enable debug logging:
```bash
export A2A_DEBUG=true
export A2A_LOG_LEVEL=DEBUG
```

## Production Checklist

- [ ] Change all default secrets
- [ ] Enable authentication (`A2A_ENABLE_AUTH=true`)
- [ ] Configure PostgreSQL database
- [ ] Set up SSL/TLS certificates
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Test disaster recovery
- [ ] Document API keys
- [ ] Review security settings

## Support

- GitHub Issues: [Report bugs and features](https://github.com/YOUR_USERNAME/a2a-system/issues)
- Documentation: [Full documentation](https://a2a-docs.yourdomain.com)
- Community: [Discord/Slack channel]

---

Last updated: July 2025