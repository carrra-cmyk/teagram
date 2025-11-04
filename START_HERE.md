# START HERE - Deploy & Test the Bot Now

This is the fastest way to get your bot running and test it immediately.

## Step 1: Create a Telegram Bot (2 minutes)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name for your bot (e.g., "Available Now Bot")
4. Choose a username (e.g., "available_now_bot_123")
5. **Copy the API Token** - you'll need this immediately

Example token: `123456789:ABCdefGHIjklmnoPQRstuvWXYZ-1234567890`

## Step 2: Create a Test Group (2 minutes)

1. In Telegram, create a new group (or use existing one)
2. Add your bot to the group
3. Send any message in the group
4. Open this URL in your browser (replace `YOUR_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
   Example:
   ```
   https://api.telegram.org/bot123456789:ABCdefGHIjklmnoPQRstuvWXYZ-1234567890/getUpdates
   ```

5. Look for the response and find:
   - **Group ID**: Look for `"chat":{"id":-123456789}` (negative number)
   - **Your User ID**: Look for `"from":{"id":123456789}` (positive number)

**Save these IDs - you'll need them next!**

## Step 3: Configure the Bot (2 minutes)

Navigate to the bot directory and create your configuration:

```bash
cd /home/ubuntu/available_now_bot

# Copy the example configuration
cp .env.example .env

# Edit the configuration file
nano .env
```

Replace the values with your information:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZ-1234567890
TARGET_GROUP_ID=-123456789
APPROVED_ADMINS=123456789
```

**Important**: 
- `TELEGRAM_BOT_TOKEN`: Paste your token from Step 1
- `TARGET_GROUP_ID`: Use the negative group ID from Step 2
- `APPROVED_ADMINS`: Use your user ID from Step 2

Save the file (Press `Ctrl+X`, then `Y`, then `Enter`)

## Step 4: Install Dependencies (1 minute)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Run the Bot (30 seconds)

```bash
# Make sure you're in the project directory
cd /home/ubuntu/available_now_bot

# Make sure virtual environment is activated
source venv/bin/activate

# Run the bot
python bot.py
```

You should see output like:
```
2025-11-04 10:30:45,123 - telegram.ext._application - INFO - Application started
2025-11-04 10:30:45,456 - telegram.ext._application - INFO - Polling started
```

**The bot is now running!** Keep this terminal open.

## Step 6: Test the Bot (5 minutes)

Open a new terminal window (keep the bot running in the first one):

### Test 1: Create a Profile

1. Open Telegram
2. Find your bot (search for its username)
3. Send `/start`
4. Click "📝 Create Profile"
5. Enter your name: `Test Model`
6. Select "🧍 In-Person"
7. Select "🏠🚗 Incall/Outcall"
8. Enter location: `Test Location`
9. Click "✅ Done Selecting"
10. Enter about: `This is a test profile`
11. Select "💬 Telegram"
12. Enter social links: `@testuser`
13. Enter rates: `Test rates`
14. Enter disclaimer: `Test disclaimer`
15. Send "done" for images
16. Send "done" for videos
17. Click "✅ Confirm"

**Result**: You should see "✅ Profile saved successfully!"

### Test 2: Mark Yourself Available

1. In the same chat with the bot, send `/available`
2. Select "2 hours"
3. Go to your test group
4. You should see your profile posted with:
   - Your name in bold
   - Timestamp and countdown
   - All your profile information
   - "Expires in: 2 hours"

**Result**: Your listing appears in the group!

### Test 3: View Available Models (Group Command)

1. In the group chat, send `/available`
2. You should see:
   ```
   📋 Available Now:
   1. Test Model (In-Person)
   ```
3. The list auto-deletes after 5 minutes

**Result**: Group members can see available models!

### Test 4: Delete Profile

1. In the bot chat, send `/start`
2. Click "🗑️ Delete Profile"
3. You should see "✅ Your profile has been deleted."

**Result**: Profile is deleted!

## Troubleshooting

### Bot doesn't respond to /start

**Problem**: Bot doesn't reply to commands

**Solution**:
1. Check that the bot is running (terminal shows "Polling started")
2. Check that you added the bot to the group
3. Verify TELEGRAM_BOT_TOKEN is correct in .env
4. Restart the bot: Press `Ctrl+C` and run `python bot.py` again

### Listings don't appear in group

**Problem**: Profile doesn't post to group

**Solution**:
1. Check that TARGET_GROUP_ID is correct (should be negative)
2. Verify the bot is a member of the group
3. Check that the bot has permission to send messages
4. Look at the bot terminal for error messages

### "You must be an approved admin" error

**Problem**: Bot says you're not approved

**Solution**:
1. Check your user ID is correct in .env
2. Make sure APPROVED_ADMINS has your ID (no spaces after commas)
3. Restart the bot after changing .env

### Bot stops responding

**Problem**: Bot becomes unresponsive

**Solution**:
1. Press `Ctrl+C` in the terminal to stop the bot
2. Run `python bot.py` again to restart
3. Check for error messages in the terminal

## Next Steps

### To Keep Bot Running 24/7

Option 1: Use a VPS (recommended)
- See DEPLOYMENT.md for detailed instructions
- Services: AWS, DigitalOcean, Heroku, Railway

Option 2: Use Docker
- See DEPLOYMENT.md for Docker setup

Option 3: Use systemd service
- See DEPLOYMENT.md for Linux service setup

### To Customize the Bot

See CONFIGURATION.md for:
- Changing messages
- Adding new fields
- Modifying availability durations
- Adding database support
- And much more!

### To Deploy to Production

1. Choose a hosting platform (see DEPLOYMENT.md)
2. Set up environment variables
3. Run the bot on the server
4. Set up monitoring and logging

## Common Commands Reference

| Command | Where | What It Does |
|---------|-------|--------------|
| `/start` | Private chat with bot | Show main menu |
| `/createprofile` | Private chat with bot | Create new profile |
| `/available` | Private chat with bot | Mark yourself available |
| `/available` | Group chat | View available models |
| `/cancel` | During profile creation | Cancel and exit |

## File Locations

- **Bot code**: `/home/ubuntu/available_now_bot/bot.py`
- **Configuration**: `/home/ubuntu/available_now_bot/.env`
- **Documentation**: `/home/ubuntu/available_now_bot/*.md`
- **Dependencies**: `/home/ubuntu/available_now_bot/requirements.txt`

## Getting Help

- **Setup issues**: Check "Troubleshooting" section above
- **Customization**: Read CONFIGURATION.md
- **Deployment**: Read DEPLOYMENT.md
- **Testing**: Read TESTING.md
- **General questions**: Read README.md

## Quick Reference: Full Setup Commands

Copy and paste these commands to set up everything at once:

```bash
# Navigate to project
cd /home/ubuntu/available_now_bot

# Copy configuration
cp .env.example .env

# Edit configuration (you need to manually edit this!)
nano .env
# Replace TELEGRAM_BOT_TOKEN, TARGET_GROUP_ID, APPROVED_ADMINS

# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

## Success Checklist

- [ ] Created bot with @BotFather
- [ ] Got bot token
- [ ] Created test group
- [ ] Got group ID and user ID
- [ ] Edited .env file with your values
- [ ] Installed dependencies
- [ ] Bot is running (see "Polling started")
- [ ] Created test profile
- [ ] Marked yourself available
- [ ] Saw listing in group
- [ ] Group members can see available list
- [ ] Deleted profile successfully

If all checkboxes are checked, your bot is working perfectly! 🎉

## What's Next?

1. **Test with more profiles**: Add another admin and test with multiple profiles
2. **Customize**: Edit CONFIGURATION.md to customize behavior
3. **Deploy**: Follow DEPLOYMENT.md to run bot 24/7
4. **Integrate database**: Follow DATABASE_SCHEMA.md for production setup
5. **Monitor**: Set up logging and monitoring

## Important Notes

- The bot stores profiles in memory - they're lost when the bot restarts
- For production, add database integration (see DATABASE_SCHEMA.md)
- Keep your bot token secret - never share it
- The bot needs to be a member of the group to post listings
- Group ID must be negative (e.g., -123456789)

---

**You're all set! Your bot should be running now.** 🚀

If you encounter any issues, check the Troubleshooting section or read the detailed documentation files.
