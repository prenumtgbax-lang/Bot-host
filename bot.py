# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║         NEBULA CLOUD HOSTING BOT — 100% WORKING & ZERO-CRASH              ║
║                                                                           ║
║  • Target Admin ID: 2014144404                                            ║
║  • Support: @YourDomains                                                  ║
║  • Token: 8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU                 ║
║  • 100% Working Buttons (Fixed all Freeze, Parsing & Callback Issues)     ║
║  • Safe Next-Step Escaper: Buttons Never Freeze or Get Stuck              ║
║  • Gateway: Binance Pay ID & USDT (Admin Toggleable)                      ║
║  • Full Bot Management: Start/Stop/Restart/Delete/Download Backup         ║
║  • Admin Controls: User Balance (+/-), Plan Manager & All Deployed Bots   ║
║  • Referral Commission & Bonus Engine Integrated                          ║
║  • Background Keep-Alive Server & 409 Conflict Auto-Recovery              ║
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

# ── KEEP-ALIVE SERVER (FOR 24/7 DEPLOYMENT ON RENDER/KOYEB/VPS) ────────────
app = Flask(__name__)

@app.route("/")
def home():
    return "Nebula Cloud Hosting System is Live & Healthy", 200

@app.route("/health")
def health():
    return "OK", 200

def run_flask_server():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[!] Flask server binding notice: {e}")

# ── CONFIGURATION & CREDENTIALS ─────────────────────────────────────────────
TOKEN = "8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU"
OWNER_ID = 2014144404
ADMIN_ID = 2014144404
YOUR_USERNAME = "@YourDomains"
SUPPORT_CONTACT_ID = 2014144404
UPDATE_CHANNEL = "https://t.me/YourChannel"

# Binance Payment Gateways Defaults
BINANCE_PAY_ID = "746899490"
BINANCE_USDT_ADDRESS = "TVgQoqGMipsdYsbtV7PPj6FKW9MM29fVDq"

# Referral Engine Settings
REFERRAL_JOIN_BONUS = 0.50  # USD for inviting a member
REFERRAL_DEPOSIT_COMMISSION = 0.10  # 10% commission on deposit

FORCE_SUB_CHANNELS = [
    {
        "name": "Updates Channel",
        "chat_id": "@YourChannel",
        "url": "https://t.me/YourChannel",
    }
]

# Path Configurations
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

# --- In-Memory Caches ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
user_profiles = {}
banned_users = set()
bot_settings_cache = {}
bot_locked = False
pending_approvals = {}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Safe Messaging Delivery Engine ---
def safe_send(chat_id, text, reply_markup=None):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        logger.error(f"safe_send error: {e}")
        try:
            clean_text = re.sub(r'<[^>]*>', '', text)
            return bot.send_message(chat_id, clean_text, reply_markup=reply_markup)
        except Exception:
            return None

def safe_reply(message, text, reply_markup=None):
    try:
        return bot.reply_to(message, text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        logger.error(f"safe_reply error: {e}")
        try:
            clean_text = re.sub(r'<[^>]*>', '', text)
            return bot.reply_to(message, clean_text, reply_markup=reply_markup)
        except Exception:
            return None

def safe_edit(chat_id, message_id, text, reply_markup=None):
    try:
        return bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        logger.error(f"safe_edit error: {e}")
        try:
            clean_text = re.sub(r'<[^>]*>', '', text)
            return bot.edit_message_text(clean_text, chat_id, message_id, reply_markup=reply_markup)
        except Exception:
            return None

# --- Database Schema & Initialization ---
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
            status TEXT DEFAULT 'pending',
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
        c.execute("""CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT)""")

        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('update_channel', ?)", (UPDATE_CHANNEL,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_pay_id', ?)", (BINANCE_PAY_ID,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_usdt_address', ?)", (BINANCE_USDT_ADDRESS,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_enabled', '1')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('free_user_limit', ?)", (str(FREE_USER_LIMIT),))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('bot_off_message', 'System offline for maintenance.')")
        c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))

        c.execute("SELECT COUNT(*) FROM plans")
        if c.fetchone()[0] == 0:
            default_plans = [
                ("starter", "Starter Tier", 3, 10.0, 30, "3 Bot Hosting Slots for 30 Days"),
                ("pro", "Pro Tier", 8, 25.0, 30, "8 Bot Hosting Slots + Dedicated RAM"),
                ("vip", "VIP Ultra", 20, 50.0, 30, "20 Bot Slots + Dedicated Priority"),
                ("lifetime", "Lifetime Access", 50, 150.0, 3650, "50 Bot Hosting Slots for 10 Years")
            ]
            c.executemany("INSERT INTO plans VALUES (?, ?, ?, ?, ?, ?)", default_plans)

        conn.commit()
        conn.close()

def load_data():
    with DB_LOCK:
        user_files.clear()
        active_users.clear()
        user_profiles.clear()
        banned_users.clear()
        admin_ids.clear()
        admin_ids.update({ADMIN_ID, OWNER_ID})

        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT user_id, plan_name, plan_expiry FROM users WHERE plan_expiry IS NOT NULL")
        for uid, pname, exp in c.fetchall():
            try: user_subscriptions[uid] = {"plan_name": pname, "expiry": datetime.fromisoformat(exp)}
            except Exception: pass

        c.execute("SELECT user_id, file_name, file_type, COALESCE(status, 'pending') FROM user_files")
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
        c.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, str(value)))
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

def save_user_file(user_id, file_name, file_type="py", status="pending"):
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
    if u and u[5]:
        try:
            if datetime.fromisoformat(u[5]) > datetime.now():
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

# ─── RELIABLE PACKAGE INSTALLER ────────────────────────────────────────────
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

def install_system_package(pkg_input):
    if pkg_input.lower().startswith("npm:"):
        pkg_name = pkg_input[4:].strip()
        cmd = ["npm", "install", "-g", pkg_name]
    else:
        pkg_name = pkg_input.strip()
        pkg_name = TELEGRAM_MODULES.get(pkg_name.lower(), pkg_name)
        cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages", pkg_name]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode == 0:
            return True, f"Package <code>{pkg_name}</code> installed successfully."
        else:
            fallback_cmd = [sys.executable, "-m", "pip", "install", "--user", pkg_name]
            res_fb = subprocess.run(fallback_cmd, capture_output=True, text=True, timeout=180)
            if res_fb.returncode == 0:
                return True, f"Package <code>{pkg_name}</code> installed successfully."
            err = res.stderr or res.stdout or "Error installing package."
            return False, f"Install Error: <code>{html.escape(err[-250:])}</code>"
    except Exception as e:
        return False, f"Execution Failure: <code>{str(e)}</code>"

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
                try: child.kill()
                except Exception: pass
            parent.kill()
    except Exception as e:
        logger.error(f"Kill process error: {e}")

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply=None, attempt=1):
    max_attempts = 2
    script_key = f"{script_owner_id}_{file_name}"
    log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")

    if script_key in bot_scripts:
        kill_process_tree(bot_scripts[script_key])
        bot_scripts.pop(script_key, None)

    req_file = os.path.join(user_folder, "requirements.txt")
    if os.path.exists(req_file):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", req_file],
                           capture_output=True, timeout=120)
        except Exception: pass

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
                safe_send(script_owner_id, f"⚠️ <b>Execution Stopped on Launch:</b>\n<pre>{html.escape(tail)}</pre>")
            return False

        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "script_owner_id": script_owner_id,
            "user_folder": user_folder,
            "type": "py"
        }

        safe_send(script_owner_id, f"✅ <b>Container Online:</b> <code>{file_name}</code> (PID: <code>{process.pid}</code>)")
        return True
    except Exception as e:
        safe_send(script_owner_id, f"❌ <b>Process Failure:</b> <code>{str(e)}</code>")
        return False

