"""
Available Now Telegram Bot - Simple Version
Compatible with Python 3.13
Uses aiogram library for better compatibility
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TARGET_GROUP_ID = int(os.getenv('TARGET_GROUP_ID', '0')) if os.getenv('TARGET_GROUP_ID') else None
APPROVED_ADMINS = set(os.getenv('APPROVED_ADMINS', '').split(',')) if os.getenv('APPROVED_ADMINS') else set()

# States for conversation
class ProfileStates(StatesGroup):
    name = State()
    offer_types = State()
    in_person_type = State()
    in_person_location = State()
    about = State()
    contact_method = State()
    phone = State()
    email = State()
    social_links = State()
    rates = State()
    disclaimer = State()
    images = State()
    videos = State()
    preview = State()
    availability_duration = State()

# In-memory storage
class ProfileDB:
    def __init__(self):
        self.profiles: Dict[int, Dict[str, Any]] = {}
        self.active_listings: Dict[int, Dict[str, Any]] = {}
    
    def save_profile(self, user_id: int, profile: Dict[str, Any]):
        self.profiles[user_id] = profile
        logger.info(f"Profile saved for user {user_id}")
    
    def get_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.profiles.get(user_id)
    
    def delete_profile(self, user_id: int) -> bool:
        if user_id in self.profiles:
            del self.profiles[user_id]
            return True
        return False
    
    def create_listing(self, user_id: int, duration_hours: int):
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        self.active_listings[user_id] = {
            'expires_at': expires_at,
            'duration_hours': duration_hours,
            'created_at': datetime.now()
        }
        logger.info(f"Listing created for user {user_id}")
    
    def get_active_listings(self) -> list:
        now = datetime.now()
        active = []
        expired = []
        
        for user_id, listing in self.active_listings.items():
            if listing['expires_at'] > now:
                active.append((user_id, listing))
            else:
                expired.append(user_id)
        
        for user_id in expired:
            del self.active_listings[user_id]
        
        return active
    
    def delete_listing(self, user_id: int):
        if user_id in self.active_listings:
            del self.active_listings[user_id]

db = ProfileDB()

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Start command"""
    user_id = message.from_user.id
    
    if len(APPROVED_ADMINS) > 0 and str(user_id) not in APPROVED_ADMINS:
        await message.reply("❌ You must be an approved admin to use this bot.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Create Profile", callback_data="create_profile")],
        [InlineKeyboardButton(text="✏️ Edit Profile", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🗑️ Delete Profile", callback_data="delete_profile")],
        [InlineKeyboardButton(text="📢 Mark Available", callback_data="mark_available")],
    ])
    
    await message.reply(
        "👋 Welcome to Available Now Bot!\n\n"
        "What would you like to do?",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "create_profile")
async def create_profile_start(query: types.CallbackQuery, state: FSMContext):
    """Start profile creation"""
    user_id = query.from_user.id
    
    if len(APPROVED_ADMINS) > 0 and str(user_id) not in APPROVED_ADMINS:
        await query.answer("❌ You must be an approved admin.", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "📝 <b>Create Your Profile</b>\n\n"
        "Let's start with your name or catchy subject line.\n\n"
        "Please enter your name:",
        parse_mode="HTML"
    )
    
    await state.set_state(ProfileStates.name)
    await state.update_data(profile={})

@dp.message(ProfileStates.name)
async def profile_name(message: types.Message, state: FSMContext):
    """Handle profile name"""
    await state.update_data(profile={'name': message.text})
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧍 In-Person", callback_data="offer_in_person")],
        [InlineKeyboardButton(text="📱 Facetime", callback_data="offer_facetime")],
        [InlineKeyboardButton(text="🎥 Custom", callback_data="offer_custom")],
        [InlineKeyboardButton(text="❓ Other", callback_data="offer_other")],
        [InlineKeyboardButton(text="✅ Done", callback_data="offers_done")],
    ])
    
    await message.reply(
        "What services do you offer? Select all that apply:",
        reply_markup=keyboard
    )
    await state.set_state(ProfileStates.offer_types)

@dp.callback_query(ProfileStates.offer_types, F.data.startswith("offer_"))
async def offer_selected(query: types.CallbackQuery, state: FSMContext):
    """Handle offer selection"""
    await query.answer()
    
    offer_type = query.data.replace("offer_", "")
    data = await state.get_data()
    profile = data.get('profile', {})
    
    if 'offer_types' not in profile:
        profile['offer_types'] = []
    
    if offer_type != "done":
        profile['offer_types'].append(offer_type)
        await state.update_data(profile=profile)
        await query.message.edit_text(
            f"✅ Added: {offer_type}\n\n"
            "Select another service or click 'Done':",
            reply_markup=query.message.reply_markup
        )
    else:
        if not profile.get('offer_types'):
            await query.answer("Please select at least one service", show_alert=True)
            return
        
        await query.message.edit_text(
            "Tell us about yourself:\n\n"
            "Please enter your description:"
        )
        await state.set_state(ProfileStates.about)

