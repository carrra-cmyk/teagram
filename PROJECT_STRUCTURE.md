# Project Structure - Available Now Bot

## Overview

The Available Now Bot is a comprehensive Telegram bot solution for group admins to manage and post their availability profiles. This document describes the project structure and file purposes.

## Directory Structure

```
available_now_bot/
├── bot.py                      # Main bot implementation (original version)
├── bot_enhanced.py             # Enhanced bot with better code organization
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
│
├── README.md                   # Main documentation and setup guide
├── QUICKSTART.md               # 5-minute quick start guide
├── CONFIGURATION.md            # Advanced configuration and customization
├── DEPLOYMENT.md               # Deployment guide for various platforms
├── DATABASE_SCHEMA.md          # Database design and SQLAlchemy models
├── TESTING.md                  # Comprehensive testing guide
├── RESEARCH_FINDINGS.md        # API research and technical findings
├── PROJECT_STRUCTURE.md        # This file
│
└── (Future additions)
    ├── models/                 # SQLAlchemy database models
    ├── handlers/               # Modular handler functions
    ├── utils/                  # Utility functions
    ├── tests/                  # Unit and integration tests
    └── migrations/             # Database migrations
```

## File Descriptions

### Core Application Files

#### `bot.py` (Original Version)
- **Purpose**: Main bot implementation with all core features
- **Size**: ~1000 lines
- **Features**:
  - Profile creation with guided conversation flow
  - Availability toggle with timed listings
  - Group member interaction
  - Admin verification
  - In-memory profile storage
- **Use**: Development and testing
- **Status**: Fully functional

#### `bot_enhanced.py` (Enhanced Version)
- **Purpose**: Improved version with better code organization
- **Size**: ~1200 lines
- **Improvements**:
  - Better code organization with ProfileFormatter class
  - Improved error handling
  - Better logging
  - Cleaner state management with IntEnum
  - Enhanced task management for deletions
- **Use**: Production deployment
- **Status**: Recommended for use

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Contents**:
  - `python-telegram-bot==20.7`: Telegram Bot API wrapper
  - `python-dotenv==1.0.0`: Environment variable management
- **Usage**: `pip install -r requirements.txt`

#### `.env.example`
- **Purpose**: Template for environment variables
- **Variables**:
  - `TELEGRAM_BOT_TOKEN`: Bot API token from @BotFather
  - `TARGET_GROUP_ID`: Group where listings are posted
  - `APPROVED_ADMINS`: Comma-separated list of admin user IDs
- **Usage**: Copy to `.env` and fill with actual values

### Documentation Files

#### `README.md` (Main Documentation)
- **Purpose**: Comprehensive project documentation
- **Sections**:
  - Features overview
  - Setup instructions
  - Usage guide for models and members
  - Example profile listing
  - Deployment options
  - Database integration guide
  - Troubleshooting
  - Future enhancements
- **Audience**: All users
- **Length**: ~500 lines

#### `QUICKSTART.md` (Quick Start Guide)
- **Purpose**: Get started in 5 minutes
- **Sections**:
  - 5-minute setup
  - First steps
  - Common commands
  - Troubleshooting
  - Next steps
- **Audience**: New users
- **Length**: ~100 lines

#### `CONFIGURATION.md` (Advanced Configuration)
- **Purpose**: Customize bot behavior
- **Sections**:
  - Environment variables
  - Customization options
  - Advanced features
  - Performance tuning
  - Security hardening
  - Testing examples
- **Audience**: Developers
- **Length**: ~400 lines

#### `DEPLOYMENT.md` (Deployment Guide)
- **Purpose**: Deploy bot to various platforms
- **Sections**:
  - Local machine
  - Linux VPS/Cloud Server
  - Docker
  - Heroku
  - AWS EC2
  - DigitalOcean
  - Railway
  - Monitoring and maintenance
  - Troubleshooting
- **Audience**: DevOps/System Administrators
- **Length**: ~400 lines

#### `DATABASE_SCHEMA.md` (Database Design)
- **Purpose**: Database schema for production
- **Sections**:
  - Table definitions (SQL)
  - Relationships
  - Indexes
  - Data types
  - Migration path
  - SQLAlchemy models
  - Performance considerations
  - Backup strategy
