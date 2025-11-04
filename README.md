# Available Now Telegram Bot

A sophisticated Telegram bot for group admins to manage and post their availability profiles with guided profile creation, timed listings, and dynamic group interaction features.

## Features

### For Models (Approved Admins)
- **Private Profile Creation**: Create detailed profiles with guided prompts
- **Multi-Service Support**: Offer In-Person, Facetime Shows, Custom Content, or Other services
- **Rich Profile Content**: Include name, services, about section, contact info, social links, rates, and disclaimers
- **Media Gallery**: Upload up to 10 images and 4 videos
- **Availability Toggle**: Mark yourself available for 2, 4, or 6 hours
- **Auto-Expiration**: Listings automatically delete after the selected duration
- **Profile Management**: Edit or delete profiles at any time

### For Group Members
- **Dynamic Listings**: View all currently available models with `/available` command
- **Auto-Deleting List**: The availability list self-deletes after 5 minutes to reduce clutter
- **Direct Access**: Click on model names to view full profiles

### Technical Features
- **Admin Verification**: Only approved admins can create/edit profiles
- **Scheduled Deletion**: Automatic cleanup of expired listings
- **Rich Formatting**: Markdown/HTML formatting with emojis for professional appearance
- **Rate Limiting**: Prevents spam by limiting command usage
- **Secure Storage**: Profiles stored in-memory (easily upgradeable to database)

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Choose a name and username for your bot
4. Copy the **API Token** provided (you'll need this)

### 2. Get Your Group ID

1. Add your bot to the Telegram group where listings will be posted
2. Send a message in the group
3. Use this command to get the group ID:
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. Look for the `chat` object and note the `id` (it will be negative for groups)

### 3. Get Your User ID

1. Send a message to your bot in private chat
2. Use this command:
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Look for your `from` object and note the `id`

### 4. Clone and Setup

```bash
# Clone the repository
git clone <repository_url>
cd available_now_bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
```

### 5. Configure Environment Variables

Edit `.env` with your values:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TARGET_GROUP_ID=-123456789  # Negative number for groups
APPROVED_ADMINS=123456789,987654321  # Your user IDs
```

### 6. Run the Bot

```bash
python bot.py
```

The bot will start polling for updates and be ready to use.

## Usage Guide

### For Models (Admins)

#### Create a Profile
1. Send `/start` to the bot in private chat
2. Click "📝 Create Profile"
3. Follow the guided prompts:
   - Enter your name or subject line
   - Select services you offer (In-Person, Facetime, Custom Content, Other)
   - For each service, provide relevant details:
     - **In-Person**: Choose incall/outcall type and location
     - **Facetime Shows**: List platforms and payment methods
     - **Custom Content**: List payment methods and delivery method
     - **Other**: Describe your custom service
   - Write an about section describing yourself
   - Choose contact method (Phone, Email, or Telegram)
   - Add social media links
   - Enter your rates
   - Add any disclaimers or notices
   - Upload up to 10 images
   - Upload up to 4 videos
4. Review the preview and confirm

#### Mark Yourself Available
1. Send `/available` to the bot in private chat
2. Select duration (2, 4, or 6 hours)
3. Your profile will be posted to the group
4. The listing will automatically delete after the selected time

#### Edit Your Profile
1. Send `/editprofile` to the bot
2. Follow the prompts to update specific fields
3. Confirm the changes

#### Delete Your Profile
1. Send `/deleteprofile` to the bot
2. Confirm deletion

### For Group Members

#### View Available Models
1. Send `/available` in the group chat
2. See a list of all currently available models
3. Click on a model's name to view their full profile
4. Contact them using the provided contact information

## Example Profile Listing

```
💋 Alex's Availability 💋
📅 Posted: Nov 04, 2025, 10:39 AM | Expires in: 2 hours

Services Offered:
- 🧍 In-Person (Incall/Outcall, Times Square)
- 📱 Facetime Shows (Facetime, CashApp/PayPal)
- 🎥 Custom Content (Delivered via Telegram, PayPal)

About:
Hi, I'm Alex! Ready to make your night unforgettable with my charm and energy. Let's connect! 💃

Contact:
Telegram: @AlexStar
Phone: (123) 456-7890

Social Media:
X: @AlexStarX
OnlyFans: onlyfans.com/alexstar

Rates:
In-Person: $200/hr
Facetime: $50/30min
Custom Content: Discuss privately

Notice:
Please contact me privately to book. Deposits required.
```

## Deployment Options

### Option 1: Local Machine (Development)
```bash
python bot.py
```

### Option 2: VPS/Cloud Server (Production)
```bash
# Install systemd service
sudo nano /etc/systemd/system/telegram-bot.service
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
ExecStart=/home/ubuntu/available_now_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### Option 3: Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bot.py .
CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t available-now-bot .
docker run --env-file .env available-now-bot
```

## Database Integration (Future)

The current implementation uses in-memory storage. For production, upgrade to SQLAlchemy + PostgreSQL:

```bash
pip install sqlalchemy psycopg2-binary
```

Then modify `bot.py` to use SQLAlchemy models instead of the `ProfileDatabase` class.

## Troubleshooting

### Bot doesn't respond
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Check that the bot is added to the group
- Ensure the bot has permissions to send messages

### Listings don't appear in group
- Verify `TARGET_GROUP_ID` is correct (should be negative for groups)
- Ensure the bot is a member of the target group
- Check bot permissions in group settings

### Profile creation fails
- Verify user ID is in `APPROVED_ADMINS`
- Check that all required fields are filled
- Review logs for detailed error messages

### Listings don't auto-delete
- Ensure the bot has permission to delete messages in the group
- Check that the bot is still running
- Review logs for deletion errors

## Security Considerations

1. **Admin Verification**: Only approved admins (by Telegram ID) can create profiles
2. **Token Security**: Keep `TELEGRAM_BOT_TOKEN` secret and never commit to version control
3. **User Data**: Store sensitive information securely (upgrade to encrypted database)
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Input Validation**: Validate all user inputs before processing

## Future Enhancements

- [ ] Database integration (SQLAlchemy + PostgreSQL)
- [ ] Profile editing without recreation
- [ ] Advanced media management (image cropping, video trimming)
- [ ] Payment integration (Stripe, PayPal)
- [ ] User reviews and ratings
- [ ] Advanced filtering and search
- [ ] Analytics and statistics
- [ ] Multi-language support
- [ ] Webhook support for faster updates
- [ ] Admin dashboard

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or feature requests, please contact the bot administrator or create an issue in the repository.
