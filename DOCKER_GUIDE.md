# Docker Deployment Guide - Available Now Bot

This guide explains how to deploy the Available Now Bot using Docker.

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Install Docker Compose](https://docs.docker.com/compose/install/))
- Bot token from @BotFather
- Your Telegram user ID
- Target group ID

## Quick Start (5 minutes)

### Step 1: Prepare Environment File

```bash
cd /path/to/teagram
cp .env.example .env
```

Edit `.env` with your values:

```env
TELEGRAM_BOT_TOKEN=your_token_here
TARGET_GROUP_ID=-123456789
APPROVED_ADMINS=987654321
```

### Step 2: Build and Run with Docker Compose

```bash
# Build the Docker image
docker-compose build

# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f teagram-bot
```

### Step 3: Verify Bot is Running

```bash
# Check container status
docker-compose ps

# View recent logs
docker-compose logs teagram-bot --tail 20
```

### Step 4: Stop the Bot

```bash
docker-compose down
```

## Docker Commands Reference

### Build Image

```bash
# Build with docker-compose (recommended)
docker-compose build

# Or build manually
docker build -t teagram-bot:latest .
```

### Run Container

#### Using Docker Compose (Recommended)

```bash
# Start in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Stop container
docker-compose down

# View logs
docker-compose logs -f

# Restart container
docker-compose restart
```

#### Using Docker Directly

```bash
# Run container
docker run -d \
  --name teagram-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TARGET_GROUP_ID=-123456789 \
  -e APPROVED_ADMINS=987654321 \
  teagram-bot:latest

# View logs
docker logs -f teagram-bot

# Stop container
docker stop teagram-bot

# Remove container
docker rm teagram-bot
```

### Container Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs teagram-bot

# Follow logs in real-time
docker logs -f teagram-bot

# Execute command in container
docker exec -it teagram-bot bash

# Restart container
docker restart teagram-bot

# Stop container
docker stop teagram-bot

# Remove container
docker rm teagram-bot

# View container stats
docker stats teagram-bot
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi teagram-bot:latest

# Tag image
docker tag teagram-bot:latest teagram-bot:v1.0

# Push to registry
docker push your-registry/teagram-bot:latest
```

## Docker Compose Configuration

The `docker-compose.yml` file includes:

- **Service Definition**: Configures the bot container
- **Environment Variables**: Loads from `.env` file
- **Restart Policy**: `unless-stopped` - restarts on failure
- **Volume Mounts**: Stores logs in `./logs` directory
- **Logging**: JSON file driver with rotation
- **Network**: Isolated network for the bot

### Customizing docker-compose.yml

#### Add Port Mapping (if needed)

```yaml
services:
  teagram-bot:
    ports:
      - "8080:8080"
```

#### Add Memory Limits

```yaml
services:
  teagram-bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

#### Add Database Service

```yaml
services:
  teagram-bot:
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: teagram
      POSTGRES_USER: teagram
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Dockerfile Explanation

The Dockerfile includes:

1. **Base Image**: `python:3.11-slim` - Lightweight Python image
2. **Working Directory**: `/app` - Container working directory
3. **Environment Variables**: Optimized Python settings
4. **System Dependencies**: curl for health checks
5. **Python Dependencies**: Installed from requirements.txt
6. **Bot Code**: Copied into container
7. **Non-root User**: Security best practice
8. **Health Check**: Monitors container health
9. **Default Command**: Runs the bot

## Deployment Scenarios

### Scenario 1: Local Development

```bash
# Clone repository
git clone https://github.com/your-username/teagram.git
cd teagram

# Setup environment
cp .env.example .env
# Edit .env with your values

# Run with docker-compose
docker-compose up

# Bot will restart automatically on code changes (with volume mounts)
```

### Scenario 2: Production Server

```bash
# SSH into server
ssh user@your-server.com

# Clone repository
git clone https://github.com/your-username/teagram.git
cd teagram

# Setup environment
cp .env.example .env
# Edit .env with production values

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Setup auto-restart on server reboot
docker-compose up -d --restart unless-stopped
```

### Scenario 3: Docker Hub Deployment

```bash
# Build image
docker build -t your-username/teagram-bot:latest .

# Push to Docker Hub
docker login
docker push your-username/teagram-bot:latest

# On another machine, pull and run
docker run -d \
  --name teagram-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TARGET_GROUP_ID=-123456789 \
  -e APPROVED_ADMINS=987654321 \
  your-username/teagram-bot:latest
```

### Scenario 4: Multiple Instances

```yaml
version: '3.8'

services:
  teagram-bot-1:
    build: .
    container_name: teagram-bot-1
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${BOT_TOKEN_1}
      - TARGET_GROUP_ID=${GROUP_ID_1}
      - APPROVED_ADMINS=${ADMINS_1}

  teagram-bot-2:
    build: .
    container_name: teagram-bot-2
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${BOT_TOKEN_2}
      - TARGET_GROUP_ID=${GROUP_ID_2}
      - APPROVED_ADMINS=${ADMINS_2}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs teagram-bot

# Common issues:
# 1. Missing .env file - create it
# 2. Invalid token - check TELEGRAM_BOT_TOKEN
# 3. Missing dependencies - rebuild image
```

### Bot Not Responding

```bash
# Check if container is running
docker-compose ps

# Check logs for errors
docker-compose logs -f teagram-bot

# Restart container
docker-compose restart teagram-bot
```

### High Memory Usage

```bash
# Check container stats
docker stats teagram-bot

# Limit memory in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
```

### Permission Denied Errors

```bash
# Run with sudo
sudo docker-compose up -d

# Or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## Monitoring and Logging

### View Logs

```bash
# Last 50 lines
docker-compose logs --tail 50 teagram-bot

# Follow logs in real-time
docker-compose logs -f teagram-bot

# View logs from specific time
docker-compose logs --since 2025-11-04T10:00:00 teagram-bot
```

### Container Stats

```bash
# Real-time stats
docker stats teagram-bot

# One-time stats
docker stats --no-stream teagram-bot
```

### Health Checks

```bash
# Check container health
docker inspect teagram-bot --format='{{.State.Health.Status}}'

# View health check history
docker inspect teagram-bot --format='{{json .State.Health}}'
```

## Security Best Practices

1. **Use Secrets Management**
   ```bash
   # Use Docker secrets for sensitive data
   echo "your_token" | docker secret create bot_token -
   ```

2. **Non-root User**
   - Dockerfile already uses non-root user (botuser)

3. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

4. **Network Isolation**
   - docker-compose.yml uses isolated network

5. **Regular Updates**
   ```bash
   # Update base image
   docker pull python:3.11-slim
   docker-compose build --no-cache
   ```

## Advanced Configuration

### Using Environment File

```bash
# Create .env.production
TELEGRAM_BOT_TOKEN=prod_token
TARGET_GROUP_ID=-123456789
APPROVED_ADMINS=987654321

# Use specific env file
docker-compose --env-file .env.production up -d
```

### Custom Logging

```yaml
services:
  teagram-bot:
    logging:
      driver: "splunk"
      options:
        splunk-token: "${SPLUNK_TOKEN}"
        splunk-url: "https://your-splunk-instance.com"
```

### Health Checks

The Dockerfile includes a health check. Customize it:

```dockerfile
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1
```

## Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] `.env` file created with correct values
- [ ] `.dockerignore` file present
- [ ] Dockerfile present
- [ ] docker-compose.yml present
- [ ] Bot token is valid
- [ ] Group ID is correct
- [ ] User ID is correct
- [ ] Image builds successfully: `docker-compose build`
- [ ] Container starts: `docker-compose up -d`
- [ ] Bot responds to commands
- [ ] Logs show no errors: `docker-compose logs`

## Getting Help

- Check logs: `docker-compose logs -f`
- Review Dockerfile: `cat Dockerfile`
- Check docker-compose.yml: `cat docker-compose.yml`
- Test locally first before deploying to production
- Refer to START_HERE.md for bot usage

## Next Steps

1. **Test locally** with Docker Compose
2. **Deploy to production server** using Docker
3. **Set up monitoring** with container stats
4. **Configure backups** if using database
5. **Document your setup** for team members

## Useful Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Execute command
docker-compose exec teagram-bot bash

# Remove everything (including volumes)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# View service status
docker-compose ps

# View configuration
docker-compose config
```

---

Your bot is now ready for Docker deployment! Follow the Quick Start section to get running in minutes.