- **Audience**: Database Administrators
- **Length**: ~300 lines

#### `TESTING.md` (Testing Guide)
- **Purpose**: Comprehensive testing procedures
- **Sections**:
  - Setup for testing
  - Manual testing checklist
  - Automated testing
  - Performance testing
  - Test scenarios
  - Regression testing
  - Browser/client testing
  - Deployment testing
  - Test report template
- **Audience**: QA Engineers
- **Length**: ~400 lines

#### `RESEARCH_FINDINGS.md` (Technical Research)
- **Purpose**: API research and technical findings
- **Sections**:
  - Media groups capabilities
  - ConversationHandler state management
  - Inline keyboards and callbacks
  - Message editing and updates
  - Auto-deletion and scheduling
  - File handling
  - Performance considerations
  - Security best practices
  - Recommended enhancements
  - API version information
- **Audience**: Developers
- **Length**: ~300 lines

#### `PROJECT_STRUCTURE.md` (This File)
- **Purpose**: Explain project structure and file organization
- **Sections**:
  - Directory structure
  - File descriptions
  - Code organization
  - Development workflow
  - Contribution guidelines
- **Audience**: Developers
- **Length**: ~200 lines

## Code Organization

### Bot Application Structure

```python
# bot.py / bot_enhanced.py structure:

1. Imports and Configuration
   - Standard library imports
   - Third-party imports
   - Logging setup
   - Environment variables

2. Constants and Configuration
   - Approved admins
   - Bot token
   - Target group ID
   - Conversation states

3. Database Layer
   - ProfileDatabase class
   - CRUD operations
   - Listing management

4. Formatting Layer (Enhanced version)
   - ProfileFormatter class
   - Service formatting
   - Contact formatting
   - Preview formatting
   - Group listing formatting

5. Command Handlers
   - /start command
   - /createprofile command
   - /available command
   - /deleteprofile command
   - /cancel command

6. Conversation Handlers
   - Profile creation flow (20 states)
   - State transition handlers
   - Input validation
   - Error handling

7. Utility Functions
   - Message formatting
   - Profile preview
   - Listing deletion scheduling
   - Message deletion scheduling

8. Main Application
   - Application initialization
   - Handler registration
   - Polling setup
   - Error handling
```

### Key Classes

#### ProfileDatabase
- **Purpose**: In-memory profile storage
- **Methods**:
  - `save_profile()`: Save user profile
  - `get_profile()`: Retrieve profile
  - `delete_profile()`: Delete profile
  - `create_listing()`: Create active listing
  - `get_active_listings()`: Get all active listings
  - `delete_listing()`: Delete listing
  - `cancel_deletion_task()`: Cancel scheduled deletion

#### ProfileFormatter (Enhanced version)
- **Purpose**: Format profiles for display
- **Methods**:
  - `format_services()`: Format services section
  - `format_contact()`: Format contact section
  - `format_preview()`: Format preview for private chat
  - `format_group_listing()`: Format listing for group chat
- **Attributes**:
  - `SERVICE_EMOJIS`: Emoji mapping for services
  - `CONTACT_EMOJIS`: Emoji mapping for contact methods

### Conversation States

The bot uses ConversationHandler with 20 states:

1. **PROFILE_NAME**: Get user's name/subject line
2. **PROFILE_OFFER_TYPES**: Select services offered
3. **PROFILE_IN_PERSON_TYPE**: Choose incall/outcall type
4. **PROFILE_IN_PERSON_LOCATION**: Enter location
5. **PROFILE_FACETIME_PLATFORMS**: Enter platforms
6. **PROFILE_FACETIME_PAYMENT**: Enter payment methods
7. **PROFILE_CUSTOM_PAYMENT**: Enter custom payment methods
8. **PROFILE_CUSTOM_DELIVERY**: Enter delivery method
9. **PROFILE_OTHER_SERVICE**: Describe custom service
10. **PROFILE_ABOUT**: Enter about section
11. **PROFILE_CONTACT_METHOD**: Choose contact method
12. **PROFILE_PHONE**: Enter phone number
13. **PROFILE_EMAIL**: Enter email address
14. **PROFILE_SOCIAL_LINKS**: Enter social media links
15. **PROFILE_RATES**: Enter rates
16. **PROFILE_DISCLAIMER**: Enter disclaimer
17. **PROFILE_IMAGES**: Upload images
18. **PROFILE_VIDEOS**: Upload videos
19. **PROFILE_PREVIEW**: Preview and confirm
20. **AVAILABILITY_DURATION**: Choose availability duration