# ─── REAL PURGE / BOT DELETION ENGINE ──────────────────────────────────────
def execute_permanent_bot_delete(owner_id, fname, executed_by_admin=False):
    skey = f"{owner_id}_{fname}"
    if skey in bot_scripts:
        kill_process_tree(bot_scripts[skey])
        bot_scripts.pop(skey, None)

    remove_user_file_db(owner_id, fname)
    user_folder = get_user_folder(owner_id)
    main_file = os.path.join(user_folder, fname)
    log_file = os.path.join(user_folder, f"{os.path.splitext(fname)[0]}.log")

    try:
        if os.path.exists(main_file): os.remove(main_file)
    except Exception: pass

    try:
        if os.path.exists(log_file): os.remove(log_file)
    except Exception: pass

    if executed_by_admin and owner_id != OWNER_ID:
        safe_send(owner_id, f"🗑️ <b>Administrative Notice:</b>\nYour bot container <code>{fname}</code> was terminated and purged from the server.")

# ─── RELIABLE 100% WORKING MENUS & KEYBOARDS ──────────────────────────────
COMMAND_BUTTONS_USER = [
    ["📤 Upload File", "🤖 My Bots"],
    ["💎 Plans & Upgrade", "💳 Wallet & Deposit"],
    ["⚡ Server Benchmark", "🎁 Referral Program"],
    ["🎧 Help Desk", "⚙️ Manual Install"],
    ["📢 Updates Channel"]
]

COMMAND_BUTTONS_ADMIN = [
    ["📤 Upload File", "🤖 My Bots"],
    ["💎 Plans & Upgrade", "💳 Wallet & Deposit"],
    ["⚡ Server Benchmark", "🎁 Referral Program"],
    ["👑 Admin Console", "⚙️ Manual Install"],
    ["🎧 Help Desk", "📢 Updates Channel"]
]

def create_main_reply_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout = COMMAND_BUTTONS_ADMIN if (user_id in admin_ids or user_id == OWNER_ID) else COMMAND_BUTTONS_USER
    for row in layout:
        markup.add(*[types.KeyboardButton(txt) for txt in row])
    return markup

def create_admin_panel_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💎 Manage Plans", callback_data="adm_plans_mgr"),
        types.InlineKeyboardButton("🤖 All Deployed Bots", callback_data="adm_all_bots"),
    )
    markup.add(
        types.InlineKeyboardButton("🔍 Scan User & Balance", callback_data="adm_scan_user"),
        types.InlineKeyboardButton("⏳ Pending Approvals", callback_data="adm_pending_files"),
    )
    markup.add(
        types.InlineKeyboardButton("📢 Broadcast Notice", callback_data="adm_broadcast"),
        types.InlineKeyboardButton("📩 SMS All Bot Owners", callback_data="adm_bots_sms"),
    )
    markup.add(
        types.InlineKeyboardButton("💳 Binance Gateways", callback_data="adm_binance_cfg"),
        types.InlineKeyboardButton("🗄️ Switch Database", callback_data="adm_change_db"),
    )
    markup.add(
        types.InlineKeyboardButton("▶️ Reboot All Workers", callback_data="adm_reboot_all"),
        types.InlineKeyboardButton("⏹️ Stop All Workers", callback_data="adm_stop_all"),
    )
    markup.add(
        types.InlineKeyboardButton("🔒 Lock System", callback_data="adm_lock_system"),
        types.InlineKeyboardButton("❌ Close Console", callback_data="adm_close"),
    )
    return markup

