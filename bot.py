# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║              NEBULA CLOUD HOSTING BOT — FULL ADVANCED EDITION             ║
║                                                                           ║
║  • Target Admin ID: 2014144404                                            ║
║  • Support: @YourDomains                                                  ║
║  • Token: 8675366388:AAGFTx2E3aJKA3Ahw8BKyne_ZNsTSF0wcBI                 ║
║  • Auto Module Guide, Interactive Installer & Crash Log Engine            ║
║  • Dynamic Plans, Approval System & Full Multi-Subprocess Hosting         ║
║  • Zero Raw Unicode Emojis — 100% Telegram Custom Emoji IDs & Colors      ║
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

# --- Flask Keep Alive ---
app = Flask("")

@app.route("/")
def home():
    return "Nebula File Host Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")

# --- Configuration (Previous Credentials Retained) ---
TOKEN = "8675366388:AAGaY5OCj7NrzLbLPUt5cYID6ZnDpRDoLMU"
OWNER_ID = 2014144404
ADMIN_ID = 2014144404
YOUR_USERNAME = "@YourDomains"
SUPPORT_CONTACT_ID = 2014144404
UPDATE_CHANNEL = "https://t.me/YourChannel"

# --- Force Subscribe Config ---
FORCE_SUB_CHANNELS = [
    {
        "name": "Updates Channel",
        "chat_id": "@YourChannel",
        "url": "https://t.me/YourChannel",
    }
]

# Folder setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, "upload_bots")
IROTECH_DIR = os.path.join(BASE_DIR, "database_store")
DATABASE_PATH = os.path.join(IROTECH_DIR, "nebulahost.db")

# File upload limits
FREE_USER_LIMIT = 3
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float("inf")

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

# ─── TELEGRAM CUSTOM EMOJIS MAPPING ────────────────────────────────────────
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
    "star": "6314235179393096157"
}

def CE(key: str) -> str:
    """Returns official custom Telegram emoji HTML element."""
    emoji_id = EMOJIS.get(key, "6314480331831385997")
    return f'<tg-emoji emoji-id="{emoji_id}">•</tg-emoji>'

# ---------------------------------------------------------------------------
# Bot API 7.0+ colored-button & custom emoji icon compatibility patch
# ---------------------------------------------------------------------------
def _patch_button_style(button_cls):
    _orig_init = button_cls.__init__

    def _new_init(self, *args, style=None, icon_custom_emoji_id=None, **kwargs):
        _orig_init(self, *args, **kwargs)
        self.style = style
        self.icon_custom_emoji_id = icon_custom_emoji_id

    button_cls.__init__ = _new_init

    for dict_method_name in ("to_dict", "to_dic"):
        if hasattr(button_cls, dict_method_name):
            _orig_dict_method = getattr(button_cls, dict_method_name)

            def _new_dict_method(self, _orig=_orig_dict_method):
                d = _orig(self)
                if getattr(self, "style", None):
                    d["style"] = self.style
                if getattr(self, "icon_custom_emoji_id", None):
                    d["icon_custom_emoji_id"] = self.icon_custom_emoji_id
                return d

            setattr(button_cls, dict_method_name, _new_dict_method)

_patch_button_style(types.InlineKeyboardButton)
_patch_button_style(types.KeyboardButton)

def cbtn(text, callback_data=None, url=None, style="primary", icon=None):
    icon_id = EMOJIS.get(icon) if icon else None
    return types.InlineKeyboardButton(text, callback_data=callback_data, url=url, style=style, icon_custom_emoji_id=icon_id)

def rkbtn(text, style="primary", icon=None):
    icon_id = EMOJIS.get(icon) if icon else None
    return types.KeyboardButton(text, style=style, icon_custom_emoji_id=icon_id)
# ---------------------------------------------------------------------------

# --- Data structures ---
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
user_selected_plan = {}

# --- Malware Detection Configuration ---
MALWARE_SIGNATURES = [
    b"MZ", b"\x7fELF", b"\xfe\xed\xfa", b"\xce\xfa\xed\xfe"
]

SUSPICIOUS_KEYWORDS = [
    b"ransomware", b"trojan", b"virus", b"malware",
    b"backdoor", b"exploit", b"keylogger", b"rootkit",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Command Button Layouts (Clean text with colors & icons) ---
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    [("Updates Channel", "primary", "link")],
    [("Upload File", "success", "up"), ("Check Files", "primary", "trader")],
    [("Bot Speed", "primary", "speed"), ("Statistics", "primary", "trader")],
    [("Contact Owner", "success", "support")],
    [("Manual Install", "primary", "power"), ("Help Desk", "primary", "notice")],
]

ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    [("Updates Channel", "primary", "link")],
    [("Upload File", "success", "up"), ("Check Files", "primary", "trader")],
    [("Bot Speed", "primary", "speed"), ("Statistics", "primary", "trader")],
    [("Contact Owner", "success", "support"), ("Admin Panel", "danger", "admin")],
    [("Manual Install", "primary", "power"), ("Help Desk", "primary", "notice")],
]

# --- Database Setup ---
DB_LOCK = threading.Lock()

