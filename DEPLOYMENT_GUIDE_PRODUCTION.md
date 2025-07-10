# A2A System Production Deployment Guide

## 🚀 Deployment Options

### Option 1: Render.com (Recommended)
Simple, scalable, with free tier available.

1. **Login to Render CLI**:
   ```bash
   render login
   ```

2. **Deploy with Blueprint**:
   ```bash
   render blueprint launch
   ```

3. **Or deploy manually**:
   - Go to https://render.com
   - Connect your GitHub repository
   - Use the `render.yaml` blueprint
   - Set environment variables

### Option 2: Docker on VPS
For full control on DigitalOcean, AWS EC2, etc.

1. **On your server**:
   ```bash
   # Clone repository
   git clone https://github.com/dvanosdol88/a2a-system.git
   cd a2a-system
   
   # Copy and edit production config
   cp .env.production .env
   nano .env
   
   # Start with Docker Compose
   docker-compose --env-file .env up -d
   ```

2. **Set up Nginx for SSL**:
   ```nginx
   server {
       listen 443 ssl;
       server_name a2a.yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/a2a.yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/a2a.yourdomain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:5006;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Option 3: Railway.app
One-click deployment with GitHub integration.

1. Visit https://railway.app
2. Connect GitHub repository
3. Add PostgreSQL database
4. Set environment variables
5. Deploy

## 🔑 Required Environment Variables

```bash
# Security (MUST CHANGE)
A2A_SECRET_KEY=<generate-with-script>
A2A_ENABLE_AUTH=true

# Database
A2A_DB_TYPE=postgresql
A2A_DATABASE_URL=<from-cloud-provider>

# GitHub
GITHUB_TOKEN=<your-github-token>
GITHUB_OWNER=dvanosdol88

# Production
A2A_ENVIRONMENT=production
A2A_LOG_LEVEL=INFO
```

## 📊 Post-Deployment Checklist

- [ ] Verify all services are running:
  ```bash
  curl https://your-jules-api.com/health
  curl https://your-dashboard.com/health
  ```

- [ ] Create production API key:
  ```bash
  ./scripts/production-setup.sh
  ```

- [ ] Test API with key:
  ```bash
  curl -H "X-API-Key: your-key" https://your-api.com/tasks
  ```

- [ ] Configure monitoring (UptimeRobot, Pingdom)
- [ ] Set up automated backups
- [ ] Configure alerts for errors

## 🔒 Security Hardening

1. **Firewall Rules**:
   - Only expose necessary ports (443, 80)
   - Whitelist admin IPs if needed

2. **API Security**:
   - Rotate API keys regularly
   - Monitor rate limit violations
   - Review access logs

3. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Regular backups

## 🚨 Monitoring Setup

1. **Application Monitoring**:
   - Health checks every 5 minutes
   - Alert on service downtime
   - Monitor response times

2. **Log Aggregation**:
   - Ship logs to CloudWatch/Datadog
   - Set up error alerts
   - Track performance metrics

## 💾 Backup Strategy

1. **Database Backups**:
   ```bash
   # Automated daily backups
   0 2 * * * pg_dump $DATABASE_URL > /backups/a2a_$(date +\%Y\%m\%d).sql
   ```

2. **File Backups**:
   - Task data
   - Configuration files
   - Agent logs

## 🎯 Ready to Deploy!

Your A2A system is configured for production deployment. Choose your platform and follow the steps above. The system will handle agent coordination securely in your private environment.