# ─── BUTTON MAPPING & REPLY ROUTER ─────────────────────────────────────────
BUTTON_MAPPING = {
    "Upload File": lambda m: _logic_upload_file(m),
    "My Bots": lambda m: show_user_bots(m.chat.id, m.from_user.id),
    "Plans & Upgrade": lambda m: show_plans_menu(m.chat.id, m.from_user.id),
    "Wallet & Deposit": lambda m: show_wallet_menu(m.chat.id, m.from_user.id),
    "Server Benchmark": lambda m: _logic_speed(m),
    "Referral Program": lambda m: show_referral_menu(m.chat.id, m.from_user.id),
    "Help Desk": lambda m: safe_send(m.chat.id, f"🎧 <b>Dedicated Consultant:</b> {YOUR_USERNAME}\n24/7 Priority Support Desk."),
    "Manual Install": lambda m: _prompt_manual_install(m),
    "Updates Channel": lambda m: safe_send(m.chat.id, f"📢 <b>Official Channel:</b> {UPDATE_CHANNEL}"),
    "Admin Console": lambda m: safe_send(m.chat.id, "👑 <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
}

def match_reply_button(text):
    t_clean = re.sub(r'[^\w\s]', '', text or '').strip().lower()
    for k in BUTTON_MAPPING:
        k_clean = re.sub(r'[^\w\s]', '', k).strip().lower()
        if k_clean in t_clean or t_clean in k_clean:
            return BUTTON_MAPPING[k]
    return None

# ─── SAFE NEXT STEP ESCAPER (BUTTONS NEVER FREEZE) ────────────────────────
def safe_next_step(msg, callback):
    """If user taps ANY menu button or sends /start, immediately cancels pending state and executes button."""
    def wrapper(message):
        text = (message.text or "").strip()
        if text.startswith("/"):
            if text == "/start":
                command_start(message)
                return
            elif text == "/admin" and (message.from_user.id in admin_ids or message.from_user.id == OWNER_ID):
                safe_send(message.chat.id, "👑 <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
                return
        handler = match_reply_button(text)
        if handler:
            handler(message)
            return
        callback(message)
    bot.register_next_step_handler(msg, wrapper)

# ─── REGISTRATION & WELCOME ────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def command_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username or "N/A"
    name = message.from_user.first_name or "User"

    referrer_id = None
    parts = message.text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            ref_candidate = int(parts[1].replace("ref_", ""))
            if ref_candidate != user_id:
                referrer_id = ref_candidate
        except Exception: pass

    user = get_user_data(user_id)
    if not user:
        now = datetime.now().isoformat()
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (user_id, username, name, joined_at, referred_by) VALUES (?, ?, ?, ?, ?)",
                      (user_id, username, name, now, referrer_id))
            c.execute("INSERT OR IGNORE INTO active_users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            conn.close()

        active_users.add(user_id)
        user_profiles[user_id] = {"name": name, "username": username}

        if referrer_id:
            update_user_balance(referrer_id, REFERRAL_JOIN_BONUS)
            safe_send(referrer_id, f"🎁 <b>New Referral Registered!</b>\nUser <code>{user_id}</code> joined via your link. You earned <code>${REFERRAL_JOIN_BONUS:.2f}</code> bonus!")

    user = get_user_data(user_id)
    if user and user[6] == 1:
        safe_send(chat_id, "⚠️ <b>Account Restricted from Accessing Network.</b>")
        return

    # Force Sub Verification
    if not (user_id == OWNER_ID or user_id in admin_ids):
        for ch in FORCE_SUB_CHANNELS:
            try:
                m = bot.get_chat_member(ch["chat_id"], user_id)
                if m.status in ["left", "kicked"]:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("📢 Join Updates Channel", url=ch["url"]))
                    markup.add(types.InlineKeyboardButton("✅ Verify Membership", callback_data="verify_fsub"))
                    safe_send(chat_id, "🛡️ <b>Channel Membership Required!</b>\nPlease subscribe to our official channel to unlock container hosting slots:", reply_markup=markup)
                    return
            except Exception: pass

    bal = user[3] if user else 0.0
    pname = user[4] if user and user[4] else "Free Tier"
    slots_used = get_user_file_count(user_id)
    max_slots = get_user_file_limit(user_id)
    limit_str = str(max_slots) if max_slots != float('inf') else "Unlimited"

    welcome_text = (
        f"👑 <b>NEBULA CLOUD HOSTING ENGINE</b> ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Holder:</b> <code>{html.escape(name)}</code>\n"
        f"🔗 <b>Account ID:</b> <code>{user_id}</code>\n"
        f"💳 <b>Balance:</b> <code>${bal:.2f} USD</code>\n"
        f"🛡️ <b>Subscription:</b> <code>{pname}</code>\n"
        f"⚡ <b>Allocated Slots:</b> <code>{slots_used} / {limit_str}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <i>High-Speed 24/7 Subprocess Container Hosting (Python & Node.js).</i>\n"
        f"<i>Select an option below to initiate operations:</i>"
    )
    safe_send(chat_id, welcome_text, reply_markup=create_main_reply_keyboard(user_id))

# ─── 2-STEP UPLOAD & STRICT ADMIN FORWARDING ──────────────────────────────
user_staged_uploads = {}

@bot.message_handler(content_types=["document"])
def handle_incoming_file(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document

    user = get_user_data(user_id)
    if user and user[6] == 1:
        return safe_send(chat_id, "⚠️ <b>Account Restricted.</b>")

    limit = get_user_file_limit(user_id)
    if get_user_file_count(user_id) >= limit:
        return safe_send(chat_id, f"❌ <b>Container Quota Full ({get_user_file_count(user_id)}/{limit})!</b> Upgrade your plan to deploy more bots.")

    filename = doc.file_name or "main.py"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".py", ".js", ".zip", ".txt"]:
        return safe_send(chat_id, "❌ <b>Unsupported File! Send .py, .js, .zip, or requirements.txt.</b>")

    user_folder = get_user_folder(user_id)

    if filename.lower() == "requirements.txt" and user_id in user_staged_uploads:
        wait_m = safe_reply(message, "⏳ <i>Linking requirements.txt and preparing admin dispatch...</i>")
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open(os.path.join(user_folder, "requirements.txt"), "wb") as f:
            f.write(downloaded)

        staged_fname = user_staged_uploads.pop(user_id)
        forward_bot_to_admin(user_id, staged_fname, os.path.join(user_folder, staged_fname))
        safe_edit(chat_id, wait_m.message_id, "✅ <b>Script & Requirements forwarded to Admin! Pending approval.</b>")
        return

    wait_m = safe_reply(message, "⏳ <i>Downloading & staging file...</i>")
    file_info = bot.get_file(doc.file_id)
    downloaded = bot.download_file(file_info.file_path)
    file_path = os.path.join(user_folder, filename)
    with open(file_path, "wb") as f:
        f.write(downloaded)

    if ext == ".py":
        user_staged_uploads[user_id] = filename
        step2_text = (
            f"✅ <b>STEP 1 VERIFIED: SCRIPT PARSED!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 <b>File:</b> <code>{filename}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📤 <b>STEP 2: UPLOAD REQUIREMENTS.TXT</b>\n\n"
            f"Please send your <code>requirements.txt</code> file now.\n"
            f"<i>(If this bot requires no external libraries, tap Skip below)</i>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⚡ Skip Requirements", callback_data=f"skip_req_{filename}"))
        markup.add(types.InlineKeyboardButton("❌ Cancel Deployment", callback_data="cancel_action"))
        safe_edit(chat_id, wait_m.message_id, step2_text, reply_markup=markup)

    elif ext in [".js", ".zip"]:
        forward_bot_to_admin(user_id, filename, file_path)
        safe_edit(chat_id, wait_m.message_id, "✅ <b>File forwarded to Admin! Waiting for approval before launch.</b>")

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
        types.InlineKeyboardButton("▶️ Approve & Run", callback_data=f"apprv_{file_id}"),
        types.InlineKeyboardButton("🗑️ Reject & Purge", callback_data=f"rjct_{file_id}")
    )

    caption = (
        f"🔔 <b>NEW HOSTING CONTAINER DISPATCHED (PENDING)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User:</b> {html.escape(name)} ({username})\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"📄 <b>File Name:</b> <code>{filename}</code>\n"
        f"⏰ <b>Time:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
    )

    try:
        with open(file_path, "rb") as f:
            bot.send_document(OWNER_ID, f, caption=caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        safe_send(OWNER_ID, caption + f"\n\n<i>(Attachment relay fallback: {e})</i>", reply_markup=markup)

# ─── BINANCE GATEWAY CONFIGURATION ─────────────────────────────────────────
def show_binance_config_panel(chat_id, message_id=None):
    enabled = get_setting("binance_enabled", "1") == "1"
    pay_id = get_setting("binance_pay_id", BINANCE_PAY_ID)
    usdt_addr = get_setting("binance_usdt_address", BINANCE_USDT_ADDRESS)

    status_str = "🟢 ENABLED (ONLINE)" if enabled else "🔴 DISABLED (OFFLINE)"
    toggle_text = "🔴 Disable Gateway" if enabled else "🟢 Enable Gateway"

    text = (
        f"💳 <b>BINANCE GATEWAY CONFIGURATION</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>Current Status:</b> {status_str}\n"
        f"🆔 <b>Binance Pay ID:</b> <code>{pay_id}</code>\n"
        f"🪙 <b>USDT Address:</b> <code>{usdt_addr}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Select an option below to modify gateway parameters:</i>"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(toggle_text, callback_data="adm_toggle_binance"),
        types.InlineKeyboardButton("✏️ Set Pay ID", callback_data="adm_set_pay_id")
    )
    markup.add(
        types.InlineKeyboardButton("🪙 Set USDT Address", callback_data="adm_set_usdt_addr"),
        types.InlineKeyboardButton("⬅️ Back to Admin Console", callback_data="admin_console")
    )

    if message_id:
        safe_edit(chat_id, message_id, text, reply_markup=markup)
    else:
        safe_send(chat_id, text, reply_markup=markup)

# ─── BINANCE DEPOSIT FLOW ──────────────────────────────────────────────────
def trigger_deposit_binance(chat_id, user_id):
    enabled = get_setting("binance_enabled", "1") == "1"
    if not enabled:
        return safe_send(chat_id, "❌ <b>Binance deposits are currently paused by administration for maintenance. Please check back later!</b>")

    pay_id = get_setting("binance_pay_id", BINANCE_PAY_ID)
    usdt_addr = get_setting("binance_usdt_address", BINANCE_USDT_ADDRESS)

    text = (
        f"💳 <b>BINANCE OFFICIAL PAYMENT GATEWAY</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Send USDT to our verified Binance credentials:\n\n"
        f"🆔 <b>Binance Pay ID:</b> <code>{pay_id}</code> (Tap to Copy)\n"
        f"🪙 <b>USDT Address (BEP20/TRC20):</b>\n<code>{usdt_addr}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"➡️ <b>Next Step:</b> Send your <b>Payment Screenshot</b> and include the <b>Amount & TrxID</b> as caption!"
    )
    safe_send(chat_id, text)

@bot.message_handler(content_types=["photo"])
def handle_payment_screenshot_upload(message):
    user_id = message.from_user.id
    enabled = get_setting("binance_enabled", "1") == "1"
    if not enabled:
        return safe_reply(message, "❌ <b>Binance deposits are currently closed.</b>")

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
        types.InlineKeyboardButton("✅ Approve Deposit", callback_data=f"appdep_{dep_id}_{user_id}"),
        types.InlineKeyboardButton("❌ Reject Deposit", callback_data=f"rejdep_{dep_id}_{user_id}")
    )

    admin_cap = (
        f"💳 <b>NEW BINANCE DEPOSIT SUBMITTED #{dep_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
        f"✉️ <b>Submission Details:</b> <code>{html.escape(caption_text)}</code>\n"
        f"📅 <b>Time:</b> <code>{now_str}</code>"
    )

    try:
        bot.send_photo(OWNER_ID, message.photo[-1].file_id, caption=admin_cap, reply_markup=markup, parse_mode="HTML")
        safe_reply(message, "✅ <b>Deposit Proof Received!</b>\nOur administrators will verify and credit your balance shortly.")
    except Exception as e:
        safe_reply(message, f"❌ Error sending proof to admin: {e}")

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
        f"🎁 <b>AFFILIATE & REFERRAL PROGRAM</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Share your unique referral link to earn wallet balance bonuses!\n\n"
        f"🔗 <b>Your Referral Link:</b>\n<code>{ref_link}</code>\n\n"
        f"• <b>Join Bonus:</b> <code>${REFERRAL_JOIN_BONUS:.2f} USD</code> per verified referral\n"
        f"• <b>Deposit Commission:</b> <code>10%</code> of every deposit made\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Referrals:</b> <code>{ref_count} Members</code>\n"
        f"💰 <b>Total Affiliate Profits:</b> <code>${earnings:.2f} USD</code>"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎁 Share Referral Link", url=f"https://t.me/share/url?url={ref_link}&text=Deploy%20Telegram%20Bots%2024/7%20on%20Nebula%20Cloud!"))
    safe_send(chat_id, text, reply_markup=markup)

