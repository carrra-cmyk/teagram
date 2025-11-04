# Quick Start Guide - Available Now Telegram Bot

## 5-Minute Setup

### Step 1: Create Your Bot (2 minutes)
1. Open Telegram and message `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "Available Now Bot")
4. Choose a username (e.g., "available_now_bot")
5. **Copy the API token** - you'll need this!

### Step 2: Get Your IDs (2 minutes)
1. Add your bot to your Telegram group
2. Send a test message in the group
3. Open this URL in your browser (replace `YOUR_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
4. Find your **group ID** (negative number in `chat.id`)
5. Find your **user ID** (positive number in `from.id`)

### Step 3: Configure and Run (1 minute)
```bash
# Clone the project
git clone <repo_url>
cd available_now_bot

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your TOKEN, GROUP_ID, and USER_ID

# Run
python bot.py
```

Done! Your bot is now running.

## First Steps

### As an Admin:
1. Open Telegram and find your bot
2. Send `/start`
3. Click "📝 Create Profile"
4. Fill out your profile following the prompts
5. Upload images and videos
6. Confirm and save

### To Go Live:
1. Send `/available` to your bot
2. Choose duration (2, 4, or 6 hours)
3. Your profile appears in the group!

### For Group Members:
1. Send `/available` in the group
2. See all available models
3. Click a name to view their full profile

## Common Commands

| Command | Where | What It Does |
|---------|-------|--------------|
| `/start` | Private chat | Show main menu |
| `/createprofile` | Private chat | Create new profile |
| `/available` | Private chat | Mark yourself available |
| `/editprofile` | Private chat | Update your profile |
| `/deleteprofile` | Private chat | Delete your profile |
| `/available` | Group chat | View available models |

## Troubleshooting

**Bot doesn't respond?**
- Check that `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Restart the bot: `Ctrl+C` then `python bot.py`

**Listings don't appear in group?**
- Make sure bot is added to the group
- Check that `TARGET_GROUP_ID` is correct (should start with `-`)
- Verify bot has permission to send messages

**Profile creation fails?**
- Make sure your user ID is in `APPROVED_ADMINS` in `.env`
- Fill all required fields

## Next Steps

- Read `README.md` for detailed documentation
- Customize bot behavior by editing `bot.py`
- Deploy to a server for 24/7 operation
- Add database integration for persistence

## Need Help?

Check the README.md file for detailed documentation and advanced setup options.
