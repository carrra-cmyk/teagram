# Render Deployment Guide - Available Now Bot

This guide explains how to deploy the Available Now Bot on Render.com.

## What is Render?

Render is a modern cloud platform that makes it easy to deploy applications. It offers:
- Free tier for testing
- Automatic deployments from GitHub
- Built-in Docker support
- Environment variable management
- 24/7 uptime

## Prerequisites

1. GitHub account with your teagram repository
2. Render.com account (free)
3. Bot token from @BotFather
4. Your Telegram user ID
5. Target group ID

## Step-by-Step Deployment

### Step 1: Create Render Account

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your GitHub account

### Step 2: Connect GitHub Repository

1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Click "Connect a repository"
4. Search for "teagram"
5. Click "Connect" next to your repository

### Step 3: Configure Web Service

Fill in the following details:

| Field | Value |
|-------|-------|
| **Name** | `teagram-bot` |
| **Environment** | `Docker` |
| **Region** | Choose closest to you (e.g., `Oregon` for US) |
| **Branch** | `main` |
| **Build Command** | (leave empty - Dockerfile handles it) |
| **Start Command** | `python bot.py` |

### Step 4: Add Environment Variables

1. Scroll down to "Environment"
2. Click "Add Environment Variable"
3. Add these variables:

```
TELEGRAM_BOT_TOKEN = 8541560958:AAHSghhi_dGkoiRGxqg_1JZc23EBYuwo69E
TARGET_GROUP_ID = -4844846245
APPROVED_ADMINS = 1328927348
```

**Important**: Replace with your actual values!

### Step 5: Configure Plan

1. Scroll to "Plan"
2. Select "Free" (or "Starter" if you want more reliability)
3. Click "Create Web Service"

Render will now:
- Build your Docker image
- Deploy the container
- Start the bot

This takes about 2-3 minutes.

### Step 6: Monitor Deployment

1. Watch the "Logs" tab for deployment progress
2. You should see: "Polling started" when the bot is running
3. If there are errors, check the logs for details

## Start Commands for Render

### Command 1: Run Default Bot
```
python bot.py
```
- Uses the original bot implementation
- Simpler, straightforward
- Good for testing

### Command 2: Run Enhanced Bot
```
python bot_enhanced.py
```
- Better code organization
- Improved error handling
- Recommended for production

### Command 3: Run with Logging
```
python -u bot.py
```
- `-u` flag: Unbuffered output
- Logs appear immediately in Render
- Useful for debugging

### Command 4: Run with Custom Log File
```
python bot.py >> /tmp/bot.log 2>&1 && tail -f /tmp/bot.log
```
- Logs to file and displays
- Useful for monitoring

## Render Configuration File

Create a `render.yaml` file in your repository root for automatic configuration:

```yaml
services:
  - type: web
    name: teagram-bot
    env: docker
    region: oregon
    plan: free
    healthCheckPath: /health
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TARGET_GROUP_ID
        sync: false
      - key: APPROVED_ADMINS
        sync: false
```

Then push to GitHub and Render will use this configuration.

## Deployment Methods

### Method 1: Manual Deployment (Easiest)

1. Go to https://render.com/dashboard
2. Click "New +"
3. Select "Web Service"
4. Connect your GitHub repository
5. Fill in the form (see Step 3 above)
6. Click "Create Web Service"

### Method 2: Using render.yaml (Recommended)

1. Create `render.yaml` in repository root
2. Push to GitHub
3. Go to https://render.com/dashboard
4. Click "New +"
5. Select "Web Service"
6. Select your repository
7. Render auto-fills from `render.yaml`
8. Click "Create Web Service"

### Method 3: Infrastructure as Code

Use Render's API to deploy programmatically:

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy --service teagram-bot
```

## Testing Your Deployment

### Check Bot Status

1. Go to Render dashboard
2. Click on your service "teagram-bot"
3. Check the "Logs" tab
4. You should see "Polling started"

### Test in Telegram

1. Open Telegram
2. Find your bot
3. Send `/start`
4. Create a test profile
5. Send `/available`
6. Check your group for the listing

## Monitoring and Logs

### View Logs in Render

1. Go to your service dashboard
2. Click "Logs" tab
3. See real-time bot output

### Common Log Messages

```
# Bot starting
2025-11-04 10:30:45,123 - telegram.ext._application - INFO - Application started
2025-11-04 10:30:45,456 - telegram.ext._application - INFO - Polling started

# Profile created
2025-11-04 10:35:20,789 - __main__ - INFO - Profile saved for user 1328927348

# Listing posted
2025-11-04 10:40:10,234 - __main__ - INFO - Listing created for user 1328927348
```

### Troubleshooting Logs

```
# Bot not responding
ERROR - Could not read from remote repository

# Token invalid
ERROR - Unauthorized

