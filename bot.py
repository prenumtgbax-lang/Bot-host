"""
Telegram Host Bot (Python & Node.js Cloud Hosting Platform)
Target Admin: 2014144404
Default Support: @YourDomains
Language: English (Styled UI / Custom Emojis & Button Colors)
Framework: Aiogram 3.x + SQLite3 + Subprocess Manager
"""

import os
import sys
import time
import html
import zipfile
import shutil
import asyncio
import sqlite3
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Tuple

import psutil
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile
)

# ─── BUTTON COLOR & STYLE MONKEY PATCHING (Aiogram 3.x / Bot API 7.0+) ─────
orig_ikb_dump = InlineKeyboardButton.model_dump
def new_ikb_dump(self, *args, **kwargs):
    d = orig_ikb_dump(self, *args, **kwargs)
    if hasattr(self, 'style') and self.style:
        d['style'] = self.style
    if hasattr(self, 'icon_custom_emoji_id') and self.icon_custom_emoji_id:
        d['icon_custom_emoji_id'] = self.icon_custom_emoji_id
    return d
InlineKeyboardButton.model_dump = new_ikb_dump

orig_kb_dump = KeyboardButton.model_dump
def new_kb_dump(self, *args, **kwargs):
    d = orig_kb_dump(self, *args, **kwargs)
    if hasattr(self, 'style') and self.style:
        d['style'] = self.style
    if hasattr(self, 'icon_custom_emoji_id') and self.icon_custom_emoji_id:
        d['icon_custom_emoji_id'] = self.icon_custom_emoji_id
    return d
KeyboardButton.model_dump = new_kb_dump

def ikb(text: str, callback_data: str = None, url: str = None, style: str = "primary", icon_id: str = None):
    btn = InlineKeyboardButton(text=text, callback_data=callback_data, url=url)
    if style: btn.style = style
    if icon_id: btn.icon_custom_emoji_id = icon_id
    return btn

def rkb(text: str, style: str = "primary", icon_id: str = None):
    btn = KeyboardButton(text=text)
    if style: btn.style = style
    if icon_id: btn.icon_custom_emoji_id = icon_id
    return btn

# ─── CUSTOM TELEGRAM EMOJIS MAPPING ────────────────────────────────────────
EMOJIS = {
    "wallet": "6073556477824472025",
    "balance": "6073556477824472025",
    "support": "6073400909814042854",
    "gift": "6071123877067494706",
    "telegram": "5472217698689638395",
    "up": "6204251568137574946",
    "download": "6204251568137574946",
    "sms": "6206112371308500200",
    "done": "6206378324273403309",
    "loading": "6206118633370818254",
    "notice": "6129433877791382400",
    "fire": "6131660139729522939",
    "bkash": "6237975191784266396",
    "nagad": "6235336389647407554",
    "binance": "6237610939902858402",
    "100": "6071051768861562054",
    "world": "6071096140168696563",
    "power": "6037220740967697584",
    "percent": "6039591820613127611",
    "arrow_right": "6244676977148564926",
    "date": "6244762094810436779",
    "delete": "5341319525142905998",
    "close": "5341718759532938160",
    "link": "6111396350883010682",
    "admin": "6111432544572414098",
    "trader": "6053216517732964810",
    "boom": "6052973985224728368",
    "crown": "6314576556278685829",
    "shield": "6314537472076291328",
    "diamond": "6314583342327011784",
    "speed": "6311939527963319025",
    "play": "6314426086394436542",
    "stop": "6314185920413179479",
    "restart": "6312314362644143742",
    "logs": "6314203594203602602",
    "money": "6312104703815590263",
    "search": "6311848921333245664",
    "sparkle": "6314480331831385997",
    "bell": "6314420734865185420",
    "star": "6314235179393096157"
}

def CE(key: str, fallback: str = "✨") -> str:
    emoji_id = EMOJIS.get(key, "6314480331831385997")
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
BOT_TOKEN = "8675366388:AAGFTx2E3aJKA3Ahw8BKyne_ZNsTSF0wcBI"
PRIMARY_ADMIN = 2014144404
BOT_STORAGE_DIR = "hosted_bots"
DB_FILE = "babyhost.db"

os.makedirs(BOT_STORAGE_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)

