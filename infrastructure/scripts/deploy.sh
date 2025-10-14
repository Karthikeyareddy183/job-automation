#!/bin/bash
# Production deployment script

set -e

echo "=== Deploying Job Automation System ==="

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Build and restart services
echo "Building Docker containers..."
cd infrastructure/docker
docker-compose -f docker-compose.prod.yml build

echo "Stopping old containers..."
docker-compose -f docker-compose.prod.yml down

echo "Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

echo "✅ Deployment complete!"
echo "Services running:"
docker-compose -f docker-compose.prod.yml ps
