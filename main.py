#!/usr/bin/env python3
"""
Available Now Telegram Bot - Render Compatible Version
Minimal, production-ready implementation using aiogram
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TARGET_GROUP_ID = int(os.getenv('TARGET_GROUP_ID', 0)) if os.getenv('TARGET_GROUP_ID') else None
APPROVED_ADMINS = set(os.getenv('APPROVED_ADMINS', '').split(',')) if os.getenv('APPROVED_ADMINS') else set()

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

logger.info(f"Bot configured - Group ID: {TARGET_GROUP_ID}, Admins: {len(APPROVED_ADMINS)}")

# States
class ProfileStates(StatesGroup):
    name = State()
    about = State()
    contact = State()
    rates = State()
    preview = State()
    duration = State()

# Simple in-memory database
class Database:
    def __init__(self):
        self.profiles: Dict[int, Dict[str, Any]] = {}
        self.listings: Dict[int, Dict[str, Any]] = {}
    
    def save_profile(self, user_id: int, profile: Dict[str, Any]) -> None:
        self.profiles[user_id] = profile
        logger.info(f"Profile saved for user {user_id}")
    
    def get_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.profiles.get(user_id)
    
    def delete_profile(self, user_id: int) -> bool:
        if user_id in self.profiles:
            del self.profiles[user_id]
            if user_id in self.listings:
                del self.listings[user_id]
            logger.info(f"Profile deleted for user {user_id}")
            return True
        return False
    
    def create_listing(self, user_id: int, hours: int) -> None:
        self.listings[user_id] = {
            'created': datetime.now(),
            'expires': datetime.now() + timedelta(hours=hours),
            'hours': hours
        }
        logger.info(f"Listing created for user {user_id} for {hours} hours")
    
    def get_active_listings(self) -> list:
        now = datetime.now()
        active = []
        expired = []
        
        for user_id, listing in self.listings.items():
            if listing['expires'] > now:
                active.append((user_id, listing))
            else:
                expired.append(user_id)
        
        for user_id in expired:
            del self.listings[user_id]
        
        return active

# Initialize
db = Database()
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Start command"""
    user_id = message.from_user.id
    
    if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
        await message.reply("❌ You are not authorized to use this bot.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Create Profile", callback_data="create")],
        [InlineKeyboardButton(text="🗑️ Delete Profile", callback_data="delete")],
        [InlineKeyboardButton(text="📢 Mark Available", callback_data="available")],
    ])
    
    await message.reply(
        "👋 Welcome to Available Now Bot!\n\nWhat would you like to do?",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "create")
async def create_profile(query: types.CallbackQuery, state: FSMContext) -> None:
    """Start profile creation"""
    user_id = query.from_user.id
    
    if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
        await query.answer("❌ Not authorized", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text("📝 Enter your name or subject line:")
    await state.set_state(ProfileStates.name)
    await state.update_data(profile={})

@dp.message(ProfileStates.name)
async def handle_name(message: types.Message, state: FSMContext) -> None:
    """Handle name input"""
    await state.update_data(profile={'name': message.text})
    await message.reply("Tell us about yourself:")
    await state.set_state(ProfileStates.about)

@dp.message(ProfileStates.about)
async def handle_about(message: types.Message, state: FSMContext) -> None:
    """Handle about input"""
    data = await state.get_data()
    profile = data['profile']
    profile['about'] = message.text
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Phone", callback_data="phone")],
        [InlineKeyboardButton(text="📧 Email", callback_data="email")],
        [InlineKeyboardButton(text="💬 Telegram", callback_data="telegram")],
    ])
    
    await message.reply("How should people contact you?", reply_markup=keyboard)
    await state.update_data(profile=profile)
    await state.set_state(ProfileStates.contact)

@dp.callback_query(ProfileStates.contact)
async def handle_contact(query: types.CallbackQuery, state: FSMContext) -> None:
    """Handle contact method"""
    await query.answer()
    
    data = await state.get_data()
    profile = data['profile']
    method = query.data
    profile['contact_method'] = method
    
    if method == "phone":
        await query.message.edit_text("Enter your phone number:")
        await state.set_state(ProfileStates.rates)
    elif method == "email":
        await query.message.edit_text("Enter your email:")
        await state.set_state(ProfileStates.rates)
    else:
        profile['contact'] = f"@{query.from_user.username or 'unknown'}"
        await query.message.edit_text("Enter your rates (or 'skip'):")
        await state.set_state(ProfileStates.rates)
    
    await state.update_data(profile=profile)