# ─── WALLET & PLANS INTERFACES ─────────────────────────────────────────────
def show_wallet_menu(chat_id, user_id):
    user = get_user_data(user_id)
    bal = user[3] if user else 0.0
    pname = user[4] if user and user[4] else "Free Tier"
    exp = user[5] if user and user[5] else "No Active Expiry"

    text = (
        f"💳 <b>YOUR CLOUD WALLET</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Available Balance:</b> <code>${bal:.2f} USD</code>\n"
        f"💎 <b>Active Package:</b> <code>{pname}</code>\n"
        f"📅 <b>Validity:</b> <code>{exp}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Add funds via Binance to purchase or upgrade your hosting subscriptions.</i>"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🟡 Deposit Binance", callback_data="deposit_binance"),
        types.InlineKeyboardButton("💎 Browse Plans", callback_data="view_plans")
    )
    safe_send(chat_id, text, reply_markup=markup)

def show_plans_menu(chat_id, user_id):
    plans = get_all_plans()
    text = "💎 <b>CLOUD SUBSCRIPTION TIERS</b> ⚡\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    markup = types.InlineKeyboardMarkup(row_width=1)
    for pid, pname, mbots, price, days, desc in plans:
        text += (
            f"• <b>{pname}:</b> <code>${price:.2f} USD</code>\n"
            f"  ⚡ Limit: <code>{mbots} Bots</code> | 📅 Duration: <code>{days} Days</code>\n"
            f"  <i>{desc}</i>\n\n"
        )
        markup.add(types.InlineKeyboardButton(f"🛒 Purchase {pname} (${price:.0f})", callback_data=f"buyplan_{pid}"))

    markup.add(types.InlineKeyboardButton("💳 Deposit Balance (Binance)", callback_data="deposit_binance"))
    safe_send(chat_id, text, reply_markup=markup)

# ─── MY BOTS CONTROLLER ────────────────────────────────────────────────────
def show_user_bots(chat_id, user_id):
    flist = user_files.get(user_id, [])
    if not flist:
        return safe_send(chat_id, "🔔 <b>You have no hosted instances deployed.</b>")

    markup = types.InlineKeyboardMarkup(row_width=1)
    for fn, ft, st in sorted(flist):
        if st == "pending":
            markup.add(types.InlineKeyboardButton(f"⏳ [PENDING APPROVAL] {fn}", callback_data=f"ctl_{user_id}_{fn}"))
        else:
            running = (st == "approved" and is_bot_running(user_id, fn))
            st_text = "🟢 ONLINE" if running else "🔴 STOPPED"
            markup.add(types.InlineKeyboardButton(f"[{st_text}] {fn}", callback_data=f"ctl_{user_id}_{fn}"))

    safe_send(chat_id, "🤖 <b>DEPLOYED INSTANCES CONTROLLER:</b>", reply_markup=markup)

