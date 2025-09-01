#!/bin/bash

# SEAS Financial Tracker Deployment Script
# Usage: ./deploy.sh [staging|production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
APP_NAME="seas-financial-tracker"
DOCKER_COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    error "Invalid environment. Use 'staging' or 'production'"
fi

log "Starting deployment to ${ENVIRONMENT} environment..."

# Check prerequisites
log "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || error "Docker is required but not installed"
command -v docker-compose >/dev/null 2>&1 || error "Docker Compose is required but not installed"

# Check if docker-compose file exists
if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
    error "Docker Compose file $DOCKER_COMPOSE_FILE not found"
fi

# Create necessary directories
log "Creating necessary directories..."
mkdir -p data logs backups nginx/ssl monitoring/grafana/dashboards monitoring/grafana/datasources

# Set up SSL certificates (self-signed for staging, proper for production)
if [[ "$ENVIRONMENT" == "staging" ]]; then
    if [[ ! -f "nginx/ssl/cert.pem" ]] || [[ ! -f "nginx/ssl/key.pem" ]]; then
        log "Generating self-signed SSL certificates for staging..."
        mkdir -p nginx/ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    fi
else
    log "Production environment detected. Please ensure SSL certificates are in nginx/ssl/"
    if [[ ! -f "nginx/ssl/cert.pem" ]] || [[ ! -f "nginx/ssl/key.pem" ]]; then
        warning "SSL certificates not found. Please add them to nginx/ssl/ before continuing."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Deployment cancelled"
        fi
    fi
fi

# Stop existing containers
log "Stopping existing containers..."
docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans || true

# Clean up old images
log "Cleaning up old images..."
docker system prune -f

# Pull latest images
log "Pulling latest images..."
docker-compose -f "$DOCKER_COMPOSE_FILE" pull

# Start services
log "Starting services..."
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

# Wait for services to be ready
log "Waiting for services to be ready..."
sleep 30

# Health check
log "Performing health check..."
if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
    success "Application is healthy"
else
    error "Application health check failed"
fi

# Check container status
log "Checking container status..."
docker-compose -f "$DOCKER_COMPOSE_FILE" ps

# Show logs
log "Recent application logs:"
docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20 seas-financial-tracker

success "Deployment to ${ENVIRONMENT} completed successfully!"
log "Application is available at:"
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "  - HTTPS: https://your-domain.com"
    echo "  - Monitoring: http://localhost:3000 (Grafana)"
    echo "  - Metrics: http://localhost:9090 (Prometheus)"
else
    echo "  - HTTP: http://localhost:8501"
    echo "  - HTTPS: https://localhost (if SSL configured)"
fi

log "To view logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
log "To stop services: docker-compose -f $DOCKER_COMPOSE_FILE down"
