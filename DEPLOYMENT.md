# Deployment Guide - Available Now Bot

This guide covers deploying the Available Now bot to various hosting platforms.

## Prerequisites

- Python 3.8+
- Git
- A Telegram bot token from @BotFather
- Target group ID
- Approved admin IDs

## Option 1: Local Machine (Development)

### Requirements
- Python 3.8+
- pip

### Steps

```bash
# Clone repository
git clone <repository_url>
cd available_now_bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python bot.py
```

**Note**: The bot will stop when you close the terminal. For continuous operation, use one of the other deployment options.

## Option 2: Linux VPS/Cloud Server (Recommended)

### Requirements
- Ubuntu 20.04+ or similar Linux distribution
- SSH access
- sudo privileges

### Steps

#### 1. Connect to Server
```bash
ssh user@your_server_ip
```

#### 2. Install Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

#### 3. Clone and Setup
```bash
cd /home/ubuntu
git clone <repository_url>
cd available_now_bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your credentials
nano .env
```

#### 4. Create Systemd Service

```bash
sudo nano /etc/systemd/system/available-now-bot.service
```

Add the following content:

```ini
[Unit]
Description=Available Now Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/available_now_bot
Environment="PATH=/home/ubuntu/available_now_bot/venv/bin"
ExecStart=/home/ubuntu/available_now_bot/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 5. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable available-now-bot
sudo systemctl start available-now-bot
sudo systemctl status available-now-bot
```

#### 6. Monitor Logs

```bash
# View logs
sudo journalctl -u available-now-bot -f

# View last 50 lines
sudo journalctl -u available-now-bot -n 50
```

#### 7. Update Bot

```bash
cd /home/ubuntu/available_now_bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart available-now-bot
```

## Option 3: Docker

### Requirements
- Docker
- Docker Compose (optional)

### Steps

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Run bot
CMD ["python", "bot.py"]
```

#### 2. Create .dockerignore

```
venv
.env
.git
__pycache__
*.pyc
.DS_Store
```

#### 3. Build Image

```bash
docker build -t available-now-bot:latest .
```

#### 4. Run Container

```bash
docker run --name available-now-bot \
  --env-file .env \
  --restart always \
  available-now-bot:latest
```

#### 5. Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: available-now-bot
    env_file: .env
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Run with:
```bash
docker-compose up -d
docker-compose logs -f
```

## Option 4: Heroku (Free Tier Deprecated)

Heroku's free tier is no longer available, but you can deploy to paid dynos.

### Steps

1. Install Heroku CLI
2. Create Procfile:
   ```
   worker: python bot.py
   ```
3. Deploy:
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set TARGET_GROUP_ID=your_group_id
   heroku config:set APPROVED_ADMINS=your_ids
   git push heroku main
   heroku ps:scale worker=1
   heroku logs --tail
   ```

## Option 5: AWS EC2

### Requirements
- AWS Account
- EC2 instance (t2.micro or larger)
- Security group allowing SSH

### Steps

1. Launch EC2 instance (Ubuntu 20.04)
2. Connect via SSH
3. Follow "Linux VPS" steps above
4. Optionally: Use AWS Systems Manager Session Manager instead of SSH

## Option 6: DigitalOcean App Platform

### Steps

1. Create GitHub repository with your code
2. Connect DigitalOcean to GitHub
3. Create new App
4. Select Python as runtime
5. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TARGET_GROUP_ID`
   - `APPROVED_ADMINS`
6. Deploy

## Option 7: Railway

### Steps

1. Push code to GitHub
2. Go to railway.app
3. Create new project
4. Connect GitHub repository
5. Add environment variables
6. Deploy

## Monitoring and Maintenance

### Health Checks

Create a simple health check script:

```bash
#!/bin/bash
# check_bot.sh

if ! pgrep -f "python bot.py" > /dev/null; then
    echo "Bot is not running!"
    systemctl restart available-now-bot
fi
```

Add to crontab:
```bash
crontab -e
# Add: */5 * * * * /home/ubuntu/available_now_bot/check_bot.sh
```

### Log Rotation

Create `/etc/logrotate.d/available-now-bot`:

```
/var/log/available-now-bot/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
}
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/available-now-bot"
mkdir -p $BACKUP_DIR

# Backup .env and profiles
tar -czf $BACKUP_DIR/backup-$(date +%Y%m%d).tar.gz \
    /home/ubuntu/available_now_bot/.env \
    /home/ubuntu/available_now_bot/profiles.db

# Keep only last 30 days
find $BACKUP_DIR -name "backup-*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /home/ubuntu/available_now_bot/backup.sh
```

## Troubleshooting

### Bot stops running
1. Check logs: `sudo journalctl -u available-now-bot -n 100`
2. Verify token is correct
3. Check internet connection
4. Restart service: `sudo systemctl restart available-now-bot`

### High memory usage
1. Check for memory leaks in logs
2. Restart bot regularly
3. Consider upgrading server resources
4. Profile code with memory_profiler

### Slow responses
1. Check bot.py for blocking operations
2. Use async/await properly
3. Consider using webhook instead of polling
4. Upgrade server resources

### Telegram API errors
1. Check rate limits
2. Verify bot permissions in group
3. Check for API changes in Telegram Bot API docs
4. Review error logs carefully

## Webhook Setup (Advanced)

For better performance, use webhooks instead of polling:

```python
# In bot.py, replace application.run_polling() with:

from telegram.ext import Application

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers...
    
    # Start webhook
    await application.bot.set_webhook(url="https://your-domain.com/webhook")
    
    # Run with webhook
    await application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="/webhook",
        webhook_url="https://your-domain.com/webhook"
    )

if __name__ == '__main__':
    asyncio.run(main())
```

## Production Checklist

- [ ] Environment variables configured securely
- [ ] Bot token stored in environment, not in code
- [ ] Logging configured and monitored
- [ ] Backup strategy in place
- [ ] Error handling and recovery configured
- [ ] Rate limiting implemented
- [ ] Database backups automated (when using DB)
- [ ] Monitoring and alerting set up
- [ ] Documentation updated
- [ ] Security audit completed
- [ ] Load testing performed
- [ ] Disaster recovery plan documented

## Support

For deployment issues, check:
1. Bot logs
2. Telegram Bot API documentation
3. Platform-specific documentation
4. GitHub issues
