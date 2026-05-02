import json
import os
import datetime
import asyncio
import logging
import requests
import html
import re
import base64
from typing import Dict, List, Optional, Union
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    BotCommand,
    Audio,
    Video
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= CONFIG =================
BOT_TOKEN = "8400631140:AAGD1nuwyEhEuhnDO9V_FvvGTki3XjlRYWk"
ADMIN_ID = 6068463116
BOT_USERNAME = "SynaxLookupBot"

# File paths
USERS_FILE = "users.json"
PAYMENTS_FILE = "payments.json"
COUPONS_FILE = "coupons.json"
CREDIT_COSTS_FILE = "credit_costs.json"
BANNED_USERS_FILE = "banned_users.json"
SETTINGS_FILE = "settings.json"
STATS_FILE = "stats.json"
GROUPS_FILE = "groups.json"

# API Configuration
# Number Search API
NUM_API_URL = "https://ayaanmods.site/number.php?key=annonymous&number="

# TG UserID to Info API
TG_USERID_API_URL = "https://tg2num-owner-api.vercel.app"

# Number to Name API
NUM_NAME_API_URL = "https://abbas-apis.vercel.app/api/num-name"

# PAN Card Search API
PAN_API_URL = "https://www.zephrexdigital.site/api?key=ZEPH-OP08F&type=PAN&term="

# Vehicle Info API
VEHICLE_API_URL = "https://revangevichelinfo.vercel.app/api/rc"

# Pincode API
PINCODE_API_URL = "https://api.postalpincode.in/pincode"

# Payment Configuration
UPI_ID = "SynaxBots@ybl"
PAYMENT_QR_URL = "https://i.ibb.co/nsfk7Vx0/20260112-051110.jpg"

# Images
WELCOME_IMAGE = "https://i.ibb.co/gbhKxbjX/file-00000000458472079c0d45d8f85c8d23.png"
ACCOUNT_IMAGE = "https://i.ibb.co/cSV8Z7Cg/file-0000000028b47208bbbd1c5150d14056.png"
PAYMENT_IMAGE = PAYMENT_QR_URL
INFO_IMAGE = "https://i.ibb.co/B56xdY6f/file-00000000525c71fa8b601089f6bdc213.png"
REFERRAL_IMAGE = "https://i.ibb.co/rGcTz9R2/file-0000000037ac72088f94dd30e9aff061.png"
SEARCH_IMAGE = "https://i.ibb.co/Mk0NLsyV/Picsart-26-01-13-13-13-23-499.jpg"
SEARCH_RESULT_IMAGE = "https://i.ibb.co/Mk0NLsyV/Picsart-26-01-13-13-13-23-499.jpg"
PAN_SEARCH_IMAGE = "https://i.ibb.co/tPpvFMyC/file-0000000084d87209b1f99172467be5f6.png"
PINCODE_SEARCH_IMAGE = "https://i.ibb.co/396ZRbw6/Picsart-26-01-13-13-17-29-807.jpg"
STYLISH_TEXT_IMAGE = "https://i.ibb.co/gFttkZyy/file-000000009f2c7209b00cf7aecaa187a6-1.png"
JOIN_IMAGE = "https://i.ibb.co/sdrfRLJd/file-00000000cb987208926a77979a9c0338.png"
MAINTENANCE_IMAGE = "https://i.ibb.co/twKv01yL/71-Ugwa-C4-Dj-L-AC-UF1000-1000-QL80.jpg"

# Force Join Channels
FORCE_JOIN_CHANNELS = [
    {"id": -1003750507861, "link": "https://t.me/SynaxBotz", "name": "𝘽𝙤𝙩𝙨 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 💚"},
    {"id": -1002682084939, "link": "https://t.me/Synaxchatgroup", "name": "𝘾𝙝𝙖𝙩 𝙂𝙧𝙤𝙪𝙥 💛"}
]

# Conversation states
PAYMENT_PLAN, PAYMENT_SCREENSHOT = range(2)
BROADCAST_TYPE, BROADCAST_CONTENT = range(2)
COUPON_CREATE = range(3)
COUPON_GEN_DETAILS = range(1)
CREDIT_COST_EDIT = range(1)
BAN_USER, BAN_REASON = range(2)
ACTIVATE_GROUP = range(1)

# ================= STYLISH TEXT GENERATOR LOGIC =================
# Font mapping for stylish text
FONT_MAP = {
    "a":"ᴧ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"є","f":"ғ","g":"ɢ","h":"ʜ","i":"ɪ",
    "j":"ᴊ","k":"ᴋ","l":"ʟ","m":"ϻ","n":"η","o":"σ","p":"ᴘ","q":"ǫ","r":"ꝛ",
    "s":"s","t":"ᴛ","u":"υ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ",
    
    "A":"𝐀‌","B":"𝐁‌","C":"𝐂‌","D":"𝐃‌","E":"𝐄‌","F":"𝐅‌","G":"𝐆‌",
    "H":"𝐇‌","I":"𝐈‌","J":"𝐉‌","K":"𝐊‌","L":"𝐋‌","M":"𝐌‌","N":"𝐍‌",
    "O":"𝐎‌","P":"𝐏‌","Q":"𝐐‌","R":"𝐑‌","S":"𝐒‌","T":"𝐓‌","U":"𝐔‌",
    "V":"𝐕‌","W":"𝐖‌","X":"𝐗‌","Y":"𝐘‌","Z":"𝐙‌",
}

# List of style pairs (prefix, suffix)
STYLES = [
    ("𓂃❛ ⟶", "❜ 🌙⤹🌸"),
    ("❍⏤●", "●───♫▷"),
    ("🤍 ⍣⃪ ᶦ ᵃᵐ⛦⃕", "❛𝆺𝅥⤹࿗𓆪ꪾ™"),
    ("𓆰𝅃🔥", "⃪⍣꯭꯭𓆪꯭🝐"),
    ("◄❥❥⃝⃪⃕🦚⟵᷽᷍", "˚◡⃝🐬᪳𔘓❁❍•:➛"),
    ("➺꯭꯭꯭𝅥𝆬🦋⃪꯭─⃛┼", "🥵⃝⃝ᬽ⃪꯭꯭➺꯭⎯⎯᪵᪳"),
    ("◄⏤🝛꯭𝐈𝛕ᷟ𝚣⃪ꙴ🥀⃝⃪", "⃝☠⎯꯭𓆩♡꧂"),
    ("🦋⃟≛⃝⋆⋆≛⃞", "𝄟🦋⃟≛⃝≛"),
    ("𐏓𓆩❤🔥𓆪𝆺꯭𝅥༎ࠫ⛧", "ࠫ༎𝆺𝅥𓆩⍣꯭⃟🍷༎᪵⛧"),
    ("𓄂𝆺𝅥⃝🥀⃪⃪꯭ᷟ⃜𖥫꯭꯭꯭𝆺꯭꯭𝅥", "𝆺꯭𝅥🎭🌹꯭"),
    ("𓄂─⃛𓆩🫧𝆺𝅥⃝𐏓", "㋛𓆪꯭⵿٭🍃"),
    ("◄⏤⃪⃝⃪𐏓🝛꯭", "⸙ꠋꠋꠋꠋꠋ⛦⃪⃪🝛꯭••➤"),
    ("🎡𓆩᪵🌸⃝۫𝞄⃕𝖋𝖋꯭ᜊ𝆺𝅥⃝", "┼⃖ꭗ🦋¦🌺--🎋"),
    ("⛦⃕𝄟•๋๋๋๋๋๋๋๋๋๋๋๋๋๋๋🦋⃟⃟⃟≛⃝💖", "🦋•๋๋๋๋๋๋๋๋๋๋๋๋๋๋๋𝄟"),
    ("••ᯓ❥๋๋๋๋๋๋๋๋๋๋๋๋๋๋ꗝ༎꯭ࠫ🤍𝆺꯭𝅥", "𝆺꯭𝅥༎ࠫ◡⃝𑲭"),
    ("𝐈𝛕ᷟ𝚣⃪ꙴ⋆†།┼⃖•🔥⃞⃪⃜", "🔥⃞⃪⃜𓆪🦋✿"),
    ("❍─⃜𓆩〭⃛〬🤍𓆪˹", ".⍣⃪ꭗ𝆺𝅥𔘓🪽"),
    ("𝆺𝅥اـ꯭ـ꯭𝞂⃕𝝲𝝴꯭•⚚•𝆺꯭𝅥", "𝆺꯭𝅥ꀭ‧₊𝁾⟶🍃˚"),
    ("◄⏤🔥⃝⃪🐼𓆩꯭❛", "❜꯭𓆪⎯⟶"),
    ("❍─⃜𓆩〭⃛〬👒𓆪⃪꯭", "🤍᪳𝆺꯭𝅥⎯⎯"),
    ("◄⏤❥≛⃝", "🍁⃝➤🕊⃝🝐"),
    ("°ꗝؖ༎꯭ࠫᜊ𝆺꯭𝅥🔥⃝❥༎ࠫ𝆺꯭𝅥", "༎ࠫ٭⃪꯭꯭⃜ꬑ�"),
    ("◄⏤🫧⃝⃪🦋꯭", "◡⃝ا۬🌸᪳𝆺꯭𝅥⎯꯭"),
    ("◄ᯓ❥≛⃝🌸꯭", "💗⃝꯭꯭❥꯭꯭✿꯭꯭࿐"),
]

def convert_to_stylish(text: str) -> str:
    """Convert text to stylish font using FONT_MAP"""
    return "".join(FONT_MAP.get(ch, ch) for ch in text)

# ==========================================

# ================= DATA HANDLERS =================
def load_json_file(filename: str) -> dict:
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
    return {}

def save_json_file(filename: str, data: dict) -> bool:
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

def load_users() -> dict:
    return load_json_file(USERS_FILE)

def save_users(data: dict) -> bool:
    return save_json_file(USERS_FILE, data)

def load_payments() -> dict:
    return load_json_file(PAYMENTS_FILE)

def save_payments(data: dict) -> bool:
    return save_json_file(PAYMENTS_FILE, data)

def load_coupons() -> dict:
    return load_json_file(COUPONS_FILE)

def save_coupons(data: dict) -> bool:
    return save_json_file(COUPONS_FILE, data)

def load_credit_costs() -> dict:
    costs = load_json_file(CREDIT_COSTS_FILE)
    if not costs:
        costs = {
            "number_search": 1,
            "tg_userid_search": 2,
            "num_name_search": 1,
            "pan_search": 2,
            "vehicle_search": 5,
            "pincode_search": 1,
            "stylish_text": 1,
        }
        save_credit_costs(costs)
    return costs

def save_credit_costs(data: dict) -> bool:
    return save_json_file(CREDIT_COSTS_FILE, data)

def get_credit_cost(feature: str) -> int:
    costs = load_credit_costs()
    return costs.get(feature, 1)

def load_banned_users() -> dict:
    return load_json_file(BANNED_USERS_FILE)

def save_banned_users(data: dict) -> bool:
    return save_json_file(BANNED_USERS_FILE, data)

def load_settings() -> dict:
    settings = load_json_file(SETTINGS_FILE)
    if not settings:
        settings = {
            "maintenance_mode": False,
            "maintenance_message": "🔧 Bot is under maintenance. Please try again later.",
            "broadcast_message": None,
            "broadcast_sent": False
        }
        save_settings(settings)
    return settings

def save_settings(data: dict) -> bool:
    return save_json_file(SETTINGS_FILE, data)

def load_stats() -> dict:
    stats = load_json_file(STATS_FILE)
    if not stats:
        stats = {
            "total_searches": {
                "number_search": 0,
                "tg_userid_search": 0,
                "num_name_search": 0,
                "pan_search": 0,
                "vehicle_search": 0,
                "pincode_search": 0,
                "stylish_text": 0,
            },
            "daily_searches": {},
            "monthly_searches": {},
            "total_revenue": 0,
            "credits_spent": 0,
            "premium_purchases": 0,
            "coupon_redemptions": 0
        }
        save_stats(stats)
    return stats

def save_stats(data: dict) -> bool:
    return save_json_file(STATS_FILE, data)

def update_search_stats(feature: str, credits_used: int = 0):
    try:
        stats = load_stats()
        if feature not in stats["total_searches"]:
            stats["total_searches"][feature] = 0
        stats["total_searches"][feature] += 1
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today not in stats["daily_searches"]:
            stats["daily_searches"][today] = {}
        if feature not in stats["daily_searches"][today]:
            stats["daily_searches"][today][feature] = 0
        stats["daily_searches"][today][feature] += 1
        
        this_month = datetime.datetime.now().strftime("%Y-%m")
        if this_month not in stats["monthly_searches"]:
            stats["monthly_searches"][this_month] = {}
        if feature not in stats["monthly_searches"][this_month]:
            stats["monthly_searches"][this_month][feature] = 0
        stats["monthly_searches"][this_month][feature] += 1
        
        stats["credits_spent"] += credits_used
        stats["total_revenue"] += credits_used * 0.1
        
        save_stats(stats)
    except Exception as e:
        logger.error(f"Error updating search stats: {e}")

