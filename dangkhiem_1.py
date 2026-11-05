#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, time, json, random, string, hashlib, re, threading, ssl, gc, base64
from collections import defaultdict
from urllib.parse import urlparse, urlencode
from datetime import datetime
import requests, psutil, paho.mqtt.client as mqtt
from colorama import init, Fore, Back, Style
init(autoreset=True)

# ==========================================
#           GRADIENT ANSI 24-BIT CHO LOG
# ==========================================
def _grad(text, palette="blue_purple"):
    if not text:
        return text
    palettes = {
        "blue_purple":  ((0, 140, 255), (200, 60, 255)),
        "green_cyan":   ((0, 200, 100), (0, 220, 240)),
        "red_purple":   ((255, 60, 60), (200, 60, 255)),
    }
    start, end = palettes.get(palette, palettes["blue_purple"])
    n = max(len(text) - 1, 1)
    out = []
    for i, ch in enumerate(text):
        t = i / n
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        out.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
    out.append("\x1b[0m")
    return "".join(out)

# ==========================================
#           MÀU SẮC & TIỆN ÍCH
# ==========================================
M1 = Fore.LIGHTMAGENTA_EX
M2 = Fore.MAGENTA
W = Fore.LIGHTWHITE_EX
C = Fore.LIGHTCYAN_EX
G = Fore.LIGHTGREEN_EX
Y = Fore.LIGHTYELLOW_EX
R = Fore.LIGHTRED_EX
Y2 = Fore.YELLOW
COLOR_LIST = ["#DB342E","#15A85F","#F27806","#F7B503","#FFFFFF","#000000"]

def anon_sent(label, kind, target, content, prefix="#"):
    head = f"{label} đã gửi {kind} đến {target}".strip()
    print(_grad(head, "blue_purple"))
    c = str(content).replace("\n", " ").strip()
    if len(c) > 200:
        c = c[:200] + "..."
    print(_grad(f"{prefix}{c}", "blue_purple"))

def box(t, m=M1):
    d = len(t)+6
    print(m+"╔"+"═"*d+"╗")
    print(m+"║  "+t+"  ║")
    print(m+"╚"+"═"*d+"╝"+Style.RESET_ALL)

def big_box(t, m=M1):
    lines = t.strip().split('\n')
    ml = max(len(x) for x in lines) if lines else 0
    print(m+"╔"+"═"*(ml+4)+"╗")
    for x in lines:
        print(m+"║  "+x.ljust(ml)+"  ║")
    print(m+"╚"+"═"*(ml+4)+"╝"+Style.RESET_ALL)

def readf(p):
    try:
        with open(p,'r',encoding='utf-8') as f:
            return f.read().strip()
    except:
        return ""
def readl(p):
    if not os.path.exists(p):
        return []
    try:
        with open(p,'r',encoding='utf-8') as f:
            return [x.strip() for x in f if x.strip()]
    except:
        return []

# ==========================================
#           BANNER ASCII
# ==========================================
def print_banner_slow():
    banner = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⡤⠤⠤⠔⠒⠒⠒⠒⢤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣀⠠⠤⣄⡀⠀⢀⣀⡒⠑⠊⠉⠀⠈⠳⠤⠤⠞⠉⠉⠁⠉⠓⠚⠁⠀⠀⠀⠀⠀⠀⠀⠘⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣀⡃⠈⠀⠉⠉⠁⠀⠈⠑⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠛⣈⣉⣉⡣⠤⠤⣀⡠⢤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠚⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⢄⣀⠀⠀⠀⠀⡀⢄⣠⣾⣯⣶⣿⣿⣟⣛⠀⠀⠢⠤⢬⡉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠤⢤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⢆⡄⣾⣯⣷⡿⣿⣿⣿⣷⠹⢅⡀⠀⠀⠀⡍⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣰⠚⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣵⣿⣾⣿⣿⣿⣿⣿⣯⠄⠓⣢⢅⠒⡤⢉⡪⡈⠝⢮⢀⣀⢀⣀⣀⣀⡠⠤⠤⠤⠀⠀⠀⠀⠀
