# Testing Guide - Available Now Bot

This guide explains how to test the Available Now bot thoroughly before deployment.

## Prerequisites

- Python 3.8+
- Telegram account with a test group
- Test bot token from @BotFather
- Test user IDs for admin verification

## Setup for Testing

### 1. Create Test Environment

```bash
# Create .env.test file
cp .env.example .env.test

# Edit with test values
nano .env.test
```

Example test configuration:
```env
TELEGRAM_BOT_TOKEN=your_test_bot_token
TARGET_GROUP_ID=-123456789  # Your test group ID
APPROVED_ADMINS=123456789,987654321  # Your test user IDs
```

### 2. Run Bot in Test Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

## Manual Testing Checklist

### Profile Creation Flow

- [ ] Send `/start` - Bot shows main menu
- [ ] Click "📝 Create Profile" - Bot asks for name
- [ ] Enter name - Bot shows service selection menu
- [ ] Select "🧍 In-Person" - Bot asks for incall/outcall type
- [ ] Select "Incall/Outcall" - Bot asks for location
- [ ] Enter location - Bot shows service menu again
- [ ] Select "📱 Facetime Shows" - Bot asks for platforms
- [ ] Enter platforms - Bot asks for payment methods
- [ ] Enter payment methods - Bot shows service menu again
- [ ] Select "🎥 Custom Content" - Bot asks for payment methods
- [ ] Enter payment methods - Bot asks for delivery method
- [ ] Enter delivery method - Bot shows service menu again
- [ ] Select "❓ Other" - Bot asks for custom service description
- [ ] Enter description - Bot shows service menu again
- [ ] Click "✅ Done Selecting" - Bot asks for about section
- [ ] Enter about text - Bot asks for contact method
- [ ] Select "📞 Text/Call" - Bot asks for phone number
- [ ] Enter phone - Bot asks for social media links
- [ ] Enter social links - Bot asks for rates
- [ ] Enter rates - Bot asks for disclaimer
- [ ] Enter disclaimer - Bot asks for images
- [ ] Upload 3 images - Bot confirms each upload
- [ ] Send "done" - Bot asks for videos
- [ ] Upload 2 videos - Bot confirms each upload
- [ ] Send "done" - Bot shows preview
- [ ] Review preview - Bot shows confirm/edit/cancel buttons
- [ ] Click "✅ Confirm" - Bot saves profile and shows success message

### Availability Toggle

- [ ] Send `/available` - Bot asks for duration
- [ ] Select "2 hours" - Bot posts listing to group
- [ ] Verify listing appears in group with correct format
- [ ] Check timestamp and countdown timer
- [ ] Wait 2 hours (or simulate) - Listing should auto-delete
- [ ] Repeat with 4 and 6 hour durations

### Group Member Interaction

- [ ] In group chat, send `/available` - Bot shows list of available models
- [ ] Verify list shows all active listings
- [ ] Check list auto-deletes after 5 minutes
- [ ] Send `/available` again - New list appears

### Admin Verification

- [ ] Test with non-admin user - Bot denies access
- [ ] Test with admin user - Bot allows access
- [ ] Test with empty APPROVED_ADMINS - All users allowed

### Profile Management

- [ ] Create profile as admin
- [ ] Send `/start` again - Main menu appears
- [ ] Click "🗑️ Delete Profile" - Profile deleted
- [ ] Try `/available` - Bot says no profile exists
- [ ] Create new profile - Works correctly

### Error Handling

- [ ] Disconnect internet - Bot handles gracefully
- [ ] Send invalid data - Bot handles gracefully
- [ ] Timeout during profile creation - Bot handles gracefully
- [ ] Send `/cancel` - Conversation ends

## Automated Testing

### Unit Tests

Create `test_bot.py`:

```python
import unittest
from bot import ProfileDatabase, ProfileFormatter

class TestProfileDatabase(unittest.TestCase):
    def setUp(self):
        self.db = ProfileDatabase()
    
    def test_save_and_get_profile(self):
        profile = {'name': 'Test', 'about': 'Test profile'}
        self.db.save_profile(123, profile)
        retrieved = self.db.get_profile(123)
        self.assertEqual(retrieved['name'], 'Test')
    
    def test_delete_profile(self):
        profile = {'name': 'Test'}
        self.db.save_profile(123, profile)
        self.assertTrue(self.db.delete_profile(123))
        self.assertIsNone(self.db.get_profile(123))
    
    def test_create_listing(self):
        self.db.create_listing(123, 2, 456)
        listings = self.db.get_active_listings()
        self.assertEqual(len(listings), 1)

class TestProfileFormatter(unittest.TestCase):
    def test_format_services(self):
        profile = {
            'offer_types': ['in_person'],
            'in_person_type': 'Incall Only',
            'in_person_location': 'Manhattan'
        }
        formatted = ProfileFormatter.format_services(profile)
        self.assertIn('In-Person', formatted)
        self.assertIn('Manhattan', formatted)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python -m unittest test_bot.py
```

