# A2A System Backup & Restore Guide

## Automatic Backups

### 1. Render Persistent Disk
- SQLite database is stored on persistent disk
- Survives deployments and restarts
- 1GB storage allocated

### 2. GitHub Actions Daily Backup
- Runs daily at 2 AM UTC
- Stores backups as GitHub artifacts
- 30-day retention
- Weekly backups create GitHub releases

### 3. Manual Backup

```bash
# Run backup script
python scripts/backup_data.py

# Backups are saved to: backups/a2a_backup_YYYYMMDD_HHMMSS.zip
```

## Backup Contents

Each backup includes:
- `shared/tasks.json` - All task history
- `shared/agent_tasks.json` - Agent-specific tasks
- `database/a2a_system.db` - SQLite database (if used)
- `backup_metadata.json` - Backup information

## Restore Process

### From Local Backup
```bash
# List available backups
ls backups/

# Extract backup
unzip backups/a2a_backup_20250111_120000.zip -d restore_temp/

# Review contents
cat restore_temp/backup_metadata.json

# Copy files (careful - this overwrites current data!)
cp restore_temp/shared/*.json shared/
```

### From GitHub Artifact
1. Go to Actions → Backup workflow
2. Download artifact from successful run
3. Extract and restore as above

### From GitHub Release
1. Go to Releases
2. Download backup zip from weekly release
3. Extract and restore as above

## Production Backup Strategy

### Current Implementation
✅ Persistent disk for database
✅ GitHub Actions for automated backups
✅ Manual backup script available

### Recommended Additions
1. **External Backup** (for critical data)
   - S3 bucket
   - Google Cloud Storage
   - Backblaze B2

2. **Database Replication** (if using PostgreSQL)
   - Render supports read replicas
   - Point-in-time recovery

3. **Export Endpoints**
   ```python
   @app.route("/export/tasks")
   @require_auth  # Add authentication!
   def export_tasks():
       return jsonify(tasks)
   ```

## Backup Commands

### Create backup now
```bash
python scripts/backup_data.py
```

### Trigger GitHub Action manually
1. Go to Actions tab
2. Select "A2A Data Backup"
3. Click "Run workflow"

### Download all tasks (public endpoint)
```bash
curl https://a2a-jules.onrender.com/tasks > tasks_backup.json
```

## Recovery Time Objectives

- **Local backup**: < 5 minutes
- **GitHub artifact**: < 10 minutes  
- **Full rebuild**: < 30 minutes

## Important Notes

⚠️ **Security**: Production backups should use authenticated endpoints
⚠️ **Privacy**: Ensure backups are stored securely
⚠️ **Testing**: Regularly test restore procedures
✅ **Automation**: Backups run automatically via GitHub Actions