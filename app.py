#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HỆ THỐNG ZALO TREO TEXT PRO - BACKEND FASTAPI & DATABASE SQLITE
Phục vụ các file Web tách biệt: index.html, style.css, script.js
"""

import os
import sys
import json
import time
import secrets
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import (
    register_user,
    authenticate_user,
    create_tab,
    get_user_tabs,
    get_tab_by_id,
    update_tab_config,
    delete_tab
)

from zalo_core import (
    bot_manager,
    fetch_groups_from_acc,
    TOOL_COLOR_LIST,
    parse_cookies_input
)

app = FastAPI(title="Zalo Treo Text Multi-Tab 3D Pro", version="4.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Quản lý phiên đăng nhập: token -> {"user_id": int, "username": str}
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập hoặc thiếu token")
    token = authorization.replace("Bearer ", "").strip()
    session = ACTIVE_SESSIONS.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã hết hạn hoặc không hợp lệ")
    return session

# ==============================================================
#                  API AUTHENTICATION (SQLITE)
# ==============================================================
@app.post("/api/register")
async def api_register(payload: Dict[str, Any]):
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()

    success, msg, user_id = register_user(username, password)
    if not success:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    # Tự động đăng nhập luôn sau khi đăng ký thành công
    token = secrets.token_hex(24)
    ACTIVE_SESSIONS[token] = {"user_id": user_id, "username": username}

    # Tạo sẵn 1 tab mặc định cho người dùng mới
    create_tab(user_id, "Tab Treo #1")

    return {
        "success": True,
        "token": token,
        "username": username,
        "message": "Đăng ký tài khoản thành công!"
    }

@app.post("/api/login")
async def api_login(payload: Dict[str, Any]):
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()

    success, msg, user_id = authenticate_user(username, password)
    if not success:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    token = secrets.token_hex(24)
    ACTIVE_SESSIONS[token] = {"user_id": user_id, "username": username}

    return {
        "success": True,
        "token": token,
        "username": username,
        "message": "Đăng nhập thành công!"
    }

@app.post("/api/logout")
async def api_logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[token]
    return {"success": True, "message": "Đã đăng xuất"}

@app.get("/api/me")
async def api_me(user: Dict[str, Any] = Depends(get_current_user)):
    return {"success": True, "user": user}

# ==============================================================
#                  API QUẢN LÝ ĐA TAB (MULTI-TAB)
# ==============================================================
@app.get("/api/tabs")
async def api_get_tabs(user: Dict[str, Any] = Depends(get_current_user)):
    tabs = get_user_tabs(user["user_id"])
    live_summary = bot_manager.get_all_tabs_summary()

    for tab in tabs:
        tid = tab["id"]
        live = live_summary.get(tid, {
            "is_running": False,
            "runtime_formatted": "00:00:00",
            "total_sent": 0,
            "total_failed": 0,
            "acc_count": len(tab.get("config", {}).get("accounts", [])),
            "target_group_name": tab.get("config", {}).get("group_name", "")
        })
        tab["is_running"] = live["is_running"]
        tab["runtime_formatted"] = live["runtime_formatted"]
        tab["total_sent"] = live["total_sent"]
        tab["total_failed"] = live["total_failed"]
        tab["acc_count"] = live["acc_count"]
        tab["target_group_name"] = live["target_group_name"]

    return {"success": True, "tabs": tabs}

@app.post("/api/tabs/create")
async def api_create_tab(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    name = str(payload.get("name", "")).strip()
    if not name:
        return JSONResponse(status_code=400, content={"success": False, "message": "Vui lòng nhập tên tab"})

    success, msg, tab_id = create_tab(user["user_id"], name)
    if not success:
        return JSONResponse(status_code=400, content={"success": False, "message": msg})

    return {
        "success": True,
        "tab_id": tab_id,
        "name": name,
        "message": "Tạo tab mới thành công!"
    }

@app.get("/api/tabs/{tab_id}")
async def api_get_tab_detail(tab_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    tab = get_tab_by_id(tab_id, user["user_id"])
    if not tab:
        raise HTTPException(status_code=404, detail="Không tìm thấy tab này")

    live_status = bot_manager.get_tab_status(tab_id)
    return {
        "success": True,
        "tab": tab,
        "status": live_status
    }

@app.post("/api/tabs/{tab_id}/save")
async def api_save_tab_config(tab_id: str, payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    config = payload.get("config", {})
    ok = update_tab_config(tab_id, user["user_id"], config)
    return {"success": ok, "message": "Đã lưu cấu hình tab"}

@app.post("/api/tabs/{tab_id}/start")
async def api_start_tab(tab_id: str, payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    tab = get_tab_by_id(tab_id, user["user_id"])
    if not tab:
        raise HTTPException(status_code=404, detail="Không tìm thấy tab")

    accounts = payload.get("accounts", [])
    group_id = str(payload.get("group_id", "")).strip()
    group_name = str(payload.get("group_name", "")).strip()
    message_text = str(payload.get("message_text", "")).strip()
    delay = int(payload.get("delay", 5) or 5)
    color_mode = str(payload.get("color_mode", "random_line")).strip()
    chosen_color = str(payload.get("chosen_color", "#DB342E")).strip()
    font_size = int(payload.get("font_size", 500) or 500)
    ttl_raw = payload.get("ttl", 0)
    ttl = int(ttl_raw) if str(ttl_raw).isdigit() and int(ttl_raw) > 0 else None

    if not accounts:
        return JSONResponse(status_code=400, content={"success": False, "message": "Vui lòng cấu hình ít nhất 1 tài khoản"})

    # Kiểm tra xem có nhóm chung hoặc bất kỳ tài khoản nào đã chọn nhóm chưa
    has_any_group = bool(group_id) or any(bool(str(acc.get("group_id", "")).strip()) for acc in accounts)
    if not has_any_group:
        return JSONResponse(status_code=400, content={"success": False, "message": "Vui lòng chọn hoặc nhập nhóm Zalo để treo"})

    # Nếu không có group_id chung, lấy nhóm của tài khoản đầu tiên làm đại diện
    if not group_id and accounts:
        for acc in accounts:
            if acc.get("group_id"):
                group_id = str(acc["group_id"]).strip()
                group_name = str(acc.get("group_name", "")).strip() or f"Nhóm {group_id}"
                break

    if not message_text:
        return JSONResponse(status_code=400, content={"success": False, "message": "Vui lòng nhập hoặc tải file ngôn (.txt)"})
    if delay < 1:
        delay = 1
    if font_size < 1:
        font_size = 500

    new_cfg = {
        "accounts": accounts,
        "group_id": group_id,
        "group_name": group_name,
        "message_text": message_text,
        "delay": delay,
        "color_mode": color_mode,
        "chosen_color": chosen_color,
        "font_size": font_size,
        "ttl": ttl
    }
    update_tab_config(tab_id, user["user_id"], new_cfg)

    try:
        bot_manager.start_tab(
            tab_id=tab_id,
            tab_name=tab["name"],
            accounts=accounts,
            group_id=group_id,
            group_name=group_name,
            message_text=message_text,
            delay=delay,
            color_mode=color_mode,
            chosen_color=chosen_color,
            font_size=font_size,
            ttl=ttl
        )
        return {"success": True, "message": f"Tab [{tab['name']}] đã bắt đầu chạy thành công!"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})

@app.post("/api/tabs/{tab_id}/stop")
async def api_stop_tab(tab_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    bot_manager.stop_tab(tab_id)
    return {"success": True, "message": "Đã dừng tab này"}

@app.delete("/api/tabs/{tab_id}")
async def api_delete_tab(tab_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    bot_manager.delete_tab(tab_id)
    ok = delete_tab(tab_id, user["user_id"])
    return {"success": ok, "message": "Đã xóa tab thành công"}

# ==============================================================
#                  API LẤY NHÓM ZALO
# ==============================================================
@app.post("/api/get-groups")
async def api_get_groups(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    imei = str(payload.get("imei", "")).strip()
    cookie_raw = payload.get("cookie", "")

    if not imei:
        return JSONResponse(status_code=400, content={"success": False, "message": "Vui lòng nhập IMEI"})
    if not cookie_raw:
        return JSONResponse(status_code=400, content={"success": False, "message": "Vui lòng nhập Cookie"})

    try:
        groups = fetch_groups_from_acc(imei, cookie_raw)
        return {
            "success": True,
            "groups": groups,
            "message": f"Tìm thấy {len(groups)} nhóm Zalo"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": f"Lỗi lấy nhóm: {str(e)}"})


# ==============================================================
#          PHỤC VỤ CÁC FILE WEB TÁCH RIÊNG (HTML, CSS, JS)
# ==============================================================
@app.get("/")
async def serve_index():
    index_path = os.path.join(CURRENT_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file index.html")
    return FileResponse(index_path, media_type="text/html")

@app.get("/style.css")
async def serve_css():
    css_path = os.path.join(CURRENT_DIR, "style.css")
    if not os.path.exists(css_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file style.css")
    return FileResponse(css_path, media_type="text/css")

@app.get("/script.js")
async def serve_js():
    js_path = os.path.join(CURRENT_DIR, "script.js")
    if not os.path.exists(js_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file script.js")
    return FileResponse(js_path, media_type="application/javascript")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"==================================================")
    print(f"🚀 ZALO TREO TEXT MULTI-TAB 3D PRO ĐANG CHẠY")
    print(f"👉 Mời sếp truy cập: http://localhost:{port}")
    print(f"📄 Tệp Web: index.html | style.css | script.js")
    print(f"💾 Cơ sở dữ liệu: SQLite (zalo_database.db)")
    print(f"==================================================")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
