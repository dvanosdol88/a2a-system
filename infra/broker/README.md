# Broker Infrastructure

This directory provides a minimal Redis broker and the AI Connector service.

## Start the broker

```bash
docker compose -f docker-compose-broker.yml up -d
```

Starting the broker with Docker Compose will also launch the Redis-backed AI Connector service.

## Stop the broker

```bash
docker compose -f docker-compose-broker.yml down
```

## Production Deployment

```bash
docker compose -f docker-compose-broker.yml -f docker-compose.prod.yml up -d
```
