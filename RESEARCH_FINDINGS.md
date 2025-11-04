# Research Findings: Telegram Bot API & python-telegram-bot

## Date: November 4, 2025

### 1. Media Groups (sendMediaGroup)

#### Key Capabilities
- **sendMediaGroup** method allows sending groups of photos, videos, documents, or audios as an album
- Documents and audio files can only be grouped in an album with messages of the same type
- Returns an array of Message objects that were sent
- Media groups must include 2-10 items

#### Supported Media Types
- `InputMediaPhoto`: Photos (JPEG, PNG, GIF)
- `InputMediaVideo`: Videos (MP4, WebM, MOV)
- `InputMediaDocument`: Documents (PDF, DOCX, etc.)
- `InputMediaAudio`: Audio files (MP3, WAV, etc.)

#### Limitations
- Animations cannot be used in media groups
- Mixed media types have restrictions (photos/videos can mix, but documents/audio must be same type)
- Maximum 10 items per group
- Minimum 2 items per group

#### Implementation in python-telegram-bot
```python
from telegram import InputMediaPhoto, InputMediaVideo

media = [
    InputMediaPhoto(media=photo_file_id),
    InputMediaPhoto(media=photo_file_id_2),
]
await context.bot.send_media_group(chat_id=chat_id, media=media)
```

### 2. ConversationHandler State Management

#### Architecture
- **entry_points**: List of handlers that start the conversation
- **states**: Dictionary mapping state integers to lists of handlers
- **fallbacks**: Handlers that work in any state (e.g., /cancel)
- **conversation_timeout**: Auto-end conversation after N seconds of inactivity

#### State Transitions
- Handlers return the next state to transition to
- Returning `None` keeps the current state
- Returning `ConversationHandler.END` or `-1` ends the conversation
- Returning `ConversationHandler.TIMEOUT` or `-2` handles timeout

#### Context Management
- `context.user_data`: Dictionary for storing user-specific data across states
- `context.chat_data`: Dictionary for storing chat-specific data
- `context.bot_data`: Dictionary for storing bot-wide data

#### Key Features
- Automatically handles per-user state tracking
- Supports concurrent conversations with multiple users
- Can handle conversation timeouts with custom handlers
- Supports `per_chat=True` for group conversations
- Supports `per_user=True` for per-user state tracking (default)

### 3. Inline Keyboards & Callback Queries

#### InlineKeyboardButton
- Creates clickable buttons within messages
- Supports various callback types:
  - `callback_data`: Custom data string (max 64 bytes)
  - `url`: Direct URL link
  - `web_app`: Web app integration
  - `switch_inline_query`: Inline query
  - `switch_inline_query_current_chat`: Inline query in current chat
  - `pay`: Payment button
  - `login_url`: Login button

#### CallbackQueryHandler
- Handles button clicks
- Pattern matching with regex or exact strings
- Can answer with notifications or alerts
- Can edit the original message

#### Implementation Pattern
```python
keyboard = [
    [InlineKeyboardButton("Option 1", callback_data='option_1')],
    [InlineKeyboardButton("Option 2", callback_data='option_2')],
]
reply_markup = InlineKeyboardMarkup(keyboard)

# Send message with keyboard
await update.message.reply_text("Choose:", reply_markup=reply_markup)

# Handle callback
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Answer the callback query
    await query.edit_message_text(text="You selected: " + query.data)
```

### 4. Message Editing & Updates

#### Supported Edit Methods
- `editMessageText`: Change text content
- `editMessageCaption`: Change caption
- `editMessageMedia`: Change media (photo, video, etc.)
- `editMessageReplyMarkup`: Change inline keyboard
- `deleteMessage`: Remove message

#### Limitations
- Can only edit messages sent by the bot
- Cannot edit messages older than 48 hours (some restrictions apply)
- Edited messages show "edited" indicator
- Callback queries can edit the original message

### 5. Auto-Deletion & Scheduling

