#!/usr/bin/env bash

set -euo pipefail

echo "🚀 Starting production deployment..."

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

# Build the AI Connector image
echo "📦 Building AI Connector image..."
docker build -t a2a-ai-connector:latest -f agents/ai_connector.Dockerfile .

# Deploy the production stack
echo "🔧 Deploying production stack..."
cd infra/broker
docker compose -f docker-compose-broker.yml -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check Redis health
echo "🏥 Checking Redis health..."
docker exec a2a-redis redis-cli PING

echo "✅ Production deployment complete!"