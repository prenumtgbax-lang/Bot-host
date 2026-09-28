# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║         NEBULA CLOUD HOSTING BOT — FULL ADVANCED MERGED EDITION           ║
║                                                                           ║
║  • Target Admin ID: 2014144404                                            ║
║  • Support: @YourDomains                                                  ║
║  • Token: 8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU                 ║
║  • Binance Pay Auto API Verification + Partial Payment Tracker            ║
║  • bKash & Nagad Manual Verification with Admin Numbers Editor            ║
║  • Auto-Module Guide & Interactive Package Installer                      ║
║  • Anti-Crash 409 Conflict Protection & Safe Next-Step Button Escaper     ║
║  • 100% Compliant Custom Telegram Emojis & Bot API 7.0+ Button Colors     ║
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

# --- Configurable Conversion Rate ---
USDT_BDT_RATE = 122.0  # 1 USDT = 122 BDT

# --- Flask Keep Alive (Render / Koyeb / VPS 24/7) ---
app = Flask("")

@app.route("/")
def home():
    return "Nebula Cloud Hosting System is Live & Active", 200

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[!] Flask server binding notice: {e}")

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("[+] Background Keep-Alive Server Online.")

# --- Configuration & Credentials ---
TOKEN = "8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU"
OWNER_ID = 2014144404
ADMIN_ID = 2014144404
YOUR_USERNAME = "@YourDomains"
UPDATE_CHANNEL = "https://t.me/YourChannel"

# Binance Pay Integration Config
BINANCE_API_KEY = "e0e4WavqDOqdmKRZHoNPcNt8TsYAUf17FdpVSasXm54QGVGs8JBp9ySkFTTPbcej"
BINANCE_SECRET_KEY = "NFmtwRqLVvcymwNgSc6NwmmyZC2bHb2DFqLwDdItlwhBdFOERa5UYhwXXMtm7r7A"
BINANCE_PAY_ID = "248391029"

# Manual bKash/Nagad Payment Numbers
DEFAULT_BKASH_NUMBER = "017XXXXXXXX"
DEFAULT_NAGAD_NUMBER = "018XXXXXXXX"

# Folder Setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, "upload_bots")
IROTECH_DIR = os.path.join(BASE_DIR, "database_store")
DATABASE_PATH = os.path.join(IROTECH_DIR, "nebulahost.db")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")

FREE_USER_LIMIT = 0
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float("inf")

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

# ─── TELEGRAM CUSTOM EMOJIS MAPPING ────────────────────────────────────────
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
    """Returns compliant custom Telegram emoji tag wrapping valid unicode character."""
    emoji_id, fallback = EMOJIS_DATA.get(key, ("6314480331831385997", "✨"))
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

# ── BOT API 7.0+ BUTTON STYLE & CUSTOM ICON ENHANCER ───────────────────────
class StyledInlineButton(types.InlineKeyboardButton):
    def __init__(self, text, callback_data=None, url=None, style=None, icon=None, **kwargs):
        super().__init__(text, callback_data=callback_data, url=url, **kwargs)
        self.style = style
        if icon and icon in EMOJIS_DATA:
            self.icon_custom_emoji_id = EMOJIS_DATA[icon][0]

    def to_dict(self):
        d = super().to_dict()
        if self.style:
            d["style"] = self.style
        if getattr(self, "icon_custom_emoji_id", None):
            d["icon_custom_emoji_id"] = self.icon_custom_emoji_id
        return d

def cbtn(text, callback_data=None, url=None, style="primary", icon=None):
    return StyledInlineButton(text, callback_data=callback_data, url=url, style=style, icon=icon)

def rkbtn(text, style="primary", icon=None):
    btn = types.KeyboardButton(text)
    if style:
        btn.style = style
    if icon and icon in EMOJIS_DATA:
        btn.icon_custom_emoji_id = EMOJIS_DATA[icon][0]
    return btn

# --- Data Structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
user_selected_plan = {}

