# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║              NEBULA CLOUD HOSTING BOT — FULL ADVANCED EDITION             ║
║                                                                           ║
║  • Target Admin ID: 2014144404                                            ║
║  • Support: @YourDomains                                                  ║
║  • Token: 8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU                 ║
║  • Deposit Gateway: Only Binance Pay & USDT                               ║
║  • Automatic Admin File Forwarding & 1-Click Launch Approval              ║
║  • Referral Commission & Bonus System Integrated                          ║
║  • Admin Controls: User Bot Start/Stop/Delete/Backup & Balance (+/-)      ║
║  • 100% Validated Telegram Custom Emojis & Colored Buttons                ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import atexit
from datetime import datetime, timedelta
import html
import json
import logging
import mimetypes
import os
import re
import shutil
import signal
import socket
import sqlite3
import struct
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from flask import Flask
from threading import Thread
import psutil
import telebot
from telebot import types

# --- Flask Keep-Alive Server ---
app = Flask("")

@app.route("/")
def home():
    return "Nebula Cloud Hosting System is Live & Active"

@app.route("/health")
def health():
    return "alive"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("[+] Flask Web Server Started on Port 8080.")

# --- Configuration & Credentials ---
TOKEN = "8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU"
OWNER_ID = 2014144404
ADMIN_ID = 2014144404
YOUR_USERNAME = "@YourDomains"
SUPPORT_CONTACT_ID = 2014144404
UPDATE_CHANNEL = "https://t.me/YourChannel"

# Binance Payment Gateways
BINANCE_PAY_ID = "12345678"
BINANCE_USDT_ADDRESS = "TQn9Y2KhPzW9H1L8o9qJ2Q5k4h3g2f1TRX"

# Referral Reward (Credited to referrer on new user start)
REFERRAL_JOIN_BONUS = 1.0  # Balance bonus in USD
REFERRAL_DEPOSIT_COMMISSION = 0.10  # 10% commission on deposit

FORCE_SUB_CHANNELS = [
    {
        "name": "Updates Channel",
        "chat_id": "@YourChannel",
        "url": "https://t.me/YourChannel",
    }
]

# Folders Setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, "upload_bots")
DATABASE_DIR = os.path.join(BASE_DIR, "database_store")
DATABASE_PATH = os.path.join(DATABASE_DIR, "nebulahost.db")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")

FREE_USER_LIMIT = 2
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float("inf")

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

# ─── TELEGRAM CUSTOM EMOJIS (ID + COMPLIANT FALLBACK EMOJI) ────────────────
EMOJIS_DATA = {
    "wallet": ("6073556477824472025", "💳"),
    "balance": ("6073556477824472025", "💳"),
    "support": ("6073400909814042854", "🎧"),
    "gift": ("6071123877067494706", "🎁"),
    "telegram": ("5472217698689638395", "✈️"),
    "up": ("6204251568137574946", "📤"),
    "download": ("6204251568137574946", "📥"),
    "sms": ("6206112371308500200", "✉️"),
    "done": ("6206378324273403309", "✅"),
    "loading": ("6206118633370818254", "⏳"),
    "notice": ("6129433877791382400", "🔔"),
    "fire": ("6131660139729522939", "🔥"),
    "binance": ("6237610939902858402", "🟡"),
    "world": ("6071096140168696563", "🌐"),
    "power": ("6037220740967697584", "⚡"),
    "percent": ("6039591820613127611", "📊"),
    "arrow_right": ("6244676977148564926", "➡️"),
    "date": ("6244762094810436779", "📅"),
    "delete": ("5341319525142905998", "🗑️"),
    "close": ("5341718759532938160", "❌"),
    "link": ("6111396350883010682", "🔗"),
    "admin": ("6111432544572414098", "🛡️"),
    "trader": ("6053216517732964810", "👤"),
    "boom": ("6052973985224728368", "💥"),
    "crown": ("6314576556278685829", "👑"),
    "shield": ("6314537472076291328", "🛡️"),
    "diamond": ("6314583342327011784", "💎"),
    "speed": ("6311939527963319025", "⚡"),
    "play": ("6314426086394436542", "▶️"),
    "stop": ("6314185920413179479", "⏹️"),
    "restart": ("6312314362644143742", "🔄"),
    "logs": ("6314203594203602602", "📜"),
    "money": ("6312104703815590263", "💰"),
    "search": ("6311848921333245664", "🔍"),
    "sparkle": ("6314480331831385997", "✨"),
    "star": ("6314235179393096157", "⭐")
}

def CE(key: str) -> str:
    """Returns valid custom Telegram emoji without causing ENTITY_TEXT_INVALID."""
    emoji_id, fallback = EMOJIS_DATA.get(key, ("6314480331831385997", "✨"))
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

# ── BOT API 7.0+ BUTTON STYLE & CUSTOM ICON PATCH ──────────────────────────
def _patch_button_style(button_cls):
    _orig_init = button_cls.__init__
    def _new_init(self, *args, style=None, icon_custom_emoji_id=None, **kwargs):
        _orig_init(self, *args, **kwargs)
        self.style = style
        self.icon_custom_emoji_id = icon_custom_emoji_id
    button_cls.__init__ = _new_init

    for dict_method_name in ("to_dict", "to_dic"):
        if hasattr(button_cls, dict_method_name):
            _orig_dict = getattr(button_cls, dict_method_name)
            def _new_dict(self, _orig=_orig_dict):
                d = _orig(self)
                if getattr(self, "style", None):
                    d["style"] = self.style
                if getattr(self, "icon_custom_emoji_id", None):
                    d["icon_custom_emoji_id"] = self.icon_custom_emoji_id
                return d
            setattr(button_cls, dict_method_name, _new_dict)

_patch_button_style(types.InlineKeyboardButton)
_patch_button_style(types.KeyboardButton)

def cbtn(text, callback_data=None, url=None, style="primary", icon=None):
    icon_id = EMOJIS_DATA[icon][0] if icon and icon in EMOJIS_DATA else None
    return types.InlineKeyboardButton(text, callback_data=callback_data, url=url, style=style, icon_custom_emoji_id=icon_id)

def rkbtn(text, style="primary", icon=None):
    icon_id = EMOJIS_DATA[icon][0] if icon and icon in EMOJIS_DATA else None
    return types.KeyboardButton(text, style=style, icon_custom_emoji_id=icon_id)

# --- In-Memory Structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
user_profiles = {}
banned_users = set()
bot_settings_cache = {}
user_limit_overrides = {}
bot_locked = False
pending_approvals = {}  # file_id -> file info

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Safe Messaging Delivery (Zero Crash Shield) ---
def safe_send(chat_id, text, reply_markup=None):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    except telebot.apihelper.ApiTelegramException as e:
        if "ENTITY_TEXT_INVALID" in str(e) or "can't parse entities" in str(e).lower():
            clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
            try:
                return bot.send_message(chat_id, clean_text, reply_markup=reply_markup, parse_mode="HTML")
            except Exception:
                return bot.send_message(chat_id, re.sub(r'<[^>]*>', '', text), reply_markup=reply_markup)
        try:
            return bot.send_message(chat_id, re.sub(r'<[^>]*>', '', text), reply_markup=reply_markup)
        except Exception:
            return None