def update_payment_stats(plan_type: str, amount: int):
    try:
        stats = load_stats()
        if plan_type == "premium":
            stats["premium_purchases"] += 1
            stats["total_revenue"] += amount * 2
        else:
            stats["total_revenue"] += amount * 0.1
        save_stats(stats)
    except Exception as e:
        logger.error(f"Error updating payment stats: {e}")

def update_coupon_stats():
    try:
        stats = load_stats()
        stats["coupon_redemptions"] += 1
        save_stats(stats)
    except Exception as e:
        logger.error(f"Error updating coupon stats: {e}")

# ==========================================

# ================= GROUP MANAGEMENT =================
def load_groups() -> dict:
    return load_json_file(GROUPS_FILE)

def save_groups(data: dict) -> bool:
    return save_json_file(GROUPS_FILE, data)

def is_group_active(group_id: str) -> bool:
    groups = load_groups()
    return groups.get(group_id, {}).get("active", False)

def activate_group(group_id: str, admin_id: str) -> bool:
    try:
        groups = load_groups()
        if group_id not in groups:
            groups[group_id] = {}
        groups[group_id]["active"] = True
        groups[group_id]["admin_id"] = admin_id
        groups[group_id]["activated_at"] = datetime.datetime.now().isoformat()
        return save_groups(groups)
    except Exception as e:
        logger.error(f"Error activating group: {e}")
        return False

def deactivate_group(group_id: str) -> bool:
    try:
        groups = load_groups()
        if group_id in groups:
            groups[group_id]["active"] = False
            return save_groups(groups)
        return False
    except Exception as e:
        logger.error(f"Error deactivating group: {e}")
        return False

# ==========================================

# ================= USER MANAGEMENT =================
def get_user(user_id: str) -> dict:
    users = load_users()
    if user_id not in users:
        users[user_id] = {
            "balance": 5,
            "premium": False,
            "premium_expiry": None,
            "referrals": 0,
            "referral_earnings": 0,
            "referred_by": None,
            "joined_at": datetime.datetime.now().isoformat()
        }
        save_users(users)
    return users[user_id]

def update_user(user_id: str, data: dict) -> bool:
    users = load_users()
    if user_id in users:
        users[user_id].update(data)
        return save_users(users)
    return False

def add_credits(user_id: str, amount: int) -> bool:
    try:
        user = get_user(user_id)
        user["balance"] += amount
        return update_user(user_id, user)
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        return False

def remove_credits(user_id: str, amount: int) -> bool:
    try:
        user = get_user(user_id)
        user["balance"] = max(0, user["balance"] - amount)
        return update_user(user_id, user)
    except Exception as e:
        logger.error(f"Error removing credits: {e}")
        return False

def add_premium(user_id: str, days: int) -> bool:
    try:
        user = get_user(user_id)
        current_expiry = None
        if user["premium_expiry"]:
            try:
                current_expiry = datetime.datetime.fromisoformat(user["premium_expiry"])
            except:
                pass
        
        if current_expiry and current_expiry > datetime.datetime.now():
            new_expiry = current_expiry + datetime.timedelta(days=days)
        else:
            new_expiry = datetime.datetime.now() + datetime.timedelta(days=days)
        
        user["premium"] = True
        user["premium_expiry"] = new_expiry.isoformat()
        return update_user(user_id, user)
    except Exception as e:
        logger.error(f"Error adding premium: {e}")
        return False

def remove_premium(user_id: str) -> bool:
    try:
        user = get_user(user_id)
        user["premium"] = False
        user["premium_expiry"] = None
        return update_user(user_id, user)
    except Exception as e:
        logger.error(f"Error removing premium: {e}")
        return False

def is_premium_user(user_id: str) -> bool:
    try:
        user = get_user(user_id)
        if not user.get("premium", False):
            return False
        if user.get("premium_expiry"):
            try:
                expiry = datetime.datetime.fromisoformat(user["premium_expiry"])
                if expiry < datetime.datetime.now():
                    user["premium"] = False
                    user["premium_expiry"] = None
                    update_user(user_id, user)
                    return False
                return True
            except:
                return False
        return True
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return False

# ==========================================

# ================= BAN SYSTEM =================
def is_user_banned(user_id: str) -> bool:
    try:
        banned_users = load_banned_users()
        return user_id in banned_users
    except Exception as e:
        logger.error(f"Error checking ban status: {e}")
        return False

def ban_user(user_id: str, reason: str = "No reason provided") -> bool:
    try:
        banned_users = load_banned_users()
        banned_users[user_id] = {
            "reason": reason,
            "banned_at": datetime.datetime.now().isoformat()
        }
        return save_banned_users(banned_users)
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        return False

def unban_user(user_id: str) -> bool:
    try:
        banned_users = load_banned_users()
        if user_id in banned_users:
            del banned_users[user_id]
            return save_banned_users(banned_users)
        return False
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        return False

def get_ban_info(user_id: str) -> Optional[dict]:
    try:
        banned_users = load_banned_users()
        return banned_users.get(user_id)
    except Exception as e:
        logger.error(f"Error getting ban info: {e}")
        return None

# ==========================================

# ================= MAINTENANCE SYSTEM =================
def is_maintenance_mode() -> bool:
    try:
        settings = load_settings()
        return settings.get("maintenance_mode", False)
    except Exception as e:
        logger.error(f"Error checking maintenance mode: {e}")
        return False

def set_maintenance_mode(enabled: bool, message: str = None) -> bool:
    try:
        settings = load_settings()
        settings["maintenance_mode"] = enabled
        if message:
            settings["maintenance_message"] = message
        return save_settings(settings)
    except Exception as e:
        logger.error(f"Error setting maintenance mode: {e}")
        return False

def get_maintenance_message() -> str:
    try:
        settings = load_settings()
        return settings.get("maintenance_message", "🔧 Bot is under maintenance. Please try again later.")
    except Exception as e:
        logger.error(f"Error getting maintenance message: {e}")
        return "🔧 Bot is under maintenance. Please try again later."

# ==========================================

# ================= CHANNEL MANAGEMENT =================
def get_required_channels() -> List[dict]:
    return FORCE_JOIN_CHANNELS