# Malware Detection Signatures
MALWARE_SIGNATURES = [b"MZ", b"\x7fELF", b"\xfe\xed\xfa", b"\xce\xfa\xed\xfe", b"PK", b"Rar!"]
ENCRYPTED_FILE_INDICATORS = []
SUSPICIOUS_KEYWORDS = [b"ransomware", b"trojan", b"virus", b"malware", b"backdoor", b"exploit", b"keylogger", b"rootkit"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Safe Messaging Delivery Engine (Zero Crash) ---
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

# --- Database Setup ---
DB_LOCK = threading.Lock()

def init_db():
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    with DB_LOCK:
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS subscriptions
                         (user_id INTEGER PRIMARY KEY, plan_name TEXT, expiry TEXT)""")
            c.execute("""CREATE TABLE IF NOT EXISTS user_files
                         (user_id INTEGER, file_name TEXT, file_type TEXT,
                          PRIMARY KEY (user_id, file_name))""")
            c.execute("""CREATE TABLE IF NOT EXISTS active_users
                         (user_id INTEGER PRIMARY KEY)""")
            c.execute("""CREATE TABLE IF NOT EXISTS admins
                         (user_id INTEGER PRIMARY KEY)""")
            c.execute("""CREATE TABLE IF NOT EXISTS plans
                         (plan_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_limit INTEGER, price TEXT, duration INTEGER, buy_link TEXT)""")
            c.execute("""CREATE TABLE IF NOT EXISTS pending_payments
                         (user_id INTEGER, plan_id INTEGER, paid_amount REAL,
                          PRIMARY KEY (user_id, plan_id))""")
            c.execute("""CREATE TABLE IF NOT EXISTS used_txids
                         (tx_id TEXT PRIMARY KEY)""")
            c.execute("""CREATE TABLE IF NOT EXISTS manual_payment_requests
                         (request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          plan_id INTEGER NOT NULL,
                          method TEXT NOT NULL,
                          amount TEXT NOT NULL,
                          tx_id TEXT NOT NULL UNIQUE,
                          status TEXT NOT NULL DEFAULT 'pending',
                          created_at TEXT NOT NULL)""")
            c.execute("""CREATE TABLE IF NOT EXISTS payment_settings
                         (setting_key TEXT PRIMARY KEY, setting_value TEXT NOT NULL)""")

            c.execute("INSERT OR IGNORE INTO payment_settings (setting_key, setting_value) VALUES (?, ?)",
                      ("bkash_number", DEFAULT_BKASH_NUMBER))
            c.execute("INSERT OR IGNORE INTO payment_settings (setting_key, setting_value) VALUES (?, ?)",
                      ("nagad_number", DEFAULT_NAGAD_NUMBER))
            c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))

            # Seed default plans if empty
            c.execute("SELECT COUNT(*) FROM plans")
            if c.fetchone()[0] == 0:
                default_plans = [
                    ("Starter Plan", 3, "500 BDT", 30, UPDATE_CHANNEL),
                    ("Pro Plan", 8, "1200 BDT", 30, UPDATE_CHANNEL),
                    ("VIP Unlimited", 20, "2500 BDT", 30, UPDATE_CHANNEL)
                ]
                c.executemany("INSERT INTO plans (name, file_limit, price, duration, buy_link) VALUES (?, ?, ?, ?, ?)", default_plans)

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)

def load_data():
    with DB_LOCK:
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()

            c.execute("SELECT user_id, plan_name, expiry FROM subscriptions")
            for row in c.fetchall():
                user_id = row[0]
                plan_name = row[1] if len(row) > 2 else "Premium"
                expiry = row[-1]
                try:
                    user_subscriptions[user_id] = {
                        "plan_name": plan_name,
                        "expiry": datetime.fromisoformat(expiry),
                    }
                except Exception:
                    pass

            c.execute("SELECT user_id, file_name, file_type FROM user_files")
            for user_id, file_name, file_type in c.fetchall():
                user_files.setdefault(user_id, []).append((file_name, file_type))

            c.execute("SELECT user_id FROM active_users")
            active_users.update(user_id for (user_id,) in c.fetchall())

            c.execute("SELECT user_id FROM admins")
            admin_ids.update(user_id for (user_id,) in c.fetchall())

            conn.close()
            logger.info("Data loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)

init_db()
load_data()

# --- Price Parser & Conversion Helper ---
def parse_price_to_usdt(price_str):
    price_clean = str(price_str).upper().strip()
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", price_clean)
    if not numbers:
        return 0.0, price_str

    val = float(numbers[0])
    if "BDT" in price_clean or "TAKA" in price_clean or "TK" in price_clean:
        usdt_val = round(val / USDT_BDT_RATE, 2)
        return usdt_val, f"{price_str} (~{usdt_val} USDT)"
    elif "USDT" in price_clean or "$" in price_clean or "USD" in price_clean:
        return round(val, 2), f"{val} USDT"
    else:
        return round(val, 2), f"{val} USDT"

def add_plan_db(name, file_limit, price, duration, buy_link):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO plans (name, file_limit, price, duration, buy_link) VALUES (?, ?, ?, ?, ?)",
                  (name, file_limit, price, duration, buy_link))
        conn.commit()
        conn.close()

def get_all_plans():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT plan_id, name, file_limit, price, duration, buy_link FROM plans")
        plans = c.fetchall()
        conn.close()
        return plans

def get_plan_by_id(plan_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT plan_id, name, file_limit, price, duration, buy_link FROM plans WHERE plan_id = ?", (plan_id,))
        plan = c.fetchone()
        conn.close()
        return plan

def delete_plan_db(plan_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM plans WHERE plan_id = ?", (plan_id,))
        conn.commit()
        conn.close()

def get_pending_payment(user_id, plan_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT paid_amount FROM pending_payments WHERE user_id=? AND plan_id=?", (user_id, plan_id))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0.0

def update_pending_payment(user_id, plan_id, amount):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO pending_payments (user_id, plan_id, paid_amount) VALUES (?, ?, ?)",
                  (user_id, plan_id, amount))
        conn.commit()
        conn.close()

def clear_pending_payment(user_id, plan_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM pending_payments WHERE user_id=? AND plan_id=?", (user_id, plan_id))
        conn.commit()
        conn.close()

def is_txid_used(tx_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT tx_id FROM used_txids WHERE tx_id=?", (str(tx_id).strip(),))
        row = c.fetchone()
        conn.close()
        return row is not None

def add_used_txid(tx_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO used_txids (tx_id) VALUES (?)", (str(tx_id).strip(),))
        conn.commit()
        conn.close()

def get_payment_number(method):
    key = "bkash_number" if method.lower() == "bkash" else "nagad_number"
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT setting_value FROM payment_settings WHERE setting_key=?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row and row[0] else (DEFAULT_BKASH_NUMBER if key == "bkash_number" else DEFAULT_NAGAD_NUMBER)

def set_payment_number(method, number):
    key = "bkash_number" if method.lower() == "bkash" else "nagad_number"
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO payment_settings (setting_key, setting_value) VALUES (?, ?)", (key, number.strip()))
        conn.commit()
        conn.close()

def manual_amount_for_plan(price):
    raw = str(price).upper().strip()
    number_match = re.findall(r"[-+]?\d*\.?\d+", raw)
    value = float(number_match[0]) if number_match else 0.0
    if "USDT" in raw or "USD" in raw or "$" in raw:
        return f"{round(value * USDT_BDT_RATE, 2)} BDT"
    return str(price).strip()

def create_manual_payment_request(user_id, plan_id, method, amount, tx_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT request_id FROM manual_payment_requests WHERE tx_id=?", (tx_id.strip(),))
        if c.fetchone():
            conn.close()
            return False, "duplicate"
        c.execute(
            "INSERT INTO manual_payment_requests (user_id, plan_id, method, amount, tx_id, status, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (user_id, plan_id, method, str(amount), tx_id.strip(), datetime.now().isoformat()),
        )
        request_id = c.lastrowid
        conn.commit()
        conn.close()
        return request_id, "created"

def get_pending_manual_payments():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT request_id, user_id, plan_id, method, amount, tx_id, created_at FROM manual_payment_requests WHERE status='pending' ORDER BY request_id DESC")
        rows = c.fetchall()
        conn.close()
        return rows

def get_manual_payment_request(request_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT request_id, user_id, plan_id, method, amount, tx_id, status FROM manual_payment_requests WHERE request_id=?", (request_id,))
        row = c.fetchone()
        conn.close()
        return row

def set_manual_payment_status(request_id, status):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("UPDATE manual_payment_requests SET status=? WHERE request_id=? AND status='pending'", (status, request_id))
        changed = c.rowcount
        conn.commit()
        conn.close()
        return changed == 1

# --- Binance Pay Verification Engine ---
def check_binance_payment(pay_order_id):
    if not BINANCE_API_KEY:
        return False, 0.0, "Binance API Key is not configured."

    endpoint = "https://api.binance.com/sapi/v1/pay/transactions"
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"

    signature = hmac.new(
        BINANCE_SECRET_KEY.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    url = f"{endpoint}?{query_string}&signature={signature}"
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            transactions = data.get("data", []) if isinstance(data, dict) else data

            for item in transactions:
                order_id_str = str(item.get("orderId", "") or item.get("transactionId", ""))
                if order_id_str.strip() == str(pay_order_id).strip():
                    amount = float(item.get("amount", 0.0))
                    currency = item.get("currency", "USDT")
                    return True, amount, f"{amount} {currency}"

            return False, 0.0, "Order/Transaction ID not found in Binance Pay records."
        else:
            logger.error(f"Binance Pay API Error: {res.text}")
            return False, 0.0, "Binance API Permission Error."
    except Exception as e:
        logger.error(f"Binance Verification Error: {e}")
        return False, 0.0, f"Error: {str(e)}"

# --- Security Scanner ---
def is_suspicious_file(file_content, file_name):
    file_lower = file_name.lower()
    suspicious_extensions = [".exe", ".dll", ".bat", ".cmd", ".msi", ".jar", ".bin", ".apk", ".iso"]
    if any(file_lower.endswith(ext) for ext in suspicious_extensions):
        return True, f"Suspicious extension: {file_name}"
    for signature in MALWARE_SIGNATURES:
        if file_content.startswith(signature):
            return True, "Malware binary signature detected"
    text_source_extensions = {".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".json", ".txt", ".sh"}
    if not any(file_lower.endswith(ext) for ext in text_source_extensions):
        sample_text = file_content[:4096].decode("utf-8", errors="ignore").lower()
        for keyword in SUSPICIOUS_KEYWORDS:
            if keyword.decode("utf-8").lower() in sample_text:
                return True, f"Suspicious signature: {keyword.decode('utf-8')}"
    return False, "File safe"

def scan_file_for_malware(file_content, file_name, user_id):
    if user_id == OWNER_ID:
        return True, "Owner bypassed security check"
    is_suspicious, reason = is_suspicious_file(file_content, file_name)
    if is_suspicious:
        return False, f"Security violation: {reason}"
    return True, "File passed verification"

# --- User & Process Helpers ---
def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]["expiry"] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    info = bot_scripts.get(script_key)
    if info and info.get("process"):
        try:
            proc = psutil.Process(info["process"].pid)
            if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                return True
            else:
                if "log_file" in info and not info["log_file"].closed:
                    info["log_file"].close()
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
        logger.error(f"Error killing process: {e}")

# --- Missing Library Recovery ---
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
    "cv2": "opencv-python",
    "flask": "Flask",
    "psutil": "psutil",
    "aiohttp": "aiohttp"
}

def monitor_and_guide_error(process, log_file_path, script_owner_id, file_name, message_obj_for_reply):
    time.sleep(3)
    if process.poll() is not None:
        try:
            with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()

            match_py = re.search(r"(?:ModuleNotFoundError|ImportError): No module named '(.+?)'", log_content)
            match_js = re.search(r"Cannot find module '(.+?)'", log_content)

            missing_module = None
            if match_py: missing_module = match_py.group(1).split(".")[0].strip("'\"")
            elif match_js: missing_module = match_js.group(1).split("/")[0].strip("'\"")

            if missing_module:
                pkg_name = TELEGRAM_MODULES.get(missing_module.lower(), missing_module)
                ext = os.path.splitext(file_name)[1].lower()
                cmd_text = f"npm install {pkg_name}" if ext == ".js" else f"pip install {pkg_name}"

                error_msg = (
                    f"{CE('notice')} <b>Execution Stopped: Missing Module</b>\n\n"
                    f"{CE('link')} <b>File:</b> <code>{file_name}</code>\n"
                    f"{CE('close')} <b>Missing Dependency:</b> <code>{missing_module}</code>\n"
                    f"{CE('power')} <b>Command:</b> <code>{cmd_text}</code>\n\n"
                    f"<i>Tap below to auto-install this package:</i>"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(cbtn(f"Install {pkg_name}", callback_data=f"instmod_{script_owner_id}_{missing_module}_{file_name}", style="success", icon="up"))
                markup.add(cbtn("Terminal Logs", callback_data=f"viewlog_{script_owner_id}_{file_name}", style="primary", icon="logs"))
                safe_send(script_owner_id, error_msg, reply_markup=markup)
            else:
                error_msg = (
                    f"{CE('notice')} <b>Runtime Execution Notice!</b>\n\n"
                    f"{CE('link')} <b>File:</b> <code>{file_name}</code>\n"
                    f"<i>The container stopped unexpectedly. View terminal logs below:</i>"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(cbtn("Terminal Logs", callback_data=f"viewlog_{script_owner_id}_{file_name}", style="primary", icon="logs"))
                safe_send(script_owner_id, error_msg, reply_markup=markup)
        except Exception as e:
            logger.error(f"Error checking log: {e}")

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, "w", encoding="utf-8", errors="ignore")
        process = subprocess.Popen([sys.executable, script_path], cwd=user_folder, stdout=log_file, stderr=log_file, stdin=subprocess.PIPE)

        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "script_owner_id": script_owner_id,
            "start_time": datetime.now(),
            "user_folder": user_folder,
            "type": "py"
        }

        safe_send(script_owner_id, f"{CE('done')} <b>Python Script Online:</b> <code>{file_name}</code> (PID: <code>{process.pid}</code>)")
        threading.Thread(target=monitor_and_guide_error, args=(process, log_file_path, script_owner_id, file_name, message_obj_for_reply)).start()
    except Exception as e:
        safe_send(script_owner_id, f"{CE('close')} <b>Process Failure:</b> <code>{str(e)}</code>")

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, "w", encoding="utf-8", errors="ignore")
        process = subprocess.Popen(["node", script_path], cwd=user_folder, stdout=log_file, stderr=log_file, stdin=subprocess.PIPE)

        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "script_owner_id": script_owner_id,
            "start_time": datetime.now(),
            "user_folder": user_folder,
            "type": "js"
        }

        safe_send(script_owner_id, f"{CE('done')} <b>Node.js Script Online:</b> <code>{file_name}</code> (PID: <code>{process.pid}</code>)")
        threading.Thread(target=monitor_and_guide_error, args=(process, log_file_path, script_owner_id, file_name, message_obj_for_reply)).start()
    except Exception as e:
        safe_send(script_owner_id, f"{CE('close')} <b>Process Failure:</b> <code>{str(e)}</code>")

def save_user_file(user_id, file_name, file_type="py"):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)", (user_id, file_name, file_type))
        conn.commit()
        conn.close()
        user_files.setdefault(user_id, [])
        user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
        user_files[user_id].append((file_name, file_type))

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM user_files WHERE user_id = ? AND file_name = ?", (user_id, file_name))
        conn.commit()
        conn.close()
        if user_id in user_files:
            user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]

def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO active_users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()

def save_subscription(user_id, plan_name, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO subscriptions (user_id, plan_name, expiry) VALUES (?, ?, ?)",
                  (user_id, plan_name, expiry.isoformat()))
        conn.commit()
        conn.close()
        user_subscriptions[user_id] = {"plan_name": plan_name, "expiry": expiry}

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        user_subscriptions.pop(user_id, None)

# ─── MENUS & KEYBOARDS (BOT API 7.0+ COLORED BUTTONS) ───────────────────────
COMMAND_BUTTONS_USER = [
    [("Updates Channel", "primary", "link")],
    [("Upload File", "success", "up"), ("Manage Files", "primary", "trader")],
    [("View Plans", "success", "diamond"), ("Speed & Ping", "primary", "speed")],
    [("Bot Stats", "primary", "percent"), ("Terminal Cmd", "primary", "power")],
    [("Contact Owner", "success", "support")]
]

COMMAND_BUTTONS_ADMIN = [
    [("Updates Channel", "primary", "link")],
    [("Upload File", "success", "up"), ("Manage Files", "primary", "trader")],
    [("View Plans", "success", "diamond"), ("Admin Panel", "danger", "admin")],
    [("Speed & Ping", "primary", "speed"), ("Bot Stats", "primary", "percent")],
    [("Contact Owner", "success", "support")]
]

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout = COMMAND_BUTTONS_ADMIN if user_id in admin_ids else COMMAND_BUTTONS_USER
    for row in layout:
        row_btns = [rkbtn(txt, style=st, icon=ic) for txt, st, ic in row]
        markup.add(*row_btns)
    return markup

def create_admin_panel_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        cbtn("Add Plan", callback_data="add_plan_init", style="success", icon="up"),
        cbtn("Manage Plans", callback_data="manage_plans", style="danger", icon="delete"),
    )
    markup.add(
        cbtn("Add Subscription", callback_data="add_subscription", style="primary", icon="diamond"),
        cbtn("Remove Sub", callback_data="remove_subscription", style="danger", icon="close"),
    )
    markup.add(
        cbtn("Add Admin", callback_data="add_admin", style="primary", icon="crown"),
        cbtn("Remove Admin", callback_data="remove_admin", style="primary", icon="delete"),
    )
    markup.add(
        cbtn("Broadcast", callback_data="broadcast", style="primary", icon="notice"),
        cbtn("Lock / Unlock", callback_data="toggle_lock", style="danger", icon="power"),
    )
    markup.add(
        cbtn("Run All Scripts", callback_data="run_all_scripts", style="success", icon="play"),
        cbtn("Bot Stats", callback_data="stats", style="primary", icon="percent"),
    )
    markup.add(
        cbtn("Pending Payments", callback_data="pending_manual_payments", style="primary", icon="money"),
        cbtn("Payment Numbers", callback_data="manual_payment_numbers", style="primary", icon="wallet"),
    )
    return markup

# ─── BUTTON MAPPING & REPLY ROUTER ─────────────────────────────────────────
BUTTON_MAPPING = {
    "Updates Channel": lambda m: safe_send(m.chat.id, f"{CE('link')} <b>Official Channel:</b> {UPDATE_CHANNEL}"),
    "Upload File": lambda m: _logic_upload_file(m),
    "Manage Files": lambda m: _logic_check_files(m),
    "View Plans": lambda m: _logic_view_plans(m),
    "Speed & Ping": lambda m: _logic_speed_ping(m),
    "Bot Stats": lambda m: _logic_bot_stats(m),
    "Terminal Cmd": lambda m: safe_send(m.chat.id, f"{CE('power')} <b>Terminal ready for execution.</b>"),
    "Contact Owner": lambda m: safe_send(m.chat.id, f"{CE('support')} <b>Owner & Support:</b> {YOUR_USERNAME}"),
    "Admin Panel": lambda m: safe_send(m.chat.id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
}

def match_reply_button(text):
    t_clean = re.sub(r'[^\w\s]', '', text or '').strip().lower()
    for k in BUTTON_MAPPING:
        k_clean = re.sub(r'[^\w\s]', '', k).strip().lower()
        if k_clean in t_clean or t_clean in k_clean:
            return BUTTON_MAPPING[k]
    return None

def safe_next_step(msg, callback):
    """Prevents user or admin inputs from getting stuck by clearing pending states on menu clicks."""
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

# ─── WELCOME LOGIC ─────────────────────────────────────────────────────────
def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    if bot_locked and user_id not in admin_ids:
        safe_send(chat_id, f"{CE('notice')} <b>Bot is temporarily locked by Admin.</b>")
        return

    if user_id not in active_users:
        add_active_user(user_id)

    if user_id == OWNER_ID:
        user_status = f"{CE('crown')} <b>Root Administrator</b>"
    elif user_id in admin_ids:
        user_status = f"{CE('shield')} <b>Authorized Admin</b>"
    elif user_id in user_subscriptions and user_subscriptions[user_id]["expiry"] > datetime.now():
        sub = user_subscriptions[user_id]
        days_left = (sub["expiry"] - datetime.now()).days
        user_status = f"{CE('diamond')} <b>{sub.get('plan_name', 'Premium')} Active</b> ({days_left} Days remaining)"
    else:
        user_status = f"{CE('close')} <b>No Active Plan</b>"

    welcome_msg = (
        f"{CE('crown')} <b>NEBULA CLOUD HOSTING ENGINE</b> {CE('fire')}\n\n"
        f"{CE('trader')} <b>Holder:</b> <code>{html.escape(user_name or 'User')}</code>\n"
        f"{CE('link')} <b>Account ID:</b> <code>{user_id}</code>\n"
        f"{CE('shield')} <b>Authority:</b> {user_status}\n"
        f"{CE('power')} <b>Allocated Containers:</b> <code>{get_user_file_count(user_id)} / {get_user_file_limit(user_id)}</code>\n\n"
        f"{CE('speed')} <i>High-performance isolated Subprocess execution for Python and Node.js.</i>\n"
        f"<i>Select an option from the menu buttons below:</i>"
    )
    safe_send(chat_id, welcome_msg, reply_markup=create_reply_keyboard_main_menu(user_id))

def _logic_view_plans(message_or_call):
    chat_id = message_or_call.chat.id if isinstance(message_or_call, telebot.types.Message) else message_or_call.message.chat.id
    plans = get_all_plans()

    if not plans:
        safe_send(chat_id, f"{CE('notice')} <b>Currently no hosting packages available.</b>")
        return

    safe_send(chat_id, f"{CE('diamond')} <b>AVAILABLE SUBSCRIPTION PACKAGES:</b>")

    for plan in plans:
        plan_id, name, limit, price, duration, _ = plan
        usdt_price, formatted_price = parse_price_to_usdt(price)

        card_text = (
            f"{CE('crown')} <b>Tier:</b> <code>{name}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"{CE('power')} <b>File Limit:</b> <code>{limit} Containers</code>\n"
            f"{CE('date')} <b>Duration:</b> <code>{duration} Days</code>\n"
            f"{CE('money')} <b>Price:</b> <code>{formatted_price}</code>\n"
            f"{CE('wallet')} <b>Gateways:</b> Binance Pay / bKash / Nagad\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            cbtn("Binance Pay", callback_data=f"buy_binance_{plan_id}", style="success", icon="binance"),
            cbtn("bKash", callback_data=f"buy_manual_bkash_{plan_id}", style="primary", icon="bkash"),
            cbtn("Nagad", callback_data=f"buy_manual_nagad_{plan_id}", style="primary", icon="nagad")
        )
        safe_send(chat_id, card_text, reply_markup=markup)

def _logic_upload_file(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        safe_reply(message, f"{CE('notice')} <b>Bot is locked by Administrator.</b>")
        return

    has_active_plan = False
    plan_name = "None"

    if user_id in admin_ids or user_id == OWNER_ID:
        has_active_plan = True
        plan_name = "Admin / Owner Unlimited"
    elif user_id in user_subscriptions and user_subscriptions[user_id]["expiry"] > datetime.now():
        has_active_plan = True
        plan_name = user_subscriptions[user_id].get("plan_name", "Premium Plan")

    if not has_active_plan:
        markup = types.InlineKeyboardMarkup()
        markup.add(cbtn("View Plans & Buy", callback_data="view_plans_cb", style="primary", icon="diamond"))
        safe_reply(
            message,
            f"{CE('close')} <b>No Active Subscription!</b>\n\nYou need an active hosting tier to upload and run bots. View packages below:",
            reply_markup=markup
        )
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(cbtn(f"Continue with {plan_name}", callback_data="confirm_plan_upload", style="success", icon="done"))
    safe_reply(
        message,
        f"{CE('shield')} <b>Active Plan Verified:</b> <code>{plan_name}</code>\n\nTap below to proceed with file upload:",
        reply_markup=markup
    )

def _logic_check_files(message):
    user_id = message.from_user.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        safe_reply(message, f"{CE('trader')} <b>Your Files:</b>\n\n<i>(No instances deployed yet)</i>")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        running = is_bot_running(user_id, file_name)
        st_text = "ONLINE" if running else "STOPPED"
        icon_k = "done" if running else "close"
        st_style = "success" if running else "danger"
        markup.add(cbtn(f"[{st_text}] {file_name} ({file_type})", callback_data=f"file_{user_id}_{file_name}", style=st_style, icon=icon_k))

    safe_reply(message, f"{CE('trader')} <b>MANAGE DEPLOYED CONTAINERS:</b>", reply_markup=markup)

def _logic_speed_ping(message):
    start = time.time()
    try: bot.get_me()
    except Exception: pass
    latency = round((time.time() - start) * 1000, 2)
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    safe_reply(
        message,
        f"{CE('speed')} <b>INFRASTRUCTURE BENCHMARK:</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('done')} <b>Latency:</b> <code>{latency} ms</code>\n"
        f"{CE('boom')} <b>CPU Usage:</b> <code>{cpu}%</code>\n"
        f"{CE('diamond')} <b>RAM Load:</b> <code>{ram}%</code>\n"
        f"{CE('power')} <b>Status:</b> <code>100% Operational & Isolated</code>"
    )

def _logic_bot_stats(message):
    running = sum(1 for k, v in bot_scripts.items() if is_bot_running(int(k.split('_')[0]), v['file_name']))
    safe_reply(
        message,
        f"{CE('percent')} <b>SYSTEM STATISTICS:</b>\n\n"
        f"{CE('trader')} <b>Total Registered:</b> <code>{len(active_users)}</code>\n"
        f"{CE('power')} <b>Hosted Containers:</b> <code>{sum(len(f) for f in user_files.values())}</code>\n"
        f"{CE('done')} <b>Active Worker PIDs:</b> <code>{running}</code>"
    )

# ─── DOCUMENT UPLOAD HANDLER ───────────────────────────────────────────────
@bot.message_handler(content_types=["document"])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document

    if user_id not in admin_ids and user_id != OWNER_ID:
        if user_id not in user_subscriptions or user_subscriptions[user_id]["expiry"] <= datetime.now():
            return safe_reply(message, f"{CE('close')} <b>No active subscription found. Please buy a plan first!</b>")

    file_name = doc.file_name or "main.py"
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in [".py", ".js", ".zip"]:
        return safe_reply(message, f"{CE('close')} <b>Only .py, .js, and .zip files are supported!</b>")

    try:
        download_wait_msg = safe_reply(message, f"{CE('loading')} <i>Downloading & Analyzing {file_name}...</i>")
        file_info_tg = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info_tg.file_path)

        if user_id != OWNER_ID:
            is_safe, reason = scan_file_for_malware(downloaded, file_name, user_id)
            if not is_safe:
                safe_edit(chat_id, download_wait_msg.message_id, f"{CE('close')} <b>Security Violation:</b> {reason}")
                return

        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        with open(file_path, "wb") as f:
            f.write(downloaded)

        safe_edit(chat_id, download_wait_msg.message_id, f"{CE('done')} <b>File <code>{file_name}</code> provisioned and launched!</b>")

        if file_ext == ".js":
            save_user_file(user_id, file_name, "js")
            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
        elif file_ext == ".py":
            save_user_file(user_id, file_name, "py")
            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, message)).start()
    except Exception as e:
        safe_reply(message, f"{CE('close')} <b>Error:</b> <code>{str(e)}</code>")

# ─── CALLBACK QUERY ENGINE ─────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global bot_locked
    user_id = call.from_user.id
    data = call.data
    chat_id = call.message.chat.id

    if data == "view_plans_cb":
        bot.answer_callback_query(call.id)
        _logic_view_plans(call)

    elif data == "confirm_plan_upload":
        bot.answer_callback_query(call.id, "Plan Verified!")
        safe_send(chat_id, f"{CE('up')} <b>Send your .py, .js, or .zip file now:</b>")

    # --- Interactive Module Recovery ---
    elif data.startswith("instmod_"):
        _, owner_id, mod_name, fname = data.split("_", 3)
        if user_id != int(owner_id) and user_id not in admin_ids:
            return bot.answer_callback_query(call.id, "Unauthorized.", show_alert=True)

        bot.answer_callback_query(call.id)
        pkg_name = TELEGRAM_MODULES.get(mod_name.lower(), mod_name)
        ext = os.path.splitext(fname)[1].lower()

        status_msg = safe_send(chat_id, f"{CE('loading')} <i>Installing package:</i> <code>{pkg_name}</code>...")

        def do_pip_install():
            cmd = ["npm", "install", pkg_name] if ext == ".js" else [sys.executable, "-m", "pip", "install", "--break-system-packages", pkg_name]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                safe_edit(chat_id, status_msg.message_id, f"{CE('done')} <b>Package <code>{pkg_name}</code> installed!</b> Rebooting...")
                time.sleep(1)
                ufolder = get_user_folder(int(owner_id))
                fpath = os.path.join(ufolder, fname)
                if ext == ".js": run_js_script(fpath, int(owner_id), ufolder, fname, call.message)
                else: run_script(fpath, int(owner_id), ufolder, fname, call.message)
            else:
                safe_edit(chat_id, status_msg.message_id, f"{CE('close')} <b>Install Failed:</b>\n<pre>{res.stderr[:250]}</pre>")

        threading.Thread(target=do_pip_install).start()

    elif data.startswith("viewlog_"):
        _, owner_id, fname = data.split("_", 2)
        ufolder = get_user_folder(int(owner_id))
        log_fpath = os.path.join(ufolder, f"{os.path.splitext(fname)[0]}.log")
        if os.path.exists(log_fpath):
            with open(log_fpath, "r", encoding="utf-8", errors="ignore") as f:
                logs = f.read()[-2000:]
            safe_send(chat_id, f"{CE('logs')} <b>Error Log for <code>{fname}</code>:</b>\n<pre>{html.escape(logs if logs else 'Logs clean')}</pre>")
        else:
            bot.answer_callback_query(call.id, "No logs recorded.", show_alert=True)

    # --- Manual bKash/Nagad Payment Handlers ---
    elif data.startswith("buy_manual_bkash_") or data.startswith("buy_manual_nagad_"):
        parts = data.split("_")
        method = "bkash" if parts[2] == "bkash" else "nagad"
        plan_id = int(parts[3])
        plan = get_plan_by_id(plan_id)
        if not plan:
            return bot.answer_callback_query(call.id, "Plan not found!", show_alert=True)

        bot.answer_callback_query(call.id)
        _, name, limit, price, duration, _ = plan
        manual_amount = manual_amount_for_plan(price)
        number = get_payment_number(method)

        pay_msg = (
            f"{CE(method)} <b>Manual {method.title()} Payment Gateway</b>\n\n"
            f"{CE('crown')} <b>Plan:</b> <code>{name}</code>\n"
            f"{CE('money')} <b>Amount:</b> <code>{manual_amount}</code>\n"
            f"{CE('date')} <b>Duration:</b> <code>{duration} Days</code>\n\n"
            f"1️⃣ Send <code>{manual_amount}</code> via Personal Send Money:\n"
            f"📱 <b>{method.title()} Number:</b> <code>{number}</code> (Tap to Copy)\n\n"
            f"2️⃣ After payment, tap the button below to submit your Transaction ID:"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(cbtn("Submit Transaction ID", callback_data=f"submit_manual_{method}_{plan_id}", style="success", icon="sms"))
        safe_send(chat_id, pay_msg, reply_markup=markup)

    elif data.startswith("submit_manual_"):
        parts = data.split("_")
        method = parts[2]
        plan_id = int(parts[3])
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('sms')} <b>Send your {method.title()} Transaction ID (TrxID):</b>")
        safe_next_step(msg, lambda m: process_manual_txid(m, plan_id, method))

    # --- Admin Manual Payment Actions ---
    elif data == "manual_payment_numbers" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            cbtn("Change bKash", callback_data="change_manual_bkash", style="primary", icon="bkash"),
            cbtn("Change Nagad", callback_data="change_manual_nagad", style="primary", icon="nagad"),
        )
        safe_send(chat_id, f"{CE('wallet')} <b>Manual Gateway Numbers:</b>\n\n• bKash: <code>{get_payment_number('bkash')}</code>\n• Nagad: <code>{get_payment_number('nagad')}</code>", reply_markup=markup)

    elif data in ("change_manual_bkash", "change_manual_nagad") and user_id in admin_ids:
        method = "bkash" if data.endswith("bkash") else "nagad"
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('sms')} <b>Send new {method.title()} number:</b>")
        safe_next_step(msg, lambda m: process_payment_number_change(m, method))

    elif data == "pending_manual_payments" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        rows = get_pending_manual_payments()
        if not rows:
            return safe_send(chat_id, f"{CE('done')} <b>No pending manual payments.</b>")
        for req_id, uid, pid, method, amount, txid, created in rows:
            plan = get_plan_by_id(pid)
            plan_name = plan[1] if plan else "Unknown"
            text = (
                f"{CE('money')} <b>Manual Payment Request #{req_id}</b>\n\n"
                f"{CE('trader')} <b>User ID:</b> <code>{uid}</code>\n"
                f"{CE('crown')} <b>Plan:</b> <code>{plan_name}</code>\n"
                f"{CE('wallet')} <b>Method:</b> <code>{method.title()}</code>\n"
                f"{CE('balance')} <b>Amount:</b> <code>{amount}</code>\n"
                f"{CE('sms')} <b>TrxID:</b> <code>{txid}</code>\n"
                f"{CE('date')} <b>Time:</b> <code>{created}</code>"
            )
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                cbtn("Approve", callback_data=f"approve_manual_{req_id}", style="success", icon="done"),
                cbtn("Reject", callback_data=f"reject_manual_{req_id}", style="danger", icon="close")
            )
            safe_send(chat_id, text, reply_markup=markup)

    elif data.startswith("approve_manual_") and user_id in admin_ids:
        req_id = int(data.split("_")[-1])
        req = get_manual_payment_request(req_id)
        if not req or req[6] != "pending":
            return bot.answer_callback_query(call.id, "Request already processed!", show_alert=True)
        _, uid, pid, method, amount, txid, status = req
        plan = get_plan_by_id(pid)
        if not plan: return bot.answer_callback_query(call.id, "Plan not found!")
        if not set_manual_payment_status(req_id, "approved"): return

        name, duration = plan[1], plan[4]
        expiry = datetime.now() + timedelta(days=duration)
        save_subscription(uid, name, expiry)
        add_used_txid(txid)
        bot.answer_callback_query(call.id, "Payment Approved!")
        safe_send(chat_id, f"{CE('done')} <b>Payment #{req_id} approved for User <code>{uid}</code>.</b>")
        safe_send(uid, f"{CE('sparkle')} <b>Payment Approved!</b>\n\n{CE('crown')} <b>Plan:</b> <code>{name}</code>\n{CE('date')} <b>Expiry:</b> <code>{expiry.strftime('%Y-%m-%d %H:%M')}</code>\n\nYour hosting slots are now active!")

    elif data.startswith("reject_manual_") and user_id in admin_ids:
        req_id = int(data.split("_")[-1])
        if not set_manual_payment_status(req_id, "rejected"): return
        bot.answer_callback_query(call.id, "Payment Rejected!")
        safe_send(chat_id, f"{CE('close')} <b>Payment #{req_id} rejected.</b>")

    # --- Binance Pay Handlers ---
    elif data.startswith("buy_binance_"):
        plan_id = int(data.split("_")[2])
        plan = get_plan_by_id(plan_id)
        if not plan: return bot.answer_callback_query(call.id, "Plan not found!")
        bot.answer_callback_query(call.id)
        _, name, limit, price, duration, _ = plan

        usdt_price, formatted_price = parse_price_to_usdt(price)
        already_paid = get_pending_payment(user_id, plan_id)
        due_amount = max(0.0, round(usdt_price - already_paid, 2))

        pay_msg = (
            f"{CE('binance')} <b>Binance Pay Automated Gateway</b>\n\n"
            f"{CE('crown')} <b>Plan:</b> <code>{name}</code>\n"
            f"{CE('money')} <b>Total Price:</b> <code>{usdt_price} USDT</code> ({formatted_price})\n"
        )
        if already_paid > 0:
            pay_msg += f"{CE('done')} <b>Previously Credited:</b> <code>{already_paid} USDT</code>\n{CE('notice')} <b>Remaining Due:</b> <code>{due_amount} USDT</code>\n\n"
        else:
            pay_msg += f"{CE('date')} <b>Duration:</b> <code>{duration} Days</code>\n\n"

        pay_msg += (
            f"1️⃣ Open Binance App ➔ Pay ➔ Send.\n"
            f"2️⃣ Send exactly <code>{due_amount} USDT</code> to:\n"
            f"🔸 <b>Binance Pay ID:</b> <code>{BINANCE_PAY_ID}</code>\n\n"
            f"3️⃣ Tap below to submit your Binance Pay Order / Transaction ID:"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(cbtn("Submit Binance Order ID", callback_data=f"submit_txid_{plan_id}", style="success", icon="binance"))
        safe_send(chat_id, pay_msg, reply_markup=markup)

    elif data.startswith("submit_txid_"):
        plan_id = int(data.split("_")[2])
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('sms')} <b>Send your Binance Pay Order ID / Transaction ID:</b>")
        safe_next_step(msg, lambda m: process_binance_txid(m, plan_id))

    # --- Admin Callbacks ---
    elif data == "add_plan_init" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('sms')} <b>Send plan configuration:</b>\n<code>Name | Limit | Price | DurationInDays | BuyLink</code>\n\n*Example:* <code>Pro | 8 | 1200 BDT | 30 | https://t.me/YourChannel</code>")
        safe_next_step(msg, process_add_plan)

    elif data == "manage_plans" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        plans = get_all_plans()
        if not plans: return safe_send(chat_id, f"{CE('notice')} <b>No plans found.</b>")
        markup = types.InlineKeyboardMarkup(row_width=1)
        for p in plans:
            markup.add(cbtn(f"Delete {p[1]}", callback_data=f"del_plan_{p[0]}", style="danger", icon="delete"))
        safe_send(chat_id, f"{CE('delete')} <b>Select Plan to Delete:</b>", reply_markup=markup)

    elif data.startswith("del_plan_") and user_id in admin_ids:
        pid = int(data.split("_")[2])
        delete_plan_db(pid)
        bot.answer_callback_query(call.id, "Plan Deleted!")
        safe_send(chat_id, f"{CE('done')} <b>Plan successfully deleted.</b>")

    elif data == "add_subscription" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('diamond')} <b>Enter User ID, Plan Name & Days:</b>\n<code>UserID PlanName Days</code>\n*Example:* <code>123456789 Pro 30</code>")
        safe_next_step(msg, process_add_subscription)

    elif data == "remove_subscription" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('close')} <b>Enter User ID to revoke subscription:</b>")
        safe_next_step(msg, lambda m: remove_subscription_db(int(m.text.strip())) or safe_send(m.chat.id, f"{CE('done')} <b>Revoked.</b>"))

    elif data == "add_admin" and user_id == OWNER_ID:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('crown')} <b>Send User ID to promote to Admin:</b>")
        safe_next_step(msg, lambda m: admin_ids.add(int(m.text.strip())) or safe_send(m.chat.id, f"{CE('done')} <b>Admin Added.</b>"))

    elif data == "remove_admin" and user_id == OWNER_ID:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('delete')} <b>Send Admin ID to demote:</b>")
        safe_next_step(msg, lambda m: admin_ids.discard(int(m.text.strip())) or safe_send(m.chat.id, f"{CE('done')} <b>Admin Removed.</b>"))

    elif data == "broadcast" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('notice')} <b>Send broadcast text:</b>\n<i>Send /cancel to abort.</i>")
        safe_next_step(msg, process_broadcast)

    elif data == "toggle_lock" and user_id in admin_ids:
        bot_locked = not bot_locked
        bot.answer_callback_query(call.id, f"Locked: {bot_locked}")
        safe_send(chat_id, f"{CE('power')} <b>Lock State:</b> <code>{bot_locked}</code>")

    elif data == "run_all_scripts" and user_id in admin_ids:
        bot.answer_callback_query(call.id, "Rebooting...")
        count = 0
        for uid, flist in user_files.items():
            for fname, ftype in flist:
                if not is_bot_running(uid, fname):
                    fpath = os.path.join(get_user_folder(uid), fname)
                    if ftype == "js": threading.Thread(target=run_js_script, args=(fpath, uid, get_user_folder(uid), fname, call.message)).start()
                    else: threading.Thread(target=run_script, args=(fpath, uid, get_user_folder(uid), fname, call.message)).start()
                    count += 1
        safe_send(chat_id, f"{CE('done')} <b>Rebooted {count} idle instances.</b>")

    elif data == "stats" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        running = sum(1 for k, v in bot_scripts.items() if is_bot_running(int(k.split('_')[0]), v['file_name']))
        safe_send(chat_id, f"{CE('percent')} <b>SYSTEM STATS:</b>\n\nUsers: <code>{len(active_users)}</code>\nFiles: <code>{sum(len(f) for f in user_files.values())}</code>\nRunning: <code>{running}</code>")

    # --- File Management Controls ---
    elif data.startswith("file_"):
        _, owner_id, fname = data.split("_", 2)
        running = is_bot_running(int(owner_id), fname)
        markup = types.InlineKeyboardMarkup(row_width=2)
        if running:
            markup.add(cbtn("Stop Process", callback_data=f"stop_{owner_id}_{fname}", style="danger", icon="stop"))
        else:
            markup.add(cbtn("Start Process", callback_data=f"start_{owner_id}_{fname}", style="success", icon="play"))
        markup.add(
            cbtn("Terminal Logs", callback_data=f"viewlog_{owner_id}_{fname}", style="primary", icon="logs"),
            cbtn("Delete File", callback_data=f"del_{owner_id}_{fname}", style="danger", icon="delete")
        )
        safe_send(chat_id, f"{CE('diamond')} <b>File:</b> <code>{fname}</code>\n{CE('speed')} <b>Status:</b> {'ONLINE' if running else 'STOPPED'}", reply_markup=markup)

    elif data.startswith("start_"):
        _, owner_id, fname = data.split("_", 2)
        fpath = os.path.join(get_user_folder(int(owner_id)), fname)
        if fname.endswith(".js"): threading.Thread(target=run_js_script, args=(fpath, int(owner_id), get_user_folder(int(owner_id)), fname, call.message)).start()
        else: threading.Thread(target=run_script, args=(fpath, int(owner_id), get_user_folder(int(owner_id)), fname, call.message)).start()
        bot.answer_callback_query(call.id, "Started!")

    elif data.startswith("stop_"):
        _, owner_id, fname = data.split("_", 2)
        skey = f"{owner_id}_{fname}"
        if skey in bot_scripts:
            kill_process_tree(bot_scripts[skey])
            bot_scripts.pop(skey, None)
        bot.answer_callback_query(call.id, "Stopped!")
        safe_send(chat_id, f"{CE('stop')} <b>Script <code>{fname}</code> stopped.</b>")

    elif data.startswith("del_"):
        _, owner_id, fname = data.split("_", 2)
        skey = f"{owner_id}_{fname}"
        if skey in bot_scripts:
            kill_process_tree(bot_scripts[skey])
            bot_scripts.pop(skey, None)
        remove_user_file_db(int(owner_id), fname)
        fpath = os.path.join(get_user_folder(int(owner_id)), fname)
        if os.path.exists(fpath): os.remove(fpath)
        bot.answer_callback_query(call.id, "Deleted!")
        safe_send(chat_id, f"{CE('delete')} <b>File <code>{fname}</code> removed.</b>")

# --- Step Handlers Processing ---
def process_payment_number_change(message, method):
    if message.from_user.id not in admin_ids: return
    number = message.text.strip().replace(" ", "").replace("-", "")
    if not re.fullmatch(r"(?:\+?88)?01[3-9]\d{8}", number):
        return safe_reply(message, f"{CE('close')} <b>Please provide a valid Bangladeshi number (e.g. 017XXXXXXXX).</b>")
    set_payment_number(method, message.text.strip())
    safe_reply(message, f"{CE('done')} <b>{method.title()} number updated to:</b> <code>{message.text.strip()}</code>")

def process_manual_txid(message, plan_id, method):
    user_id = message.from_user.id
    tx_id = message.text.strip()
    if not tx_id or len(tx_id) > 100:
        return safe_reply(message, f"{CE('close')} <b>Please send a valid Transaction ID.</b>")
    if is_txid_used(tx_id):
        return safe_reply(message, f"{CE('close')} <b>This Transaction ID has already been utilized!</b>")
    plan = get_plan_by_id(plan_id)
    if not plan: return safe_reply(message, f"{CE('close')} <b>Plan not located.</b>")

    _, name, limit, price, duration, _ = plan
    manual_amount = manual_amount_for_plan(price)
    req_id, status = create_manual_payment_request(user_id, plan_id, method, manual_amount, tx_id)
    if status == "duplicate":
        return safe_reply(message, f"{CE('close')} <b>This Transaction ID has already been submitted.</b>")

    safe_reply(message, f"{CE('done')} <b>Payment Request Registered!</b>\n\n{CE('crown')} <b>Plan:</b> <code>{name}</code>\n{CE('wallet')} <b>Method:</b> <code>{method.title()}</code>\n{CE('sms')} <b>TrxID:</b> <code>{tx_id}</code>\n\nAwaiting admin confirmation.")
    for aid in list(admin_ids):
        try:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                cbtn("Approve", callback_data=f"approve_manual_{req_id}", style="success", icon="done"),
                cbtn("Reject", callback_data=f"reject_manual_{req_id}", style="danger", icon="close")
            )
            safe_send(aid, f"{CE('notice')} <b>New Manual Payment #{req_id}</b>\n\nUser: <code>{user_id}</code>\nPlan: <code>{name}</code>\nAmount: <code>{manual_amount}</code>\nTrxID: <code>{tx_id}</code>", reply_markup=markup)
        except Exception: pass

def process_binance_txid(message, plan_id):
    pay_order_id = message.text.strip()
    user_id = message.from_user.id

    plan = get_plan_by_id(plan_id)
    if not plan: return safe_reply(message, f"{CE('close')} <b>Plan missing.</b>")
    plan_id, name, limit, price, duration, _ = plan
    usdt_price, formatted_price = parse_price_to_usdt(price)

    if is_txid_used(pay_order_id):
        return safe_reply(message, f"{CE('close')} <b>This Order ID has already been utilized!</b>")

    wait_msg = safe_reply(message, f"{CE('loading')} <i>Verifying Binance Pay Order ID via API...</i>")
    is_valid, paid_amount_new, amount_or_error = check_binance_payment(pay_order_id)

    if is_valid:
        add_used_txid(pay_order_id)
        already_paid = get_pending_payment(user_id, plan_id)
        total_paid = round(already_paid + paid_amount_new, 2)

        if total_paid < usdt_price:
            remaining = round(usdt_price - total_paid, 2)
            update_pending_payment(user_id, plan_id, total_paid)
            safe_edit(message.chat.id, wait_msg.message_id,
                      f"{CE('notice')} <b>Partial Payment Received!</b>\n\n"
                      f"Required: <code>{usdt_price} USDT</code>\n"
                      f"Received: <code>{total_paid} USDT</code>\n"
                      f"Remaining Due: <code>{remaining} USDT</code>\n\n"
                      f"Send remaining balance to complete activation.")
            return

        clear_pending_payment(user_id, plan_id)
        expiry = datetime.now() + timedelta(days=duration)
        save_subscription(user_id, name, expiry)
        safe_edit(message.chat.id, wait_msg.message_id, f"{CE('sparkle')} <b>Payment Verified!</b>\n\nPlan <code>{name}</code> activated for {duration} days.")
        safe_send(OWNER_ID, f"{CE('done')} <b>Automated Binance Subscription Activated!</b>\nUser: <code>{user_id}</code> | Plan: <code>{name}</code> | TrxID: <code>{pay_order_id}</code>")
    else:
        safe_edit(message.chat.id, wait_msg.message_id, f"{CE('close')} <b>Verification Failed:</b> <code>{amount_or_error}</code>")

def process_add_plan(message):
    try:
        parts = [p.strip() for p in message.text.split("|")]
        name, limit, price, duration, buy_link = parts[0], int(parts[1]), parts[2], int(parts[3]), parts[4]
        add_plan_db(name, limit, price, duration, buy_link)
        safe_reply(message, f"{CE('done')} <b>Plan <code>{name}</code> created!</b>")
    except Exception as e:
        safe_reply(message, f"{CE('close')} <b>Invalid Format:</b> <code>{e}</code>")

def process_add_subscription(message):
    try:
        parts = message.text.split()
        sub_uid, pname, days = int(parts[0]), parts[1], int(parts[2])
        exp = datetime.now() + timedelta(days=days)
        save_subscription(sub_uid, pname, exp)
        safe_reply(message, f"{CE('done')} <b>Subscription granted to <code>{sub_uid}</code> ({days}d).</b>")
    except Exception as e:
        safe_reply(message, f"{CE('close')} <b>Error:</b> <code>{e}</code>")

def process_broadcast(message):
    text = message.text or ""
    if text == "/cancel": return safe_reply(message, f"{CE('close')} <b>Cancelled.</b>")
    status_m = safe_reply(message, f"{CE('loading')} <i>Broadcasting...</i>")
    sent, failed = 0, 0
    for uid in list(active_users):
        try:
            safe_send(uid, f"{CE('notice')} <b>ANNOUNCEMENT:</b>\n\n{text}")
            sent += 1
            time.sleep(0.04)
        except Exception: failed += 1
    safe_edit(message.chat.id, status_m.message_id, f"{CE('done')} <b>Delivered:</b> <code>{sent}</code> | <b>Failed:</b> <code>{failed}</code>")

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

def command_start(message):
    _logic_send_welcome(message)

# ─── CLEANUP & CRASH-PROOF POLLING ENGINE ──────────────────────────────────
def cleanup():
    for key, info in list(bot_scripts.items()):
        kill_process_tree(info)
    bot_scripts.clear()

atexit.register(cleanup)

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
    print(f" Bot API 7.0+ Button Styling & Custom Emoji Ready")
    print("=" * 60)

    keep_alive()
    run_polling()