@dp.message(ProfileStates.rates)
async def handle_rates(message: types.Message, state: FSMContext) -> None:
    """Handle rates input"""
    data = await state.get_data()
    profile = data['profile']
    
    if profile['contact_method'] in ['phone', 'email']:
        profile['contact'] = message.text
    else:
        profile['rates'] = message.text if message.text.lower() != 'skip' else 'Not specified'
    
    # Save profile
    user_id = message.from_user.id
    db.save_profile(user_id, profile)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")],
    ])
    
    preview = f"<b>{profile.get('name', 'N/A')}</b>\n\n"
    preview += f"<b>About:</b> {profile.get('about', 'N/A')}\n\n"
    preview += f"<b>Contact:</b> {profile.get('contact', 'N/A')}\n"
    
    await message.reply(preview, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(ProfileStates.preview)

@dp.callback_query(ProfileStates.preview)
async def handle_preview(query: types.CallbackQuery, state: FSMContext) -> None:
    """Handle preview confirmation"""
    await query.answer()
    
    if query.data == "confirm":
        await query.message.edit_text("✅ Profile saved!")
    else:
        await query.message.edit_text("❌ Cancelled")
    
    await state.clear()

@dp.callback_query(F.data == "delete")
async def delete_profile_cmd(query: types.CallbackQuery) -> None:
    """Delete profile"""
    user_id = query.from_user.id
    
    if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
        await query.answer("❌ Not authorized", show_alert=True)
        return
    
    await query.answer()
    
    if db.delete_profile(user_id):
        await query.message.edit_text("✅ Profile deleted")
    else:
        await query.message.edit_text("❌ No profile found")

@dp.callback_query(F.data == "available")
async def mark_available(query: types.CallbackQuery, state: FSMContext) -> None:
    """Mark as available"""
    user_id = query.from_user.id
    
    if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
        await query.answer("❌ Not authorized", show_alert=True)
        return
    
    profile = db.get_profile(user_id)
    if not profile:
        await query.answer("❌ Create a profile first", show_alert=True)
        return
    
    await query.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="2 hours", callback_data="dur_2")],
        [InlineKeyboardButton(text="4 hours", callback_data="dur_4")],
        [InlineKeyboardButton(text="6 hours", callback_data="dur_6")],
    ])
    
    await query.message.edit_text("How long will you be available?", reply_markup=keyboard)
    await state.set_state(ProfileStates.duration)

@dp.callback_query(ProfileStates.duration, F.data.startswith("dur_"))
async def handle_duration(query: types.CallbackQuery, state: FSMContext) -> None:
    """Handle availability duration"""
    await query.answer()
    
    hours = int(query.data.split("_")[1])
    user_id = query.from_user.id
    profile = db.get_profile(user_id)
    
    if not profile or not TARGET_GROUP_ID:
        await query.message.edit_text("❌ Error: Profile or group not configured")
        await state.clear()
        return
    
    try:
        # Create listing message
        text = f"💋 <b>{profile.get('name', 'N/A')}</b> 💋\n\n"
        text += f"📅 Posted: {datetime.now().strftime('%b %d, %I:%M %p')}\n"
        text += f"⏰ Available for: {hours} hours\n\n"
        text += f"<b>About:</b> {profile.get('about', 'N/A')}\n\n"
        text += f"<b>Contact:</b> {profile.get('contact', 'N/A')}\n"
        
        if profile.get('rates'):
            text += f"\n<b>Rates:</b> {profile['rates']}"
        
        # Post to group
        await bot.send_message(
            chat_id=TARGET_GROUP_ID,
            text=text,
            parse_mode="HTML"
        )
        
        # Create listing
        db.create_listing(user_id, hours)
        
        await query.message.edit_text(f"✅ Posted for {hours} hours!")
        
    except Exception as e:
        logger.error(f"Error posting listing: {e}")
        await query.message.edit_text(f"❌ Error: {str(e)}")
    
    await state.clear()

@dp.message(Command("available"))
async def available_list(message: types.Message) -> None:
    """List available models"""
    listings = db.get_active_listings()
    
    if not listings:
        await message.reply("📋 No models available right now")
        return
    
    text = "📋 <b>Available Now:</b>\n\n"
    for i, (user_id, listing) in enumerate(listings, 1):
        profile = db.get_profile(user_id)
        if profile:
            text += f"{i}. <b>{profile.get('name', 'N/A')}</b>\n"
            text += f"   Contact: {profile.get('contact', 'N/A')}\n\n"
    
    await message.reply(text, parse_mode="HTML")

async def main():
    """Start the bot"""
    logger.info("Starting bot...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