# Process container cache: bot_id -> subprocess.Popen
ACTIVE_PROCESSES: Dict[int, subprocess.Popen] = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ─── DATABASE INITIALIZATION ───────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Users Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0.0,
            plan_id INTEGER DEFAULT 0,
            plan_expiry TEXT DEFAULT NULL,
            is_banned INTEGER DEFAULT 0,
            joined_at TEXT,
            trial_claimed INTEGER DEFAULT 0
        )
    ''')
    
    # Bots Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bots (
            bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            bot_name TEXT,
            bot_type TEXT,
            folder_path TEXT,
            entry_file TEXT,
            status TEXT DEFAULT 'stopped',
            created_at TEXT
        )
    ''')
    
    # Plans Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            duration_days INTEGER,
            max_bots INTEGER,
            description TEXT
        )
    ''')
    
    # Force Channels Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS force_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE,
            title TEXT,
            invite_link TEXT
        )
    ''')

    # Deposit Requests
    cur.execute('''
        CREATE TABLE IF NOT EXISTS deposit_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            method TEXT,
            amount REAL,
            trx_id TEXT,
            photo_file_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    ''')
    
    # Settings
    cur.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Admins
    cur.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    ''')

    # Default Settings
    default_settings = {
        "fsub_enabled": "1",
        "bkash_number": "017XXXXXXXX",
        "nagad_number": "018XXXXXXXX",
        "binance_id": "12345678",
        "support_user": "@YourDomains",
        "trial_enabled": "1",
        "trial_limit": "1",
        "trial_days": "3",
        "trial_max_bots": "1",
        "trial_desc": "Experience high-speed cloud hosting for 3 days."
    }
    for k, v in default_settings.items():
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        
    cur.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (PRIMARY_ADMIN,))

    conn.commit()
    conn.close()

init_db()

# ─── DATABASE & USER HELPERS ───────────────────────────────────────────────
def get_db():
    return sqlite3.connect(DB_FILE)

def get_setting(key: str) -> str:
    with get_db() as conn:
        res = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return res[0] if res else ""

def set_setting(key: str, val: str):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))
        conn.commit()

def is_admin(user_id: int) -> bool:
    if user_id == PRIMARY_ADMIN:
        return True
    with get_db() as conn:
        res = conn.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone()
        return bool(res)

def get_or_create_user(user_id: int, username: str = "N/A"):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not user:
            conn.execute(
                "INSERT INTO users (user_id, username, joined_at) VALUES (?, ?, ?)",
                (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return user

def get_user_plan_info(user_id: int):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not user:
            return None
        
        plan_id = user[3]
        plan_expiry = user[4]
        current_bots = conn.execute("SELECT COUNT(*) FROM bots WHERE user_id=?", (user_id,)).fetchone()[0]

        if plan_id == 0 or not plan_expiry:
            return {
                "plan_name": "No Plan",
                "max_bots": 0,
                "current_bots": current_bots,
                "is_active": False,
                "remaining_str": "Expired / Inactive",
                "expiry": "N/A",
                "plan_id": 0
            }

        now = datetime.now()
        try:
            expiry_dt = datetime.strptime(plan_expiry, "%Y-%m-%d %H:%M:%S")
        except Exception:
            expiry_dt = now

        if now >= expiry_dt:
            conn.execute("UPDATE users SET plan_id=0, plan_expiry=NULL WHERE user_id=?", (user_id,))
            
            # Stop user bots upon expiry
            bots = conn.execute("SELECT bot_id FROM bots WHERE user_id=?", (user_id,)).fetchall()
            for (b_id,) in bots:
                stop_bot_instance(b_id)
                
            conn.commit()
            return {
                "plan_name": "Plan Expired",
                "max_bots": 0,
                "current_bots": current_bots,
                "is_active": False,
                "remaining_str": "Expired",
                "expiry": plan_expiry,
                "plan_id": 0
            }

        diff = expiry_dt - now
        days = diff.days
        hours = diff.seconds // 3600
        mins = (diff.seconds % 3600) // 60
        remaining_str = f"{days}d {hours}h {mins}m remaining"

        if plan_id == -1:
            plan_name = "Free Trial"
            max_bots = int(get_setting("trial_max_bots") or "1")
        else:
            p = conn.execute("SELECT name, max_bots FROM plans WHERE id=?", (plan_id,)).fetchone()
            plan_name = p[0] if p else "Active Plan"
            max_bots = p[1] if p else 1

        return {
            "plan_name": plan_name,
            "max_bots": max_bots,
            "current_bots": current_bots,
            "is_active": True,
            "remaining_str": remaining_str,
            "expiry": plan_expiry,
            "plan_id": plan_id
        }

# ─── PROCESS SUPERVISOR HELPER FUNCTIONS ───────────────────────────────────
def kill_process_tree(proc: subprocess.Popen):
    """Safely kills the process and all of its spawned children."""
    try:
        parent = psutil.Process(proc.pid)
        for child in parent.children(recursive=True):
            try:
                child.terminate()
            except Exception:
                pass
        parent.terminate()
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass

def launch_bot_instance(bot_id: int, folder: str, entry: str, btype: str) -> Tuple[bool, str]:
    """Starts the bot subprocess and verifies initial execution health."""
    log_file = os.path.join(folder, "output.log")
    
    # Kill any existing instance
    if bot_id in ACTIVE_PROCESSES:
        kill_process_tree(ACTIVE_PROCESSES[bot_id])
        del ACTIVE_PROCESSES[bot_id]

    cmd = [sys.executable, entry] if btype == "python" else ["node", entry]
    
    try:
        log_fp = open(log_file, "a", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=folder, stdout=log_fp, stderr=log_fp)
        ACTIVE_PROCESSES[bot_id] = proc
    except Exception as e:
        return False, f"Failed to execute command: {str(e)}"

    # Health check on launch
    time.sleep(1.2)
    poll_res = proc.poll()
    if poll_res is not None:
        del ACTIVE_PROCESSES[bot_id]
        with get_db() as conn:
            conn.execute("UPDATE bots SET status='stopped' WHERE bot_id=?", (bot_id,))
            conn.commit()
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                tail = "".join(f.readlines()[-15:])
        except Exception:
            tail = "Check output log file."
        return False, f"Process crashed immediately on launch (Exit code: {poll_res}):\n{tail}"

    with get_db() as conn:
        conn.execute("UPDATE bots SET status='running' WHERE bot_id=?", (bot_id,))
        conn.commit()

    return True, "Bot instance is running smoothly."

def stop_bot_instance(bot_id: int):
    """Gracefully terminates a bot instance and marks it stopped."""
    if bot_id in ACTIVE_PROCESSES:
        kill_process_tree(ACTIVE_PROCESSES[bot_id])
        del ACTIVE_PROCESSES[bot_id]
        
    with get_db() as conn:
        conn.execute("UPDATE bots SET status='stopped' WHERE bot_id=?", (bot_id,))
        conn.commit()

# ─── FSM STATES ─────────────────────────────────────────────────────────────
class UserStates(StatesGroup):
    uploading_bot = State()
    deposit_amount = State()
    deposit_trx = State()
    deposit_photo = State()

class AdminStates(StatesGroup):
    scanning_user = State()
    adjust_balance = State()
    add_plan = State()
    broadcast_msg = State()
    update_payment = State()
    update_support = State()
    add_admin = State()
    remove_admin = State()
    add_channel_link = State()
    add_channel_id = State()
    edit_trial_days = State()
    edit_trial_bots = State()
    edit_trial_limit = State()

# ─── KEYBOARDS & NAVIGATION SHIELD ─────────────────────────────────────────
MENU_BUTTON_TEXTS = ["Deploy Bot", "My Bots", "Plans", "Wallet & Balance", "Server Ping", "Support", "Admin Panel"]

def main_reply_keyboard(user_id: int):
    """Builds the reply keyboard. Admin Panel button is ONLY shown if user_id is admin."""
    kb = [
        [rkb("Deploy Bot", style="success", icon_id=EMOJIS["power"])],
        [rkb("My Bots", style="primary", icon_id=EMOJIS["trader"]), rkb("Plans", style="primary", icon_id=EMOJIS["diamond"])],
        [rkb("Wallet & Balance", style="success", icon_id=EMOJIS["wallet"])],
        [rkb("Server Ping", style="primary", icon_id=EMOJIS["speed"]), rkb("Support", style="primary", icon_id=EMOJIS["support"])]
    ]
    if is_admin(user_id):
        kb.append([rkb("Admin Panel", style="danger", icon_id=EMOJIS["admin"])])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_btn():
    return InlineKeyboardMarkup(
        inline_keyboard=[[ikb("Cancel Operation", callback_data="cancel_action", style="danger", icon_id=EMOJIS["close"])]]
    )

async def check_menu_button_escape(message: types.Message, state: FSMContext) -> bool:
    """If user clicks any reply keyboard button while inside a state, clear state and open that menu."""
    text = message.text or ""
    uid = message.from_user.id
    if text.startswith("/start"):
        await state.clear()
        await start_handler(message, state)
        return True
    if any(b in text for b in MENU_BUTTON_TEXTS):
        await state.clear()
        if "Deploy Bot" in text:
            await upload_prompt(message, state)
        elif "My Bots" in text:
            await my_bots_list(message)
        elif "Plans" in text:
            await plans_handler(message)
        elif "Wallet & Balance" in text:
            await wallet_handler(message)
        elif "Server Ping" in text:
            await ping_handler(message)
        elif "Support" in text:
            await support_handler(message)
        elif "Admin Panel" in text:
            if is_admin(uid):
                await admin_panel_root(message)
        return True
    return False

# ─── FORCE SUBSCRIBE MIDDLEWARE CHECK ──────────────────────────────────────
async def check_all_fsub(user_id: int) -> bool:
    if get_setting("fsub_enabled") != "1" or is_admin(user_id):
        return True
    with get_db() as conn:
        channels = conn.execute("SELECT chat_id FROM force_channels").fetchall()
    if not channels:
        return True
    for (chat_id,) in channels:
        try:
            cid = int(chat_id) if (chat_id.startswith("-") and chat_id[1:].isdigit()) or chat_id.isdigit() else chat_id
            member = await bot.get_chat_member(chat_id=cid, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logging.error(f"FSUB verification failed for {chat_id}: {e}")
            return False
    return True

def get_fsub_keyboard():
    with get_db() as conn:
        channels = conn.execute("SELECT title, invite_link FROM force_channels").fetchall()
    buttons = []
    for title, link in channels:
        buttons.append([ikb(f"Join {title}", url=link, style="primary", icon_id=EMOJIS["link"])])
    buttons.append([ikb("Verify Membership", callback_data="verify_fsub", style="success", icon_id=EMOJIS["done"])])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── START COMMAND & PROFILE ───────────────────────────────────────────────
@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext = None):
    if state:
        await state.clear()
        
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    
    user = get_or_create_user(user_id, username)
    if user[5] == 1:
        return await message.answer(
            f"{CE('notice')} <b>Account Restricted!</b>\n\nYour profile has been prohibited from accessing hosting infrastructure.",
            parse_mode="HTML"
        )

    if not await check_all_fsub(user_id):
        return await message.answer(
            f"{CE('shield')} <b>Channel Membership Required!</b>\n\n"
            f"Please subscribe to our verified updates channels below to unlock cloud hosting slots:",
            reply_markup=get_fsub_keyboard(),
            parse_mode="HTML"
        )

    plan_info = get_user_plan_info(user_id)
    balance = user[2]

    profile_text = (
        f"{CE('crown')} <b>NEBULA CLOUD HOSTING ENGINE</b> {CE('fire')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>Holder:</b> <code>{message.from_user.full_name}</code>\n"
        f"{CE('link')} <b>User ID:</b> <code>{user_id}</code>\n"
        f"{CE('telegram')} <b>Username:</b> @{username}\n"
        f"{CE('wallet')} <b>Balance:</b> <code>{balance:.2f} ৳</code>\n"
        f"{CE('diamond')} <b>Active Plan:</b> <code>{plan_info['plan_name']}</code>\n"
        f"{CE('date')} <b>Validity:</b> <code>{plan_info['remaining_str']}</code>\n"
        f"{CE('power')} <b>Deployments:</b> <code>{plan_info['current_bots']}/{plan_info['max_bots']} Used</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('speed')} <i>High-performance isolated Subprocess execution (Python & Node.js).</i>\n"
        f"<i>Select an option from the menu buttons below:</i>"
    )
    await message.answer(profile_text, reply_markup=main_reply_keyboard(user_id), parse_mode="HTML")

@dp.callback_query(F.data == "verify_fsub")
async def verify_fsub_callback(callback: types.CallbackQuery):
    if await check_all_fsub(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer(
            f"{CE('done')} <b>Verification Complete!</b> Welcome to Nebula Cloud.",
            reply_markup=main_reply_keyboard(callback.from_user.id),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ You still haven't joined all required channels!", show_alert=True)

# ─── PING & HOST METRICS ───────────────────────────────────────────────────
@dp.message(F.text.contains("Server Ping"))
async def ping_handler(message: types.Message):
    start = time.time()
    msg = await message.answer(f"{CE('loading')} <i>Querying host hardware parameters...</i>", parse_mode="HTML")
    latency = round((time.time() - start) * 1000, 2)
    
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    diag_text = (
        f"{CE('speed')} <b>HOST HARDWARE DIAGNOSTICS</b> {CE('power')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('done')} <b>Network Latency:</b> <code>{latency} ms</code>\n"
        f"{CE('boom')} <b>CPU Usage:</b> <code>{cpu_usage}%</code>\n"
        f"{CE('diamond')} <b>RAM Load:</b> <code>{ram.percent}%</code> ({round(ram.used / (1024**3), 2)}GB / {round(ram.total / (1024**3), 2)}GB)\n"
        f"{CE('world')} <b>Disk Storage:</b> <code>{disk.percent}%</code> ({round(disk.free / (1024**3), 2)}GB Free)\n"
        f"{CE('trader')} <b>Active Worker PIDs:</b> <code>{len(ACTIVE_PROCESSES)}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('shield')} <b>Server Condition: 100% Operational & Safe</b>"
    )
    await msg.edit_text(diag_text, parse_mode="HTML")

# ─── SUPPORT DESK ──────────────────────────────────────────────────────────
@dp.message(F.text.contains("Support"))
async def support_handler(message: types.Message):
    handle = get_setting("support_user") or "@YourDomains"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [ikb("Contact Support Desk", url=f"https://t.me/{handle.replace('@', '')}", style="primary", icon_id=EMOJIS["support"])]
    ])
    await message.answer(
        f"{CE('support')} <b>DEDICATED HELPDESK & CARE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Need assistance with dependencies, deployments, or custom resource quotas?\n\n"
        f"{CE('link')} <b>Official Consultant:</b> <code>{handle}</code>\n"
        f"{CE('date')} <b>Availability:</b> 24/7 Priority Support",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ─── WALLET & BALANCE ──────────────────────────────────────────────────────
@dp.message(F.text.contains("Wallet & Balance"))
async def wallet_handler(message: types.Message):
    user_id = message.from_user.id
    user = get_or_create_user(user_id, message.from_user.username or "N/A")
    balance = user[2]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [ikb("Add Balance (Deposit)", callback_data="start_deposit", style="success", icon_id=EMOJIS["wallet"])],
        [ikb("Browse Subscriptions", callback_data="view_plans", style="primary", icon_id=EMOJIS["diamond"])]
    ])
    
    await message.answer(
        f"{CE('wallet')} <b>YOUR PERSONAL CLOUD WALLET</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('money')} <b>Current Balance:</b> <code>{balance:.2f} ৳</code>\n"
        f"{CE('arrow_right')} <i>Use your available wallet balance to purchase and activate hosting plans.</i>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ─── PLANS & SUBSCRIPTIONS (REAL-TIME EXPIRY & REMAINING TIME) ─────────────
@dp.message(F.text.contains("Plans"))
@dp.callback_query(F.data == "view_plans")
async def plans_handler(event: types.Message | types.CallbackQuery):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id

    user = get_or_create_user(user_id, event.from_user.username or "N/A")
    plan_info = get_user_plan_info(user_id)

    with get_db() as conn:
        plans = conn.execute("SELECT * FROM plans ORDER BY price ASC").fetchall()

    text = (
        f"{CE('diamond')} <b>CLOUD HOSTING SUBSCRIPTIONS</b> {CE('fire')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('crown')} <b>Active Tier:</b> <code>{plan_info['plan_name']}</code>\n"
        f"{CE('date')} <b>Remaining Validity:</b> <code>{plan_info['remaining_str']}</code>\n"
        f"{CE('power')} <b>Deployment Slots:</b> <code>{plan_info['current_bots']}/{plan_info['max_bots']} Used</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    buttons = []
    
    # 1. Free Trial Plan
    trial_enabled = get_setting("trial_enabled") == "1"
    trial_days = get_setting("trial_days") or "3"
    trial_max_bots = get_setting("trial_max_bots") or "1"
    trial_limit = int(get_setting("trial_limit") or "1")
    trial_desc = get_setting("trial_desc") or "Fast cloud hosting trial"
    trial_claimed = user[7] if user and len(user) > 7 else 0

    if trial_enabled:
        text += (
            f"{CE('gift')} <b>Tier:</b> <code>Free Trial</code>\n"
            f"{CE('money')} <b>Price:</b> <code>0.00 ৳</code>\n"
            f"{CE('date')} <b>Duration:</b> <code>{trial_days} Days</code>\n"
            f"{CE('power')} <b>Quota:</b> <code>{trial_max_bots} Bot Slot(s)</code>\n"
            f"{CE('notice')} <b>Details:</b> <i>{trial_desc}</i>\n"
            f"{CE('trader')} <b>Claimed:</b> <code>{trial_claimed}/{trial_limit} Time(s)</code>\n"
            f"────────────────────────────\n"
        )
        if plan_info["is_active"] and plan_info["plan_id"] == -1:
            buttons.append([ikb(f"Free Trial Active ({plan_info['remaining_str']})", callback_data="plan_already_active", style="success", icon_id=EMOJIS["done"])])
        elif trial_claimed >= trial_limit:
            buttons.append([ikb("Free Trial Limit Exhausted", callback_data="trial_limit_reached", style="danger", icon_id=EMOJIS["close"])])
        else:
            buttons.append([ikb(f"Claim Free Trial ({trial_days} Days)", callback_data="claim_free_trial", style="success", icon_id=EMOJIS["gift"])])

    # 2. Paid Subscription Plans
    if not plans:
        text += f"<i>No paid subscription tiers are currently available.</i>\n"

    for p in plans:
        text += (
            f"{CE('crown')} <b>Tier:</b> <code>{p[1]}</code>\n"
            f"{CE('money')} <b>Price:</b> <code>{p[2]:.2f} ৳</code>\n"
            f"{CE('date')} <b>Duration:</b> <code>{p[3]} Days</code>\n"
            f"{CE('power')} <b>Quota:</b> <code>{p[4]} Bot Slot(s)</code>\n"
            f"{CE('notice')} <b>Details:</b> <i>{p[5]}</i>\n"
            f"────────────────────────────\n"
        )
        if plan_info["is_active"] and plan_info["plan_id"] == p[0]:
            buttons.append([ikb(f"{p[1]} Active ({plan_info['remaining_str']})", callback_data="plan_already_active", style="success", icon_id=EMOJIS["done"])])
        else:
            buttons.append([ikb(f"Purchase {p[1]} - {p[2]:.2f} ৳ ({p[3]} Days)", callback_data=f"buyplan_{p[0]}", style="primary", icon_id=EMOJIS["arrow_right"])])
        
    buttons.append([ikb("Add Balance to Wallet", callback_data="start_deposit", style="success", icon_id=EMOJIS["wallet"])])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=markup, parse_mode="HTML")

@dp.callback_query(F.data == "plan_already_active")
async def plan_active_alert(callback: types.CallbackQuery):
    await callback.answer("⚠️ This subscription tier is already active on your account! Renew when it expires.", show_alert=True)

@dp.callback_query(F.data == "trial_limit_reached")
async def trial_limit_alert(callback: types.CallbackQuery):
    await callback.answer("❌ You have already exhausted your free trial claim allowance!", show_alert=True)

@dp.callback_query(F.data == "claim_free_trial")
async def claim_trial_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_or_create_user(user_id, callback.from_user.username or "N/A")
    plan_info = get_user_plan_info(user_id)

    trial_limit = int(get_setting("trial_limit") or "1")
    trial_claimed = user[7] if len(user) > 7 else 0
    trial_days = int(get_setting("trial_days") or "3")

    if plan_info["is_active"] and plan_info["plan_id"] == -1:
        return await callback.answer("⚠️ Free trial is already active on your account!", show_alert=True)
    if trial_claimed >= trial_limit:
        return await callback.answer("❌ You have reached your free trial limit!", show_alert=True)

    expiry = (datetime.now() + timedelta(days=trial_days)).strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET plan_id=-1, plan_expiry=?, trial_claimed=trial_claimed+1 WHERE user_id=?",
            (expiry, user_id)
        )
        conn.commit()

    await callback.message.edit_text(
        f"{CE('done')} <b>Free Trial Activated!</b>\n\n"
        f"{CE('date')} <b>Validity:</b> <code>{trial_days} Days</code> (Expires: <code>{expiry}</code>)\n"
        f"{CE('power')} <b>Allowed Bots:</b> <code>{get_setting('trial_max_bots') or '1'}</code>\n\n"
        f"You can now proceed to <b>Deploy Bot</b> from the main menu.",
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("buyplan_"))
async def process_buy_plan(callback: types.CallbackQuery):
    plan_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    with get_db() as conn:
        plan = conn.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
        user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        
        if not plan:
            return await callback.answer("❌ Invalid Subscription Tier!", show_alert=True)
            
        cost = plan[2]
        if user[2] < cost:
            return await callback.answer(f"❌ Insufficient Balance! You need {cost:.2f} ৳. Please deposit first.", show_alert=True)

        plan_info = get_user_plan_info(user_id)
        if plan_info["is_active"] and plan_info["plan_id"] == plan_id:
            return await callback.answer("⚠️ You already have this plan active!", show_alert=True)
            
        new_balance = user[2] - cost
        expiry = (datetime.now() + timedelta(days=plan[3])).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE users SET balance=?, plan_id=?, plan_expiry=? WHERE user_id=?", (new_balance, plan_id, expiry, user_id))
        conn.commit()
        
    await callback.message.edit_text(
        f"{CE('done')} <b>Subscription Activated!</b>\n\n"
        f"{CE('crown')} <b>Tier:</b> <code>{plan[1]}</code>\n"
        f"{CE('money')} <b>Paid:</b> <code>{cost:.2f} ৳</code>\n"
        f"{CE('date')} <b>Valid For:</b> <code>{plan[3]} Days</code> (Expires: <code>{expiry}</code>)\n"
        f"{CE('power')} <b>Deployment Slots:</b> <code>{plan[4]} Bot(s)</code>\n\n"
        f"<i>Your server slots have been updated.</i>",
        parse_mode="HTML"
    )

# ─── DEPOSIT & PAYMENT SYSTEM (WITH NAVIGATION ESCAPE) ─────────────────────
@dp.callback_query(F.data == "start_deposit")
async def deposit_methods_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [ikb("bKash Personal", callback_data="paymeth_bKash", style="primary", icon_id=EMOJIS["bkash"])],
        [ikb("Nagad Personal", callback_data="paymeth_Nagad", style="primary", icon_id=EMOJIS["nagad"])],
        [ikb("Binance Pay", callback_data="paymeth_Binance", style="primary", icon_id=EMOJIS["binance"])],
        [ikb("Cancel", callback_data="cancel_action", style="danger", icon_id=EMOJIS["close"])]
    ])
    await callback.message.edit_text(
        f"{CE('wallet')} <b>SELECT PAYMENT CHANNEL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Choose your desired payment gateway from below to load money into your wallet:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("paymeth_"))
async def method_chosen(callback: types.CallbackQuery, state: FSMContext):
    method = callback.data.split("_")[1]
    await state.update_data(method=method)

    number = ""
    if method == "bKash":
        number = get_setting("bkash_number")
    elif method == "Nagad":
        number = get_setting("nagad_number")
    elif method == "Binance":
        number = get_setting("binance_id")

    text = (
        f"{CE('wallet')} <b>PAYMENT INSTRUCTIONS ({method.upper()})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Send Money to our official address below:\n\n"
        f"{CE('link')} <b>Account / Pay ID:</b> <code>{number}</code> (Tap to Copy)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('arrow_right')} <b>Step 1:</b> Enter the amount you have sent (in ৳):"
    )
    await callback.message.edit_text(text, reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(UserStates.deposit_amount)

@dp.message(UserStates.deposit_amount)
async def process_deposit_amount(message: types.Message, state: FSMContext):
    if await check_menu_button_escape(message, state):
        return

    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await message.answer(
            f"{CE('close')} <b>Invalid amount!</b> Please write numerical figures only (e.g. <code>100</code>).",
            reply_markup=cancel_btn(),
            parse_mode="HTML"
        )

    await state.update_data(amount=amount)
    await message.answer(
        f"{CE('sms')} <b>Step 2:</b> Please provide your transaction ID (TrxID):\n\n"
        f"<i>Example:</i> <code>9JAHSD9812</code>",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(UserStates.deposit_trx)

@dp.message(UserStates.deposit_trx)
async def process_deposit_trx(message: types.Message, state: FSMContext):
    if await check_menu_button_escape(message, state):
        return

    trx_id = message.text.strip()
    await state.update_data(trx_id=trx_id)
    await message.answer(
        f"{CE('up')} <b>Step 3:</b> Now upload a clear <b>screenshot / proof photo</b> of your payment transaction:",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(UserStates.deposit_photo)

@dp.message(UserStates.deposit_photo, F.photo)
async def process_deposit_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    
    photo_file_id = message.photo[-1].file_id
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    method = data['method']
    amount = data['amount']
    trx_id = data['trx_id']
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO deposit_requests (user_id, method, amount, trx_id, photo_file_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, method, amount, trx_id, photo_file_id, now_str)
        )
        conn.commit()
        req_id = cur.lastrowid

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            ikb("Approve", callback_data=f"depapp_{req_id}", style="success", icon_id=EMOJIS["done"]),
            ikb("Reject", callback_data=f"deprej_{req_id}", style="danger", icon_id=EMOJIS["close"])
        ]
    ])
    
    admin_caption = (
        f"{CE('notice')} <b>NEW DEPOSIT REQUEST #{req_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>User:</b> {message.from_user.full_name}\n"
        f"{CE('link')} <b>User ID:</b> <code>{user_id}</code>\n"
        f"{CE('telegram')} <b>Username:</b> @{username}\n"
        f"{CE('wallet')} <b>Method:</b> <code>{method}</code>\n"
        f"{CE('money')} <b>Amount:</b> <code>{amount:.2f} ৳</code>\n"
        f"{CE('sms')} <b>Trx ID:</b> <code>{trx_id}</code>\n"
        f"{CE('date')} <b>Time:</b> <code>{now_str}</code>"
    )

    try:
        await bot.send_photo(PRIMARY_ADMIN, photo=photo_file_id, caption=admin_caption, reply_markup=admin_kb, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error alerting admin of deposit: {e}")

    await message.answer(
        f"{CE('done')} <b>Deposit Request Submitted!</b>\n\n"
        f"Your transaction details and screenshot have been delivered to our billing administrators. "
        f"Your balance will reflect automatically once confirmed.",
        reply_markup=main_reply_keyboard(user_id),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("depapp_"))
async def admin_approve_deposit(callback: types.CallbackQuery):
    req_id = int(callback.data.split("_")[1])
    with get_db() as conn:
        req = conn.execute("SELECT * FROM deposit_requests WHERE id=?", (req_id,)).fetchone()
        if not req or req[6] != "pending":
            return await callback.answer("⚠️ This request has already been processed!", show_alert=True)
            
        user_id, amount = req[1], req[3]
        conn.execute("UPDATE deposit_requests SET status='approved' WHERE id=?", (req_id,))
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
        conn.commit()

    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n{CE('done')} <b>STATUS: APPROVED BY ADMIN</b>",
        parse_mode="HTML"
    )
    try:
        await bot.send_message(
            user_id,
            f"{CE('done')} <b>Deposit Approved!</b>\n\n"
            f"<code>{amount:.2f} ৳</code> has been successfully credited to your cloud wallet.",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("Deposit Approved & Balance Added!", show_alert=True)

@dp.callback_query(F.data.startswith("deprej_"))
async def admin_reject_deposit(callback: types.CallbackQuery):
    req_id = int(callback.data.split("_")[1])
    with get_db() as conn:
        req = conn.execute("SELECT * FROM deposit_requests WHERE id=?", (req_id,)).fetchone()
        if not req or req[6] != "pending":
            return await callback.answer("⚠️ This request has already been processed!", show_alert=True)
            
        user_id = req[1]
        conn.execute("UPDATE deposit_requests SET status='rejected' WHERE id=?", (req_id,))
        conn.commit()

    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n{CE('close')} <b>STATUS: REJECTED BY ADMIN</b>",
        parse_mode="HTML"
    )
    try:
        await bot.send_message(
            user_id,
            f"{CE('close')} <b>Deposit Request Declined</b>\n\n"
            f"Your submission for TrxID <code>{req[4]}</code> was rejected by administrators. Contact support if this is a discrepancy.",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("Deposit Rejected!", show_alert=True)

# ─── UPLOAD & BOT HOSTING ENGINE (STRICT PLAN LIMIT ENFORCEMENT) ───────────
@dp.message(F.text.contains("Deploy Bot"))
async def upload_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    get_or_create_user(user_id, message.from_user.username or "N/A")
    plan_info = get_user_plan_info(user_id)

    if not plan_info or not plan_info["is_active"]:
        return await message.answer(
            f"{CE('notice')} <b>No Active Subscription Found!</b>\n\n"
            f"You require an active hosting package or Free Trial to launch bots.\n"
            f"Check out <b>Plans</b> from the main menu to claim a trial or purchase a plan.",
            parse_mode="HTML"
        )
        
    if plan_info["current_bots"] >= plan_info["max_bots"]:
        return await message.answer(
            f"{CE('close')} <b>Container Quota Full!</b>\n\n"
            f"Your active tier allows a maximum of <code>{plan_info['max_bots']}</code> bot deployment(s).\n"
            f"Currently deployed: <code>{plan_info['current_bots']}/{plan_info['max_bots']}</code>.\n\n"
            f"Please upgrade your plan or delete unused instances via <b>My Bots</b>.",
            parse_mode="HTML"
        )

    await message.answer(
        f"{CE('up')} <b>DEPLOY SOURCE ARCHIVE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Active Tier: <code>{plan_info['plan_name']}</code> ({plan_info['current_bots']}/{plan_info['max_bots']} Slots Used)\n\n"
        f"Please send your source code file document:\n"
        f"• <b>Single Source:</b> <code>.py</code> or <code>.js</code>\n"
        f"• <b>Project Archive:</b> <code>.zip</code> (must include <code>main.py</code> or <code>index.js</code>)\n\n"
        f"{CE('loading')} <i>Awaiting file document...</i>",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(UserStates.uploading_bot)

@dp.message(UserStates.uploading_bot, F.document)
async def process_file_upload(message: types.Message, state: FSMContext):
    doc = message.document
    filename = doc.file_name or "archive.zip"
    ext = os.path.splitext(filename)[1].lower()
    user_id = message.from_user.id
    
    if ext not in [".py", ".js", ".zip"]:
        return await message.answer(
            f"{CE('close')} <b>Unsupported File Extension!</b>\n"
            f"Allowed formats: <code>.py</code>, <code>.js</code>, or <code>.zip</code>",
            reply_markup=cancel_btn(),
            parse_mode="HTML"
        )
        
    status_msg = await message.answer(f"{CE('loading')} <i>Step 1/4: Downloading & Allocating isolated container...</i>", parse_mode="HTML")
    
    timestamp = int(time.time())
    bot_dir = os.path.join(BOT_STORAGE_DIR, f"{user_id}_{timestamp}")
    os.makedirs(bot_dir, exist_ok=True)
    
    file_path = os.path.join(bot_dir, filename)
    file_info = await bot.get_file(doc.file_id)
    await bot.download_file(file_info.file_path, destination=file_path)
    
    entry_file = filename
    bot_type = "python" if ext == ".py" else ("nodejs" if ext == ".js" else "unknown")
    
    # ── Step 2: Extraction & Verification ──
    if ext == ".zip":
        await status_msg.edit_text(f"{CE('loading')} <i>Step 2/4: Unpacking ZIP and validating structure...</i>", parse_mode="HTML")
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(bot_dir)
            os.remove(file_path)
        except Exception as e:
            shutil.rmtree(bot_dir, ignore_errors=True)
            return await status_msg.edit_text(f"{CE('close')} <b>Archive Extraction Failed!</b>\nError: <code>{html.escape(str(e))}</code>", parse_mode="HTML")
            
        files = os.listdir(bot_dir)
        if "main.py" in files:
            entry_file = "main.py"
            bot_type = "python"
        elif "bot.py" in files:
            entry_file = "bot.py"
            bot_type = "python"
        elif "index.js" in files:
            entry_file = "index.js"
            bot_type = "nodejs"
        elif "main.js" in files:
            entry_file = "main.js"
            bot_type = "nodejs"
        else:
            py_files = [f for f in files if f.endswith(".py")]
            if py_files:
                entry_file = py_files[0]
                bot_type = "python"
            else:
                shutil.rmtree(bot_dir, ignore_errors=True)
                return await status_msg.edit_text(
                    f"{CE('close')} <b>No Valid Entrypoint Located!</b>\n"
                    f"Your zip archive must contain <code>main.py</code>, <code>bot.py</code>, or <code>index.js</code>.",
                    parse_mode="HTML"
                )

    # ── Step 3: Dependencies Resolution ──
    req_file = os.path.join(bot_dir, "requirements.txt")
    pip_status_note = "None (No requirements.txt found)"
    if os.path.exists(req_file):
        await status_msg.edit_text(f"{CE('loading')} <i>Step 3/4: Resolving & Installing packages from requirements.txt...</i>", parse_mode="HTML")
        install_proc = subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if install_proc.returncode == 0:
            pip_status_note = "✅ Installed Successfully"
        else:
            err_log = install_proc.stderr.decode('utf-8', errors='replace')[:250]
            pip_status_note = f"⚠️ Warning during install:\n<code>{html.escape(err_log)}</code>"

    # ── Step 4: Syntax Pre-flight Check ──
    syntax_status_note = "N/A"
    if bot_type == "python":
        entry_full_path = os.path.join(bot_dir, entry_file)
        compile_check = subprocess.run([sys.executable, "-m", "py_compile", entry_full_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if compile_check.returncode == 0:
            syntax_status_note = "✅ Passed (No syntax errors detected)"
        else:
            err_text = compile_check.stderr.decode('utf-8', errors='replace')[:250]
            syntax_status_note = f"⚠️ Syntax Warning:\n<code>{html.escape(err_text)}</code>"

    # Save to Database
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bots (user_id, bot_name, bot_type, folder_path, entry_file, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, filename, bot_type, bot_dir, entry_file, "stopped", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        bot_id = cur.lastrowid
        
    await state.clear()
    
    diagnostic_report = (
        f"{CE('done')} <b>DEPLOYMENT COMPLETED & VERIFIED!</b> {CE('fire')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('link')} <b>Instance ID:</b> <code>#{bot_id}</code>\n"
        f"{CE('arrow_right')} <b>Primary File:</b> <code>{entry_file}</code>\n"
        f"{CE('power')} <b>Runtime:</b> <code>{bot_type.upper()}</code>\n"
        f"{CE('diamond')} <b>Dependencies:</b> {pip_status_note}\n"
        f"{CE('speed')} <b>Pre-flight Check:</b> {syntax_status_note}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎉 <i>Your container is provisioned and ready to run!</i>\n"
        f"Tap <b>My Bots</b> to launch and manage your instance."
    )
    
    await status_msg.edit_text(diagnostic_report, parse_mode="HTML")

# ─── MY BOTS MANAGEMENT (FULL CONTROLS & MONITORING) ───────────────────────
@dp.message(F.text.contains("My Bots"))
async def my_bots_list(message: types.Message):
    user_id = message.from_user.id
    with get_db() as conn:
        bots = conn.execute("SELECT bot_id, bot_name, status FROM bots WHERE user_id=?", (user_id,)).fetchall()
        
    if not bots:
        return await message.answer(
            f"{CE('notice')} <b>No deployed instances found.</b> Use <b>Deploy Bot</b> to upload one.",
            parse_mode="HTML"
        )

    buttons = []
    for b in bots:
        is_running = b[2] == "running" and b[0] in ACTIVE_PROCESSES and ACTIVE_PROCESSES[b[0]].poll() is None
        icon_id = EMOJIS["done"] if is_running else EMOJIS["close"]
        status_text = "LIVE" if is_running else "STOPPED"
        buttons.append([ikb(f"[{status_text}] #{b[0]} - {b[1]}", callback_data=f"managebot_{b[0]}", style="primary", icon_id=icon_id)])
        
    await message.answer(f"{CE('trader')} <b>SELECT CONTAINER INSTANCE:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("managebot_"))
async def bot_controls(callback: types.CallbackQuery):
    bot_id = int(callback.data.split("_")[1])
    with get_db() as conn:
        b = conn.execute("SELECT * FROM bots WHERE bot_id=?", (bot_id,)).fetchone()
        
    if not b:
        return await callback.answer("Instance not located!", show_alert=True)

    is_running = b[6] == "running" and bot_id in ACTIVE_PROCESSES and ACTIVE_PROCESSES[bot_id].poll() is None
    status_icon = f"{CE('done')} LIVE (Running)" if is_running else f"{CE('close')} STOPPED"
    
    res_usage_str = "Offline"
    if is_running:
        try:
            p = psutil.Process(ACTIVE_PROCESSES[bot_id].pid)
            mem_mb = round(p.memory_info().rss / (1024 * 1024), 2)
            cpu_p = p.cpu_percent(interval=None)
            res_usage_str = f"CPU: {cpu_p}% | RAM: {mem_mb} MB"
        except Exception:
            res_usage_str = "Measuring..."

    text = (
        f"{CE('diamond')} <b>BOT CONTAINER CONTROLLER #{b[0]}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('link')} <b>Name:</b> <code>{b[2]}</code>\n"
        f"{CE('power')} <b>Runtime Engine:</b> <code>{b[3].upper()}</code>\n"
        f"{CE('arrow_right')} <b>Primary File:</b> <code>{b[5]}</code>\n"
        f"{CE('speed')} <b>Status:</b> {status_icon}\n"
        f"{CE('boom')} <b>Resource Load:</b> <code>{res_usage_str}</code>\n"
        f"{CE('date')} <b>Deployed On:</b> <code>{b[7]}</code>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            ikb("Start", callback_data=f"actbot_start_{b[0]}", style="success", icon_id=EMOJIS["play"]),
            ikb("Stop", callback_data=f"actbot_stop_{b[0]}", style="danger", icon_id=EMOJIS["stop"]),
            ikb("Restart", callback_data=f"actbot_restart_{b[0]}", style="primary", icon_id=EMOJIS["restart"])
        ],
        [
            ikb("Logs", callback_data=f"actbot_logs_{b[0]}", style="primary", icon_id=EMOJIS["logs"]),
            ikb("Backup Code", callback_data=f"actbot_download_{b[0]}", style="success", icon_id=EMOJIS["download"])
        ],
        [
            ikb("Delete Bot", callback_data=f"actbot_delete_{b[0]}", style="danger", icon_id=EMOJIS["delete"]),
            ikb("Back", callback_data="back_mybots", style="primary", icon_id=EMOJIS["arrow_right"])
        ]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "back_mybots")
async def back_to_bots(callback: types.CallbackQuery):
    await callback.message.delete()
    await my_bots_list(callback.message)

@dp.callback_query(F.data.startswith("actbot_"))
async def execute_bot_action(callback: types.CallbackQuery):
    action, bot_id_str = callback.data.split("_")[1], callback.data.split("_")[2]
    bot_id = int(bot_id_str)
    
    with get_db() as conn:
        bot_row = conn.execute("SELECT * FROM bots WHERE bot_id=?", (bot_id,)).fetchone()
        
    if not bot_row:
        return await callback.answer("Instance record not found!", show_alert=True)

    folder, entry, btype = bot_row[4], bot_row[5], bot_row[3]
    log_file = os.path.join(folder, "output.log")

    # START
    if action == "start":
        if bot_id in ACTIVE_PROCESSES and ACTIVE_PROCESSES[bot_id].poll() is None:
            return await callback.answer("⚠️ Bot process is already active and running!", show_alert=True)
            
        success, msg = launch_bot_instance(bot_id, folder, entry, btype)
        if success:
            await callback.answer("✅ Bot process started successfully!", show_alert=True)
        else:
            return await callback.message.answer(
                f"{CE('notice')} <b>Launch Failure Warning (#{bot_id})!</b>\n"
                f"The bot process failed to stay alive:\n<pre>{html.escape(msg)}</pre>",
                parse_mode="HTML"
            )

    # STOP
    elif action == "stop":
        stop_bot_instance(bot_id)
        await callback.answer("🛑 Instance subprocess stopped!", show_alert=True)

    # RESTART
    elif action == "restart":
        stop_bot_instance(bot_id)
        time.sleep(0.5)
        success, msg = launch_bot_instance(bot_id, folder, entry, btype)
        if success:
            await callback.answer("🔄 Instance rebooted successfully!", show_alert=True)
        else:
            return await callback.message.answer(
                f"{CE('notice')} <b>Reboot Failure Warning (#{bot_id})!</b>\n<pre>{html.escape(msg)}</pre>",
                parse_mode="HTML"
            )

    # LOGS
    elif action == "logs":
        if not os.path.exists(log_file):
            return await callback.answer("No console log file generated yet.", show_alert=True)
            
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                tail = "".join(lines[-30:]) or "Output log file is clean and empty."
        except Exception as e:
            tail = f"Error reading log output: {e}"

        tail_escaped = html.escape(tail)
        return await callback.message.answer(
            f"{CE('logs')} <b>TERMINAL OUTPUT (#{bot_id}):</b>\n<pre>{tail_escaped}</pre>",
            parse_mode="HTML"
        )

    # DOWNLOAD BACKUP
    elif action == "download":
        await callback.answer("📦 Packaging source archive...")
        zip_archive_path = os.path.join(BOT_STORAGE_DIR, f"backup_bot_{bot_id}")
        shutil.make_archive(zip_archive_path, 'zip', folder)
        full_zip = f"{zip_archive_path}.zip"
        
        await callback.message.answer_document(
            FSInputFile(full_zip),
            caption=f"{CE('done')} <b>Complete Source Code Backup for Instance #{bot_id}</b>",
            parse_mode="HTML"
        )
        if os.path.exists(full_zip):
            os.remove(full_zip)
        return

    # DELETE
    elif action == "delete":
        stop_bot_instance(bot_id)
            
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
            
        with get_db() as conn:
            conn.execute("DELETE FROM bots WHERE bot_id=?", (bot_id,))
            conn.commit()
            
        await callback.message.delete()
        return await callback.message.answer(
            f"{CE('delete')} <b>Container instance #{bot_id} completely removed from servers.</b>",
            parse_mode="HTML"
        )

    await bot_controls(callback)

# ─── ADMIN PANEL & COMPREHENSIVE PLAN MANAGER ──────────────────────────────
@dp.message(F.text.contains("Admin Panel"))
async def admin_panel_root(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer(f"{CE('close')} <b>Permission Denied! Super Administrators Only.</b>", parse_mode="HTML")

    with get_db() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_bots = conn.execute("SELECT COUNT(*) FROM bots").fetchone()[0]
        running_bots = len([p for p in ACTIVE_PROCESSES.values() if p.poll() is None])
        plans_sold = conn.execute("SELECT COUNT(*) FROM users WHERE plan_id > 0").fetchone()[0]

    admin_text = (
        f"{CE('crown')} <b>SUPER ADMINISTRATOR CONTROL CENTER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>Total Users:</b> <code>{total_users}</code>\n"
        f"{CE('power')} <b>Total Containers:</b> <code>{total_bots}</code>\n"
        f"{CE('done')} <b>Active Worker Processes:</b> <code>{running_bots}</code>\n"
        f"{CE('diamond')} <b>Active Subscriptions:</b> <code>{plans_sold}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Configure servers, plans, trial systems, and channels below:</i>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [ikb("Scan & Manage User", callback_data="adm_scan_user", style="primary", icon_id=EMOJIS["search"]), ikb("All Hosted Bots", callback_data="adm_all_bots", style="primary", icon_id=EMOJIS["trader"])],
        [ikb("Manage Paid Plans", callback_data="adm_manage_plans", style="primary", icon_id=EMOJIS["diamond"]), ikb("Free Trial Settings", callback_data="adm_trial_settings", style="primary", icon_id=EMOJIS["gift"])],
        [ikb("Force Join Channels", callback_data="adm_manage_channels", style="primary", icon_id=EMOJIS["link"]), ikb("Payment Gateways", callback_data="adm_payments", style="primary", icon_id=EMOJIS["wallet"])],
        [ikb("Broadcast Announcement", callback_data="adm_broadcast", style="primary", icon_id=EMOJIS["notice"]), ikb("Manage Admins", callback_data="adm_manage_admins", style="primary", icon_id=EMOJIS["shield"])],
        [ikb("Update Support Desk", callback_data="adm_support", style="primary", icon_id=EMOJIS["support"])]
    ])
    await message.answer(admin_text, reply_markup=keyboard, parse_mode="HTML")

# 1. Force Join Channels Manager
@dp.callback_query(F.data == "adm_manage_channels")
async def adm_manage_channels_menu(callback: types.CallbackQuery):
    with get_db() as conn:
        channels = conn.execute("SELECT id, title, chat_id FROM force_channels").fetchall()
    fsub_status = "ENABLED" if get_setting("fsub_enabled") == "1" else "DISABLED"

    text = (
        f"{CE('link')} <b>FORCE SUBSCRIBE CHANNELS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Status: <b>{fsub_status}</b>\n\n"
    )
    buttons = []
    for cid, title, chat_id in channels:
        text += f"• <b>{title}</b> (<code>{chat_id}</code>)\n"
        buttons.append([ikb(f"Remove {title}", callback_data=f"delchan_{cid}", style="danger", icon_id=EMOJIS["delete"])])

    toggle_btn_text = "Disable Force Join" if fsub_status == "ENABLED" else "Enable Force Join"
    buttons.append([ikb(toggle_btn_text, callback_data="toggle_fsub_sys", style="primary", icon_id=EMOJIS["restart"])])
    buttons.append([ikb("Add New Channel", callback_data="add_new_channel_link", style="success", icon_id=EMOJIS["arrow_right"])])
    buttons.append([ikb("Back to Admin Panel", callback_data="back_admin_root", style="danger", icon_id=EMOJIS["close"])])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data == "toggle_fsub_sys")
async def toggle_fsub_handler(callback: types.CallbackQuery):
    curr = get_setting("fsub_enabled")
    set_setting("fsub_enabled", "0" if curr == "1" else "1")
    await callback.answer("Force subscribe status toggled!", show_alert=True)
    await adm_manage_channels_menu(callback)

@dp.callback_query(F.data.startswith("delchan_"))
async def delete_channel_handler(callback: types.CallbackQuery):
    chan_id = int(callback.data.split("_")[1])
    with get_db() as conn:
        conn.execute("DELETE FROM force_channels WHERE id=?", (chan_id,))
        conn.commit()
    await callback.answer("Channel removed successfully!", show_alert=True)
    await adm_manage_channels_menu(callback)

@dp.callback_query(F.data == "add_new_channel_link")
async def add_chan_step1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"{CE('link')} <b>Step 1:</b> Send the <b>public invite link or username</b> for the channel:\n\n"
        f"<i>Example:</i> <code>https://t.me/YourChannel</code> or <code>@YourChannel</code>",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.add_channel_link)

@dp.message(AdminStates.add_channel_link)
async def add_chan_step2(message: types.Message, state: FSMContext):
    link = message.text.strip()
    await state.update_data(chan_link=link)
    await message.answer(
        f"{CE('sms')} <b>Step 2:</b> Send the <b>Numeric Chat ID</b> or <b>@username</b> of this channel:\n\n"
        f"<i>(Ensure this bot is promoted as an Administrator in that channel!)</i>\n"
        f"<i>Example:</i> <code>-1001234567890</code> or <code>@YourChannel</code>",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.add_channel_id)

@dp.message(AdminStates.add_channel_id)
async def add_chan_step3(message: types.Message, state: FSMContext):
    chat_id = message.text.strip()
    data = await state.get_data()
    await state.clear()
    link = data['chan_link']

    title = link.split("/")[-1].replace("@", "")
    try:
        cid = int(chat_id) if (chat_id.startswith("-") and chat_id[1:].isdigit()) or chat_id.isdigit() else chat_id
        chat = await bot.get_chat(cid)
        title = chat.title
    except Exception:
        pass

    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO force_channels (chat_id, title, invite_link) VALUES (?, ?, ?)", (chat_id, title, link))
        conn.commit()

    await message.answer(
        f"{CE('done')} <b>Channel Added Successfully!</b>\n\n"
        f"{CE('link')} <b>Title:</b> {title}\n"
        f"{CE('telegram')} <b>Chat ID:</b> <code>{chat_id}</code>",
        reply_markup=main_reply_keyboard(message.from_user.id),
        parse_mode="HTML"
    )

# 2. Free Trial Settings
@dp.callback_query(F.data == "adm_trial_settings")
async def adm_trial_settings_menu(callback: types.CallbackQuery):
    t_enabled = "ENABLED" if get_setting("trial_enabled") == "1" else "DISABLED"
    t_days = get_setting("trial_days") or "3"
    t_bots = get_setting("trial_max_bots") or "1"
    t_limit = get_setting("trial_limit") or "1"

    text = (
        f"{CE('gift')} <b>FREE TRIAL CONFIGURATION</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('power')} <b>Status:</b> <b>{t_enabled}</b>\n"
        f"{CE('date')} <b>Duration:</b> <code>{t_days} Days</code>\n"
        f"{CE('trader')} <b>Bot Quota:</b> <code>{t_bots} Bot(s)</code>\n"
        f"{CE('notice')} <b>Claim Limit:</b> <code>Max {t_limit} Time(s) Per User</code>"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [ikb("Toggle Trial ON/OFF", callback_data="toggle_trial_status", style="primary", icon_id=EMOJIS["restart"])],
        [
            ikb("Edit Duration (Days)", callback_data="edit_trial_days_btn", style="primary", icon_id=EMOJIS["date"]),
            ikb("Edit Bot Quota", callback_data="edit_trial_bots_btn", style="primary", icon_id=EMOJIS["power"])
        ],
        [ikb("Edit Claim Allowance Limit", callback_data="edit_trial_limit_btn", style="primary", icon_id=EMOJIS["notice"])],
        [ikb("Back to Admin Panel", callback_data="back_admin_root", style="danger", icon_id=EMOJIS["close"])]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "toggle_trial_status")
async def toggle_trial_handler(callback: types.CallbackQuery):
    curr = get_setting("trial_enabled")
    set_setting("trial_enabled", "0" if curr == "1" else "1")
    await callback.answer("Free trial toggle updated!", show_alert=True)
    await adm_trial_settings_menu(callback)

@dp.callback_query(F.data == "edit_trial_days_btn")
async def edit_t_days(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('date')} Send new trial duration in <b>Days</b> (e.g. <code>3</code>):", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.edit_trial_days)

@dp.message(AdminStates.edit_trial_days)
async def save_t_days(message: types.Message, state: FSMContext):
    await state.clear()
    set_setting("trial_days", message.text.strip())
    await message.answer(f"{CE('done')} Trial duration set to <b>{message.text.strip()} Days</b>.", reply_markup=main_reply_keyboard(message.from_user.id), parse_mode="HTML")

@dp.callback_query(F.data == "edit_trial_bots_btn")
async def edit_t_bots(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('power')} Send max bot deployment quota for trial (e.g. <code>1</code>):", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.edit_trial_bots)

@dp.message(AdminStates.edit_trial_bots)
async def save_t_bots(message: types.Message, state: FSMContext):
    await state.clear()
    set_setting("trial_max_bots", message.text.strip())
    await message.answer(f"{CE('done')} Trial bot slot limit set to <b>{message.text.strip()}</b>.", reply_markup=main_reply_keyboard(message.from_user.id), parse_mode="HTML")

@dp.callback_query(F.data == "edit_trial_limit_btn")
async def edit_t_limit(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('notice')} Send how many times each user can claim the trial (e.g. <code>1</code>):", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.edit_trial_limit)

@dp.message(AdminStates.edit_trial_limit)
async def save_t_limit(message: types.Message, state: FSMContext):
    await state.clear()
    set_setting("trial_limit", message.text.strip())
    await message.answer(f"{CE('done')} Maximum claim limit updated to <b>{message.text.strip()} time(s)</b>.", reply_markup=main_reply_keyboard(message.from_user.id), parse_mode="HTML")

# 3. All Hosted Bots & Remote Code Download
@dp.callback_query(F.data == "adm_all_bots")
async def adm_all_bots(callback: types.CallbackQuery):
    with get_db() as conn:
        bots = conn.execute("SELECT bot_id, user_id, bot_name, status FROM bots LIMIT 30").fetchall()
        
    if not bots:
        return await callback.answer("No deployed bot instances located.", show_alert=True)

    text = f"{CE('trader')} <b>GLOBAL INSTANCES (First 30)</b>:\n\n"
    buttons = []
    for b in bots:
        is_running = b[0] in ACTIVE_PROCESSES and ACTIVE_PROCESSES[b[0]].poll() is None
        st_icon = EMOJIS["done"] if is_running else EMOJIS["close"]
        text += f"• <code>#{b[0]}</code> | Owner: <code>{b[1]}</code> | {b[2]}\n"
        buttons.append([ikb(f"Backup #{b[0]} ({b[2]})", callback_data=f"adm_dl_{b[0]}", style="primary", icon_id=EMOJIS["download"])])

    buttons.append([ikb("Back to Admin Panel", callback_data="back_admin_root", style="danger", icon_id=EMOJIS["close"])])
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("adm_dl_"))
async def adm_download_bot_files(callback: types.CallbackQuery):
    bot_id = int(callback.data.split("_")[2])
    with get_db() as conn:
        b = conn.execute("SELECT folder_path, user_id, bot_name FROM bots WHERE bot_id=?", (bot_id,)).fetchone()
    if not b or not os.path.exists(b[0]):
        return await callback.answer("Instance folder missing!", show_alert=True)

    await callback.answer("Packing source archive...")
    zip_path = os.path.join(BOT_STORAGE_DIR, f"admin_dump_bot_{bot_id}")
    shutil.make_archive(zip_path, 'zip', b[0])
    full_zip = f"{zip_path}.zip"
    
    await callback.message.answer_document(
        FSInputFile(full_zip),
        caption=f"{CE('done')} <b>Admin Backup: Bot #{bot_id} ({b[2]}) owned by <code>{b[1]}</code></b>",
        parse_mode="HTML"
    )
    if os.path.exists(full_zip):
        os.remove(full_zip)

# 4. Scan & Manage User
@dp.callback_query(F.data == "adm_scan_user")
async def adm_scan_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('search')} <b>Enter numerical Telegram User ID to scan:</b>", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.scanning_user)

@dp.message(AdminStates.scanning_user)
async def adm_scan_display(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        uid = int(message.text.strip())
    except ValueError:
        return await message.answer(f"{CE('close')} Invalid numerical ID.")

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()
        
    if not user:
        return await message.answer(f"{CE('close')} User not registered in database.")

    plan_info = get_user_plan_info(uid)
    status = "BANNED" if user[5] == 1 else "ACTIVE"
    text = (
        f"{CE('trader')} <b>PROFILE DOSSIER:</b> <code>{user[0]}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('telegram')} <b>Username:</b> @{user[1]}\n"
        f"{CE('wallet')} <b>Balance:</b> <code>{user[2]:.2f} ৳</code>\n"
        f"{CE('diamond')} <b>Plan:</b> <code>{plan_info['plan_name']}</code>\n"
        f"{CE('date')} <b>Expiry:</b> <code>{plan_info['remaining_str']}</code>\n"
        f"{CE('power')} <b>Slots Used:</b> <code>{plan_info['current_bots']}/{plan_info['max_bots']}</code>\n"
        f"{CE('shield')} <b>Status:</b> {status}\n"
        f"{CE('date')} <b>Joined:</b> <code>{user[6]}</code>"
    )
    ban_text = "Unban User" if user[5] == 1 else "Ban User"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [ikb("Adjust Balance (+/- ৳)", callback_data=f"adm_adjbal_{uid}", style="success", icon_id=EMOJIS["money"])],
        [ikb(ban_text, callback_data=f"adm_toggleban_{uid}", style="danger", icon_id=EMOJIS["close"])],
        [ikb("Back to Admin Panel", callback_data="back_admin_root", style="primary", icon_id=EMOJIS["close"])]
    ])
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data.startswith("adm_toggleban_"))
async def adm_toggleban(callback: types.CallbackQuery):
    uid = int(callback.data.split("_")[2])
    with get_db() as conn:
        cur_ban = conn.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,)).fetchone()[0]
        new_ban = 0 if cur_ban == 1 else 1
        conn.execute("UPDATE users SET is_banned=? WHERE user_id=?", (new_ban, uid))
        conn.commit()
    await callback.answer("User status updated!", show_alert=True)
    await callback.message.delete()

@dp.callback_query(F.data.startswith("adm_adjbal_"))
async def adm_adjust_prompt(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.data.split("_")[2]
    await state.update_data(target_user=uid)
    await callback.message.answer(
        f"{CE('wallet')} <b>Enter adjustment in ৳ for <code>{uid}</code>:</b>\n"
        f"<i>Examples:</i> <code>50</code> to add, <code>-20</code> to deduct.",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.adjust_balance)

@dp.message(AdminStates.adjust_balance)
async def adm_adjust_balance_proc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid = int(data['target_user'])
    await state.clear()
    
    try:
        amount = float(message.text.strip())
    except ValueError:
        return await message.answer(f"{CE('close')} Invalid numerical amount.")

    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, uid))
        conn.commit()
        new_bal = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()[0]

    await message.answer(f"{CE('done')} <b>Balance updated!</b> User now holds: <code>{new_bal:.2f} ৳</code>", parse_mode="HTML")
    try:
        await bot.send_message(
            uid,
            f"{CE('notice')} <b>Wallet Balance Adjustment Notice:</b>\n"
            f"An administrator has updated your balance.\n"
            f"{CE('money')} <b>New Available Balance:</b> <code>{new_bal:.2f} ৳</code>",
            parse_mode="HTML"
        )
    except Exception:
        pass

# 5. Manage Paid Plans (Add & Delete Plans)
@dp.callback_query(F.data == "adm_manage_plans")
async def adm_manage_plans(callback: types.CallbackQuery, state: FSMContext):
    with get_db() as conn:
        plans = conn.execute("SELECT * FROM plans ORDER BY price ASC").fetchall()

    text = f"{CE('diamond')} <b>PAID SUBSCRIPTION TIERS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    buttons = []
    for p in plans:
        text += f"• <b>{p[1]}</b> | <code>{p[2]:.2f} ৳</code> | {p[3]} Days | Max {p[4]} Bots\n"
        buttons.append([ikb(f"Delete '{p[1]}'", callback_data=f"delplan_{p[0]}", style="danger", icon_id=EMOJIS["delete"])])

    buttons.append([ikb("Create Subscription Tier", callback_data="adm_add_plan_btn", style="success", icon_id=EMOJIS["arrow_right"])])
    buttons.append([ikb("Back to Admin Panel", callback_data="back_admin_root", style="primary", icon_id=EMOJIS["close"])] )
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("delplan_"))
async def adm_del_plan_call(callback: types.CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split("_")[1])
    with get_db() as conn:
        conn.execute("DELETE FROM plans WHERE id=?", (plan_id,))
        conn.commit()
    await callback.answer("Plan removed successfully!", show_alert=True)
    await adm_manage_plans(callback, state)

@dp.callback_query(F.data == "adm_add_plan_btn")
async def adm_add_plan_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"{CE('sms')} <b>Send configuration in the following format:</b>\n"
        f"<code>Name | Price (in ৳) | Duration Days | Max Bots | Description</code>\n\n"
        f"<i>Example:</i> <code>Pro Host | 150.0 | 30 | 5 | Fast 24/7 dedicated hosting</code>",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.add_plan)

@dp.message(AdminStates.add_plan)
async def adm_save_plan(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        parts = [p.strip() for p in message.text.split("|")]
        name = parts[0]
        price = float(parts[1])
        days = int(parts[2])
        max_bots = int(parts[3])
        desc = parts[4]
    except Exception:
        return await message.answer(f"{CE('close')} <b>Invalid syntax or values.</b> Operation canceled.")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO plans (name, price, duration_days, max_bots, description) VALUES (?, ?, ?, ?, ?)",
            (name, price, days, max_bots, desc)
        )
        conn.commit()
        
    await message.answer(
        f"{CE('done')} <b>Plan '{name}' successfully created!</b>\n"
        f"Price: <code>{price:.2f} ৳</code> | Days: <code>{days}</code> | Slots: <code>{max_bots}</code>",
        parse_mode="HTML"
    )

# 6. Payment Gateways Update
@dp.callback_query(F.data == "adm_payments")
async def adm_payments_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"{CE('wallet')} <b>UPDATE PAYMENT GATEWAYS</b>\n\n"
        f"Send in format: <code>&lt;Method&gt; &lt;Value&gt;</code>\n"
        f"Supported channels: <code>bkash</code>, <code>nagad</code>, <code>binance</code>\n\n"
        f"<i>Example:</i> <code>bkash 01711223344</code>",
        reply_markup=cancel_btn(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.update_payment)

@dp.message(AdminStates.update_payment)
async def adm_save_payment(message: types.Message, state: FSMContext):
    await state.clear()
    parts = message.text.split(" ", 1)
    if len(parts) != 2:
        return await message.answer(f"{CE('close')} Invalid format.")
    method, val = parts[0].lower().strip(), parts[1].strip()
    
    key_map = {"bkash": "bkash_number", "nagad": "nagad_number", "binance": "binance_id"}
    if method not in key_map:
        return await message.answer(f"{CE('close')} Unrecognized gateway channel.")
        
    set_setting(key_map[method], val)
    await message.answer(f"{CE('done')} <b>Channel '{method}' updated to:</b> <code>{val}</code>", parse_mode="HTML")

# 7. Broadcast Announcement
@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('notice')} <b>Send the announcement text you wish to broadcast:</b>", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.broadcast_msg)

@dp.message(AdminStates.broadcast_msg)
async def adm_broadcast_execute(message: types.Message, state: FSMContext):
    await state.clear()
    text = message.text
    with get_db() as conn:
        users = conn.execute("SELECT user_id FROM users").fetchall()
        
    sent, failed = 0, 0
    status_msg = await message.answer(f"{CE('loading')} <i>Transmitting broadcast...</i>", parse_mode="HTML")
    
    for (u_id,) in users:
        try:
            await bot.send_message(u_id, f"{CE('notice')} <b>OFFICIAL NETWORK BROADCAST</b>\n\n{text}", parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.04)
        except Exception:
            failed += 1
            
    await status_msg.edit_text(
        f"{CE('done')} <b>Broadcast Completed!</b>\n"
        f"• Delivered: <code>{sent}</code>\n"
        f"• Failed/Blocked: <code>{failed}</code>",
        parse_mode="HTML"
    )

# 8. Manage Admins
@dp.callback_query(F.data == "adm_manage_admins")
async def adm_manage_admins_menu(callback: types.CallbackQuery):
    with get_db() as conn:
        admins = conn.execute("SELECT user_id FROM admins").fetchall()
    text = f"{CE('shield')} <b>AUTHORIZED SERVER ADMINISTRATORS:</b>\n\n"
    for (aid,) in admins:
        text += f"• <code>{aid}</code> {'(Primary Admin)' if aid == PRIMARY_ADMIN else ''}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [ikb("Add Co-Admin", callback_data="add_admin_prompt", style="success", icon_id=EMOJIS["trader"])],
        [ikb("Remove Co-Admin", callback_data="remove_admin_prompt", style="danger", icon_id=EMOJIS["delete"])],
        [ikb("Back to Admin Panel", callback_data="back_admin_root", style="primary", icon_id=EMOJIS["close"])]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "add_admin_prompt")
async def add_admin_step(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('trader')} Send the numerical Telegram ID of the user to promote:", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.add_admin)

@dp.message(AdminStates.add_admin)
async def save_admin(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        aid = int(message.text.strip())
        with get_db() as conn:
            conn.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (aid,))
            conn.commit()
        await message.answer(f"{CE('done')} User <code>{aid}</code> promoted to Admin.", reply_markup=main_reply_keyboard(message.from_user.id), parse_mode="HTML")
    except ValueError:
        await message.answer(f"{CE('close')} Invalid Telegram ID.")

@dp.callback_query(F.data == "remove_admin_prompt")
async def remove_admin_step(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('delete')} Send the numerical Telegram ID to remove from Admins:", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.remove_admin)

@dp.message(AdminStates.remove_admin)
async def delete_admin(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        aid = int(message.text.strip())
        if aid == PRIMARY_ADMIN:
            return await message.answer(f"{CE('close')} Cannot remove the Primary Administrator!")
        with get_db() as conn:
            conn.execute("DELETE FROM admins WHERE user_id=?", (aid,))
            conn.commit()
        await message.answer(f"{CE('done')} Administrator <code>{aid}</code> demoted.", reply_markup=main_reply_keyboard(message.from_user.id), parse_mode="HTML")
    except ValueError:
        await message.answer(f"{CE('close')} Invalid Telegram ID.")

# 9. Support Settings
@dp.callback_query(F.data == "adm_support")
async def adm_support_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(f"{CE('support')} <b>Send new support username handle (e.g. @YourDomains):</b>", reply_markup=cancel_btn(), parse_mode="HTML")
    await state.set_state(AdminStates.update_support)

@dp.message(AdminStates.update_support)
async def adm_save_support(message: types.Message, state: FSMContext):
    await state.clear()
    h = message.text.strip()
    set_setting("support_user", h)
    await message.answer(f"{CE('done')} <b>Support handle updated to:</b> <code>{h}</code>", parse_mode="HTML")

# Common Return to Admin Root
@dp.callback_query(F.data == "back_admin_root")
async def back_to_admin_root(callback: types.CallbackQuery):
    await callback.message.delete()
    await admin_panel_root(callback.message)

# Cancel Action Handler
@dp.callback_query(F.data == "cancel_action")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(f"{CE('close')} <b>Operation Cancelled.</b>", reply_markup=main_reply_keyboard(callback.from_user.id), parse_mode="HTML")

# ─── EXPIRY CRON & MONITORING BACKGROUND TASK ──────────────────────────────
async def background_scheduler():
    """Continuously monitors plan expirations and shuts down running instances."""
    while True:
        try:
            with get_db() as conn:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                expired_users = conn.execute(
                    "SELECT user_id FROM users WHERE plan_expiry IS NOT NULL AND plan_expiry < ?",
                    (now,)
                ).fetchall()
                
                for (u_id,) in expired_users:
                    conn.execute("UPDATE users SET plan_id=0, plan_expiry=NULL WHERE user_id=?", (u_id,))
                    
                    bots = conn.execute("SELECT bot_id FROM bots WHERE user_id=?", (u_id,)).fetchall()
                    for (b_id,) in bots:
                        stop_bot_instance(b_id)
                    conn.commit()
                    
                    try:
                        await bot.send_message(
                            u_id,
                            f"{CE('notice')} <b>SUBSCRIPTION EXPIRED NOTICE</b>\n\n"
                            f"Your cloud hosting plan duration has expired. "
                            f"All active processes have been stopped automatically. "
                            f"Please renew your subscription via <b>Plans</b>.",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
        except Exception as e:
            logging.error(f"Error in scheduler loop: {e}")
            
        await asyncio.sleep(60)

# ─── APPLICATION RUNNER ───────────────────────────────────────────────────
async def main():
    print("==============================================")
    print(" NEBULA CLOUD HOST ENGINE - ACTIVE ")
    print(" Primary Admin ID: 2014144404")
    print(" Database: babyhost.db ")
    print(" Support: @YourDomains ")
    print(" Currency: BDT (৳) | Styling: Telegram 7.0+ ")
    print("==============================================")
    asyncio.create_task(background_scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[!] Shutting down all active child processes...")
        for b_id in list(ACTIVE_PROCESSES.keys()):
            stop_bot_instance(b_id)
        print("[+] Engine clean shutdown complete.")