async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    required_channels = get_required_channels()
    if not required_channels:
        return True
    for channel in required_channels:
        try:
            member = await context.bot.get_chat_member(channel["id"], user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except TelegramError as e:
            logger.error(f"Error checking channel membership: {e}")
            return False
    return True

async def send_force_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    required_channels = get_required_channels()
    if not required_channels:
        return True
    
    not_joined = []
    for channel in required_channels:
        try:
            member = await context.bot.get_chat_member(channel["id"], update.effective_user.id)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except TelegramError as e:
            logger.error(f"Error checking channel membership: {e}")
            not_joined.append(channel)
    
    if not not_joined:
        await show_main_menu(update, context)
        return True
    
    keyboard = []
    for channel in not_joined:
        keyboard.append([InlineKeyboardButton(f"📢 {channel['name']}", url=channel["link"])])
    
    keyboard.append([InlineKeyboardButton("✅ I've Joined All Channels", callback_data="check_joined")])
    keyboard.append([InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_join_status")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    joined_count = len(required_channels) - len(not_joined)
    total_count = len(required_channels)
    
    await update.message.reply_photo(
        photo=JOIN_IMAGE,
        caption=(
            f"⚠️ *Mandatory Channels Required*\n\n"
            f"📊 Progress: {joined_count}/{total_count} channels joined\n\n"
            f"Please join all channels below to use the bot:\n\n"
            f"⚡ *Channels not joined:* {len(not_joined)}\n"
            f"✅ *Channels joined:* {joined_count}"
        ),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return False

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)
    
    # Clear service states
    for key in list(context.user_data.keys()):
        if key.startswith("awaiting_"):
            del context.user_data[key]
    
    # Main Menu
    keyboard = [
        [InlineKeyboardButton("💳 Buy Credits", callback_data="buy_credits"), InlineKeyboardButton("👑 Buy Premium", callback_data="buy_premium")],
        [InlineKeyboardButton("👤 My Account", callback_data="my_account")],
        [InlineKeyboardButton("🔗 Referral", callback_data="referral"), InlineKeyboardButton("🎫 Coupon Code", callback_data="coupon")],
        [InlineKeyboardButton("🔍 Search Number", callback_data="search_number")],
        [InlineKeyboardButton("🆔 TG UserID to Info", callback_data="tg_userid_search")],
        [InlineKeyboardButton("📞 Num to Name", callback_data="num_name_search")],
        [InlineKeyboardButton("🆔 PAN Card Info", callback_data="pan_search")],
        [InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle_search")],
        [InlineKeyboardButton("📍 Pincode Search", callback_data="pincode_search")],
        [InlineKeyboardButton("✨ Stylish Text", callback_data="stylish_text")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    premium_status = "✅ Active" if is_premium_user(user_id) else "❌ Inactive"
    
    if update.message:
        await update.message.reply_photo(
            photo=WELCOME_IMAGE,
            caption=(
                f"*👋 Welcome to Synax Osnit*\n\n"
                f"Powerful OSINT bot for Mobile, TG UserID, Name, PAN, Vehicle, Pincode & Stylish Text.\n\n"
                f"⚡ Fast • Secure • Easy to Use\n"
                f"— Made by @synaxnetwork —\n\n"
                f"👤 *User:* {update.effective_user.first_name}\n"
                f"💰 *Credits:* {user.get('balance', 0)}\n"
                f"👑 *Premium:* {premium_status}\n\n"
                f"Choose an option below:"
            ),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        query = update.callback_query
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=WELCOME_IMAGE,
                    caption=(
                        f"*👋 Welcome to Synax Osnit*\n\n"
                        f"Powerful OSINT bot for Mobile, TG UserID, Name, PAN, Vehicle, Pincode & Stylish Text.\n\n"
                        f"⚡ Fast • Secure • Easy to Use\n"
                        f"— Made by @synaxnetwork —\n\n"
                        f"👤 *User:* {query.from_user.first_name}\n"
                        f"💰 *Credits:* {user.get('balance', 0)}\n"
                        f"👑 *Premium:* {premium_status}\n\n"
                        f"Choose an option below:"
                    ),
                    parse_mode="Markdown"
                ),
                reply_markup=reply_markup
            )
        except:
            await context.bot.send_photo(
                chat_id=query.from_user.id,
                photo=WELCOME_IMAGE,
                caption=(
                    f"*👋 Welcome to Synax Osnit*\n\n"
                    f"Powerful OSINT bot for Mobile, TG UserID, Name, PAN, Vehicle, Pincode & Stylish Text.\n\n"
                    f"⚡ Fast • Secure • Easy to Use\n"
                    f"— Made by @synaxnetwork —\n\n"
                    f"👤 *User:* {query.from_user.first_name}\n"
                    f"💰 *Credits:* {user.get('balance', 0)}\n"
                    f"👑 *Premium:* {premium_status}\n\n"
                    f"Choose an option below:"
                ),
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

# ==========================================

# ================= REFERRAL SYSTEM =================
def process_referral(user_id: str, referrer_id: str) -> bool:
    try:
        users = load_users()
        bonus_credits = 3
        if user_id in users and referrer_id in users:
            if not users[user_id].get("referred_by"):
                users[user_id]["referred_by"] = referrer_id
                users[referrer_id]["referrals"] = users[referrer_id].get("referrals", 0) + 1
                users[referrer_id]["referral_earnings"] = users[referrer_id].get("referral_earnings", 0) + bonus_credits
                users[referrer_id]["balance"] = users[referrer_id].get("balance", 0) + bonus_credits
                save_users(users)
                return True
        return False
    except Exception as e:
        logger.error(f"Error processing referral: {e}")
        return False

def get_referral_link(user_id: str) -> str:
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"

# ==========================================

# ================= COUPON SYSTEM =================
def create_coupon(code: str, reward_type: str, reward_value: int, max_uses: int, expiry_days: int) -> bool:
    try:
        coupons = load_coupons()
        if "coupons" not in coupons:
            coupons["coupons"] = {}
        expiry_date = (datetime.datetime.now() + datetime.timedelta(days=expiry_days)).isoformat()
        coupons["coupons"][code] = {
            "reward_type": reward_type,
            "reward_value": reward_value,
            "max_uses": max_uses,
            "used": 0,
            "expiry": expiry_date,
            "created_at": datetime.datetime.now().isoformat(),
            "used_by": []
        }
        return save_coupons(coupons)
    except Exception as e:
        logger.error(f"Error creating coupon: {e}")
        return False

def validate_coupon(code: str) -> Optional[dict]:
    try:
        coupons = load_coupons()
        if "coupons" not in coupons or code not in coupons["coupons"]:
            return None
        coupon = coupons["coupons"][code]
        try:
            expiry = datetime.datetime.fromisoformat(coupon["expiry"])
            if expiry < datetime.datetime.now():
                return None
        except:
            return None
        if coupon["used"] >= coupon["max_uses"]:
            return None
        return coupon
    except Exception as e:
        logger.error(f"Error validating coupon: {e}")
        return None

def use_coupon(code: str, user_id: str) -> bool:
    try:
        coupons = load_coupons()
        if "coupons" not in coupons or code not in coupons["coupons"]:
            return False
        coupon = coupons["coupons"][code]
        if user_id in coupon.get("used_by", []):
            return False
        if coupon["reward_type"] == "credits":
            add_credits(user_id, coupon["reward_value"])
        elif coupon["reward_type"] == "premium":
            add_premium(user_id, coupon["reward_value"])
        coupon["used"] += 1
        coupon["used_by"].append(user_id)
        update_coupon_stats()
        return save_coupons(coupons)
    except Exception as e:
        logger.error(f"Error using coupon: {e}")
        return False

def generate_coupon_code(length=8):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_coupon_stats() -> dict:
    try:
        coupons = load_coupons()
        stats = {"total": 0, "active": 0, "expired": 0, "used": 0, "unused": 0}
        current_time = datetime.datetime.now()
        for code, coupon in coupons.get("coupons", {}).items():
            stats["total"] += 1
            try:
                expiry = datetime.datetime.fromisoformat(coupon["expiry"])
                if expiry < current_time:
                    stats["expired"] += 1
                else:
                    stats["active"] += 1
            except:
                stats["expired"] += 1
            if coupon["used"] > 0:
                stats["used"] += 1
            else:
                stats["unused"] += 1
        return stats
    except Exception as e:
        logger.error(f"Error getting coupon stats: {e}")
        return {"total": 0, "active": 0, "expired": 0, "used": 0, "unused": 0}

# ==========================================

# ================= PAYMENT SYSTEM =================
def create_payment_request(user_id: str, plan_type: str, plan_details: dict) -> str:
    try:
        payments = load_payments()
        if "payments" not in payments:
            payments["payments"] = {}
        payment_id = f"pay_{user_id}_{int(datetime.datetime.now().timestamp())}"
        payments["payments"][payment_id] = {
            "user_id": user_id,
            "plan_type": plan_type,
            "plan_details": plan_details,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }
        save_payments(payments)
        return payment_id
    except Exception as e:
        logger.error(f"Error creating payment request: {e}")
        return ""

def get_payment(payment_id: str) -> Optional[dict]:
    try:
        payments = load_payments()
        return payments.get("payments", {}).get(payment_id)
    except Exception as e:
        logger.error(f"Error getting payment: {e}")
        return None

def update_payment(payment_id: str, status: str, **kwargs) -> bool:
    try:
        payments = load_payments()
        if "payments" in payments and payment_id in payments["payments"]:
            payments["payments"][payment_id]["status"] = status
            payments["payments"][payment_id].update(kwargs)
            return save_payments(payments)
        return False
    except Exception as e:
        logger.error(f"Error updating payment: {e}")
        return False

# ==========================================

# ================= ADMIN HELPER =================
def get_admin_keyboard():
    settings = load_settings()
    maintenance_status = "🔴 ON" if settings.get("maintenance_mode", False) else "🟢 OFF"
    return [
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("➕ Add Credits", callback_data="admin_add_credits")],
        [InlineKeyboardButton("➖ Remove Credits", callback_data="admin_remove_credits")],
        [InlineKeyboardButton("👑 Add Premium", callback_data="admin_add_premium")],
        [InlineKeyboardButton("❌ Remove Premium", callback_data="admin_remove_premium")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎫 Create Coupon", callback_data="admin_create_coupon")],
        [InlineKeyboardButton("🎟️ Generate Coupon", callback_data="admin_generate_coupon")],
        [InlineKeyboardButton("📊 Coupon Stats", callback_data="admin_coupon_stats")],
        [InlineKeyboardButton("💰 Credit Costs", callback_data="admin_credit_costs")],
        [InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban_user")],
        [InlineKeyboardButton("✅ Unban User", callback_data="admin_unban_user")],
        [InlineKeyboardButton(f"🔧 Maintenance: {maintenance_status}", callback_data="admin_maintenance")],
        [InlineKeyboardButton("🏢 Group Management", callback_data="admin_groups")]
    ]

# ==========================================

# ================= COMMAND HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if is_user_banned(user_id):
        ban_info = get_ban_info(user_id)
        await update.message.reply_photo(
            photo=INFO_IMAGE,
            caption=f"❌ *You are banned from using this bot*\n\nReason: {ban_info.get('reason', 'No reason provided')}",
            parse_mode="Markdown"
        )
        return
    
    if is_maintenance_mode() and update.effective_user.id != ADMIN_ID:
        await update.message.reply_photo(
            photo=MAINTENANCE_IMAGE,
            caption=get_maintenance_message(),
            parse_mode="Markdown"
        )
        return
    
    args = context.args
    if args and args[0].isdigit():
        referrer_id = args[0]
        if referrer_id != user_id:
            if process_referral(user_id, referrer_id):
                await update.message.reply_text("🎉 Referral bonus added to your account!")
    
    get_user(user_id)
    
    if not await check_channel_membership(update.effective_user.id, context):
        await send_force_join_message(update, context)
        return
    
    await show_main_menu(update, context)

async def show_admin_menu(query, context):
    keyboard = get_admin_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "*🛠️ Admin Panel*\n\nSelect an action:"
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    except:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if "admin_action" in context.user_data:
        del context.user_data["admin_action"]
        
    keyboard = get_admin_keyboard()
    await update.message.reply_text(
        "*🛠️ Admin Panel*\n\nSelect an action:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def addcredit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        amount = int(context.args[1])
        if add_credits(user_id, amount):
            await update.message.reply_text(f"✅ Added {amount} credits to user {user_id}")
        else:
            await update.message.reply_text("❌ Failed to add credits")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /addcredit USERID AMOUNT")

async def removecredit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        amount = int(context.args[1])
        if remove_credits(user_id, amount):
            await update.message.reply_text(f"✅ Removed {amount} credits from user {user_id}")
        else:
            await update.message.reply_text("❌ Failed to remove credits")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /removecredit USERID AMOUNT")

async def addpremium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        days = int(context.args[1])
        if add_premium(user_id, days):
            await update.message.reply_text(f"✅ Added {days} days premium to user {user_id}")
        else:
            await update.message.reply_text("❌ Failed to add premium")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /addpremium USERID DAYS")

async def removepremium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        if remove_premium(user_id):
            await update.message.reply_text(f"✅ Removed premium from user {user_id}")
        else:
            await update.message.reply_text("❌ Failed to remove premium")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /removepremium USERID")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        if ban_user(user_id, reason):
            await update.message.reply_text(f"✅ User {user_id} has been banned\nReason: {reason}")
            try:
                await context.bot.send_message(chat_id=user_id, text=f"❌ You have been banned from using this bot\nReason: {reason}")
            except:
                pass
        else:
            await update.message.reply_text("❌ Failed to ban user")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /ban USERID [reason]")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        if unban_user(user_id):
            await update.message.reply_text(f"✅ User {user_id} has been unbanned")
            try:
                await context.bot.send_message(chat_id=user_id, text="✅ You have been unbanned and can now use the bot again")
            except:
                pass
        else:
            await update.message.reply_text("❌ Failed to unban user or user was not banned")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /unban USERID")

async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) == 0:
        status = "ON" if is_maintenance_mode() else "OFF"
        await update.message.reply_text(f"🔧 Maintenance mode is currently: {status}")
        return
    
    action = context.args[0].lower()
    message = " ".join(context.args[1:]) if len(context.args) > 1 else None
    
    if action == "on":
        if set_maintenance_mode(True, message):
            await update.message.reply_text("✅ Maintenance mode has been enabled")
        else:
            await update.message.reply_text("❌ Failed to enable maintenance mode")
    elif action == "off":
        if set_maintenance_mode(False):
            await update.message.reply_text("✅ Maintenance mode has been disabled")
        else:
            await update.message.reply_text("❌ Failed to disable maintenance mode")
    else:
        await update.message.reply_text("Usage: /maintenance on [message] OR /maintenance off")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    stats_text = await get_comprehensive_stats()
    if len(stats_text) > 4000:
        parts = [stats_text[i:i+4000] for i in range(0, len(stats_text), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode="Markdown")
    else:
        await update.message.reply_text(stats_text, parse_mode="Markdown")

async def get_comprehensive_stats() -> str:
    try:
        users = load_users()
        stats = load_stats()
        payments = load_payments()
        coupons = load_coupons()
        banned_users = load_banned_users()
        groups = load_groups()
        
        total_users = len(users)
        premium_users = sum(1 for u in users.values() if is_premium_user(u))
        total_credits = sum(u.get("balance", 0) for u in users.values())
        total_banned = len(banned_users)
        
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        today_searches = 0
        if today_str in stats.get("daily_searches", {}):
            today_searches = sum(stats["daily_searches"][today_str].values())
        
        stats_text = (
            f"*📊 BOT STATISTICS*\n\n"
            f"👥 Total Users: {total_users}\n"
            f"👑 Premium Users: {premium_users}\n"
            f"💳 Total Credits: {total_credits}\n"
            f"🚫 Banned Users: {total_banned}\n"
            f"🔍 Today's Searches: {today_searches}\n"
            f"🏢 Active Groups: {sum(1 for g in groups.values() if g.get('active', False))}\n\n"
            f"⚡ Powered by @synaxnetwork"
        )
        return stats_text
    except Exception as e:
        logger.error(f"Error getting comprehensive stats: {e}")
        return f"❌ Error loading statistics: {str(e)}"

# ==========================================

# ================= GROUP COMMAND HANDLERS =================
async def activate_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command can only be used in groups.")
        return
    
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    
    if user_id != str(ADMIN_ID):
        await update.message.reply_text("❌ Only the bot admin can activate groups.")
        return
    
    if activate_group(chat_id, user_id):
        await update.message.reply_text(
            "✅ *Group Activated Successfully*\n\n"
            "Bot commands will now work in this group.\n\n"
            "Available commands:\n"
            "/number - Search mobile number\n"
            "/tguserid - TG UserID to Info\n"
            "/numname - Number to Name\n"
            "/pan - PAN Card Info\n"
            "/vehicle - Vehicle Info\n"
            "/pincode - Pincode Search\n"
            "/stylish - Stylish Text Generator\n\n"
            "Made by @synaxnetwork",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Failed to activate group. Please try again.")

async def deactivate_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command can only be used in groups.")
        return
    
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    
    if user_id != str(ADMIN_ID):
        await update.message.reply_text("❌ Only the bot admin can deactivate groups.")
        return
    
    if deactivate_group(chat_id):
        await update.message.reply_text(
            "✅ *Group Deactivated Successfully*\n\n"
            "Bot commands will no longer work in this group.\n\n"
            "Made by @synaxnetwork",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Failed to deactivate group. Please try again.")

async def number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(update.effective_chat.id)
    if not is_group_active(chat_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a mobile number.\n\nUsage: /number 9876543210", parse_mode="Markdown")
        return
    
    number = context.args[0]
    if not number.isdigit() or len(number) != 10:
        await update.message.reply_text("❌ Invalid number! Please send a 10-digit mobile number.", parse_mode="Markdown")
        return
    
    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{NUM_API_URL}{number}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("result") and isinstance(data.get("result"), list):
                records = data.get("result", [])
                
                if not records:
                    await update.message.reply_text("❌ No record found!")
                    return

                result_text = f"✅ *Search Result for* `{number}`\n\n"
                
                for i, item in enumerate(records):
                    name = item.get("name", "N/A")
                    father_name = item.get("father_name", "N/A")
                    address = item.get("address", "N/A")
                    mobile = item.get("mobile", "N/A")
                    circle = item.get("circle", "N/A")
                    alt_num = item.get("alternate", "N/A")
                    email = item.get("email", "N/A")
                    uid = item.get("id", "N/A")
                    
                    result_text += (
                        f"━━━━━━━━━━━━━━━\n"
                        f"📋 *Record {i+1}*\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"👤 Name: {name}\n"
                        f"👨 Father: {father_name}\n"
                        f"🏠 Address: {address}\n"
                        f"📞 Mobile: {mobile}\n"
                        f"📡 Circle: {circle}\n"
                        f"📞 Alt Number: {alt_num}\n"
                        f"📧 Email: {email}\n"
                        f"🆔 ID: `{uid}`\n\n"
                    )
                
                result_text += "🏢 *Group Active - Unlimited Searches*"
                await update.message.reply_text(result_text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ No record found!")
        else:
            await update.message.reply_text("❌ API error!")
            
    except Exception as e:
        await update.message.reply_text("❌ Search failed!")
        logger.error(f"Group search error: {e}")

async def tg_userid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(update.effective_chat.id)
    if not is_group_active(chat_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a Telegram User ID.\n\nUsage: /tguserid 6931300801", parse_mode="Markdown")
        return
    
    tg_id = context.args[0]
    if not tg_id.isdigit():
        await update.message.reply_text("❌ Invalid ID! Please send a valid numeric Telegram User ID.", parse_mode="Markdown")
        return
    
    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{TG_USERID_API_URL}?userid={tg_id}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                result_data = data.get("data", {})
                if result_data.get("found"):
                    number = result_data.get("number", "N/A")
                    country = result_data.get("country", "N/A")
                    cc = result_data.get("country_code", "N/A")
                    searched_id = data.get("searched_userid", tg_id)

                    result_text = (
                        f"✅ *TG UserID Info*\n\n"
                        f"🆔 *User ID:* `{searched_id}`\n"
                        f"🌍 *Country:* {country}\n"
                        f"📞 *Country Code:* {cc}\n"
                        f"📱 *Number:* `{number}`\n\n"
                        f"🏢 *Group Active - Unlimited Searches*"
                    )
                    await update.message.reply_text(result_text, parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ No details found for this User ID!")
            else:
                await update.message.reply_text("❌ API Error or Invalid User ID!")
        else:
            await update.message.reply_text("❌ API Error!")
            
    except Exception as e:
        await update.message.reply_text("❌ Search failed!")
        logger.error(f"Group TG UserID error: {e}")

async def num_name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(update.effective_chat.id)
    if not is_group_active(chat_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a mobile number.\n\nUsage: /numname 919087654321", parse_mode="Markdown")
        return
    
    number = context.args[0]
    if not number.isdigit() or not (10 <= len(number) <= 12):
        await update.message.reply_text("❌ Invalid number! Please send a valid mobile number.", parse_mode="Markdown")
        return
    
    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{NUM_NAME_API_URL}?number={number}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success") == True and result.get("data"):
                data = result.get("data", {})
                name = data.get("name", "Unknown")
                number_res = data.get("number", number)

                result_text = (
                    f"✅ *Number to Name Result*\n\n"
                    f"📞 *Number:* `{number_res}`\n"
                    f"👤 *Name:* {name}\n\n"
                    f"🏢 *Group Active - Unlimited Searches*"
                )
                
                await update.message.reply_text(result_text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ No record found!")
        else:
            await update.message.reply_text("❌ API error!")
            
    except Exception as e:
        await update.message.reply_text("❌ Search failed!")
        logger.error(f"Group Num to Name error: {e}")

async def pan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(update.effective_chat.id)
    if not is_group_active(chat_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a PAN number.\n\nUsage: /pan ABCDE1234F", parse_mode="Markdown")
        return
    
    pan_number = context.args[0]
    if not pan_number or len(pan_number) != 10 or not pan_number.isalnum():
        await update.message.reply_text("❌ Invalid PAN number! Please send a valid 10-digit PAN number.", parse_mode="Markdown")
        return
    
    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{PAN_API_URL}{pan_number}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") and data.get("data"):
                pan_data = data.get("data", {})
                
                result_text = (
                    f"✅ *PAN Card Information*\n\n"
                    f"👤 *Full Name:* {pan_data.get('fullName', 'N/A')}\n"
                    f"👤 *First Name:* {pan_data.get('firstName', 'N/A')}\n"
                    f"👤 *Last Name:* {pan_data.get('lastName', 'N/A')}\n"
                    f"📅 *Date of Birth:* {pan_data.get('dob', 'N/A')}\n"
                    f"✅ *PAN Status:* {pan_data.get('panStatus', 'N/A')}\n\n"
                    f"🏢 *Group Active - Unlimited Searches*"
                )
                
                await update.message.reply_text(result_text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ No record found!")
        else:
            await update.message.reply_text("❌ API error!")
            
    except Exception as e:
        await update.message.reply_text("❌ Search failed!")
        logger.error(f"Group PAN search error: {e}")

async def vehicle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(update.effective_chat.id)
    if not is_group_active(chat_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a Vehicle Number.\n\nUsage: /vehicle UP32AB1234", parse_mode="Markdown")
        return
    
    rc_input = context.args[0].strip().upper()
    if len(rc_input) != 10:
        await update.message.reply_text("❌ Invalid Vehicle Number! Please send a valid 10-character RC (e.g., UP32AB1234).", parse_mode="Markdown")
        return
    
    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{VEHICLE_API_URL}?number={rc_input}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("rc_number"):
                result_text = (
                    f"🚗 *Vehicle Details*\n\n"
                    f"🆔 *RC Number:* `{data.get('rc_number', 'N/A')}`\n"
                    f"👤 *Owner Name:* {data.get('owner_name', 'N/A')}\n"
                    f"👨 *Father Name:* {data.get('father_name', 'N/A')}\n"
                    f"🔢 *Owner Serial:* {data.get('owner_serial_no', 'N/A')}\n"
                    f"🏢 *Model Name:* {data.get('model_name', 'N/A')}\n"
                    f"🚘 *Maker Model:* {data.get('maker_model', 'N/A')}\n"
                    f"🚦 *Vehicle Class:* {data.get('vehicle_class', 'N/A')}\n"
                    f"⛽ *Fuel Type:* {data.get('fuel_type', 'N/A')}\n"
                    f"🌍 *Fuel Norms:* {data.get('fuel_norms', 'N/A')}\n"
                    f"📅 *Reg. Date:* {data.get('registration_date', 'N/A')}\n"
                    f"🛡️ *Ins. Company:* {data.get('insurance_company', 'N/A')}\n"
                    f"📅 *Ins. Expiry:* {data.get('insurance_expiry', 'N/A')}\n"
                    f"🏋️ *Fitness Upto:* {data.get('fitness_upto', 'N/A')}\n"
                    f"💰 *Tax Upto:* {data.get('tax_upto', 'N/A')}\n"
                    f"🏛️ *RTO:* {data.get('rto', 'N/A')}\n"
                    f"📍 *Address:* {data.get('address', 'N/A')}\n"
                    f"🏙️ *City:* {data.get('city', 'N/A')}\n"
                    f"📞 *Phone:* {data.get('phone', 'N/A')}\n\n"
                    f"🏢 *Group Active - Unlimited Searches*"
                )
                
                await update.message.reply_text(result_text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ No record found or invalid RC number!")
        else:
            await update.message.reply_text("❌ API error!")
            
    except Exception as e:
        await update.message.reply_text("❌ Search failed!")
        logger.error(f"Group Vehicle search error: {e}")

async def pincode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(update.effective_chat.id)
    if not is_group_active(chat_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a pincode.\n\nUsage: /pincode 110001", parse_mode="Markdown")
        return
    
    pincode = context.args[0]
    if not pincode.isdigit() or len(pincode) != 6:
        await update.message.reply_text("❌ Invalid pincode! Please send a 6-digit Indian pincode.", parse_mode="Markdown")
        return
    
    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{PINCODE_API_URL}/{pincode}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0 and data[0].get("Status") == "Success":
                result = data[0]
                post_offices = result.get("PostOffice", [])
                
                if post_offices and len(post_offices) > 0:
                    msg = (
                        f"*📍 Pincode Information*\n\n"
                        f"🔢 *Pincode:* `{pincode}`\n"
                        f"📊 *Status:* {result.get('Status', 'N/A')}\n"
                        f"📝 *Message:* {result.get('Message', 'N/A')}\n\n"
                        f"🏢 *Found {len(post_offices)} Post Office(s):*\n"
                    )
                    
                    for i, office in enumerate(post_offices[:3]):  # Limit to first 3 offices
                        msg += (
                            f"\n*📍 Location {i+1}:*\n"
                            f"🏢 *Name:* {office.get('Name', 'N/A')}\n"
                            f"🏭 *Branch Type:* {office.get('BranchType', 'N/A')}\n"
                            f"🚚 *Delivery Status:* {office.get('DeliveryStatus', 'N/A')}\n"
                            f"🗺️ *District:* {office.get('District', 'N/A')}\n"
                            f"🏛️ *State:* {office.get('State', 'N/A')}\n"
                        )
                    
                    if len(post_offices) > 3:
                        msg += f"\n\n*... and {len(post_offices) - 3} more post offices*"
                    
                    msg += "\n\n🏢 *Group Active - Unlimited Searches*"
                    await update.message.reply_text(msg, parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ No post offices found for this pincode!")
            else:
                await update.message.reply_text("❌ Invalid pincode or no data found!")
        else:
            await update.message.reply_text("❌ API error!")
            
    except Exception as e:
        await update.message.reply_text("❌ Search failed!")
        logger.error(f"Pincode search error: {e}")

async def stylish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(update.effective_chat.id)
    if not is_group_active(chat_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide text to convert.\n\nUsage: /stylish Your text here", parse_mode="Markdown")
        return
    
    text = " ".join(context.args)
    if not text:
        return
        
    # In groups, unlimited if active, but let's limit the styles sent to avoid spam
    # We'll send first 5 styles as a sample in groups
    stylish_text = convert_to_stylish(text)
    
    msg = f"✨ *Stylish Text Variations for:* `{text}`\n\n"
    
    # Send only first 5 for groups to prevent spam
    for i, (prefix, suffix) in enumerate(STYLES[:5], 1):
        styled_name = f"{prefix}{stylish_text}{suffix}"
        msg += f"{i}. {styled_name}\n"
        
    msg += "\n🏢 *Group Active - Unlimited Generations*"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ==========================================

# ================= CALLBACK HANDLERS =================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    
    if is_user_banned(user_id):
        ban_info = get_ban_info(user_id)
        await query.message.reply_photo(
            photo=INFO_IMAGE,
            caption=f"❌ *You are banned from using this bot*\n\nReason: {ban_info.get('reason', 'No reason provided')}",
            parse_mode="Markdown"
        )
        return
    
    if is_maintenance_mode() and query.from_user.id != ADMIN_ID:
        await query.message.reply_photo(
            photo=MAINTENANCE_IMAGE,
            caption=get_maintenance_message(),
            parse_mode="Markdown"
        )
        return
    
    if data not in ["check_joined", "refresh_join_status", "admin_"] and not await check_channel_membership(query.from_user.id, context):
        await send_force_join_message(update, context)
        return
    
    if data == "check_joined":
        required_channels = get_required_channels()
        not_joined = []
        for channel in required_channels:
            try:
                member = await context.bot.get_chat_member(channel["id"], query.from_user.id)
                if member.status not in ["member", "administrator", "creator"]:
                    not_joined.append(channel)
            except:
                not_joined.append(channel)
        
        if not not_joined:
            await query.answer("✅ Thank you for joining all channels!", show_alert=True)
            await show_main_menu(update, context)
        else:
            await query.answer(f"❌ You haven't joined {len(not_joined)} channel(s) yet!", show_alert=True)
            await send_force_join_message(update, context)
    
    elif data == "refresh_join_status":
        await send_force_join_message(update, context)
        await query.answer("🔄 Status refreshed!", show_alert=True)
    
    elif data == "copy_referral":
        user_id = str(query.from_user.id)
        referral_link = get_referral_link(user_id)
        await query.answer("📋 Referral link copied!", show_alert=True)
        await query.message.reply_text(
            f"📋 *Your Referral Link*\n\n`{referral_link}`\n\nShare this link with your friends to earn 3 credits for each referral!",
            parse_mode="Markdown"
        )
    
    elif data.startswith("copy_coupon_"):
        coupon_code = data.split("_", 2)[2]
        await query.answer("📋 Coupon code copied!", show_alert=True)
        await query.message.reply_text(
            f"📋 *Coupon Code*\n\n`{coupon_code}`\n\nShare this code with users to give them rewards!",
            parse_mode="Markdown"
        )
    
    elif data == "buy_credits":
        await show_credit_plans(query, context)
    
    elif data == "buy_premium":
        await show_premium_plans(query, context)
    
    elif data == "my_account":
        await show_my_account(query, context)
    
    elif data == "referral":
        await show_referral_info(query, context)
    
    elif data == "coupon":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        await query.message.reply_photo(
            photo=INFO_IMAGE,
            caption="🎫 *Enter Coupon Code*\n\nPlease send the coupon code you want to redeem:",
            parse_mode="Markdown"
        )
        context.user_data["awaiting_coupon"] = True
    
    elif data == "search_number":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        context.user_data["awaiting_number"] = True
        await query.message.reply_photo(
            photo=SEARCH_IMAGE,
            caption="📱 *Enter Mobile Number*\n\nPlease send a 10-digit mobile number to search:",
            parse_mode="Markdown"
        )
    
    elif data == "tg_userid_search":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        context.user_data["awaiting_tg_userid"] = True
        await query.message.reply_photo(
            photo=SEARCH_IMAGE,
            caption="🆔 *TG UserID to Info*\n\nPlease send a Telegram User ID (Numeric) to find the linked phone number:\n\nExample: `6931300801`",
            parse_mode="Markdown"
        )
    
    elif data == "num_name_search":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        context.user_data["awaiting_num_name"] = True
        await query.message.reply_photo(
            photo=SEARCH_IMAGE,
            caption="📞 *Number to Name*\n\nPlease send a mobile number (with country code e.g., 919876543210):",
            parse_mode="Markdown"
        )
    
    elif data == "pan_search":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        context.user_data["awaiting_pan"] = True
        await query.message.reply_photo(
            photo=PAN_SEARCH_IMAGE,
            caption="🆔 *PAN Card Information*\n\nPlease send a PAN number to get information:\n\nExample: `ABCDE1234F`",
            parse_mode="Markdown"
        )
    
    elif data == "vehicle_search":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        context.user_data["awaiting_vehicle"] = True
        await query.message.reply_photo(
            photo=SEARCH_IMAGE,
            caption="🚗 *Vehicle Info (RC)*\n\nPlease send a Vehicle Number (RC):\n\nExample: `UP32AB1234`",
            parse_mode="Markdown"
        )
    
    elif data == "pincode_search":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        context.user_data["awaiting_pincode"] = True
        await query.message.reply_photo(
            photo=PINCODE_SEARCH_IMAGE,
            caption="📍 *Pincode Search*\n\nPlease send a 6-digit Indian Pincode to search:\n\nExample: `110001`",
            parse_mode="Markdown"
        )
    
    elif data == "stylish_text":
        for key in list(context.user_data.keys()):
            if key.startswith("awaiting_"):
                del context.user_data[key]
        context.user_data["awaiting_stylish_text"] = True
        await query.message.reply_photo(
            photo=STYLISH_TEXT_IMAGE,
            caption="✨ *Stylish Text Generator*\n\nPlease send the text you want to convert to stylish text:\n\nExample: `Your Name`\n\nYou'll receive each style in a separate message for easy copying!",
            parse_mode="Markdown"
        )
    
    elif data == "back_to_menu":
        await show_main_menu(update, context)
    
    elif data.startswith("admin_"):
        await handle_admin_callbacks(query, context, data)
    
    elif data.startswith("maintenance_"):
        await handle_maintenance_callbacks(query, context, data)
    
    elif data.startswith("credit_plan_"):
        plan_id = data.split("_")[-1]
        await process_credit_plan(query, context, plan_id)
    
    elif data.startswith("premium_plan_"):
        plan_id = data.split("_")[-1]
        await process_premium_plan(query, context, plan_id)
    
    elif data.startswith("payment_approve_"):
        payment_id = data.split("_", 2)[-1]
        await approve_payment(query, context, payment_id)
    
    elif data.startswith("payment_reject_"):
        payment_id = data.split("_", 2)[-1]
        await reject_payment(query, context, payment_id)
    
    elif data.startswith("payment_pending_"):
        payment_id = data.split("_", 2)[-1]
        await handle_payment_pending(query, context, payment_id)
    
    elif data.startswith("coupon_type_"):
        coupon_type = data.split("_")[-1]
        context.user_data["coupon_gen"]["type"] = coupon_type
        context.user_data["coupon_gen"]["step"] = 2
        await query.message.reply_text(
            f"*🎟️ Advanced Coupon Generator*\n\nReward type: {coupon_type}\n\nNow send the reward value (credits or days):",
            parse_mode="Markdown"
        )
    
    elif data == "coupon_gen_cancel":
        if "coupon_gen" in context.user_data:
            del context.user_data["coupon_gen"]
        await query.message.reply_text("❌ Coupon generation cancelled.", parse_mode="Markdown")
    
    elif data.startswith("credit_cost_"):
        feature = data.split("_", 2)[-1]
        await show_credit_cost_edit(query, context, feature)
    
    elif data.startswith("edit_credit_cost_"):
        feature = data.split("_", 3)[-1]
        context.user_data["editing_credit_cost"] = feature
        await query.message.reply_text(
            f"*💰 Edit Credit Cost*\n\nCurrent cost: {get_credit_cost(feature)} credits\n\nPlease send the new credit cost (number):",
            parse_mode="Markdown"
        )
    
    elif data == "admin_activate_group":
        context.user_data["admin_action"] = "activate_group"
        await query.message.reply_text(
            "🏢 *Activate Group*\n\nPlease send the Group ID to activate:\n\nExample: `-1001234567890`",
            parse_mode="Markdown"
        )
    
    elif data == "admin_deactivate_group":
        context.user_data["admin_action"] = "deactivate_group"
        await query.message.reply_text(
            "🏢 *Deactivate Group*\n\nPlease send the Group ID to deactivate:\n\nExample: `-1001234567890`",
            parse_mode="Markdown"
        )
    
    elif data == "admin_active_groups":
        await show_active_groups(query, context)

async def handle_maintenance_callbacks(query, context, data):
    if query.from_user.id != ADMIN_ID:
        await query.answer("Unauthorized!", show_alert=True)
        return
    
    if data == "maintenance_on":
        if set_maintenance_mode(True):
            await query.answer("✅ Maintenance mode enabled!", show_alert=True)
            await show_maintenance_options(query, context)
        else:
            await query.answer("❌ Failed to enable maintenance mode!", show_alert=True)
    
    elif data == "maintenance_off":
        if set_maintenance_mode(False):
            await query.answer("✅ Maintenance mode disabled!", show_alert=True)
            await show_maintenance_options(query, context)
        else:
            await query.answer("❌ Failed to disable maintenance mode!", show_alert=True)
    
    elif data == "maintenance_edit_message":
        context.user_data["editing_maintenance_message"] = True
        await query.message.reply_text(
            "📝 *Edit Maintenance Message*\n\nPlease send the new maintenance message:",
            parse_mode="Markdown"
        )

async def handle_payment_pending(query, context, payment_id):
    user_id = str(query.from_user.id)
    payment = get_payment(payment_id)
    
    if not payment or payment["user_id"] != user_id:
        await query.answer("Invalid payment session!", show_alert=True)
        return
    
    context.user_data["pending_payment"] = payment_id
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="buy_credits" if payment["plan_type"] == "credits" else "buy_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            f"*💳 Payment Confirmation*\n\nThank you for your payment!\n\nPlease send a screenshot of your payment to complete the process.\n\nPlan: {payment['plan_type']}\nDetails: {payment['plan_details']}\n\n⏳ Waiting for your payment screenshot...",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except:
        pass

async def show_credit_plans(query, context):
    keyboard = [
        [InlineKeyboardButton("💎 10 Credits - ₹10", callback_data="credit_plan_10")],
        [InlineKeyboardButton("💎 50 Credits - ₹30", callback_data="credit_plan_50")],
        [InlineKeyboardButton("💎 100 Credits - ₹50", callback_data="credit_plan_100")],
        [InlineKeyboardButton("💎 300 Credits - ₹100", callback_data="credit_plan_300")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=PAYMENT_IMAGE,
                caption="*💳 Buy Credits*\n\nSelect a credit package below:\n💳 UPI ID: `" + UPI_ID + "`\n\nAfter payment, click 'I've Paid' and send the screenshot.",
                parse_mode="Markdown"
            ),
            reply_markup=reply_markup
        )
    except:
        pass

async def show_premium_plans(query, context):
    keyboard = [
        [InlineKeyboardButton("👑 1 Day - ₹30", callback_data="premium_plan_1")],
        [InlineKeyboardButton("👑 3 Days - ₹70", callback_data="premium_plan_3")],
        [InlineKeyboardButton("👑 1 Week - ₹120", callback_data="premium_plan_7")],
        [InlineKeyboardButton("👑 1 Month - ₹200", callback_data="premium_plan_30")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=PAYMENT_IMAGE,
                caption="*👑 Buy Premium*\n\nSelect a premium plan below:\n💳 UPI ID: `" + UPI_ID + "`\n\nAfter payment, click 'I've Paid' and send the screenshot.",
                parse_mode="Markdown"
            ),
            reply_markup=reply_markup
        )
    except:
        pass

async def show_my_account(query, context):
    user_id = str(query.from_user.id)
    user = get_user(user_id)
    
    premium_status = "✅ Active" if is_premium_user(user_id) else "❌ Inactive"
    premium_expiry = "N/A"
    if user.get("premium_expiry"):
        try:
            expiry = datetime.datetime.fromisoformat(user["premium_expiry"])
            premium_expiry = expiry.strftime("%d-%m-%Y %H:%M")
        except:
            pass
    
    account_text = (
        f"*👤 My Account*\n\n"
        f"🆔 User ID: `{user_id}`\n"
        f"👤 Username: @{query.from_user.username or 'N/A'}\n"
        f"💰 Credits: {user.get('balance', 0)}\n"
        f"👑 Premium: {premium_status}\n"
        f"⏰ Premium Expiry: {premium_expiry}\n"
        f"🔗 Referrals: {user.get('referrals', 0)}\n"
        f"💸 Referral Earnings: {user.get('referral_earnings', 0)} credits"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(media=ACCOUNT_IMAGE, caption=account_text, parse_mode="Markdown"),
            reply_markup=reply_markup
        )
    except:
        pass

async def show_referral_info(query, context):
    user_id = str(query.from_user.id)
    referral_link = get_referral_link(user_id)
    user = get_user(user_id)
    
    referral_text = (
        f"*🔗 Referral System*\n\n"
        f"📱 Your Referral Link:\n`{referral_link}`\n\n"
        f"👥 Total Referrals: {user.get('referrals', 0)}\n"
        f"💰 Earned Credits: {user.get('referral_earnings', 0)}\n\n"
        f"🎁 *Reward*: 3 credits for each referral!"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy Link", callback_data="copy_referral")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(media=REFERRAL_IMAGE, caption=referral_text, parse_mode="Markdown"),
            reply_markup=reply_markup
        )
    except:
        pass

async def process_credit_plan(query, context, plan_id):
    plans = {
        "10": {"credits": 10, "price": "₹10"},
        "50": {"credits": 50, "price": "₹30"},
        "100": {"credits": 100, "price": "₹50"},
        "300": {"credits": 300, "price": "₹100"}
    }
    
    if plan_id not in plans:
        await query.answer("Invalid plan!", show_alert=True)
        return
    
    plan = plans[plan_id]
    user_id = str(query.from_user.id)
    payment_id = create_payment_request(user_id, "credits", {"credits": plan["credits"], "price": plan["price"]})
    
    keyboard = [
        [InlineKeyboardButton("💳 I've Paid", callback_data=f"payment_pending_{payment_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="buy_credits")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            f"*💳 Payment Details*\n\nPlan: {plan['credits']} Credits\nPrice: {plan['price']}\nUPI ID: `{UPI_ID}`\n\n1. Pay the amount above\n2. Click 'I've Paid'\n3. Send payment screenshot",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except:
        pass

async def process_premium_plan(query, context, plan_id):
    plans = {
        "1": {"days": 1, "price": "₹30"},
        "3": {"days": 3, "price": "₹70"},
        "7": {"days": 7, "price": "₹120"},
        "30": {"days": 30, "price": "₹200"}
    }
    
    if plan_id not in plans:
        await query.answer("Invalid plan!", show_alert=True)
        return
    
    plan = plans[plan_id]
    user_id = str(query.from_user.id)
    payment_id = create_payment_request(user_id, "premium", {"days": plan["days"], "price": plan["price"]})
    
    keyboard = [
        [InlineKeyboardButton("💳 I've Paid", callback_data=f"payment_pending_{payment_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="buy_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            f"*👑 Payment Details*\n\nPlan: {plan['days']} Days Premium\nPrice: {plan['price']}\nUPI ID: `{UPI_ID}`\n\n1. Pay the amount above\n2. Click 'I've Paid'\n3. Send payment screenshot",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except:
        pass

async def handle_admin_callbacks(query, context, data):
    if query.from_user.id != ADMIN_ID:
        await query.answer("Unauthorized!", show_alert=True)
        return
    
    if "admin_action" in context.user_data:
        del context.user_data["admin_action"]

    if data == "admin_menu":
        await show_admin_menu(query, context)
        return

    if data == "admin_stats":
        stats_text = await get_comprehensive_stats()
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_menu")]]
        await query.edit_message_text(stats_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "admin_add_credits":
        context.user_data["admin_action"] = "add_credits"
        await query.edit_message_text("➕ *Add Credits*\n\nUse: /addcredit USERID AMOUNT\n\nExample: /addcredit 123456789 50", parse_mode="Markdown")
    
    elif data == "admin_remove_credits":
        context.user_data["admin_action"] = "remove_credits"
        await query.edit_message_text("➖ *Remove Credits*\n\nUse: /removecredit USERID AMOUNT\n\nExample: /removecredit 123456789 50", parse_mode="Markdown")
    
    elif data == "admin_add_premium":
        context.user_data["admin_action"] = "add_premium"
        await query.edit_message_text("👑 *Add Premium*\n\nUse: /addpremium USERID DAYS\n\nExample: /addpremium 123456789 7", parse_mode="Markdown")
    
    elif data == "admin_remove_premium":
        context.user_data["admin_action"] = "remove_premium"
        await query.edit_message_text("❌ *Remove Premium*\n\nUse: /removepremium USERID\n\nExample: /removepremium 123456789", parse_mode="Markdown")
    
    elif data == "admin_broadcast":
        context.user_data["admin_action"] = "broadcast"
        context.user_data["broadcast_mode"] = True
        await query.edit_message_text("📢 *Broadcast System*\n\nSend the message you want to broadcast.\nType /cancel to cancel.", parse_mode="Markdown")
    
    elif data == "admin_create_coupon":
        context.user_data["admin_action"] = "create_coupon"
        context.user_data["coupon_creation"] = True
        await query.edit_message_text("🎫 *Create Coupon*\n\nSend coupon details in format:\n`CODE|TYPE|VALUE|MAX_USES|EXPIRY_DAYS`\n\nTYPE: credits or premium\nVALUE: credit amount or premium days\n\nExample: `WELCOME50|credits|50|100|30`", parse_mode="Markdown")
    
    elif data == "admin_generate_coupon":
        context.user_data["admin_action"] = "generate_coupon"
        await start_coupon_generation(query, context)
    
    elif data == "admin_coupon_stats":
        await show_coupon_stats(query, context)
    
    elif data == "admin_credit_costs":
        context.user_data["admin_action"] = "credit_costs"
        await show_credit_costs(query, context)
    
    elif data == "admin_ban_user":
        if "ban_user_id" in context.user_data:
            del context.user_data["ban_user_id"]
        if "ban_reason" in context.user_data:
            del context.user_data["ban_reason"]
        context.user_data["admin_action"] = "ban_user"
        context.user_data["ban_user_id"] = True
        await query.edit_message_text("🚫 *Ban User*\n\nSend the User ID to ban:\n\nExample: `123456789`\n\nOr use: /ban USERID [reason]", parse_mode="Markdown")
    
    elif data == "admin_unban_user":
        if "unban_user_id" in context.user_data:
            del context.user_data["unban_user_id"]
        context.user_data["admin_action"] = "unban_user"
        context.user_data["unban_user_id"] = True
        await query.edit_message_text("✅ *Unban User*\n\nSend the User ID to unban:\n\nExample: `123456789`\n\nOr use: /unban USERID", parse_mode="Markdown")
    
    elif data == "admin_banned_users":
        await show_banned_users(query, context)
    
    elif data == "admin_maintenance":
        await show_maintenance_options(query, context)
    
    elif data == "admin_groups":
        await show_group_management(query, context)

async def show_group_management(query, context):
    groups = load_groups()
    active_groups = [g for g in groups.values() if g.get('active', False)]
    
    keyboard = [
        [InlineKeyboardButton("📊 Active Groups", callback_data="admin_active_groups")],
        [InlineKeyboardButton("🔓 Activate Group", callback_data="admin_activate_group")],
        [InlineKeyboardButton("🔒 Deactivate Group", callback_data="admin_deactivate_group")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    groups_text = (
        f"*🏢 Group Management*\n\n"
        f"📊 Total Groups: {len(groups)}\n"
        f"✅ Active Groups: {len(active_groups)}\n\n"
        f"Select an option:"
    )
    
    try:
        await query.edit_message_text(groups_text, parse_mode="Markdown", reply_markup=reply_markup)
    except:
        pass

async def show_active_groups(query, context):
    groups = load_groups()
    active_groups = {gid: g for gid, g in groups.items() if g.get('active', False)}
    
    if not active_groups:
        await query.edit_message_text("📊 *Active Groups*\n\nNo active groups found.", parse_mode="Markdown")
        return
    
    groups_text = "*📊 Active Groups*\n\n"
    for group_id, group_data in active_groups.items():
        admin_id = group_data.get("admin_id", "N/A")
        activated_at = group_data.get("activated_at", "N/A")
        groups_text += f"🆔 *Group ID:* `{group_id}`\n👤 *Admin ID:* `{admin_id}`\n🕐 *Activated At:* {activated_at}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_groups")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(groups_text, parse_mode="Markdown", reply_markup=reply_markup)

async def show_banned_users(query, context):
    banned_users = load_banned_users()
    if not banned_users:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]
        await query.edit_message_text("📋 *Banned Users*\n\nNo users are currently banned.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    banned_text = "*📋 Banned Users*\n\n"
    for user_id, ban_info in banned_users.items():
        banned_text += f"🆔 *User ID:* `{user_id}`\n📝 *Reason:* {ban_info.get('reason', 'No reason')}\n📅 *Banned on:* {ban_info.get('banned_at', 'N/A')}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]]
    await query.edit_message_text(banned_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_maintenance_options(query, context):
    settings = load_settings()
    is_enabled = settings.get("maintenance_mode", False)
    current_message = settings.get("maintenance_message", "🔧 Bot is under maintenance. Please try again later.")
    status_text = "🔴 *ENABLED*" if is_enabled else "🟢 *DISABLED*"
    
    keyboard = [
        [InlineKeyboardButton("🔧 Turn ON", callback_data="maintenance_on")],
        [InlineKeyboardButton("✅ Turn OFF", callback_data="maintenance_off")],
        [InlineKeyboardButton("📝 Edit Message", callback_data="maintenance_edit_message")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    maintenance_text = (
        f"*🔧 Maintenance Mode*\n\n"
        f"Status: {status_text}\n\n"
        f"Current Message:\n{current_message}\n\n"
        f"Choose an action:"
    )
    
    try:
        await query.edit_message_text(maintenance_text, parse_mode="Markdown", reply_markup=reply_markup)
    except:
        pass

async def show_credit_costs(query, context):
    costs = load_credit_costs()
    cost_text = (
        "*💰 Credit Costs Configuration*\n\n"
        f"📱 Number Search: {costs.get('number_search', 1)} credits\n"
        f"🆔 TG UserID Search: {costs.get('tg_userid_search', 2)} credits\n"
        f"📞 Num to Name: {costs.get('num_name_search', 1)} credits\n"
        f"🆔 PAN Card Search: {costs.get('pan_search', 2)} credits\n"
        f"🚗 Vehicle Info: {costs.get('vehicle_search', 5)} credits\n"
        f"📍 Pincode Search: {costs.get('pincode_search', 1)} credits\n"
        f"✨ Stylish Text: {costs.get('stylish_text', 1)} credits\n\n"
        "Click on a feature below to change its credit cost:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 Number Search", callback_data="credit_cost_number_search")],
        [InlineKeyboardButton("🆔 TG UserID Search", callback_data="credit_cost_tg_userid_search")],
        [InlineKeyboardButton("📞 Num to Name", callback_data="credit_cost_num_name_search")],
        [InlineKeyboardButton("🆔 PAN Card", callback_data="credit_cost_pan_search")],
        [InlineKeyboardButton("🚗 Vehicle Info", callback_data="credit_cost_vehicle_search")],
        [InlineKeyboardButton("📍 Pincode Search", callback_data="credit_cost_pincode_search")],
        [InlineKeyboardButton("✨ Stylish Text", callback_data="credit_cost_stylish_text")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(cost_text, parse_mode="Markdown", reply_markup=reply_markup)
    except:
        pass

async def start_coupon_generation(query, context):
    context.user_data["coupon_gen"] = {"step": 1}
    
    keyboard = [
        [InlineKeyboardButton("Credits", callback_data="coupon_type_credits")],
        [InlineKeyboardButton("Premium Days", callback_data="coupon_type_premium")],
        [InlineKeyboardButton("❌ Cancel", callback_data="coupon_gen_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("*🎟️ Advanced Coupon Generator*\n\nSelect coupon reward type:", parse_mode="Markdown", reply_markup=reply_markup)

async def show_coupon_stats(query, context):
    stats = get_coupon_stats()
    coupons = load_coupons()
    
    stats_text = (
        f"*📊 Coupon Statistics*\n\n"
        f"🔢 Total Coupons: {stats['total']}\n"
        f"✅ Active Coupons: {stats['active']}\n"
        f"❌ Expired Coupons: {stats['expired']}\n"
        f"📈 Used Coupons: {stats['used']}\n"
        f"📉 Unused Coupons: {stats['unused']}"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_menu")]]
    await query.edit_message_text(stats_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def approve_payment(query, context, payment_id):
    if query.from_user.id != ADMIN_ID:
        return
    
    payment = get_payment(payment_id)
    if not payment:
        await query.answer("Payment not found!", show_alert=True)
        return
    
    await query.message.reply_text(
        f"*💳 Approve Payment*\n\nUser ID: {payment['user_id']}\nPlan: {payment['plan_type']}\nDetails: {payment['plan_details']}\n\nSend the amount to add (credits for credit plan, days for premium):",
        parse_mode="Markdown"
    )
    context.user_data["approving_payment"] = payment_id

async def reject_payment(query, context, payment_id):
    if query.from_user.id != ADMIN_ID:
        return
    
    payment = get_payment(payment_id)
    if not payment:
        await query.answer("Payment not found!", show_alert=True)
        return
    
    update_payment(payment_id, "rejected")
    try:
        await context.bot.send_message(payment["user_id"], "❌ Your payment has been rejected. Please contact admin for details.")
    except:
        pass
    
    await query.answer("Payment rejected!")
    await query.message.reply_text("✅ Payment rejected and user notified.")

# ==========================================

# ================= MESSAGE HANDLERS =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip() if update.message.text else ""
    
    if is_user_banned(user_id):
        ban_info = get_ban_info(user_id)
        await update.message.reply_photo(
            photo=INFO_IMAGE,
            caption=f"❌ *You are banned from using this bot*\n\nReason: {ban_info.get('reason', 'No reason provided')}",
            parse_mode="Markdown"
        )
        return
    
    if is_maintenance_mode() and update.effective_user.id != ADMIN_ID:
        await update.message.reply_photo(
            photo=MAINTENANCE_IMAGE,
            caption=get_maintenance_message(),
            parse_mode="Markdown"
        )
        return
    
    # Handle admin actions
    if update.effective_user.id == ADMIN_ID and context.user_data.get("admin_action"):
        action = context.user_data["admin_action"]
        
        if action == "activate_group":
            group_id = text.strip()
            if group_id.startswith("-100") and group_id[1:].isdigit():
                if activate_group(group_id, str(ADMIN_ID)):
                    await update.message.reply_text(f"✅ *Group Activated Successfully*\n\nGroup ID: `{group_id}`", parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ Failed to activate group.")
            else:
                await update.message.reply_text("❌ Invalid Group ID! Format: -1001234567890", parse_mode="Markdown")
            del context.user_data["admin_action"]
            return
        
        if action == "deactivate_group":
            group_id = text.strip()
            if group_id.startswith("-100") and group_id[1:].isdigit():
                if deactivate_group(group_id):
                    await update.message.reply_text(f"✅ *Group Deactivated Successfully*\n\nGroup ID: `{group_id}`", parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ Failed to deactivate group.")
            else:
                await update.message.reply_text("❌ Invalid Group ID!", parse_mode="Markdown")
            del context.user_data["admin_action"]
            return
        
        if action == "broadcast" and context.user_data.get("broadcast_mode"):
            await process_broadcast(update, context)
            return
        
        if action == "create_coupon" and context.user_data.get("coupon_creation"):
            await process_coupon_creation(update, context)
            return
    
    # Handle credit cost editing
    if context.user_data.get("editing_credit_cost"):
        feature = context.user_data["editing_credit_cost"]
        del context.user_data["editing_credit_cost"]
        
        try:
            new_cost = int(text)
            if new_cost < 0 or new_cost > 100:
                await update.message.reply_text("❌ Invalid cost! Please send a number between 0 and 100.", parse_mode="Markdown")
                return
            
            costs = load_credit_costs()
            costs[feature] = new_cost
            save_credit_costs(costs)
            
            feature_name = feature.replace('_', ' ').title()
            await update.message.reply_text(f"✅ Credit cost for {feature_name} updated to {new_cost} credits!", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Invalid input! Please send a valid number.", parse_mode="Markdown")
        return
    
    # Handle maintenance message edit
    if context.user_data.get("editing_maintenance_message") and update.effective_user.id == ADMIN_ID:
        context.user_data["editing_maintenance_message"] = False
        if set_maintenance_mode(True, text):
            await update.message.reply_text(f"✅ Maintenance message updated:\n\n{text}")
        else:
            await update.message.reply_text("❌ Failed to update maintenance message")
        return
    
    # Handle ban user
    if context.user_data.get("ban_user_id") and update.effective_user.id == ADMIN_ID:
        context.user_data["ban_user_id"] = False
        context.user_data["ban_reason"] = True
        context.user_data["pending_ban_user"] = text
        await update.message.reply_text(f"*🚫 Ban User*\n\nUser ID: `{text}`\n\nNow send the ban reason:", parse_mode="Markdown")
        return
    
    # Handle ban reason
    if context.user_data.get("ban_reason") and update.effective_user.id == ADMIN_ID:
        user_to_ban = context.user_data.get("pending_ban_user")
        context.user_data["ban_reason"] = False
        del context.user_data["pending_ban_user"]
        
        if ban_user(user_to_ban, text):
            await update.message.reply_text(f"✅ User {user_to_ban} has been banned\nReason: {text}")
            try:
                await context.bot.send_message(chat_id=user_to_ban, text=f"❌ You have been banned from using this bot\nReason: {text}")
            except:
                pass
        else:
            await update.message.reply_text("❌ Failed to ban user")
        return
    
    # Handle unban user
    if context.user_data.get("unban_user_id") and update.effective_user.id == ADMIN_ID:
        context.user_data["unban_user_id"] = False
        if unban_user(text):
            await update.message.reply_text(f"✅ User {text} has been unbanned")
            try:
                await context.bot.send_message(chat_id=text, text="✅ You have been unbanned and can now use the bot again")
            except:
                pass
        else:
            await update.message.reply_text("❌ Failed to unban user or user was not banned")
        return
    
    # Handle coupon generation process
    if context.user_data.get("coupon_gen"):
        await handle_coupon_generation(update, context)
        return
    
    # Handle coupon redemption
    if context.user_data.get("awaiting_coupon"):
        context.user_data["awaiting_coupon"] = False
        coupon = validate_coupon(text.upper())
        if not coupon:
            await update.message.reply_photo(photo=INFO_IMAGE, caption="❌ Invalid or expired coupon code!")
            return
        
        if use_coupon(text.upper(), user_id):
            reward_text = f"{coupon['reward_value']} credits" if coupon["reward_type"] == "credits" else f"{coupon['reward_value']} days premium"
            await update.message.reply_photo(photo=INFO_IMAGE, caption=f"✅ Coupon redeemed successfully! You received {reward_text}.")
        else:
            await update.message.reply_photo(photo=INFO_IMAGE, caption="❌ You have already used this coupon!")
        return
    
    # Handle number search
    if context.user_data.get("awaiting_number"):
        context.user_data["awaiting_number"] = False
        
        if not text.isdigit() or len(text) != 10:
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Invalid number! Please send a 10-digit mobile number.")
            return
        
        credit_cost = get_credit_cost("number_search")
        if not is_premium_user(user_id):
            user = get_user(user_id)
            if user["balance"] < credit_cost:
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption=f"❌ Insufficient credits! Number search requires {credit_cost} credits.")
                return
            remove_credits(user_id, credit_cost)
            update_search_stats("number_search", credit_cost)
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{NUM_API_URL}{text}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("result") and isinstance(data.get("result"), list):
                    records = data.get("result", [])
                    
                    if len(records) == 0:
                        if not is_premium_user(user_id):
                            add_credits(user_id, credit_cost)
                        await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ No record found!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                        return

                    result_text = f"✅ *Search Result for* `{text}`\n\n"
                    
                    for i, item in enumerate(records):
                        name = item.get("name", "N/A")
                        father_name = item.get("father_name", "N/A")
                        address = item.get("address", "N/A")
                        mobile = item.get("mobile", "N/A")
                        circle = item.get("circle", "N/A")
                        alt_num = item.get("alternate", "N/A")
                        email = item.get("email", "N/A")
                        uid = item.get("id", "N/A")
                        
                        result_text += (
                            f"━━━━━━━━━━━━━━━\n"
                            f"📋 *Record {i+1}*\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👤 Name: {name}\n"
                            f"👨 Father: {father_name}\n"
                            f"🏠 Address: {address}\n"
                            f"📞 Mobile: {mobile}\n"
                            f"📡 Circle: {circle}\n"
                            f"📞 Alt Number: {alt_num}\n"
                            f"📧 Email: {email}\n"
                            f"🆔 ID: `{uid}`\n\n"
                        )
                    
                    if not is_premium_user(user_id):
                        result_text += f"💰 Remaining Credits: {get_user(user_id)['balance']}"
                    else:
                        result_text += "👑 *Premium User*"
                    
                    await update.message.reply_photo(photo=SEARCH_RESULT_IMAGE, caption=result_text, parse_mode="Markdown")
                else:
                    if not is_premium_user(user_id):
                        add_credits(user_id, credit_cost)
                    await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ No record found!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            else:
                if not is_premium_user(user_id):
                    add_credits(user_id, credit_cost)
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ API error!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                
        except Exception as e:
            if not is_premium_user(user_id):
                add_credits(user_id, credit_cost)
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Search failed!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            logger.error(f"Search error: {e}")
        return

    # Handle TG UserID Search
    if context.user_data.get("awaiting_tg_userid"):
        context.user_data["awaiting_tg_userid"] = False
        
        if not text.isdigit():
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Invalid ID! Please send a valid numeric Telegram User ID.")
            return
        
        credit_cost = get_credit_cost("tg_userid_search")
        if not is_premium_user(user_id):
            user = get_user(user_id)
            if user["balance"] < credit_cost:
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption=f"❌ Insufficient credits! TG UserID search requires {credit_cost} credits.")
                return
            remove_credits(user_id, credit_cost)
            update_search_stats("tg_userid_search", credit_cost)
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{TG_USERID_API_URL}?userid={text}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    result_data = data.get("data", {})
                    if result_data.get("found"):
                        number = result_data.get("number", "N/A")
                        country = result_data.get("country", "N/A")
                        cc = result_data.get("country_code", "N/A")
                        searched_id = data.get("searched_userid", text)

                        result_text = (
                            f"✅ *TG UserID Info*\n\n"
                            f"🆔 *User ID:* `{searched_id}`\n"
                            f"🌍 *Country:* {country}\n"
                            f"📞 *Country Code:* {cc}\n"
                            f"📱 *Number:* `{number}`\n\n"
                        )
                        
                        if not is_premium_user(user_id):
                            result_text += f"💰 Remaining Credits: {get_user(user_id)['balance']}"
                        else:
                            result_text += "👑 *Premium User*"
                        
                        await update.message.reply_photo(photo=SEARCH_RESULT_IMAGE, caption=result_text, parse_mode="Markdown")
                    else:
                        if not is_premium_user(user_id):
                            add_credits(user_id, credit_cost)
                        await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ No details found for this User ID!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                else:
                    if not is_premium_user(user_id):
                        add_credits(user_id, credit_cost)
                    await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ API Error or Invalid User ID!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            else:
                if not is_premium_user(user_id):
                    add_credits(user_id, credit_cost)
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ API Error!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                
        except Exception as e:
            if not is_premium_user(user_id):
                add_credits(user_id, credit_cost)
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Search failed!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            logger.error(f"TG UserID search error: {e}")
        return

    # Handle Num to Name search
    if context.user_data.get("awaiting_num_name"):
        context.user_data["awaiting_num_name"] = False
        
        if not text.isdigit() or not (10 <= len(text) <= 12):
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Invalid number! Please send a valid mobile number (e.g., 919087654321 or 9087654321).")
            return
        
        credit_cost = get_credit_cost("num_name_search")
        if not is_premium_user(user_id):
            user = get_user(user_id)
            if user["balance"] < credit_cost:
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption=f"❌ Insufficient credits! Num to Name search requires {credit_cost} credits.")
                return
            remove_credits(user_id, credit_cost)
            update_search_stats("num_name_search", credit_cost)
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{NUM_NAME_API_URL}?number={text}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success") == True and result.get("data"):
                    data = result.get("data", {})
                    name = data.get("name", "Unknown")
                    number = data.get("number", text)

                    result_text = (
                        f"✅ *Number to Name Result*\n\n"
                        f"📞 *Number:* `{number}`\n"
                        f"👤 *Name:* {name}\n\n"
                    )
                    
                    if not is_premium_user(user_id):
                        result_text += f"💰 Remaining Credits: {get_user(user_id)['balance']}"
                    else:
                        result_text += "👑 *Premium User*"
                    
                    await update.message.reply_photo(photo=SEARCH_RESULT_IMAGE, caption=result_text, parse_mode="Markdown")
                else:
                    if not is_premium_user(user_id):
                        add_credits(user_id, credit_cost)
                    await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ No record found!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            else:
                if not is_premium_user(user_id):
                    add_credits(user_id, credit_cost)
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ API error!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                
        except Exception as e:
            if not is_premium_user(user_id):
                add_credits(user_id, credit_cost)
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Search failed!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            logger.error(f"Num to Name search error: {e}")
        return

    # Handle PAN search
    if context.user_data.get("awaiting_pan"):
        context.user_data["awaiting_pan"] = False
        
        if not text or len(text) != 10 or not text.isalnum():
            await update.message.reply_photo(photo=PAN_SEARCH_IMAGE, caption="❌ Invalid PAN number! Please send a valid 10-digit PAN number (e.g., ABCDE1234F).")
            return
        
        credit_cost = get_credit_cost("pan_search")
        if not is_premium_user(user_id):
            user = get_user(user_id)
            if user["balance"] < credit_cost:
                await update.message.reply_photo(photo=PAN_SEARCH_IMAGE, caption=f"❌ Insufficient credits! PAN search requires {credit_cost} credits.")
                return
            remove_credits(user_id, credit_cost)
            update_search_stats("pan_search", credit_cost)
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{PAN_API_URL}{text}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("data"):
                    pan_data = data.get("data", {})
                    
                    result_text = (
                        f"✅ *PAN Card Information*\n\n"
                        f"👤 *Full Name:* {pan_data.get('fullName', 'N/A')}\n"
                        f"👤 *First Name:* {pan_data.get('firstName', 'N/A')}\n"
                        f"👤 *Last Name:* {pan_data.get('lastName', 'N/A')}\n"
                        f"📅 *Date of Birth:* {pan_data.get('dob', 'N/A')}\n"
                        f"✅ *PAN Status:* {pan_data.get('panStatus', 'N/A')}\n\n"
                    )
                    
                    if not is_premium_user(user_id):
                        result_text += f"💰 Remaining Credits: {get_user(user_id)['balance']}"
                    else:
                        result_text += "👑 *Premium User*"
                    
                    await update.message.reply_photo(photo=PAN_SEARCH_IMAGE, caption=result_text, parse_mode="Markdown")
                else:
                    if not is_premium_user(user_id):
                        add_credits(user_id, credit_cost)
                    await update.message.reply_photo(photo=PAN_SEARCH_IMAGE, caption="❌ No record found!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            else:
                if not is_premium_user(user_id):
                    add_credits(user_id, credit_cost)
                await update.message.reply_photo(photo=PAN_SEARCH_IMAGE, caption="❌ API error!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                
        except Exception as e:
            if not is_premium_user(user_id):
                add_credits(user_id, credit_cost)
            await update.message.reply_photo(photo=PAN_SEARCH_IMAGE, caption="❌ Search failed!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            logger.error(f"PAN search error: {e}")
        return

    # Handle Vehicle Info Search
    if context.user_data.get("awaiting_vehicle"):
        context.user_data["awaiting_vehicle"] = False
        
        rc_input = text.strip().upper()
        if len(rc_input) != 10:
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Invalid Vehicle Number! Please send a valid 10-character RC (e.g., UP32AB1234).")
            return
        
        credit_cost = get_credit_cost("vehicle_search")
        if not is_premium_user(user_id):
            user = get_user(user_id)
            if user["balance"] < credit_cost:
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption=f"❌ Insufficient credits! Vehicle search requires {credit_cost} credits.")
                return
            remove_credits(user_id, credit_cost)
            update_search_stats("vehicle_search", credit_cost)
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{VEHICLE_API_URL}?number={rc_input}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("rc_number"):
                    result_text = (
                        f"🚗 *Vehicle Details*\n\n"
                        f"🆔 *RC Number:* `{data.get('rc_number', 'N/A')}`\n"
                        f"👤 *Owner Name:* {data.get('owner_name', 'N/A')}\n"
                        f"👨 *Father Name:* {data.get('father_name', 'N/A')}\n"
                        f"🔢 *Owner Serial:* {data.get('owner_serial_no', 'N/A')}\n"
                        f"🏢 *Model Name:* {data.get('model_name', 'N/A')}\n"
                        f"🚘 *Maker Model:* {data.get('maker_model', 'N/A')}\n"
                        f"🚦 *Vehicle Class:* {data.get('vehicle_class', 'N/A')}\n"
                        f"⛽ *Fuel Type:* {data.get('fuel_type', 'N/A')}\n"
                        f"🌍 *Fuel Norms:* {data.get('fuel_norms', 'N/A')}\n"
                        f"📅 *Reg. Date:* {data.get('registration_date', 'N/A')}\n"
                        f"🛡️ *Ins. Company:* {data.get('insurance_company', 'N/A')}\n"
                        f"📅 *Ins. Expiry:* {data.get('insurance_expiry', 'N/A')}\n"
                        f"🏋️ *Fitness Upto:* {data.get('fitness_upto', 'N/A')}\n"
                        f"💰 *Tax Upto:* {data.get('tax_upto', 'N/A')}\n"
                        f"🏛️ *RTO:* {data.get('rto', 'N/A')}\n"
                        f"📍 *Address:* {data.get('address', 'N/A')}\n"
                        f"🏙️ *City:* {data.get('city', 'N/A')}\n"
                        f"📞 *Phone:* {data.get('phone', 'N/A')}\n\n"
                    )
                    
                    if not is_premium_user(user_id):
                        result_text += f"💰 Remaining Credits: {get_user(user_id)['balance']}"
                    else:
                        result_text += "👑 *Premium User*"
                    
                    await update.message.reply_photo(photo=SEARCH_RESULT_IMAGE, caption=result_text, parse_mode="Markdown")
                else:
                    if not is_premium_user(user_id):
                        add_credits(user_id, credit_cost)
                    await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ No record found or invalid RC number!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            else:
                if not is_premium_user(user_id):
                    add_credits(user_id, credit_cost)
                await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ API error!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                
        except Exception as e:
            if not is_premium_user(user_id):
                add_credits(user_id, credit_cost)
            await update.message.reply_photo(photo=SEARCH_IMAGE, caption="❌ Search failed!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            logger.error(f"Vehicle search error: {e}")
        return

    # Handle Pincode Search
    if context.user_data.get("awaiting_pincode"):
        context.user_data["awaiting_pincode"] = False
        
        if not text.isdigit() or len(text) != 6:
            await update.message.reply_photo(photo=PINCODE_SEARCH_IMAGE, caption="❌ Invalid pincode! Please send a 6-digit Indian pincode.")
            return
        
        credit_cost = get_credit_cost("pincode_search")
        if not is_premium_user(user_id):
            user = get_user(user_id)
            if user["balance"] < credit_cost:
                await update.message.reply_photo(photo=PINCODE_SEARCH_IMAGE, caption=f"❌ Insufficient credits! Pincode search requires {credit_cost} credits.")
                return
            remove_credits(user_id, credit_cost)
            update_search_stats("pincode_search", credit_cost)
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{PINCODE_API_URL}/{text}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0 and data[0].get("Status") == "Success":
                    result = data[0]
                    post_offices = result.get("PostOffice", [])
                    
                    if post_offices and len(post_offices) > 0:
                        msg = (
                            f"*📍 Pincode Information*\n\n"
                            f"🔢 *Pincode:* `{text}`\n"
                            f"📊 *Status:* {result.get('Status', 'N/A')}\n"
                            f"📝 *Message:* {result.get('Message', 'N/A')}\n\n"
                            f"🏢 *Found {len(post_offices)} Post Office(s):*\n"
                        )
                        
                        for i, office in enumerate(post_offices[:3]):  # Limit to first 3 offices
                            msg += (
                                f"\n*📍 Location {i+1}:*\n"
                                f"🏢 *Name:* {office.get('Name', 'N/A')}\n"
                                f"🏭 *Branch Type:* {office.get('BranchType', 'N/A')}\n"
                                f"🚚 *Delivery Status:* {office.get('DeliveryStatus', 'N/A')}\n"
                                f"🗺️ *District:* {office.get('District', 'N/A')}\n"
                                f"🏛️ *State:* {office.get('State', 'N/A')}\n"
                            )
                        
                        if len(post_offices) > 3:
                            msg += f"\n\n*... and {len(post_offices) - 3} more post offices*"
                        
                        if not is_premium_user(user_id):
                            msg += f"\n\n💰 Remaining Credits: {get_user(user_id)['balance']}"
                        else:
                            msg += "\n\n👑 *Premium User*"
                        
                        await update.message.reply_photo(photo=PINCODE_SEARCH_IMAGE, caption=msg, parse_mode="Markdown")
                    else:
                        if not is_premium_user(user_id):
                            add_credits(user_id, credit_cost)
                        await update.message.reply_photo(photo=PINCODE_SEARCH_IMAGE, caption="❌ No post offices found for this pincode!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                else:
                    if not is_premium_user(user_id):
                        add_credits(user_id, credit_cost)
                    await update.message.reply_photo(photo=PINCODE_SEARCH_IMAGE, caption="❌ Invalid pincode or no data found!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            else:
                if not is_premium_user(user_id):
                    add_credits(user_id, credit_cost)
                await update.message.reply_photo(photo=PINCODE_SEARCH_IMAGE, caption="❌ API error!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
                
        except Exception as e:
            if not is_premium_user(user_id):
                add_credits(user_id, credit_cost)
            await update.message.reply_photo(photo=PINCODE_SEARCH_IMAGE, caption="❌ Search failed!" + (" Credit refunded." if not is_premium_user(user_id) else ""))
            logger.error(f"Pincode search error: {e}")
        return

    # Handle Stylish Text Generator
    if context.user_data.get("awaiting_stylish_text"):
        context.user_data["awaiting_stylish_text"] = False
        
        credit_cost = get_credit_cost("stylish_text")
        if not is_premium_user(user_id):
            user = get_user(user_id)
            if user["balance"] < credit_cost:
                await update.message.reply_photo(photo=STYLISH_TEXT_IMAGE, caption=f"❌ Insufficient credits! Stylish text generation requires {credit_cost} credits.")
                return
            remove_credits(user_id, credit_cost)
            update_search_stats("stylish_text", credit_cost)
        
        stylish_text = convert_to_stylish(text)
        
        start_msg = await update.message.reply_text(
            f"✨ *Generating {len(STYLES)} stylish text variations for:* `{text}`\n\n"
            f"⏳ Please wait, each style will be sent in a separate message for easy copying..."
        )
        
        for i, (prefix, suffix) in enumerate(STYLES, 1):
            try:
                styled_name = f"{prefix}{stylish_text}{suffix}"
                await update.message.reply_text(f"✨ *Style {i}/{len(STYLES)}*\n\n{styled_name}")
                await asyncio.sleep(0.5) # Delay to avoid rate limit
            except Exception as e:
                logger.error(f"Error sending style {i}: {e}")
                continue
        
        await start_msg.edit_text(
            f"✅ *Generated {len(STYLES)} stylish text variations for:* `{text}`\n\n"
            f"💰 Remaining Credits: {get_user(user_id)['balance']}" if not is_premium_user(user_id) else "👑 Premium User"
        )
        return

    # Handle payment approval amount
    if context.user_data.get("approving_payment"):
        payment_id = context.user_data["approving_payment"]
        context.user_data["approving_payment"] = None
        
        try:
            amount = int(text)
            payment = get_payment(payment_id)
            
            if payment:
                if payment["plan_type"] == "credits":
                    add_credits(payment["user_id"], amount)
                elif payment["plan_type"] == "premium":
                    add_premium(payment["user_id"], amount)
                
                update_payment(payment_id, "approved", approved_amount=amount)
                update_payment_stats(payment["plan_type"], amount)
                
                try:
                    await context.bot.send_message(
                        payment["user_id"],
                        f"✅ Your payment has been approved! You received {amount} {'credits' if payment['plan_type'] == 'credits' else 'days premium'}."
                    )
                except:
                    pass
                
                await update.message.reply_text("✅ Payment approved successfully!")
            else:
                await update.message.reply_text("❌ Payment not found!")
        except ValueError:
            await update.message.reply_text("❌ Invalid amount! Please send a number.")
        return
    
    # Handle broadcast
    if context.user_data.get("broadcast_mode") and update.effective_user.id == ADMIN_ID:
        await process_broadcast(update, context)
        return
    
    # Handle coupon creation
    if context.user_data.get("coupon_creation") and update.effective_user.id == ADMIN_ID:
        await process_coupon_creation(update, context)
        return

async def handle_coupon_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    step = context.user_data["coupon_gen"]["step"]
    
    if step == 2:
        try:
            value = int(text)
            context.user_data["coupon_gen"]["value"] = value
            context.user_data["coupon_gen"]["step"] = 3
            await update.message.reply_text(f"*🎟️ Advanced Coupon Generator*\n\nReward type: {context.user_data['coupon_gen']['type']}\n\nNow send the maximum number of uses:", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Invalid value! Please send a number.", parse_mode="Markdown")
    
    elif step == 3:
        try:
            max_uses = int(text)
            context.user_data["coupon_gen"]["max_uses"] = max_uses
            context.user_data["coupon_gen"]["step"] = 4
            await update.message.reply_text(f"*🎟️ Advanced Coupon Generator*\n\nReward type: {context.user_data['coupon_gen']['type']}\nReward value: {context.user_data['coupon_gen']['value']}\nMax uses: {max_uses}\n\nNow send the number of days until expiry:", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Invalid value! Please send a number.", parse_mode="Markdown")
    
    elif step == 4:
        try:
            expiry_days = int(text)
            reward_type = context.user_data["coupon_gen"]["type"]
            reward_value = context.user_data["coupon_gen"]["value"]
            max_uses = context.user_data["coupon_gen"]["max_uses"]
            
            code = generate_coupon_code()
            
            if create_coupon(code, reward_type, reward_value, max_uses, expiry_days):
                coupon_stats = get_coupon_stats()
                expiry_date = datetime.datetime.now() + datetime.timedelta(days=expiry_days)
                
                coupon_text = (
                    f"*🎟️ ADVANCED COUPON GENERATED*\n\n"
                    f"🔑 *Coupon Code:* `{code}`\n"
                    f"🎁 *Reward Type:* {reward_type.title()}\n"
                    f"💰 *Reward Value:* {reward_value} {'credits' if reward_type == 'credits' else 'days premium'}\n"
                    f"👥 *Max Uses:* {max_uses}\n"
                    f"📅 *Expiry Date:* {expiry_date.strftime('%d-%m-%Y')}\n\n"
                    f"🔢 *Total Coupons:* {coupon_stats['total']}"
                )
                await update.message.reply_text(coupon_text, parse_mode="Markdown")
                del context.user_data["coupon_gen"]
            else:
                await update.message.reply_text("❌ Failed to create coupon!", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Invalid value! Please send a number.", parse_mode="Markdown")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if is_user_banned(user_id):
        ban_info = get_ban_info(user_id)
        await update.message.reply_photo(photo=INFO_IMAGE, caption=f"❌ *You are banned from using this bot*\n\nReason: {ban_info.get('reason', 'No reason provided')}", parse_mode="Markdown")
        return
    
    if is_maintenance_mode() and update.effective_user.id != ADMIN_ID:
        await update.message.reply_photo(photo=MAINTENANCE_IMAGE, caption=get_maintenance_message(), parse_mode="Markdown")
        return
    
    if context.user_data.get("pending_payment"):
        payment_id = context.user_data["pending_payment"]
        payment = get_payment(payment_id)
        if not payment:
            await update.message.reply_photo(photo=INFO_IMAGE, caption="❌ Payment session expired!")
            context.user_data["pending_payment"] = None
            return
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"payment_approve_{payment_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"payment_reject_{payment_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        caption = (
            f"💳 *New Payment Request*\n\n"
            f"👤 User: {update.effective_user.full_name}\n"
            f"🆔 User ID: {user_id}\n"
            f"🔗 Username: @{update.effective_user.username or 'N/A'}\n"
            f"📦 Plan: {payment['plan_type']}\n"
            f"📋 Details: {payment['plan_details']}\n"
            f"⏰ Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        try:
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            await context.bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode="Markdown", reply_markup=reply_markup)
            await update.message.reply_photo(photo=INFO_IMAGE, caption="✅ Payment screenshot sent to admin! Please wait for approval.")
            context.user_data["pending_payment"] = None
        except Exception as e:
            logger.error(f"Error forwarding payment screenshot: {e}")
            await update.message.reply_photo(photo=INFO_IMAGE, caption="❌ Failed to send screenshot to admin. Please try again.")
        return
    
    if context.user_data.get("broadcast_mode") and update.effective_user.id == ADMIN_ID:
        await process_broadcast(update, context)
        return

async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    context.user_data["broadcast_mode"] = False
    users = load_users()
    success = 0
    failed = 0
    
    await update.message.reply_text(f"📢 Starting broadcast to {len(users)} users...")
    
    for user_id in users.keys():
        try:
            if update.message.photo:
                await context.bot.send_photo(chat_id=user_id, photo=update.message.photo[-1].file_id, caption=update.message.caption, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=user_id, text=update.message.text, parse_mode="Markdown")
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
    
    await update.message.reply_text(f"✅ Broadcast completed!\n\n✅ Success: {success}\n❌ Failed: {failed}")

async def process_coupon_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    context.user_data["coupon_creation"] = False
    parts = update.message.text.strip().split("|")
    
    if len(parts) == 5:
        try:
            code, reward_type, reward_value, max_uses, expiry_days = parts
            reward_value = int(reward_value)
            max_uses = int(max_uses)
            expiry_days = int(expiry_days)
            
            if create_coupon(code.upper(), reward_type, reward_value, max_uses, expiry_days):
                coupon_stats = get_coupon_stats()
                expiry_date = datetime.datetime.now() + datetime.timedelta(days=expiry_days)
                
                coupon_text = (
                    f"*🎟️ ADVANCED COUPON CREATED*\n\n"
                    f"🔑 *Coupon Code:* `{code.upper()}`\n"
                    f"🎁 *Reward Type:* {reward_type.title()}\n"
                    f"💰 *Reward Value:* {reward_value} {'credits' if reward_type == 'credits' else 'days premium'}\n"
                    f"👥 *Max Uses:* {max_uses}\n"
                    f"📅 *Expiry Date:* {expiry_date.strftime('%d-%m-%Y')}\n\n"
                    f"🔢 *Total Coupons:* {coupon_stats['total']}"
                )
                await update.message.reply_text(coupon_text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Failed to create coupon!")
        except ValueError:
            await update.message.reply_text("❌ Invalid values! Please check your input.")
    else:
        await update.message.reply_text("❌ Invalid format! Please use: CODE|TYPE|VALUE|MAX_USES|EXPIRY_DAYS")

# ==========================================

# ================= ERROR HANDLING =================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ==========================================

# ================= MAIN FUNCTION =================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("addcredit", addcredit_command))
    application.add_handler(CommandHandler("removecredit", removecredit_command))
    application.add_handler(CommandHandler("addpremium", addpremium_command))
    application.add_handler(CommandHandler("removepremium", removepremium_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("maintenance", maintenance_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Add group command handlers
    application.add_handler(CommandHandler("activate", activate_group_command))
    application.add_handler(CommandHandler("deactivate", deactivate_group_command))
    application.add_handler(CommandHandler("number", number_command))
    application.add_handler(CommandHandler("tguserid", tg_userid_command))
    application.add_handler(CommandHandler("numname", num_name_command))
    application.add_handler(CommandHandler("pan", pan_command))
    application.add_handler(CommandHandler("vehicle", vehicle_command))
    application.add_handler(CommandHandler("pincode", pincode_command))
    application.add_handler(CommandHandler("stylish", stylish_command))
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
