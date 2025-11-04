"""
Available Now Telegram Bot
A bot for group admins to manage and post their availability profiles.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import asyncio

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
from telegram.constants import ChatAction, ParseMode
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

APPROVED_ADMINS = set(os.getenv('APPROVED_ADMINS', '').split(',')) if os.getenv('APPROVED_ADMINS') else set()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TARGET_GROUP_ID = int(os.getenv('TARGET_GROUP_ID', '0')) if os.getenv('TARGET_GROUP_ID') else None

# Conversation states
(
    PROFILE_NAME, PROFILE_OFFER_TYPES, PROFILE_IN_PERSON_TYPE,
    PROFILE_IN_PERSON_LOCATION, PROFILE_FACETIME_PLATFORMS,
    PROFILE_FACETIME_PAYMENT, PROFILE_CUSTOM_PAYMENT,
    PROFILE_CUSTOM_DELIVERY, PROFILE_OTHER_SERVICE,
    PROFILE_ABOUT, PROFILE_CONTACT_METHOD, PROFILE_PHONE,
    PROFILE_EMAIL, PROFILE_SOCIAL_LINKS, PROFILE_RATES,
    PROFILE_DISCLAIMER, PROFILE_IMAGES, PROFILE_VIDEOS,
    PROFILE_PREVIEW, AVAILABILITY_DURATION
) = range(20)

# ============================================================================
# DATABASE SIMULATION (In production, use SQLAlchemy + PostgreSQL)
# ============================================================================

class ProfileDatabase:
    """Simple in-memory database for profiles. Replace with SQLAlchemy in production."""
    
    def __init__(self):
        self.profiles: Dict[int, Dict[str, Any]] = {}
        self.active_listings: Dict[int, Dict[str, Any]] = {}  # user_id -> listing info
        self.listing_messages: Dict[int, Dict[str, Any]] = {}  # message_id -> listing info
    
    def save_profile(self, user_id: int, profile: Dict[str, Any]):
        """Save a user's profile."""
        self.profiles[user_id] = profile
    
    def get_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a user's profile."""
        return self.profiles.get(user_id)
    
    def delete_profile(self, user_id: int):
        """Delete a user's profile."""
        if user_id in self.profiles:
            del self.profiles[user_id]
    
    def create_listing(self, user_id: int, duration_hours: int, message_id: int):
        """Create an active listing."""
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        self.active_listings[user_id] = {
            'message_id': message_id,
            'expires_at': expires_at,
            'duration_hours': duration_hours
        }
        self.listing_messages[message_id] = {
            'user_id': user_id,
            'expires_at': expires_at
        }
    
    def get_active_listings(self) -> List[tuple]:
        """Get all active listings (user_id, listing_info)."""
        now = datetime.now()
        active = []
        expired = []
        
        for user_id, listing in self.active_listings.items():
            if listing['expires_at'] > now:
                active.append((user_id, listing))
            else:
                expired.append(user_id)
        
        # Clean up expired listings
        for user_id in expired:
            del self.active_listings[user_id]
        
        return active
    
    def delete_listing(self, user_id: int):
        """Delete a user's active listing."""
        if user_id in self.active_listings:
            message_id = self.active_listings[user_id]['message_id']
            del self.active_listings[user_id]
            if message_id in self.listing_messages:
                del self.listing_messages[message_id]

db = ProfileDatabase()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_approved_admin(user_id: int) -> bool:
    """Check if user is an approved admin."""
    return str(user_id) in APPROVED_ADMINS or len(APPROVED_ADMINS) == 0