@dp.message(ProfileStates.about)
async def profile_about(message: types.Message, state: FSMContext):
    """Handle about section"""
    data = await state.get_data()
    profile = data.get('profile', {})
    profile['about'] = message.text
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Phone", callback_data="contact_phone")],
        [InlineKeyboardButton(text="📧 Email", callback_data="contact_email")],
        [InlineKeyboardButton(text="💬 Telegram", callback_data="contact_telegram")],
    ])
    
    await message.reply(
        "How should people contact you?",
        reply_markup=keyboard
    )
    await state.update_data(profile=profile)
    await state.set_state(ProfileStates.contact_method)

@dp.callback_query(ProfileStates.contact_method)
async def contact_method(query: types.CallbackQuery, state: FSMContext):
    """Handle contact method"""
    await query.answer()
    
    method = query.data.replace("contact_", "")
    data = await state.get_data()
    profile = data.get('profile', {})
    profile['contact_method'] = method
    
    if method == "phone":
        await query.message.edit_text("Please enter your phone number:")
        await state.set_state(ProfileStates.phone)
    elif method == "email":
        await query.message.edit_text("Please enter your email:")
        await state.set_state(ProfileStates.email)
    else:  # telegram
        profile['telegram_username'] = query.from_user.username or "unknown"
        await query.message.edit_text(
            "Enter your social media links (or send 'skip'):"
        )
        await state.set_state(ProfileStates.social_links)
    
    await state.update_data(profile=profile)

@dp.message(ProfileStates.phone)
async def handle_phone(message: types.Message, state: FSMContext):
    """Handle phone input"""
    data = await state.get_data()
    profile = data.get('profile', {})
    profile['phone'] = message.text
    
    await message.reply("Enter your social media links (or send 'skip'):")
    await state.update_data(profile=profile)
    await state.set_state(ProfileStates.social_links)

@dp.message(ProfileStates.email)
async def handle_email(message: types.Message, state: FSMContext):
    """Handle email input"""
    data = await state.get_data()
    profile = data.get('profile', {})
    profile['email'] = message.text
    
    await message.reply("Enter your social media links (or send 'skip'):")
    await state.update_data(profile=profile)
    await state.set_state(ProfileStates.social_links)

@dp.message(ProfileStates.social_links)
async def handle_social_links(message: types.Message, state: FSMContext):
    """Handle social links"""
    data = await state.get_data()
    profile = data.get('profile', {})
    
    if message.text.lower() != 'skip':
        profile['social_links'] = message.text
    
    await message.reply("Enter your rates (or send 'skip'):")
    await state.update_data(profile=profile)
    await state.set_state(ProfileStates.rates)

@dp.message(ProfileStates.rates)
async def handle_rates(message: types.Message, state: FSMContext):
    """Handle rates"""
    data = await state.get_data()
    profile = data.get('profile', {})
    
    if message.text.lower() != 'skip':
        profile['rates'] = message.text
    
    await message.reply("Enter any disclaimer (or send 'skip'):")
    await state.update_data(profile=profile)
    await state.set_state(ProfileStates.disclaimer)

@dp.message(ProfileStates.disclaimer)
async def handle_disclaimer(message: types.Message, state: FSMContext):
    """Handle disclaimer"""
    data = await state.get_data()
    profile = data.get('profile', {})
    
    if message.text.lower() != 'skip':
        profile['disclaimer'] = message.text
    
    profile['images'] = []
    profile['videos'] = []
    
    # Save profile
    user_id = message.from_user.id
    db.save_profile(user_id, profile)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="profile_confirm")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="profile_cancel")],
    ])
    
    preview = f"<b>Profile Preview</b>\n\n"
    preview += f"<b>{profile.get('name', 'N/A')}</b>\n\n"
    preview += f"<b>About:</b> {profile.get('about', 'N/A')}\n\n"
    preview += f"<b>Contact:</b> {profile.get('contact_method', 'N/A')}\n"
    
    await message.reply(preview, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(ProfileStates.preview)

@dp.callback_query(ProfileStates.preview)
async def profile_preview(query: types.CallbackQuery, state: FSMContext):
    """Handle profile preview"""
    await query.answer()
    
    if query.data == "profile_confirm":
        await query.message.edit_text("✅ Profile saved successfully!")
    else:
        await query.message.edit_text("❌ Profile cancelled.")
    
    await state.clear()

@dp.callback_query(F.data == "mark_available")
async def mark_available(query: types.CallbackQuery, state: FSMContext):
    """Mark as available"""
    user_id = query.from_user.id
    
    if len(APPROVED_ADMINS) > 0 and str(user_id) not in APPROVED_ADMINS:
        await query.answer("❌ You must be an approved admin.", show_alert=True)
        return
    
    profile = db.get_profile(user_id)
    if not profile:
        await query.answer("❌ You must create a profile first.", show_alert=True)
        return
    
    await query.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="2 hours", callback_data="duration_2")],
        [InlineKeyboardButton(text="4 hours", callback_data="duration_4")],
        [InlineKeyboardButton(text="6 hours", callback_data="duration_6")],
    ])
    
    await query.message.edit_text(
        "How long will you be available?",
        reply_markup=keyboard
    )
    await state.set_state(ProfileStates.availability_duration)

