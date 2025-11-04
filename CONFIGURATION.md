# Configuration Guide - Available Now Bot

This guide explains how to customize the Available Now bot for your specific needs.

## Environment Variables

### Required Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
- Get from @BotFather on Telegram
- Keep this secret! Never commit to version control

```env
TARGET_GROUP_ID=-123456789
```
- The group where listings will be posted
- Must be negative for groups (e.g., -123456789)
- Positive for channels

```env
APPROVED_ADMINS=123456789,987654321
```
- Comma-separated list of Telegram user IDs
- Only these users can create profiles
- Leave empty to allow all users (not recommended)

### Optional Variables

```env
LOG_LEVEL=INFO
```
- Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Default: INFO

```env
DATABASE_URL=postgresql://user:password@localhost/bot_db
```
- For future database integration
- Not used in current version

## Customization Options

### 1. Modify Messages

Edit the message strings in `bot.py`:

```python
# Example: Change welcome message
await update.message.reply_text(
    "👋 Welcome to Available Now Bot!\n\n"
    "What would you like to do?"
)
```

### 2. Change Availability Durations

In `availability_duration()` function:

```python
keyboard = [
    [InlineKeyboardButton("1 hour", callback_data='duration_1')],
    [InlineKeyboardButton("3 hours", callback_data='duration_3')],
    [InlineKeyboardButton("8 hours", callback_data='duration_8')],
]
```

### 3. Modify Profile Fields

Add new fields to the profile creation flow:

```python
# In profile_disclaimer() function
async def profile_disclaimer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle disclaimer input."""
    context.user_data['profile']['disclaimer'] = update.message.text
    
    # Add new field
    await update.message.reply_text(
        "Add your availability schedule (e.g., 'Available Mon-Fri 6PM-2AM'):"
    )
    return PROFILE_SCHEDULE  # New state

# Add new state to conversation handler
PROFILE_SCHEDULE = 19  # Add to state definitions
```

### 4. Change Profile Display Format

Edit `format_group_listing()` function:

```python
def format_group_listing(profile: Dict[str, Any], expires_at: datetime) -> str:
    """Format a profile for display in the group chat."""
    # Customize the layout and formatting here
    text = f"💋 <b>{profile.get('name', 'N/A')}</b> 💋\n"
    # ... rest of formatting
    return text
```

### 5. Add Emoji Customization

```python
# In format_group_listing()
EMOJIS = {
    'in_person': '🧍',
    'facetime': '📱',
    'custom': '🎥',
    'other': '❓',
    'phone': '📞',
    'email': '📧',
    'telegram': '💬',
}

text += f"{EMOJIS['in_person']} In-Person services\n"
```

### 6. Customize Admin Verification

```python
# Add role-based access control
def is_approved_admin(user_id: int, role: str = 'admin') -> bool:
    """Check if user has required role."""
    admin_roles = {
        'admin': [123456789, 987654321],
        'moderator': [111111111, 222222222],
        'viewer': []  # Everyone
    }
    return user_id in admin_roles.get(role, [])
```

### 7. Add Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]
        
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        return False

# Usage
rate_limiter = RateLimiter(max_requests=5, time_window=60)

async def available_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not rate_limiter.is_allowed(update.effective_user.id):
        await update.message.reply_text(
            "⏱️ You're using this command too frequently. Please wait a moment."
        )
        return
    # ... rest of function
```

### 8. Add Database Support

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./bot.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use in handlers
async def profile_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    db = next(get_db())
    # Save to database
    db.add(profile)
    db.commit()
```

### 9. Add Webhook Support

```python
from telegram.ext import Application
import asyncio

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers...
    
    # Setup webhook
    webhook_url = "https://your-domain.com/webhook"
    await application.bot.set_webhook(url=webhook_url)
    
    # Run with webhook
    await application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="/webhook",
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    asyncio.run(main())
```

