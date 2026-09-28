# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║         NEBULA CLOUD HOSTING BOT — FULL ADVANCED MERGED EDITION           ║
║                                                                           ║
║  • Target Admin ID: 2014144404                                            ║
║  • Support: @YourDomains                                                  ║
║  • Token: 8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU                 ║
║  • Strict Manual .txt Requirements Validation (No Automatic Guessing)     ║
║  • Admin Actions: Full Bot Backup (.zip) & Permanent Purge with Notice    ║
║  • Individual Payment Gateway Toggles: Binance, bKash & Nagad (ON/OFF)    ║
║  • Zero Button Freeze: Instant Callback ACK + Re-entrant RLock            ║
║  • Full Multi-Process Hosting, Auto-Recovery & 24/7 Keep-Alive Web Server ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import atexit
from datetime import datetime, timedelta
import hashlib
import hmac
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
import requests
import telebot
from telebot import types

# ── KEEP-ALIVE SERVER (FOR 24/7 HOSTING ON RENDER / KOYEB / VPS) ───────────
app = Flask(__name__)

@app.route("/")
def home():
    return "Nebula Cloud Hosting System is Live & Healthy", 200

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[!] Web server binding notice: {e}")

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("[+] Background Keep-Alive Server Online.")

# ── CONFIGURATION & CREDENTIALS ─────────────────────────────────────────────
TOKEN = "8675366388:AAGmd_idkGdVv8aoyRmCE2VbOjvRrTm_7uM"
OWNER_ID = 2014144404
ADMIN_ID = 2014144404
YOUR_USERNAME = "@YourDomains"
SUPPORT_CONTACT_ID = 2014144404
UPDATE_CHANNEL = "https://t.me/BABY_CODER_1"

# Binance Pay Integration Config
BINANCE_API_KEY = "e0e4WavqDOqdmKRZHoNPcNt8TsYAUf17FdpVSasXm54QGVGs8JBp9ySkFTTPbcej"
BINANCE_SECRET_KEY = "NFmtwRqLVvcymwNgSc6NwmmyZC2bHb2DFqLwDdItlwhBdFOERa5UYhwXXMtm7r7A"
BINANCE_PAY_ID = "248391029"
BINANCE_USDT_ADDRESS = "TQn9Y2KhPzW9H1L8o9qJ2Q5k4h3g2f1TRX"

# Default Gateway Numbers & Rates
DEFAULT_BKASH_NUMBER = "017XXXXXXXX"
DEFAULT_NAGAD_NUMBER = "018XXXXXXXX"
USDT_BDT_RATE = 122.0

# Referral Settings
REFERRAL_JOIN_BONUS = 0.50  # USD
REFERRAL_DEPOSIT_COMMISSION = 0.10  # 10%

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

# ── TELEGRAM CUSTOM EMOJIS MAPPING ─────────────────────────────────────────
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
    "bkash": ("6237975191784266396", "🌸"),
    "nagad": ("6235336389647407554", "🔶"),
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
    """Compliant custom Telegram emoji tag wrapping valid unicode character."""
    emoji_id, fallback = EMOJIS_DATA.get(key, ("6314480331831385997", "✨"))
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

def cbtn(text, callback_data=None, url=None, style=None, icon=None):
    return types.InlineKeyboardButton(text, callback_data=callback_data, url=url)