### Integration Tests

Create `test_integration.py`:

```python
import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes

class TestBotIntegration(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        self.update.effective_user.id = 123456789
        self.update.effective_user.username = 'testuser'
        self.update.effective_chat.id = -987654321
    
    @patch('bot.db')
    async def test_profile_creation_flow(self, mock_db):
        # Test profile name input
        self.update.message.text = 'Test Model'
        # ... continue testing
        pass

if __name__ == '__main__':
    unittest.main()
```

## Performance Testing

### Load Testing

Test bot with multiple concurrent users:

```python
import asyncio
import time
from telegram import Update

async def simulate_user(user_id, num_messages=10):
    """Simulate a user sending messages."""
    for i in range(num_messages):
        # Simulate user action
        await asyncio.sleep(0.1)

async def load_test(num_users=10):
    """Run load test with multiple users."""
    start_time = time.time()
    
    tasks = [
        simulate_user(i, 10)
        for i in range(num_users)
    ]
    
    await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    print(f"Completed {num_users} users in {elapsed:.2f} seconds")
    print(f"Average: {elapsed / num_users:.2f} seconds per user")

# Run test
asyncio.run(load_test(10))
```

### Memory Testing

Monitor memory usage during operation:

```python
import psutil
import os

def check_memory():
    """Check bot memory usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")

# Call periodically during testing
check_memory()
```

## Test Scenarios

### Scenario 1: Complete User Journey

1. User creates account
2. User creates profile with all fields
3. User uploads media
4. User marks available
5. Group members see listing
6. Listing expires and auto-deletes
7. User marks available again

### Scenario 2: Error Recovery

1. Bot loses connection during profile creation
2. User resends message
3. Bot recovers and continues
4. Profile saved successfully

### Scenario 3: Concurrent Users

1. Multiple users create profiles simultaneously
2. Multiple users mark available at same time
3. All listings appear correctly in group
4. No conflicts or data loss

### Scenario 4: Edge Cases

1. User sends very long text (>4096 characters)
2. User uploads maximum media (10 images, 4 videos)
3. User sends special characters and emojis
4. User sends links in social media field

## Regression Testing

After making changes, test:

- [ ] Profile creation still works
- [ ] Availability toggle still works
- [ ] Group listing still appears correctly
- [ ] Auto-deletion still works
- [ ] Admin verification still works
- [ ] Error handling still works

## Browser/Client Testing

Test with different Telegram clients:

- [ ] Desktop app
- [ ] Mobile app (iOS)
- [ ] Mobile app (Android)
- [ ] Web client
- [ ] Bot API

## Deployment Testing

Before production deployment:

- [ ] Test on staging server
- [ ] Test with production bot token
- [ ] Test with real group
- [ ] Monitor logs for errors
- [ ] Test with real users
- [ ] Verify all features work
- [ ] Check performance metrics
- [ ] Verify security measures

## Test Report Template

```markdown
# Test Report - Available Now Bot

## Date: [DATE]
## Tester: [NAME]
## Version: [VERSION]

### Summary
- Total Tests: 50
- Passed: 48
- Failed: 2
- Skipped: 0

### Failed Tests
1. [Test name] - [Description]
2. [Test name] - [Description]

### Issues Found
1. [Issue] - [Severity] - [Status]
2. [Issue] - [Severity] - [Status]

### Recommendations
- [Recommendation 1]
- [Recommendation 2]

### Sign-off
- [ ] Ready for production
- [ ] Needs fixes
- [ ] Needs more testing
```

## Continuous Testing

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Test Bot

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: pytest tests/
    
    - name: Run linting
      run: |
        pip install flake8
        flake8 bot.py
```

## Troubleshooting Test Issues

### Bot doesn't respond to commands
- Check bot token is correct
- Verify bot is added to group
- Check bot has required permissions
- Review logs for errors

### Listings don't appear in group
- Verify TARGET_GROUP_ID is correct
- Check bot is member of group
- Verify bot has send_message permission
- Check for API errors in logs

### Media not uploading
- Check file size limits
- Verify file format is supported
- Check Telegram API limits
- Review logs for upload errors

### Performance issues
- Check memory usage
- Monitor CPU usage
- Review database queries
- Optimize code if needed

## Success Criteria

Bot is ready for production when:

- [ ] All manual tests pass
- [ ] All automated tests pass
- [ ] No critical bugs found
- [ ] Performance meets requirements
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Deployment plan ready
- [ ] Rollback plan ready