⠤⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣽⣿⣿⣽⣻⣿⠷⡿⣟⠀⣀⡓⣌⠂⡥⡘⡆⠈⢆⠉⠁⠀⠧⠤⠤⢄⡠⠤⠖⠉⠁⠀⠀⠀⠀
⣴⡏⣳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣏⢰⡟⡿⣯⢻⣿⣿⣽⣮⠻⣀⢱⠀⢈⣄⣉⠁⡀⢏⠢⠡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠉⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣌⡱⢏⡟⣹⣯⣯⣮⣽⠏⡈⡑⢙⡸⢴⠪⢠⠇⡈⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣄⢇⡇⢸⠀⢌⠀⣸⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⡏⠀⠀⠘⠒⠃⡞⣱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠙⢦⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣛⣛⢷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠛⠉⠉⢱⠀⣀⣀⣤⣴⡄⡸⠢⡀⢱⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠿⠿⢿⡽⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠤⠴⠋⢸⣿⣿⣿⣿⡿⠀⠀⢣⠀⠉⠓⢦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣦⣤⣀⣹⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠖⢉⠁⠀⠀⢰⣲⠀⢀⢿⣿⡿⠫⠀⠀⣀⠀⠑⠒⠤⢄⡈⠙⠲⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠉⠙⠻⢿⣿⣿⣿⣿⣿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠞⠁⢸⣙⢲⠀⠀⡬⡄⠀⢸⣿⠟⠁⠀⣠⠞⠃⠀⠀⠀⠀⠀⠈⠉⠲⡄⠈⠳⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠹⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠞⠁⠀⣀⡀⠀⣗⡆⠀⠀⠋⠃⢀⢾⠏⠀⠀⠘⠃⠀⠀⠀⠀⣖⡆⠀⠀⠀⠀⡇⠀⠀⢱⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣶⣄⡀⣀⣀⡤⠔⠊⠉⠀⠀⠀⠀⠀⠐⡜⡄⡗⡇⠀⢠⣠⢠⢜⠚⠀⣀⠯⠇⠀⠀⠀⠀⢀⠁⠀⠀⠀⢀⡀⢣⠀⠀⠘⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⡆⠀⠰⣌⢆⠀⠀⠀⠀⠀⠀⠀⠰⠸⡨⠬⠇⢸⢸⢩⠎⠀⡰⢣⠃⠀⠀⠀⠀⠀⢸⠽⠀⠀⠠⡫⠄⢇⠀⠀⠀⢣⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡿⠀⠀⠀⠘⢪⢦⡀⠀⠀⢠⠴⠋⠙⢦⡌⣲⠀⢸⣸⠈⠀⡰⢡⠃⠀⠀⠀⠀⠀⠀⣖⡆⢠⡖⠀⠀⠀⡎⣄⠆⠀⠈⡆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡔⠙⣆⠄⠀⠀⠀⢸⠀⠳⣄⠀⡎⠀⠀⠀⠀⢱⠀⢀⠆⡆⠀⢠⢥⠃⠀⠀⠀⠀⠀⠀⢸⢰⢸⢰⠉⠀⠀⢸⢀⢱⠁⠀⠀⢣⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠣⠤⣀⡀⠀⢇⠀⠘⢦⢱⠀⠀⠀⠀⡸⠀⡜⡚⠀⢀⣋⠎⠀⠀⠀⠀⠀⠀⠀⠀⡜⠘⡌⢸⠀⠀⠀⡇⡜⢸⠀⠀⠀⠸⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠉⠒⠊⠀⠀⠈⠓⠃⠀⠀⠀⡇⢠⢭⠁⠀⣞⡜⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀⠀⢪⠀⠀⢰⢁⠇⠀⡇⠀⠀⠀⢣⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⣖⡎⠀⡜⡰⠀⠀⠀⠀⠀⠀⠀⠀⡤⣘⠄⠀⢣⠀⠀⡜⢸⠀⠀⢇⠀⠀⠀⢱⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡇⣲⠀⢰⣩⠁⠀⠀⠀⠀⠀⠀⠀⠀⢱⡀⠁⠀⢸⠀⠀⡇⡇⠀⠀⡇⠀⠀⠀⠸⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠐⡠⢃⠖⡆⠀⡖⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣄⠀⡸⠀⠰⠸⠀⠀⠀⡇⠀⠀⠀⠀⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡠⠤⠤⠖⠸⡁⠧⠬⠭⣃⣳⠁⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠘⢦⢸⠀⣇⠇⠀⠀⠀⢣⠀⠀⠀⠀⢸⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⠀⠀⠀⠀⠀⢀⣠⠔⠋⠁⠀⠀⠀⠀⠀⢱⡈⠃⠀⣈⣀⢀⡓⣒⡠⠄⢉⠑⠒⠤⢄⣀⡀⣠⠼⠀⡇⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠘⡄⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢀⡠⠔⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡏⠉⠀⠀⠁⠈⠀⠈⠉⠁⠉⠉⠀⠀⠀⠈⠤⢄⡀⡸⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⢇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⢸⠀
---------------------------------------------------------------------------------------------------
                                        Tool 5 App Siêu Ba
    """
    for line in banner.strip().split('\n'):
        print(Fore.MAGENTA + line + Style.RESET_ALL)
        time.sleep(0.03)
    print()

# ==========================================
#           PHẦN 1: FACEBOOK
# ==========================================
cookie_attempts = defaultdict(lambda: {'count': 0, 'last_reset': time.time(), 'banned_until': 0, 'permanent_ban': False})
cookie_delays = {}
active_threads = {}
cleanup_lock = threading.Lock()
stop_events = {
    'treo ngon': threading.Event(),
    'nhay': threading.Event(),
    'poll': threading.Event(),
    'fake typing': threading.Event(),
    'theme': threading.Event(),
    'nickname': threading.Event(),
    'nhay tag': threading.Event()
}
active_functions = {}

def handle_failed_connection(cookie_hash):
    global cookie_attempts
    current_time = time.time()
    if current_time - cookie_attempts[cookie_hash]['last_reset'] > 43200:
        cookie_attempts[cookie_hash]['count'] = 0
        cookie_attempts[cookie_hash]['last_reset'] = current_time
        cookie_attempts[cookie_hash]['banned_until'] = 0
    if cookie_attempts[cookie_hash]['banned_until'] > 0:
        ban_count = getattr(cookie_attempts[cookie_hash], 'ban_count', 0) + 1
        cookie_attempts[cookie_hash]['ban_count'] = ban_count
        if ban_count >= 5:
            cookie_attempts[cookie_hash]['permanent_ban'] = True
            print(f"Cookie {cookie_hash[:10]} Đã Bị Ngưng Hoạt Động Vĩnh Viễn")
            for key in list(active_threads.keys()):
                if key.startswith(cookie_hash):
                    try:
                        active_threads[key].stop()
                    except:
                        pass
                    del active_threads[key]

def cleanup_global_memory():
    global active_threads, cookie_attempts
    with cleanup_lock:
        current_time = time.time()
        expired_cookies = []
        for cookie_hash, data in cookie_attempts.items():
            if data['permanent_ban'] or (current_time - data['last_reset'] > 86400):
                expired_cookies.append(cookie_hash)
        for cookie_hash in expired_cookies:
            del cookie_attempts[cookie_hash]
            for key in list(active_threads.keys()):
                if key.startswith(cookie_hash):
                    try:
                        active_threads[key].stop()
                    except:
                        pass
                    del active_threads[key]
        gc.collect()
        process = psutil.Process()
        memory_info = process.memory_info()
        print(f"Memory Usage: {memory_info.rss / (1024**3):.2f} GB")

def parse_cookie_string(cookie_string):
    cookie_dict = {}
    cookies = cookie_string.split(";")
    for cookie in cookies:
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookie_dict[key] = value
    return cookie_dict

def generate_offline_threading_id() -> str:
    ret = int(time.time() * 1000)
    value = random.randint(0, 4294967295)
    binary_str = format(value, "022b")[-22:]
    msgs = bin(ret)[2:] + binary_str
    return str(int(msgs, 2))

def get_headers(url: str, options: dict = {}, ctx: dict = {}, customHeader: dict = {}) -> dict:
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.facebook.com/",
        "Host": urlparse(url).netloc,
        "Origin": "https://www.facebook.com",
        "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G973U Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
        "Connection": "keep-alive",
    }
    if "user_agent" in options:
        headers["User-Agent"] = options["user_agent"]
    for key in customHeader:
        headers[key] = customHeader[key]
    if "region" in ctx:
        headers["X-MSGR-Region"] = ctx["region"]
    return headers

def json_minimal(data):
    return json.dumps(data, separators=(",", ":"))

class Counter:
    def __init__(self, initial_value=0):
        self.value = initial_value
    def increment(self):
        self.value += 1
        return self.value
    @property
    def counter(self):
        return self.value

def formAll(dataFB, FBApiReqFriendlyName=None, docID=None, requireGraphql=None):
    global _req_counter
    if '_req_counter' not in globals():
        _req_counter = Counter(0)
    __reg = _req_counter.increment()
    dataForm = {}
    if requireGraphql is None:
        dataForm["fb_dtsg"] = dataFB["fb_dtsg"]
        dataForm["jazoest"] = dataFB["jazoest"]
        dataForm["__a"] = 1
        dataForm["__user"] = str(dataFB["FacebookID"])
        dataForm["__req"] = str_base(__reg, 36)
        dataForm["__rev"] = dataFB["clientRevision"]
        dataForm["av"] = dataFB["FacebookID"]
        dataForm["fb_api_caller_class"] = "RelayModern"
        dataForm["fb_api_req_friendly_name"] = FBApiReqFriendlyName
        dataForm["server_timestamps"] = "true"
        dataForm["doc_id"] = str(docID)
    else:
        dataForm["fb_dtsg"] = dataFB["fb_dtsg"]
        dataForm["jazoest"] = dataFB["jazoest"]
        dataForm["__a"] = 1
        dataForm["__user"] = str(dataFB["FacebookID"])
        dataForm["__req"] = str_base(__reg, 36)
        dataForm["__rev"] = dataFB["clientRevision"]
        dataForm["av"] = dataFB["FacebookID"]
    return dataForm

def mainRequests(url, data, cookies):
    return {
        "url": url,
        "data": data,
        "headers": {
            "authority": "www.facebook.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,vi;q=0.8",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.facebook.com",
            "referer": "https://www.facebook.com/",
            "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "x-fb-friendly-name": "FriendingCometFriendRequestsRootQueryRelayPreloader",
            "x-fb-lsd": "YCb7tYCGWDI6JLU5Aexa1-"
        },
        "cookies": parse_cookie_string(cookies),
        "verify": True
    }

def digitToChar(digit):
    if digit < 10:
        return str(digit)
    return chr(ord('a') + digit - 10)

def str_base(number, base):
    if number < 0:
        return "-" + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digitToChar(m)
    return digitToChar(m)

def generate_session_id():
    return random.randint(1, 2 ** 53)

def generate_client_id():
    def gen(length):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return gen(8) + '-' + gen(4) + '-' + gen(4) + '-' + gen(4) + '-' + gen(12)

class fbTools:
    def __init__(self, dataFB, threadID="0"):
        self.threadID = threadID
        self.dataGet = None
        self.dataFB = dataFB
        self.ProcessingTime = None
        self.last_seq_id = None
    def getAllThreadList(self):
        randomNumber = str(int(format(int(time.time() * 1000), "b") + ("0000000000000000000000" + format(int(random.random() * 4294967295), "b"))[-22:], 2))
        dataForm = formAll(self.dataFB, requireGraphql=0)
        dataForm["queries"] = json.dumps({
            "o0": {
                "doc_id": "3336396659757871",
                "query_params": {
                    "limit": 20,
                    "before": None,
                    "tags": ["INBOX"],
                    "includeDeliveryReceipts": False,
                    "includeSeqID": True,
                }
            }
        })
        sendRequests = requests.post(**mainRequests("https://www.facebook.com/api/graphqlbatch/", dataForm, self.dataFB["cookieFacebook"]))
        response_text = sendRequests.text
        self.ProcessingTime = sendRequests.elapsed.total_seconds()
        if response_text.startswith("for(;;);"):
            response_text = response_text[9:]
        if not response_text.strip():
            print("Error: Empty response from Facebook API")
            return False
        try:
            response_parts = response_text.split("\n")
            first_part = response_parts[0]
            if first_part.strip():
                response_data = json.loads(first_part)
                self.dataGet = first_part
                if "o0" in response_data and "data" in response_data["o0"] and "viewer" in response_data["o0"]["data"] and "message_threads" in response_data["o0"]["data"]["viewer"]:
                    self.last_seq_id = response_data["o0"]["data"]["viewer"]["message_threads"]["sync_sequence_id"]
                    return True
                else:
                    print("Error: Expected fields not found in response")
                    return False
            else:
                print("Error: Empty first part of response")
                return False
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return False
        except KeyError as e:
            print(f"Key Error: {e}")
            return False

class MessageSender:
    def __init__(self, fbt, dataFB, fb_instance):
        self.fbt = fbt
        self.dataFB = dataFB
        self.fb_instance = fb_instance
        self.mqtt = None
        self.ws_req_number = 0
        self.ws_task_number = 0
        self.syncToken = None
        self.lastSeqID = None
        self.req_callbacks = {}
        self.cookie_hash = hashlib.md5(dataFB['cookieFacebook'].encode()).hexdigest()
        self.connect_attempts = 0
        self.last_cleanup = time.time()
        self.THEMES = [
            {"id": "3650637715209675", "name": "Besties"},
            {"id": "769656934577391", "name": "Women's History Month"},
            {"id": "702099018755409", "name": "Dune: Part Two"},
            {"id": "1480404512543552", "name": "Avatar: The Last Airbender"},
            {"id": "952656233130616", "name": "J.Lo"},
            {"id": "741311439775765", "name": "Love"},
            {"id": "215565958307259", "name": "Bob Marley: One Love"},
            {"id": "194982117007866", "name": "Football"},
            {"id": "1743641112805218", "name": "Soccer"},
            {"id": "730357905262632", "name": "Mean Girls"},
            {"id": "1270466356981452", "name": "Wonka"},
            {"id": "704021702720552", "name": "Pizza"},
            {"id": "1013083536414851", "name": "Wish"},
            {"id": "359537246600743", "name": "Trolls"},
            {"id": "173976782455615", "name": "The Marvels"},
            {"id": "2317258455139234", "name": "One Piece"},
            {"id": "6685081604943977", "name": "1989"},
            {"id": "1508524016651271", "name": "Avocado"},
            {"id": "265997946276694", "name": "Loki Season 2"},
            {"id": "6584393768293861", "name": "olivia rodrigo"},
            {"id": "845097890371902", "name": "Baseball"},
            {"id": "292955489929680", "name": "Lollipop"},
            {"id": "976389323536938", "name": "Loops"},
            {"id": "810978360551741", "name": "Parenthood"},
            {"id": "195296273246380", "name": "Bubble Tea"},
            {"id": "6026716157422736", "name": "Basketball"},
            {"id": "693996545771691", "name": "Elephants & Flowers"},
            {"id": "390127158985345", "name": "Chill"},
            {"id": "365557122117011", "name": "Support"},
            {"id": "339021464972092", "name": "Music"},
            {"id": "1060619084701625", "name": "Lo-Fi"},
            {"id": "3190514984517598", "name": "Sky"},
            {"id": "627144732056021", "name": "Celebration"},
            {"id": "275041734441112", "name": "Care"},
            {"id": "3082966625307060", "name": "Astrology"},
            {"id": "539927563794799", "name": "Cottagecore"},
            {"id": "527564631955494", "name": "Ocean"},
            {"id": "230032715012014", "name": "Tie-Dye"},
            {"id": "788274591712841", "name": "Monochrome"},
            {"id": "3259963564026002", "name": "Default"},
            {"id": "724096885023603", "name": "Berry"},
            {"id": "624266884847972", "name": "Candy"},
            {"id": "273728810607574", "name": "Unicorn"},
            {"id": "262191918210707", "name": "Tropical"},
            {"id": "2533652183614000", "name": "Maple"},
            {"id": "909695489504566", "name": "Sushi"},
            {"id": "582065306070020", "name": "Rocket"},
            {"id": "557344741607350", "name": "Citrus"},
            {"id": "280333826736184", "name": "Lollipop"},
            {"id": "271607034185782", "name": "Shadow"},
            {"id": "1257453361255152", "name": "Rose"},
            {"id": "571193503540759", "name": "Lavender"},
            {"id": "2873642949430623", "name": "Tulip"},
            {"id": "3273938616164733", "name": "Classic"},
            {"id": "403422283881973", "name": "Apple"},
            {"id": "3022526817824329", "name": "Peach"},
            {"id": "672058580051520", "name": "Honey"},
            {"id": "3151463484918004", "name": "Kiwi"},
            {"id": "736591620215564", "name": "Ocean"},
            {"id": "193497045377796", "name": "Grape"},
        ]
    def set_theme(self, theme_id, thread_id, callback=None):
        if self.mqtt is None:
            print("Error: Not Connected To MQTT")
            return False
        self.cleanup_memory()
        self.ws_req_number += 1
        self.ws_task_number += 1
        if not theme_id:
            selected_theme = random.choice(self.THEMES)
            theme_id = selected_theme["id"]
            theme_name = selected_theme["name"]
        else:
            selected_theme = next((t for t in self.THEMES if t["id"] == theme_id), None)
            if not selected_theme:
                print(f"Error: Theme ID {theme_id} not found")
                return False
            theme_name = selected_theme["name"]
        task_payload = {"thread_key": thread_id, "theme_fbid": theme_id, "source": None, "sync_group": 1, "payload": None}
        task = {"failure_count": None, "label": "43", "payload": json.dumps(task_payload, separators=(",", ":")), "queue_name": "thread_theme", "task_id": self.ws_task_number}
        content = {"app_id": "2220391788200892", "payload": json.dumps({"data_trace_id": None, "epoch_id": int(generate_offline_threading_id()), "tasks": [task], "version_id": "25095469420099952"}, separators=(",", ":")), "request_id": self.ws_req_number, "type": 3}
        if callback is not None and callable(callback):
            self.req_callbacks[self.ws_req_number] = callback
        try:
            self.mqtt.publish(topic="/ls_req", payload=json.dumps(content, separators=(",", ":")), qos=1, retain=False)
            print(f"[✓] Đã thay đổi theme thành: {theme_name} (ID: {theme_id}) cho box {thread_id}")
            return True
        except Exception as e:
            print(f"Error Publishing Theme Change: {e}")
            return False
    def cleanup_memory(self):
        current_time = time.time()
        if current_time - self.last_cleanup > 3600:
            self.req_callbacks.clear()
            gc.collect()
            self.last_cleanup = current_time
    def get_last_seq_id(self):
        success = self.fbt.getAllThreadList()
        if success:
            self.lastSeqID = self.fbt.last_seq_id
        else:
            print("Failed To Get Last Sequence ID. Check Facebook Authentication.")
            return
    def on_disconnect(self, client, userdata, rc):
        global cookie_attempts
        print(f"Disconnected With Code {rc}")
        cookie_attempts[self.cookie_hash]['count'] += 1
        current_time = time.time()
        if current_time - cookie_attempts[self.cookie_hash]['last_reset'] > 43200:
            cookie_attempts[self.cookie_hash]['count'] = 1
            cookie_attempts[self.cookie_hash]['last_reset'] = current_time
        if cookie_attempts[self.cookie_hash]['count'] >= 20:
            print(f"Cookie {self.cookie_hash[:10]} Bị Tạm Ngưng Connect Trong 12 Giờ")
            cookie_attempts[self.cookie_hash]['banned_until'] = current_time + 43200
            return
        if rc != 0:
            print("Attempting To Reconnect...")
            try:
                time.sleep(min(cookie_attempts[self.cookie_hash]['count'] * 2, 30))
                client.reconnect()
            except:
                print("Reconnect Failed")
    def _messenger_queue_publish(self, client, userdata, flags, rc):
        print(f"Connected To MQTT With Code: {rc}")
        if rc != 0:
            print(f"Connection Failed With Code {rc}")
            return
        topics = [("/t_ms", 0)]
        client.subscribe(topics)
        queue = {"sync_api_version": 10, "max_deltas_able_to_process": 1000, "delta_batch_size": 500, "encoding": "JSON", "entity_fbid": self.dataFB['FacebookID']}
        if self.syncToken is None:
            topic = "/messenger_sync_create_queue"
            queue["initial_titan_sequence_id"] = self.lastSeqID
            queue["device_params"] = None
        else:
            topic = "/messenger_sync_get_diffs"
            queue["last_seq_id"] = self.lastSeqID
            queue["sync_token"] = self.syncToken
        print(f"Publishing To {topic}")
        client.publish(topic, json_minimal(queue), qos=1, retain=False)
    def connect_mqtt(self):
        global cookie_attempts
        if cookie_attempts[self.cookie_hash]['permanent_ban']:
            print(f"Cookie {self.cookie_hash[:10]} Đã Bị Ngưng Connect Vĩnh Viễn")
            return False
        current_time = time.time()
        if current_time < cookie_attempts[self.cookie_hash]['banned_until']:
            remaining = cookie_attempts[self.cookie_hash]['banned_until'] - current_time
            print(f"Cookie {self.cookie_hash[:10]} Bị Tạm Khóa, Còn {remaining/3600:.1f} Giờ")
            return False
        if not self.lastSeqID:
            print("Error: No last_seq_id Available. Cannot Connect To MQTT.")
            return False
        chat_on = json_minimal(True)
        session_id = generate_session_id()
        user = {"u": self.dataFB["FacebookID"], "s": session_id, "chat_on": chat_on, "fg": False, "d": generate_client_id(), "ct": "websocket", "aid": 219994525426954, "mqtt_sid": "", "cp": 3, "ecp": 10, "st": ["/t_ms", "/messenger_sync_get_diffs", "/messenger_sync_create_queue"], "pm": [], "dc": "", "no_auto_fg": True, "gas": None, "pack": []}
        host = f"wss://edge-chat.messenger.com/chat?region=eag&sid={session_id}"
        options = {"client_id": "mqttwsclient", "username": json_minimal(user), "clean": True, "ws_options": {"headers": {"Cookie": self.dataFB['cookieFacebook'], "Origin": "https://www.messenger.com", "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G973U Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36", "Referer": "https://www.messenger.com/", "Host": "edge-chat.messenger.com"}}, "keepalive": 10}
        self.mqtt = mqtt.Client(client_id="mqttwsclient", clean_session=True, protocol=mqtt.MQTTv31, transport="websockets")
        self.mqtt.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.mqtt.on_connect = self._messenger_queue_publish
        self.mqtt.on_disconnect = self.on_disconnect
        self.mqtt.username_pw_set(username=options["username"])
        parsed_host = urlparse(host)
        self.mqtt.ws_set_options(path=f"{parsed_host.path}?{parsed_host.query}", headers=options["ws_options"]["headers"])
        print(f"Connecting To {options['ws_options']['headers']['Host']}...")
        try:
            self.mqtt.connect(host=options["ws_options"]["headers"]["Host"], port=443, keepalive=options["keepalive"])
            print("MQTT Connection Established")
            self.mqtt.loop_start()
            return True
        except Exception as e:
            print(f"MQTT Connection Error: {e}")
            cookie_attempts[self.cookie_hash]['count'] += 1
            return False
    def stop(self):
        if self.mqtt:
            print("Stopping MQTT Client...")
            try:
                self.mqtt.disconnect()
                self.mqtt.loop_stop()
            except:
                pass
        self.cleanup_memory()
    def sendTypingIndicatorMqtt(self, isTyping, thread_id, callback=None):
        if self.mqtt is None:
            print("Error: Not Connected To MQTT")
            return False
        self.cleanup_memory()
        self.ws_req_number += 1
        task_payload = {"thread_key": thread_id, "is_group_thread": 1, "is_typing": 1 if isTyping else 0, "attribution": 0}
        content = {"app_id": "2220391788200892", "payload": json.dumps({"label": "3", "payload": json.dumps(task_payload, separators=(",", ":")), "version": "25393437286970779"}, separators=(",", ":")), "request_id": self.ws_req_number, "type": 4}
        if callback is not None and callable(callback):
            self.req_callbacks[self.ws_req_number] = callback
        try:
            self.mqtt.publish(topic="/ls_req", payload=json.dumps(content, separators=(",", ":")), qos=1, retain=False)
            return True
        except Exception as e:
            print(f"Error Publishing Typing Indicator: {e}")
            return False
    def createPollMqtt(self, title, options, thread_id, callback=None):
        if self.mqtt is None:
            print("Error: Not Connected To MQTT")
            return False
        self.cleanup_memory()
        self.ws_req_number += 1
        self.ws_task_number += 1
        task_payload = {"question_text": title, "thread_key": thread_id, "options": options, "sync_group": 1}
        task = {"failure_count": None, "label": "163", "payload": json.dumps(task_payload, separators=(",", ":")), "queue_name": "poll_creation", "task_id": self.ws_task_number}
        content = {"app_id": "2220391788200892", "payload": json.dumps({"data_trace_id": None, "epoch_id": int(generate_offline_threading_id()), "tasks": [task], "version_id": "7158486590867448"}, separators=(",", ":")), "request_id": self.ws_req_number, "type": 3}
        if callback is not None and callable(callback):
            self.req_callbacks[self.ws_req_number] = callback
        try:
            self.mqtt.publish(topic="/ls_req", payload=json.dumps(content, separators=(",", ":")), qos=1, retain=False)
            return True
        except Exception as e:
            print(f"Error Publishing Poll Creation: {e}")
            return False
    def send_message(self, text=None, thread_id=None, attachment=None, mentions=None, message_id=None, callback=None):
        if self.mqtt is None:
            print("Error: Not Connected To MQTT")
            return False
        if thread_id is None:
            print("Error: Thread ID Is Required")
            return False
        if text is None and attachment is None:
            print("Error: Text Or Attachment Is Required")
            return False
        self.cleanup_memory()
        self.ws_req_number += 1
        content = {"app_id": "2220391788200892", "payload": {"data_trace_id": None, "epoch_id": int(generate_offline_threading_id()), "tasks": [], "version_id": "7545284305482586"}, "request_id": self.ws_req_number, "type": 3}
        text = str(text) if text is not None else ""
        if len(text) > 0:
            self.ws_task_number += 1
            task_payload = {
                "initiating_source": 0,
                "multitab_env": 0,
                "otid": generate_offline_threading_id(),
                "send_type": 1,
                "skip_url_preview_gen": 0,
                "source": 0,
                "sync_group": 1,
                "text": text,
                "text_has_links": 0,
                "thread_id": int(thread_id)
            }
            if mentions and isinstance(mentions, list) and len(mentions) > 0:
                mention_entities = []
                for uid in mentions:
                    pattern = f"@{uid}"
                    start = 0
                    while True:
                        pos = text.find(pattern, start)
                        if pos == -1:
                            break
                        mention_entities.append({
                            "id": str(uid),
                            "offset": pos,
                            "length": len(pattern)
                        })
                        start = pos + 1
                if mention_entities:
                    task_payload["mentions"] = mention_entities
            if message_id is not None:
                if not isinstance(message_id, str):
                    raise ValueError("message_id must be a string")
                task_payload["reply_metadata"] = {"reply_source_id": message_id, "reply_source_type": 1, "reply_type": 0}
            task = {"failure_count": None, "label": "46", "payload": json.dumps(task_payload, separators=(",", ":")), "queue_name": str(thread_id), "task_id": self.ws_task_number}
            content["payload"]["tasks"].append(task)
        self.ws_task_number += 1
        task_mark_payload = {"last_read_watermark_ts": int(time.time() * 1000), "sync_group": 1, "thread_id": int(thread_id)}
        task_mark = {"failure_count": None, "label": "21", "payload": json.dumps(task_mark_payload, separators=(",", ":")), "queue_name": str(thread_id), "task_id": self.ws_task_number}
        content["payload"]["tasks"].append(task_mark)
        content["payload"] = json.dumps(content["payload"], separators=(",", ":"))
        if callback is not None and callable(callback):
            self.req_callbacks[self.ws_req_number] = callback
        try:
            self.mqtt.publish(topic="/ls_req", payload=json.dumps(content, separators=(",", ":")), qos=1, retain=False)
            return True
        except Exception as e:
            print(f"Error Publishing Message: {e}")
            return False
    def upload_file(self, file_path): pass
    def download_and_upload_file(self, file_url): pass
    def share_contact(self, text, sender_id, thread_id): pass
    def share_link(self, text, url, thread_id): pass

def get_friends_list(dataFB):
    try:
        form = {"viewer": str(dataFB["FacebookID"]), "fb_dtsg": dataFB["fb_dtsg"], "jazoest": dataFB["jazoest"], "__user": str(dataFB["FacebookID"]), "__a": "1", "__req": "1", "__rev": dataFB.get("clientRevision", "1015919737")}
        headers = get_headers("https://www.facebook.com/chat/user_info_all", customHeader={"Content-Type": "application/x-www-form-urlencoded"})
        response = requests.post("https://www.facebook.com/chat/user_info_all", data=form, headers=headers, cookies=parse_cookie_string(dataFB["cookieFacebook"]), timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP Error {response.status_code}")
        content = response.text.replace('for (;;);', '')
        data = json.loads(content)
        if not data or "payload" not in data:
            raise Exception("getFriendsList returned empty object or missing payload.")
        if "error" in data:
            raise Exception(f"API Error: {data.get('errorDescription', 'Unknown error')}")
        friends = data["payload"]
        friend_ids = [str(user_id) for user_id in friends.keys()]
        return True, friend_ids, f"✅ Lấy được {len(friend_ids)} bạn bè."
    except Exception as e:
        return False, [], f"❌ Lỗi lấy danh sách bạn bè: {str(e)}"

def tenbox(newTitle, threadID, dataFB):
    try:
        message_id = generate_offline_threading_id()
        timestamp = int(time.time() * 1000)
        form_data = {"client": "mercury", "action_type": "ma-type:log-message", "author": f"fbid:{dataFB['FacebookID']}", "thread_id": str(threadID), "timestamp": timestamp, "timestamp_relative": str(int(time.time())), "source": "source:chat:web", "source_tags[0]": "source:chat", "offline_threading_id": message_id, "message_id": message_id, "threading_id": generate_offline_threading_id(), "thread_fbid": str(threadID), "thread_name": str(newTitle), "log_message_type": "log:thread-name", "fb_dtsg": dataFB["fb_dtsg"], "jazoest": dataFB["jazoest"], "__user": str(dataFB["FacebookID"]), "__a": "1", "__req": "1", "__rev": dataFB.get("clientRevision", "1015919737")}
        response = requests.post("https://www.facebook.com/messaging/set_thread_name/", data=form_data, headers=get_headers("https://www.facebook.com", customHeader={"Content-Length": str(len(form_data))}), cookies=parse_cookie_string(dataFB["cookieFacebook"]), timeout=10)
        if response.status_code == 200:
            return True, f"✅ Đã đổi tên thành: {newTitle}"
        else:
            return False, f"❌ Lỗi HTTP {response.status_code} khi đổi tên."
    except Exception as e:
        return False, f"❌ Lỗi đổi tên: {e}"

def change_nickname(nickname, thread_id, participant_id, dataFB):
    try:
        form = {"nickname": nickname, "participant_id": str(participant_id), "thread_or_other_fbid": str(thread_id), "source": "thread_settings", "dpr": "1", "fb_dtsg": dataFB["fb_dtsg"], "jazoest": dataFB["jazoest"], "__user": str(dataFB["FacebookID"]), "__a": "1", "__req": str_base(Counter().increment(), 36), "__rev": dataFB.get("clientRevision", "1015919737")}
        headers = get_headers("https://www.facebook.com/messaging/save_thread_nickname/", customHeader={"Content-Type": "application/x-www-form-urlencoded"})
        response = requests.post("https://www.facebook.com/messaging/save_thread_nickname/", data=form, headers=headers, cookies=parse_cookie_string(dataFB["cookieFacebook"]), timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP Error {response.status_code}")
        content = response.text.replace('for (;;);', '')
        data = json.loads(content)
        if "error" in data:
            raise Exception(f"API Error: {data.get('errorDescription', 'Unknown error')}")
        return True, f"✅ Đã đổi biệt danh cho user {participant_id} thành {nickname} trong box {thread_id}"
    except Exception as e:
        return False, f"❌ Lỗi đổi biệt danh: {str(e)}"

def get_thread_info_graphql(thread_id, dataFB):
    try:
        form = {"queries": json.dumps({"o0": {"doc_id": "3449967031715030", "query_params": {"id": str(thread_id), "message_limit": 0, "load_messages": False, "load_read_receipts": False, "before": None}}}, separators=(",", ":")), "batch_name": "MessengerGraphQLThreadFetcher", "fb_dtsg": dataFB["fb_dtsg"], "jazoest": dataFB["jazoest"], "__user": str(dataFB["FacebookID"]), "__a": "1", "__req": str_base(Counter().increment(), 36), "__rev": dataFB.get("clientRevision", "1015919737")}
        headers = get_headers("https://www.facebook.com/api/graphqlbatch/", customHeader={"Content-Type": "application/x-www-form-urlencoded"})
        response = requests.post("https://www.facebook.com/api/graphqlbatch/", data=form, headers=headers, cookies=parse_cookie_string(dataFB["cookieFacebook"]), timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP Error {response.status_code}")
        content = response.text.replace('for (;;);', '')
        response_parts = content.split("\n")
        if not response_parts or not response_parts[0].strip():
            raise Exception("Empty response from API")
        data = json.loads(response_parts[0])
        if "error" in data:
            raise Exception(f"API Error: {data.get('errorDescription', 'Unknown error')}")
        message_thread = data["o0"]["data"]["message_thread"]
        participant_ids = [edge["node"]["messaging_actor"]["id"] for edge in message_thread["all_participants"]["edges"]]
        return True, participant_ids, f"✅ Lấy được {len(participant_ids)} thành viên."
    except Exception as e:
        return False, [], f"❌ Lỗi lấy thông tin box: {str(e)}"

def add_user_to_group(dataFB, user_ids, thread_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            if not isinstance(user_ids, list):
                user_ids = [user_ids]
            message_and_otid = generate_offline_threading_id()
            form = {"client": "mercury", "action_type": "ma-type:log-message", "author": f"fbid:{dataFB['FacebookID']}", "thread_id": "", "timestamp": str(int(time.time() * 1000)), "timestamp_absolute": "Today", "timestamp_relative": "Just now", "timestamp_time_passed": "0", "is_unread": "false", "is_cleared": "false", "is_forward": "false", "is_filtered_content": "false", "is_filtered_content_bh": "false", "is_filtered_content_account": "false", "is_spoof_warning": "false", "source": "source:chat:web", "source_tags[0]": "source:chat", "log_message_type": "log:subscribe", "status": "0", "offline_threading_id": message_and_otid, "message_id": message_and_otid, "threading_id": f"<{int(time.time() * 1000)}:{message_and_otid}>", "manual_retry_cnt": "0", "thread_fbid": str(thread_id), "fb_dtsg": dataFB["fb_dtsg"], "jazoest": dataFB["jazoest"], "__user": str(dataFB["FacebookID"]), "__a": "1", "__req": str_base(Counter().increment(), 36), "__rev": dataFB.get("clientRevision", "1015919737")}
            for i, user_id in enumerate(user_ids):
                form[f"log_message_data[added_participants][{i}]"] = f"fbid:{user_id}"
            headers = get_headers("https://www.facebook.com/messaging/send/", customHeader={"Content-Type": "application/x-www-form-urlencoded", "X-FB-LSD": dataFB.get("lsd", "YCb7tYCGWDI6JLU5Aexa1-"), "Content-Length": str(len(urlencode(form)))})
            response = requests.post("https://www.facebook.com/messaging/send/", data=form, headers=headers, cookies=parse_cookie_string(dataFB["cookieFacebook"]), timeout=15)
            if response.status_code != 200:
                raise Exception(f"HTTP Error {response.status_code}")
            content = response.text.replace('for (;;);', '')
            data = json.loads(content)
            if "error" in data:
                raise Exception(f"API Error: {data.get('errorDescription', 'Unknown error')}")
            return True, f"✅ Đã thêm {len(user_ids)} người vào nhóm {thread_id}"
        except Exception as e:
            if attempt == max_retries - 1:
                return False, f"❌ Lỗi thêm người vào nhóm: {str(e)}"
            time.sleep(5)
    return False, "❌ Failed after retries"

def read_cookies_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cookies = [line.strip() for line in f if line.strip()]
        if not cookies:
            raise ValueError("File cookie rỗng")
        return cookies
    except Exception as e:
        raise Exception(f"Lỗi đọc file cookie: {str(e)}")

class minhloi:
    def __init__(self, cookie, mqtt_broker="broker.hivemq.com", mqtt_port=1883):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.fb_dtsg = None
        self.jazoest = None
        self.rev = None
        self.init_params()
    def id_user(self):
        try:
            match = re.search(r"c_user=(\d+)", self.cookie)
            if not match:
                raise Exception("Cookie không hợp lệ")
            return match.group(1)
        except Exception as e:
            raise Exception(f"Lỗi lấy user_id: {str(e)}")
    def init_params(self):
        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1'}
        urls = ['https://www.facebook.com', 'https://mbasic.facebook.com', 'https://m.facebook.com']
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                patterns = [r'"token":"(.*?)"', r'name="fb_dtsg" value="(.*?)"', r'"fb_dtsg":"(.*?)"', r'fb_dtsg=([^&"]+)']
                fb_dtsg = None
                for p in patterns:
                    match = re.search(p, response.text)
                    if match:
                        fb_dtsg = match.group(1)
                        break
                jazoest_match = re.search(r'name="jazoest" value="(\d+)"', response.text)
                rev_match = re.search(r'"__rev":"(\d+)"', response.text)
                if fb_dtsg:
                    self.fb_dtsg = fb_dtsg
                    self.jazoest = jazoest_match.group(1) if jazoest_match else "22036"
                    self.rev = rev_match.group(1) if rev_match else "1015919737"
                    return
            except:
                pass
            time.sleep(1)
        raise Exception("Không lấy được fb_dtsg")

def run_spam_task(sender, cookie_hash, thread_id, delay, option,
                  name_file, message_files, file_path, contact_uid,
                  nickname, tag_ids, barrier, func_name):
    current_time = time.time()
    stop_event = stop_events.get(func_name) if func_name else None
    try:
        if option == 1:
            while True:
                if stop_event and stop_event.is_set():
                    print(f"[{cookie_hash[:10]}] Dừng treo ngôn cho box {thread_id}")
                    break
                if barrier:
                    barrier.wait()
                content = ""
                if message_files:
                    with open(message_files[0], 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                if content:
                    sender.send_message(content, thread_id)
                    anon_sent(f"#{cookie_hash[:10]}", "tin nhắn", f"nhóm {thread_id}", content)
                time.sleep(delay)
                if current_time - sender.last_cleanup > 600:
                    gc.collect()
        elif option == 2:
            with open(name_file, 'r', encoding='utf-8') as f:
                group_names = [line.strip() for line in f if line.strip()]
            if not group_names:
                print(f"[{cookie_hash[:10]}] File nhay.txt rỗng!")
                return
            while True:
                if stop_event and stop_event.is_set():
                    print(f"[{cookie_hash[:10]}] Dừng nhay tên cho box {thread_id}")
                    break
                for gname in group_names:
                    if stop_event and stop_event.is_set():
                        break
                    if barrier:
                        barrier.wait()
                    success, log = tenbox(gname, thread_id, sender.dataFB)
                    print(f"[{cookie_hash[:10]}] {log}")
                    time.sleep(delay)
        elif option == 3:
            with open(name_file, 'r', encoding='utf-8') as f:
                poll_titles = [line.strip() for line in f if line.strip()]
            while True:
                if stop_event and stop_event.is_set():
                    print(f"[{cookie_hash[:10]}] Dừng poll cho box {thread_id}")
                    break
                for title in poll_titles:
                    if stop_event and stop_event.is_set():
                        break
                    if barrier:
                        barrier.wait()
                    options_poll = ["Bá war", "Bá sàn"]
                    sender.createPollMqtt(title, options_poll, thread_id)
                    print(f"[{cookie_hash[:10]}] Đã tạo poll: {title}")
                    time.sleep(delay)
        elif option == 4:
            with open(name_file, 'r', encoding='utf-8') as f:
                messages = [line.strip() for line in f if line.strip()]
            while True:
                if stop_event and stop_event.is_set():
                    print(f"[{cookie_hash[:10]}] Dừng fake typing cho box {thread_id}")
                    break
                for msg in messages:
                    if stop_event and stop_event.is_set():
                        break
                    if barrier:
                        barrier.wait()
                    sender.sendTypingIndicatorMqtt(True, thread_id)
                    time.sleep(random.uniform(1, 3))
                    sender.send_message(msg, thread_id)
                    sender.sendTypingIndicatorMqtt(False, thread_id)
                    anon_sent(f"#{cookie_hash[:10]}", "tin nhắn", f"nhóm {thread_id}", msg)
                    time.sleep(delay)
        elif option == 5:
            theme_index = 0
            while True:
                if stop_event and stop_event.is_set():
                    print(f"[{cookie_hash[:10]}] Dừng theme cho box {thread_id}")
                    break
                if barrier:
                    barrier.wait()
                theme = sender.THEMES[theme_index % len(sender.THEMES)]
                sender.set_theme(theme["id"], thread_id)
                theme_index += 1
                time.sleep(delay)
        elif option == 6:
            while True:
                if stop_event and stop_event.is_set():
                    print(f"[{cookie_hash[:10]}] Dừng đổi biệt danh cho box {thread_id}")
                    break
                nickname_input = input("[+] Nhập biệt danh (Enter để dừng): ").strip()
                if not nickname_input:
                    break
                success, participant_ids, log = get_thread_info_graphql(thread_id, sender.dataFB)
                print(f"[{cookie_hash[:10]}] {log}")
                if not success:
                    break
                for pid in participant_ids:
                    if stop_event and stop_event.is_set():
                        break
                    if barrier:
                        barrier.wait()
                    change_nickname(nickname_input, thread_id, pid, sender.dataFB)
                    time.sleep(delay)
        elif option == 7:
            if not tag_ids:
                print(f"[{cookie_hash[:10]}] Chưa nhập ID tag!")
                return
            with open(name_file, 'r', encoding='utf-8') as f:
                messages = [line.strip() for line in f if line.strip()]
            if not messages:
                print(f"[{cookie_hash[:10]}] File nhay.txt rỗng!")
                return
            tag_placeholders = " ".join([f"@{uid}" for uid in tag_ids])
            while True:
                if stop_event and stop_event.is_set():
                    print(f"[{cookie_hash[:10]}] Dừng nhây tag cho box {thread_id}")
                    break
                for msg in messages:
                    if stop_event and stop_event.is_set():
                        break
                    if barrier:
                        barrier.wait()
                    full_text = f"{msg} {tag_placeholders}".strip()
                    sender.send_message(full_text, thread_id, mentions=tag_ids)
                    anon_sent(f"#{cookie_hash[:10]}", "tin nhắn", f"nhóm {thread_id}", full_text)
                    time.sleep(delay)
                    if current_time - sender.last_cleanup > 600:
                        gc.collect()
    except KeyboardInterrupt:
        pass
    finally:
        if option not in [4, 10]:
            sender.stop()
        if f"{cookie_hash}_{thread_id}" in active_threads:
            del active_threads[f"{cookie_hash}_{thread_id}"]

def send_messages_with_cookie(cookies, thread_ids, message_files, delay, option=0,
                               file_path=None, contact_uid=None, name_file=None,
                               nickname=None, tag_ids=None, func_name=None):
    global cookie_attempts, active_threads, stop_events, active_functions
    if func_name and func_name in stop_events:
        stop_events[func_name].clear()
        active_functions[func_name] = threading.current_thread()
    barrier = threading.Barrier(len(cookies)) if len(cookies) > 1 else None
    for cookie in cookies:
        cookie_hash = hashlib.md5(cookie.encode()).hexdigest()
        if cookie_attempts[cookie_hash]['permanent_ban']:
            print(f"Cookie {cookie_hash[:10]} đã bị ngưng vĩnh viễn.")
            continue
        current_time = time.time()
        if current_time < cookie_attempts[cookie_hash]['banned_until']:
            remaining = cookie_attempts[cookie_hash]['banned_until'] - current_time
            print(f"Cookie {cookie_hash[:10]} bị khóa, còn {remaining/3600:.1f} giờ.")
            continue
        try:
            fb = minhloi(cookie)
            dataFB = {"FacebookID": fb.user_id, "fb_dtsg": fb.fb_dtsg, "clientRevision": fb.rev, "jazoest": fb.jazoest, "cookieFacebook": cookie}
            fbt = fbTools(dataFB)
            sender = MessageSender(fbt, dataFB, fb)
            if option not in [4, 10]:
                sender.get_last_seq_id()
                if not sender.connect_mqtt():
                    handle_failed_connection(cookie_hash)
                    continue
            for thread_id in thread_ids:
                t = threading.Thread(
                    target=run_spam_task,
                    args=(sender, cookie_hash, thread_id, delay, option,
                          name_file, message_files, file_path, contact_uid,
                          nickname, tag_ids, barrier, func_name)
                )
                t.daemon = True
                t.start()
                active_threads[f"{cookie_hash}_{thread_id}"] = sender
        except Exception as e:
            print(f"Lỗi với cookie {cookie_hash[:10]}: {e}")
            handle_failed_connection(cookie_hash)
            continue
    if func_name:
        print(f"\nĐang chạy {func_name}.")
        print("Lệnh điều khiển:")
        print("  k               -> về menu (vẫn giữ các chức năng đang chạy)")
        print("  stop ngôn      -> dừng chức năng 1 (treo ngôn)")
        print("  stop nhây      -> dừng chức năng 4 (fake typing)")
        print("  stop nhây tag  -> dừng chức năng 7")
        print("  stop all       -> dừng tất cả")
        print()
        while True:
            try:
                cmd = input(W + "  ╰─> " + Style.RESET_ALL).strip().lower()
                if cmd == 'k':
                    print(f"Quay về menu. {func_name} vẫn chạy ngầm.")
                    break
                elif cmd.startswith('stop '):
                    target = cmd[5:].strip()
                    if target == 'all':
                        for ev in stop_events.values():
                            ev.set()
                        print("Đã dừng tất cả.")
                        break
                    elif target in stop_events:
                        stop_events[target].set()
                        print(f"Đã dừng {target}.")
                        if target == func_name:
                            break
                    else:
                        print(f"Không có chức năng '{target}'. Các chức năng: {', '.join(stop_events.keys())}")
                else:
                    print("Lệnh không hợp lệ. Chỉ nhận: k, stop <tên>, stop all")
            except KeyboardInterrupt:
                break
    return True

def fb_exec(opt):
    try:
        cookie_file = input(W + "[+] Nhập đường dẫn file chứa cookie (mỗi cookie 1 dòng):\n  ╰─> " + Style.RESET_ALL).strip()
        if not os.path.isfile(cookie_file):
            print(R + f"✘ File không tồn tại: {cookie_file}" + Style.RESET_ALL)
            return
        cookies = read_cookies_from_file(cookie_file)
        print(G + f"✓ Đã đọc {len(cookies)} cookie từ file." + Style.RESET_ALL)
        thread_ids = []
        delay = 0
        message_files = []
        name_file = None
        tag_ids = []
        func_name = None
        if opt == 1:
            func_name = "treo ngon"
            print(C + "[*] Chế độ Treo ngôn" + Style.RESET_ALL)
            num_threads = int(input(W + "[+] Nhập số lượng ID box:\n  ╰─> " + Style.RESET_ALL).strip())
            for i in range(num_threads):
                tid = input(W + f"[+] Nhập ID box thứ {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
                if tid:
                    thread_ids.append(tid)
            delay = float(input(W + "[+] Nhập delay (s):\n  ╰─> " + Style.RESET_ALL).strip())
            file_txt = input(W + "[+] Nhập đường dẫn file txt chứa nội dung:\n  ╰─> " + Style.RESET_ALL).strip()
            if not os.path.isfile(file_txt):
                print(R + f"✘ File không tồn tại: {file_txt}" + Style.RESET_ALL)
                return
            message_files = [file_txt]
        elif opt == 2:
            func_name = "nhay"
            print(C + "[*] Chế độ Nhay tên nhóm" + Style.RESET_ALL)
            num_threads = int(input(W + "[+] Nhập số lượng ID box:\n  ╰─> " + Style.RESET_ALL).strip())
            for i in range(num_threads):
                tid = input(W + f"[+] Nhập ID box thứ {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
                if tid:
                    thread_ids.append(tid)
            delay = float(input(W + "[+] Nhập delay (s):\n  ╰─> " + Style.RESET_ALL).strip())
            name_file = input(W + "[+] Nhập đường dẫn file nhay.txt chứa danh sách tên:\n  ╰─> " + Style.RESET_ALL).strip()
            if not os.path.isfile(name_file):
                print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
                return
        elif opt == 3:
            func_name = "poll"
            print(C + "[*] Chế độ Treo poll" + Style.RESET_ALL)
            num_threads = int(input(W + "[+] Nhập số lượng ID box:\n  ╰─> " + Style.RESET_ALL).strip())
            for i in range(num_threads):
                tid = input(W + f"[+] Nhập ID box thứ {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
                if tid:
                    thread_ids.append(tid)
            delay = float(input(W + "[+] Nhập delay (s):\n  ╰─> " + Style.RESET_ALL).strip())
            name_file = input(W + "[+] Nhập đường dẫn file nhay.txt chứa tiêu đề poll:\n  ╰─> " + Style.RESET_ALL).strip()
            if not os.path.isfile(name_file):
                print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
                return
        elif opt == 4:
            func_name = "fake typing"
            print(C + "[*] Chế độ Fake typing (gọi là 'nhây')" + Style.RESET_ALL)
            num_threads = int(input(W + "[+] Nhập số lượng ID box:\n  ╰─> " + Style.RESET_ALL).strip())
            for i in range(num_threads):
                tid = input(W + f"[+] Nhập ID box thứ {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
                if tid:
                    thread_ids.append(tid)
            delay = float(input(W + "[+] Nhập delay (s):\n  ╰─> " + Style.RESET_ALL).strip())
            name_file = input(W + "[+] Nhập đường dẫn file nhay.txt chứa tin nhắn:\n  ╰─> " + Style.RESET_ALL).strip()
            if not os.path.isfile(name_file):
                print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
                return
        elif opt == 5:
            func_name = "theme"
            print(C + "[*] Chế độ Thay đổi theme" + Style.RESET_ALL)
            num_threads = int(input(W + "[+] Nhập số lượng ID box:\n  ╰─> " + Style.RESET_ALL).strip())
            for i in range(num_threads):
                tid = input(W + f"[+] Nhập ID box thứ {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
                if tid:
                    thread_ids.append(tid)
            delay = float(input(W + "[+] Nhập delay (s):\n  ╰─> " + Style.RESET_ALL).strip())
        elif opt == 6:
            func_name = "nickname"
            print(C + "[*] Chế độ Đổi biệt danh" + Style.RESET_ALL)
            num_threads = int(input(W + "[+] Nhập số lượng ID box:\n  ╰─> " + Style.RESET_ALL).strip())
            for i in range(num_threads):
                tid = input(W + f"[+] Nhập ID box thứ {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
                if tid:
                    thread_ids.append(tid)
            delay = float(input(W + "[+] Nhập delay (s):\n  ╰─> " + Style.RESET_ALL).strip())
        elif opt == 7:
            func_name = "nhay tag"
            print(C + "[*] Chế độ Nhây tag" + Style.RESET_ALL)
            num_threads = int(input(W + "[+] Nhập số lượng ID box:\n  ╰─> " + Style.RESET_ALL).strip())
            for i in range(num_threads):
                tid = input(W + f"[+] Nhập ID box thứ {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
                if tid:
                    thread_ids.append(tid)
            tag_input = input(W + "[+] Nhập ID người cần tag (cách nhau dấu phẩy):\n  ╰─> " + Style.RESET_ALL).strip()
            tag_ids = [t.strip() for t in tag_input.split(',') if t.strip()]
            if not tag_ids:
                print(R + "✘ Chưa nhập ID tag!" + Style.RESET_ALL)
                return
            delay = float(input(W + "[+] Nhập delay (s):\n  ╰─> " + Style.RESET_ALL).strip())
            name_file = input(W + "[+] Nhập đường dẫn file nhay.txt chứa nội dung:\n  ╰─> " + Style.RESET_ALL).strip()
            if not os.path.isfile(name_file):
                print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
                return
        if not thread_ids:
            print(R + "✘ Chưa nhập ID box nào." + Style.RESET_ALL)
            return
        box(" BẮT ĐẦU XỬ LÝ ", Y2)
        print(C + f"• Số cookie: {len(cookies)}" + Style.RESET_ALL)
        print(C + f"• Số box  : {len(thread_ids)}" + Style.RESET_ALL)
        print(C + f"• Delay   : {delay}s" + Style.RESET_ALL)
        send_messages_with_cookie(
            cookies,
            thread_ids,
            message_files if opt == 1 else [],
            delay,
            option=opt,
            file_path=None,
            contact_uid=None,
            name_file=name_file if opt in [2,3,4,7] else None,
            nickname=None,
            tag_ids=tag_ids if opt == 7 else None,
            func_name=func_name
        )
    except KeyboardInterrupt:
        print(R + "\n[!] Đã dừng chương trình." + Style.RESET_ALL)
    except Exception as e:
        print(R + f"[!] Lỗi: {str(e)}" + Style.RESET_ALL)

# ==========================================
#           PHẦN 2: DISCORD
# ==========================================
class DiscordTool:
    def __init__(self):
        self.tokens = []
        self.delays = {}
        self.kenh_id = ""
        self.nguoi_tag = []
        self.tin_nhan = []
        self.ngon_lines = []
        self.chi_so_tn = 0
        self.fake_typing = False
        self.lock = threading.Lock()
        self.proxies = []
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        self.current_ua_index = 0
        self.proxy_index = 0
        self.token_status = {}

    def load_proxies(self, proxy_file="proxy.txt"):
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            if self.proxies:
                print(f"Đã tải {len(self.proxies)} proxy")
        else:
            print("Không có file proxy.txt, sẽ không dùng proxy")

    def get_random_ua(self):
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return self.user_agents[self.current_ua_index]

    def get_proxy(self):
        if not self.proxies:
            return None
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        proxy = self.proxies[self.proxy_index]
        return {"http": proxy, "https": proxy}

    def doc_token(self):
        while True:
            file_token = input("Nhap file chua token (mỗi token 1 dòng): ").strip()
            if os.path.exists(file_token):
                with open(file_token, 'r', encoding='utf-8') as f:
                    self.tokens = [line.strip() for line in f if line.strip()]
                if not self.tokens:
                    print("File token rong!")
                    continue
                print(f"Da doc {len(self.tokens)} token")
                break
            print("File khong ton tai!")

    def nhap_delay(self):
        while True:
            try:
                delay_chung = float(input("Nhap delay chung (giay): "))
                if delay_chung < 0.5:
                    print("Delay qua thap, de nghi >= 0.5s de tranh rate limit")
                    continue
                break
            except:
                print("Nhap so!")
        for token in self.tokens:
            self.delays[token] = delay_chung

    def nhap_kenh(self):
        self.kenh_id = input("Nhap ID kenh: ").strip()

    def nhap_tag(self):
        print("Nhap ID nguoi tag (done de dung):")
        while True:
            user_id = input().strip()
            if user_id.lower() == 'done':
                break
            if user_id:
                self.nguoi_tag.append(f"<@{user_id}>")
        if self.nguoi_tag:
            print(f"Da tag {len(self.nguoi_tag)} nguoi")

    def hoi_fake_typing(self):
        while True:
            choice = input("Fake typing? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                self.fake_typing = True
                print("Da bat fake typing")
                break
            elif choice in ['n', 'no']:
                self.fake_typing = False
                print("Da tat fake typing")
                break

    def doc_tin_nhan(self):
        file_tn = input("Nhap file chua tin nhan: ").strip()
        if os.path.exists(file_tn):
            with open(file_tn, 'r', encoding='utf-8') as f:
                self.tin_nhan = [line.strip() for line in f if line.strip()]
            if not self.tin_nhan:
                print("File tin nhan rong!")
                sys.exit()
            print(f"Da doc {len(self.tin_nhan)} tin nhan")
        else:
            print("File khong ton tai!")
            sys.exit()

    def doc_ngon(self):
        file_ngon = input("Nhap file chua ngon: ").strip()
        if os.path.exists(file_ngon):
            with open(file_ngon, 'r', encoding='utf-8') as f:
                self.ngon_lines = [line.strip() for line in f if line.strip()]
            if not self.ngon_lines:
                print("File ngon rong!")
                sys.exit()
            print(f"Da doc {len(self.ngon_lines)} cau ngon")
        else:
            print("File khong ton tai!")
            sys.exit()

    def lay_tin_nhan_nhay(self):
        with self.lock:
            if not self.tin_nhan:
                return "# Hello"
            tin = self.tin_nhan[self.chi_so_tn]
            self.chi_so_tn = (self.chi_so_tn + 1) % len(self.tin_nhan)
            if not tin.startswith('#'):
                tin = f"# {tin}"
            if self.nguoi_tag:
                tags = " ".join(self.nguoi_tag)
                if random.choice([True, False]):
                    tin = f"{tin} {tags}"
                else:
                    tin = tin.replace("# ", f"# {tags} ", 1)
            return tin

    def lay_tin_nhan_ngon(self):
        with self.lock:
            if not self.ngon_lines:
                return "Ngon day!"
            return "\n".join(self.ngon_lines)

    def tao_headers(self, token, ua=None):
        if ua is None:
            ua = self.get_random_ua()
        return {
            'Authorization': token,
            'User-Agent': ua,
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def check_token(self, token):
        headers = self.tao_headers(token)
        proxy = self.get_proxy()
        try:
            resp = requests.get('https://discord.com/api/v9/users/@me', headers=headers, proxies=proxy, timeout=10)
            if resp.status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def fake_typing_request(self, token):
        if not self.fake_typing:
            return
        headers = self.tao_headers(token)
        proxy = self.get_proxy()
        try:
            requests.post(f'https://discord.com/api/v9/channels/{self.kenh_id}/typing',
                         headers=headers, proxies=proxy, timeout=10)
        except:
            pass

    def lay_ten_kenh(self, token):
        headers = self.tao_headers(token)
        proxy = self.get_proxy()
        try:
            response = requests.get(f'https://discord.com/api/v9/channels/{self.kenh_id}',
                                  headers=headers, proxies=proxy, timeout=10)
            if response.status_code == 200:
                return response.json().get('name', 'Unknown')
        except:
            pass
        return 'Unknown'

    def send_message_with_retry(self, token, content, max_retries=3):
        headers = self.tao_headers(token)
        proxy = self.get_proxy()
        data = {'content': content}
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f'https://discord.com/api/v9/channels/{self.kenh_id}/messages',
                    headers=headers,
                    json=data,
                    proxies=proxy,
                    timeout=15
                )
                if response.status_code == 200:
                    return True, None
                elif response.status_code == 429:
                    retry_after = response.json().get('retry_after', 5)
                    wait = retry_after + random.uniform(0.5, 1.5)
                    print(f"Rate limit, chờ {wait:.2f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                elif response.status_code in [401, 403, 404]:
                    return False, f"Lỗi {response.status_code}"
                else:
                    time.sleep(2 ** attempt + random.random())
                    continue
            except Exception as e:
                time.sleep(2 ** attempt + random.random())
                continue
        return False, "Hết số lần thử"

    def gui_tin_nhay(self, token):
        token_hien = token[:4] + "..." + token[-4:]
        base_delay = self.delays.get(token, 5.0)
        if not self.check_token(token):
            print(R + f"[{token_hien}] Token không hợp lệ hoặc đã chết!" + W)
            return
        ten_kenh = self.lay_ten_kenh(token)
        if ten_kenh == 'Unknown':
            print(Y + f"[{token_hien}] Không lấy được tên kênh, có thể token không có quyền" + W)
        else:
            print(G + f"[{token_hien}] Token hợp lệ, kênh: {ten_kenh}" + W)
        while True:
            if random.random() < 0.3:
                self.fake_typing_request(token)
            delay = base_delay + random.uniform(-0.5, 0.5)
            if delay < 0.5:
                delay = 0.5
            time.sleep(delay)
            tin = self.lay_tin_nhan_nhay()
            ok, err = self.send_message_with_retry(token, tin)
            if ok:
                anon_sent(f"token #{token_hien}", "tin nhắn", f"nhóm {ten_kenh}", tin)
            else:
                if "401" in err or "403" in err:
                    print(R + f"[{token_hien}] Token lỗi, dừng!" + W)
                    return
                else:
                    print(R + f"[{token_hien}] Gửi thất bại: {err}" + W)
            time.sleep(random.uniform(0, 0.5))

    def gui_tin_ngon(self, token):
        token_hien = token[:4] + "..." + token[-4:]
        base_delay = self.delays.get(token, 5.0)
        if not self.check_token(token):
            print(R + f"[{token_hien}] Token không hợp lệ hoặc đã chết!" + W)
            return
        ten_kenh = self.lay_ten_kenh(token)
        tin = self.lay_tin_nhan_ngon()
        while True:
            if self.fake_typing:
                self.fake_typing_request(token)
            delay = base_delay + random.uniform(-0.5, 0.5)
            if delay < 0.5:
                delay = 0.5
            time.sleep(delay)
            ok, err = self.send_message_with_retry(token, tin)
            if ok:
                anon_sent(f"token #{token_hien}", "ngôn", f"nhóm {ten_kenh}", tin, prefix="ngôn #")
            else:
                if "401" in err or "403" in err:
                    print(R + f"[{token_hien}] Token lỗi, dừng!" + W)
                    return
                else:
                    print(R + f"[{token_hien}] Gửi thất bại: {err}" + W)
            time.sleep(random.uniform(0, 0.5))

    def chay_nhay(self):
        self.doc_token()
        self.load_proxies()
        self.nhap_kenh()
        self.nhap_tag()
        self.hoi_fake_typing()
        self.doc_tin_nhan()
        self.nhap_delay()
        print("\n" + "─" * 50)
        print(">>> BAT DAU NHAY (nâng cấp)...")
        print(f"├─ Token: {len(self.tokens)}")
        print(f"├─ Tin nhan: {len(self.tin_nhan)}")
        if self.proxies:
            print(f"├─ Proxy: {len(self.proxies)}")
        print("─" * 50)
        threads = []
        for token in self.tokens:
            thread = threading.Thread(target=self.gui_tin_nhay, args=(token,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\n[!] Da dung chuong trinh!")

    def chay_ngon(self):
        self.doc_token()
        self.load_proxies()
        self.nhap_kenh()
        self.doc_ngon()
        self.nhap_delay()
        print("\n" + "─" * 50)
        print(">>> BAT DAU TREO NGON (nâng cấp)...")
        print(f"├─ Token: {len(self.tokens)}")
        print(f"├─ Cau ngon: {len(self.ngon_lines)} (gui tat ca trong 1 tin)")
        if self.proxies:
            print(f"├─ Proxy: {len(self.proxies)}")
        print("─" * 50)
        threads = []
        for token in self.tokens:
            thread = threading.Thread(target=self.gui_tin_ngon, args=(token,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\n[!] Da dung chuong trinh!")

def dc_exec(opt):
    tool = DiscordTool()
    if opt == 1:
        tool.chay_nhay()
    elif opt == 2:
        tool.chay_ngon()

# ==========================================
#           PHẦN 3: ZALO
# ==========================================
try:
    from zlapi import ZaloAPI, ThreadType, Message
    from zlapi.models import Mention, MultiMention, MessageStyle, MultiMsgStyle
    ZALO_AVAILABLE = True
except ImportError:
    ZALO_AVAILABLE = False
    class ZaloAPI:
        def __init__(self, *args, **kwargs): pass
        def fetchAllGroups(self): return type('obj', (object,), {'gridVerMap': {}})()
        def fetchGroupInfo(self, gid): return type('obj', (object,), {'gridInfoMap': {gid: {'name': 'Unknown', 'memVerList': []}}})()
        def fetchUserInfo(self, uid): return type('obj', (object,), {'changed_profiles': {uid: {'userId': uid, 'displayName': 'User'}}})()
        def send(self, *args, **kwargs): pass
    class ThreadType: GROUP = 1
    class Message: pass
    class Mention: pass
    class MultiMention: pass
    class MessageStyle: pass
    class MultiMsgStyle: pass

def normalize_ttl_value(ttl):
    if ttl is None: return None
    try: t = int(ttl)
    except: return None
    if t <= 0: return None
    if t < 1000: return t * 1000
    return t

class Bot(ZaloAPI):
    def __init__(self, imei, session_cookies, acc_index, delay, message_text, use_color=True, ttl=None):
        super().__init__("dummy_api_key", "dummy_secret_key", imei, session_cookies)
        self.acc_index = acc_index
        self.delay = delay
        self.stop_event = threading.Event()
        self.message_text = message_text
        self.use_color = use_color
        self.ttl = ttl
    def fetch_groups(self):
        groups_data = []
        try:
            all_groups = self.fetchAllGroups()
            for gid, _ in all_groups.gridVerMap.items():
                ginfo = super().fetchGroupInfo(gid)
                gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
                groups_data.append({"id": gid, "name": gname})
        except Exception as e:
            print(f"[Acc {self.acc_index}] Lỗi lấy nhóm: {e}")
        return groups_data
    def send_spam(self, group_id, group_name=None):
        text = self.message_text.strip()
        mention = Mention("-1", length=len(text), offset=0)
        style = MultiMsgStyle([
            MessageStyle(offset=0, length=10000, style="color", color=random.choice(COLOR_LIST), auto_format=False),
            MessageStyle(offset=0, length=10000, style="font", size="100", auto_format=False),
        ])
        try:
            while not self.stop_event.is_set():
                self.send(Message(text=text, mention=mention, style=style),
                          thread_id=group_id,
                          thread_type=ThreadType.GROUP,
                          ttl=self.ttl if self.ttl else None)
                anon_sent("tool", "ngôn", f"nhóm {group_id}", text, prefix="ngôn #")
                time.sleep(self.delay)
        except Exception as e:
            print(f"Lỗi khi spam: {e}")

def run_multi_acc():
    try: num_acc = int(input(" Nhập số lượng acc: ").strip())
    except: return
    bots = []
    for i in range(num_acc):
        imei = input("Imei: ").strip()
        cookie_str = input("Cookie: ").strip()
        file_txt = input("File(.txt): ").strip()
        try: delay = int(input("Delay: ").strip() or "5")
        except: delay = 5
        ttl_input = input("Ttl (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None
        try: cookies = json.loads(cookie_str)
        except: continue
        message_text = readf(file_txt)
        bot = Bot(imei, cookies, i+1, delay, message_text, ttl=ttl)
        bots.append(bot)
        groups = bot.fetch_groups()
        if not groups: continue
        print("\nDanh sách nhóm:")
        for idx, g in enumerate(groups, 1):
            print(f"{idx}. {g['name']} (ID: {g['id']})")
        choice_str = input(" Chọn nhóm: ").strip()
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        for choice in choices:
            if 1 <= choice <= len(groups):
                gid = groups[choice-1]['id']
                gname = groups[choice-1]['name']
                threading.Thread(target=bot.send_spam, args=(gid,gname)).start()
    if not bots:
        print("❌ Không có acc nào hợp lệ.")
    while True:
        time.sleep(1)

class TagBot(ZaloAPI):
    def __init__(self, imei=None, session_cookies=None):
        super().__init__("dummy_api_key", "dummy_secret_key", imei, session_cookies)
        self.running = False
    def fetchGroupInfo(self):
        try:
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id, _ in all_groups.gridVerMap.items():
                group_info = super().fetchGroupInfo(group_id)
                group_name = group_info.gridInfoMap[group_id]["name"]
                group_list.append({'id': group_id, 'name': group_name})
            return group_list
        except Exception as e:
            print(f"❌ Lỗi khi lấy danh sách nhóm: {e}")
            return []
    def fetchGroupMembers(self, group_id):
        try:
            group_info = super().fetchGroupInfo(group_id)
            mem_ver_list = group_info.gridInfoMap[group_id]["memVerList"]
            member_ids = [mem.split("_")[0] for mem in mem_ver_list]
            members = []
            for user_id in member_ids:
                try:
                    user_info = self.fetchUserInfo(user_id)
                    user_data = user_info.changed_profiles[user_id]
                    members.append({'id': user_data['userId'], 'name': user_data['displayName']})
                except Exception:
                    members.append({'id': user_id, 'name': f"[Không lấy được tên {user_id}]"})
            return members
        except Exception as e:
            print(f"❌ Lỗi khi lấy danh sách thành viên: {e}")
            return []
    def send_message_multi(self, thread_id, message_text, users):
        try:
            mentions = []
            formatted_message = (message_text or "").rstrip() + " "
            for uid in users:
                user_info = self.fetchUserInfo(uid)
                user_name = user_info.changed_profiles[uid]['displayName']
                tag_text = f"@{user_name}"
                offset = len(formatted_message)
                formatted_message += tag_text + " "
                mentions.append(Mention(uid=uid, length=len(tag_text), offset=offset, auto_format=False))
            multi_mention = MultiMention(mentions) if mentions else None
            style = MultiMsgStyle([
                MessageStyle(offset=0, length=len(formatted_message), style="color", color=random.choice(COLOR_LIST), auto_format=False),
                MessageStyle(offset=0, length=len(formatted_message), style="font", size="100", auto_format=False),
            ])
            self.send(
                Message(text=formatted_message, mention=multi_mention, style=style),
                thread_id=thread_id,
                thread_type=ThreadType.GROUP
            )
            anon_sent("tool", "tin nhắn", f"nhóm {thread_id}", message_text)
        except Exception as e:
            print(f"❌ Lỗi khi gửi: {e}")
    def send_message_all(self, thread_id, message_text):
        try:
            tag_text = "@All"
            formatted_message = (message_text or "").rstrip() + " " + tag_text
            offset = len(formatted_message) - len(tag_text)
            mention = Mention(uid="-1", length=len(tag_text), offset=offset, auto_format=False)
            multi_mention = MultiMention([mention])
            style = MultiMsgStyle([
                MessageStyle(offset=0, length=len(formatted_message), style="color", color=random.choice(COLOR_LIST), auto_format=False),
                MessageStyle(offset=0, length=len(formatted_message), style="font", size="100", auto_format=False),
            ])
            self.send(
                Message(text=formatted_message, mention=multi_mention, style=style),
                thread_id=thread_id,
                thread_type=ThreadType.GROUP
            )
            anon_sent("tool", "tin nhắn", f"nhóm {thread_id} (@All)", message_text)
        except Exception as e:
            print(f"❌ Lỗi khi gửi @All: {e}")
    def send_file_content(self, thread_id, filename, delay, users):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
            if not lines:
                print("❌ File rỗng hoặc không có nội dung.")
                return
            self.running = True
            while self.running:
                for line in lines:
                    if not self.running:
                        break
                    if users == ["@all"]:
                        self.send_message_all(thread_id, line)
                    else:
                        self.send_message_multi(thread_id, line, users)
                    time.sleep(delay)
            print(f"✅ Hoàn thành gửi nội dung từ file {filename} vào nhóm {thread_id}")
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file: {filename}")
        except Exception as e:
            print(f"❌ Lỗi khi đọc file hoặc gửi tin nhắn: {e}")
    def stop_sending(self):
        self.running = False
        print("🚦 Đã dừng gửi tin nhắn.")

def run_tag_spam():
    imei = input("IMEI : ").strip()
    cookie_str = input("Cookie : ").strip()
    try: cookies = json.loads(cookie_str)
    except: print("Cookie không hợp lệ"); return
    client = TagBot(imei, cookies)
    groups = client.fetchGroupInfo()
    if not groups: return
    print("\nDanh sách nhóm:")
    for idx, g in enumerate(groups, 1):
        print(f"{idx}. {g['name']} - ID: {g['id']}")
    choice_str = input("\n Nhập số nhóm muốn chọn (vd: 1,2,3): ")
    choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
    selected_groups = [groups[c-1] for c in choices if 1 <= c <= len(groups)]
    if not selected_groups: return
    filename = input("📄 Nhập tên file chứa tin nhắn (ví dụ: tag.txt): ").strip()
    try: delay = float(input("⏳ Nhập delay (giây): ").strip() or "5")
    except: delay = 5
    for group in selected_groups:
        members = client.fetchGroupMembers(group['id'])
        print(f"\nThành viên nhóm {group['name']}:")
        for i, m in enumerate(members, 1):
            print(f"{i}. {m['name']} (ID: {m['id']})")
        choice = input("Nhập số thành viên để tag (0 để bỏ qua, all để @All): ").strip()
        if choice.lower() == "0":
            users = []
        elif choice.lower() == "all":
            users = ["@all"]
        else:
            users = [members[int(x.strip()) - 1]['id'] for x in choice.split(",") if x.strip().isdigit()]
        send_thread = threading.Thread(target=client.send_file_content, args=(group['id'], filename, delay, users))
        send_thread.daemon = True
        send_thread.start()
    input("Nhấn Enter để quay lại menu...")

class TreongonBot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies,
                 delay=5, message_text="", ttl=None,
                 media_source="videos.txt"):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.delay = delay
        self.message_text = message_text
        self.ttl = int(ttl) if ttl is not None else None
        self.media_source = media_source
        self.running_flag = threading.Event()
        self.running_flag.set()
        self.thumb_url = None
        self.font_size = 500
        self.color_mode = 'y'
    def spam_messages(self, thread_id, thread_type, ttl=None):
        while self.running_flag.is_set():
            try:
                self.setTyping(thread_id, thread_type)
                time.sleep(4)
                vids = readl(self.media_source)
                if vids:
                    url = random.choice(vids)
                    thumb = self.thumb_url if self.thumb_url else ""
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    self.sendRemoteVideo(
                        url, thumb, duration="100000",
                        thread_id=thread_id, thread_type=thread_type,
                        width=1920, height=1080,
                        ttl=ttl_to_send
                    )
                if self.message_text:
                    lines = self.message_text.strip().splitlines()
                    styles = []
                    formatted_text = ""
                    offset = 0
                    if self.color_mode == 'n':
                        chosen_color = random.choice(COLOR_LIST)
                    for line in lines:
                        color = random.choice(COLOR_LIST) if self.color_mode == 'y' else chosen_color
                        line_text = line + "\n"
                        formatted_text += line_text
                        styles.append(MessageStyle(offset=offset, length=len(line_text), style="color", color=color, auto_format=False))
                        styles.append(MessageStyle(offset=offset, length=len(line_text), style="font", size=str(self.font_size), auto_format=False))
                        offset += len(line_text)
                    style = MultiMsgStyle(styles)
                    mention = Mention("-1", length=len(formatted_text), offset=0)
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    self.send(Message(text=formatted_text, mention=mention, style=style),
                              thread_id=thread_id, thread_type=thread_type,
                              ttl=ttl_to_send)
                anon_sent("tool", "ngôn + video", f"nhóm {thread_id}", self.message_text, prefix="ngôn #")
            except Exception as e:
                print(f"Lỗi: {e}")
            time.sleep(self.delay)

def run_treongonbot():
    try: num_acc = int(input(" Nhập số lượng acc: ").strip())
    except: return
    bots = []
    for i in range(num_acc):
        imei = input("Imei: ").strip()
        cookie_str = input("Cookie: ").strip()
        try: cookies = json.loads(cookie_str)
        except: continue
        file_txt = input("File(.txt): ").strip()
        message_text = readf(file_txt)
        try: delay = int(input("Delay: ").strip() or "5")
        except: delay = 5
        ttl_input = input("Ttl (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None
        media_source = "videos.txt"
        thumb_url = input("👉 Nhập URL ảnh làm bìa video: ").strip()
        font_size_input = input("👉 Nhập size chữ (tối đa 500, mặc định 500): ").strip()
        font_size = int(font_size_input) if font_size_input.isdigit() else 500
        bot = TreongonBot("api", "secret", imei, cookies, delay, message_text, ttl, media_source=media_source)
        bot.thumb_url = thumb_url
        bot.font_size = font_size
        color_choice = input("👉 Chọn chế độ màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        bot.color_mode = 'y' if color_choice == 'y' else 'n'
        bots.append(bot)
        groups = []
        try:
            all_groups = bot.fetchAllGroups()
            for gid, _ in all_groups.gridVerMap.items():
                ginfo = bot.fetchGroupInfo(gid)
                gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
                groups.append({"id": gid, "name": gname})
        except: pass
        if not groups: continue
        print("\nDanh sách nhóm:")
        for idx, g in enumerate(groups, 1):
            print(f"{idx}. {g['name']} (ID: {g['id']})")
        choice_str = input(" Chọn nhóm (vd: 1,2,3): ").strip()
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        for choice in choices:
            if 1 <= choice <= len(groups):
                gid = groups[choice-1]['id']
                threading.Thread(target=bot.spam_messages, args=(gid, ThreadType.GROUP, ttl), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

class TreongonTextBot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies,
                 delay=5, message_text="", ttl=None):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.delay = delay
        self.message_text = message_text
        self.ttl = int(ttl) if ttl is not None else None
        self.running_flag = threading.Event()
        self.running_flag.set()
        self.font_size = 500
        self.color_mode = 'y'
    def spam_messages(self, thread_id, thread_type, ttl=None):
        while self.running_flag.is_set():
            try:
                if self.message_text:
                    lines = self.message_text.strip().splitlines()
                    styles = []
                    formatted_text = ""
                    offset = 0
                    if self.color_mode == 'n':
                        chosen_color = random.choice(COLOR_LIST)
                    for line in lines:
                        color = random.choice(COLOR_LIST) if self.color_mode == 'y' else chosen_color
                        line_text = line + "\n"
                        formatted_text += line_text
                        styles.append(MessageStyle(offset=offset, length=len(line_text), style="color", color=color, auto_format=False))
                        styles.append(MessageStyle(offset=offset, length=len(line_text), style="font", size=str(self.font_size), auto_format=False))
                        offset += len(line_text)
                    style = MultiMsgStyle(styles)
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    self.send(Message(text=formatted_text, style=style),
                              thread_id=thread_id, thread_type=thread_type,
                              ttl=ttl_to_send)
                anon_sent("tool", "ngôn", f"nhóm {thread_id}", self.message_text, prefix="ngôn #")
            except Exception as e:
                print(f"Lỗi: {e}")
            time.sleep(self.delay)

def run_treongon_text():
    try: num_acc = int(input(" Nhập số lượng acc: ").strip())
    except: return
    bots = []
    for i in range(num_acc):
        imei = input("Imei: ").strip()
        cookie_str = input("Cookie: ").strip()
        try: cookies = json.loads(cookie_str)
        except: continue
        file_txt = input("File(.txt): ").strip()
        message_text = readf(file_txt)
        try: delay = int(input("Delay: ").strip() or "5")
        except: delay = 5
        ttl_input = input("Ttl (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None
        bot = TreongonTextBot("api", "secret", imei, cookies, delay, message_text, ttl)
        font_size_input = input("👉 Nhập size chữ (tối đa 500, mặc định 500): ").strip()
        bot.font_size = int(font_size_input) if font_size_input.isdigit() else 500
        color_choice = input("👉 Chọn chế độ màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        bot.color_mode = 'y' if color_choice == 'y' else 'n'
        bots.append(bot)
        groups = []
        try:
            all_groups = bot.fetchAllGroups()
            for gid, _ in all_groups.gridVerMap.items():
                ginfo = bot.fetchGroupInfo(gid)
                gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
                groups.append({"id": gid, "name": gname})
        except: pass
        if not groups: continue
        print("\nDanh sách nhóm:")
        for idx, g in enumerate(groups, 1):
            print(f"{idx}. {g['name']} (ID: {g['id']})")
        choice_str = input(" Chọn nhóm (vd: 1,2,3): ").strip()
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        for choice in choices:
            if 1 <= choice <= len(groups):
                gid = groups[choice-1]['id']
                threading.Thread(target=bot.spam_messages, args=(gid, ThreadType.GROUP, ttl), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

class TreoAnhBot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies,
                 delay=5, message_text="", ttl=None, image_folder="Gbao",
                 font_size=500, color_mode="y", mentions=None):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.delay = delay
        self.message_text = message_text
        self.ttl = int(ttl) if ttl is not None else None
        self.running_flag = threading.Event()
        self.running_flag.set()
        self.image_folder = image_folder
        self.font_size = font_size
        self.color_mode = color_mode
        self.mentions = mentions or []
    def spam_messages(self, thread_id, thread_type, ttl=None):
        while self.running_flag.is_set():
            try:
                if os.path.exists(self.image_folder):
                    images = [f for f in os.listdir(self.image_folder) if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]
                    if images:
                        img_file = random.choice(images)
                        img_path = os.path.join(self.image_folder, img_file)
                        ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                        self.sendLocalImage(img_path, thread_id=thread_id, thread_type=thread_type, ttl=ttl_to_send)
                if self.message_text:
                    lines = self.message_text.strip().splitlines()
                    styles = []
                    formatted_text = ""
                    offset = 0
                    if self.color_mode == 'n':
                        chosen_color = random.choice(COLOR_LIST)
                    for line in lines:
                        color = random.choice(COLOR_LIST) if self.color_mode == 'y' else chosen_color
                        line_text = line + "\n"
                        formatted_text += line_text
                        styles.append(MessageStyle(offset=offset, length=len(line_text), style="color", color=color, auto_format=False))
                        styles.append(MessageStyle(offset=offset, length=len(line_text), style="font", size=str(self.font_size), auto_format=False))
                        offset += len(line_text)
                    style = MultiMsgStyle(styles)
                    ttl_to_send = normalize_ttl_value(ttl if ttl is not None else self.ttl)
                    multi_mention = None
                    if self.mentions:
                        multi_mention = MultiMention([Mention(uid=uid, length=5, offset=len(formatted_text), auto_format=False) for uid in self.mentions])
                    self.send(Message(text=formatted_text, style=style, mention=multi_mention),
                              thread_id=thread_id, thread_type=thread_type, ttl=ttl_to_send)
                anon_sent("tool", "ảnh + ngôn", f"nhóm {thread_id}", self.message_text, prefix="ngôn #")
            except Exception as e:
                print(f"Lỗi khi gửi ảnh + ngôn: {e}")
            time.sleep(self.delay)

def run_treoanh():
    try: num_acc = int(input(" Nhập số lượng acc: ").strip())
    except: return
    bots = []
    for i in range(num_acc):
        imei = input("Imei: ").strip()
        cookie_str = input("Cookie: ").strip()
        try: cookies = json.loads(cookie_str)
        except: continue
        file_txt = input("File ngôn (.txt): ").strip()
        message_text = readf(file_txt)
        try: delay = int(input("Delay (giây): ").strip() or "5")
        except: delay = 5
        ttl_input = input("TTL (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None
        font_size_input = input("👉 Nhập size chữ (tối đa 500, mặc định 500): ").strip()
        font_size = int(font_size_input) if font_size_input.isdigit() else 500
        color_choice = input("👉 Chọn chế độ màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        color_mode = 'y' if color_choice == 'y' else 'n'
        bot_tmp = ZaloAPI("api", "secret", imei, cookies)
        groups = []
        try:
            all_groups = bot_tmp.fetchAllGroups()
            for gid, _ in all_groups.gridVerMap.items():
                ginfo = bot_tmp.fetchGroupInfo(gid)
                gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
                groups.append({"id": gid, "name": gname})
        except: pass
        if not groups: continue
        print("\nDanh sách nhóm:")
        for idx, g in enumerate(groups, 1):
            print(f"{idx}. {g['name']} (ID: {g['id']})")
        choice_str = input(" Chọn nhóm (vd: 1,2,3): ").strip()
        choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
        for choice in choices:
            if 1 <= choice <= len(groups):
                gid = groups[choice-1]['id']
                tag_all_choice = input("👉 Có tag tất cả thành viên? (y/n): ").strip().lower()
                mentions = []
                if tag_all_choice == "y":
                    try:
                        members = bot_tmp.fetchGroupInfo(gid).gridInfoMap[gid]["memVerList"]
                        mentions = [m.split("_")[0] for m in members]
                    except: pass
                bot = TreoAnhBot("api", "secret", imei, cookies, delay=delay, message_text=message_text, ttl=ttl, image_folder="Gbao", font_size=font_size, color_mode=color_mode, mentions=mentions)
                bots.append(bot)
                threading.Thread(target=bot.spam_messages, args=(gid, ThreadType.GROUP, ttl), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

def zl_exec(opt):
    if not ZALO_AVAILABLE:
        print("⚠️ Thư viện zlapi chưa được cài đặt. Vui lòng cài: pip install zlapi")
        input("Nhấn Enter để quay lại...")
        return
    if opt == 1:
        run_multi_acc()
    elif opt == 2:
        run_tag_spam()
    elif opt == 3:
        run_treongonbot()
    elif opt == 4:
        run_treongon_text()
    elif opt == 5:
        run_treoanh()

# ==========================================
#           PHẦN 4: TELEGRAM (TURBO)
# ==========================================
from concurrent.futures import ThreadPoolExecutor

class TgSpam:
    def __init__(self):
        self.tf = 'token.txt'; self.mc = 4000
        self.st = threading.Event(); self.ec = 0; self.delay = None
        self.infos = {}; self.tags = []; self.tc = 100
        self.turbo = False
        self.session = requests.Session()
        _ad = requests.adapters.HTTPAdapter(pool_connections=1000, pool_maxsize=1000, max_retries=0)
        self.session.mount('https://', _ad); self.session.mount('http://', _ad)

    def load_tokens(self, fn):
        if not os.path.exists(fn): print(f"❌ Không thấy {fn}"); return None
        try:
            with open(fn, 'r', encoding='utf-8') as f:
                return [x.strip() for x in f if x.strip() and not x.startswith('#') and ':' in x]
        except Exception as e: print(f"Lỗi: {e}"); return None

    def get_info(self, tk):
        try:
            r = self.session.get(f"https://api.telegram.org/bot{tk}/getMe", timeout=5)
            if r.status_code == 200 and r.json().get('ok'):
                return r.json()['result'].get('username', f"Bot_{tk.split(':')[0]}")
            return "INVALID"
        except: return "INVALID"

    def load_full(self, fn):
        if not os.path.exists(fn): print(f"❌ Không thấy {fn}"); return None
        try:
            with open(fn, 'r', encoding='utf-8') as f: c = f.read().strip()
            if not c: print("❌ File rỗng"); return None
            if len(c) > self.mc: print(f"❌ Quá {self.mc} ký tự"); return None
            return c
        except Exception as e: print(f"Lỗi: {e}"); return None

    def load_lines(self, fn):
        if not os.path.exists(fn): print(f"❌ Không thấy {fn}"); return None
        try:
            with open(fn, 'r', encoding='utf-8') as f:
                lines = [x.strip() for x in f if x.strip()]
            if not lines: print("❌ File rỗng"); return None
            for i, x in enumerate(lines):
                if len(x) > self.mc: print(f"❌ Dòng {i+1} quá {self.mc} ký tự"); return None
            return lines
        except Exception as e: print(f"Lỗi: {e}"); return None

    def get_ids(self):
        ids = []
        print("\n--- NHẬP ID CHAT ---")
        print(" (ID nhóm/kênh bắt đầu bằng '-')")
        while True:
            raw = input("ID (hoặc 'done'): ").strip()
            if raw.lower() == 'done': break
            cl = raw.replace(" ", "").replace("_", "")
            if cl and cl.lstrip('-').isdigit():
                ids.append(cl); print(f"  ✅ Đã thêm {cl}")
            else: print("  ❌ Không hợp lệ")
        if not ids: print("❌ Không có ID nào"); sys.exit(1)
        return ids

    def get_tags(self):
        tags = []
        print("\n--- NHẬP ID/@USERNAME ĐỂ TAG ---")
        while True:
            t = input("ID/@ (hoặc 'done'): ").strip()
            if t.lower() == 'done': break
            if t and (t.isdigit() or t.startswith('@')):
                tags.append(t); print(f"  ✅ Đã thêm {t}")
            else: print("  ❌ Không hợp lệ")
        return tags

    def send(self, tk, cid, text, no_wait=False):
        if self.st.is_set(): return False, "STOPPED"
        try:
            r = self.session.post(
                f"https://api.telegram.org/bot{tk}/sendMessage",
                data={"chat_id": cid, "text": text, "parse_mode": "HTML"},
                timeout=(3, 10))
            d = r.json()
            if r.status_code == 429:
                if no_wait:
                    return False, "FLOOD"
                wa = d.get('parameters', {}).get('retry_after', 5)
                print(f"    ⚠️ Rate limit, chờ {wa}s"); time.sleep(wa + 0.1)
                return self.send(tk, cid, text, no_wait)
            if d.get('ok'): return True, None
            return False, d.get('description', 'Lỗi')
        except Exception as e: return False, str(e)

    def worker(self, tid, tk, ids, msgs, tag_mode):
        name = self.infos.get(tk, f"T-{tid}")
        cnt = len(msgs); idx = 0
        mode = "FULL" if not tag_mode else "TAG"
        print(f"[{tid}|{name}] Bắt đầu ({mode}|{len(ids)} kênh)")
        while not self.st.is_set():
            cur = msgs[idx % cnt]; final = cur
            if tag_mode and self.tags and random.randint(1, 100) <= self.tc:
                tags = random.sample(self.tags, min(3, len(self.tags)))
                ts = ""
                for t in tags:
                    if t.isdigit(): ts += f' <a href="tg://user?id={t}">Tag</a>'
                    elif t.startswith('@'): ts += f' {t}'
                if len(final) + len(ts) <= self.mc: final += ts
            for cid in ids:
                if self.st.is_set(): return
                ok, err = self.send(tk, cid, final)
                if ok: anon_sent(f"token #{name}", "tin nhắn", f"group {cid}", final)
                elif err != "STOPPED": print(R + f"[{name}] Thất bại | {cid} | {err}" + W)
                if not self.st.is_set(): time.sleep(self.delay)
            idx += 1
            if not self.st.is_set(): time.sleep(1.0)

    def _turbo_worker(self, tid, tk, ids, msgs, tag_mode):
        name = self.infos.get(tk, f"T-{tid}")
        cnt = len(msgs); idx = 0
        mode = "FULL" if not tag_mode else "TAG"
        n_workers = min(800, max(50, len(ids) * 8))
        print(f"[{tid}|{name}] 🔥 TURBO ({mode}|{len(ids)} kênh|workers={n_workers})")
        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            while not self.st.is_set():
                cur = msgs[idx % cnt]; final = cur
                if tag_mode and self.tags:
                    tags = random.sample(self.tags, min(3, len(self.tags)))
                    ts = ""
                    for t in tags:
                        if t.isdigit(): ts += f' <a href="tg://user?id={t}">Tag</a>'
                        elif t.startswith('@'): ts += f' {t}'
                    if len(final) + len(ts) <= self.mc: final += ts
                for cid in ids:
                    if self.st.is_set(): break
                    pool.submit(self._fire, name, tk, cid, final)
                idx += 1

    def _fire(self, name, tk, cid, text):
        if self.st.is_set(): return
        try:
            r = self.session.post(
                f"https://api.telegram.org/bot{tk}/sendMessage",
                data={"chat_id": cid, "text": text, "parse_mode": "HTML"},
                timeout=(2, 5))
            if r.status_code == 200 and r.json().get('ok'):
                anon_sent(f"token #{name}", "tin nhắn", f"group {cid}", text)
        except: pass

    def listener(self):
        while not self.st.is_set():
            try:
                ln = sys.stdin.readline().strip()
                if ln.lower() == 'stop': print("\n🛑 Dừng..."); self.st.set(); break
                if not ln:
                    self.ec += 1
                    if self.ec >= 2: print("\n🛑 Dừng..."); self.st.set(); break
                    else: sys.stdout.write("  (Enter lần nữa để dừng)\r"); sys.stdout.flush()
                else: self.ec = 0
            except: pass

    def run(self, mode):
        print(C + " ⚡ TELEGRAM TOOL (TURBO) ⚡" + W)
        fn = input(f"File token (mặc định '{self.tf}'): ").strip() or self.tf
        tokens = self.load_tokens(fn)
        if not tokens: return
        valid = []
        for tk in tokens:
            name = self.get_info(tk)
            if name != "INVALID":
                self.infos[tk] = name; valid.append(tk); print(f"  ✅ {name}")
            else: print(f"  ❌ {tk[:20]}...")
        if not valid: print("❌ Không có token hợp lệ"); return
        print(f"✅ Có {len(valid)} token.")
        ids = self.get_ids()
        msgs = None
        if mode == 1:
            print("\n--- TREO NGÔN (FULL FILE) ---")
            f = input("File nội dung: ").strip()
            c = self.load_full(f)
            if not c: return
            msgs = [c]; tag = False
        else:
            print("\n--- NHÂY TAG (TỪNG DÒNG) ---")
            self.tags = self.get_tags()
            if self.tags: print(f"✅ Sẽ tag {len(self.tags)} mục tiêu.")
            f = input("File nội dung (mỗi dòng 1 tin): ").strip()
            lines = self.load_lines(f)
            if not lines: return
            msgs = lines; tag = True

        while True:
            try:
                dl = input("Delay (giây) — >0 thường | 0 không chờ | <0 🔥TURBO siêu nhanh: ").strip()
                if not dl: print("❌ Phải nhập delay!"); continue
                self.delay = float(dl)
                break
            except ValueError: print("❌ Nhập số!")

        self.turbo = self.delay < 0
        if self.turbo:
            print(R + "\n🔥🔥 TURBO MODE — bỏ mọi sleep, gửi song song 🔥🔥" + W)
            print(Y + "⚠️ Nạp càng nhiều token càng nhanh — 1 token Telegram chặn ~30 msg/s/kênh" + W)

        tag_str = 'TURBO' if self.turbo else f'delay {self.delay}s'
        print(f"\n--- BẮT ĐẦU ({len(valid)} luồng, {tag_str}) ---")
        threading.Thread(target=self.listener, daemon=True).start()
        for i, tk in enumerate(valid):
            target = self._turbo_worker if self.turbo else self.worker
            threading.Thread(target=target, args=(i + 1, tk, ids, msgs, tag), daemon=True).start()

        print("\n   Dừng: gõ 'stop' + Enter, Enter 2 lần, hoặc Ctrl+C.")
        try:
            while not self.st.is_set(): time.sleep(1)
        except KeyboardInterrupt: self.st.set()
        print("\n✔️ ĐÃ DỪNG.")

def tg_exec(opt):
    TgSpam().run(opt)

# ==========================================
#           PHẦN 5: TIKTOK
# ==========================================
import base64 as tiktok_base64
import uuid as tiktok_uuid
import httpx
from cryptography.hazmat.primitives import hashes as crypto_hashes
from cryptography.hazmat.primitives.asymmetric import ec as crypto_ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.backends import default_backend as crypto_default_backend

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
IM_AID = "1988"
SEND_MSG_FULL_URL = "https://im-api-sg.tiktok.com/v1/message/send"

def encode_varint(value: int) -> bytes:
    bits = value & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while bits >= 0x80:
        out.append((bits & 0x7F) | 0x80)
        bits >>= 7
    out.append(bits & 0x7F)
    return bytes(out)

def encode_tag(field_number: int, wire_type: int) -> bytes:
    return encode_varint((field_number << 3) | wire_type)

def pb_varint(field_num: int, val: int) -> bytes:
    if not val:
        return b""
    return encode_tag(field_num, 0) + encode_varint(val)

def pb_bytes(field_num: int, data: bytes) -> bytes:
    if not data:
        return b""
    return encode_tag(field_num, 2) + encode_varint(len(data)) + data

def pb_str(field_num: int, text: str) -> bytes:
    if not text:
        return b""
    return pb_bytes(field_num, text.encode("utf-8"))

def pb_kv(key: str, val: str) -> bytes:
    return pb_bytes(15, pb_str(1, key) + pb_str(2, val))

def decode_varint(data: bytes, idx: int):
    res = 0
    shift = 0
    while True:
        if idx >= len(data):
            raise IndexError()
        b = data[idx]
        idx += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return res, idx

def parse_proto_fields(data: bytes):
    fields = []
    idx = 0
    n = len(data)
    while idx < n:
        try:
            tag, idx = decode_varint(data, idx)
            fn = tag >> 3
            wt = tag & 0x07
            if wt == 0:
                val, idx = decode_varint(data, idx)
                fields.append((fn, wt, val))
            elif wt == 2:
                length, idx = decode_varint(data, idx)
                val = data[idx : idx + length]
                idx += length
                fields.append((fn, wt, val))
            elif wt == 1:
                idx += 8
            elif wt == 5:
                idx += 4
            else:
                break
        except Exception:
            break
    return fields

def looks_like_title(s: str) -> bool:
    if not s:
        return False
    s = s.replace("\u2068", "").replace("\u2069", "").strip()
    if len(s) < 2 or len(s) > 80:
        return False
    if any(ord(c) < 32 for c in s):
        return False
    if s.isdigit():
        return False
    bad = (
        "aweType", "client_message_id", "source_aid", "im_callback", "avatar",
        "group_type", "deprecated", "conv_set_notification", "involved_user",
        "was_minor_group", "tt-ticket", "Web-Sdk", "device_id", "msToken",
        "verify_", "tos-", "http", "AAA", "BAA", "LMS", "s_v_web", "MS4wLjAB"
    )
    low = s.lower()
    if any(b.lower() in low for b in bad):
        return False
    if len(s) > 28 and " " not in s:
        if sum(c.isalnum() or c in "_-" for c in s) / max(len(s), 1) > 0.92:
            viet = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
            if not any(c in viet for c in low):
                return False
    return True

def extract_group_conversations_pure(data: bytes):
    candidates = []
    def walk(blob: bytes, depth=0):
        if depth > 15 or not blob or len(blob) < 3:
            return
        fields = parse_proto_fields(blob)
        ids_here = []
        titles_here = []
        typ = 0
        src = 0
        for fn, wt, val in fields:
            if wt == 0:
                if fn in (2, 5, 6) and val in (1, 2, 3):
                    typ = val
                if fn == 5 and isinstance(val, int) and val > 10**13:
                    src = val
            elif wt == 2 and isinstance(val, bytes):
                try:
                    s = val.decode("utf-8", errors="ignore").strip()
                    s_clean = s.replace("\u2068", "").replace("\u2069", "").strip()
                    if s.isdigit() and 15 <= len(s) <= 22:
                        ids_here.append(s)
                    elif looks_like_title(s_clean):
                        titles_here.append(s_clean)
                except Exception:
                    pass
                walk(val, depth + 1)
        for cid in ids_here:
            title = titles_here[0] if titles_here else ""
            candidates.append((cid, title, typ, src or int(cid)))
    walk(data)
    try:
        raw = data.decode("latin-1", errors="ignore")
        for m in re.finditer(r"(?<!\d)(\d{15,22})(?!\d)", raw):
            cid = m.group(1)
            candidates.append((cid, "", 0, int(cid)))
    except Exception:
        pass
    best = {}
    for cid, title, typ, src in candidates:
        if cid not in best:
            best[cid] = {
                "id": cid,
                "source_id": src,
                "type": typ,
                "name": title if title else f"Box {cid[-8:]}"
            }
        else:
            if title and (best[cid]["name"].startswith("Box ") or len(title) > len(best[cid]["name"])):
                best[cid]["name"] = title
            if typ and not best[cid]["type"]:
                best[cid]["type"] = typ
    groups = list(best.values())
    groups.sort(key=lambda g: (0 if not g["name"].startswith("Box ") else 1, g["name"].lower()))
    return groups

def random_bogus() -> str:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(chars) for _ in range(32))

def extract_cookie(cookie_str: str, name: str) -> str:
    for part in cookie_str.split(";"):
        kv = part.strip().split("=", 1)
        if len(kv) == 2 and kv[0].strip() == name:
            return kv[1].strip()
    return ""

def b64url(b: bytes) -> str:
    return tiktok_base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")

def generate_p256_key():
    return crypto_ec.generate_private_key(crypto_ec.SECP256R1(), crypto_default_backend())

def p256_uncompressed_point(priv) -> bytes:
    numbers = priv.public_key().public_numbers()
    return b"\x04" + numbers.x.to_bytes(32, "big") + numbers.y.to_bytes(32, "big")

def build_dpop_jwt(priv, htm: str, htu: str) -> str:
    numbers = priv.public_key().public_numbers()
    jwk = {
        "crv": "P-256",
        "kty": "EC",
        "x": b64url(numbers.x.to_bytes(32, "big")),
        "y": b64url(numbers.y.to_bytes(32, "big"))
    }
    header_json = json.dumps({"alg": "ES256", "typ": "dpop+jwt", "jwk": jwk}, separators=(",", ":")).encode("utf-8")
    payload_json = json.dumps({
        "jti": b64url(os.urandom(32)),
        "htm": htm,
        "htu": htu,
        "iat": int(time.time())
    }, separators=(",", ":")).encode("utf-8")
    signing_input = f"{b64url(header_json)}.{b64url(payload_json)}"
    sig_der = priv.sign(signing_input.encode("utf-8"), crypto_ec.ECDSA(crypto_hashes.SHA256()))
    r, s = decode_dss_signature(sig_der)
    return f"{signing_input}.{b64url(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}"

def build_send_metadata_pb(device_id: str, ms_token: str, verify_fp: str, public_key_b64: str) -> bytes:
    pairs = [
        ("aid", IM_AID), ("app_name", "tiktok_web"), ("channel", "web"), ("device_platform", "web_pc"),
        ("device_id", device_id), ("region", "VN"), ("priority_region", "VN"), ("os", "windows"),
        ("referer", "https://www.tiktok.com/messages"), ("root_referer", ""), ("cookie_enabled", "true"),
        ("screen_width", "1920"), ("screen_height", "1080"), ("browser_language", "vi-VN"),
        ("browser_platform", "Win32"), ("browser_name", "Mozilla"), ("browser_version", DEFAULT_USER_AGENT),
        ("browser_online", "true")
    ]
    if verify_fp:
        pairs.append(("verifyFp", verify_fp))
    pairs.extend([
        ("app_language", "vi-VN"), ("webcast_language", "vi-VN"), ("tz_name", "Asia/Ho_Chi_Minh"),
        ("is_page_visible", "true"), ("focus_state", "true"), ("is_fullscreen", "false"), ("history_len", "2"),
        ("user_is_login", "true"), ("data_collection_enabled", "true"), ("from_appID", IM_AID), ("locale", "vi-VN"),
        ("tt-ticket-guard-public-key", public_key_b64), ("tt-ticket-guard-client-data", ""),
        ("tt-ticket-guard-version", "2"), ("tt-ticket-guard-iteration-version", "0"),
        ("tt-ticket-guard-web-version", "1"), ("user_agent", DEFAULT_USER_AGENT)
    ])
    if ms_token:
        pairs.append(("Web-Sdk-Ms-Token", ms_token))
    out = b""
    for k, v in pairs:
        out += pb_kv(k, v)
    return out

class TikTokPureClient:
    def __init__(self, cookie_string: str):
        self.cookie_string = cookie_string.strip()
        headers = {
            "Cookie": self.cookie_string,
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.tiktok.com/",
            "Origin": "https://www.tiktok.com",
        }
        self.r = httpx.Client(base_url="https://www.tiktok.com", headers=headers, timeout=20.0, follow_redirects=True)
        self.r_ia = httpx.Client(base_url="https://im-api-sg.tiktok.com", headers=headers, timeout=20.0, follow_redirects=True)

    def get_self(self):
        for path in ["/tiktok/v1/im/user/profile/", "/api/user/detail/?aid=1988"]:
            try:
                resp = self.r.get(path)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status_code", -1) == 0 or "user" in data or "userInfo" in data:
                        user_obj = data.get("user") or data.get("userInfo", {}).get("user") or {}
                        uid = str(user_obj.get("uid") or user_obj.get("id") or "")
                        if not uid:
                            multi_sids = extract_cookie(self.cookie_string, "multi_sids")
                            if multi_sids and "%3A" in multi_sids:
                                uid = multi_sids.split("%3A")[0].strip()
                            elif multi_sids and ":" in multi_sids:
                                uid = multi_sids.split(":")[0].strip()
                            else:
                                uid = extract_cookie(self.cookie_string, "uid_tt") or extract_cookie(self.cookie_string, "living_user_id") or ""
                        unique_id = str(user_obj.get("unique_id") or user_obj.get("uniqueId") or "user")
                        nickname = str(user_obj.get("nickname") or "User")
                        if uid or unique_id != "user":
                            return {"user_id": uid, "unique_id": unique_id, "nickname": nickname}
            except Exception:
                continue
        uid = extract_cookie(self.cookie_string, "uid_tt") or extract_cookie(self.cookie_string, "living_user_id") or ""
        multi = extract_cookie(self.cookie_string, "multi_sids")
        if multi and "%3A" in multi:
            uid = multi.split("%3A")[0].strip()
        if not uid:
            raise RuntimeError("Cookie TikTok hết hạn hoặc không hợp lệ!")
        return {"user_id": uid, "unique_id": "cookie_user", "nickname": "CookieUser"}

    def get_groups(self):
        device_id = extract_cookie(self.cookie_string, "s_v_web_id") or "verify_msodzfdz_LM6w5Wfo_LJer_4bBr_8hqT_IC0ULF1Unn72"
        ms_token = extract_cookie(self.cookie_string, "msToken")
        verify_fp = extract_cookie(self.cookie_string, "s_v_web_id")
        payload = (
            encode_tag(1, 0) + encode_varint(203)
            + encode_tag(2, 0) + encode_varint(10002)
            + pb_str(3, "1.6.0")
            + encode_tag(4, 2) + encode_varint(0)
            + encode_tag(5, 0) + encode_varint(3)
            + encode_tag(6, 0) + encode_varint(1)
            + pb_bytes(8, b"\xda\x0c\x02\x08\x00")
            + pb_str(9, device_id)
            + pb_str(11, "web")
            + build_send_metadata_pb(device_id, ms_token, verify_fp, "")
            + encode_tag(18, 0) + encode_varint(1)
            + pb_bytes(100, pb_bytes(1, encode_tag(1, 0) + encode_varint(0)))
        )
        headers = {
            "Accept": "application/x-protobuf",
            "Content-Type": "application/x-protobuf",
            "Referer": "https://www.tiktok.com/messages"
        }
        params = {
            "aid": IM_AID,
            "version_code": "1.0.0",
            "app_name": "tiktok_web",
            "device_platform": "web_pc",
            "msToken": ms_token,
            "X-Bogus": random_bogus()
        }
        resp = self.r_ia.post("/v2/message/get_by_user_init", headers=headers, params=params, content=payload)
        if resp.is_error:
            raise RuntimeError(f"Lỗi lấy box TikTok: {resp.status_code}")
        return extract_group_conversations_pure(resp.content)

    def send_group_message(self, conv_id: str, conv_source_id: int, text: str) -> str:
        device_id = extract_cookie(self.cookie_string, "s_v_web_id") or "verify_msodzfdz_LM6w5Wfo_LJer_4bBr_8hqT_IC0ULF1Unn72"
        ms_token = extract_cookie(self.cookie_string, "msToken")
        verify_fp = extract_cookie(self.cookie_string, "s_v_web_id")
        priv = generate_p256_key()
        pub_key_b64 = tiktok_base64.b64encode(p256_uncompressed_point(priv)).decode("utf-8")
        dpop_token = build_dpop_jwt(priv, "POST", SEND_MSG_FULL_URL)
        client_msg_id = str(tiktok_uuid.uuid4())

        tag1 = pb_bytes(5, pb_str(1, "s:mentioned_users"))
        tag2 = pb_bytes(5, pb_str(1, "s:client_message_id") + pb_bytes(2, client_msg_id.encode("utf-8")))
        text_dict = {"aweType": 0, "text": text}
        send_body_pb = (
            pb_str(1, conv_id)
            + pb_varint(2, 2)
            + pb_varint(3, conv_source_id)
            + pb_bytes(4, json.dumps(text_dict).encode("utf-8"))
            + tag1
            + tag2
            + pb_varint(6, 7)
            + pb_str(7, "deprecated")
            + pb_str(8, client_msg_id)
        )
        send_payload_pb = pb_bytes(100, send_body_pb)
        payload = (
            encode_tag(1, 0) + encode_varint(100)
            + encode_tag(2, 0) + encode_varint(10014)
            + pb_str(3, "1.6.0")
            + encode_tag(4, 2) + encode_varint(0)
            + encode_tag(5, 0) + encode_varint(3)
            + encode_tag(6, 0) + encode_varint(1)
            + encode_tag(7, 2) + encode_varint(0)
            + pb_bytes(8, send_payload_pb)
            + pb_str(9, device_id)
            + pb_str(11, "web")
            + build_send_metadata_pb(device_id, ms_token, verify_fp, pub_key_b64)
            + encode_tag(18, 0) + encode_varint(1)
        )
        headers = {
            "Accept": "application/x-protobuf",
            "Content-Type": "application/x-protobuf",
            "Cache-Control": "no-cache",
            "Origin": "https://www.tiktok.com",
            "Referer": "https://www.tiktok.com/messages",
            "tt-ticket-guard-iteration-version": "0",
            "tt-ticket-guard-public-key": pub_key_b64,
            "tt-ticket-guard-version": "2",
            "tt-ticket-guard-web-version": "1",
            "DPoP": dpop_token,
        }
        params = {
            "aid": IM_AID,
            "version_code": "1.0.0",
            "app_name": "tiktok_web",
            "device_platform": "web_pc",
            "ztca-version": "1",
            "ztca-dpop": dpop_token,
            "msToken": ms_token,
            "X-Bogus": random_bogus()
        }
        resp = self.r_ia.post("/v1/message/send", headers=headers, params=params, content=payload)
        if resp.is_error:
            raise RuntimeError(f"Lỗi gửi tin TikTok: {resp.status_code}")
        return client_msg_id

def read_tiktok_cookies_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cookies = [line.strip() for line in f if line.strip()]
        if not cookies:
            raise ValueError("File cookie TikTok rỗng")
        return cookies
    except Exception as e:
        raise Exception(f"Lỗi đọc file TikTok: {str(e)}")

class TikTokSpamTask:
    def __init__(self, task_id, client, groups, mode, content_text, lines, delay, acc_name=""):
        self.task_id = task_id
        self.client = client
        self.groups = groups
        self.mode = mode
        self.content_text = content_text
        self.lines = lines
        self.delay = delay
        self.acc_name = acc_name
        self.running = True
        self.count = 0
        self.line_idx = 0
        self.g_idx = 0
        self.thread = None

    def get_mode_name(self):
        return "TREO" if self.mode == 1 else "NHẢY"

    def run(self):
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        try:
            while self.running:
                group = self.groups[self.g_idx]
                self.g_idx = (self.g_idx + 1) % len(self.groups)
                if self.mode == 1:
                    text = self.content_text
                else:
                    text = self.lines[self.line_idx]
                    self.line_idx = (self.line_idx + 1) % len(self.lines)
                self.count += 1
                short = group["name"][:20]
                try:
                    self.client.send_group_message(group["id"], group["source_id"], text)
                    anon_sent(f"cookie #{self.acc_name}", "thông báo", f"group {short}", text)
                except Exception as e:
                    print(R + f"cookie #{self.acc_name} lỗi gửi | {short} | {e}" + Style.RESET_ALL)
                time.sleep(self.delay)
        except Exception:
            pass

    def stop(self):
        self.running = False

def tik_exec(opt):
    """opt: 1 = treo, 2 = nhảy"""
    print(C + "[*] Chế độ TikTok" + Style.RESET_ALL)
    try:
        cookie_file = input(W + "[+] Nhập đường dẫn file cookie TikTok (mỗi cookie 1 dòng):\n  ╰─> " + Style.RESET_ALL).strip()
        if not os.path.isfile(cookie_file):
            print(R + f"✘ File không tồn tại: {cookie_file}" + Style.RESET_ALL)
            return
        cookies = read_tiktok_cookies_from_file(cookie_file)
        print(G + f"✓ Đã đọc {len(cookies)} cookie TikTok." + Style.RESET_ALL)
    except Exception as e:
        print(R + f"✘ {e}" + Style.RESET_ALL)
        return

    tasks = []
    task_id = 0

    for idx, cookie in enumerate(cookies, 1):
        print(f"{C}{'='*50}{Style.RESET_ALL}")
        print(f"{Y}>>> Tài khoản {idx}/{len(cookies)}{Style.RESET_ALL}")
        client = TikTokPureClient(cookie)
        try:
            info = client.get_self()
            print(f"{G}✓ Login OK: @{info['unique_id']} ({info['nickname']}){Style.RESET_ALL}")
        except Exception as e:
            print(f"{R}✗ Login fail: {e}{Style.RESET_ALL}")
            print(f"{Y}Bỏ qua cookie này...{Style.RESET_ALL}\n")
            continue

        try:
            print(f"{C}Đang quét box...{Style.RESET_ALL}")
            groups = client.get_groups()
        except Exception as e:
            print(f"{R}Lỗi quét box: {e}{Style.RESET_ALL}")
            continue

        if not groups:
            print(f"{R}Không tìm thấy box nào cho acc này{Style.RESET_ALL}")
            continue

        print(f"{G}✓ Tìm thấy {len(groups)} box{Style.RESET_ALL}")
        for i, g in enumerate(groups, 1):
            print(f"  {Y}{i:2}.{Style.RESET_ALL} {W}{g['name']}{Style.RESET_ALL}")
            print(f"      {C}{g['id']}{Style.RESET_ALL}")
        print(f"  {R}0.{Style.RESET_ALL} Bỏ qua acc này")

        try:
            stt_input = input(f"{Y}Chọn STT box (vd: 1 hoặc 1,3,5): {Style.RESET_ALL}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Y}Thoát.{Style.RESET_ALL}")
            return

        if stt_input == "0" or not stt_input:
            print(f"{Y}Bỏ qua acc này.{Style.RESET_ALL}\n")
            continue

        selected = []
        try:
            for p in stt_input.split(","):
                stt = int(p.strip())
                if 1 <= stt <= len(groups):
                    selected.append(groups[stt - 1])
        except ValueError:
            print(f"{R}Nhập số STT{Style.RESET_ALL}")
            continue

        if not selected:
            print(f"{R}Không chọn được box{Style.RESET_ALL}")
            continue

        seen = set()
        uniq = []
        for g in selected:
            if g["id"] not in seen:
                seen.add(g["id"])
                uniq.append(g)
        selected = uniq
        print(f"{G}→ Đã chọn {len(selected)} box{Style.RESET_ALL}")

        content_text = None
        lines = None
        while True:
            try:
                fpath = input(f"{Y}File nội dung: {Style.RESET_ALL}").strip().strip('"').strip("'")
            except (KeyboardInterrupt, EOFError):
                break
            if not fpath or not os.path.exists(fpath):
                print(f"{R}File không tồn tại{Style.RESET_ALL}")
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    raw = f.read()
                if opt == 1:
                    content_text = raw.strip()
                    if not content_text:
                        print(f"{R}File rỗng{Style.RESET_ALL}")
                        continue
                else:
                    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
                    if not lines:
                        print(f"{R}File rỗng{Style.RESET_ALL}")
                        continue
                break
            except Exception as e:
                print(f"{R}Lỗi: {e}{Style.RESET_ALL}")
        else:
            continue

        while True:
            try:
                delay = float(input(f"{Y}Delay (giây): {Style.RESET_ALL}").strip())
                if delay < 0:
                    print(f"{R}Không âm{Style.RESET_ALL}")
                    continue
                break
            except ValueError:
                print(f"{R}Nhập số{Style.RESET_ALL}")
            except (KeyboardInterrupt, EOFError):
                delay = 5.0
                break

        task_id += 1
        task = TikTokSpamTask(task_id, client, selected, opt, content_text, lines, delay, info["unique_id"])
        task.run()
        tasks.append(task)
        print(f"{G}✓ Đã tạo Task {task_id} cho @{info['unique_id']}{Style.RESET_ALL}\n")

    if not tasks:
        print(f"{R}Không có task nào được tạo.{Style.RESET_ALL}")
        return

    print(f"\n{G}{'='*50}{Style.RESET_ALL}")
    print(f"{G}✓ Tổng {len(tasks)} task TikTok đang chạy nền{Style.RESET_ALL}")
    print(f"{C}Ctrl+C để thoát (task vẫn sống đến khi tắt process){Style.RESET_ALL}")
    print(f"{C}Hoặc gõ 'tab' để xem danh sách task{Style.RESET_ALL}\n")

    try:
        while True:
            cmd = input(f"{Y}> {Style.RESET_ALL}").strip().lower()
            if cmd == "tab":
                print(f"{W}=== TASK TIKTOK ĐANG CHẠY ==={Style.RESET_ALL}")
                for i, t in enumerate(tasks, 1):
                    status = "CHẠY" if t.running else "DỪNG"
                    print(f"  {Y}{i}.{Style.RESET_ALL} @{t.acc_name} | {t.get_mode_name()} | count={t.count} | delay={t.delay}s | {status}")
            elif cmd.startswith("stop "):
                try:
                    stt = int(cmd.split()[1])
                    if 1 <= stt <= len(tasks):
                        tasks[stt-1].stop()
                        print(f"{G}Đã dừng task {stt}{Style.RESET_ALL}")
                except Exception:
                    print(f"{R}Nhap: stop 1{Style.RESET_ALL}")
            elif cmd in ("0", "exit", "quit"):
                break
    except (KeyboardInterrupt, EOFError):
        pass

    print(f"{Y}Thoát. Task nền vẫn sống đến khi tắt process.{Style.RESET_ALL}")

# ==========================================
#           CHỨC NĂNG TREO TẤT CẢ APP (19)
# ==========================================
def input_box(prompt, color=W):
    print(color + "╭" + "─" * (len(prompt)+4) + "╮")
    print(color + "│  " + prompt + "  │")
    print(color + "╰" + "─" * (len(prompt)+4) + "╯" + Style.RESET_ALL)
    return input(color + "  ╰─> " + Style.RESET_ALL).strip()

def ask_fb():
    print(C + "\n╔══════════════════════════════════════╗")
    print("║           FACEBOOK                  ║")
    print("╚══════════════════════════════════════╝" + Style.RESET_ALL)
    opt = input(W + "[+] Chọn chức năng (1-7) hoặc 'done' để bỏ qua:\n  ╰─> " + Style.RESET_ALL).strip()
    if opt.lower() == 'done':
        return None
    if not opt.isdigit() or int(opt) not in range(1,8):
        print(R + "✘ Không hợp lệ!" + Style.RESET_ALL)
        return None
    opt = int(opt)

    cookie_file = input(W + "[+] File cookie:\n  ╰─> " + Style.RESET_ALL).strip()
    if not os.path.isfile(cookie_file):
        print(R + f"✘ File không tồn tại: {cookie_file}" + Style.RESET_ALL)
        return None
    cookies = read_cookies_from_file(cookie_file)

    num_threads = input(W + "[+] Số ID box:\n  ╰─> " + Style.RESET_ALL).strip()
    if not num_threads.isdigit():
        print(R + "✘ Nhập số!" + Style.RESET_ALL)
        return None
    thread_ids = []
    for i in range(int(num_threads)):
        tid = input(W + f"[+] ID box {i+1}:\n  ╰─> " + Style.RESET_ALL).strip()
        if tid:
            thread_ids.append(tid)
    if not thread_ids:
        print(R + "✘ Chưa nhập ID!" + Style.RESET_ALL)
        return None

    delay = input(W + "[+] Delay (s):\n  ╰─> " + Style.RESET_ALL).strip()
    try:
        delay = float(delay)
    except:
        print(R + "✘ Delay không hợp lệ!" + Style.RESET_ALL)
        return None

    message_files = []
    name_file = None
    tag_ids = []

    if opt == 1:
        file_txt = input(W + "[+] File nội dung:\n  ╰─> " + Style.RESET_ALL).strip()
        if not os.path.isfile(file_txt):
            print(R + f"✘ File không tồn tại: {file_txt}" + Style.RESET_ALL)
            return None
        message_files = [file_txt]
    elif opt == 2:
        name_file = input(W + "[+] File nhay.txt (tên nhóm):\n  ╰─> " + Style.RESET_ALL).strip()
        if not os.path.isfile(name_file):
            print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
            return None
    elif opt == 3:
        name_file = input(W + "[+] File poll.txt (tiêu đề):\n  ╰─> " + Style.RESET_ALL).strip()
        if not os.path.isfile(name_file):
            print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
            return None
    elif opt == 4:
        name_file = input(W + "[+] File nhay.txt (tin nhắn):\n  ╰─> " + Style.RESET_ALL).strip()
        if not os.path.isfile(name_file):
            print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
            return None
    elif opt == 7:
        tag_input = input(W + "[+] ID người tag (cách dấu phẩy):\n  ╰─> " + Style.RESET_ALL).strip()
        tag_ids = [t.strip() for t in tag_input.split(',') if t.strip()]
        name_file = input(W + "[+] File nhay.txt (nội dung):\n  ╰─> " + Style.RESET_ALL).strip()
        if not os.path.isfile(name_file):
            print(R + f"✘ File không tồn tại: {name_file}" + Style.RESET_ALL)
            return None

    return {
        'opt': opt,
        'cookies': cookies,
        'thread_ids': thread_ids,
        'delay': delay,
        'message_files': message_files,
        'name_file': name_file,
        'tag_ids': tag_ids
    }

def ask_dc():
    print(C + "\n╔══════════════════════════════════════╗")
    print("║           DISCORD                   ║")
    print("╚══════════════════════════════════════╝" + Style.RESET_ALL)
    opt = input(W + "[+] Chọn (8: nhây, 9: treo ngôn) hoặc 'done':\n  ╰─> " + Style.RESET_ALL).strip()
    if opt.lower() == 'done':
        return None
    if opt not in ('8','9'):
        print(R + "✘ Chỉ nhận 8 hoặc 9!" + Style.RESET_ALL)
        return None
    opt = int(opt)

    token_file = input(W + "[+] File token:\n  ╰─> " + Style.RESET_ALL).strip()
    if not os.path.isfile(token_file):
        print(R + f"✘ File không tồn tại: {token_file}" + Style.RESET_ALL)
        return None
    with open(token_file, 'r', encoding='utf-8') as f:
        tokens = [line.strip() for line in f if line.strip()]
    if not tokens:
        print(R + "✘ File token rỗng!" + Style.RESET_ALL)
        return None

    channel_id = input(W + "[+] ID kênh:\n  ╰─> " + Style.RESET_ALL).strip()
    if not channel_id:
        print(R + "✘ Chưa nhập ID!" + Style.RESET_ALL)
        return None

    delay = input(W + "[+] Delay (s):\n  ╰─> " + Style.RESET_ALL).strip()
    try:
        delay = float(delay)
    except:
        print(R + "✘ Delay không hợp lệ!" + Style.RESET_ALL)
        return None

    msg_file = input(W + "[+] File nội dung (tin/ngôn):\n  ╰─> " + Style.RESET_ALL).strip()
    if not os.path.isfile(msg_file):
        print(R + f"✘ File không tồn tại: {msg_file}" + Style.RESET_ALL)
        return None
    with open(msg_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        print(R + "✘ File rỗng!" + Style.RESET_ALL)
        return None

    fake_typing = False
    tag_ids = []
    if opt == 8:
        ft = input(W + "[+] Fake typing? (y/n):\n  ╰─> " + Style.RESET_ALL).strip().lower()
        fake_typing = ft in ('y','yes')
        tag_input = input(W + "[+] ID tag (cách dấu phẩy, Enter bỏ qua):\n  ╰─> " + Style.RESET_ALL).strip()
        if tag_input:
            tag_ids = [t.strip() for t in tag_input.split(',') if t.strip()]

    return {
        'opt': opt,
        'tokens': tokens,
        'channel_id': channel_id,
        'delay': delay,
        'message_lines': lines,
        'fake_typing': fake_typing,
        'tag_ids': tag_ids
    }

def ask_zl():
    print(C + "\n╔══════════════════════════════════════╗")
    print("║           ZALO                      ║")
    print("╚══════════════════════════════════════╝" + Style.RESET_ALL)
    opt = input(W + "[+] Chọn (10-14) hoặc 'done':\n  ╰─> " + Style.RESET_ALL).strip()
    if opt.lower() == 'done':
        return None
    if not opt.isdigit() or int(opt) not in range(10,15):
        print(R + "✘ Chỉ nhận 10-14!" + Style.RESET_ALL)
        return None
    opt = int(opt)

    if not ZALO_AVAILABLE:
        print(R + "✘ zlapi chưa cài!" + Style.RESET_ALL)
        return None

    num_acc = input(W + "[+] Số acc:\n  ╰─> " + Style.RESET_ALL).strip()
    if not num_acc.isdigit():
        print(R + "✘ Nhập số!" + Style.RESET_ALL)
        return None
    num_acc = int(num_acc)
    accs = []
    for i in range(num_acc):
        print(f"\n--- Acc {i+1} ---")
        imei = input("  Imei: ").strip()
        cookie_str = input("  Cookie: ").strip()
        try:
            cookies = json.loads(cookie_str)
        except:
            print(R + "  ✘ Cookie không hợp lệ!" + Style.RESET_ALL)
            continue
        file_txt = input("  File .txt nội dung: ").strip()
        if not os.path.isfile(file_txt):
            print(R + f"  ✘ File không tồn tại!" + Style.RESET_ALL)
            continue
        message_text = readf(file_txt)
        try:
            delay = int(input("  Delay (s): ").strip() or "5")
        except:
            delay = 5
        ttl_input = input("  TTL (giây, 0 = không): ").strip()
        ttl = int(ttl_input) if ttl_input.isdigit() and int(ttl_input) > 0 else None
        accs.append({
            'imei': imei,
            'cookies': cookies,
            'message_text': message_text,
            'delay': delay,
            'ttl': ttl
        })
    if not accs:
        print(R + "✘ Không có acc hợp lệ!" + Style.RESET_ALL)
        return None

    temp_bot = ZaloAPI("api", "secret", accs[0]['imei'], accs[0]['cookies'])
    groups = []
    try:
        all_groups = temp_bot.fetchAllGroups()
        for gid, _ in all_groups.gridVerMap.items():
            ginfo = temp_bot.fetchGroupInfo(gid)
            gname = ginfo.gridInfoMap[gid]["name"] if gid in ginfo.gridInfoMap else "Unknown"
            groups.append({"id": gid, "name": gname})
    except Exception as e:
        print(R + f"✘ Lỗi lấy nhóm: {e}" + Style.RESET_ALL)
        return None
    if not groups:
        print(R + "✘ Không có nhóm nào!" + Style.RESET_ALL)
        return None

    print("\nDanh sách nhóm:")
    for idx, g in enumerate(groups, 1):
        print(f"{idx}. {g['name']} (ID: {g['id']})")
    choice_str = input(" Chọn nhóm (vd: 1,2,3): ").strip()
    choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
    selected_groups = [groups[c-1] for c in choices if 1 <= c <= len(groups)]
    if not selected_groups:
        print(R + "✘ Không chọn nhóm!" + Style.RESET_ALL)
        return None

    extra = {}
    if opt == 11:
        tag_all = input("Tag tất cả thành viên? (y/n): ").strip().lower() == 'y'
        extra['tag_all'] = tag_all
    elif opt == 12:
        media_source = input("File videos.txt (mặc định videos.txt): ").strip() or "videos.txt"
        thumb_url = input("URL ảnh bìa video: ").strip()
        font_size = int(input("Size chữ (tối đa 500, mặc định 500): ").strip() or "500")
        color_mode = input("Màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        extra.update({'media_source': media_source, 'thumb_url': thumb_url, 'font_size': font_size, 'color_mode': color_mode})
    elif opt == 13:
        font_size = int(input("Size chữ (tối đa 500, mặc định 500): ").strip() or "500")
        color_mode = input("Màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        extra.update({'font_size': font_size, 'color_mode': color_mode})
    elif opt == 14:
        font_size = int(input("Size chữ (tối đa 500, mặc định 500): ").strip() or "500")
        color_mode = input("Màu (y = mỗi dòng 1 màu, n = cả tin 1 màu): ").strip().lower()
        tag_all = input("Tag tất cả thành viên? (y/n): ").strip().lower() == 'y'
        extra.update({'font_size': font_size, 'color_mode': color_mode, 'tag_all': tag_all})

    return {
        'opt': opt,
        'accs': accs,
        'groups': selected_groups,
        'extra': extra
    }

def ask_tg():
    print(C + "\n╔══════════════════════════════════════╗")
    print("║           TELEGRAM                  ║")
    print("╚══════════════════════════════════════╝" + Style.RESET_ALL)
    opt = input(W + "[+] Chọn (15: treo ngôn, 16: nhây tag) hoặc 'done':\n  ╰─> " + Style.RESET_ALL).strip()
    if opt.lower() == 'done':
        return None
    if opt not in ('15','16'):
        print(R + "✘ Chỉ nhận 15 hoặc 16!" + Style.RESET_ALL)
        return None
    opt = int(opt)

    token_file = input(W + "[+] File token (định dạng bot:token):\n  ╰─> " + Style.RESET_ALL).strip()
    if not os.path.isfile(token_file):
        print(R + f"✘ File không tồn tại: {token_file}" + Style.RESET_ALL)
        return None
    with open(token_file, 'r', encoding='utf-8') as f:
        tokens = [line.strip() for line in f if line.strip() and not line.startswith('#') and ':' in line]
    if not tokens:
        print(R + "✘ Không có token hợp lệ!" + Style.RESET_ALL)
        return None

    chat_ids = []
    print("Nhập ID chat (bắt đầu bằng '-'), nhập 'done' để kết thúc:")
    while True:
        cid = input("  ID: ").strip()
        if cid.lower() == 'done':
            break
        if cid and cid.lstrip('-').isdigit():
            chat_ids.append(cid)
        else:
            print("  ✘ Không hợp lệ!")
    if not chat_ids:
        print(R + "✘ Chưa nhập ID chat!" + Style.RESET_ALL)
        return None

    delay = input(W + "[+] Delay (s) — số âm = 🔥TURBO:\n  ╰─> " + Style.RESET_ALL).strip()
    try:
        delay = float(delay)
    except:
        print(R + "✘ Delay không hợp lệ!" + Style.RESET_ALL)
        return None

    msg_file = input(W + "[+] File nội dung (mỗi dòng 1 tin):\n  ╰─> " + Style.RESET_ALL).strip()
    if not os.path.isfile(msg_file):
        print(R + f"✘ File không tồn tại: {msg_file}" + Style.RESET_ALL)
        return None
    with open(msg_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        print(R + "✘ File rỗng!" + Style.RESET_ALL)
        return None

    tag_ids = []
    if opt == 16:
        print("Nhập ID/@username để tag (nhập 'done' kết thúc):")
        while True:
            t = input("  Tag: ").strip()
            if t.lower() == 'done':
                break
            if t and (t.isdigit() or t.startswith('@')):
                tag_ids.append(t)
            else:
                print("  ✘ Không hợp lệ!")

    return {
        'opt': opt,
        'tokens': tokens,
        'chat_ids': chat_ids,
        'delay': delay,
        'message_lines': lines,
        'tag_ids': tag_ids
    }

def ask_tiktok():
    print(C + "\n╔══════════════════════════════════════╗")
    print("║           TIKTOK                    ║")
    print("╚══════════════════════════════════════╝" + Style.RESET_ALL)
    opt = input(W + "[+] Chọn (17: treo ngôn, 18: nhây) hoặc 'done':\n  ╰─> " + Style.RESET_ALL).strip()
    if opt.lower() == 'done':
        return None
    if opt not in ('17','18'):
        print(R + "✘ Chỉ nhận 17 hoặc 18!" + Style.RESET_ALL)
        return None
    opt = int(opt)

    cookie_file = input(W + "[+] File cookie TikTok:\n  ╰─> " + Style.RESET_ALL).strip()
    if not os.path.isfile(cookie_file):
        print(R + f"✘ File không tồn tại: {cookie_file}" + Style.RESET_ALL)
        return None
    try:
        cookies = read_tiktok_cookies_from_file(cookie_file)
    except Exception as e:
        print(R + f"✘ {e}" + Style.RESET_ALL)
        return None

    if not cookies:
        print(R + "✘ Không có cookie!" + Style.RESET_ALL)
        return None

    print("Tiếp theo nhập thông số cho TikTok:")
    try:
        client = TikTokPureClient(cookies[0])
        groups = client.get_groups()
    except Exception as e:
        print(R + f"✘ Lỗi lấy box từ cookie đầu: {e}" + Style.RESET_ALL)
        return None

    if not groups:
        print(R + "✘ Không tìm thấy box nào!" + Style.RESET_ALL)
        return None

    print("\nDanh sách box từ cookie đầu:")
    for i, g in enumerate(groups, 1):
        print(f"{i}. {g['name']} (ID: {g['id']})")
    choice_str = input(" Chọn STT box (vd: 1,2,3): ").strip()
    choices = [int(x) for x in choice_str.split(",") if x.strip().isdigit()]
    selected_groups = [groups[c-1] for c in choices if 1 <= c <= len(groups)]
    if not selected_groups:
        print(R + "✘ Không chọn box!" + Style.RESET_ALL)
        return None

    file_content = input(W + "[+] File nội dung:\n  ╰─> " + Style.RESET_ALL).strip()
    if not os.path.isfile(file_content):
        print(R + f"✘ File không tồn tại!" + Style.RESET_ALL)
        return None

    delay = input(W + "[+] Delay (s):\n  ╰─> " + Style.RESET_ALL).strip()
    try:
        delay = float(delay)
    except:
        print(R + "✘ Delay không hợp lệ!" + Style.RESET_ALL)
        return None

    return {
        'opt': opt,
        'cookies': cookies,
        'groups': selected_groups,
        'file_content': file_content,
        'delay': delay
    }

def run_tiktok(params):
    opt = params['opt']
    cookies = params['cookies']
    selected_groups = params['groups']
    file_content = params['file_content']
    delay = params['delay']

    try:
        with open(file_content, 'r', encoding='utf-8') as f:
            raw = f.read()
        if opt == 17:
            content_text = raw.strip()
            if not content_text:
                print(R + "✘ File rỗng!" + Style.RESET_ALL)
                return
            lines = None
        else:
            lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
            if not lines:
                print(R + "✘ File rỗng!" + Style.RESET_ALL)
                return
            content_text = None
    except Exception as e:
        print(R + f"✘ Lỗi đọc file: {e}" + Style.RESET_ALL)
        return

    tasks = []
    task_id = 0
    for idx, cookie in enumerate(cookies, 1):
        client = TikTokPureClient(cookie)
        try:
            info = client.get_self()
            print(G + f"✓ Login TikTok: @{info['unique_id']}" + Style.RESET_ALL)
        except Exception as e:
            print(R + f"✘ Login fail: {e}" + Style.RESET_ALL)
            continue

        try:
            groups = client.get_groups()
        except Exception as e:
            print(R + f"✘ Lỗi lấy box: {e}" + Style.RESET_ALL)
            continue

        selected = [g for g in groups if g['id'] in [sg['id'] for sg in selected_groups]]
        if not selected:
            print(R + f"✘ Không tìm thấy box đã chọn cho acc này" + Style.RESET_ALL)
            continue

        task_id += 1
        task = TikTokSpamTask(task_id, client, selected, opt, content_text, lines, delay, info["unique_id"])
        task.run()
        tasks.append(task)
        print(G + f"✓ Đã tạo Task {task_id} cho @{info['unique_id']}" + Style.RESET_ALL)

    if not tasks:
        print(R + "✘ Không có task nào!" + Style.RESET_ALL)
        return

    print(G + f"\n✓ Tổng {len(tasks)} task TikTok đang chạy." + Style.RESET_ALL)
    while True:
        time.sleep(1)

def run_fb(params):
    send_messages_with_cookie(
        cookies=params['cookies'],
        thread_ids=params['thread_ids'],
        message_files=params['message_files'],
        delay=params['delay'],
        option=params['opt'],
        name_file=params['name_file'],
        tag_ids=params['tag_ids'],
        func_name=None
    )

def run_dc(params):
    tool = DiscordTool()
    tool.tokens = params['tokens']
    tool.kenh_id = params['channel_id']
    tool.delays = {token: params['delay'] for token in tool.tokens}
    if params['opt'] == 8:
        tool.tin_nhan = params['message_lines']
        tool.fake_typing = params.get('fake_typing', False)
        tool.nguoi_tag = params.get('tag_ids', [])
        for token in tool.tokens:
            threading.Thread(target=tool.gui_tin_nhay, args=(token,), daemon=True).start()
    else:
        tool.ngon_lines = params['message_lines']
        for token in tool.tokens:
            threading.Thread(target=tool.gui_tin_ngon, args=(token,), daemon=True).start()
    while True:
        time.sleep(1)

def run_zl(params):
    opt = params['opt']
    accs = params['accs']
    groups = params['groups']
    extra = params['extra']

    if opt == 10:
        for acc in accs:
            bot = Bot(acc['imei'], acc['cookies'], 0, acc['delay'], acc['message_text'], ttl=acc['ttl'])
            for g in groups:
                threading.Thread(target=bot.send_spam, args=(g['id'], g['name']), daemon=True).start()
    elif opt == 11:
        for acc in accs:
            client = TagBot(acc['imei'], acc['cookies'])
            for g in groups:
                members = client.fetchGroupMembers(g['id'])
                users = ["@all"] if extra.get('tag_all', False) else [m['id'] for m in members]
                threading.Thread(target=client.send_file_content, args=(g['id'], "tag.txt", acc['delay'], users), daemon=True).start()
    elif opt == 12:
        for acc in accs:
            bot = TreongonBot("api", "secret", acc['imei'], acc['cookies'],
                              delay=acc['delay'], message_text=acc['message_text'], ttl=acc['ttl'],
                              media_source=extra.get('media_source', 'videos.txt'))
            bot.thumb_url = extra.get('thumb_url', '')
            bot.font_size = extra.get('font_size', 500)
            bot.color_mode = extra.get('color_mode', 'y')
            for g in groups:
                threading.Thread(target=bot.spam_messages, args=(g['id'], ThreadType.GROUP, acc['ttl']), daemon=True).start()
    elif opt == 13:
        for acc in accs:
            bot = TreongonTextBot("api", "secret", acc['imei'], acc['cookies'],
                                  delay=acc['delay'], message_text=acc['message_text'], ttl=acc['ttl'])
            bot.font_size = extra.get('font_size', 500)
            bot.color_mode = extra.get('color_mode', 'y')
            for g in groups:
                threading.Thread(target=bot.spam_messages, args=(g['id'], ThreadType.GROUP, acc['ttl']), daemon=True).start()
    elif opt == 14:
        for acc in accs:
            mentions = []
            if extra.get('tag_all', False):
                temp_bot = ZaloAPI("api", "secret", acc['imei'], acc['cookies'])
                for g in groups:
                    try:
                        members = temp_bot.fetchGroupInfo(g['id']).gridInfoMap[g['id']]["memVerList"]
                        mentions = [m.split("_")[0] for m in members]
                    except:
                        pass
            bot = TreoAnhBot("api", "secret", acc['imei'], acc['cookies'],
                             delay=acc['delay'], message_text=acc['message_text'], ttl=acc['ttl'],
                             image_folder="Gbao", font_size=extra.get('font_size', 500),
                             color_mode=extra.get('color_mode', 'y'), mentions=mentions)
            for g in groups:
                threading.Thread(target=bot.spam_messages, args=(g['id'], ThreadType.GROUP, acc['ttl']), daemon=True).start()
    while True:
        time.sleep(1)

def run_tg(params):
    spam = TgSpam()
    tokens = params['tokens']
    chat_ids = params['chat_ids']
    delay = params['delay']
    message_lines = params['message_lines']
    tag_ids = params.get('tag_ids', [])
    opt = params['opt']

    for tk in tokens:
        spam.infos[tk] = spam.get_info(tk)
    spam.tags = tag_ids

    turbo = delay < 0
    if turbo:
        print(R + "\n🔥🔥 TURBO MODE (chức năng 19) 🔥🔥" + W)
    else:
        spam.delay = delay

    spam.st.clear()
    threading.Thread(target=spam.listener, daemon=True).start()
    for i, tk in enumerate(tokens):
        if turbo:
            t = threading.Thread(target=spam._turbo_worker, args=(i+1, tk, chat_ids, message_lines, opt==16), daemon=True)
        else:
            t = threading.Thread(target=spam.worker, args=(i+1, tk, chat_ids, message_lines, opt==16), daemon=True)
        t.start()

    while not spam.st.is_set():
        time.sleep(1)

def all_exec():
    box(" TREO TẤT CẢ APP (19) ", Y2)
    fb_params = ask_fb()
    dc_params = ask_dc()
    zl_params = ask_zl()
    tg_params = ask_tg()
    tik_params = ask_tiktok()

    threads = []
    if fb_params:
        t = threading.Thread(target=run_fb, args=(fb_params,), daemon=True)
        threads.append(t); t.start()
    if dc_params:
        t = threading.Thread(target=run_dc, args=(dc_params,), daemon=True)
        threads.append(t); t.start()
    if zl_params:
        t = threading.Thread(target=run_zl, args=(zl_params,), daemon=True)
        threads.append(t); t.start()
    if tg_params:
        t = threading.Thread(target=run_tg, args=(tg_params,), daemon=True)
        threads.append(t); t.start()
    if tik_params:
        t = threading.Thread(target=run_tiktok, args=(tik_params,), daemon=True)
        threads.append(t); t.start()

    if not threads:
        print(R + "✘ Không chọn app nào!" + Style.RESET_ALL)
        return

    print(G + "\n✅ Đang treo tất cả app đã chọn. Nhấn Ctrl+C để dừng." + Style.RESET_ALL)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(R + "\n🛑 Đã dừng tất cả." + Style.RESET_ALL)

# ==========================================
#                MENU CHÍNH (19 chức năng)
# ==========================================
def menu():
    title = " ☁️ TOOL 5 APP SIEU BA BY DKHIEM "
    width = 58
    padding = width - len(title) - 2
    left_pad = padding // 2
    right_pad = padding - left_pad

    print("\n" + C + "╔" + "═" * width + "╗")
    print(C + "║" + " " * left_pad + title + " " * right_pad + "║")
    print(C + "╚" + "═" * width + "╝" + Style.RESET_ALL)

    contact = "📱 Mua tool, via ib zl: 0365242844"
    print(C + "╔" + "═" * (len(contact)+4) + "╗")
    print(C + "║  " + contact + "  ║")
    print(C + "╚" + "═" * (len(contact)+4) + "╝" + Style.RESET_ALL)

    while True:
        print("\n" + Y2 + "╔" + "═" * width + "╗")
        print("║" + " " * 18 + "📋 DANH SÁCH 19 CHỨC NĂNG" + " " * 18 + "║")
        print("╠" + "═" * width + "╣")
        print("║" + C + " 1. Treo ngôn (FB)" + " " * 38 + W + "║")
        print("║" + C + " 2. Nhây tên nhóm (FB)" + " " * 33 + W + "║")
        print("║" + C + " 3. Treo poll (FB)" + " " * 37 + W + "║")
        print("║" + C + " 4. Nhây fake typing (FB)" + " " * 30 + W + "║")
        print("║" + C + " 5. Thay đổi theme (FB)" + " " * 31 + W + "║")
        print("║" + C + " 6. Đổi biệt danh nhóm (FB)" + " " * 28 + W + "║")
        print("║" + C + " 7. Nhây tag (FB)" + " " * 38 + W + "║")
        print("║" + Y + " 8. Nhây dis (Discord) - nâng cấp" + " " * 23 + W + "║")
        print("║" + Y + " 9. Treo ngôn dis (Discord) - nâng cấp" + " " * 18 + W + "║")
        print("║" + R + "10. Réo nhiều người (Zalo)" + " " * 29 + W + "║")
        print("║" + R + "11. Nhây tag (Zalo)" + " " * 34 + W + "║")
        print("║" + R + "12. Treo video + ngôn (Zalo)" + " " * 25 + W + "║")
        print("║" + R + "13. Treo ngôn text (Zalo)" + " " * 27 + W + "║")
        print("║" + R + "14. Treo ảnh (Zalo)" + " " * 33 + W + "║")
        print("║" + M1 + "15. Treo ngôn (Telegram) - full file" + " " * 13 + W + "║")
        print("║" + M1 + "16. Nhây tag (Telegram) - từng dòng" + " " * 15 + W + "║")
        print("║" + G + "17. Treo ngôn TikTok" + " " * 32 + W + "║")
        print("║" + G + "18. Nhây TikTok" + " " * 37 + W + "║")
        print("║" + M2 + "19. Treo tất cả app (FB+DC+ZALO+TG+TIK)" + " " * 14 + W + "║")
        print("╠" + "═" * width + "╣")
        print("║" + " " * 5 + "Nhập số (1-19) hoặc 0 để thoát" + " " * 23 + "║")
        print("╚" + "═" * width + "╝" + Style.RESET_ALL)

        ch = input(W + "  ╰─> " + Style.RESET_ALL).strip()
        if ch == '0':
            print(M1 + "\n👋 Đã thoát. Tạm biệt!" + Style.RESET_ALL)
            sys.exit()
        try:
            n = int(ch)
        except ValueError:
            print(R + "✘ Vui lòng nhập số!" + Style.RESET_ALL)
            continue

        if 1 <= n <= 7:
            fb_exec(n)
        elif n == 8:
            dc_exec(1)
        elif n == 9:
            dc_exec(2)
        elif n == 10:
            zl_exec(2)
        elif n == 11:
            zl_exec(1)
        elif n == 12:
            zl_exec(3)
        elif n == 13:
            zl_exec(4)
        elif n == 14:
            zl_exec(5)
        elif n == 15:
            tg_exec(1)
        elif n == 16:
            tg_exec(2)
        elif n == 17:
            tik_exec(1)
        elif n == 18:
            tik_exec(2)
        elif n == 19:
            all_exec()
        else:
            print(R + "✘ Số không hợp lệ!" + Style.RESET_ALL)

# ==========================================
#                KHỞI CHẠY
# ==========================================
if __name__=="__main__":
    if sys.version_info < (3,6):
        print("⚠️ Python 3.6+ required")
        sys.exit(1)
    if os.name == 'nt':
        print("⚠️ Hỗ trợ tốt nhất trên Linux/Android")

    print_banner_slow()

    time.sleep(0.5)
    menu()