def rkbtn(text):
    return types.KeyboardButton(text)

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
    except telebot.apihelper.ApiTelegramException:
        clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
        try:
            return bot.send_message(chat_id, clean_text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            return bot.send_message(chat_id, re.sub(r'<[^>]*>', '', text), reply_markup=reply_markup)
    except Exception:
        return None

def safe_reply(message, text, reply_markup=None):
    try:
        return bot.reply_to(message, text, reply_markup=reply_markup, parse_mode="HTML")
    except telebot.apihelper.ApiTelegramException:
        clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
        try:
            return bot.reply_to(message, clean_text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            return bot.reply_to(message, re.sub(r'<[^>]*>', '', text), reply_markup=reply_markup)
    except Exception:
        return None

def safe_edit(chat_id, message_id, text, reply_markup=None):
    try:
        return bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
    except telebot.apihelper.ApiTelegramException:
        clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
        try:
            return bot.edit_message_text(clean_text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            return bot.edit_message_text(re.sub(r'<[^>]*>', '', text), chat_id, message_id, reply_markup=reply_markup)
    except Exception:
        return None

# --- Re-entrant Thread Lock to Eliminate Deadlocks ---
DB_LOCK = threading.RLock()

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
        c.execute("""CREATE TABLE IF NOT EXISTS manual_payment_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id TEXT NOT NULL,
            method TEXT NOT NULL,
            amount TEXT NOT NULL,
            tx_id TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS used_txids (tx_id TEXT PRIMARY KEY)""")
        c.execute("""CREATE TABLE IF NOT EXISTS pending_payments (user_id INTEGER, plan_id TEXT, paid_amount REAL, PRIMARY KEY (user_id, plan_id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT)""")

        # Default Settings
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('update_channel', ?)", (UPDATE_CHANNEL,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_pay_id', ?)", (BINANCE_PAY_ID,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_usdt_address', ?)", (BINANCE_USDT_ADDRESS,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('bkash_number', ?)", (DEFAULT_BKASH_NUMBER,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('nagad_number', ?)", (DEFAULT_NAGAD_NUMBER,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('binance_enabled', '1')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('bkash_enabled', '1')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('nagad_enabled', '1')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('free_user_limit', ?)", (str(FREE_USER_LIMIT),))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('bot_off_message', 'System maintenance in progress.')")
        c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))

        # Default Plans
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

def get_plan_by_id(plan_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT plan_id, name, max_bots, price, days, description FROM plans WHERE plan_id = ?", (plan_id,))
        row = c.fetchone()
        conn.close()
        return row

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

# ─── MANUAL PAYMENT HELPERS ────────────────────────────────────────────────
def is_txid_used(tx_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT tx_id FROM used_txids WHERE tx_id = ?", (str(tx_id).strip(),))
        row = c.fetchone()
        conn.close()
        return row is not None

def add_used_txid(tx_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO used_txids VALUES (?)", (str(tx_id).strip(),))
        conn.commit()
        conn.close()

def create_manual_payment_request(user_id, plan_id, method, amount, tx_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT request_id FROM manual_payment_requests WHERE tx_id = ?", (tx_id.strip(),))
        if c.fetchone():
            conn.close()
            return False, "duplicate"
        c.execute("INSERT INTO manual_payment_requests (user_id, plan_id, method, amount, tx_id, status, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?)",
                  (user_id, plan_id, method, str(amount), tx_id.strip(), datetime.now().isoformat()))
        req_id = c.lastrowid
        conn.commit()
        conn.close()
        return req_id, "created"

def get_pending_manual_payments():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT request_id, user_id, plan_id, method, amount, tx_id, created_at FROM manual_payment_requests WHERE status = 'pending' ORDER BY request_id DESC")
        rows = c.fetchall()
        conn.close()
        return rows

def get_manual_payment_request(request_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT request_id, user_id, plan_id, method, amount, tx_id, status FROM manual_payment_requests WHERE request_id = ?", (request_id,))
        row = c.fetchone()
        conn.close()
        return row

def set_manual_payment_status(request_id, status):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("UPDATE manual_payment_requests SET status = ? WHERE request_id = ? AND status = 'pending'", (status, request_id))
        changed = c.rowcount
        conn.commit()
        conn.close()
        return changed == 1

# ─── RELIABLE PACKAGE INSTALLER ────────────────────────────────────────────
def install_requirements_file(req_file_path):
    """Installs dependencies strictly from the provided requirements.txt file."""
    cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", req_file_path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        if res.returncode == 0:
            return True, "All dependencies installed successfully."
        else:
            # Fallback with --user
            fallback_cmd = [sys.executable, "-m", "pip", "install", "--user", "-r", req_file_path]
            res_fb = subprocess.run(fallback_cmd, capture_output=True, text=True, timeout=240)
            if res_fb.returncode == 0:
                return True, "All dependencies installed successfully."
            err = res.stderr or res.stdout or "Error installing requirements."
            return False, f"Install Error: <code>{html.escape(err[-300:])}</code>"
    except Exception as e:
        return False, f"Install Failure: <code>{str(e)}</code>"

def install_system_package(pkg_input):
    if pkg_input.lower().startswith("npm:"):
        pkg_name = pkg_input[4:].strip()
        cmd = ["npm", "install", "-g", pkg_name]
    else:
        pkg_name = pkg_input.strip()
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

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply=None):
    script_key = f"{script_owner_id}_{file_name}"
    log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")

    if script_key in bot_scripts:
        kill_process_tree(bot_scripts[script_key])
        bot_scripts.pop(script_key, None)

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
                safe_send(script_owner_id, f"{CE('notice')} <b>Execution Stopped on Launch:</b>\n<pre>{html.escape(tail)}</pre>")
            return False

        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "script_owner_id": script_owner_id,
            "user_folder": user_folder,
            "type": "py"
        }

        safe_send(script_owner_id, f"{CE('done')} <b>Container Online:</b> <code>{file_name}</code> (PID: <code>{process.pid}</code>)")
        return True
    except Exception as e:
        safe_send(script_owner_id, f"{CE('close')} <b>Process Failure:</b> <code>{str(e)}</code>")
        return False

def execute_permanent_bot_delete(owner_id, fname, executed_by_admin=False):
    skey = f"{owner_id}_{fname}"
    if skey in bot_scripts:
        kill_process_tree(bot_scripts[skey])
        bot_scripts.pop(skey, None)

    remove_user_file_db(owner_id, fname)
    user_folder = get_user_folder(owner_id)
    main_file = os.path.join(user_folder, fname)
    log_file = os.path.join(user_folder, f"{os.path.splitext(fname)[0]}.log")
    req_file = os.path.join(user_folder, "requirements.txt")

    try:
        if os.path.exists(main_file): os.remove(main_file)
    except Exception: pass

    try:
        if os.path.exists(log_file): os.remove(log_file)
    except Exception: pass

    try:
        if os.path.exists(req_file): os.remove(req_file)
    except Exception: pass

    if executed_by_admin and int(owner_id) != OWNER_ID:
        safe_send(
            owner_id,
            f"{CE('delete')} <b>Administrative Notice:</b>\n"
            f"Your bot container <code>{fname}</code> was <b>permanently deleted</b> by the administrator. "
            f"This bot can no longer be hosted or executed."
        )

# ─── MENUS & KEYBOARDS ─────────────────────────────────────────────────────
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
        cbtn("💎 Manage Plans", callback_data="adm_plans_mgr"),
        cbtn("🤖 All Deployed Bots", callback_data="adm_all_bots"),
    )
    markup.add(
        cbtn("🔍 Scan User & Balance", callback_data="adm_scan_user"),
        cbtn("⏳ Pending Approvals", callback_data="adm_pending_files"),
    )
    markup.add(
        cbtn("📢 Broadcast Notice", callback_data="adm_broadcast"),
        cbtn("📩 SMS All Bot Owners", callback_data="adm_bots_sms"),
    )
    markup.add(
        cbtn("💳 Payment Gateways (ON/OFF)", callback_data="adm_gateways_mgr"),
        cbtn("🗄️ Switch Database", callback_data="adm_change_db"),
    )
    markup.add(
        cbtn("💰 Pending Payments", callback_data="pending_manual_payments"),
        cbtn("▶️ Reboot All Workers", callback_data="adm_reboot_all"),
    )
    markup.add(
        cbtn("⏹️ Stop All Workers", callback_data="adm_stop_all"),
        cbtn("🔒 Lock System", callback_data="adm_lock_system"),
    )
    markup.add(
        cbtn("❌ Close Console", callback_data="adm_close"),
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
    "Help Desk": lambda m: safe_send(m.chat.id, f"{CE('support')} <b>Dedicated Consultant:</b> {YOUR_USERNAME}\n24/7 Priority Support Desk."),
    "Manual Install": lambda m: _prompt_manual_install(m),
    "Updates Channel": lambda m: safe_send(m.chat.id, f"{CE('link')} <b>Official Channel:</b> {UPDATE_CHANNEL}"),
    "Admin Console": lambda m: safe_send(m.chat.id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
}

def match_reply_button(text):
    t_clean = re.sub(r'[^\w\s]', '', text or '').strip().lower()
    for k in BUTTON_MAPPING:
        k_clean = re.sub(r'[^\w\s]', '', k).strip().lower()
        if k_clean in t_clean or t_clean in k_clean:
            return BUTTON_MAPPING[k]
    return None

def safe_next_step(msg, callback):
    """If user taps ANY menu button or sends /start, cancels pending state and executes button."""
    def wrapper(message):
        text = (message.text or "").strip()
        if text.startswith("/"):
            if text == "/start":
                command_start(message)
                return
            elif text == "/admin" and (message.from_user.id in admin_ids or message.from_user.id == OWNER_ID):
                safe_send(message.chat.id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
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
            safe_send(referrer_id, f"{CE('gift')} <b>New Referral Registered!</b>\nUser <code>{user_id}</code> joined via your link. You earned <code>${REFERRAL_JOIN_BONUS:.2f}</code> bonus!")

    user = get_user_data(user_id)
    if user and user[6] == 1:
        safe_send(chat_id, f"{CE('notice')} <b>Account Restricted from Accessing Network.</b>")
        return

    # Force Sub Verification
    if not (user_id == OWNER_ID or user_id in admin_ids):
        for ch in FORCE_SUB_CHANNELS:
            try:
                m = bot.get_chat_member(ch["chat_id"], user_id)
                if m.status in ["left", "kicked"]:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(cbtn("📢 Join Updates Channel", url=ch["url"]))
                    markup.add(cbtn("✅ Verify Membership", callback_data="verify_fsub"))
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

# ─── 2-STEP UPLOAD & MANUAL REQUIREMENTS.TXT INSPECTION ───────────────────
user_staged_uploads = {}

@bot.message_handler(content_types=["document"])
def handle_incoming_file(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document

    user = get_user_data(user_id)
    if user and user[6] == 1:
        return safe_send(chat_id, f"{CE('notice')} <b>Account Restricted.</b>")

    limit = get_user_file_limit(user_id)
    if get_user_file_count(user_id) >= limit:
        return safe_send(chat_id, f"{CE('close')} <b>Container Quota Full ({get_user_file_count(user_id)}/{limit})!</b> Upgrade your plan to deploy more bots.")

    filename = doc.file_name or "main.py"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".py", ".js", ".zip", ".txt"]:
        return safe_send(chat_id, f"{CE('close')} <b>Unsupported File! Send .py, .js, .zip, or requirements.txt.</b>")

    user_folder = get_user_folder(user_id)

    # If user uploads requirements.txt for staged script
    if (ext == ".txt" or filename.lower() == "requirements.txt") and user_id in user_staged_uploads:
        wait_m = safe_reply(message, f"{CE('loading')} <i>Checking and validating your requirements.txt...</i>")
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        req_path = os.path.join(user_folder, "requirements.txt")
        with open(req_path, "wb") as f:
            f.write(downloaded)

        # Inspect requirements
        with open(req_path, "r", encoding="utf-8", errors="ignore") as rf:
            req_lines = [line.strip() for line in rf.readlines() if line.strip() and not line.startswith("#")]

        if not req_lines:
            safe_edit(chat_id, wait_m.message_id, f"{CE('notice')} <b>Requirements file is empty!</b> Staging script without extra packages.")
        else:
            safe_edit(chat_id, wait_m.message_id, f"{CE('loading')} <i>Installing {len(req_lines)} dependencies via PIP package manager...</i>")
            ok, msg = install_requirements_file(req_path)
            if not ok:
                safe_send(chat_id, f"{CE('notice')} <b>Package Install Warning:</b>\n{msg}")

        staged_fname = user_staged_uploads.pop(user_id)
        forward_bot_to_admin(user_id, staged_fname, os.path.join(user_folder, staged_fname))
        safe_send(chat_id, f"{CE('done')} <b>Requirements verified! Script dispatched to Admin for launch approval.</b>")
        return

    wait_m = safe_reply(message, f"{CE('loading')} <i>Downloading & pre-flight staging file...</i>")
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
            f"{CE('up')} <b>STEP 2: SEND YOUR REQUIREMENTS.TXT NOW</b>\n\n"
            f"⚠️ <i>Auto-guessing is disabled. Please upload your <code>requirements.txt</code> file to install necessary dependencies.</i>\n\n"
            f"<i>If this bot uses only standard Python libraries with no external packages, tap below:</i>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(cbtn("⚡ Proceed Without Dependencies", callback_data=f"skip_req_{filename}"))
        markup.add(cbtn("❌ Cancel Deployment", callback_data="cancel_action"))
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
        cbtn("▶️ Approve & Run", callback_data=f"apprv_{file_id}"),
        cbtn("🗑️ Reject & Purge", callback_data=f"rjct_{file_id}")
    )

    caption = (
        f"{CE('notice')} <b>NEW HOSTING CONTAINER DISPATCHED (PENDING)</b>\n"
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
        safe_send(OWNER_ID, caption + f"\n\n<i>(Attachment relay fallback: {e})</i>", reply_markup=markup)

# ─── GATEWAYS MANAGER (INDIVIDUAL ON/OFF) ──────────────────────────────────
def show_gateways_manager(chat_id, message_id=None):
    bn_on = get_setting("binance_enabled", "1") == "1"
    bk_on = get_setting("bkash_enabled", "1") == "1"
    ng_on = get_setting("nagad_enabled", "1") == "1"

    text = (
        f"{CE('wallet')} <b>PAYMENT GATEWAYS CONTROLLER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• <b>Binance Gateway:</b> {'🟢 ENABLED' if bn_on else '🔴 DISABLED'}\n"
        f"• <b>bKash Gateway:</b> {'🟢 ENABLED' if bk_on else '🔴 DISABLED'}\n"
        f"• <b>Nagad Gateway:</b> {'🟢 ENABLED' if ng_on else '🔴 DISABLED'}\n\n"
        f"<i>Tap below to toggle any payment method individually ON or OFF:</i>"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        cbtn(f"Binance: {'🟢 ON' if bn_on else '🔴 OFF'} (Tap to Toggle)", callback_data="togg_gate_binance"),
        cbtn(f"bKash: {'🟢 ON' if bk_on else '🔴 OFF'} (Tap to Toggle)", callback_data="togg_gate_bkash"),
        cbtn(f"Nagad: {'🟢 ON' if ng_on else '🔴 OFF'} (Tap to Toggle)", callback_data="togg_gate_nagad"),
    )
    markup.add(
        cbtn("✏️ Set bKash Number", callback_data="change_manual_bkash"),
        cbtn("✏️ Set Nagad Number", callback_data="change_manual_nagad")
    )
    markup.add(
        cbtn("✏️ Set Binance Pay ID", callback_data="adm_set_pay_id"),
        cbtn("✏️ Set USDT Address", callback_data="adm_set_usdt_addr")
    )
    markup.add(cbtn("⬅️ Back to Admin Console", callback_data="admin_console"))

    if message_id:
        safe_edit(chat_id, message_id, text, reply_markup=markup)
    else:
        safe_send(chat_id, text, reply_markup=markup)

# ─── PLANS & PURCHASE ──────────────────────────────────────────────────────
def show_plans_menu(chat_id, user_id):
    plans = get_all_plans()
    text = f"{CE('diamond')} <b>CLOUD SUBSCRIPTION TIERS</b> {CE('fire')}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    bn_on = get_setting("binance_enabled", "1") == "1"
    bk_on = get_setting("bkash_enabled", "1") == "1"
    ng_on = get_setting("nagad_enabled", "1") == "1"

    markup = types.InlineKeyboardMarkup(row_width=1)
    for pid, pname, mbots, price, days, desc in plans:
        val = float(price)
        bdt_val = round(val * USDT_BDT_RATE, 2)
        text += (
            f"• <b>{pname}:</b> <code>${val:.2f} USD (~{bdt_val} BDT)</code>\n"
            f"  {CE('power')} Limit: <code>{mbots} Bots</code> | {CE('date')} Duration: <code>{days} Days</code>\n"
            f"  <i>{desc}</i>\n\n"
        )
        row_btns = []
        if bn_on:
            row_btns.append(cbtn(f"🟡 Binance", callback_data=f"buy_binance_{pid}"))
        if bk_on:
            row_btns.append(cbtn(f"🌸 bKash", callback_data=f"buy_manual_bkash_{pid}"))
        if ng_on:
            row_btns.append(cbtn(f"🔶 Nagad", callback_data=f"buy_manual_nagad_{pid}"))

        if row_btns:
            markup.row(*row_btns)
        else:
            markup.add(cbtn(f"Purchase {pname} (Contact Admin)", url=f"https://t.me/{YOUR_USERNAME.lstrip('@')}"))

    safe_send(chat_id, text, reply_markup=markup)

# ─── MY BOTS CONTROLLER ────────────────────────────────────────────────────
def show_user_bots(chat_id, user_id):
    flist = user_files.get(user_id, [])
    if not flist:
        return safe_send(chat_id, f"{CE('notice')} <b>You have no hosted instances deployed.</b>")

    markup = types.InlineKeyboardMarkup(row_width=1)
    for fn, ft, st in sorted(flist):
        if st == "pending":
            markup.add(cbtn(f"⏳ [PENDING APPROVAL] {fn}", callback_data=f"ctl_{user_id}_{fn}"))
        else:
            running = (st == "approved" and is_bot_running(user_id, fn))
            st_text = "🟢 ONLINE" if running else "🔴 STOPPED"
            markup.add(cbtn(f"[{st_text}] {fn}", callback_data=f"ctl_{user_id}_{fn}"))

    safe_send(chat_id, f"{CE('trader')} <b>DEPLOYED INSTANCES CONTROLLER:</b>", reply_markup=markup)

def show_bot_controls_card(chat_id, owner_id, fname, message_id=None):
    ftype, status = None, None
    for fn, ft, st in user_files.get(owner_id, []):
        if fn == fname:
            ftype, status = ft, st
            break

    if not ftype:
        return safe_send(chat_id, f"{CE('close')} <b>Instance record missing.</b>")

    if status == "pending":
        st_text = f"{CE('loading')} PENDING ADMIN APPROVAL"
    elif is_bot_running(owner_id, fname):
        st_text = f"{CE('done')} ONLINE & RUNNING"
    else:
        st_text = f"{CE('close')} STOPPED"

    card_text = (
        f"{CE('diamond')} <b>CONTAINER CONTROLLER #{fname}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('link')} <b>Runtime:</b> <code>{ftype.upper()}</code>\n"
        f"{CE('trader')} <b>Owner ID:</b> <code>{owner_id}</code>\n"
        f"{CE('speed')} <b>Status:</b> {st_text}"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    if status == "approved":
        if is_bot_running(owner_id, fname):
            markup.add(
                cbtn("⏹️ Stop Process", callback_data=f"bact_stop_{owner_id}_{fname}"),
                cbtn("🔄 Restart Process", callback_data=f"bact_restart_{owner_id}_{fname}")
            )
        else:
            markup.add(
                cbtn("▶️ Start Process", callback_data=f"bact_start_{owner_id}_{fname}"),
                cbtn("🗑️ Delete Container", callback_data=f"bact_del_{owner_id}_{fname}")
            )
    else:
        markup.add(cbtn("🗑️ Delete Container", callback_data=f"bact_del_{owner_id}_{fname}"))

    markup.add(
        cbtn("📜 Terminal Logs", callback_data=f"bact_logs_{owner_id}_{fname}"),
        cbtn("📥 Download Backup (.zip)", callback_data=f"bact_dl_{owner_id}_{fname}")
    )
    markup.add(cbtn("⬅️ Return to Bots List", callback_data="back_my_bots"))

    if message_id:
        safe_edit(chat_id, message_id, card_text, reply_markup=markup)
    else:
        safe_send(chat_id, card_text, reply_markup=markup)

# ════════════════════════════════════════════════════════════════════════════
# ALL-IN-ONE 100% UNFREEZING CALLBACK ROUTER
# ════════════════════════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    # ── INSTANT ACKNOWLEDGEMENT: Stops the loading spinner from freezing! ──
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    global bot_locked
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    try:
        # --- Force Subscribe ---
        if data == "verify_fsub":
            command_start(call.message)
            return

        # --- Cancel Action ---
        if data == "cancel_action":
            user_staged_uploads.pop(user_id, None)
            safe_edit(chat_id, call.message.message_id, f"{CE('close')} <b>Operation Cancelled.</b>")
            return

        # --- Skip Requirements in Upload ---
        if data.startswith("skip_req_"):
            fname = data.replace("skip_req_", "")
            user_staged_uploads.pop(user_id, None)
            fpath = os.path.join(get_user_folder(user_id), fname)
            forward_bot_to_admin(user_id, fname, fpath)
            safe_edit(chat_id, call.message.message_id, f"{CE('done')} <b>File dispatched to Admin for launch approval!</b>")
            return

        # --- Admin Approval Queue ---
        if data.startswith("apprv_"):
            if user_id != OWNER_ID and user_id not in admin_ids: return
            fid = data.replace("apprv_", "")
            info = pending_approvals.pop(fid, None)
            if not info:
                safe_send(chat_id, f"{CE('close')} <b>Request already processed or expired.</b>")
                return

            target_uid = info["user_id"]
            fname = info["file_name"]
            fpath = info["file_path"]

            save_user_file(target_uid, fname, info["file_type"], "approved")
            threading.Thread(target=run_script, args=(fpath, target_uid, get_user_folder(target_uid), fname, None)).start()
            safe_edit(chat_id, call.message.message_id, f"{CE('done')} <b>Worker <code>{fname}</code> Approved and Running!</b>")
            safe_send(target_uid, f"{CE('done')} <b>Your bot <code>{fname}</code> has been approved by admin and is now ONLINE!</b>")
            return

        if data.startswith("rjct_"):
            if user_id != OWNER_ID and user_id not in admin_ids: return
            fid = data.replace("rjct_", "")
            info = pending_approvals.pop(fid, None)
            if info:
                execute_permanent_bot_delete(info["user_id"], info["file_name"])
                safe_send(info["user_id"], f"{CE('close')} <b>Your deployment request for <code>{info['file_name']}</code> was rejected.</b>")
            safe_edit(chat_id, call.message.message_id, f"{CE('close')} <b>Container Rejected & Purged.</b>")
            return

        # --- Gateway Toggles (Individual ON/OFF) ---
        if data == "adm_gateways_mgr" and (user_id in admin_ids or user_id == OWNER_ID):
            show_gateways_manager(chat_id, call.message.message_id)
            return

        if data == "togg_gate_binance" and (user_id in admin_ids or user_id == OWNER_ID):
            cur = get_setting("binance_enabled", "1") == "1"
            set_setting("binance_enabled", "0" if cur else "1")
            show_gateways_manager(chat_id, call.message.message_id)
            return

        if data == "togg_gate_bkash" and (user_id in admin_ids or user_id == OWNER_ID):
            cur = get_setting("bkash_enabled", "1") == "1"
            set_setting("bkash_enabled", "0" if cur else "1")
            show_gateways_manager(chat_id, call.message.message_id)
            return

        if data == "togg_gate_nagad" and (user_id in admin_ids or user_id == OWNER_ID):
            cur = get_setting("nagad_enabled", "1") == "1"
            set_setting("nagad_enabled", "0" if cur else "1")
            show_gateways_manager(chat_id, call.message.message_id)
            return

        if data == "change_manual_bkash" and user_id in admin_ids:
            msg = safe_send(chat_id, f"{CE('sms')} <b>Send new bKash Number (e.g. 017XXXXXXXX):</b>")
            safe_next_step(msg, lambda m: process_payment_number_change(m, "bkash"))
            return

        if data == "change_manual_nagad" and user_id in admin_ids:
            msg = safe_send(chat_id, f"{CE('sms')} <b>Send new Nagad Number (e.g. 018XXXXXXXX):</b>")
            safe_next_step(msg, lambda m: process_payment_number_change(m, "nagad"))
            return

        if data == "adm_set_pay_id" and user_id in admin_ids:
            msg = safe_send(chat_id, f"{CE('binance')} <b>Enter new Binance Pay ID:</b>")
            safe_next_step(msg, process_set_binance_pay_id)
            return

        if data == "adm_set_usdt_addr" and user_id in admin_ids:
            msg = safe_send(chat_id, f"{CE('wallet')} <b>Enter new Binance USDT Deposit Address:</b>")
            safe_next_step(msg, process_set_binance_usdt_address)
            return

        # --- User Payment Handlers (bKash/Nagad) ---
        if data.startswith("buy_manual_bkash_") or data.startswith("buy_manual_nagad_"):
            parts = data.split("_")
            method = "bkash" if parts[2] == "bkash" else "nagad"
            if get_setting(f"{method}_enabled", "1") != "1":
                safe_send(chat_id, f"{CE('close')} <b>{method.title()} is currently disabled by administration.</b>")
                return

            plan_id = parts[3]
            plan = get_plan_by_id(plan_id)
            if not plan: return
            _, name, limit, price, duration, _ = plan
            bdt_val = round(float(price) * USDT_BDT_RATE, 2)
            number = get_setting(f"{method}_number", DEFAULT_BKASH_NUMBER if method == "bkash" else DEFAULT_NAGAD_NUMBER)

            pay_msg = (
                f"{CE(method)} <b>{method.title()} Payment Gateway</b>\n\n"
                f"{CE('crown')} <b>Plan:</b> <code>{name}</code>\n"
                f"{CE('money')} <b>Amount:</b> <code>{bdt_val} BDT (${price:.2f} USD)</code>\n"
                f"{CE('date')} <b>Duration:</b> <code>{duration} Days</code>\n\n"
                f"1️⃣ Send <code>{bdt_val} BDT</code> via Personal Send Money:\n"
                f"📱 <b>Number:</b> <code>{number}</code> (Tap to Copy)\n\n"
                f"2️⃣ Tap below to submit your Transaction ID:"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(cbtn("Submit Transaction ID", callback_data=f"submit_manual_{method}_{plan_id}"))
            safe_send(chat_id, pay_msg, reply_markup=markup)
            return

        if data.startswith("submit_manual_"):
            parts = data.split("_")
            method, plan_id = parts[2], parts[3]
            msg = safe_send(chat_id, f"{CE('sms')} <b>Send your {method.title()} Transaction ID (TrxID):</b>")
            safe_next_step(msg, lambda m: process_manual_txid(m, plan_id, method))
            return

        # --- Admin Approval for Manual Payments ---
        if data == "pending_manual_payments" and user_id in admin_ids:
            rows = get_pending_manual_payments()
            if not rows:
                safe_send(chat_id, f"{CE('done')} <b>No pending manual payments.</b>")
                return
            for req_id, uid, pid, method, amount, txid, created in rows:
                plan = get_plan_by_id(pid)
                pname = plan[1] if plan else "Plan"
                text = (
                    f"{CE('money')} <b>Manual Payment Request #{req_id}</b>\n\n"
                    f"{CE('trader')} <b>User:</b> <code>{uid}</code>\n"
                    f"{CE('crown')} <b>Plan:</b> <code>{pname}</code>\n"
                    f"{CE('wallet')} <b>Method:</b> <code>{method.title()}</code>\n"
                    f"{CE('balance')} <b>Amount:</b> <code>{amount}</code>\n"
                    f"{CE('sms')} <b>TrxID:</b> <code>{txid}</code>"
                )
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    cbtn("Approve", callback_data=f"app_man_{req_id}"),
                    cbtn("Reject", callback_data=f"rej_man_{req_id}")
                )
                safe_send(chat_id, text, reply_markup=markup)
            return

        if data.startswith("app_man_") and user_id in admin_ids:
            req_id = int(data.replace("app_man_", ""))
            req = get_manual_payment_request(req_id)
            if not req or req[6] != "pending": return
            _, uid, pid, method, amount, txid, status = req
            plan = get_plan_by_id(pid)
            if not plan: return
            if not set_manual_payment_status(req_id, "approved"): return

            name, duration = plan[1], plan[4]
            expiry = datetime.now() + timedelta(days=duration)
            save_subscription(uid, name, expiry)
            add_used_txid(txid)
            safe_send(chat_id, f"{CE('done')} <b>Payment #{req_id} approved for user <code>{uid}</code>.</b>")
            safe_send(uid, f"{CE('sparkle')} <b>Payment Verified!</b>\nYour plan <code>{name}</code> is active for {duration} days.")
            return

        if data.startswith("rej_man_") and user_id in admin_ids:
            req_id = int(data.replace("rej_man_", ""))
            if set_manual_payment_status(req_id, "rejected"):
                safe_send(chat_id, f"{CE('close')} <b>Payment #{req_id} rejected.</b>")
            return

        # --- User Binance Pay Flow ---
        if data.startswith("buy_binance_"):
            if get_setting("binance_enabled", "1") != "1":
                safe_send(chat_id, f"{CE('close')} <b>Binance Pay is currently disabled. Please choose another method.</b>")
                return
            plan_id = data.replace("buy_binance_", "")
            plan = get_plan_by_id(plan_id)
            if not plan: return
            _, name, limit, price, duration, _ = plan

            pay_id = get_setting("binance_pay_id", BINANCE_PAY_ID)
            usdt_addr = get_setting("binance_usdt_address", BINANCE_USDT_ADDRESS)

            pay_msg = (
                f"{CE('binance')} <b>Binance Pay Auto Verification</b>\n\n"
                f"{CE('crown')} <b>Plan:</b> <code>{name}</code>\n"
                f"{CE('money')} <b>Total Due:</b> <code>${price:.2f} USDT</code>\n"
                f"{CE('date')} <b>Duration:</b> <code>{duration} Days</code>\n\n"
                f"1️⃣ Open Binance App ➔ Pay ➔ Send\n"
                f"🔸 <b>Binance Pay ID:</b> <code>{pay_id}</code> (Tap to Copy)\n"
                f"🔸 <b>Or USDT (TRC20/BEP20):</b> <code>{usdt_addr}</code>\n\n"
                f"2️⃣ Send exactly <code>${price:.2f} USDT</code> and tap below to submit Order ID:"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(cbtn("Submit Binance Order ID", callback_data=f"sub_bn_txid_{plan_id}"))
            safe_send(chat_id, pay_msg, reply_markup=markup)
            return

        if data.startswith("sub_bn_txid_"):
            plan_id = data.replace("sub_bn_txid_", "")
            msg = safe_send(chat_id, f"{CE('sms')} <b>Send your Binance Pay Order ID / Transaction ID:</b>")
            safe_next_step(msg, lambda m: process_binance_txid(m, plan_id))
            return

        # --- In-Bot Controls (Admin & User) ---
        if data == "back_my_bots":
            show_user_bots(chat_id, user_id)
            return

        if data.startswith("ctl_"):
            _, owner_str, fname = data.split("_", 2)
            show_bot_controls_card(chat_id, int(owner_str), fname, call.message.message_id)
            return

        if data.startswith("bact_"):
            parts = data.split("_", 3)
            act, owner_id, fname = parts[1], int(parts[2]), parts[3]
            is_adm = (user_id in admin_ids or user_id == OWNER_ID)
            if user_id != owner_id and not is_adm: return

            ftype, st = None, None
            for fn, ft, s in user_files.get(owner_id, []):
                if fn == fname:
                    ftype, st = ft, s
                    break

            if act == "start":
                if st != "approved":
                    safe_send(chat_id, f"{CE('notice')} <b>Cannot start: Pending admin approval.</b>")
                    return
                fpath = os.path.join(get_user_folder(owner_id), fname)
                threading.Thread(target=run_script, args=(fpath, owner_id, get_user_folder(owner_id), fname, None)).start()
                time.sleep(1.2)
                show_bot_controls_card(chat_id, owner_id, fname, call.message.message_id)

            elif act == "stop":
                skey = f"{owner_id}_{fname}"
                if skey in bot_scripts:
                    kill_process_tree(bot_scripts[skey])
                    bot_scripts.pop(skey, None)
                show_bot_controls_card(chat_id, owner_id, fname, call.message.message_id)

            elif act == "restart":
                if st != "approved":
                    safe_send(chat_id, f"{CE('notice')} <b>Cannot restart: Bot not approved yet.</b>")
                    return
                skey = f"{owner_id}_{fname}"
                if skey in bot_scripts:
                    kill_process_tree(bot_scripts[skey])
                    bot_scripts.pop(skey, None)
                time.sleep(0.5)
                fpath = os.path.join(get_user_folder(owner_id), fname)
                threading.Thread(target=run_script, args=(fpath, owner_id, get_user_folder(owner_id), fname, None)).start()
                time.sleep(1.2)
                show_bot_controls_card(chat_id, owner_id, fname, call.message.message_id)

            elif act == "logs":
                log_path = os.path.join(get_user_folder(owner_id), f"{os.path.splitext(fname)[0]}.log")
                if os.path.exists(log_path):
                    with open(log_path, "r", errors="ignore") as f:
                        tail = "".join(f.readlines()[-25:]) or "Terminal buffer empty."
                    safe_send(chat_id, f"{CE('logs')} <b>TERMINAL OUTPUT (<code>{fname}</code>):</b>\n<pre>{html.escape(tail)}</pre>")
                else:
                    safe_send(chat_id, f"{CE('notice')} <b>No logs generated yet.</b>")

            elif act == "dl":
                folder = get_user_folder(owner_id)
                zip_path = os.path.join(BACKUPS_DIR, f"backup_{fname}")
                shutil.make_archive(zip_path, "zip", folder)
                full_zip = f"{zip_path}.zip"
                with open(full_zip, "rb") as f:
                    bot.send_document(chat_id, f, caption=f"{CE('done')} <b>Complete Backup Archive for {fname}</b>", parse_mode="HTML")
                if os.path.exists(full_zip): os.remove(full_zip)

            elif act == "del":
                execute_permanent_bot_delete(owner_id, fname, executed_by_admin=is_adm)
                safe_edit(chat_id, call.message.message_id, f"{CE('delete')} <b>Bot container <code>{fname}</code> has been completely deleted and purged.</b>")
            return

        # --- Admin Console Routes ---
        if data == "adm_plans_mgr" and (user_id in admin_ids or user_id == OWNER_ID):
            plans = get_all_plans()
            text = f"{CE('diamond')} <b>PLAN MANAGER CONSOLE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            markup = types.InlineKeyboardMarkup(row_width=1)
            for pid, pname, mbots, price, days, _ in plans:
                text += f"• <code>{pid}</code>: <b>{pname}</b> | ${price:.0f} | {days}d | {mbots} bots\n"
                markup.add(cbtn(f"Delete: {pname}", callback_data=f"delplan_{pid}"))
            markup.add(cbtn("➕ Add New Plan", callback_data="add_plan_init"))
            markup.add(cbtn("⬅️ Back to Admin Console", callback_data="admin_console"))
            safe_edit(chat_id, call.message.message_id, text, reply_markup=markup)
            return

        if data.startswith("delplan_"):
            pid = data.replace("delplan_", "")
            delete_plan_db(pid)
            safe_send(chat_id, f"{CE('done')} <b>Plan <code>{pid}</code> removed from database.</b>")
            return

        if data == "add_plan_init":
            msg = safe_send(chat_id, f"{CE('sms')} <b>Send new plan in format:</b>\n<code>plan_id | Plan Name | Max Bots | Price | Days | Description</code>\n\n*Example:*\n<code>mega | Mega Host | 15 | 40 | 30 | 15 Bot Slots with Dedicated Resources</code>")
            safe_next_step(msg, process_add_plan_step)
            return

        if data == "adm_all_bots":
            markup = types.InlineKeyboardMarkup(row_width=1)
            count = 0
            for uid, files in user_files.items():
                for fn, ft, st in files:
                    running = (st == "approved" and is_bot_running(uid, fn))
                    st_icon = "🟢" if running else "🔴"
                    markup.add(cbtn(f"{st_icon} {fn} ({uid})", callback_data=f"ctl_{uid}_{fn}"))
                    count += 1
            markup.add(cbtn("⬅️ Back to Admin Console", callback_data="admin_console"))
            safe_send(chat_id, f"{CE('trader')} <b>GLOBAL INSTANCES MONITOR ({count} Bots):</b>", reply_markup=markup)
            return

        if data == "adm_pending_files":
            pending_items = [(uid, fn) for uid, files in user_files.items() for fn, ft, st in files if st == "pending"]
            if not pending_items:
                safe_send(chat_id, f"{CE('done')} <b>No files awaiting approval.</b>")
                return
            for p_uid, p_fn in pending_items:
                markup = types.InlineKeyboardMarkup(row_width=2)
                f_id = f"{p_uid}_{p_fn}"
                pending_approvals[f_id] = {"user_id": p_uid, "file_name": p_fn, "file_path": os.path.join(get_user_folder(p_uid), p_fn), "file_type": "py"}
                markup.add(
                    cbtn("▶️ Approve & Run", callback_data=f"apprv_{f_id}"),
                    cbtn("🗑️ Reject & Purge", callback_data=f"rjct_{f_id}")
                )
                safe_send(chat_id, f"{CE('notice')} <b>Pending File:</b> <code>{p_fn}</code>\n👤 <b>Owner:</b> <code>{p_uid}</code>", reply_markup=markup)
            return

        if data == "adm_scan_user":
            msg = safe_send(chat_id, f"{CE('search')} <b>Enter User ID to inspect profile & adjust balance:</b>")
            safe_next_step(msg, process_scan_user_input)
            return

        if data.startswith("adm_bal_"):
            parts = data.split("_")
            mode, target_uid = parts[2], int(parts[3])
            sign = "+" if mode == "add" else "-"
            msg = safe_send(chat_id, f"{CE('money')} <b>Enter amount to {mode} for User <code>{target_uid}</code>:</b>\n<i>Example: send 10.0 to {sign}10.0 USD</i>")
            safe_next_step(msg, lambda m: process_balance_adjustment_step(m, target_uid, mode))
            return

        if data.startswith("adm_ban_toggle_"):
            target_uid = int(data.split("_")[3])
            user = get_user_data(target_uid)
            if not user: return
            new_ban = 0 if user[6] == 1 else 1
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (new_ban, target_uid))
                conn.commit()
                conn.close()
            action_text = "Unbanned" if new_ban == 0 else "Banned"
            safe_send(chat_id, f"{CE('done')} <b>User <code>{target_uid}</code> is now {action_text}.</b>")
            return

        if data == "adm_broadcast":
            msg = safe_send(chat_id, f"{CE('notice')} <b>Send announcement text to broadcast to ALL network users:</b>\n<i>Send /cancel to abort.</i>")
            safe_next_step(msg, process_broadcast_transmission)
            return

        if data == "adm_bots_sms":
            msg = safe_send(chat_id, f"{CE('sms')} <b>BROADCAST TO HOSTED BOT OWNERS:</b>\nSend message text:\n<i>Send /cancel to abort.</i>")
            safe_next_step(msg, process_all_bot_owners_sms)
            return

        if data == "adm_change_db":
            msg = safe_send(chat_id, f"{CE('world')} <b>DATABASE SWITCHER:</b>\nEnter database file name (e.g. <code>custom_data.db</code>):")
            safe_next_step(msg, process_switch_database)
            return

        if data == "adm_reboot_all":
            count = 0
            for uid, files in user_files.items():
                for fn, ft, st in files:
                    if st == "approved" and not is_bot_running(uid, fn):
                        fpath = os.path.join(get_user_folder(uid), fn)
                        threading.Thread(target=run_script, args=(fpath, uid, get_user_folder(uid), fn, None)).start()
                        count += 1
            safe_send(chat_id, f"{CE('done')} <b>Rebooted {count} approved worker instances.</b>")
            return

        if data == "adm_stop_all":
            stopped = len(bot_scripts)
            for skey in list(bot_scripts.keys()):
                kill_process_tree(bot_scripts[skey])
                bot_scripts.pop(skey, None)
            safe_send(chat_id, f"{CE('stop')} <b>Terminated {stopped} active running processes.</b>")
            return

        if data == "adm_lock_system":
            bot_locked = not bot_locked
            safe_send(chat_id, f"{CE('power')} <b>Emergency Lockdown State:</b> <code>{bot_locked}</code>")
            return

        if data == "admin_console":
            safe_send(chat_id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
            return

        if data == "adm_close":
            try: bot.delete_message(chat_id, call.message.message_id)
            except Exception: pass
            return

    except Exception as e:
        logger.error(f"Callback exception: {e}")

# ─── ADMIN STEP HANDLERS ───────────────────────────────────────────────────
def process_payment_number_change(message, method):
    num = message.text.strip().replace(" ", "")
    set_setting(f"{method}_number", num)
    safe_send(message.chat.id, f"{CE('done')} <b>{method.title()} number updated to:</b> <code>{num}</code>")

def process_set_binance_pay_id(message):
    new_id = message.text.strip()
    if new_id:
        set_setting("binance_pay_id", new_id)
        safe_send(message.chat.id, f"{CE('done')} <b>Binance Pay ID updated to:</b> <code>{new_id}</code>")

def process_set_binance_usdt_address(message):
    new_addr = message.text.strip()
    if new_addr:
        set_setting("binance_usdt_address", new_addr)
        safe_send(message.chat.id, f"{CE('done')} <b>Binance USDT Address updated to:</b>\n<code>{new_addr}</code>")

def process_switch_database(message):
    global DATABASE_PATH
    db_name = message.text.strip()
    if not db_name.endswith(".db"): db_name += ".db"
    DATABASE_PATH = os.path.join(DATABASE_DIR, db_name)
    init_db()
    load_data()
    safe_send(message.chat.id, f"{CE('done')} <b>Database Switched to <code>{db_name}</code>!</b>")

def process_all_bot_owners_sms(message):
    text = message.text or ""
    if text == "/cancel": return safe_send(message.chat.id, f"{CE('close')} <b>Cancelled.</b>")
    target_ids = [uid for uid, files in user_files.items() if len(files) > 0]
    sent, failed = 0, 0
    for uid in target_ids:
        try:
            safe_send(uid, f"{CE('sms')} <b>IMPORTANT HOSTING NOTICE:</b>\n\n{text}")
            sent += 1
            time.sleep(0.04)
        except Exception: failed += 1
    safe_send(message.chat.id, f"{CE('done')} <b>Delivered to <code>{sent}</code> bot owners (Failed: {failed}).</b>")

def process_manual_txid(message, plan_id, method):
    user_id = message.from_user.id
    tx_id = message.text.strip()
    if not tx_id or len(tx_id) > 100:
        return safe_reply(message, f"{CE('close')} <b>Please send a valid Transaction ID.</b>")
    if is_txid_used(tx_id):
        return safe_reply(message, f"{CE('close')} <b>This Transaction ID has already been utilized!</b>")

    plan = get_plan_by_id(plan_id)
    if not plan: return safe_reply(message, f"{CE('close')} <b>Plan not found.</b>")

    _, name, limit, price, duration, _ = plan
    bdt_val = round(float(price) * USDT_BDT_RATE, 2)
    req_id, status = create_manual_payment_request(user_id, plan_id, method, f"{bdt_val} BDT", tx_id)
    if status == "duplicate":
        return safe_reply(message, f"{CE('close')} <b>This Transaction ID was already submitted.</b>")

    safe_reply(message, f"{CE('done')} <b>Payment Request Registered!</b>\n\nPlan: <code>{name}</code>\nMethod: <code>{method.title()}</code>\nTrxID: <code>{tx_id}</code>\n\nAwaiting admin confirmation.")
    for aid in list(admin_ids):
        try:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                cbtn("Approve", callback_data=f"app_man_{req_id}"),
                cbtn("Reject", callback_data=f"rej_man_{req_id}")
            )
            safe_send(aid, f"{CE('notice')} <b>New Manual Payment #{req_id}</b>\nUser: <code>{user_id}</code>\nPlan: <code>{name}</code>\nAmount: <code>{bdt_val} BDT</code>\nTrxID: <code>{tx_id}</code>", reply_markup=markup)
        except Exception: pass

def process_binance_txid(message, plan_id):
    pay_order_id = message.text.strip()
    user_id = message.from_user.id

    plan = get_plan_by_id(plan_id)
    if not plan: return safe_reply(message, f"{CE('close')} <b>Plan missing.</b>")
    plan_id, name, limit, price, duration, _ = plan
    due_price = float(price)

    if is_txid_used(pay_order_id):
        return safe_reply(message, f"{CE('close')} <b>This Order ID has already been used!</b>")

    wait_msg = safe_reply(message, f"{CE('loading')} <i>Verifying Binance Pay Order ID via API...</i>")

    def run_verify():
        valid, paid, err = check_binance_payment(pay_order_id)
        if valid:
            add_used_txid(pay_order_id)
            expiry = (datetime.now() + timedelta(days=duration)).isoformat()
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute("UPDATE users SET plan_name = ?, plan_expiry = ? WHERE user_id = ?", (name, expiry, user_id))
                conn.commit()
                conn.close()
            safe_edit(message.chat.id, wait_msg.message_id, f"{CE('sparkle')} <b>Binance Payment Verified!</b>\nPlan <code>{name}</code> activated for {duration} days.")
            safe_send(OWNER_ID, f"{CE('done')} <b>Automated Binance Subscription Activated!</b>\nUser: <code>{user_id}</code> | Plan: <code>{name}</code> | TrxID: <code>{pay_order_id}</code>")
        else:
            safe_edit(message.chat.id, wait_msg.message_id, f"{CE('close')} <b>Verification Failed:</b> <code>{err}</code>")
    threading.Thread(target=run_verify).start()

def check_binance_payment(pay_order_id):
    if not BINANCE_API_KEY:
        return False, 0.0, "Binance API Key not configured."
    endpoint = "https://api.binance.com/sapi/v1/pay/transactions"
    ts = int(time.time() * 1000)
    qs = f"timestamp={ts}"
    sig = hmac.new(BINANCE_SECRET_KEY.encode(), qs.encode(), hashlib.sha256).hexdigest()
    url = f"{endpoint}?{qs}&signature={sig}"
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json().get("data", [])
            for item in data:
                oid = str(item.get("orderId", "") or item.get("transactionId", ""))
                if oid.strip() == str(pay_order_id).strip():
                    return True, float(item.get("amount", 0.0)), "Verified"
            return False, 0.0, "Order ID not found in Binance records."
        return False, 0.0, "Binance API permission error."
    except Exception as e:
        return False, 0.0, str(e)

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
            f"<i>Choose an action below to manage user:</i>"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            cbtn("➕ Add Balance", callback_data=f"adm_bal_add_{uid}"),
            cbtn("➖ Deduct Balance", callback_data=f"adm_bal_sub_{uid}")
        )
        ban_lbl = "✅ Unban User" if u[6] == 1 else "🚫 Ban User"
        markup.add(
            cbtn(ban_lbl, callback_data=f"adm_ban_toggle_{uid}"),
            cbtn("⬅️ Back to Admin Console", callback_data="admin_console")
        )
        safe_send(message.chat.id, text, reply_markup=markup)
    except Exception:
        safe_send(message.chat.id, f"{CE('close')} <b>Please provide a numerical User ID.</b>")

def process_balance_adjustment_step(message, target_uid, mode):
    try:
        amount = float(message.text.strip())
        delta = amount if mode == "add" else -amount
        new_bal = update_user_balance(target_uid, delta)
        safe_send(message.chat.id, f"{CE('done')} <b>Balance Updated! User <code>{target_uid}</code> now has <code>${new_bal:.2f} USD</code>.</b>")
        safe_send(target_uid, f"{CE('notice')} <b>Wallet Adjustment Notice:</b>\nAn administrator modified your balance by <code>{delta:+.2f} USD</code>. Current Balance: <code>${new_bal:.2f}</code>.")
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

# ─── USER BUTTON ACTIONS ───────────────────────────────────────────────────
def _logic_upload_file(message):
    user_id = message.from_user.id
    limit = get_user_file_limit(user_id)
    if get_user_file_count(user_id) >= limit:
        return safe_send(message.chat.id, f"{CE('close')} <b>Container Quota Full ({get_user_file_count(user_id)}/{limit})!</b> Upgrade your tier to deploy more bots.")
    safe_send(message.chat.id, f"{CE('up')} <b>Send your .py, .js, or .zip project file document now.</b>\n<i>Our engine will inspect and stage your container for admin approval.</i>")

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
    safe_next_step(msg, _execute_manual_install)

def _execute_manual_install(message):
    pkg = message.text.strip()
    status_m = safe_send(message.chat.id, f"{CE('loading')} <i>Installing {pkg}...</i>")
    ok, text = install_system_package(pkg)
    safe_edit(message.chat.id, status_m.message_id, f"{CE('done') if ok else CE('close')} {text}")

# ─── UNIVERSAL REPLY KEYBOARD MESSAGE HANDLER ──────────────────────────────
@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_universal_text(message):
    if bot_locked and message.from_user.id not in admin_ids:
        return safe_send(message.chat.id, f"{CE('notice')} <b>System Locked for Maintenance.</b>")

    handler = match_reply_button(message.text)
    if handler:
        handler(message)
    elif message.text.startswith("/"):
        if message.text == "/start":
            command_start(message)
        elif message.text == "/admin" and (message.from_user.id in admin_ids or message.from_user.id == OWNER_ID):
            safe_send(message.chat.id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())

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

                        safe_send(uid, f"{CE('notice')} <b>Subscription Plan {pname} Expired!</b>\nYour running bots have been stopped. Renew to restore full container slots.")
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
            print("[+] Starting Infinity Polling (Resilient Engine)...")
            bot.infinity_polling(timeout=30, long_polling_timeout=20, skip_pending=True)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"[!] Telegram API error: {e}")
            if "Conflict" in str(e):
                print("[!] 409 Conflict: Waiting 12 seconds for old instance to release...")
                time.sleep(12)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"[!] Polling recovery loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("=" * 60)
    print(f" NEBULA CLOUD HOSTING - ZERO-CRASH ACTIVE ")
    print(f" Super Admin ID: {OWNER_ID}")
    print(f" Support: {YOUR_USERNAME}")
    print(f" Payment Gateways: Binance, bKash & Nagad (Toggleable)")
    print("=" * 60)

    atexit.register(lambda: [kill_process_tree(p) for p in bot_scripts.values()])
    threading.Thread(target=expiry_cron_loop, daemon=True).start()

    t_flask = Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()

    run_polling()
