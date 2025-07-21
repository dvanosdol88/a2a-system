# Production Runbook

## Deployment

1. **Deploy the production stack:**
   ```bash
   bash scripts/deploy_production.sh
   ```

2. **Verify deployment:**
   ```bash
   docker ps
   redis-cli PING
   ```

## Health Checks

- **Redis health:** `docker exec a2a-redis redis-cli PING`
- **AI Connector logs:** `docker logs a2a-ai-connector`
- **Container status:** `docker ps --filter "name=a2a"`

## Monitoring

- Redis metrics: `docker exec a2a-redis redis-cli INFO`
- Container resource usage: `docker stats a2a-redis a2a-ai-connector`

## Backup

1. **Trigger Redis backup:**
   ```bash
   redis-cli BGSAVE
   ```

2. **Check backup status:**
   ```bash
   redis-cli LASTSAVE
   ```

3. **Backup location:** `/data/dump.rdb` inside the Redis container

## Rollback

If issues occur:

1. **Stop production stack:**
   ```bash
   cd infra/broker
   docker compose -f docker-compose-broker.yml -f docker-compose.prod.yml down
   ```

2. **Restore previous version:**
   ```bash
   git checkout <previous-version>
   bash scripts/deploy_production.sh
   ```

## Troubleshooting

- **Redis connection issues:** Check firewall rules and ensure port 6379 is accessible
- **AI Connector not processing:** Check logs with `docker logs a2a-ai-connector`
- **High memory usage:** Monitor with `docker stats` and adjust Redis maxmemory if needed