# Group not found
ERROR - Bad Request: chat not found
```

## Environment Variables on Render

### Setting Variables

1. Go to service dashboard
2. Click "Environment"
3. Click "Add Environment Variable"
4. Enter key and value
5. Click "Save"

### Updating Variables

1. Click on existing variable
2. Edit the value
3. Click "Save"
4. Service automatically redeploys

### Sensitive Variables

Use Render's secret management:

1. Create `.env` file locally (never commit)
2. Add to `.gitignore`
3. Set variables in Render dashboard
4. Render injects at runtime

## Deployment Checklist

- [ ] Render account created
- [ ] GitHub account connected
- [ ] Repository pushed to GitHub
- [ ] Dockerfile present in repository
- [ ] requirements.txt present
- [ ] .env.example present
- [ ] Environment variables set in Render
- [ ] Start command set to `python bot.py`
- [ ] Service deployed successfully
- [ ] Logs show "Polling started"
- [ ] Bot responds to `/start` in Telegram
- [ ] Profile creation works
- [ ] Listings appear in group

## Pricing

| Plan | Cost | Features |
|------|------|----------|
| **Free** | $0/month | 0.5 CPU, 512MB RAM, auto-sleep after 15 min inactivity |
| **Starter** | $7/month | 0.5 CPU, 512MB RAM, always running |
| **Standard** | $25/month | 1 CPU, 2GB RAM, always running |
| **Pro** | $100+/month | 4 CPU, 8GB RAM, always running |

**For a Telegram bot, Free or Starter plan is sufficient.**

## Keeping Bot Running 24/7

### Option 1: Use Starter Plan
- Costs $7/month
- Bot runs continuously
- No auto-sleep

### Option 2: Use Cron Job to Keep Alive
- Free plan auto-sleeps after 15 minutes of inactivity
- Use external cron service to ping bot periodically
- Services: EasyCron, cron-job.org (free)

### Option 3: Use Render's Background Workers
- Deploy as background worker
- Runs continuously on free plan
- Better for long-running tasks

## Advanced Configuration

### Custom Domain

1. Go to service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records
5. Render provides SSL certificate automatically

### Auto-Deploy from GitHub

1. Go to service settings
2. "Auto-Deploy" is enabled by default
3. Every push to main branch triggers deployment
4. Deployment takes 2-3 minutes

### Manual Redeploy

1. Go to service dashboard
2. Click "Manual Deploy"
3. Select branch (main)
4. Click "Deploy"

## Updating Your Bot

### To Update Code

1. Make changes locally
2. Commit and push to GitHub
3. Render automatically deploys
4. Check logs to verify

### To Update Environment Variables

1. Go to Render dashboard
2. Click on service
3. Click "Environment"
4. Update variable values
5. Service redeploys automatically

### To Switch Bot Version

1. Change start command to `python bot_enhanced.py`
2. Click "Save"
3. Service redeploys

## Troubleshooting

### Bot Not Starting

**Problem**: Service shows "Build failed"

**Solution**:
1. Check logs for error messages
2. Verify Dockerfile exists
3. Verify requirements.txt is correct
4. Verify Python version compatibility
5. Try rebuilding: Click "Manual Deploy"

### Bot Not Responding

**Problem**: Bot doesn't reply to commands

**Solution**:
1. Check logs for "Polling started"
2. Verify TELEGRAM_BOT_TOKEN is correct
3. Verify bot is added to group
4. Try redeploying: Click "Manual Deploy"

### Service Keeps Crashing

**Problem**: Service shows "Crashed"

**Solution**:
1. Check logs for error messages
2. Verify environment variables are set
3. Check for infinite loops in code
4. Increase memory: Upgrade plan
5. Check resource usage

### Environment Variables Not Working

**Problem**: Bot says token is invalid

**Solution**:
1. Verify variables are set in Render dashboard
2. Check variable names are exact
3. Verify values don't have extra spaces
4. Redeploy service
5. Check logs for variable values

## Performance Tips

1. **Use Starter Plan** for 24/7 uptime
2. **Monitor Logs** for errors and performance issues
3. **Set Resource Limits** if needed
4. **Use Enhanced Bot** for better performance
5. **Add Database** for better scalability (see DATABASE_SCHEMA.md)

## Security Best Practices

1. **Never commit .env file** - use .gitignore
2. **Use Render's secret management** for sensitive data
3. **Keep bot token secret** - never share
4. **Use HTTPS** for custom domains
5. **Monitor logs** for suspicious activity
6. **Rotate token** if compromised

## Scaling Your Bot

### When to Scale

- Multiple groups using the bot
- Thousands of profiles
- High message volume
- Need database persistence

### How to Scale

1. **Add Database**: See DATABASE_SCHEMA.md
2. **Upgrade Plan**: Get more CPU/RAM
3. **Use Background Workers**: For heavy tasks
4. **Implement Caching**: Reduce database queries
5. **Monitor Performance**: Use Render's metrics

## Render vs Other Platforms

| Platform | Free | Docker | Ease | Cost |
|----------|------|--------|------|------|
| **Render** | Yes | Yes | Easy | $7+/mo |
| **Heroku** | No | Yes | Easy | $7+/mo |
| **Railway** | Yes | Yes | Easy | $5+/mo |
| **Replit** | Yes | No | Very Easy | Free |
| **AWS** | Limited | Yes | Hard | Variable |

## Getting Help

- **Render Docs**: https://render.com/docs
- **Render Support**: https://render.com/support
- **Bot Issues**: Check START_HERE.md
- **Docker Issues**: Check DOCKER_GUIDE.md

## Quick Reference

| Task | Command/Action |
|------|-----------------|
| **Deploy** | Push to GitHub, Render auto-deploys |
| **View Logs** | Go to service → Logs tab |
| **Update Env Vars** | Service → Environment → Edit |
| **Redeploy** | Service → Manual Deploy |
| **Check Status** | Service dashboard |
| **Stop Service** | Service → Settings → Delete |

## Next Steps

1. Create Render account at https://render.com
2. Connect GitHub repository
3. Create Web Service with settings above
4. Set environment variables
5. Deploy and test
6. Monitor logs
7. Enjoy your 24/7 bot!

---

Your bot is now ready for Render deployment! Follow the Step-by-Step Deployment section to get started.

**Start Command for Render**: `python bot.py`