### 10. Add Logging to File

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure file logging
file_handler = RotatingFileHandler(
    'bot.log',
    maxBytes=1024*1024,  # 1MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)
```

## Advanced Features

### 1. Profile Verification

```python
async def verify_profile(profile: Dict[str, Any]) -> bool:
    """Verify profile has all required fields."""
    required_fields = ['name', 'about', 'contact_method', 'offer_types']
    return all(field in profile for field in required_fields)
```

### 2. Auto-Renewal

```python
async def auto_renew_listing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically renew listing when it expires."""
    user_id = update.effective_user.id
    profile = db.get_profile(user_id)
    
    if profile and user_id in context.user_data.get('auto_renew', []):
        # Automatically mark available again
        await mark_available(update, context)
```

### 3. Profile Analytics

```python
class ProfileAnalytics:
    def __init__(self):
        self.views = defaultdict(int)
        self.contacts = defaultdict(int)
    
    def track_view(self, profile_id: int):
        self.views[profile_id] += 1
    
    def track_contact(self, profile_id: int):
        self.contacts[profile_id] += 1
    
    def get_stats(self, profile_id: int) -> Dict:
        return {
            'views': self.views[profile_id],
            'contacts': self.contacts[profile_id]
        }

analytics = ProfileAnalytics()
```

### 4. Multi-Language Support

```python
MESSAGES = {
    'en': {
        'welcome': '👋 Welcome to Available Now Bot!',
        'create_profile': '📝 Create Profile',
    },
    'es': {
        'welcome': '👋 ¡Bienvenido al Bot Available Now!',
        'create_profile': '📝 Crear Perfil',
    }
}

def get_message(key: str, language: str = 'en') -> str:
    return MESSAGES.get(language, MESSAGES['en']).get(key, '')
```

### 5. Payment Integration

```python
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

async def create_payment_intent(profile_id: int, amount: int):
    """Create Stripe payment intent."""
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='usd',
        metadata={'profile_id': profile_id}
    )
    return intent
```

## Performance Tuning

### 1. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_profile_cached(user_id: int):
    return db.get_profile(user_id)
```

### 2. Async Operations

```python
import asyncio

async def batch_process_listings():
    """Process multiple listings concurrently."""
    tasks = [
        process_listing(listing)
        for listing in db.get_active_listings()
    ]
    await asyncio.gather(*tasks)
```

### 3. Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

## Security Hardening

### 1. Input Validation

```python
import re

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

### 2. Rate Limiting

```python
from telegram.error import TelegramError

async def safe_send_message(context, chat_id, text):
    """Send message with error handling."""
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
    except TelegramError as e:
        logger.error(f"Failed to send message: {e}")
```

### 3. Audit Logging

```python
def log_action(user_id: int, action: str, details: Dict = None):
    """Log user actions for audit trail."""
    logger.info(f"User {user_id} performed {action}: {details}")
    # Save to database for compliance
```

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import patch, AsyncMock

class TestBot(unittest.TestCase):
    def test_is_approved_admin(self):
        self.assertTrue(is_approved_admin(123456789))
        self.assertFalse(is_approved_admin(999999999))
    
    def test_validate_email(self):
        self.assertTrue(validate_email('test@example.com'))
        self.assertFalse(validate_email('invalid-email'))
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_profile_creation():
    # Test complete profile creation flow
    pass
```

## Monitoring

### Health Check Endpoint

```python
from aiohttp import web

async def health_check(request):
    return web.json_response({'status': 'healthy'})

app = web.Application()
app.router.add_get('/health', health_check)
```

### Metrics

```python
from prometheus_client import Counter, Histogram

profile_creations = Counter('profile_creations_total', 'Total profiles created')
listing_duration = Histogram('listing_duration_seconds', 'Listing duration')
```

## Troubleshooting Configuration Issues

1. **Bot not responding**: Check TELEGRAM_BOT_TOKEN
2. **Listings not appearing**: Verify TARGET_GROUP_ID and bot permissions
3. **Admin access denied**: Confirm user ID in APPROVED_ADMINS
4. **High memory usage**: Check for memory leaks in custom code
5. **Slow performance**: Enable caching and optimize database queries

For more help, check the main README.md or DEPLOYMENT.md files.