def init_db():
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, plan_name TEXT, expiry TEXT, warned INTEGER DEFAULT 0, expired_notified INTEGER DEFAULT 0)""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT, status TEXT DEFAULT 'approved',
                      PRIMARY KEY (user_id, file_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS active_users (user_id INTEGER PRIMARY KEY)""")
        c.execute("""CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)""")
        c.execute("""CREATE TABLE IF NOT EXISTS plans
                     (plan_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_limit INTEGER, price TEXT, duration INTEGER, buy_link TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS force_sub_channels
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, chat_id TEXT, url TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_limits (user_id INTEGER PRIMARY KEY, file_limit INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_profiles
                     (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, last_seen TEXT, joined_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS ban_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, reason TEXT, admin_id INTEGER, timestamp TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS sales_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, plan_name TEXT, price TEXT, admin_id INTEGER, timestamp TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY, banned_at TEXT, reason TEXT)""")

        c.execute("SELECT COUNT(*) FROM force_sub_channels")
        if c.fetchone()[0] == 0:
            for ch in FORCE_SUB_CHANNELS:
                c.execute("INSERT INTO force_sub_channels (name, chat_id, url) VALUES (?, ?, ?)",
                          (ch["name"], ch["chat_id"], ch["url"]))

        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('update_channel', ?)", (UPDATE_CHANNEL,))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('faq_text', 'Deploy python or node.js code 24/7 with zero latency.')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('terms_text', 'Malicious bots, root exploit attempts, or fork bombs will result in permanent ban.')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('free_user_limit', ?)", (str(FREE_USER_LIMIT),))
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('bot_off_message', 'System offline for scheduled upgrade.')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('auto_approve_paid', 'false')")
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('contact_owner_username', ?)", (YOUR_USERNAME,))

        c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)

def load_data():
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute("SELECT user_id, plan_name, expiry FROM subscriptions")
        for row in c.fetchall():
            user_id = row[0]
            plan_name = row[1] if len(row) > 2 else "Premium"
            expiry = row[-1]
            try:
                user_subscriptions[user_id] = {"plan_name": plan_name, "expiry": datetime.fromisoformat(expiry)}
            except Exception:
                pass

        c.execute("SELECT user_id, file_name, file_type, COALESCE(status, 'approved') FROM user_files")
        for user_id, file_name, file_type, status in c.fetchall():
            user_files.setdefault(user_id, []).append((file_name, file_type, status))

        c.execute("SELECT user_id FROM active_users")
        active_users.update(uid for (uid,) in c.fetchall())

        c.execute("SELECT user_id FROM admins")
        admin_ids.update(uid for (uid,) in c.fetchall())

        c.execute("SELECT id, name, chat_id, url FROM force_sub_channels")
        rows = c.fetchall()
        if rows:
            FORCE_SUB_CHANNELS.clear()
            for ch_id, name, chat_id, url in rows:
                FORCE_SUB_CHANNELS.append({"db_id": ch_id, "name": name, "chat_id": chat_id, "url": url})

        global UPDATE_CHANNEL
        c.execute("SELECT value FROM bot_settings WHERE key = 'update_channel'")
        row = c.fetchone()
        if row: UPDATE_CHANNEL = row[0]

        c.execute("SELECT key, value FROM bot_settings")
        bot_settings_cache.update(dict(c.fetchall()))

        c.execute("SELECT user_id, file_limit FROM user_limits")
        for uid, lim in c.fetchall():
            user_limit_overrides[uid] = lim

        c.execute("SELECT user_id, name, username, last_seen, joined_at FROM user_profiles")
        for uid, name, uname, last_seen, joined_at in c.fetchall():
            user_profiles[uid] = {"name": name, "username": uname, "last_seen": last_seen, "joined_at": joined_at}

        c.execute("SELECT user_id FROM banned_users")
        banned_users.update(uid for (uid,) in c.fetchall())

        conn.close()
        logger.info("Data loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)

init_db()
load_data()

# --- Database Helper Operations ---
def add_plan_db(name, file_limit, price, duration, buy_link):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO plans (name, file_limit, price, duration, buy_link) VALUES (?, ?, ?, ?, ?)",
                  (name, file_limit, price, duration, buy_link))
        conn.commit()
        conn.close()

def get_all_plans():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT plan_id, name, file_limit, price, duration, buy_link FROM plans")
    plans = c.fetchall()
    conn.close()
    return plans

def get_plan_by_id(plan_id):
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

# --- Security Functions ---
def is_suspicious_file(file_content, file_name):
    file_lower = file_name.lower()
    suspicious_extensions = [".exe", ".dll", ".bat", ".cmd", ".msi", ".bin", ".apk", ".iso"]
    if any(file_lower.endswith(ext) for ext in suspicious_extensions):
        return True, f"Suspicious file extension: {file_name}"
    for signature in MALWARE_SIGNATURES:
        if file_content.startswith(signature):
            return True, "Malware binary signature detected"
    sample_text = file_content[:4096].decode("utf-8", errors="ignore").lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.decode("utf-8") in sample_text:
            return True, f"Dangerous pattern signature found: {keyword.decode('utf-8')}"
    return False, "File safe"

def scan_file_for_malware(file_content, file_name, user_id):
    if user_id == OWNER_ID:
        return True, "Owner bypassed security check"
    is_suspicious, reason = is_suspicious_file(file_content, file_name)
    if is_suspicious:
        return False, f"Security violation: {reason}"
    return True, "File verified safe"

def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

# --- Force Subscribe Helpers ---
def get_unjoined_channels(user_id):
    unjoined = []
    for ch in FORCE_SUB_CHANNELS:
        try:
            member = bot.get_chat_member(ch["chat_id"], user_id)
            if member.status in ("left", "kicked"):
                unjoined.append(ch)
        except Exception as e:
            logger.warning(f"Force-sub check exception: {e}")
    return unjoined

def send_force_sub_prompt(chat_id, unjoined_channels):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in unjoined_channels:
        markup.add(cbtn(ch["name"], url=ch["url"], style="primary", icon="link"))
    markup.add(cbtn("Verify Membership", callback_data="verify_fsub", style="success", icon="done"))
    safe_send(
        chat_id,
        f"{CE('shield')} <b>Channel Membership Required!</b>\n\n"
        f"Please join our verified channels below, then tap Verify Membership to unlock hosting slots.",
        reply_markup=markup
    )

def enforce_force_sub(user_id, chat_id):
    if user_id == OWNER_ID or user_id in admin_ids:
        return True
    unjoined = get_unjoined_channels(user_id)
    if unjoined:
        send_force_sub_prompt(chat_id, unjoined)
        return False
    return True

def get_user_file_limit(user_id):
    if user_id in user_limit_overrides:
        return user_limit_overrides[user_id]
    if user_id == OWNER_ID:
        return OWNER_LIMIT
    if user_id in admin_ids:
        return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]["expiry"] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return get_free_user_limit()

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get("process"):
        try:
            proc = psutil.Process(script_info["process"].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                if "log_file" in script_info and not script_info["log_file"].closed:
                    script_info["log_file"].close()
                bot_scripts.pop(script_key, None)
            return is_running
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
        logger.error(f"Error killing process: {e}")

# --- Module / Package Mapping ---
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
                    f"{CE('notice')} <b>Execution Stopped: Missing Dependency</b>\n\n"
                    f"{CE('link')} <b>File:</b> <code>{file_name}</code>\n"
                    f"{CE('close')} <b>Missing Module:</b> <code>{missing_module}</code>\n"
                    f"{CE('speed')} <b>Required Package:</b> <code>{cmd_text}</code>\n\n"
                    f"<i>Tap below to auto-install this library directly:</i>"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(cbtn(f"Install {pkg_name}", callback_data=f"instmod_{script_owner_id}_{missing_module}_{file_name}", style="success", icon="up"))
                markup.add(cbtn("Terminal Logs", callback_data=f"viewlog_{script_owner_id}_{file_name}", style="primary", icon="logs"))
                safe_send(script_owner_id, error_msg, reply_markup=markup)
            else:
                error_msg = (
                    f"{CE('notice')} <b>Runtime Execution Warning!</b>\n\n"
                    f"{CE('link')} <b>File:</b> <code>{file_name}</code>\n"
                    f"<i>The container process stopped unexpectedly. View terminal logs below:</i>"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(cbtn("Terminal Logs", callback_data=f"viewlog_{script_owner_id}_{file_name}", style="primary", icon="logs"))
                safe_send(script_owner_id, error_msg, reply_markup=markup)
        except Exception as e:
            logger.error(f"Error checking log file: {e}")

def safe_next_step(msg, callback):
    def wrapper(message):
        text = message.text or ""
        user_id = message.from_user.id
        if text in BUTTON_MAPPING or text.startswith("/"):
            if is_banned(user_id):
                safe_send(message.chat.id, f"{CE('notice')} <b>You are restricted from using this bot.</b>")
                return
            if bot_locked and user_id not in admin_ids:
                safe_send(message.chat.id, get_bot_off_message())
                return
            if text == "/start":
                _logic_send_welcome(message)
            elif text == "/plans":
                if enforce_force_sub(user_id, message.chat.id):
                    _logic_view_plans(message)
            elif text == "/checkfiles":
                if enforce_force_sub(user_id, message.chat.id):
                    _logic_check_files(message)
            elif text in BUTTON_MAPPING:
                if enforce_force_sub(user_id, message.chat.id):
                    touch_last_seen(user_id)
                    BUTTON_MAPPING[text](message)
            return
        callback(message)
    bot.register_next_step_handler(msg, wrapper)

def notify_admin_log(text):
    for aid in admin_ids | {OWNER_ID}:
        try: safe_send(aid, text)
        except Exception: pass

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, "w", encoding="utf-8", errors="ignore")
        script_env = os.environ.copy()
        script_env["PORT"] = str(get_free_port())
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            env=script_env,
        )

        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "script_owner_id": script_owner_id,
            "start_time": datetime.now(),
            "user_folder": user_folder,
            "type": "py",
            "script_key": script_key,
        }

        safe_send(
            script_owner_id,
            f"{CE('done')} <b>Python Script Online:</b> <code>{file_name}</code> (PID: <code>{process.pid}</code>)"
        )
        notify_admin_log(
            f"{CE('power')} <b>Worker Container Started</b>\n\n"
            f"{CE('trader')} <b>User:</b> <code>{script_owner_id}</code>\n"
            f"{CE('link')} <b>File:</b> <code>{file_name}</code>\n"
            f"{CE('date')} <b>Time:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
        )
        threading.Thread(
            target=monitor_and_guide_error,
            args=(process, log_file_path, script_owner_id, file_name, message_obj_for_reply)
        ).start()
    except Exception as e:
        safe_send(script_owner_id, f"{CE('close')} <b>Process Failure:</b> <code>{str(e)}</code>")

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, "w", encoding="utf-8", errors="ignore")
        script_env = os.environ.copy()
        script_env["PORT"] = str(get_free_port())
        process = subprocess.Popen(
            ["node", script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            env=script_env,
        )

        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "script_owner_id": script_owner_id,
            "start_time": datetime.now(),
            "user_folder": user_folder,
            "type": "js",
            "script_key": script_key,
        }

        safe_send(
            script_owner_id,
            f"{CE('done')} <b>Node.js Script Online:</b> <code>{file_name}</code> (PID: <code>{process.pid}</code>)"
        )
        notify_admin_log(
            f"{CE('power')} <b>Worker Container Started</b>\n\n"
            f"{CE('trader')} <b>User:</b> <code>{script_owner_id}</code>\n"
            f"{CE('link')} <b>File:</b> <code>{file_name}</code>\n"
            f"{CE('date')} <b>Time:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
        )
        threading.Thread(
            target=monitor_and_guide_error,
            args=(process, log_file_path, script_owner_id, file_name, message_obj_for_reply)
        ).start()
    except Exception as e:
        safe_send(script_owner_id, f"{CE('close')} <b>Process Failure:</b> <code>{str(e)}</code>")

def save_user_file(user_id, file_name, file_type="py", status="approved"):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO user_files (user_id, file_name, file_type, status) VALUES (?, ?, ?, ?)",
                  (user_id, file_name, file_type, status))
        conn.commit()
        conn.close()
        user_files.setdefault(user_id, [])
        user_files[user_id] = [(fn, ft, st) for fn, ft, st in user_files[user_id] if fn != file_name]
        user_files[user_id].append((file_name, file_type, status))

def update_file_status_db(user_id, file_name, status):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("UPDATE user_files SET status=? WHERE user_id=? AND file_name=?", (status, user_id, file_name))
        conn.commit()
        conn.close()
        if user_id in user_files:
            user_files[user_id] = [(fn, ft, status) if fn == file_name else (fn, ft, st) for fn, ft, st in user_files[user_id]]

def get_file_record(user_id, file_name):
    for fn, ft, st in user_files.get(user_id, []):
        if fn == file_name:
            return ft, st
    return None, None

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
        c.execute("INSERT OR REPLACE INTO subscriptions (user_id, plan_name, expiry, warned, expired_notified) VALUES (?, ?, ?, 0, 0)",
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

def add_force_sub_channel_db(name, chat_id, url):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO force_sub_channels (name, chat_id, url) VALUES (?, ?, ?)", (name, chat_id, url))
        new_id = c.lastrowid
        conn.commit()
        conn.close()
        FORCE_SUB_CHANNELS.append({"db_id": new_id, "name": name, "chat_id": chat_id, "url": url})

def remove_force_sub_channel_db(db_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM force_sub_channels WHERE id = ?", (db_id,))
        conn.commit()
        conn.close()
        FORCE_SUB_CHANNELS[:] = [ch for ch in FORCE_SUB_CHANNELS if ch.get("db_id") != db_id]

def set_update_channel_db(new_link):
    global UPDATE_CHANNEL
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES ('update_channel', ?)", (new_link,))
        conn.commit()
        conn.close()
        UPDATE_CHANNEL = new_link

def get_setting(key, default=""):
    return bot_settings_cache.get(key, default)

def set_setting(key, value):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
        bot_settings_cache[key] = value

def get_faq_text():
    return f"{CE('notice')} <b>FREQUENTLY ASKED QUESTIONS</b>\n\n{get_setting('faq_text', 'Deploy 24/7 bots with isolated resource allocations.')}"

def get_terms_text():
    return f"{CE('shield')} <b>TERMS & CONDITIONS</b>\n\n{get_setting('terms_text', 'Abusive scripts and unauthorized scrapers are prohibited.')}"

def get_free_user_limit():
    try: return int(get_setting("free_user_limit", str(FREE_USER_LIMIT)))
    except Exception: return FREE_USER_LIMIT

def get_bot_off_message():
    return get_setting("bot_off_message", f"{CE('notice')} <b>Server Maintenance Active. Try again later.</b>")

def is_auto_approve_paid_enabled():
    return get_setting("auto_approve_paid", "false") == "true"

def get_contact_owner_username():
    return get_setting("contact_owner_username", YOUR_USERNAME)

def has_active_subscription(user_id):
    return user_id in user_subscriptions and user_subscriptions[user_id]["expiry"] > datetime.now()

def set_user_limit_override(user_id, limit):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO user_limits (user_id, file_limit) VALUES (?, ?)", (user_id, limit))
        conn.commit()
        conn.close()
        user_limit_overrides[user_id] = limit

def remove_user_limit_override(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM user_limits WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        user_limit_overrides.pop(user_id, None)

def ban_user_db(user_id, reason=None, admin_id=None):
    now = datetime.now().isoformat()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO banned_users (user_id, banned_at, reason) VALUES (?, ?, ?)", (user_id, now, reason))
        c.execute("INSERT INTO ban_log (user_id, action, reason, admin_id, timestamp) VALUES (?, 'ban', ?, ?, ?)", (user_id, reason, admin_id, now))
        conn.commit()
        conn.close()
        banned_users.add(user_id)

def unban_user_db(user_id, admin_id=None):
    now = datetime.now().isoformat()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
        c.execute("INSERT INTO ban_log (user_id, action, reason, admin_id, timestamp) VALUES (?, 'unban', NULL, ?, ?)", (user_id, admin_id, now))
        conn.commit()
        conn.close()
        banned_users.discard(user_id)

def get_ban_log(user_id=None, limit=20):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    if user_id is not None:
        c.execute("SELECT user_id, action, reason, admin_id, timestamp FROM ban_log WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    else:
        c.execute("SELECT user_id, action, reason, admin_id, timestamp FROM ban_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def log_sale(user_id, plan_name, price, admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO sales_log (user_id, plan_name, price, admin_id, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (user_id, plan_name, price, admin_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()

def get_sales_log(limit=200):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT user_id, plan_name, price, admin_id, timestamp FROM sales_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def is_banned(user_id):
    return user_id in banned_users and user_id != OWNER_ID

def save_user_profile(user_id, name, username):
    now = datetime.now().isoformat()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT joined_at FROM user_profiles WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        joined_at = row[0] if row and row[0] else now
        c.execute("INSERT OR REPLACE INTO user_profiles (user_id, name, username, last_seen, joined_at) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, username, now, joined_at))
        conn.commit()
        conn.close()
        user_profiles[user_id] = {"name": name, "username": username, "last_seen": now, "joined_at": joined_at}

def touch_last_seen(user_id):
    if user_id not in user_profiles: return
    now = datetime.now().isoformat()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("UPDATE user_profiles SET last_seen = ? WHERE user_id = ?", (now, user_id))
        conn.commit()
        conn.close()
        user_profiles[user_id]["last_seen"] = now

def add_admin_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        admin_ids.add(user_id)

def remove_admin_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        admin_ids.discard(user_id)

# --- Clean Keyboards (No Raw Emojis) ---
def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row in layout:
        row_btns = [rkbtn(txt, style=st, icon=ic) for txt, st, ic in row]
        markup.add(*row_btns)
    return markup

def create_admin_panel_inline():
    pending_count = sum(1 for files in user_files.values() for _, _, st in files if st == "pending")
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
        cbtn("Message One User", callback_data="broadcast_one_init", style="primary", icon="sms"),
    )
    markup.add(
        cbtn("Lock / Unlock", callback_data="toggle_lock", style="primary", icon="power"),
    )
    markup.add(
        cbtn("Run All Scripts", callback_data="run_all_scripts", style="primary", icon="play"),
        cbtn("Bot Stats", callback_data="stats", style="primary", icon="trader"),
    )
    markup.add(
        cbtn("Add Force Channel", callback_data="add_force_channel", style="success", icon="link"),
        cbtn("Manage Force Channels", callback_data="manage_force_channels", style="danger", icon="delete"),
    )
    markup.add(
        cbtn("Change Update Channel", callback_data="change_update_channel", style="primary", icon="link"),
    )
    markup.add(
        cbtn("Change Owner Username", callback_data="change_owner_username_init", style="primary", icon="support"),
    )
    markup.add(
        cbtn("All Users", callback_data="all_users", style="primary", icon="trader"),
        cbtn("Check User", callback_data="check_user_init", style="primary", icon="search"),
    )
    markup.add(
        cbtn("Ban User", callback_data="ban_user_init", style="danger", icon="delete"),
        cbtn("Unban User", callback_data="unban_user_init", style="success", icon="done"),
    )
    markup.add(
        cbtn("Ban Log", callback_data="ban_log_init", style="primary", icon="logs"),
    )
    markup.add(
        cbtn("Bulk Delete", callback_data="bulk_delete_init", style="danger", icon="delete"),
        cbtn("Bulk Approve", callback_data="bulk_approve", style="success", icon="done"),
    )
    markup.add(
        cbtn(f"Pending Approvals ({pending_count})", callback_data="pending_approvals", style="primary", icon="loading"),
    )
    markup.add(
        cbtn("All Files", callback_data="all_files", style="primary", icon="trader"),
        cbtn("Running Bots", callback_data="running_bots", style="primary", icon="play"),
    )
    markup.add(
        cbtn("Stop All Bots", callback_data="stop_all_bots", style="danger", icon="stop"),
    )
    markup.add(
        cbtn("Growth Stats", callback_data="growth_stats", style="primary", icon="trader"),
        cbtn("Inactive Users", callback_data="inactive_users", style="primary", icon="notice"),
    )
    markup.add(
        cbtn("Revenue Report", callback_data="revenue_report", style="primary", icon="money"),
    )
    markup.add(
        cbtn("Edit FAQ", callback_data="edit_faq_init", style="primary", icon="notice"),
        cbtn("Edit Terms", callback_data="edit_terms_init", style="primary", icon="logs"),
    )
    markup.add(
        cbtn("Edit Bot Off Message", callback_data="edit_bot_off_msg_init", style="primary", icon="notice"),
    )
    markup.add(
        cbtn(f"Auto-Approve Paid: {'ON' if is_auto_approve_paid_enabled() else 'OFF'}",
             callback_data="toggle_auto_approve_paid", style="success" if is_auto_approve_paid_enabled() else "danger", icon="done"),
    )
    markup.add(
        cbtn("Change Free Limit", callback_data="change_free_limit_init", style="primary", icon="power"),
    )
    markup.add(
        cbtn("Set User File Limit", callback_data="set_user_limit_init", style="primary", icon="power"),
    )
    return markup

def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    if is_banned(user_id):
        safe_send(chat_id, f"{CE('notice')} <b>You are restricted from using this bot.</b>")
        return

    if bot_locked and user_id not in admin_ids:
        safe_send(chat_id, get_bot_off_message())
        return

    if not enforce_force_sub(user_id, chat_id):
        return

    _send_actual_welcome(user_id, chat_id, user_name, username)

def get_user_status_line(user_id):
    if user_id == OWNER_ID:
        return "Root Administrator"
    elif user_id in admin_ids:
        return "Authorized Admin"
    elif user_id in user_subscriptions and user_subscriptions[user_id]["expiry"] > datetime.now():
        sub = user_subscriptions[user_id]
        days_left = (sub["expiry"] - datetime.now()).days
        return f"{sub.get('plan_name', 'Premium')} ({days_left} Days remaining)"
    else:
        return "Free Tier Account"

def _send_actual_welcome(user_id, chat_id, user_name, username):
    is_new_user = user_id not in active_users
    save_user_profile(user_id, user_name, username)
    if is_new_user:
        add_active_user(user_id)
        now = datetime.now()
        notify_admin_log(
            f"{CE('sparkle')} <b>New User Registered!</b>\n\n"
            f"{CE('trader')} <b>Name:</b> {html.escape(user_name or 'Unknown')}\n"
            f"{CE('telegram')} <b>Username:</b> @{username or 'N/A'}\n"
            f"{CE('link')} <b>User ID:</b> <code>{user_id}</code>\n"
            f"{CE('date')} <b>Date:</b> <code>{now.strftime('%Y-%m-%d %H:%M:%S')}</code>"
        )

    status_line = get_user_status_line(user_id)
    welcome_msg = (
        f"{CE('crown')} <b>NEBULA CLOUD HOSTING ENGINE</b> {CE('fire')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('trader')} <b>Holder:</b> <code>{html.escape(user_name or 'User')}</code>\n"
        f"{CE('link')} <b>Account ID:</b> <code>{user_id}</code>\n"
        f"{CE('shield')} <b>Authority:</b> <code>{status_line}</code>\n"
        f"{CE('power')} <b>Allocated Slots:</b> <code>{get_user_file_count(user_id)} / {get_user_file_limit(user_id)}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('speed')} <i>High-performance subprocess execution for Python and Node.js.</i>\n"
        f"<i>Select an option below to initiate actions:</i>"
    )
    safe_send(chat_id, welcome_msg, reply_markup=create_reply_keyboard_main_menu(user_id))

def _logic_view_plans(message_or_call):
    chat_id = message_or_call.chat.id if isinstance(message_or_call, telebot.types.Message) else message_or_call.message.chat.id
    plans = get_all_plans()

    if not plans:
        safe_send(chat_id, f"{CE('notice')} <b>No active plans found.</b>")
        return

    safe_send(chat_id, f"{CE('diamond')} <b>AVAILABLE SUBSCRIPTION PACKAGES:</b>")
    for plan in plans:
        plan_id, name, limit, price, duration, buy_link = plan
        card_text = (
            f"{CE('crown')} <b>Tier:</b> <code>{name}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"{CE('power')} <b>Quota:</b> <code>{limit} Bots</code>\n"
            f"{CE('date')} <b>Duration:</b> <code>{duration} Days</code>\n"
            f"{CE('money')} <b>Price:</b> <code>{price}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Payment Methods: bKash, Nagad, Binance Pay</i>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(cbtn("Contact Owner to Purchase", url=f"https://t.me/{get_contact_owner_username().lstrip('@')}", style="success", icon="support"))
        safe_send(chat_id, card_text, reply_markup=markup)

def _logic_upload_file(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        safe_send(message.chat.id, get_bot_off_message())
        return

    current_count = get_user_file_count(user_id)
    limit = get_user_file_limit(user_id)

    if current_count >= limit:
        markup = types.InlineKeyboardMarkup()
        markup.add(cbtn("View Plans & Upgrade", callback_data="view_plans_cb", style="primary", icon="diamond"))
        safe_send(
            message.chat.id,
            f"{CE('close')} <b>Container Quota Exhausted ({current_count}/{limit})!</b>\n\nUpgrade your tier to deploy more instances.",
            reply_markup=markup
        )
        return

    safe_send(
        message.chat.id,
        f"{CE('up')} <b>Send your Python (.py), Node.js (.js), or ZIP archive document.</b>\n\n"
        f"<i>All files are verified by our security engine before running.</i>"
    )

def _build_global_file_chunks(filter_running_only=False, chunk_size=20):
    items = []
    for owner_id, files in user_files.items():
        for fname, ftype, status in files:
            if filter_running_only and not (status == "approved" and is_bot_running(owner_id, fname)):
                continue
            items.append((owner_id, fname, ftype, status))
    items.sort(key=lambda x: (x[0], x[1]))
    if not items: return []
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

def _build_check_files_chunks(user_id, chunk_size=25):
    user_files_list = sorted(user_files.get(user_id, []))
    if not user_files_list: return []
    return [user_files_list[i : i + chunk_size] for i in range(0, len(user_files_list), chunk_size)]

def _build_check_files_view(user_id, files_chunk=None, page=1, total_pages=1):
    if files_chunk is None:
        chunks = _build_check_files_chunks(user_id)
        if not chunks:
            return f"{CE('trader')} <b>Your Files:</b>\n\n<i>(No instances deployed yet)</i>", None
        files_chunk = chunks[0]
        total_pages = len(chunks)

    header = f"{CE('trader')} <b>Deployed Instances:</b>"
    if total_pages > 1:
        header += f" (Page {page}/{total_pages})"
    lines = [header + "\n"]

    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type, status in files_chunk:
        is_running = (status == "approved" and is_bot_running(user_id, file_name))
        run_st = "ONLINE" if is_running else "STOPPED"
        icon_k = "done" if is_running else "close"
        st_style = "success" if is_running else "danger"

        btn_text = f"[{run_st}] {file_name} ({file_type})"
        markup.add(cbtn(btn_text, callback_data=f"file_{user_id}_{file_name}", style=st_style, icon=icon_k))
    return "\n".join(lines), markup

def _logic_check_files(message):
    user_id = message.from_user.id
    chunks = _build_check_files_chunks(user_id)
    if not chunks:
        safe_send(message.chat.id, f"{CE('trader')} <b>Your Files:</b>\n\n<i>(No instances deployed yet)</i>")
        return
    for i, chunk in enumerate(chunks, 1):
        text, markup = _build_check_files_view(user_id, files_chunk=chunk, page=i, total_pages=len(chunks))
        safe_send(message.chat.id, text, reply_markup=markup)

# --- Document Upload Processing ---
@bot.message_handler(content_types=["document"])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document

    if is_banned(user_id):
        safe_send(chat_id, f"{CE('notice')} <b>You are restricted from using this bot.</b>")
        return

    if bot_locked and user_id not in admin_ids:
        safe_send(chat_id, get_bot_off_message())
        return

    if not enforce_force_sub(user_id, chat_id):
        return

    is_privileged = user_id == OWNER_ID or user_id in admin_ids
    is_paid_auto_approved = not is_privileged and is_auto_approve_paid_enabled() and has_active_subscription(user_id)

    if not is_privileged:
        current_count = get_user_file_count(user_id)
        limit = get_user_file_limit(user_id)
        if current_count >= limit:
            safe_send(chat_id, f"{CE('close')} <b>Container Quota Full ({current_count}/{limit})!</b> Upgrade plan first.")
            return

    file_name = doc.file_name
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in [".py", ".js", ".zip"]:
        safe_send(chat_id, f"{CE('notice')} <b>Only .py, .js, and .zip files are supported.</b>")
        return

    TELEGRAM_DOWNLOAD_LIMIT = 20 * 1024 * 1024
    if doc.file_size and doc.file_size > TELEGRAM_DOWNLOAD_LIMIT:
        safe_send(chat_id, f"{CE('notice')} <b>File exceeds 20 MB limit.</b>")
        return

    try:
        download_wait_msg = bot.reply_to(message, f"{CE('loading')} <i>Step 1/2: Processing & Allocating Container...</i>", parse_mode="HTML")
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)

        if user_id != OWNER_ID:
            is_safe, reason = scan_file_for_malware(downloaded_file_content, file_name, user_id)
            if not is_safe:
                bot.edit_message_text(f"{CE('close')} <b>Security Violation:</b> {reason}", chat_id, download_wait_msg.message_id, parse_mode="HTML")
                return

        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        with open(file_path, "wb") as f:
            f.write(downloaded_file_content)

        file_type = "js" if file_ext == ".js" else "py"

        if is_privileged or is_paid_auto_approved:
            bot.edit_message_text(f"{CE('done')} <b>File {file_name} provisioned & launched!</b>", chat_id, download_wait_msg.message_id, parse_mode="HTML")
            save_user_file(user_id, file_name, file_type, "approved")
            if file_ext == ".js":
                threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
            elif file_ext == ".py":
                threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, message)).start()
        else:
            save_user_file(user_id, file_name, file_type, "pending")
            bot.edit_message_text(
                f"{CE('done')} <b>Script {file_name} Uploaded Successfully!</b>\n\n"
                f"{CE('loading')} <b>Status:</b> <code>PENDING APPROVAL</code>\n"
                f"<i>Our administrative desk has been notified for launch authorization.</i>",
                chat_id, download_wait_msg.message_id, parse_mode="HTML"
            )

            review_markup = types.InlineKeyboardMarkup(row_width=2)
            review_markup.add(
                cbtn("Approve", callback_data=f"approve_{user_id}_{file_name}", style="success", icon="done"),
                cbtn("Reject", callback_data=f"reject_{user_id}_{file_name}", style="danger", icon="close")
            )
            review_text = (
                f"{CE('notice')} <b>NEW CONTAINER APPROVAL REQUIRED</b>\n\n"
                f"{CE('trader')} <b>User:</b> <code>{user_id}</code>\n"
                f"{CE('link')} <b>File:</b> <code>{file_name}</code> ({file_type})"
            )
            for aid in admin_ids | {OWNER_ID}:
                try: safe_send(aid, review_text, reply_markup=review_markup)
                except Exception: pass
    except Exception as e:
        safe_send(chat_id, f"{CE('close')} <b>Upload Error:</b> <code>{str(e)}</code>")

# --- Callback Routing ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global bot_locked
    user_id = call.from_user.id
    data = call.data
    chat_id = call.message.chat.id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "Access restricted.", show_alert=True)
        return

    if bot_locked and user_id not in admin_ids:
        bot.answer_callback_query(call.id, "System offline.", show_alert=True)
        return

    if data == "verify_fsub":
        unjoined = [] if (user_id == OWNER_ID or user_id in admin_ids) else get_unjoined_channels(user_id)
        if unjoined:
            bot.answer_callback_query(call.id, "Please join all required channels first!", show_alert=True)
            return
        bot.answer_callback_query(call.id, "Verified!")
        try: bot.delete_message(chat_id, call.message.message_id)
        except Exception: pass
        _send_actual_welcome(user_id, chat_id, call.from_user.first_name, call.from_user.username)
        return

    if not enforce_force_sub(user_id, chat_id):
        bot.answer_callback_query(call.id, "Channel membership mandatory.", show_alert=True)
        return

    if data == "view_plans_cb":
        bot.answer_callback_query(call.id)
        _logic_view_plans(call)

    elif data == "help_faq":
        bot.answer_callback_query(call.id)
        safe_send(chat_id, get_faq_text())

    elif data == "help_terms":
        bot.answer_callback_query(call.id)
        safe_send(chat_id, get_terms_text())

    elif data == "write_message_init":
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('sms')} <b>Type your technical message:</b>")
        safe_next_step(msg, process_write_message)

    elif data.startswith("instmod_"):
        _, owner_id, mod_name, fname = data.split("_", 3)
        if user_id != int(owner_id) and user_id not in admin_ids:
            return bot.answer_callback_query(call.id, "Unauthorized.", show_alert=True)

        bot.answer_callback_query(call.id)
        pkg_name = TELEGRAM_MODULES.get(mod_name.lower(), mod_name)
        ext = os.path.splitext(fname)[1].lower()

        status_msg = safe_send(chat_id, f"{CE('loading')} <i>Installing package:</i> <code>{pkg_name}</code>...")

        def do_pip_install():
            cmd = ["npm", "install", pkg_name] if ext == ".js" else [sys.executable, "-m", "pip", "install", "--user", pkg_name]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                bot.edit_message_text(f"{CE('done')} <b>Package <code>{pkg_name}</code> installed!</b> Rebooting...", chat_id, status_msg.message_id, parse_mode="HTML")
                time.sleep(1)
                ufolder = get_user_folder(int(owner_id))
                fpath = os.path.join(ufolder, fname)
                if ext == ".js": run_js_script(fpath, int(owner_id), ufolder, fname, call.message)
                else: run_script(fpath, int(owner_id), ufolder, fname, call.message)
            else:
                bot.edit_message_text(f"{CE('close')} <b>Install Failed:</b>\n<pre>{res.stderr[:250]}</pre>", chat_id, status_msg.message_id, parse_mode="HTML")

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

    # --- Admin Callbacks ---
    elif data == "add_plan_init" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('sms')} <b>Send Plan Configuration:</b>\n<code>Name | Limit | Price | Days | BuyLink</code>")
        safe_next_step(msg, process_add_plan)

    elif data == "manage_plans" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        plans = get_all_plans()
        if not plans:
            safe_send(chat_id, f"{CE('notice')} <b>No active plans.</b>")
            return
        markup = types.InlineKeyboardMarkup()
        for p in plans:
            markup.add(cbtn(f"Delete {p[1]}", callback_data=f"del_plan_{p[0]}", style="danger", icon="delete"))
        safe_send(chat_id, f"{CE('delete')} <b>Select Plan to Delete:</b>", reply_markup=markup)

    elif data.startswith("del_plan_") and user_id in admin_ids:
        pid = int(data.split("_")[2])
        delete_plan_db(pid)
        bot.answer_callback_query(call.id, "Plan Purged!")
        safe_send(chat_id, f"{CE('done')} <b>Plan removed from database.</b>")

    elif data == "add_subscription" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        msg = safe_send(chat_id, f"{CE('diamond')} <b>Enter User ID or @username to grant tier:</b>")
        safe_next_step(msg, process_add_subscription_target)

    elif data.startswith("grantsub_") and user_id in admin_ids:
        _, target_uid, plan_id = data.split("_", 2)
        target_uid, plan_id = int(target_uid), int(plan_id)
        plan = get_plan_by_id(plan_id)
        if not plan: return bot.answer_callback_query(call.id, "Plan missing.")
        _, pname, limit, price, duration, _ = plan
        exp = datetime.now() + timedelta(days=duration)
        save_subscription(target_uid, pname, exp)
        set_user_limit_override(target_uid, limit)
        log_sale(target_uid, pname, price, user_id)
        bot.answer_callback_query(call.id, "Granted!")
        safe_send(chat_id, f"{CE('done')} <b>Plan <code>{pname}</code> activated for User <code>{target_uid}</code> ({duration}d).</b>")

    elif data == "toggle_lock" and user_id in admin_ids:
        bot_locked = not bot_locked
        bot.answer_callback_query(call.id, f"Lock State: {bot_locked}")
        safe_send(chat_id, f"{CE('power')} <b>Lock State Updated:</b> <code>{bot_locked}</code>")

    # --- File Management Callbacks ---
    elif data.startswith("file_"):
        _, owner_id, fname = data.split("_", 2)
        owner_id = int(owner_id)
        file_type, status = get_file_record(owner_id, fname)
        if file_type is None:
            return bot.answer_callback_query(call.id, "File missing.", show_alert=True)

        is_running = status == "approved" and is_bot_running(owner_id, fname)
        st_text = f"{CE('done')} ONLINE & RUNNING" if is_running else f"{CE('close')} STOPPED"

        card_text = (
            f"{CE('diamond')} <b>CONTAINER CONTROLLER #{fname}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{CE('link')} <b>Runtime:</b> <code>{file_type.upper()}</code>\n"
            f"{CE('trader')} <b>User:</b> <code>{owner_id}</code>\n"
            f"{CE('speed')} <b>Status:</b> {st_text}"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        if is_running:
            markup.add(
                cbtn("Stop Process", callback_data=f"stop_{owner_id}_{fname}", style="danger", icon="stop"),
                cbtn("Delete Worker", callback_data=f"del_{owner_id}_{fname}", style="danger", icon="delete")
            )
        else:
            markup.add(
                cbtn("Start Process", callback_data=f"start_{owner_id}_{fname}", style="success", icon="play"),
                cbtn("Delete Worker", callback_data=f"del_{owner_id}_{fname}", style="danger", icon="delete")
            )
        markup.add(cbtn("Terminal Logs", callback_data=f"viewlog_{owner_id}_{fname}", style="primary", icon="logs"))
        if user_id in admin_ids:
            markup.add(cbtn("Download Archive", callback_data=f"download_{owner_id}_{fname}", style="success", icon="download"))
        markup.add(cbtn("Back to Files", callback_data=f"backfiles_{owner_id}", style="primary", icon="arrow_right"))

        bot.answer_callback_query(call.id)
        safe_send(chat_id, card_text, reply_markup=markup)

    elif data.startswith("start_"):
        _, owner_id, fname = data.split("_", 2)
        owner_id = int(owner_id)
        fpath = os.path.join(get_user_folder(owner_id), fname)
        ftype, status = get_file_record(owner_id, fname)
        if status != "approved":
            return bot.answer_callback_query(call.id, "Awaiting approval.", show_alert=True)
        if is_bot_running(owner_id, fname):
            return bot.answer_callback_query(call.id, "Already active.")

        bot.answer_callback_query(call.id, "Starting...")
        if ftype == "js": threading.Thread(target=run_js_script, args=(fpath, owner_id, get_user_folder(owner_id), fname, call.message)).start()
        else: threading.Thread(target=run_script, args=(fpath, owner_id, get_user_folder(owner_id), fname, call.message)).start()

    elif data.startswith("stop_"):
        _, owner_id, fname = data.split("_", 2)
        skey = f"{owner_id}_{fname}"
        if skey in bot_scripts:
            kill_process_tree(bot_scripts[skey])
            bot_scripts.pop(skey, None)
        bot.answer_callback_query(call.id, "Terminated.")
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
        bot.answer_callback_query(call.id, "Deleted.")
        safe_send(chat_id, f"{CE('delete')} <b>Container <code>{fname}</code> purged.</b>")

    elif data.startswith("approve_"):
        if user_id not in admin_ids and user_id != OWNER_ID: return
        _, owner_id, fname = data.split("_", 2)
        owner_id = int(owner_id)
        update_file_status_db(owner_id, fname, "approved")
        bot.answer_callback_query(call.id, "Approved!")
        fpath = os.path.join(get_user_folder(owner_id), fname)
        threading.Thread(target=run_script, args=(fpath, owner_id, get_user_folder(owner_id), fname, call.message)).start()

    elif data.startswith("reject_"):
        if user_id not in admin_ids and user_id != OWNER_ID: return
        _, owner_id, fname = data.split("_", 2)
        owner_id = int(owner_id)
        remove_user_file_db(owner_id, fname)
        bot.answer_callback_query(call.id, "Rejected.")
        safe_send(chat_id, f"{CE('close')} <b>File <code>{fname}</code> rejected.</b>")

    elif data.startswith("download_") and user_id in admin_ids:
        _, owner_id, fname = data.split("_", 2)
        fpath = os.path.join(get_user_folder(int(owner_id)), fname)
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                bot.send_document(chat_id, f, caption=f"{CE('done')} <b>Backup Archive for {fname}</b>", parse_mode="HTML")

    elif data.startswith("backfiles_"):
        _, owner_id = data.split("_", 1)
        _logic_check_files(call.message)

    elif data == "all_files" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        chunks = _build_global_file_chunks(filter_running_only=False)
        for chunk in chunks:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for owner_id, fname, ftype, status in chunk:
                running = (status == "approved" and is_bot_running(owner_id, fname))
                st_icon = "done" if running else "close"
                markup.add(cbtn(f"{fname} ({owner_id})", callback_data=f"file_{owner_id}_{fname}", style="primary", icon=st_icon))
            safe_send(chat_id, f"{CE('trader')} <b>System Deployed Containers:</b>", reply_markup=markup)

    elif data == "running_bots" and user_id in admin_ids:
        bot.answer_callback_query(call.id)
        chunks = _build_global_file_chunks(filter_running_only=True)
        for chunk in chunks:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for owner_id, fname, ftype, status in chunk:
                markup.add(cbtn(f"{fname} ({owner_id})", callback_data=f"file_{owner_id}_{fname}", style="success", icon="play"))
            safe_send(chat_id, f"{CE('done')} <b>Running Containers:</b>", reply_markup=markup)

    elif data == "stop_all_bots" and user_id in admin_ids:
        bot.answer_callback_query(call.id, "Stopping all...")
        stopped = len(bot_scripts)
        for skey in list(bot_scripts.keys()):
            kill_process_tree(bot_scripts[skey])
            bot_scripts.pop(skey, None)
        safe_send(chat_id, f"{CE('stop')} <b>Terminated <code>{stopped}</code> active instances.</b>")

# --- Step Handlers ---
def process_add_plan(message):
    try:
        parts = [p.strip() for p in message.text.split("|")]
        name, limit, price, duration, buy_link = parts[0], int(parts[1]), parts[2], int(parts[3]), parts[4]
        add_plan_db(name, limit, price, duration, buy_link)
        safe_send(message.chat.id, f"{CE('done')} <b>Plan <code>{name}</code> created successfully!</b>")
    except Exception as e:
        safe_send(message.chat.id, f"{CE('close')} <b>Invalid Format:</b> <code>{e}</code>")

def process_write_message(message):
    user_id = message.from_user.id
    header = f"{CE('sms')} <b>Support Ticket Relay</b>\n\n{CE('trader')} <b>User:</b> <code>{user_id}</code>"
    for aid in admin_ids | {OWNER_ID}:
        try:
            safe_send(aid, header)
            bot.copy_message(aid, message.chat.id, message.message_id)
        except Exception: pass
    safe_send(message.chat.id, f"{CE('done')} <b>Message transmitted to support.</b>")

def process_add_subscription_target(message):
    identifier = message.text.strip()
    uid = resolve_user_identifier(identifier) or (int(identifier) if identifier.isdigit() else None)
    if not uid: return safe_send(message.chat.id, f"{CE('close')} <b>User not found.</b>")
    plans = get_all_plans()
    markup = types.InlineKeyboardMarkup(row_width=1)
    for plan_id, name, limit, price, duration, _ in plans:
        markup.add(cbtn(f"{name} ({limit} slots, {duration}d)", callback_data=f"grantsub_{uid}_{plan_id}", style="primary", icon="diamond"))
    safe_send(message.chat.id, f"{CE('diamond')} <b>Select tier to grant:</b>", reply_markup=markup)

def process_manual_install(message):
    pkg_input = message.text.strip()
    status_msg = safe_send(message.chat.id, f"{CE('loading')} <i>Installing package:</i> <code>{pkg_input}</code>...")
    cmd = ["npm", "install", "-g", pkg_input[4:]] if pkg_input.startswith("npm:") else [sys.executable, "-m", "pip", "install", "--user", pkg_input]

    def run_install():
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode == 0:
            bot.edit_message_text(f"{CE('done')} <b><code>{pkg_input}</code> installed successfully.</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text(f"{CE('close')} <b>Installation Failed.</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
    threading.Thread(target=run_install).start()

def _logic_manual_install(message):
    msg = safe_send(message.chat.id, f"{CE('power')} <b>Send library name to install:</b>\n<i>(e.g. requests, telebot, or npm:express)</i>")
    safe_next_step(msg, process_manual_install)

def _logic_help(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(cbtn("Write Message", callback_data="write_message_init", style="primary", icon="sms"))
    markup.row(
        cbtn("FAQ", callback_data="help_faq", style="primary", icon="notice"),
        cbtn("Terms", callback_data="help_terms", style="primary", icon="logs")
    )
    safe_send(message.chat.id, f"{CE('support')} <b>Customer Helpdesk</b>", reply_markup=markup)

def _logic_updates_channel(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(cbtn("Updates Channel", url=UPDATE_CHANNEL, style="primary", icon="link"))
    safe_send(message.chat.id, f"{CE('link')} <b>Official Transmission Channel</b>", reply_markup=markup)

def _logic_bot_speed(message):
    user_id = message.from_user.id
    start = time.time()
    try: bot.get_me()
    except Exception: pass
    latency = round((time.time() - start) * 1000, 2)
    safe_send(
        message.chat.id,
        f"{CE('speed')} <b>SERVER DIAGNOSTIC BENCHMARK:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{CE('done')} <b>Latency:</b> <code>{latency} ms</code>\n"
        f"{CE('power')} <b>State:</b> <code>{'Locked' if bot_locked else 'Active'}</code>\n"
        f"{CE('shield')} <b>Authority:</b> <code>{get_user_status_line(user_id)}</code>"
    )

def _logic_statistics(message):
    user_id = message.from_user.id
    total_files = sum(len(f) for f in user_files.values())
    running = sum(1 for skey, info in bot_scripts.items() if info.get("script_owner_id") == user_id)
    safe_send(
        message.chat.id,
        f"{CE('trader')} <b>INFRASTRUCTURE STATISTICS:</b>\n\n"
        f"{CE('link')} <b>Registered Users:</b> <code>{len(active_users)}</code>\n"
        f"{CE('power')} <b>Hosted Containers:</b> <code>{total_files}</code>\n"
        f"{CE('done')} <b>Active Processes:</b> <code>{len(bot_scripts)}</code>\n"
        f"{CE('speed')} <b>Your Active Bots:</b> <code>{running}</code>"
    )

def _logic_contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(cbtn("Contact Owner", url=f"https://t.me/{get_contact_owner_username().lstrip('@')}", style="success", icon="support"))
    safe_send(message.chat.id, f"{CE('support')} <b>Customer Care Consultant:</b>", reply_markup=markup)

def safe_send(chat_id, text, reply_markup=None):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"HTML send failed, fallback plain: {e}")
        try: return bot.send_message(chat_id, re.sub(r'<[^>]*>', '', text), reply_markup=reply_markup)
        except Exception: return None

def resolve_user_identifier(identifier):
    identifier = identifier.strip().lstrip("@").lower()
    for uid, profile in user_profiles.items():
        if profile.get("username") and profile["username"].lower() == identifier:
            return uid
    return None

BUTTON_MAPPING = {
    "Updates Channel": _logic_updates_channel,
    "Upload File": _logic_upload_file,
    "Check Files": _logic_check_files,
    "Bot Speed": _logic_bot_speed,
    "Statistics": _logic_statistics,
    "Contact Owner": _logic_contact_owner,
    "Manual Install": _logic_manual_install,
    "Help Desk": _logic_help,
    "Admin Panel": lambda m: safe_send(m.chat.id, f"{CE('crown')} <b>SUPER ADMINISTRATOR CONSOLE:</b>", reply_markup=create_admin_panel_inline())
}

@bot.message_handler(func=lambda m: m.text in BUTTON_MAPPING)
def handle_main_buttons(message):
    if is_banned(message.from_user.id): return
    if bot_locked and message.from_user.id not in admin_ids:
        safe_send(message.chat.id, get_bot_off_message())
        return
    if not enforce_force_sub(message.from_user.id, message.chat.id): return
    touch_last_seen(message.from_user.id)
    BUTTON_MAPPING[message.text](message)

@bot.message_handler(commands=["start"])
def start_cmd(message):
    _logic_send_welcome(message)

# --- Cleanup & Expiry Routine ---
def cleanup():
    for key in list(bot_scripts.keys()):
        kill_process_tree(bot_scripts[key])

def expiry_warning_loop():
    while True:
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            now = datetime.now()
            c.execute("SELECT user_id, plan_name, expiry FROM subscriptions WHERE expired_notified = 0")
            for uid, pname, exp_str in c.fetchall():
                try: exp = datetime.fromisoformat(exp_str)
                except Exception: continue
                if now > exp:
                    safe_send(uid, f"{CE('notice')} <b>Subscription Plan {pname} Expired!</b> Renew to restore full container slots.")
                    remove_user_limit_override(uid)
                    c.execute("UPDATE subscriptions SET expired_notified = 1 WHERE user_id = ?", (uid,))
                    conn.commit()
            conn.close()
        except Exception: pass
        time.sleep(3600)

atexit.register(cleanup)
threading.Thread(target=expiry_warning_loop, daemon=True).start()

if __name__ == "__main__":
    logger.info("Starting Nebula Host Cloud...")
    keep_alive()
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
