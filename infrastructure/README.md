# Infrastructure

Deployment and infrastructure configuration files.

## Directory Structure

### `/docker`
- `Dockerfile.backend` - Backend container image
- `Dockerfile.frontend` - Frontend container image
- `docker-compose.yml` - Local development setup
- `docker-compose.prod.yml` - Production configuration

### `/nginx`
- `nginx.conf` - Reverse proxy configuration
- `ssl/` - SSL certificate storage

### `/scripts`
Deployment and maintenance scripts:
- `deploy.sh` - Production deployment script
- `backup.sh` - Database backup automation
- `setup.sh` - Initial server setup
- `migrate.sh` - Run database migrations