def show_bot_controls_card(chat_id, owner_id, fname, message_id=None):
    ftype, status = None, None
    for fn, ft, st in user_files.get(owner_id, []):
        if fn == fname:
            ftype, status = ft, st
            break

    if not ftype:
        return safe_send(chat_id, "❌ <b>Instance record missing.</b>")

    if status == "pending":
        st_text = "⏳ PENDING ADMIN APPROVAL"
    elif is_bot_running(owner_id, fname):
        st_text = "🟢 ONLINE & RUNNING"
    else:
        st_text = "🔴 STOPPED"

    card_text = (
        f"🤖 <b>CONTAINER CONTROLLER #{fname}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ <b>Runtime:</b> <code>{ftype.upper()}</code>\n"
        f"👤 <b>Owner ID:</b> <code>{owner_id}</code>\n"
        f"⚡ <b>Status:</b> {st_text}"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    if status == "approved":
        if is_bot_running(owner_id, fname):
            markup.add(
                types.InlineKeyboardButton("⏹️ Stop Process", callback_data=f"bact_stop_{owner_id}_{fname}"),
                types.InlineKeyboardButton("🔄 Restart Process", callback_data=f"bact_restart_{owner_id}_{fname}")
            )
        else:
            markup.add(
                types.InlineKeyboardButton("▶️ Start Process", callback_data=f"bact_start_{owner_id}_{fname}"),
                types.InlineKeyboardButton("🗑️ Delete Container", callback_data=f"bact_del_{owner_id}_{fname}")
            )
    else:
        markup.add(types.InlineKeyboardButton("🗑️ Delete Container", callback_data=f"bact_del_{owner_id}_{fname}"))

    markup.add(
        types.InlineKeyboardButton("📜 Terminal Logs", callback_data=f"bact_logs_{owner_id}_{fname}"),
        types.InlineKeyboardButton("📥 Download Backup (.zip)", callback_data=f"bact_dl_{owner_id}_{fname}")
    )
    markup.add(types.InlineKeyboardButton("⬅️ Return to Bots List", callback_data="back_my_bots"))

    if message_id:
        safe_edit(chat_id, message_id, card_text, reply_markup=markup)
    else:
        safe_send(chat_id, card_text, reply_markup=markup)

# ─── CALLBACK QUERY ENGINE (100% RELIABLE & CONNECTED) ─────────────────────
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    global bot_locked
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    if data == "verify_fsub":
        command_start(call.message)
        bot.answer_callback_query(call.id, "Verified!")
        return

    if data == "deposit_binance":
        trigger_deposit_binance(chat_id, user_id)
        bot.answer_callback_query(call.id)
        return

    if data in ["view_plans", "view_plans_cb"]:
        show_plans_menu(chat_id, user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "cancel_action":
        user_staged_uploads.pop(user_id, None)
        safe_edit(chat_id, call.message.message_id, "❌ <b>Operation Cancelled.</b>")
        bot.answer_callback_query(call.id)
        return

    if data.startswith("skip_req_"):
        fname = data.replace("skip_req_", "")
        user_staged_uploads.pop(user_id, None)
        fpath = os.path.join(get_user_folder(user_id), fname)
        forward_bot_to_admin(user_id, fname, fpath)
        safe_edit(chat_id, call.message.message_id, "✅ <b>File dispatched to Admin for launch approval!</b>")
        bot.answer_callback_query(call.id)
        return

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
        safe_edit(chat_id, call.message.message_id, f"✅ <b>Worker <code>{fname}</code> Approved and Running!</b>")
        safe_send(target_uid, f"✅ <b>Your bot <code>{fname}</code> has been approved by admin and is now ONLINE!</b>")
        return

    if data.startswith("rjct_"):
        if user_id != OWNER_ID and user_id not in admin_ids: return
        fid = data.replace("rjct_", "")
        info = pending_approvals.pop(fid, None)
        if info:
            execute_permanent_bot_delete(info["user_id"], info["file_name"])
            safe_send(info["user_id"], f"❌ <b>Your deployment request for <code>{info['file_name']}</code> was rejected and removed.</b>")
        bot.answer_callback_query(call.id, "Rejected.")
        safe_edit(chat_id, call.message.message_id, "❌ <b>Container Rejected & Purged.</b>")
        return

    if data.startswith("appdep_"):
        if user_id != OWNER_ID: return
        _, dep_id, target_uid = data.split("_")
        dep_id, target_uid = int(dep_id), int(target_uid)

        msg = safe_send(chat_id, f"💰 <b>Enter exact USD amount to credit for Deposit #{dep_id} (e.g. 25.0):</b>")
        safe_next_step(msg, lambda m: process_deposit_approval_amount(m, dep_id, target_uid))
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
        safe_send(int(target_uid), f"❌ <b>Your deposit submission #{dep_id} was rejected by billing admin.</b>")
        return

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

        update_user_balance(user_id, -price)
        expiry = (datetime.now() + timedelta(days=days)).isoformat()

        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("UPDATE users SET plan_name = ?, plan_expiry = ? WHERE user_id = ?", (pname, expiry, user_id))
            conn.commit()
            conn.close()

        bot.answer_callback_query(call.id, "Subscription Activated!")
        safe_send(chat_id, f"✅ <b>Plan <code>{pname}</code> Activated!</b>\nValid for <code>{days} Days</code>. Slot quota increased to <code>{mbots} Bots</code>.")
        return

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

        ftype, st = None, None
        for fn, ft, s in user_files.get(owner_id, []):
            if fn == fname:
                ftype, st = ft, s
                break

        if act == "start":
            if st != "approved":
                return bot.answer_callback_query(call.id, "Cannot start: This bot is pending admin approval.", show_alert=True)
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
            if st != "approved":
                return bot.answer_callback_query(call.id, "Cannot restart: Bot not approved yet.", show_alert=True)
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
                safe_send(chat_id, f"📜 <b>TERMINAL OUTPUT (<code>{fname}</code>):</b>\n<pre>{html.escape(tail)}</pre>")
            else:
                bot.answer_callback_query(call.id, "No logs recorded.", show_alert=True)

        elif act == "dl":
            folder = get_user_folder(owner_id)
            zip_path = os.path.join(BACKUPS_DIR, f"backup_{fname}")
            shutil.make_archive(zip_path, "zip", folder)
            full_zip = f"{zip_path}.zip"
            with open(full_zip, "rb") as f:
                bot.send_document(chat_id, f, caption=f"✅ <b>Complete Backup for {fname}</b>", parse_mode="HTML")
            if os.path.exists(full_zip): os.remove(full_zip)
            bot.answer_callback_query(call.id, "Backup Generated!")

        elif act == "del":
            is_adm = (user_id in admin_ids or user_id == OWNER_ID)
            execute_permanent_bot_delete(owner_id, fname, executed_by_admin=is_adm)
            bot.answer_callback_query(call.id, "Bot completely deleted!")
            safe_edit(chat_id, call.message.message_id, f"🗑️ <b>Bot container <code>{fname}</code> has been completely terminated & purged.</b>")

        return

    # --- Admin Operations (Full Connection) ---
    if data == "adm_binance_cfg" and (user_id in admin_ids or user_id == OWNER_ID):
        show_binance_config_panel(chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_toggle_binance" and (user_id in admin_ids or user_id == OWNER_ID):
        cur = get_setting("binance_enabled", "1") == "1"
        new_val = "0" if cur else "1"
        set_setting("binance_enabled", new_val)
        show_binance_config_panel(chat_id, call.message.message_id)
        bot.answer_callback_query(call.id, "Gateway Status Updated!")
        return

    if data == "adm_set_pay_id" and (user_id in admin_ids or user_id == OWNER_ID):
        msg = safe_send(chat_id, "💳 <b>Enter new Binance Pay ID:</b>")
        safe_next_step(msg, process_set_binance_pay_id)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_set_usdt_addr" and (user_id in admin_ids or user_id == OWNER_ID):
        msg = safe_send(chat_id, "🪙 <b>Enter new Binance USDT Deposit Address:</b>")
        safe_next_step(msg, process_set_binance_usdt_address)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_change_db" and (user_id in admin_ids or user_id == OWNER_ID):
        msg = safe_send(chat_id, "🗄️ <b>DATABASE SWITCHER:</b>\nEnter database file name (e.g. <code>custom_data.db</code>):\n<i>The system will link to this DB immediately and reload all data.</i>")
        safe_next_step(msg, process_switch_database)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_bots_sms" and (user_id in admin_ids or user_id == OWNER_ID):
        msg = safe_send(chat_id, "📩 <b>BROADCAST TO HOSTED BOT OWNERS:</b>\nSend message text. It will be delivered only to users with at least 1 hosted bot:\n<i>Send /cancel to abort.</i>")
        safe_next_step(msg, process_all_bot_owners_sms)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_plans_mgr" and (user_id in admin_ids or user_id == OWNER_ID):
        plans = get_all_plans()
        text = "💎 <b>PLAN MANAGER CONSOLE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        for pid, pname, mbots, price, days, _ in plans:
            text += f"• <code>{pid}</code>: <b>{pname}</b> | ${price:.0f} | {days}d | {mbots} bots\n"
            markup.add(types.InlineKeyboardButton(f"🗑️ Delete: {pname}", callback_data=f"delplan_{pid}"))
        markup.add(types.InlineKeyboardButton("➕ Add New Plan", callback_data="add_plan_init"))
        markup.add(types.InlineKeyboardButton("⬅️ Back to Admin Console", callback_data="admin_console"))
        safe_edit(chat_id, call.message.message_id, text, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("delplan_"):
        pid = data.replace("delplan_", "")
        delete_plan_db(pid)
        bot.answer_callback_query(call.id, "Plan Deleted!")
        safe_send(chat_id, f"✅ <b>Plan <code>{pid}</code> removed from database.</b>")
        return

    if data == "add_plan_init":
        msg = safe_send(chat_id, "📝 <b>Send new plan details in format:</b>\n<code>plan_id | Plan Name | Max Bots | Price | Days | Description</code>\n\n<i>Example:</i>\n<code>mega | Mega Host | 15 | 40 | 30 | 15 Bot Slots with Dedicated Resources</code>")
        safe_next_step(msg, process_add_plan_step)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_all_bots":
        markup = types.InlineKeyboardMarkup(row_width=1)
        count = 0
        for uid, files in user_files.items():
            for fn, ft, st in files:
                running = (st == "approved" and is_bot_running(uid, fn))
                st_icon = "🟢" if running else "🔴"
                markup.add(types.InlineKeyboardButton(f"{st_icon} {fn} ({uid})", callback_data=f"ctl_{uid}_{fn}"))
                count += 1
        markup.add(types.InlineKeyboardButton("⬅️ Back to Admin Console", callback_data="admin_console"))
        safe_send(chat_id, f"🤖 <b>GLOBAL INSTANCES MONITOR ({count} Bots):</b>", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "adm_pending_files":
        if user_id != OWNER_ID and user_id not in admin_ids: return
        bot.answer_callback_query(call.id)
        pending_items = [(uid, fn) for uid, files in user_files.items() for fn, ft, st in files if st == "pending"]
        if not pending_items:
            safe_send(chat_id, "✅ <b>No files awaiting approval.</b>")
            return
        for p_uid, p_fn in pending_items:
            markup = types.InlineKeyboardMarkup(row_width=2)
            f_id = f"{p_uid}_{p_fn}"
            pending_approvals[f_id] = {"user_id": p_uid, "file_name": p_fn, "file_path": os.path.join(get_user_folder(p_uid), p_fn), "file_type": "py"}
            markup.add(
                types.InlineKeyboardButton("▶️ Approve & Run", callback_data=f"apprv_{f_id}"),
                types.InlineKeyboardButton("🗑️ Reject & Purge", callback_data=f"rjct_{f_id}")
            )
            safe_send(chat_id, f"🔔 <b>Pending File:</b> <code>{p_fn}</code>\n👤 <b>Owner:</b> <code>{p_uid}</code>", reply_markup=markup)
        return

    if data == "adm_scan_user":
        msg = safe_send(chat_id, "🔍 <b>Enter User ID to inspect profile & adjust balance:</b>")
        safe_next_step(msg, process_scan_user_input)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("adm_bal_"):
        parts = data.split("_")
        mode, target_uid = parts[2], int(parts[3])
        sign = "+" if mode == "add" else "-"
        msg = safe_send(chat_id, f"💰 <b>Enter amount to {mode} for User <code>{target_uid}</code>:</b>\n<i>Example: send 10.0 to {sign}10.0 USD</i>")
        safe_next_step(msg, lambda m: process_balance_adjustment_step(m, target_uid, mode))
        bot.answer_callback_query(call.id)
        return

    if data.startswith("adm_ban_toggle_"):
        target_uid = int(data.split("_")[3])
        user = get_user_data(target_uid)
        if not user: return bot.answer_callback_query(call.id, "User not found.")
        cur_ban = user[6]
        new_ban = 0 if cur_ban == 1 else 1
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (new_ban, target_uid))
            conn.commit()
            conn.close()
        action_text = "Unbanned" if new_ban == 0 else "Banned"
        bot.answer_callback_query(call.id, f"User {action_text}!")
        safe_send(chat_id, f"✅ <b>User <code>{target_uid}</code> is now {action_text}.</b>")
        return

    if data == "adm_broadcast":
        msg = safe_send(chat_id, "📢 <b>Send announcement text to broadcast to ALL network users:</b>\n<i>Send /cancel to abort.</i>")
        safe_next_step(msg, process_broadcast_transmission)
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
        safe_send(chat_id, f"✅ <b>Rebooted {count} approved worker instances.</b>")
        bot.answer_callback_query(call.id)
        return

    if data == "adm_stop_all":
        stopped = len(bot_scripts)
        for skey in list(bot_scripts.keys()):
            kill_process_tree(bot_scripts[skey])
            bot_scripts.pop(skey, None)
        safe_send(chat_id, f"⏹️ <b>Terminated {stopped} active running processes.</b>")
        bot.answer_callback_query(call.id)
        return

    if data == "adm_lock_system":
        bot_locked = not bot_locked
        safe_send(chat_id, f"⚡ <b>Emergency Lockdown State:</b> <code>{bot_locked}</code>")
        bot.answer_callback_query(call.id, "Lock State Toggled!")
        return

    if data == "admin_console":
        safe_send(chat_id, "👑 <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
        bot.answer_callback_query(call.id)
        return

    if data == "adm_close":
        try: bot.delete_message(chat_id, call.message.message_id)
        except Exception: pass
        bot.answer_callback_query(call.id)
        return

# ─── ADMIN STEP HANDLERS (ESCAPE-PROTECTED) ────────────────────────────────
def process_set_binance_pay_id(message):
    new_id = message.text.strip()
    if new_id:
        set_setting("binance_pay_id", new_id)
        safe_send(message.chat.id, f"✅ <b>Binance Pay ID updated to:</b> <code>{new_id}</code>")
    else:
        safe_send(message.chat.id, "❌ <b>Invalid Pay ID provided.</b>")

def process_set_binance_usdt_address(message):
    new_addr = message.text.strip()
    if new_addr:
        set_setting("binance_usdt_address", new_addr)
        safe_send(message.chat.id, f"✅ <b>Binance USDT Address updated to:</b>\n<code>{new_addr}</code>")
    else:
        safe_send(message.chat.id, "❌ <b>Invalid USDT address provided.</b>")

def process_switch_database(message):
    global DATABASE_PATH
    db_name = message.text.strip()
    if not db_name.endswith(".db"):
        db_name += ".db"

    new_path = os.path.join(DATABASE_DIR, db_name)
    try:
        DATABASE_PATH = new_path
        init_db()
        load_data()
        safe_send(message.chat.id, f"✅ <b>Database Switched Successfully!</b>\nActive DB: <code>{db_name}</code>\nTables initialized & cached data reloaded.")
    except Exception as e:
        safe_send(message.chat.id, f"❌ <b>Database Connection Error:</b> {e}")

def process_all_bot_owners_sms(message):
    text = message.text or ""
    if text == "/cancel":
        return safe_send(message.chat.id, "❌ <b>Bot Owners SMS Cancelled.</b>")

    target_user_ids = [uid for uid, files in user_files.items() if len(files) > 0]
    if not target_user_ids:
        return safe_send(message.chat.id, "🔔 <b>No active bot owners found to message.</b>")

    status_m = safe_send(message.chat.id, f"⏳ <i>Delivering SMS to {len(target_user_ids)} bot owners...</i>")
    sent, failed = 0, 0
    for uid in target_user_ids:
        try:
            safe_send(uid, f"📩 <b>IMPORTANT HOSTING NOTICE:</b>\n\n{text}")
            sent += 1
            time.sleep(0.04)
        except Exception:
            failed += 1

    safe_edit(message.chat.id, status_m.message_id, f"✅ <b>Hosted Bot SMS Finished!</b>\nDelivered: <code>{sent}</code> | Failed: <code>{failed}</code>.")

def process_deposit_approval_amount(message, dep_id, target_uid):
    try:
        amount = float(message.text.strip())
        new_bal = update_user_balance(target_uid, amount)

        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("UPDATE deposits SET status = 'approved', amount = ? WHERE deposit_id = ?", (amount, dep_id))
            c.execute("SELECT referred_by FROM users WHERE user_id = ?", (target_uid,))
            ref_row = c.fetchone()
            conn.commit()
            conn.close()

        if ref_row and ref_row[0]:
            comm = amount * REFERRAL_DEPOSIT_COMMISSION
            update_user_balance(ref_row[0], comm)
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute("UPDATE users SET referral_earnings = referral_earnings + ? WHERE user_id = ?", (comm, ref_row[0]))
                conn.commit()
                conn.close()
            safe_send(ref_row[0], f"🎁 <b>Referral Commission Earned!</b>\nYour referral deposited <code>${amount:.2f}</code>. You received <code>${comm:.2f} USD</code> commission!")

        safe_send(message.chat.id, f"✅ <b>Deposit #{dep_id} Approved! User <code>{target_uid}</code> credited with <code>${amount:.2f}</code> (New Balance: <code>${new_bal:.2f}</code>).</b>")
        safe_send(target_uid, f"✅ <b>Deposit Confirmed!</b> <code>${amount:.2f} USD</code> has been credited to your Cloud Wallet. Available: <code>${new_bal:.2f}</code>.")
    except Exception as e:
        safe_send(message.chat.id, f"❌ <b>Invalid Amount:</b> {e}")

def process_add_plan_step(message):
    try:
        parts = [p.strip() for p in message.text.split("|")]
        pid, name, max_bots, price, days, desc = parts[0], parts[1], int(parts[2]), float(parts[3]), int(parts[4]), parts[5]
        save_or_update_plan(pid, name, max_bots, price, days, desc)
        safe_send(message.chat.id, f"✅ <b>Plan <code>{name}</code> ({pid}) successfully created!</b>")
    except Exception as e:
        safe_send(message.chat.id, f"❌ <b>Invalid format:</b> {e}")

def process_scan_user_input(message):
    try:
        uid = int(message.text.strip())
        u = get_user_data(uid)
        if not u:
            return safe_send(message.chat.id, "❌ <b>User not found in database.</b>")

        status_str = "BANNED" if u[6] == 1 else "ACTIVE"
        text = (
            f"👤 <b>USER PROFILE DOSSIER:</b> <code>{uid}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✈️ <b>Username:</b> @{u[1] or 'N/A'}\n"
            f"💰 <b>Balance:</b> <code>${u[3]:.2f} USD</code>\n"
            f"💎 <b>Plan:</b> <code>{u[4] or 'Free Tier'}</code>\n"
            f"📅 <b>Expiry:</b> <code>{u[5] or 'N/A'}</code>\n"
            f"🛡️ <b>Status:</b> <code>{status_str}</code>\n"
            f"⚡ <b>Hosted Bots:</b> <code>{len(user_files.get(uid, []))}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Choose an action below to manage user:</i>"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ Add Balance", callback_data=f"adm_bal_add_{uid}"),
            types.InlineKeyboardButton("➖ Deduct Balance", callback_data=f"adm_bal_sub_{uid}")
        )
        ban_lbl = "✅ Unban User" if u[6] == 1 else "🚫 Ban User"
        markup.add(
            types.InlineKeyboardButton(ban_lbl, callback_data=f"adm_ban_toggle_{uid}"),
            types.InlineKeyboardButton("⬅️ Back to Admin Console", callback_data="admin_console")
        )
        safe_send(message.chat.id, text, reply_markup=markup)
    except Exception:
        safe_send(message.chat.id, "❌ <b>Please provide a numerical User ID.</b>")

def process_balance_adjustment_step(message, target_uid, mode):
    try:
        amount = float(message.text.strip())
        delta = amount if mode == "add" else -amount
        new_bal = update_user_balance(target_uid, delta)
        safe_send(message.chat.id, f"✅ <b>Balance Updated! User <code>{target_uid}</code> now has <code>${new_bal:.2f} USD</code>.</b>")
        safe_send(target_uid, f"🔔 <b>Wallet Adjustment Notice:</b>\nAn administrator modified your balance by <code>{delta:+.2f} USD</code>. Current Balance: <code>${new_bal:.2f}</code>.")
    except Exception as e:
        safe_send(message.chat.id, f"❌ <b>Error:</b> {e}")

def process_broadcast_transmission(message):
    text = message.text or ""
    if text == "/cancel": return safe_send(message.chat.id, "❌ <b>Broadcast Cancelled.</b>")
    status_m = safe_send(message.chat.id, "⏳ <i>Transmitting announcement to network...</i>")
    sent, failed = 0, 0
    for uid in list(active_users):
        try:
            safe_send(uid, f"📢 <b>NETWORK BROADCAST:</b>\n\n{text}")
            sent += 1
            time.sleep(0.04)
        except Exception: failed += 1
    safe_edit(message.chat.id, status_m.message_id, f"✅ <b>Broadcast Finished! Delivered: <code>{sent}</code> | Failed: <code>{failed}</code>.</b>")

# ─── USER BUTTON ACTIONS ───────────────────────────────────────────────────
def _logic_upload_file(message):
    user_id = message.from_user.id
    limit = get_user_file_limit(user_id)
    if get_user_file_count(user_id) >= limit:
        return safe_send(message.chat.id, f"❌ <b>Container Quota Full ({get_user_file_count(user_id)}/{limit})!</b> Upgrade your tier to deploy more bots.")
    safe_send(message.chat.id, "📤 <b>Send your .py, .js, or .zip project file document now.</b>\n<i>Our pre-flight engine will inspect and stage your container for admin approval.</i>")

def _logic_speed(message):
    start = time.time()
    try: bot.get_me()
    except Exception: pass
    lat = round((time.time() - start) * 1000, 2)
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    safe_send(message.chat.id, f"⚡ <b>INFRASTRUCTURE BENCHMARK:</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ Latency: <code>{lat} ms</code>\n💥 CPU: <code>{cpu}%</code>\n💎 RAM: <code>{ram}%</code>\n⚡ Status: <code>100% Operational & Isolated</code>")

def _prompt_manual_install(message):
    msg = safe_send(message.chat.id, "⚡ <b>Manual Package Installation:</b>\nSend library name to install:\n• Python: <code>requests</code>, <code>telebot</code>\n• Node.js: <code>npm:express</code>")
    safe_next_step(msg, _execute_manual_install)

def _execute_manual_install(message):
    pkg = message.text.strip()
    status_m = safe_send(message.chat.id, f"⏳ <i>Installing {pkg}...</i>")
    ok, text = install_system_package(pkg)
    safe_edit(message.chat.id, status_m.message_id, f"{'✅' if ok else '❌'} {text}")

# ─── UNIVERSAL REPLY KEYBOARD MESSAGE HANDLER ──────────────────────────────
@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_universal_text(message):
    if bot_locked and message.from_user.id not in admin_ids:
        return safe_send(message.chat.id, "🔔 <b>System Locked for Maintenance.</b>")

    handler = match_reply_button(message.text)
    if handler:
        handler(message)
    elif message.text.startswith("/"):
        if message.text == "/start":
            command_start(message)
        elif message.text == "/admin" and (message.from_user.id in admin_ids or message.from_user.id == OWNER_ID):
            safe_send(message.chat.id, "👑 <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())

# ─── BACKGROUND CRON LOOP (AUTO EXPIRY CHECK) ──────────────────────────────
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

                        for skey in list(bot_scripts.keys()):
                            if skey.startswith(f"{uid}_"):
                                kill_process_tree(bot_scripts[skey])
                                bot_scripts.pop(skey, None)

                        safe_send(uid, f"🔔 <b>Subscription Plan {pname} Expired!</b>\nYour running bots have been stopped. Renew to restore full container slots.")
                except Exception: pass
        except Exception: pass
        time.sleep(3600)

# ─── CRASH-PROOF TELEGRAM POLLING ENGINE ────────────────────────────────────
def run_polling():
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception: pass

    while True:
        try:
            print("[+] Infinity Polling Started (Zero Crash Active)...")
            bot.infinity_polling(timeout=30, long_polling_timeout=20, skip_pending=True)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"[!] Telegram API error: {e}")
            if "Conflict" in str(e):
                print("[!] 409 Conflict: Waiting 12 seconds for old instance to close...")
                time.sleep(12)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"[!] Polling recovery loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("=" * 60)
    print(f" NEBULA HOST CLOUD - PRODUCTION READY ")
    print(f" Super Admin ID: {OWNER_ID}")
    print(f" Support: {YOUR_USERNAME}")
    print(" Payment: Only Binance Pay & USDT (Admin Toggleable)")
    print(" Deploy Resilience: 409 Conflict & Port Healthcheck Safe")
    print("=" * 60)

    atexit.register(lambda: [kill_process_tree(p) for p in bot_scripts.values()])
    threading.Thread(target=expiry_cron_loop, daemon=True).start()

    t_flask = Thread(target=run_flask_server)
    t_flask.daemon = True
    t_flask.start()

    run_polling()