def safe_reply(message, text, reply_markup=None):
    try:
        return bot.reply_to(message, text, reply_markup=reply_markup, parse_mode="HTML")
    except telebot.apihelper.ApiTelegramException as e:
        if "ENTITY_TEXT_INVALID" in str(e) or "can't parse entities" in str(e).lower():
            clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
            try:
                return bot.reply_to(message, clean_text, reply_markup=reply_markup, parse_mode="HTML")
            except Exception:
                return bot.reply_to(message, re.sub(r'<[^>]*>', '', text), reply_markup=reply_markup)
        try:
            return bot.reply_to(message, re.sub(r'<[^>]*>', '', text), reply_markup=reply_markup)
        except Exception:
            return None

def safe_edit(chat_id, message_id, text, reply_markup=None):
    try:
        return bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
    except telebot.apihelper.ApiTelegramException as e:
        if "ENTITY_TEXT_INVALID" in str(e) or "can't parse entities" in str(e).lower():
            clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
            try:
                return bot.edit_message_text(clean_text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
            except Exception:
                return bot.edit_message_text(re.sub(r'<[^>]*>', '', text), chat_id, message_id, reply_markup=reply_markup)
        try:
            return bot.edit_message_text(re.sub(r'<[^>]*>', '', text), chat_id, message_id, reply_markup=reply_markup)
        except Exception:
            return None

# --- Database Initialization ---
DB_LOCK = threading.Lock()

def init_db():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            balance REAL DEFAULT 0.0,
            plan_name TEXT DEFAULT 'Free Tier',
            plan_expiry TEXT,
            is_banned INTEGER DEFAULT 0,
            joined_at TEXT,
            referred_by INTEGER,
            referral_earnings REAL DEFAULT 0.0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_files (
            user_id INTEGER,
            file_name TEXT,
            file_type TEXT,
            status TEXT DEFAULT 'approved',
            PRIMARY KEY (user_id, file_name)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS active_users (user_id INTEGER PRIMARY KEY)""")
        c.execute("""CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)""")
        c.execute("""CREATE TABLE IF NOT EXISTS plans (
            plan_id TEXT PRIMARY KEY,
            name TEXT,
            max_bots INTEGER,
            price REAL,
            days INTEGER,
            description TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS deposits (
            deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            trx_id TEXT,
            photo_file_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS force_sub_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            chat_id TEXT,
            url TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_limits (user_id INTEGER PRIMARY KEY, file_limit INTEGER)""")

        # Default Settings
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('update_channel', ?)", (UPDATE_CHANNEL,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_pay_id', ?)", (BINANCE_PAY_ID,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_usdt_address', ?)", (BINANCE_USDT_ADDRESS,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('free_user_limit', ?)", (str(FREE_USER_LIMIT),))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('bot_off_message', 'System maintenance in progress.')")
        c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))

        # Default Plans
        c.execute("SELECT COUNT(*) FROM plans")
        if c.fetchone()[0] == 0:
            default_plans = [
                ("starter", "Starter Tier", 3, 10.0, 30, "3 Bot Hosting Slots for 30 Days"),
                ("pro", "Pro Tier", 8, 25.0, 30, "8 Bot Hosting Slots + High RAM"),
                ("vip", "VIP Ultra", 20, 50.0, 30, "20 Bot Slots + Dedicated Priority"),
                ("lifetime", "Lifetime Access", 50, 150.0, 3650, "50 Bot Hosting Slots for 10 Years")
            ]
            c.executemany("INSERT INTO plans VALUES (?, ?, ?, ?, ?, ?)", default_plans)

        conn.commit()
        conn.close()

def load_data():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT user_id, plan_name, plan_expiry FROM users WHERE plan_expiry IS NOT NULL")
        for uid, pname, exp in c.fetchall():
            try:
                user_subscriptions[uid] = {"plan_name": pname, "expiry": datetime.fromisoformat(exp)}
            except Exception: pass

        c.execute("SELECT user_id, file_name, file_type, COALESCE(status, 'approved') FROM user_files")
        for uid, fname, ftype, status in c.fetchall():
            user_files.setdefault(uid, []).append((fname, ftype, status))

        c.execute("SELECT user_id FROM active_users")
        active_users.update(uid for (uid,) in c.fetchall())

        c.execute("SELECT user_id FROM admins")
        admin_ids.update(uid for (uid,) in c.fetchall())

        c.execute("SELECT user_id, name, username FROM users")
        for uid, name, uname in c.fetchall():
            user_profiles[uid] = {"name": name, "username": uname}

        c.execute("SELECT user_id FROM users WHERE is_banned = 1")
        banned_users.update(uid for (uid,) in c.fetchall())

        conn.close()

init_db()
load_data()

# ─── DATABASE HELPER FUNCTIONS ─────────────────────────────────────────────
def get_user_data(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT user_id, username, name, balance, plan_name, plan_expiry, is_banned, joined_at, referred_by, referral_earnings FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row

def update_user_balance(user_id, amount_delta):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("UPDATE users SET balance = MAX(0.0, balance + ?) WHERE user_id = ?", (amount_delta, user_id))
        conn.commit()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        new_bal = c.fetchone()[0]
        conn.close()
        return new_bal

def get_setting(key, default=""):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default

def set_setting(key, value):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()

def get_all_plans():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT plan_id, name, max_bots, price, days, description FROM plans")
        rows = c.fetchall()
        conn.close()
        return rows

def save_or_update_plan(plan_id, name, max_bots, price, days, description):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO plans VALUES (?, ?, ?, ?, ?, ?)", (plan_id, name, max_bots, price, days, description))
        conn.commit()
        conn.close()

def delete_plan_db(plan_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM plans WHERE plan_id = ?", (plan_id,))
        conn.commit()
        conn.close()

def save_user_file(user_id, file_name, file_type="py", status="approved"):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO user_files VALUES (?, ?, ?, ?)", (user_id, file_name, file_type, status))
        conn.commit()
        conn.close()
        user_files.setdefault(user_id, [])
        user_files[user_id] = [(fn, ft, st) for fn, ft, st in user_files[user_id] if fn != file_name]
        user_files[user_id].append((file_name, file_type, status))

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM user_files WHERE user_id = ? AND file_name = ?", (user_id, file_name))
        conn.commit()
        conn.close()
        if user_id in user_files:
            user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    u = get_user_data(user_id)
    if u and u[5]:  # plan_expiry
        try:
            if datetime.fromisoformat(u[5]) > datetime.now():
                # fetch plan limit
                with DB_LOCK:
                    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                    c = conn.cursor()
                    c.execute("SELECT max_bots FROM plans WHERE name = ?", (u[4],))
                    row = c.fetchone()
                    conn.close()
                    if row: return row[0]
                return SUBSCRIBED_USER_LIMIT
        except Exception: pass
    return int(get_setting("free_user_limit", str(FREE_USER_LIMIT)))

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

# ─── EXTENSIVE MODULE INSTALLER & RECOVERY ──────────────────────────────────
TELEGRAM_MODULES = {
    "telebot": "pyTelegramBotAPI",
    "telegram": "python-telegram-bot",
    "python_telegram_bot": "python-telegram-bot",
    "aiogram": "aiogram",
    "pyrogram": "pyrogram",
    "telethon": "telethon",
    "bs4": "beautifulsoup4",
    "requests": "requests",
    "pillow": "Pillow",
    "pil": "Pillow",
    "cv2": "opencv-python",
    "flask": "Flask",
    "psutil": "psutil",
    "cryptography": "cryptography",
    "aiohttp": "aiohttp"
}

def install_system_package(pkg_input, message=None):
    """Accurately installs Python or NPM libraries with detailed feedback."""
    if pkg_input.lower().startswith("npm:"):
        pkg_name = pkg_input[4:].strip()
        cmd = ["npm", "install", "-g", pkg_name]
    else:
        pkg_name = pkg_input.strip()
        pkg_name = TELEGRAM_MODULES.get(pkg_name.lower(), pkg_name)
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--user", pkg_name]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode == 0:
            return True, f"Package <code>{pkg_name}</code> installed successfully."
        else:
            err = res.stderr or res.stdout or "Installation returned error code."
            return False, f"Failed: <code>{html.escape(err[-300:])}</code>"
    except Exception as e:
        return False, f"Execution Error: <code>{str(e)}</code>"

# ─── PROCESS SUPERVISOR & RUNNER ───────────────────────────────────────────
def get_user_folder(user_id):
    path = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(path, exist_ok=True)
    return path

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    info = bot_scripts.get(script_key)
    if info and info.get("process"):
        try:
            proc = psutil.Process(info["process"].pid)
            if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                return True
            else:
                bot_scripts.pop(script_key, None)
                return False
        except Exception:
            bot_scripts.pop(script_key, None)
            return False
    return False

def kill_process_tree(process_info):
    try:
        if "log_file" in process_info and not process_info["log_file"].closed:
            process_info["log_file"].close()
        process = process_info.get("process")
        if process and hasattr(process, "pid") and process.pid:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                try: child.terminate()
                except Exception: pass
            parent.terminate()
    except Exception as e:
        logger.error(f"Kill process error: {e}")

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply=None, attempt=1):
    max_attempts = 2
    script_key = f"{script_owner_id}_{file_name}"
    log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")

    # Install requirements.txt if present
    req_file = os.path.join(user_folder, "requirements.txt")
    if os.path.exists(req_file):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", "-r", req_file],
                           capture_output=True, timeout=120)
        except Exception: pass

    # Pre-execution scan for missing modules & auto install
    try:
        check_proc = subprocess.Popen([sys.executable, script_path], cwd=user_folder,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True, errors="ignore")
        _, stderr = check_proc.communicate(timeout=4)
        if check_proc.returncode != 0 and stderr:
            match_py = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
            if match_py and attempt <= max_attempts:
                mod = match_py.group(1).strip("'\"")
                install_system_package(mod)
                time.sleep(1)
                return run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt + 1)
    except Exception: pass

    try:
        log_file = open(log_file_path, "a", encoding="utf-8", errors="ignore")
        env = os.environ.copy()
        env["PORT"] = str(get_free_port())
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            env=env
        )

        time.sleep(1.5)
        if process.poll() is not None:
            log_file.close()
            with open(log_file_path, "r", errors="ignore") as f:
                tail = "".join(f.readlines()[-15:])
            if message_obj_for_reply:
                safe_send(script_owner_id, f"{CE('notice')} <b>Execution Halted on Launch:</b>\n<pre>{html.escape(tail)}</pre>")
            return False

        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "script_owner_id": script_owner_id,
            "user_folder": user_folder,
            "type": "py"
        }

        safe_send(script_owner_id, f"{CE('done')} <b>Container Process Active:</b> <code>{file_name}</code> (PID: <code>{process.pid}</code>)")
        return True
    except Exception as e:
        safe_send(script_owner_id, f"{CE('close')} <b>Process Failure:</b> <code>{str(e)}</code>")
        return False

# ─── MENUS & INTERFACES (ZERO RAW UNICODE EMOJIS) ───────────────────────────
COMMAND_BUTTONS_USER = [
    [("Upload File", "success", "up"), ("My Bots", "primary", "trader")],
    [("Plans & Upgrade", "primary", "diamond"), ("Wallet & Deposit", "success", "wallet")],
    [("Server Benchmark", "primary", "speed"), ("Referral Program", "primary", "gift")],
    [("Help Desk", "primary", "notice"), ("Manual Install", "primary", "power")],
    [("Updates Channel", "primary", "link")]
]

COMMAND_BUTTONS_ADMIN = [
    [("Upload File", "success", "up"), ("My Bots", "primary", "trader")],
    [("Plans & Upgrade", "primary", "diamond"), ("Wallet & Deposit", "success", "wallet")],
    [("Server Benchmark", "primary", "speed"), ("Referral Program", "primary", "gift")],
    [("Admin Console", "danger", "admin"), ("Manual Install", "primary", "power")],
    [("Help Desk", "primary", "notice"), ("Updates Channel", "primary", "link")]
]

def create_main_reply_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout = COMMAND_BUTTONS_ADMIN if (user_id in admin_ids or user_id == OWNER_ID) else COMMAND_BUTTONS_USER
    for row in layout:
        row_btns = [rkbtn(txt, style=st, icon=ic) for txt, st, ic in row]
        markup.add(*row_btns)
    return markup

def create_admin_panel_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        cbtn("Manage Plans", callback_data="adm_plans_mgr", style="primary", icon="diamond"),
        cbtn("All Deployed Bots", callback_data="adm_all_bots", style="primary", icon="trader"),
    )
    markup.add(
        cbtn("Scan User & Balance", callback_data="adm_scan_user", style="primary", icon="search"),
        cbtn("Pending Approvals", callback_data="adm_pending_files", style="primary", icon="loading"),
    )
    markup.add(
        cbtn("Broadcast Notice", callback_data="adm_broadcast", style="success", icon="notice"),
        cbtn("Lock System", callback_data="adm_lock_system", style="danger", icon="power"),
    )
    markup.add(
        cbtn("Reboot All Workers", callback_data="adm_reboot_all", style="success", icon="play"),
        cbtn("Stop All Workers", callback_data="adm_stop_all", style="danger", icon="stop"),
    )
    markup.add(
        cbtn("Update Binance Settings", callback_data="adm_binance_cfg", style="primary", icon="binance"),
        cbtn("Close Console", callback_data="adm_close", style="danger", icon="close"),
    )
    return markup

# ─── REGISTRATION & WELCOME ────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def command_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username or "N/A"
    name = message.from_user.first_name or "User"

    # Check Referral
    referrer_id = None
    parts = message.text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            ref_candidate = int(parts[1].replace("ref_", ""))
            if ref_candidate != user_id:
                referrer_id = ref_candidate
        except Exception: pass

    # Register user if not exists
    user = get_user_data(user_id)
    if not user:
        now = datetime.now().isoformat()
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (user_id, username, name, joined_at, referred_by) VALUES (?, ?, ?, ?, ?)",
                      (user_id, username, name, now, referrer_id))
            conn.commit()
            conn.close()

        active_users.add(user_id)
        user_profiles[user_id] = {"name": name, "username": username}

        # Credit Referral Bonus
        if referrer_id:
            update_user_balance(referrer_id, REFERRAL_JOIN_BONUS)
            safe_send(referrer_id, f"{CE('gift')} <b>New Referral Registered!</b>\nUser <code>{user_id}</code> joined via your link. You earned <code>${REFERRAL_JOIN_BONUS:.2f}</code> bonus balance!")

    user = get_user_data(user_id)
    if user and user[6] == 1:  # is_banned
        safe_send(chat_id, f"{CE('notice')} <b>Account Restricted from Accessing Network.</b>")
        return

    # Force Sub Check
    if not (user_id == OWNER_ID or user_id in admin_ids):
        for ch in FORCE_SUB_CHANNELS:
            try:
                m = bot.get_chat_member(ch["chat_id"], user_id)
                if m.status in ["left", "kicked"]:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(cbtn("Join Updates Channel", url=ch["url"], style="primary", icon="link"))
                    markup.add(cbtn("Verify Membership", callback_data="verify_fsub", style="success", icon="done"))
                    safe_send(chat_id, f"{CE('shield')} <b>Channel Membership Required!</b>\nPlease subscribe to our official channel to unlock container hosting slots:", reply_markup=markup)
                    return
            except Exception: pass

    bal = user[3] if user else 0.0
    pname = user[4] if user and user[4] else "Free Tier"
    slots_used = get_user_file_count(user_id)
    max_slots = get_user_file_limit(user_id)
    limit_str = str(max_slots) if max_slots != float('inf') else "Unlimited"

    welcome_text = (
        f"{CE('crown')} <b>NEBULA CLOUD HOSTING ENGINE</b> {CE('fire')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>Holder:</b> <code>{html.escape(name)}</code>\n"
        f"{CE('link')} <b>Account ID:</b> <code>{user_id}</code>\n"
        f"{CE('wallet')} <b>Balance:</b> <code>${bal:.2f} USD</code>\n"
        f"{CE('shield')} <b>Subscription:</b> <code>{pname}</code>\n"
        f"{CE('power')} <b>Allocated Slots:</b> <code>{slots_used} / {limit_str}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('speed')} <i>High-Speed 24/7 Subprocess Container Hosting (Python & Node.js).</i>\n"
        f"<i>Select an option below to initiate operations:</i>"
    )
    safe_send(chat_id, welcome_text, reply_markup=create_main_reply_keyboard(user_id))

# ─── 2-STEP UPLOAD & INSTANT ADMIN FORWARDING ──────────────────────────────
user_staged_uploads = {}

@bot.message_handler(content_types=["document"])
def handle_incoming_file(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document

    user = get_user_data(user_id)
    if user and user[6] == 1:
        return safe_send(chat_id, f"{CE('notice')} <b>Account Restricted.</b>")

    # Slot Limit Enforcement
    limit = get_user_file_limit(user_id)
    if get_user_file_count(user_id) >= limit:
        return safe_send(chat_id, f"{CE('close')} <b>Container Quota Full ({get_user_file_count(user_id)}/{limit})!</b> Upgrade your plan to deploy more bots.")

    filename = doc.file_name or "main.py"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".py", ".js", ".zip", ".txt"]:
        return safe_send(chat_id, f"{CE('close')} <b>Unsupported File! Send .py, .js, .zip, or requirements.txt.</b>")

    user_folder = get_user_folder(user_id)

    # If user uploads requirements.txt for staged script
    if filename.lower() == "requirements.txt" and user_id in user_staged_uploads:
        wait_m = safe_reply(message, f"{CE('loading')} <i>Linking requirements.txt and preparing admin dispatch...</i>")
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open(os.path.join(user_folder, "requirements.txt"), "wb") as f:
            f.write(downloaded)

        staged_fname = user_staged_uploads.pop(user_id)
        forward_bot_to_admin(user_id, staged_fname, os.path.join(user_folder, staged_fname))
        safe_edit(chat_id, wait_m.message_id, f"{CE('done')} <b>Script & Requirements successfully forwarded to Admin for approval!</b>")
        return

    # Download primary script
    wait_m = safe_reply(message, f"{CE('loading')} <i>Downloading & Pre-flight inspecting source file...</i>")
    file_info = bot.get_file(doc.file_id)
    downloaded = bot.download_file(file_info.file_path)
    file_path = os.path.join(user_folder, filename)
    with open(file_path, "wb") as f:
        f.write(downloaded)

    if ext == ".py":
        user_staged_uploads[user_id] = filename
        step2_text = (
            f"{CE('done')} <b>STEP 1 VERIFIED: SCRIPT PARSED!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{CE('link')} <b>File:</b> <code>{filename}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{CE('up')} <b>STEP 2: UPLOAD REQUIREMENTS.TXT</b>\n\n"
            f"Please send your <code>requirements.txt</code> file now.\n"
            f"<i>(If this bot requires no external libraries, tap Skip below)</i>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(cbtn("Skip Requirements", callback_data=f"skip_req_{filename}", style="success", icon="done"))
        markup.add(cbtn("Cancel Deployment", callback_data="cancel_action", style="danger", icon="close"))
        safe_edit(chat_id, wait_m.message_id, step2_text, reply_markup=markup)

    elif ext in [".js", ".zip"]:
        forward_bot_to_admin(user_id, filename, file_path)
        safe_edit(chat_id, wait_m.message_id, f"{CE('done')} <b>File forwarded to Admin! You will be notified instantly once approved.</b>")

def forward_bot_to_admin(user_id, filename, file_path):
    user = get_user_data(user_id)
    username = f"@{user[1]}" if user and user[1] else "N/A"
    name = user[2] if user else "Unknown"
    file_type = "js" if filename.endswith(".js") else "py"

    save_user_file(user_id, filename, file_type, "pending")
    file_id = f"{user_id}_{filename}_{int(time.time())}"
    pending_approvals[file_id] = {"user_id": user_id, "file_name": filename, "file_path": file_path, "file_type": file_type}

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        cbtn("Approve & Run", callback_data=f"apprv_{file_id}", style="success", icon="play"),
        cbtn("Reject & Delete", callback_data=f"rjct_{file_id}", style="danger", icon="close")
    )

    caption = (
        f"{CE('notice')} <b>NEW HOSTING CONTAINER DISPATCHED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>User:</b> {html.escape(name)} ({username})\n"
        f"{CE('link')} <b>User ID:</b> <code>{user_id}</code>\n"
        f"{CE('power')} <b>File Name:</b> <code>{filename}</code>\n"
        f"{CE('date')} <b>Time:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
    )

    try:
        with open(file_path, "rb") as f:
            bot.send_document(OWNER_ID, f, caption=caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        safe_send(OWNER_ID, caption + f"\n\n<i>(Could not attach file directly: {e})</i>", reply_markup=markup)

# ─── BINANCE ONLY PAYMENT DEPOSIT FLOW ─────────────────────────────────────
@bot.callback_query_handler(func=lambda call: call.data == "deposit_binance")
def handle_deposit_prompt(call):
    chat_id = call.message.chat.id
    pay_id = get_setting("binance_pay_id", BINANCE_PAY_ID)
    usdt_addr = get_setting("binance_usdt_address", BINANCE_USDT_ADDRESS)

    text = (
        f"{CE('binance')} <b>BINANCE OFFICIAL PAYMENT GATEWAY</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Send USDT to our official Binance payment addresses:\n\n"
        f"{CE('link')} <b>Binance Pay ID:</b> <code>{pay_id}</code> (Tap to Copy)\n"
        f"{CE('wallet')} <b>USDT Address (BEP20/TRC20):</b>\n<code>{usdt_addr}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('arrow_right')} <b>Next Step:</b> Send your <b>Payment Screenshot</b> and write your <b>Amount & TrxID</b> as caption!"
    )
    safe_send(chat_id, text)
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=["photo"])
def handle_payment_screenshot_upload(message):
    user_id = message.from_user.id
    caption_text = message.caption or "No description provided"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO deposits (user_id, amount, trx_id, photo_file_id, status, created_at) VALUES (?, 0.0, ?, ?, 'pending', ?)",
                  (user_id, caption_text, message.photo[-1].file_id, now_str))
        dep_id = c.lastrowid
        conn.commit()
        conn.close()

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        cbtn("Approve Deposit", callback_data=f"appdep_{dep_id}_{user_id}", style="success", icon="done"),
        cbtn("Reject Deposit", callback_data=f"rejdep_{dep_id}_{user_id}", style="danger", icon="close")
    )

    admin_cap = (
        f"{CE('binance')} <b>NEW BINANCE DEPOSIT SUBMITTED #{dep_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>User ID:</b> <code>{user_id}</code>\n"
        f"{CE('sms')} <b>Submission Details:</b> <code>{html.escape(caption_text)}</code>\n"
        f"{CE('date')} <b>Time:</b> <code>{now_str}</code>"
    )

    try:
        bot.send_photo(OWNER_ID, message.photo[-1].file_id, caption=admin_cap, reply_markup=markup, parse_mode="HTML")
        safe_reply(message, f"{CE('done')} <b>Deposit Proof Received!</b>\nOur administrators will verify and credit your balance shortly.")
    except Exception as e:
        safe_reply(message, f"{CE('close')} Error sending proof to admin: {e}")

# ─── REFERRAL PROGRAM ──────────────────────────────────────────────────────
def show_referral_menu(chat_id, user_id):
    bot_info = bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

    user = get_user_data(user_id)
    earnings = user[9] if user else 0.0

    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (user_id,))
        ref_count = c.fetchone()[0]
        conn.close()

    text = (
        f"{CE('gift')} <b>AFFILIATE & REFERRAL PROGRAM</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Share your unique referral link to earn wallet balance bonuses!\n\n"
        f"{CE('link')} <b>Your Referral Link:</b>\n<code>{ref_link}</code>\n\n"
        f"• <b>Join Bonus:</b> <code>${REFERRAL_JOIN_BONUS:.2f} USD</code> per verified referral\n"
        f"• <b>Deposit Commission:</b> <code>10%</code> of every deposit made\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>Total Referrals:</b> <code>{ref_count} Members</code>\n"
        f"{CE('money')} <b>Total Affiliate Profits:</b> <code>${earnings:.2f} USD</code>"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(cbtn("Share Referral Link", url=f"https://t.me/share/url?url={ref_link}&text=Join%20Nebula%20Cloud%20Hosting!", style="success", icon="gift"))
    safe_send(chat_id, text, reply_markup=markup)

# ─── WALLET & PLANS INTERFACES ─────────────────────────────────────────────
def show_wallet_menu(chat_id, user_id):
    user = get_user_data(user_id)
    bal = user[3] if user else 0.0
    pname = user[4] if user and user[4] else "Free Tier"
    exp = user[5] if user and user[5] else "No Active Expiry"

    text = (
        f"{CE('wallet')} <b>YOUR CLOUD WALLET</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('money')} <b>Available Balance:</b> <code>${bal:.2f} USD</code>\n"
        f"{CE('diamond')} <b>Active Package:</b> <code>{pname}</code>\n"
        f"{CE('date')} <b>Validity:</b> <code>{exp}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Add funds via Binance to purchase or upgrade your hosting subscriptions.</i>"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        cbtn("Deposit Binance", callback_data="deposit_binance", style="success", icon="binance"),
        cbtn("Browse Plans", callback_data="view_plans", style="primary", icon="diamond")
    )
    safe_send(chat_id, text, reply_markup=markup)

def show_plans_menu(chat_id, user_id):
    plans = get_all_plans()
    text = f"{CE('diamond')} <b>CLOUD SUBSCRIPTION TIERS</b> {CE('fire')}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    markup = types.InlineKeyboardMarkup(row_width=1)
    for pid, pname, mbots, price, days, desc in plans:
        text += (
            f"• <b>{pname}:</b> <code>${price:.2f} USD</code>\n"
            f"  {CE('power')} Limit: <code>{mbots} Bots</code> | {CE('date')} Duration: <code>{days} Days</code>\n"
            f"  <i>{desc}</i>\n\n"
        )
        markup.add(cbtn(f"Purchase {pname} (${price:.0f})", callback_data=f"buyplan_{pid}", style="primary", icon="diamond"))

    markup.add(cbtn("Deposit Balance", callback_data="deposit_binance", style="success", icon="binance"))
    safe_send(chat_id, text, reply_markup=markup)

# ─── MY BOTS (LIVE CONTROLLER) ─────────────────────────────────────────────
def show_user_bots(chat_id, user_id):
    flist = user_files.get(user_id, [])
    if not flist:
        return safe_send(chat_id, f"{CE('notice')} <b>You have no hosted instances deployed.</b>")

    markup = types.InlineKeyboardMarkup(row_width=1)
    for fn, ft, st in sorted(flist):
        running = (st == "approved" and is_bot_running(user_id, fn))
        st_text = "ONLINE" if running else "STOPPED"
        icon_k = "done" if running else "close"
        st_style = "success" if running else "danger"
        markup.add(cbtn(f"[{st_text}] {fn}", callback_data=f"ctl_{user_id}_{fn}", style=st_style, icon=icon_k))

    safe_send(chat_id, f"{CE('trader')} <b>DEPLOYED INSTANCES CONTROLLER:</b>", reply_markup=markup)

def show_bot_controls_card(chat_id, owner_id, fname, message_id=None):
    ftype, status = None, None
    for fn, ft, st in user_files.get(owner_id, []):
        if fn == fname:
            ftype, status = ft, st
            break

    if not ftype: return safe_send(chat_id, f"{CE('close')} <b>Instance record missing.</b>")

    running = (status == "approved" and is_bot_running(owner_id, fname))
    st_text = f"{CE('done')} ONLINE & RUNNING" if running else f"{CE('close')} STOPPED"

    card_text = (
        f"{CE('diamond')} <b>CONTAINER CONTROLLER #{fname}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('link')} <b>Runtime:</b> <code>{ftype.upper()}</code>\n"
        f"{CE('trader')} <b>Owner ID:</b> <code>{owner_id}</code>\n"
        f"{CE('speed')} <b>Status:</b> {st_text}"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    if running:
        markup.add(
            cbtn("Stop Process", callback_data=f"bact_stop_{owner_id}_{fname}", style="danger", icon="stop"),
            cbtn("Restart Process", callback_data=f"bact_restart_{owner_id}_{fname}", style="primary", icon="restart")
        )
    else:
        markup.add(
            cbtn("Start Process", callback_data=f"bact_start_{owner_id}_{fname}", style="success", icon="play"),
            cbtn("Delete Container", callback_data=f"bact_del_{owner_id}_{fname}", style="danger", icon="delete")
        )

    markup.add(
        cbtn("Terminal Logs", callback_data=f"bact_logs_{owner_id}_{fname}", style="primary", icon="logs"),
        cbtn("Download Backup (.zip)", callback_data=f"bact_dl_{owner_id}_{fname}", style="success", icon="download")
    )
    markup.add(cbtn("Return to Bots List", callback_data="back_my_bots", style="primary", icon="arrow_right"))

    if message_id:
        safe_edit(chat_id, message_id, card_text, reply_markup=markup)
    else:
        safe_send(chat_id, card_text, reply_markup=markup)

# ─── CALLBACK QUERY ENGINE ─────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    global bot_locked
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    # --- Force Sub Verification ---
    if data == "verify_fsub":
        command_start(call.message)
        bot.answer_callback_query(call.id, "Verified!")
        return

    # --- Skip Requirements in Upload ---
    if data.startswith("skip_req_"):
        fname = data.replace("skip_req_", "")
        user_staged_uploads.pop(user_id, None)
        fpath = os.path.join(get_user_folder(user_id), fname)
        forward_bot_to_admin(user_id, fname, fpath)
        safe_edit(chat_id, call.message.message_id, f"{CE('done')} <b>File dispatched to Admin for launch approval!</b>")
        bot.answer_callback_query(call.id)
        return

    # --- Admin File Approval ---
    if data.startswith("apprv_"):
        if user_id != OWNER_ID and user_id not in admin_ids:
            return bot.answer_callback_query(call.id, "Unauthorized.", show_alert=True)
        fid = data.replace("apprv_", "")
        info = pending_approvals.pop(fid, None)
        if not info:
            return bot.answer_callback_query(call.id, "Request expired or already processed.", show_alert=True)

        target_uid = info["user_id"]
        fname = info["file_name"]
        fpath = info["file_path"]

        save_user_file(target_uid, fname, info["file_type"], "approved")
        threading.Thread(target=run_script, args=(fpath, target_uid, get_user_folder(target_uid), fname, None)).start()

        bot.answer_callback_query(call.id, "Instance Approved!")
        safe_edit(chat_id, call.message.message_id, f"{CE('done')} <b>Worker <code>{fname}</code> Approved and Running!</b>")
        safe_send(target_uid, f"{CE('done')} <b>Your bot <code>{fname}</code> has been approved by admin and is now ONLINE!</b>")
        return

    if data.startswith("rjct_"):
        if user_id != OWNER_ID and user_id not in admin_ids: return
        fid = data.replace("rjct_", "")
        info = pending_approvals.pop(fid, None)
        if info:
            remove_user_file_db(info["user_id"], info["file_name"])
            try: os.remove(info["file_path"])
            except Exception: pass
            safe_send(info["user_id"], f"{CE('close')} <b>Your deployment request for <code>{info['file_name']}</code> was rejected by administrators.</b>")
        bot.answer_callback_query(call.id, "Rejected.")
        safe_edit(chat_id, call.message.message_id, f"{CE('close')} <b>Container Rejected & Purged.</b>")
        return

    # --- Admin Binance Deposit Approval ---
    if data.startswith("appdep_"):
        if user_id != OWNER_ID: return
        _, dep_id, target_uid = data.split("_")
        dep_id, target_uid = int(dep_id), int(target_uid)

        msg = safe_send(chat_id, f"{CE('money')} <b>Enter exact USD amount to credit for Deposit #{dep_id} (e.g. 25.0):</b>")
        bot.register_next_step_handler(msg, lambda m: process_deposit_approval_amount(m, dep_id, target_uid))
        bot.answer_callback_query(call.id)
        return

    if data.startswith("rejdep_"):
        if user_id != OWNER_ID: return
        _, dep_id, target_uid = data.split("_")
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("UPDATE deposits SET status = 'rejected' WHERE deposit_id = ?", (dep_id,))
            conn.commit()
            conn.close()
        bot.answer_callback_query(call.id, "Deposit Rejected.")
        safe_send(int(target_uid), f"{CE('close')} <b>Your deposit submission #{dep_id} was rejected by billing admin.</b>")
        return

    # --- Plan Purchase ---
    if data.startswith("buyplan_"):
        pid = data.replace("buyplan_", "")
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT plan_id, name, max_bots, price, days FROM plans WHERE plan_id = ?", (pid,))
            plan = c.fetchone()
            conn.close()

        if not plan: return bot.answer_callback_query(call.id, "Plan missing.", show_alert=True)
        _, pname, mbots, price, days = plan

        user = get_user_data(user_id)
        bal = user[3] if user else 0.0

        if bal < price:
            bot.answer_callback_query(call.id, f"Insufficient Balance! You need ${price:.2f} USD.", show_alert=True)
            return

        # Deduct balance & activate
        update_user_balance(user_id, -price)
        expiry = (datetime.now() + timedelta(days=days)).isoformat()

        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("UPDATE users SET plan_name = ?, plan_expiry = ? WHERE user_id = ?", (pname, expiry, user_id))
            conn.commit()
            conn.close()

        bot.answer_callback_query(call.id, "Subscription Activated!")
        safe_send(chat_id, f"{CE('done')} <b>Plan <code>{pname}</code> Activated!</b>\nValid for <code>{days} Days</code>. Slot quota increased to <code>{mbots} Bots</code>.")
        return

    # --- Bot Controls ---
    if data == "back_my_bots":
        show_user_bots(chat_id, user_id)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("ctl_"):
        _, owner_str, fname = data.split("_", 2)
        show_bot_controls_card(chat_id, int(owner_str), fname, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("bact_"):
        parts = data.split("_", 3)
        act, owner_id, fname = parts[1], int(parts[2]), parts[3]
        if user_id != owner_id and user_id not in admin_ids: return

        if act == "start":
            fpath = os.path.join(get_user_folder(owner_id), fname)
            threading.Thread(target=run_script, args=(fpath, owner_id, get_user_folder(owner_id), fname, None)).start()
            time.sleep(1.5)
            bot.answer_callback_query(call.id, "Process Started!")
            show_bot_controls_card(chat_id, owner_id, fname, call.message.message_id)

        elif act == "stop":
            skey = f"{owner_id}_{fname}"
            if skey in bot_scripts:
                kill_process_tree(bot_scripts[skey])
                bot_scripts.pop(skey, None)
            bot.answer_callback_query(call.id, "Process Stopped!")
            show_bot_controls_card(chat_id, owner_id, fname, call.message.message_id)

        elif act == "restart":
            skey = f"{owner_id}_{fname}"
            if skey in bot_scripts:
                kill_process_tree(bot_scripts[skey])
                bot_scripts.pop(skey, None)
            time.sleep(1)
            fpath = os.path.join(get_user_folder(owner_id), fname)
            threading.Thread(target=run_script, args=(fpath, owner_id, get_user_folder(owner_id), fname, None)).start()
            time.sleep(1.5)
            bot.answer_callback_query(call.id, "Process Rebooted!")
            show_bot_controls_card(chat_id, owner_id, fname, call.message.message_id)

        elif act == "logs":
            log_path = os.path.join(get_user_folder(owner_id), f"{os.path.splitext(fname)[0]}.log")
            if os.path.exists(log_path):
                with open(log_path, "r", errors="ignore") as f:
                    tail = "".join(f.readlines()[-25:]) or "Terminal buffer empty."
                safe_send(chat_id, f"{CE('logs')} <b>TERMINAL OUTPUT (<code>{fname}</code>):</b>\n<pre>{html.escape(tail)}</pre>")
            else:
                bot.answer_callback_query(call.id, "No logs recorded.", show_alert=True)

        elif act == "dl":
            folder = get_user_folder(owner_id)
            zip_path = os.path.join(BACKUPS_DIR, f"backup_{fname}")
            shutil.make_archive(zip_path, "zip", folder)
            full_zip = f"{zip_path}.zip"
            with open(full_zip, "rb") as f:
                bot.send_document(chat_id, f, caption=f"{CE('done')} <b>Complete Backup for {fname}</b>", parse_mode="HTML")
            if os.path.exists(full_zip): os.remove(full_zip)
            bot.answer_callback_query(call.id, "Backup Generated!")

        elif act == "del":
            skey = f"{owner_id}_{fname}"
            if skey in bot_scripts:
                kill_process_tree(bot_scripts[skey])
                bot_scripts.pop(skey, None)
            remove_user_file_db(owner_id, fname)
            fpath = os.path.join(get_user_folder(owner_id), fname)
            if os.path.exists(fpath): os.remove(fpath)
            bot.answer_callback_query(call.id, "Instance Deleted!")
            safe_edit(chat_id, call.message.message_id, f"{CE('delete')} <b>Instance <code>{fname}</code> permanently purged.</b>")

        return

    # --- Admin Console Routes ---
    if data == "adm_plans_mgr" and (user_id in admin_ids or user_id == OWNER_ID):
        plans = get_all_plans()
        text = f"{CE('diamond')} <b>PLAN MANAGER CONSOLE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        for pid, pname, mbots, price, days, _ in plans:
            text += f"• <code>{pid}</code>: <b>{pname}</b> | ${price:.0f} | {days}d | {mbots} bots\n"
            markup.add(cbtn(f"Delete: {pname}", callback_data=f"delplan_{pid}", style="danger", icon="delete"))
        markup.add(cbtn("Add New Plan", callback_data="add_plan_init", style="success", icon="up"))
        markup.add(cbtn("Back to Admin Console", callback_data="admin_console", style="primary", icon="arrow_right"))
        safe_edit(chat_id, call.message.message_id, text, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("delplan_"):
        pid = data.replace("delplan_", "")
        delete_plan_db(pid)
        bot.answer_callback_query(call.id, "Plan Deleted!")
        safe_send(chat_id, f"{CE('done')} <b>Plan <code>{pid}</code> removed from database.</b>")
        return

    if data == "add_plan_init":
        msg = safe_send(chat_id, f"{CE('sms')} <b>Send new plan details in format:</b>\n<code>plan_id | Plan Name | Max Bots | Price | Days | Description</code>\n\n<i>Example:</i>\n<code>mega | Mega Host | 15 | 40 | 30 | 15 Bot Slots with Dedicated Resources</code>")
        bot.register_next_step_handler(msg, process_add_plan_step)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_all_bots":
        markup = types.InlineKeyboardMarkup(row_width=1)
        count = 0
        for uid, files in user_files.items():
            for fn, ft, st in files:
                running = is_bot_running(uid, fn)
                st_icon = "done" if running else "close"
                markup.add(cbtn(f"{fn} ({uid})", callback_data=f"ctl_{uid}_{fn}", style="primary", icon=st_icon))
                count += 1
        markup.add(cbtn("Back to Admin Console", callback_data="admin_console", style="primary", icon="arrow_right"))
        safe_send(chat_id, f"{CE('trader')} <b>GLOBAL INSTANCES MONITOR ({count} Bots):</b>", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_scan_user":
        msg = safe_send(chat_id, f"{CE('search')} <b>Enter User ID to scan & adjust balance:</b>")
        bot.register_next_step_handler(msg, process_scan_user_input)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_broadcast":
        msg = safe_send(chat_id, f"{CE('notice')} <b>Send the announcement text you wish to broadcast to all users:</b>\n<i>Send /cancel to abort.</i>")
        bot.register_next_step_handler(msg, process_broadcast_transmission)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_reboot_all":
        count = 0
        for uid, files in user_files.items():
            for fn, ft, st in files:
                if st == "approved" and not is_bot_running(uid, fn):
                    fpath = os.path.join(get_user_folder(uid), fn)
                    threading.Thread(target=run_script, args=(fpath, uid, get_user_folder(uid), fn, None)).start()
                    count += 1
        safe_send(chat_id, f"{CE('done')} <b>Rebooted {count} idle worker instances.</b>")
        bot.answer_callback_query(call.id)
        return

    if data == "adm_stop_all":
        stopped = len(bot_scripts)
        for skey in list(bot_scripts.keys()):
            kill_process_tree(bot_scripts[skey])
            bot_scripts.pop(skey, None)
        safe_send(chat_id, f"{CE('stop')} <b>Terminated {stopped} active running processes.</b>")
        bot.answer_callback_query(call.id)
        return

    if data == "adm_lock_system":
        bot_locked = not bot_locked
        safe_send(chat_id, f"{CE('power')} <b>Emergency Lockdown State:</b> <code>{bot_locked}</code>")
        bot.answer_callback_query(call.id, "Lock State Toggled!")
        return

    if data == "admin_console":
        safe_send(chat_id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
        bot.answer_callback_query(call.id)
        return

    if data == "adm_close":
        try: bot.delete_message(chat_id, call.message.message_id)
        except Exception: pass
        bot.answer_callback_query(call.id)
        return

# ─── ADMIN STEP HANDLERS ───────────────────────────────────────────────────
def process_deposit_approval_amount(message, dep_id, target_uid):
    try:
        amount = float(message.text.strip())
        new_bal = update_user_balance(target_uid, amount)

        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("UPDATE deposits SET status = 'approved', amount = ? WHERE deposit_id = ?", (amount, dep_id))
            # Check if user had a referrer for deposit commission
            c.execute("SELECT referred_by FROM users WHERE user_id = ?", (target_uid,))
            ref_row = c.fetchone()
            conn.commit()
            conn.close()

        # Handle Referral Commission
        if ref_row and ref_row[0]:
            comm = amount * REFERRAL_DEPOSIT_COMMISSION
            update_user_balance(ref_row[0], comm)
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute("UPDATE users SET referral_earnings = referral_earnings + ? WHERE user_id = ?", (comm, ref_row[0]))
                conn.commit()
                conn.close()
            safe_send(ref_row[0], f"{CE('gift')} <b>Referral Commission Earned!</b>\nYour referral deposited <code>${amount:.2f}</code>. You received <code>${comm:.2f} USD</code> commission!")

        safe_send(message.chat.id, f"{CE('done')} <b>Deposit #{dep_id} Approved! User <code>{target_uid}</code> credited with <code>${amount:.2f}</code> (New Balance: <code>${new_bal:.2f}</code>).</b>")
        safe_send(target_uid, f"{CE('done')} <b>Deposit Confirmed!</b> <code>${amount:.2f} USD</code> has been credited to your Cloud Wallet. Available: <code>${new_bal:.2f}</code>.")
    except Exception as e:
        safe_send(message.chat.id, f"{CE('close')} <b>Invalid Amount figure:</b> {e}")

def process_add_plan_step(message):
    try:
        parts = [p.strip() for p in message.text.split("|")]
        pid, name, max_bots, price, days, desc = parts[0], parts[1], int(parts[2]), float(parts[3]), int(parts[4]), parts[5]
        save_or_update_plan(pid, name, max_bots, price, days, desc)
        safe_send(message.chat.id, f"{CE('done')} <b>Plan <code>{name}</code> ({pid}) successfully created!</b>")
    except Exception as e:
        safe_send(message.chat.id, f"{CE('close')} <b>Invalid format:</b> {e}")

def process_scan_user_input(message):
    try:
        uid = int(message.text.strip())
        u = get_user_data(uid)
        if not u:
            return safe_send(message.chat.id, f"{CE('close')} <b>User not found in database.</b>")

        status_str = "BANNED" if u[6] == 1 else "ACTIVE"
        text = (
            f"{CE('trader')} <b>USER PROFILE DOSSIER:</b> <code>{uid}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{CE('telegram')} <b>Username:</b> @{u[1] or 'N/A'}\n"
            f"{CE('wallet')} <b>Balance:</b> <code>${u[3]:.2f} USD</code>\n"
            f"{CE('diamond')} <b>Plan:</b> <code>{u[4] or 'Free Tier'}</code>\n"
            f"{CE('date')} <b>Expiry:</b> <code>{u[5] or 'N/A'}</code>\n"
            f"{CE('shield')} <b>Status:</b> <code>{status_str}</code>\n"
            f"{CE('power')} <b>Hosted Bots:</b> <code>{len(user_files.get(uid, []))}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Send an amount to adjust balance (e.g. <code>+15</code> or <code>-5</code>):</i>"
        )
        msg = safe_send(message.chat.id, text)
        bot.register_next_step_handler(msg, lambda m: process_balance_adjustment(m, uid))
    except Exception:
        safe_send(message.chat.id, f"{CE('close')} <b>Please provide a numerical User ID.</b>")

def process_balance_adjustment(message, target_uid):
    try:
        delta = float(message.text.strip())
        new_bal = update_user_balance(target_uid, delta)
        safe_send(message.chat.id, f"{CE('done')} <b>Balance Updated! User <code>{target_uid}</code> now has <code>${new_bal:.2f} USD</code>.</b>")
        safe_send(target_uid, f"{CE('notice')} <b>Wallet Adjustment Notice:</b>\nAn administrator modified your balance by <code>{delta:+.2f} USD</code>. Current: <code>${new_bal:.2f}</code>.")
    except Exception as e:
        safe_send(message.chat.id, f"{CE('close')} <b>Error:</b> {e}")

def process_broadcast_transmission(message):
    text = message.text or ""
    if text == "/cancel": return safe_send(message.chat.id, f"{CE('close')} <b>Broadcast Cancelled.</b>")
    status_m = safe_send(message.chat.id, f"{CE('loading')} <i>Transmitting announcement to network...</i>")
    sent, failed = 0, 0
    for uid in list(active_users):
        try:
            safe_send(uid, f"{CE('notice')} <b>NETWORK BROADCAST:</b>\n\n{text}")
            sent += 1
            time.sleep(0.04)
        except Exception: failed += 1
    safe_edit(message.chat.id, status_m.message_id, f"{CE('done')} <b>Broadcast Finished! Delivered: <code>{sent}</code> | Failed: <code>{failed}</code>.</b>")

# ─── BUTTON MAPPING & REPLY ENGINE ─────────────────────────────────────────
BUTTON_MAPPING = {
    "Upload File": lambda m: _logic_upload_file(m),
    "My Bots": lambda m: show_user_bots(m.chat.id, m.from_user.id),
    "Plans & Upgrade": lambda m: show_plans_menu(m.chat.id, m.from_user.id),
    "Wallet & Deposit": lambda m: show_wallet_menu(m.chat.id, m.from_user.id),
    "Server Benchmark": lambda m: _logic_speed(m),
    "Referral Program": lambda m: show_referral_menu(m.chat.id, m.from_user.id),
    "Help Desk": lambda m: safe_send(m.chat.id, f"{CE('support')} <b>Dedicated Consultant:</b> {YOUR_USERNAME}\n24/7 Priority Ticket Desk."),
    "Manual Install": lambda m: _prompt_manual_install(m),
    "Updates Channel": lambda m: safe_send(m.chat.id, f"{CE('link')} <b>Official Channel:</b> {UPDATE_CHANNEL}"),
    "Admin Console": lambda m: safe_send(m.chat.id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
}

def _logic_upload_file(message):
    user_id = message.from_user.id
    limit = get_user_file_limit(user_id)
    if get_user_file_count(user_id) >= limit:
        return safe_send(message.chat.id, f"{CE('close')} <b>Container Quota Full ({get_user_file_count(user_id)}/{limit})!</b> Upgrade your tier to deploy more bots.")
    safe_send(message.chat.id, f"{CE('up')} <b>Send your .py, .js, or .zip project file document now.</b>\n<i>Our pre-flight engine will inspect and stage your container for launch.</i>")

def _logic_speed(message):
    start = time.time()
    try: bot.get_me()
    except Exception: pass
    lat = round((time.time() - start) * 1000, 2)
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    safe_send(message.chat.id, f"{CE('speed')} <b>INFRASTRUCTURE BENCHMARK:</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{CE('done')} Latency: <code>{lat} ms</code>\n{CE('boom')} CPU: <code>{cpu}%</code>\n{CE('diamond')} RAM: <code>{ram}%</code>\n{CE('power')} Status: <code>100% Operational & Isolated</code>")

def _prompt_manual_install(message):
    msg = safe_send(message.chat.id, f"{CE('power')} <b>Manual Package Installation:</b>\nSend library name to install:\n• Python: <code>requests</code>, <code>telebot</code>\n• Node.js: <code>npm:express</code>")
    bot.register_next_step_handler(msg, _execute_manual_install)

def _execute_manual_install(message):
    pkg = message.text.strip()
    status_m = safe_send(message.chat.id, f"{CE('loading')} <i>Installing {pkg}...</i>")
    ok, text = install_system_package(pkg)
    safe_edit(message.chat.id, status_m.message_id, f"{CE('done') if ok else CE('close')} {text}")

@bot.message_handler(func=lambda m: m.text in BUTTON_MAPPING)
def handle_main_menu_buttons(message):
    if bot_locked and message.from_user.id not in admin_ids:
        return safe_send(message.chat.id, f"{CE('notice')} <b>System Locked for Maintenance.</b>")
    BUTTON_MAPPING[message.text](message)

# ─── BACKGROUND CRON SCHEDULER ─────────────────────────────────────────────
def expiry_cron_loop():
    while True:
        try:
            now = datetime.now()
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute("SELECT user_id, plan_name, plan_expiry FROM users WHERE plan_expiry IS NOT NULL")
                rows = c.fetchall()
                conn.close()

            for uid, pname, exp_str in rows:
                try:
                    exp = datetime.fromisoformat(exp_str)
                    if now >= exp:
                        with DB_LOCK:
                            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                            c = conn.cursor()
                            c.execute("UPDATE users SET plan_name = 'Free Tier', plan_expiry = NULL WHERE user_id = ?", (uid,))
                            conn.commit()
                            conn.close()

                        # Stop all active bots of user
                        for skey in list(bot_scripts.keys()):
                            if skey.startswith(f"{uid}_"):
                                kill_process_tree(bot_scripts[skey])
                                bot_scripts.pop(skey, None)

                        safe_send(uid, f"{CE('notice')} <b>Subscription Plan {pname} Expired!</b>\nYour running bots have been stopped. Renew to restore full container slots.")
                except Exception: pass
        except Exception: pass
        time.sleep(3600)

atexit.register(lambda: [kill_process_tree(p) for p in bot_scripts.values()])
threading.Thread(target=expiry_cron_loop, daemon=True).start()

if __name__ == "__main__":
    print("=" * 60)
    print(f" {BOT_NAME} - SYSTEM ONLINE ")
    print(f" Super Admin ID: {OWNER_ID}")
    print(f" Support: {YOUR_USERNAME}")
    print(" Payment: Only Binance Pay & USDT")
    print(" UI: Pure Custom Telegram Emojis & Validated Buttons")
    print("=" * 60)

    keep_alive()
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
