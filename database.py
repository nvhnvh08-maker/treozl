#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database SQLite quản lý Tài khoản & Đa Tab cho Zalo Treo Text Pro
"""

import sqlite3
import hashlib
import uuid
import json
import os
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zalo_database.db")
SECRET_SALT = "ZaloTreoTextPro_2026_SecureSalt"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Bảng người dùng (Không có tài khoản mặc định, người dùng tự đăng ký)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Bảng các tab treo text độc lập
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tabs (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        config_json TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET_SALT).encode('utf-8')).hexdigest()

def register_user(username: str, password: str) -> tuple[bool, str, Optional[int]]:
    username = username.strip()
    password = password.strip()
    if len(username) < 3:
        return False, "Tên đăng nhập phải có ít nhất 3 ký tự", None
    if len(password) < 3:
        return False, "Mật khẩu phải có ít nhất 3 ký tự", None

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Tên tài khoản này đã tồn tại, vui lòng chọn tên khác", None

        pwd_hash = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        conn.commit()
        user_id = cursor.lastrowid
        return True, "Đăng ký thành công", user_id
    except Exception as e:
        return False, f"Lỗi cơ sở dữ liệu: {str(e)}", None
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> tuple[bool, str, Optional[int]]:
    username = username.strip()
    password = password.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        cursor.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
        row = cursor.fetchone()
        if row:
            return True, "Đăng nhập thành công", row["id"]
        return False, "Sai tên tài khoản hoặc mật khẩu", None
    finally:
        conn.close()

def create_tab(user_id: int, name: str) -> tuple[bool, str, Optional[str]]:
    name = name.strip()
    if not name:
        return False, "Tên tab không được để trống", None

    tab_id = str(uuid.uuid4())[:8]
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        default_config = {
            "accounts": [{"imei": "", "cookie": ""}],
            "group_id": "",
            "group_name": "",
            "message_text": "",
            "delay": 5,
            "color_mode": "random_line",
            "chosen_color": "#DB342E",
            "font_size": 500,
            "ttl": 0
        }
        cursor.execute(
            "INSERT INTO tabs (id, user_id, name, config_json) VALUES (?, ?, ?, ?)",
            (tab_id, user_id, name, json.dumps(default_config, ensure_ascii=False))
        )
        conn.commit()
        return True, "Tạo tab thành công", tab_id
    except Exception as e:
        return False, f"Lỗi tạo tab: {str(e)}", None
    finally:
        conn.close()

def get_user_tabs(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, user_id, name, config_json, created_at FROM tabs WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            cfg = {}
            try:
                cfg = json.loads(r["config_json"]) if r["config_json"] else {}
            except Exception:
                pass
            result.append({
                "id": r["id"],
                "name": r["name"],
                "config": cfg,
                "created_at": r["created_at"]
            })
        return result
    finally:
        conn.close()

def get_tab_by_id(tab_id: str, user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, user_id, name, config_json, created_at FROM tabs WHERE id = ? AND user_id = ?", (tab_id, user_id))
        r = cursor.fetchone()
        if not r:
            return None
        cfg = {}
        try:
            cfg = json.loads(r["config_json"]) if r["config_json"] else {}
        except Exception:
            pass
        return {
            "id": r["id"],
            "name": r["name"],
            "config": cfg,
            "created_at": r["created_at"]
        }
    finally:
        conn.close()

def update_tab_config(tab_id: str, user_id: int, config_dict: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tabs SET config_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (json.dumps(config_dict, ensure_ascii=False), tab_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_tab(tab_id: str, user_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tabs WHERE id = ? AND user_id = ?", (tab_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Khởi tạo bảng ngay khi import
init_db()
