#!/usr/bin/env python3
"""
Available Now Telegram Bot - Pure Python Implementation
Uses Telegram Bot API directly with requests library
No external framework dependencies - works on any Python 3.13 environment
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TARGET_GROUP_ID = int(os.getenv('TARGET_GROUP_ID', 0)) if os.getenv('TARGET_GROUP_ID') else None
APPROVED_ADMINS = set(os.getenv('APPROVED_ADMINS', '').split(',')) if os.getenv('APPROVED_ADMINS') else set()

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

logger.info(f"Bot configured - Group ID: {TARGET_GROUP_ID}, Admins: {len(APPROVED_ADMINS)}")

# Telegram API base URL
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# In-memory database
class Database:
    def __init__(self):
        self.profiles: Dict[int, Dict[str, Any]] = {}
        self.listings: Dict[int, Dict[str, Any]] = {}
        self.user_states: Dict[int, Dict[str, Any]] = {}
    
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

db = Database()

# Telegram API helpers
def send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None, parse_mode: str = "HTML") -> bool:
    """Send a message via Telegram API"""
    try:
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
        }
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(f"{TELEGRAM_API}/sendMessage", json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def answer_callback(callback_query_id: str, text: str = "", show_alert: bool = False) -> bool:
    """Answer a callback query"""
    try:
        data = {
            'callback_query_id': callback_query_id,
            'text': text,
            'show_alert': show_alert,
        }
        response = requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error answering callback: {e}")
        return False

def edit_message(chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None, parse_mode: str = "HTML") -> bool:
    """Edit a message"""
    try:
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode,
        }
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(f"{TELEGRAM_API}/editMessageText", json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return False

def get_updates(offset: int = 0) -> List[Dict]:
    """Get updates from Telegram"""
    try:
        response = requests.post(f"{TELEGRAM_API}/getUpdates", json={'offset': offset, 'timeout': 30}, timeout=35)
        if response.status_code == 200:
            return response.json().get('result', [])
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
    return []

# Message handlers
def handle_start(user_id: int, chat_id: int, message_id: int) -> None:
    """Handle /start command"""
    if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
        send_message(chat_id, "❌ You are not authorized to use this bot.")
        return
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '📝 Create Profile', 'callback_data': 'create'}],
            [{'text': '🗑️ Delete Profile', 'callback_data': 'delete'}],
            [{'text': '📢 Mark Available', 'callback_data': 'available'}],
        ]
    }
    
    send_message(chat_id, "👋 Welcome to Available Now Bot!\n\nWhat would you like to do?", reply_markup=keyboard)

def handle_available_command(chat_id: int) -> None:
    """Handle /available command in group"""
    listings = db.get_active_listings()
    
    if not listings:
        send_message(chat_id, "📋 No models available right now")
        return
    
    text = "📋 <b>Available Now:</b>\n\n"
    for i, (user_id, listing) in enumerate(listings, 1):
        profile = db.get_profile(user_id)
        if profile:
            text += f"{i}. <b>{profile.get('name', 'N/A')}</b>\n"
            text += f"   Contact: {profile.get('contact', 'N/A')}\n\n"
    
    send_message(chat_id, text)

def handle_callback(callback_id: str, user_id: int, chat_id: int, message_id: int, data: str) -> None:
    """Handle callback queries"""
    answer_callback(callback_id)
    
    if data == "create":
        if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
            answer_callback(callback_id, "❌ Not authorized", show_alert=True)
            return
        
        db.user_states[user_id] = {'step': 'name', 'profile': {}}
        edit_message(chat_id, message_id, "📝 Enter your name or subject line:")
    
    elif data == "delete":
        if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
            answer_callback(callback_id, "❌ Not authorized", show_alert=True)
            return
        
        if db.delete_profile(user_id):
            edit_message(chat_id, message_id, "✅ Profile deleted")
        else:
            edit_message(chat_id, message_id, "❌ No profile found")
    
    elif data == "available":
        if APPROVED_ADMINS and str(user_id) not in APPROVED_ADMINS:
            answer_callback(callback_id, "❌ Not authorized", show_alert=True)
            return
        
        profile = db.get_profile(user_id)
        if not profile:
            answer_callback(callback_id, "❌ Create a profile first", show_alert=True)
            return
        
        keyboard = {
            'inline_keyboard': [
                [{'text': '2 hours', 'callback_data': 'dur_2'}],
                [{'text': '4 hours', 'callback_data': 'dur_4'}],
                [{'text': '6 hours', 'callback_data': 'dur_6'}],
            ]
        }
        edit_message(chat_id, message_id, "How long will you be available?", reply_markup=keyboard)
        db.user_states[user_id] = {'step': 'duration'}
    
    elif data.startswith("dur_"):
        hours = int(data.split("_")[1])
        profile = db.get_profile(user_id)
        
        if not profile or not TARGET_GROUP_ID:
            edit_message(chat_id, message_id, "❌ Error: Profile or group not configured")
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
            send_message(TARGET_GROUP_ID, text)
            
            # Create listing
            db.create_listing(user_id, hours)
            
            edit_message(chat_id, message_id, f"✅ Posted for {hours} hours!")
            
        except Exception as e:
            logger.error(f"Error posting listing: {e}")
            edit_message(chat_id, message_id, f"❌ Error: {str(e)}")

def handle_text(user_id: int, chat_id: int, text: str) -> None:
    """Handle text messages"""
    state = db.user_states.get(user_id, {})
    step = state.get('step')
    
    if step == 'name':
        state['profile']['name'] = text
        state['step'] = 'about'
        send_message(chat_id, "Tell us about yourself:")
    
    elif step == 'about':
        state['profile']['about'] = text
        state['step'] = 'contact'
        keyboard = {
            'inline_keyboard': [
                [{'text': '📞 Phone', 'callback_data': 'contact_phone'}],
                [{'text': '📧 Email', 'callback_data': 'contact_email'}],
                [{'text': '💬 Telegram', 'callback_data': 'contact_telegram'}],
            ]
        }
        send_message(chat_id, "How should people contact you?", reply_markup=keyboard)
    
    elif step == 'contact_input':
        state['profile']['contact'] = text
        state['step'] = 'rates'
        send_message(chat_id, "Enter your rates (or 'skip'):")
    
    elif step == 'rates':
        if text.lower() != 'skip':
            state['profile']['rates'] = text
        
        # Save profile
        db.save_profile(user_id, state['profile'])
        
        keyboard = {
            'inline_keyboard': [
                [{'text': '✅ Confirm', 'callback_data': 'confirm'}],
                [{'text': '❌ Cancel', 'callback_data': 'cancel'}],
            ]
        }
        
        profile = state['profile']
        preview = f"<b>{profile.get('name', 'N/A')}</b>\n\n"
        preview += f"<b>About:</b> {profile.get('about', 'N/A')}\n\n"
        preview += f"<b>Contact:</b> {profile.get('contact', 'N/A')}\n"
        
        send_message(chat_id, preview, reply_markup=keyboard)
        state['step'] = 'preview'
    
    db.user_states[user_id] = state

def handle_callback_contact(callback_id: str, user_id: int, chat_id: int, data: str) -> None:
    """Handle contact method selection"""
    answer_callback(callback_id)
    
    state = db.user_states.get(user_id, {'profile': {}})
    
    if data == 'contact_phone':
        send_message(chat_id, "Enter your phone number:")
        state['step'] = 'contact_input'
    elif data == 'contact_email':
        send_message(chat_id, "Enter your email:")
        state['step'] = 'contact_input'
    elif data == 'contact_telegram':
        state['profile']['contact'] = f"@{data}"  # Placeholder
        state['step'] = 'rates'
        send_message(chat_id, "Enter your rates (or 'skip'):")
    
    db.user_states[user_id] = state

# Main polling loop
def main():
    """Main bot loop"""
    logger.info("Starting bot polling...")
    offset = 0
    
    while True:
        try:
            updates = get_updates(offset)
            
            for update in updates:
                offset = update['update_id'] + 1
                
                # Handle messages
                if 'message' in update:
                    msg = update['message']
                    user_id = msg['from']['id']
                    chat_id = msg['chat']['id']
                    
                    if 'text' in msg:
                        text = msg['text']
                        
                        if text == '/start':
                            handle_start(user_id, chat_id, msg['message_id'])
                        elif text == '/available':
                            handle_available_command(chat_id)
                        else:
                            handle_text(user_id, chat_id, text)
                
                # Handle callback queries
                elif 'callback_query' in update:
                    query = update['callback_query']
                    user_id = query['from']['id']
                    chat_id = query['message']['chat']['id']
                    message_id = query['message']['message_id']
                    data = query['data']
                    callback_id = query['id']
                    
                    if data.startswith('contact_'):
                        handle_callback_contact(callback_id, user_id, chat_id, data)
                    else:
                        handle_callback(callback_id, user_id, chat_id, message_id, data)
            
            time.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