#### Current Implementation Approach
- Use `asyncio.sleep()` for scheduled deletions
- Track message IDs and expiration times
- Delete messages when expiration time is reached

#### Recommended Improvements
- Implement a background task scheduler
- Use APScheduler for more complex scheduling
- Store expiration times in database for persistence
- Handle bot restarts gracefully

### 6. File Handling & Media Storage

#### Telegram File IDs
- Each media item has a unique `file_id`
- File IDs are persistent and can be reused
- No need to download and re-upload media
- File IDs are bot-specific (different for different bots)

#### File Upload Methods
- Direct file upload: Send file bytes
- File ID reuse: Send existing file_id
- URL: Send media from URL (Telegram downloads it)

#### Storage Recommendations
- Store file_ids in database for reuse
- Don't store actual file bytes (use Telegram's servers)
- Keep metadata (filename, size, type) in database
- Implement file access logging

### 7. Performance Considerations

#### Rate Limiting
- Telegram enforces rate limits on API calls
- Recommended: Max 30 messages per second per bot
- Use exponential backoff for retries
- Implement request queuing for high-volume scenarios

#### Polling vs Webhooks
- **Polling** (current implementation): Simple but less efficient
- **Webhooks**: More efficient, requires HTTPS and public URL
- Polling suitable for: Development, low-traffic bots
- Webhooks suitable for: Production, high-traffic bots

#### Memory Management
- Store only necessary data in memory
- Use database for persistent storage
- Implement cleanup routines for old data
- Monitor memory usage in production

### 8. Security Best Practices

#### Token Security
- Never commit bot token to version control
- Use environment variables
- Rotate token if compromised
- Use different tokens for dev/prod

#### Input Validation
- Validate all user inputs
- Sanitize text before displaying
- Use HTML escaping for user-generated content
- Implement rate limiting per user

#### Admin Verification
- Verify user IDs before granting admin access
- Log all admin actions
- Implement role-based access control
- Use Telegram's built-in admin features when possible

### 9. Recommended Enhancements for Current Bot

1. **Database Integration**
   - Replace in-memory storage with SQLAlchemy + PostgreSQL
   - Enable persistence across bot restarts
   - Implement backup and recovery

2. **Advanced Scheduling**
   - Use APScheduler instead of asyncio.sleep()
   - Support recurring availability patterns
   - Handle timezone-aware scheduling

3. **Media Optimization**
   - Implement image compression
   - Generate thumbnails for galleries
   - Support multiple image formats

4. **Analytics**
   - Track profile views and contacts
   - Generate usage statistics
   - Monitor bot performance

5. **Webhook Support**
   - Implement webhook endpoint for production
   - Add SSL certificate support
   - Implement request verification

6. **Error Handling**
   - Implement comprehensive error logging
   - Add retry logic with exponential backoff
   - Graceful degradation for API failures

7. **Testing**
   - Unit tests for core functions
   - Integration tests for conversation flows
   - Mock Telegram API for testing

### 10. API Version Information

- **Current Bot API**: Version 8.0+ (as of August 2025)
- **python-telegram-bot**: Version 22.5+
- **Latest Features**: Checklists, Gifts, Direct Messages in Channels
- **Deprecations**: None affecting current implementation

### References

1. [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
2. [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
3. [ConversationHandler Guide](https://docs.python-telegram-bot.org/en/stable/telegram.ext.conversationhandler.html)
4. [sendMediaGroup Documentation](https://core.telegram.org/bots/api#sendmediagroup)

### Conclusion

The current implementation using `python-telegram-bot` v20.7+ is well-suited for the Available Now bot. The library provides:

- Robust conversation handling with state management
- Full support for inline keyboards and callback queries
- Media group support for image/video galleries
- Automatic message editing and deletion
- Comprehensive error handling

For production deployment, consider:
- Adding database persistence
- Implementing webhook support
- Adding comprehensive logging and monitoring
- Implementing advanced scheduling with APScheduler
- Adding unit and integration tests
