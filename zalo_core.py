#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core module xử lý Zalo API cho tính năng Treo Text Zalo Đa Luồng Đa Tab
Hỗ trợ chạy song song nhiều Tab độc lập không giới hạn!
"""

import os
import sys
import time
import json
import random
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from zlapi import ZaloAPI, ThreadType, Message
    from zlapi.models import MessageStyle, MultiMsgStyle
    ZALO_AVAILABLE = True
except ImportError:
    ZALO_AVAILABLE = False

# Danh sách mã màu chuẩn trong tool gốc dangkhiem_1.py
TOOL_COLOR_LIST = [
    "#DB342E",  # Đỏ rực
    "#15A85F",  # Xanh lá
    "#F27806",  # Cam tươi
    "#F7B503",  # Vàng nghệ
    "#FFFFFF",  # Trắng tinh
    "#000000"   # Đen huyền
]

def normalize_ttl_value(ttl):
    """Chuẩn hóa giá trị TTL tự hủy theo millisecond"""
    if ttl is None:
        return None
    try:
        t = int(ttl)
    except Exception:
        return None
    if t <= 0:
        return None
    if t < 1000:
        return t * 1000
    return t

def parse_cookies_input(cookie_raw: Any) -> Dict[str, str]:
    """Phân tích linh hoạt mọi định dạng Cookie"""
    if not cookie_raw:
        return {}
    if isinstance(cookie_raw, dict):
        return {str(k).strip(): str(v).strip() for k, v in cookie_raw.items()}
    if isinstance(cookie_raw, list):
        res = {}
        for item in cookie_raw:
            if isinstance(item, dict) and "name" in item and "value" in item:
                res[str(item["name"]).strip()] = str(item["value"]).strip()
        return res

    cookie_str = str(cookie_raw).strip()
    if not cookie_str:
        return {}

    if (cookie_str.startswith("{") and cookie_str.endswith("}")) or (cookie_str.startswith("[") and cookie_str.endswith("]")):
        try:
            parsed = json.loads(cookie_str)
            return parse_cookies_input(parsed)
        except Exception:
            pass

    res = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k:
                res[k] = v
    return res

def fetch_groups_from_acc(imei: str, cookie_raw: Any) -> List[Dict[str, str]]:
    """Lấy danh sách nhóm từ ZaloAPI qua IMEI và Cookie"""
    if not ZALO_AVAILABLE:
        raise RuntimeError("Thư viện zlapi chưa được cài đặt. Vui lòng cài: pip install zlapi")

    imei = str(imei).strip()
    cookies = parse_cookies_input(cookie_raw)
    if not imei:
        raise ValueError("IMEI không được để trống")
    if not cookies:
        raise ValueError("Cookie không hợp lệ hoặc để trống")

    bot = ZaloAPI("api", "secret", imei, cookies)
    groups = []
    
    try:
        all_groups = bot.fetchAllGroups()
    except Exception as e:
        raise RuntimeError(f"Lỗi kết nối Zalo khi lấy danh sách nhóm: {str(e)}")

    grid_map = getattr(all_groups, "gridVerMap", None)
    if not grid_map and isinstance(all_groups, dict):
        grid_map = all_groups.get("gridVerMap", {})

    if not grid_map:
        return []

    for gid in grid_map.keys():
        gid_str = str(gid)
        gname = f"Nhóm {gid_str}"
        try:
            ginfo = bot.fetchGroupInfo(gid)
            info_map = getattr(ginfo, "gridInfoMap", None)
            if not info_map and isinstance(ginfo, dict):
                info_map = ginfo.get("gridInfoMap", {})
            if info_map and gid_str in info_map:
                name_val = info_map[gid_str].get("name")
                if name_val:
                    gname = name_val
        except Exception:
            pass
        groups.append({"id": gid_str, "name": gname})

    return groups


class SingleTabRunner:
    """
    Tiến trình chạy độc lập cho một Tab cụ thể
    """
    def __init__(self, tab_id: str, name: str):
        self.tab_id = tab_id
        self.name = name
        self.is_running = False
        self.start_time: Optional[float] = None
        self.stop_event = threading.Event()
        self.active_threads: List[threading.Thread] = []
        self.logs: List[Dict[str, Any]] = []
        self.logs_lock = threading.Lock()
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "acc_count": 0,
            "target_group": "",
            "target_group_name": "",
            "color_info": ""
        }

    def add_log(self, message: str, level: str = "info"):
        now = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "time": now,
            "level": level,
            "message": message
        }
        with self.logs_lock:
            self.logs.append(log_entry)
            if len(self.logs) > 300:
                self.logs.pop(0)

    def get_status(self) -> Dict[str, Any]:
        runtime_seconds = 0
        if self.is_running and self.start_time:
            runtime_seconds = int(time.time() - self.start_time)

        hours = runtime_seconds // 3600
        minutes = (runtime_seconds % 3600) // 60
        seconds = runtime_seconds % 60
        runtime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        with self.logs_lock:
            recent_logs = list(self.logs[-80:])

        return {
            "tab_id": self.tab_id,
            "name": self.name,
            "is_running": self.is_running,
            "runtime_seconds": runtime_seconds,
            "runtime_formatted": runtime_str,
            "total_sent": self.stats["total_sent"],
            "total_failed": self.stats["total_failed"],
            "acc_count": self.stats["acc_count"],
            "target_group": self.stats["target_group"],
            "target_group_name": self.stats["target_group_name"],
            "color_info": self.stats["color_info"],
            "logs": recent_logs
        }

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self.stop_event.set()
        self.add_log("⏹️ Đã phát lệnh dừng tiến trình treo text của tab này.", "warning")

    def _worker(self, acc_index: int, imei: str, cookies: dict, group_id: str, group_name: str,
                message_text: str, delay: int, color_mode: str, chosen_color: str,
                font_size: int, ttl: Optional[int]):
        acc_label = f"Acc #{acc_index + 1}"
        try:
            bot = ZaloAPI("api", "secret", imei, cookies)
            self.add_log(f"[{acc_label}] Khởi tạo bot Zalo thành công. Mục tiêu: {group_name} ({group_id})", "info")
        except Exception as e:
            self.add_log(f"[{acc_label}] Lỗi khởi tạo ZaloAPI: {e}", "error")
            return

        lines = [ln for ln in message_text.splitlines() if ln]
        if not lines:
            lines = [message_text]

        loop_count = 0
        while not self.stop_event.is_set() and self.is_running:
            loop_count += 1
            try:
                msg_color = chosen_color
                if color_mode == "random_msg":
                    msg_color = random.choice(TOOL_COLOR_LIST)

                styles = []
                formatted_text = ""
                offset = 0

                for line in lines:
                    line_color = random.choice(TOOL_COLOR_LIST) if color_mode == "random_line" else msg_color
                    line_text = line + "\n"
                    formatted_text += line_text

                    styles.append(MessageStyle(
                        offset=offset,
                        length=len(line_text),
                        style="color",
                        color=line_color,
                        auto_format=False
                    ))
                    styles.append(MessageStyle(
                        offset=offset,
                        length=len(line_text),
                        style="font",
                        size=str(font_size),
                        auto_format=False
                    ))
                    offset += len(line_text)

                multi_style = MultiMsgStyle(styles)
                ttl_to_send = normalize_ttl_value(ttl)

                # Gửi toàn bộ ngôn cùng lúc trong 1 tin nhắn
                msg_payload = Message(text=formatted_text, style=multi_style)
                bot.send(msg_payload, thread_id=group_id, thread_type=ThreadType.GROUP, ttl=ttl_to_send)

                self.stats["total_sent"] += 1
                preview = lines[0][:26] + ("..." if len(lines[0]) > 26 else "")
                self.add_log(
                    f"[{acc_label}] Lượt #{loop_count}: Đã gửi toàn bộ ngôn ({len(lines)} dòng) vào {group_name} ({group_id}) [Size: {font_size} | Màu: {line_color}] - \"{preview}\"",
                    "success"
                )

            except Exception as e:
                self.stats["total_failed"] += 1
                self.add_log(f"[{acc_label}] Gửi thất bại lượt #{loop_count} (Nhóm: {group_id}): {e}", "error")

            # Delay giữa các lần gửi (ngắt quãng để dừng ngay khi người dùng bấm Stop)
            sleep_chunks = max(int(delay * 10), 1)
            for _ in range(sleep_chunks):
                if self.stop_event.is_set() or not self.is_running:
                    break
                time.sleep(0.1)

        self.add_log(f"[{acc_label}] Luồng đã dừng hoàn toàn.", "warning")

    def start(self, accounts: List[Dict[str, Any]], group_id: str, group_name: str,
              message_text: str, delay: int = 5, color_mode: str = "random_line",
              chosen_color: str = "#DB342E", font_size: int = 500, ttl: Optional[int] = None) -> bool:
        if self.is_running:
            self.stop()
            time.sleep(0.4)

        if not ZALO_AVAILABLE:
            raise RuntimeError("Thư viện zlapi chưa được cài đặt")

        if not accounts:
            raise ValueError("Không có tài khoản nào được cấu hình")
        if not message_text.strip():
            raise ValueError("Nội dung ngôn không được để trống")

        self.stop_event.clear()
        self.is_running = True
        self.start_time = time.time()
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "acc_count": len(accounts),
            "target_group": group_id,
            "target_group_name": group_name or group_id,
            "color_info": f"{color_mode} ({chosen_color if color_mode == 'fixed' else 'Ngẫu nhiên'}) | Size: {font_size}"
        }
        self.active_threads = []

        self.add_log(
            f"🚀 BẮT ĐẦU TAB: [{self.name}] | {len(accounts)} Acc | Size chữ: {font_size} | Delay: {delay}s",
            "info"
        )

        valid_thread_count = 0
        for idx, acc in enumerate(accounts):
            imei = acc.get("imei", "").strip()
            cookies = parse_cookies_input(acc.get("cookie", ""))
            if not imei or not cookies:
                self.add_log(f"[Acc #{idx+1}] Bỏ qua vì thiếu IMEI hoặc Cookie hợp lệ", "warning")
                continue

            # Ưu tiên nhóm cấu hình riêng cho tài khoản này, nếu không có mới dùng nhóm chung
            acc_gid = str(acc.get("group_id") or "").strip() or group_id
            acc_gname = str(acc.get("group_name") or "").strip() or (group_name if acc_gid == group_id else f"Nhóm {acc_gid}")

            if not acc_gid:
                self.add_log(f"[Acc #{idx+1}] Bỏ qua vì chưa cấu hình nhóm Zalo", "warning")
                continue

            t = threading.Thread(
                target=self._worker,
                args=(idx, imei, cookies, acc_gid, acc_gname, message_text, delay, color_mode, chosen_color, font_size, ttl),
                daemon=True
            )
            t.start()
            self.active_threads.append(t)
            valid_thread_count += 1

        if valid_thread_count == 0:
            self.is_running = False
            raise ValueError("Không có tài khoản nào đủ điều kiện khởi chạy (kiểm tra lại IMEI, Cookie hoặc nhóm chọn)")

        return True


class MultiTabBotManager:
    """
    Quản lý tập trung toàn bộ các Tab đang chạy
    """
    def __init__(self):
        self.tabs: Dict[str, SingleTabRunner] = {}
        self.lock = threading.Lock()

    def get_or_create_runner(self, tab_id: str, name: str = "") -> SingleTabRunner:
        with self.lock:
            if tab_id not in self.tabs:
                self.tabs[tab_id] = SingleTabRunner(tab_id, name or f"Tab {tab_id}")
            elif name:
                self.tabs[tab_id].name = name
            return self.tabs[tab_id]

    def start_tab(self, tab_id: str, tab_name: str, accounts: list, group_id: str,
                  group_name: str, message_text: str, delay: int, color_mode: str,
                  chosen_color: str, font_size: int, ttl: Optional[int]) -> bool:
        runner = self.get_or_create_runner(tab_id, tab_name)
        return runner.start(
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

    def stop_tab(self, tab_id: str):
        with self.lock:
            if tab_id in self.tabs:
                self.tabs[tab_id].stop()

    def get_tab_status(self, tab_id: str) -> Dict[str, Any]:
        with self.lock:
            if tab_id in self.tabs:
                return self.tabs[tab_id].get_status()
        return {
            "tab_id": tab_id,
            "name": "",
            "is_running": False,
            "runtime_seconds": 0,
            "runtime_formatted": "00:00:00",
            "total_sent": 0,
            "total_failed": 0,
            "acc_count": 0,
            "target_group": "",
            "target_group_name": "",
            "color_info": "",
            "logs": []
        }

    def get_all_tabs_summary(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            summary = {}
            for tid, runner in self.tabs.items():
                summary[tid] = {
                    "is_running": runner.is_running,
                    "runtime_formatted": runner.get_status()["runtime_formatted"],
                    "total_sent": runner.stats["total_sent"],
                    "total_failed": runner.stats["total_failed"],
                    "acc_count": runner.stats["acc_count"],
                    "target_group_name": runner.stats["target_group_name"]
                }
            return summary

    def delete_tab(self, tab_id: str):
        with self.lock:
            if tab_id in self.tabs:
                self.tabs[tab_id].stop()
                del self.tabs[tab_id]

# Singleton instance quản lý đa tab
bot_manager = MultiTabBotManager()