## Data Structures

### Profile Dictionary

```python
{
    'name': str,                      # User's name/subject line
    'offer_types': List[str],         # ['in_person', 'facetime', 'custom', 'other']
    'in_person_type': str,            # 'Incall Only', 'Outcall Only', 'Incall/Outcall'
    'in_person_location': str,        # Location
    'facetime_platforms': str,        # Platforms used
    'facetime_payment': str,          # Payment methods
    'custom_payment': str,            # Payment methods for custom content
    'custom_delivery': str,           # Delivery method
    'other_service': str,             # Custom service description
    'about': str,                     # About section
    'contact_method': str,            # 'phone', 'email', 'telegram'
    'phone': str,                     # Phone number (if contact_method='phone')
    'email': str,                     # Email address (if contact_method='email')
    'telegram_username': str,         # Telegram username (if contact_method='telegram')
    'social_links': str,              # Social media links
    'rates': str,                     # Pricing information
    'disclaimer': str,                # Important notices
    'images': List[str],              # File IDs of uploaded images
    'videos': List[str],              # File IDs of uploaded videos
    'created_at': datetime,           # Profile creation timestamp
    'updated_at': datetime            # Profile update timestamp
}
```

### Listing Dictionary

```python
{
    'message_id': int,                # Telegram message ID
    'expires_at': datetime,           # Expiration time
    'duration_hours': int,            # Duration in hours
    'created_at': datetime            # Creation timestamp
}
```

## Development Workflow

### 1. Local Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with test values

# Run
python bot.py
```

### 2. Testing

```bash
# Run tests
python -m unittest test_bot.py

# Manual testing
# Send /start to bot
# Follow conversation flow
# Verify all features work
```

### 3. Code Changes

```bash
# Make changes to bot.py or bot_enhanced.py
# Test locally
# Update documentation if needed
# Commit changes
```

### 4. Deployment

```bash
# Create checkpoint
git commit -m "Feature: [description]"

# Deploy to production
# See DEPLOYMENT.md for platform-specific instructions
```

## Future Enhancements

### Planned Additions

1. **Database Integration** (`models/`)
   - SQLAlchemy models
   - PostgreSQL integration
   - Alembic migrations

2. **Modular Handlers** (`handlers/`)
   - Separate handler files
   - Better code organization
   - Easier maintenance

3. **Utilities** (`utils/`)
   - Common functions
   - Validators
   - Formatters

4. **Tests** (`tests/`)
   - Unit tests
   - Integration tests
   - Fixtures

5. **Migrations** (`migrations/`)
   - Database schema migrations
   - Version control for database

### Proposed Directory Structure (Future)

```
available_now_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── listing.py
│   │   └── media.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── profile.py
│   │   ├── availability.py
│   │   └── group.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── formatters.py
│   │   ├── validators.py
│   │   └── database.py
│   └── database.py             # Database connection
├── tests/
│   ├── __init__.py
│   ├── test_bot.py
│   ├── test_handlers.py
│   └── test_formatters.py
├── migrations/
│   └── versions/
├── docs/
│   └── (documentation files)
├── requirements.txt
├── .env.example
└── setup.py
```

## Contribution Guidelines

### Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Keep functions focused and small

### Documentation

- Update README.md for user-facing changes
- Update CONFIGURATION.md for customization options
- Add comments for complex logic
- Keep documentation current

### Testing

- Write unit tests for new features
- Test locally before committing
- Update TESTING.md with new test cases
- Ensure all tests pass

### Commits

- Use clear, descriptive commit messages
- Reference issues when applicable
- Keep commits focused on single changes
- Follow conventional commit format

## Getting Help

- Check README.md for general questions
- Check QUICKSTART.md for setup issues
- Check CONFIGURATION.md for customization
- Check TESTING.md for testing questions
- Check DEPLOYMENT.md for deployment issues

## License

This project is provided as-is for educational and commercial use.
