# Deploy A2A System to Render - Step by Step

## Option 1: Deploy via Render Dashboard (Easiest)

### Step 1: Push to GitHub
```bash
git push origin main
```

### Step 2: Create Services in Render Dashboard

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository: `dvanosdol88/projects-master`
4. Select the branch: `main`
5. Set Blueprint path: `a2a-system/render.yaml`
6. Click "Apply"

### Step 3: Configure Environment Variables

After blueprint creation, for each service set:

**For a2a-jules service:**
- `GITHUB_TOKEN`: Your GitHub personal access token
- `A2A_SECRET_KEY`: Click "Generate" or use: `RamOJOZDSokSsZpNZIrtAsqhZlleVoYZDSnLRFmikpI`

**Database will be created automatically**

### Step 4: Deploy
- Click "Deploy" for each service
- Wait for services to become healthy

## Option 2: Manual Service Creation

If blueprint doesn't work, create services manually:

### 1. Create PostgreSQL Database
- New → PostgreSQL
- Name: `a2a-db`
- Plan: Starter (free)
- Create Database

### 2. Create Jules API Service
- New → Web Service
- Repository: `dvanosdol88/projects-master`
- Name: `a2a-jules`
- Root Directory: `a2a-system`
- Environment: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `python api/jules_server.py`
- Add environment variables:
  - `A2A_DATABASE_URL`: (copy from database Internal Database URL)
  - `A2A_SECRET_KEY`: Generate new value
  - `A2A_ENABLE_AUTH`: `true`
  - `GITHUB_TOKEN`: Your token
  - `GITHUB_OWNER`: `dvanosdol88`

### 3. Create Dashboard Service
- Similar to Jules, but:
- Name: `a2a-dashboard`
- Start Command: `python monitoring/dashboard_server.py`
- Add: `A2A_JULES_API_URL`: `https://a2a-jules.onrender.com`

## Verification Steps

Once deployed, test your services:

```bash
# Test Jules API health
curl https://a2a-jules.onrender.com/health

# Test Dashboard
curl https://a2a-dashboard.onrender.com/health

# Test API with authentication (if enabled)
curl -H "X-API-Key: your-api-key" https://a2a-jules.onrender.com/tasks
```

## Post-Deployment

1. **Get your API key**:
   - SSH into Jules service
   - Run: `python -c "from database.db_manager import db; print(db.create_api_key('Production'))"`

2. **Configure agents**:
   - Update agent configurations with production URLs
   - Set API keys for authentication

3. **Monitor services**:
   - Check Render dashboard for logs
   - Set up health check alerts

Your A2A system will be running privately on Render's infrastructure!