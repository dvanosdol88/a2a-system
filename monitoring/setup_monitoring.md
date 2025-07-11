# A2A System Monitoring Setup

## Built-in Monitoring

### 1. Render Dashboard
- **URL**: https://dashboard.render.com
- **Features**:
  - Service health status
  - Memory/CPU usage
  - Request logs
  - Deploy history
  - Automatic restart on failure

### 2. Health Endpoints
- Jules API: https://a2a-jules.onrender.com/health
- Dashboard: https://a2a-dashboard.onrender.com/api/health

### 3. Interactive Dashboard
- **URL**: https://a2a-dashboard.onrender.com
- Real-time task monitoring
- Agent status visualization
- Live activity feed

## External Monitoring Options

### Option 1: UptimeRobot (Free)
1. Sign up at https://uptimerobot.com
2. Add monitors:
   - Jules API: https://a2a-jules.onrender.com/health
   - Dashboard: https://a2a-dashboard.onrender.com/api/health
3. Set check interval: 5 minutes
4. Configure alerts: Email, SMS, Slack

### Option 2: Cronitor
1. Sign up at https://cronitor.io
2. Create monitors for each endpoint
3. Set up alerting rules
4. Get detailed performance metrics

### Option 3: GitHub Actions (Free)
Create `.github/workflows/health-check.yml`:
```yaml
name: A2A Health Check
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check Jules API
        run: |
          curl -f https://a2a-jules.onrender.com/health || exit 1
          
      - name: Check Dashboard
        run: |
          curl -f https://a2a-dashboard.onrender.com/api/health || exit 1
          
      - name: Send Alert on Failure
        if: failure()
        run: |
          echo "Services are down! Send alert here"
```

## Local Monitoring Script

Run `health_monitor.py` locally or on a cron job:

```bash
# Test now
python monitoring/health_monitor.py

# Add to crontab (every 5 minutes)
*/5 * * * * cd /path/to/a2a-system && python monitoring/health_monitor.py
```

## Render Built-in Alerts

Render automatically:
- Restarts crashed services
- Sends email alerts for failures
- Monitors memory/CPU usage
- Tracks deployment status

## Current Status
✅ Services have health endpoints
✅ Render provides basic monitoring
✅ Health check script created
✅ Documentation complete

## Recommended Setup
1. Use Render's built-in monitoring (already active)
2. Add UptimeRobot for external monitoring (free)
3. Use the interactive dashboard for real-time monitoring