async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send typing action to show the bot is processing."""
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

def format_profile_preview(profile: Dict[str, Any]) -> str:
    """Format a profile for preview in the private chat."""
    text = f"<b>Preview of Your Listing</b>\n\n"
    text += f"<b>{profile.get('name', 'N/A')}</b>\n\n"
    
    # Services
    services = profile.get('offer_types', [])
    if services:
        text += "<b>Services Offered:</b>\n"
        for service in services:
            if service == 'in_person':
                text += f"  🧍 In-Person ({profile.get('in_person_type', 'N/A')}, {profile.get('in_person_location', 'N/A')})\n"
            elif service == 'facetime':
                text += f"  📱 Facetime Shows ({profile.get('facetime_platforms', 'N/A')}, {profile.get('facetime_payment', 'N/A')})\n"
            elif service == 'custom':
                text += f"  🎥 Custom Content ({profile.get('custom_delivery', 'N/A')}, {profile.get('custom_payment', 'N/A')})\n"
            elif service == 'other':
                text += f"  ❓ {profile.get('other_service', 'N/A')}\n"
        text += "\n"
    
    # About
    if profile.get('about'):
        text += f"<b>About:</b>\n{profile['about']}\n\n"
    
    # Contact
    contact_method = profile.get('contact_method', 'N/A')
    text += "<b>Contact:</b>\n"
    if contact_method == 'phone':
        text += f"  Phone: {profile.get('phone', 'N/A')}\n"
    elif contact_method == 'email':
        text += f"  Email: {profile.get('email', 'N/A')}\n"
    elif contact_method == 'telegram':
        text += f"  Telegram: @{profile.get('telegram_username', 'N/A')}\n"
    text += "\n"
    
    # Social Media
    if profile.get('social_links'):
        text += f"<b>Social Media:</b>\n{profile['social_links']}\n\n"
    
    # Rates
    if profile.get('rates'):
        text += f"<b>Rates:</b>\n{profile['rates']}\n\n"
    
    # Disclaimer
    if profile.get('disclaimer'):
        text += f"<b>Notice:</b>\n{profile['disclaimer']}\n\n"
    
    text += "<i>Images and videos will be displayed in the group listing.</i>"
    return text

def format_group_listing(profile: Dict[str, Any], expires_at: datetime) -> str:
    """Format a profile for display in the group chat."""
    now = datetime.now()
    time_remaining = expires_at - now
    hours = int(time_remaining.total_seconds() // 3600)
    minutes = int((time_remaining.total_seconds() % 3600) // 60)
    
    countdown = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    text = f"💋 <b>{profile.get('name', 'N/A')}</b> 💋\n"
    text += f"📅 Posted: {datetime.now().strftime('%b %d, %Y, %I:%M %p')} | Expires in: {countdown}\n\n"
    
    # Services
    services = profile.get('offer_types', [])
    if services:
        text += "<b>Services Offered:</b>\n"
        for service in services:
            if service == 'in_person':
                text += f"  🧍 In-Person ({profile.get('in_person_type', 'N/A')}, {profile.get('in_person_location', 'N/A')})\n"
            elif service == 'facetime':
                text += f"  📱 Facetime Shows ({profile.get('facetime_platforms', 'N/A')}, {profile.get('facetime_payment', 'N/A')})\n"
            elif service == 'custom':
                text += f"  🎥 Custom Content ({profile.get('custom_delivery', 'N/A')}, {profile.get('custom_payment', 'N/A')})\n"
            elif service == 'other':
                text += f"  ❓ {profile.get('other_service', 'N/A')}\n"
        text += "\n"
    
    # About
    if profile.get('about'):
        text += f"<b>About:</b>\n{profile['about']}\n\n"
    
    # Contact
    contact_method = profile.get('contact_method', 'N/A')
    text += "<b>Contact:</b>\n"
    if contact_method == 'phone':
        text += f"  Phone: {profile.get('phone', 'N/A')}\n"
    elif contact_method == 'email':
        text += f"  Email: {profile.get('email', 'N/A')}\n"
    elif contact_method == 'telegram':
        text += f"  Telegram: @{profile.get('telegram_username', 'N/A')}\n"
    text += "\n"
    
    # Social Media
    if profile.get('social_links'):
        text += f"<b>Social Media:</b>\n{profile['social_links']}\n\n"
    
    # Rates
    if profile.get('rates'):
        text += f"<b>Rates:</b>\n{profile['rates']}\n\n"
    
    # Disclaimer
    if profile.get('disclaimer'):
        text += f"<b>Notice:</b>\n{profile['disclaimer']}\n\n"
    
    return text

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - show main menu."""
    user_id = update.effective_user.id
    
    if not is_approved_admin(user_id):
        await update.message.reply_text(
            "❌ You must be an approved admin to use this bot."
        )
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("📝 Create Profile", callback_data='create_profile')],
        [InlineKeyboardButton("✏️ Edit Profile", callback_data='edit_profile')],
        [InlineKeyboardButton("🗑️ Delete Profile", callback_data='delete_profile')],
        [InlineKeyboardButton("📢 Mark Available", callback_data='mark_available')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Welcome to Available Now Bot!\n\n"
        "What would you like to do?",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def create_profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the profile creation process."""
    user_id = update.effective_user.id
    
    if not is_approved_admin(user_id):
        await update.callback_query.answer("❌ You must be an approved admin.", show_alert=True)
        return ConversationHandler.END
    
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "📝 <b>Create Your Profile</b>\n\n"
        "Let's start with your name or catchy subject line.\n\n"
        "Examples:\n"
        "  • Alex\n"
        "  • Ready for an unforgettable night? 💋\n\n"
        "Please enter your name or subject line:",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data['profile'] = {}
    return PROFILE_NAME

async def profile_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle profile name input."""
    context.user_data['profile']['name'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("🧍 In-Person", callback_data='offer_in_person')],
        [InlineKeyboardButton("📱 Facetime Shows", callback_data='offer_facetime')],
        [InlineKeyboardButton("🎥 Custom Content", callback_data='offer_custom')],
        [InlineKeyboardButton("❓ Other", callback_data='offer_other')],
        [InlineKeyboardButton("✅ Done Selecting", callback_data='offers_done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Great! Now, what services do you offer? Select all that apply:\n\n"
        "(Click 'Done Selecting' when finished)",
        reply_markup=reply_markup
    )
    
    context.user_data['profile']['offer_types'] = []
    return PROFILE_OFFER_TYPES

async def offer_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle offer type selection."""
    query = update.callback_query
    await query.answer()
    
    offer_type = query.data.replace('offer_', '')
    
    if offer_type == 'in_person':
        context.user_data['current_offer'] = 'in_person'
        
        keyboard = [
            [InlineKeyboardButton("🏠 Incall Only", callback_data='inperson_incall')],
            [InlineKeyboardButton("🚗 Outcall Only", callback_data='inperson_outcall')],
            [InlineKeyboardButton("🏠🚗 Incall/Outcall", callback_data='inperson_both')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "For In-Person services, which do you offer?",
            reply_markup=reply_markup
        )
        return PROFILE_IN_PERSON_TYPE
    
    elif offer_type == 'facetime':
        context.user_data['current_offer'] = 'facetime'
        await query.edit_message_text(
            "Which platforms do you use for Facetime shows?\n\n"
            "Examples: Facetime, Google Duo, OnlyFans\n\n"
            "Please enter the platforms:",
            parse_mode=ParseMode.HTML
        )
        return PROFILE_FACETIME_PLATFORMS
    
    elif offer_type == 'custom':
        context.user_data['current_offer'] = 'custom'
        await query.edit_message_text(
            "What payment methods do you accept for custom content?\n\n"
            "Examples: PayPal, CashApp, Bitcoin\n\n"
            "Please enter the payment methods:",
            parse_mode=ParseMode.HTML
        )
        return PROFILE_CUSTOM_PAYMENT
    
    elif offer_type == 'other':
        context.user_data['current_offer'] = 'other'
        await query.edit_message_text(
            "Describe your custom service:\n\n"
            "Please enter a description:",
            parse_mode=ParseMode.HTML
        )
        return PROFILE_OTHER_SERVICE
    
    elif offer_type == 'done':
        if not context.user_data['profile'].get('offer_types'):
            await query.answer("❌ Please select at least one service.", show_alert=True)
            return PROFILE_OFFER_TYPES
        
        await query.edit_message_text(
            "Now, tell us about yourself.\n\n"
            "You can include:\n"
            "  • Physical stats (height, measurements)\n"
            "  • Personality traits\n"
            "  • What makes you special\n\n"
            "Please enter your description:",
            parse_mode=ParseMode.HTML
        )
        return PROFILE_ABOUT
    
    return PROFILE_OFFER_TYPES

async def in_person_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle in-person type selection."""
    query = update.callback_query
    await query.answer()
    
    in_person_type = query.data.replace('inperson_', '')
    type_map = {
        'incall': 'Incall Only',
        'outcall': 'Outcall Only',
        'both': 'Incall/Outcall'
    }
    
    context.user_data['profile']['in_person_type'] = type_map.get(in_person_type, 'N/A')
    context.user_data['profile']['offer_types'].append('in_person')
    
    await query.edit_message_text(
        "What's your general location?\n\n"
        "Examples: Uptown Manhattan, Times Square\n\n"
        "Please enter your location:",
        parse_mode=ParseMode.HTML
    )
    return PROFILE_IN_PERSON_LOCATION

async def in_person_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle in-person location input."""
    context.user_data['profile']['in_person_location'] = update.message.text
    
    # Show offer menu again
    keyboard = [
        [InlineKeyboardButton("🧍 In-Person", callback_data='offer_in_person')],
        [InlineKeyboardButton("📱 Facetime Shows", callback_data='offer_facetime')],
        [InlineKeyboardButton("🎥 Custom Content", callback_data='offer_custom')],
        [InlineKeyboardButton("❓ Other", callback_data='offer_other')],
        [InlineKeyboardButton("✅ Done Selecting", callback_data='offers_done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Great! Select another service or continue:\n\n"
        "(Click 'Done Selecting' when finished)",
        reply_markup=reply_markup
    )
    return PROFILE_OFFER_TYPES

async def facetime_platforms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle facetime platforms input."""
    context.user_data['profile']['facetime_platforms'] = update.message.text
    context.user_data['profile']['offer_types'].append('facetime')
    
    await update.message.reply_text(
        "What payment methods do you accept?\n\n"
        "Examples: CashApp, PayPal, Bitcoin\n\n"
        "Please enter the payment methods:"
    )
    return PROFILE_FACETIME_PAYMENT

async def facetime_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle facetime payment input."""
    context.user_data['profile']['facetime_payment'] = update.message.text
    
    # Show offer menu again
    keyboard = [
        [InlineKeyboardButton("🧍 In-Person", callback_data='offer_in_person')],
        [InlineKeyboardButton("📱 Facetime Shows", callback_data='offer_facetime')],
        [InlineKeyboardButton("🎥 Custom Content", callback_data='offer_custom')],
        [InlineKeyboardButton("❓ Other", callback_data='offer_other')],
        [InlineKeyboardButton("✅ Done Selecting", callback_data='offers_done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select another service or continue:\n\n"
        "(Click 'Done Selecting' when finished)",
        reply_markup=reply_markup
    )
    return PROFILE_OFFER_TYPES

async def custom_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle custom content payment input."""
    context.user_data['profile']['custom_payment'] = update.message.text
    context.user_data['profile']['offer_types'].append('custom')
    
    await update.message.reply_text(
        "How will content be delivered?\n\n"
        "Examples: Email, Telegram, Dropbox\n\n"
        "Please enter the delivery method:"
    )
    return PROFILE_CUSTOM_DELIVERY

async def custom_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle custom content delivery input."""
    context.user_data['profile']['custom_delivery'] = update.message.text
    
    # Show offer menu again
    keyboard = [
        [InlineKeyboardButton("🧍 In-Person", callback_data='offer_in_person')],
        [InlineKeyboardButton("📱 Facetime Shows", callback_data='offer_facetime')],
        [InlineKeyboardButton("🎥 Custom Content", callback_data='offer_custom')],
        [InlineKeyboardButton("❓ Other", callback_data='offer_other')],
        [InlineKeyboardButton("✅ Done Selecting", callback_data='offers_done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select another service or continue:\n\n"
        "(Click 'Done Selecting' when finished)",
        reply_markup=reply_markup
    )
    return PROFILE_OFFER_TYPES

async def other_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle other service input."""
    context.user_data['profile']['other_service'] = update.message.text
    context.user_data['profile']['offer_types'].append('other')
    
    # Show offer menu again
    keyboard = [
        [InlineKeyboardButton("🧍 In-Person", callback_data='offer_in_person')],
        [InlineKeyboardButton("📱 Facetime Shows", callback_data='offer_facetime')],
        [InlineKeyboardButton("🎥 Custom Content", callback_data='offer_custom')],
        [InlineKeyboardButton("❓ Other", callback_data='offer_other')],
        [InlineKeyboardButton("✅ Done Selecting", callback_data='offers_done')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select another service or continue:\n\n"
        "(Click 'Done Selecting' when finished)",
        reply_markup=reply_markup
    )
    return PROFILE_OFFER_TYPES

async def profile_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle about section input."""
    context.user_data['profile']['about'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("📞 Text/Call", callback_data='contact_phone')],
        [InlineKeyboardButton("📧 Email", callback_data='contact_email')],
        [InlineKeyboardButton("💬 Telegram", callback_data='contact_telegram')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "How should people contact you?",
        reply_markup=reply_markup
    )
    return PROFILE_CONTACT_METHOD

async def contact_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle contact method selection."""
    query = update.callback_query
    await query.answer()
    
    method = query.data.replace('contact_', '')
    context.user_data['profile']['contact_method'] = method
    
    if method == 'phone':
        await query.edit_message_text(
            "Please enter your phone number:"
        )
        return PROFILE_PHONE
    elif method == 'email':
        await query.edit_message_text(
            "Please enter your email address:"
        )
        return PROFILE_EMAIL
    elif method == 'telegram':
        username = update.effective_user.username or 'unknown'
        context.user_data['profile']['telegram_username'] = username
        
        await query.edit_message_text(
            f"Great! Your Telegram username is @{username}\n\n"
            "Now, enter links to your social media or content platforms.\n\n"
            "Examples: X, Instagram, OnlyFans, Snapchat\n\n"
            "You can enter multiple links separated by commas or new lines."
        )
        return PROFILE_SOCIAL_LINKS
    
    return PROFILE_CONTACT_METHOD

async def profile_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle phone number input."""
    context.user_data['profile']['phone'] = update.message.text
    
    await update.message.reply_text(
        "Now, enter links to your social media or content platforms.\n\n"
        "Examples: X, Instagram, OnlyFans, Snapchat\n\n"
        "You can enter multiple links separated by commas or new lines."
    )
    return PROFILE_SOCIAL_LINKS

async def profile_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle email input."""
    context.user_data['profile']['email'] = update.message.text
    
    await update.message.reply_text(
        "Now, enter links to your social media or content platforms.\n\n"
        "Examples: X, Instagram, OnlyFans, Snapchat\n\n"
        "You can enter multiple links separated by commas or new lines."
    )
    return PROFILE_SOCIAL_LINKS

async def profile_social_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle social media links input."""
    context.user_data['profile']['social_links'] = update.message.text
    
    await update.message.reply_text(
        "Enter your rates or note that they're discussed privately.\n\n"
        "Examples:\n"
        "  • In-Person: $200/hr\n"
        "  • Facetime: $50/30min\n"
        "  • Custom Content: Discuss privately"
    )
    return PROFILE_RATES

async def profile_rates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle rates input."""
    context.user_data['profile']['rates'] = update.message.text
    
    await update.message.reply_text(
        "Add any disclaimers or notices.\n\n"
        "Examples:\n"
        "  • Please contact me privately to book\n"
        "  • Deposits required\n"
        "  • Verification required"
    )
    return PROFILE_DISCLAIMER

async def profile_disclaimer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle disclaimer input."""
    context.user_data['profile']['disclaimer'] = update.message.text
    
    await update.message.reply_text(
        "Now, upload up to 10 images for your gallery.\n\n"
        "Send images one at a time, or send 'done' when finished."
    )
    context.user_data['profile']['images'] = []
    return PROFILE_IMAGES

async def profile_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle image uploads."""
    if update.message.text and update.message.text.lower() == 'done':
        await update.message.reply_text(
            "Now, upload up to 4 videos for your listing.\n\n"
            "Send videos one at a time, or send 'done' when finished."
        )
        context.user_data['profile']['videos'] = []
        return PROFILE_VIDEOS
    
    if update.message.photo:
        if len(context.user_data['profile']['images']) < 10:
            context.user_data['profile']['images'].append(update.message.photo[-1].file_id)
            await update.message.reply_text(
                f"✅ Image {len(context.user_data['profile']['images'])}/10 saved.\n\n"
                "Send another image or 'done' to continue."
            )
        else:
            await update.message.reply_text(
                "You've reached the maximum of 10 images.\n\n"
                "Send 'done' to continue."
            )
    else:
        await update.message.reply_text(
            "Please send an image or type 'done' to continue."
        )
    
    return PROFILE_IMAGES

async def profile_videos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle video uploads."""
    if update.message.text and update.message.text.lower() == 'done':
        # Show preview
        profile = context.user_data['profile']
        preview_text = format_profile_preview(profile)
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data='profile_confirm')],
            [InlineKeyboardButton("✏️ Edit", callback_data='profile_edit')],
            [InlineKeyboardButton("❌ Cancel", callback_data='profile_cancel')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            preview_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return PROFILE_PREVIEW
    
    if update.message.video:
        if len(context.user_data['profile']['videos']) < 4:
            context.user_data['profile']['videos'].append(update.message.video.file_id)
            await update.message.reply_text(
                f"✅ Video {len(context.user_data['profile']['videos'])}/4 saved.\n\n"
                "Send another video or 'done' to continue."
            )
        else:
            await update.message.reply_text(
                "You've reached the maximum of 4 videos.\n\n"
                "Send 'done' to continue."
            )
    else:
        await update.message.reply_text(
            "Please send a video or type 'done' to continue."
        )
    
    return PROFILE_VIDEOS

async def profile_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle profile preview actions."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'profile_confirm':
        user_id = update.effective_user.id
        db.save_profile(user_id, context.user_data['profile'])
        
        await query.edit_message_text(
            "✅ Profile saved successfully!\n\n"
            "You can now mark yourself as available using /available"
        )
        return ConversationHandler.END
    
    elif query.data == 'profile_edit':
        await query.edit_message_text(
            "Edit functionality coming soon. For now, create a new profile."
        )
        return ConversationHandler.END
    
    elif query.data == 'profile_cancel':
        await query.edit_message_text(
            "Profile creation cancelled."
        )
        return ConversationHandler.END
    
    return PROFILE_PREVIEW

async def mark_available(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mark user as available."""
    user_id = update.effective_user.id
    
    if not is_approved_admin(user_id):
        await update.callback_query.answer("❌ You must be an approved admin.", show_alert=True)
        return ConversationHandler.END
    
    profile = db.get_profile(user_id)
    if not profile:
        await update.callback_query.answer(
            "❌ You must create a profile first.",
            show_alert=True
        )
        return ConversationHandler.END
    
    await update.callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton("2 hours", callback_data='duration_2')],
        [InlineKeyboardButton("4 hours", callback_data='duration_4')],
        [InlineKeyboardButton("6 hours", callback_data='duration_6')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "How long will you be available?",
        reply_markup=reply_markup
    )
    return AVAILABILITY_DURATION

async def availability_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle availability duration selection."""
    query = update.callback_query
    await query.answer()
    
    duration_hours = int(query.data.replace('duration_', ''))
    user_id = update.effective_user.id
    
    profile = db.get_profile(user_id)
    if not profile:
        await query.edit_message_text("❌ Profile not found.")
        return ConversationHandler.END
    
    if not TARGET_GROUP_ID:
        await query.edit_message_text(
            "❌ Target group not configured. Please set TARGET_GROUP_ID environment variable."
        )
        return ConversationHandler.END
    
    try:
        # Format and send listing to group
        listing_text = format_group_listing(profile, datetime.now() + timedelta(hours=duration_hours))
        
        message = await context.bot.send_message(
            chat_id=TARGET_GROUP_ID,
            text=listing_text,
            parse_mode=ParseMode.HTML
        )
        
        # Save listing info
        db.create_listing(user_id, duration_hours, message.message_id)
        
        await query.edit_message_text(
            f"✅ Your listing has been posted to the group for {duration_hours} hours!\n\n"
            "It will automatically be deleted when the time expires."
        )
        
        # Schedule deletion
        context.application.create_task(
            schedule_listing_deletion(context, TARGET_GROUP_ID, message.message_id, duration_hours)
        )
        
    except TelegramError as e:
        logger.error(f"Error posting listing: {e}")
        await query.edit_message_text(
            f"❌ Error posting listing: {str(e)}"
        )
    
    return ConversationHandler.END

async def schedule_listing_deletion(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, hours: int):
    """Schedule deletion of a listing after the specified hours."""
    await asyncio.sleep(hours * 3600)
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted listing message {message_id}")
    except TelegramError as e:
        logger.error(f"Error deleting listing: {e}")

async def available_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /available command in group to show active listings."""
    active_listings = db.get_active_listings()
    
    if not active_listings:
        message = await update.message.reply_text(
            "📋 No models available right now.\n\n"
            "Check back soon!"
        )
    else:
        text = "📋 <b>Available Now:</b>\n\n"
        for i, (user_id, listing) in enumerate(active_listings, 1):
            profile = db.get_profile(user_id)
            if profile:
                services = ', '.join([
                    'In-Person' if s == 'in_person' else
                    'Facetime Shows' if s == 'facetime' else
                    'Custom Content' if s == 'custom' else
                    'Other'
                    for s in profile.get('offer_types', [])
                ])
                text += f"{i}. <b>{profile.get('name', 'N/A')}</b> ({services})\n"
        
        text += "\n<i>This list will auto-delete in 5 minutes.</i>"
        message = await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML
        )
    
    # Schedule deletion of the list message
    context.application.create_task(
        schedule_message_deletion(context, update.effective_chat.id, message.message_id, 5)
    )

async def schedule_message_deletion(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, minutes: int):
    """Schedule deletion of a message after the specified minutes."""
    await asyncio.sleep(minutes * 60)
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted message {message_id}")
    except TelegramError as e:
        logger.error(f"Error deleting message: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('createprofile', create_profile_start),
            CommandHandler('available', mark_available),
            CallbackQueryHandler(create_profile_start, pattern='^create_profile$'),
            CallbackQueryHandler(mark_available, pattern='^mark_available$'),
        ],
        states={
            PROFILE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_name)],
            PROFILE_OFFER_TYPES: [CallbackQueryHandler(offer_type_selected)],
            PROFILE_IN_PERSON_TYPE: [CallbackQueryHandler(in_person_type)],
            PROFILE_IN_PERSON_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, in_person_location)],
            PROFILE_FACETIME_PLATFORMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, facetime_platforms)],
            PROFILE_FACETIME_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, facetime_payment)],
            PROFILE_CUSTOM_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_payment)],
            PROFILE_CUSTOM_DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_delivery)],
            PROFILE_OTHER_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, other_service)],
            PROFILE_ABOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_about)],
            PROFILE_CONTACT_METHOD: [CallbackQueryHandler(contact_method)],
            PROFILE_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_phone)],
            PROFILE_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_email)],
            PROFILE_SOCIAL_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_social_links)],
            PROFILE_RATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_rates)],
            PROFILE_DISCLAIMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_disclaimer)],
            PROFILE_IMAGES: [
                MessageHandler(filters.PHOTO, profile_images),
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_images),
            ],
            PROFILE_VIDEOS: [
                MessageHandler(filters.VIDEO, profile_videos),
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_videos),
            ],
            PROFILE_PREVIEW: [CallbackQueryHandler(profile_preview)],
            AVAILABILITY_DURATION: [CallbackQueryHandler(availability_duration)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('available', available_command))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