@dp.callback_query(ProfileStates.availability_duration, F.data.startswith("duration_"))
async def availability_duration(query: types.CallbackQuery, state: FSMContext):
    """Handle availability duration"""
    await query.answer()
    
    duration_hours = int(query.data.replace("duration_", ""))
    user_id = query.from_user.id
    profile = db.get_profile(user_id)
    
    if not profile:
        await query.message.edit_text("❌ Profile not found.")
        return
    
    if not TARGET_GROUP_ID:
        await query.message.edit_text("❌ Target group not configured.")
        return
    
    try:
        # Create listing message
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        listing_text = f"💋 <b>{profile.get('name', 'N/A')}</b> 💋\n\n"
        listing_text += f"📅 Posted: {datetime.now().strftime('%b %d, %I:%M %p')}\n"
        listing_text += f"⏰ Available for: {duration_hours} hours\n\n"
        listing_text += f"<b>Services:</b> {', '.join(profile.get('offer_types', []))}\n\n"
        
        if profile.get('about'):
            listing_text += f"<b>About:</b> {profile['about']}\n\n"
        
        if profile.get('rates'):
            listing_text += f"<b>Rates:</b> {profile['rates']}\n\n"
        
        if profile.get('contact_method') == 'phone':
            listing_text += f"<b>Contact:</b> {profile.get('phone', 'N/A')}\n"
        elif profile.get('contact_method') == 'email':
            listing_text += f"<b>Contact:</b> {profile.get('email', 'N/A')}\n"
        else:
            listing_text += f"<b>Contact:</b> @{profile.get('telegram_username', 'N/A')}\n"
        
        # Send to group
        await bot.send_message(
            chat_id=TARGET_GROUP_ID,
            text=listing_text,
            parse_mode="HTML"
        )
        
        # Create listing record
        db.create_listing(user_id, duration_hours)
        
        await query.message.edit_text(
            f"✅ Your listing has been posted for {duration_hours} hours!"
        )
        
    except Exception as e:
        logger.error(f"Error posting listing: {e}")
        await query.message.edit_text(f"❌ Error: {str(e)}")
    
    await state.clear()

@dp.callback_query(F.data == "delete_profile")
async def delete_profile(query: types.CallbackQuery):
    """Delete profile"""
    user_id = query.from_user.id
    
    if len(APPROVED_ADMINS) > 0 and str(user_id) not in APPROVED_ADMINS:
        await query.answer("❌ You must be an approved admin.", show_alert=True)
        return
    
    await query.answer()
    
    if db.delete_profile(user_id):
        db.delete_listing(user_id)
        await query.message.edit_text("✅ Your profile has been deleted.")
    else:
        await query.message.edit_text("❌ You don't have a profile to delete.")

@dp.message(Command("available"))
async def available_command(message: types.Message):
    """Show available models"""
    active_listings = db.get_active_listings()
    
    if not active_listings:
        await message.reply("📋 No models available right now.")
    else:
        text = "📋 <b>Available Now:</b>\n\n"
        for i, (user_id, listing) in enumerate(active_listings, 1):
            profile = db.get_profile(user_id)
            if profile:
                services = ', '.join(profile.get('offer_types', []))
                time_remaining = listing['expires_at'] - datetime.now()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                
                text += f"{i}. <b>{profile.get('name', 'N/A')}</b>\n"
                text += f"   Services: {services}\n"
                text += f"   Available for: {hours}h {minutes}m\n\n"
        
        await message.reply(text, parse_mode="HTML")

async def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return
    
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
