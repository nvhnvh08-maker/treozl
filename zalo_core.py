import uuid
import secrets


import os
import sys
import time
import json
import random
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

import os
import sys
import time
import json
import random
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import requests
    import zlapi
    from zlapi import ZaloAPI, ThreadType, Message
    from zlapi.models import MessageStyle, MultiMsgStyle
    import zlapi._state
    import zlapi._exception
    import zlapi._util
    ZALO_AVAILABLE = True

    def _safe_state_login(self, phone, password, imei, session_cookies=None, user_agent=None):
        if user_agent:
            self._headers["User-Agent"] = user_agent

        cookies = getattr(self, "_cookies", None)
        if not cookies and session_cookies:
            self.set_cookies(session_cookies)
            cookies = getattr(self, "_cookies", None)

        if cookies:
            try:
                url = f"https://wpa.chat.zalo.me/api/login/getLoginInfo?imei={imei}&type=30&client_version=645&computer_name=Web&ts={zlapi._util.now()}"
                req_headers = getattr(self, "_headers", getattr(zlapi._util, "HEADERS", {}))
                response = requests.get(url, headers=req_headers, cookies=cookies, timeout=15)
                data = response.json()

                login_data = data.get("data")
                if not login_data or not isinstance(login_data, dict):
                    err_code = data.get("error_code", "102")
                    err_msg = data.get("error_message", "Phiên đăng nhập không hợp lệ hoặc đã hết hạn")
                    raise zlapi._exception.ZaloLoginError(
                        f"Phiên Zalo hết hạn hoặc IMEI/Cookie không khớp (Mã {err_code}: {err_msg}). "
                        f"Sếp vui lòng vào chat.zalo.me lấy lại token zpw_sek và IMEI mới!"
                    )

                zpw = login_data.get("zpw_ws")
                uid = login_data.get("uid")
                phone = login_data.get("phone_number")
                key = login_data.get("zpw_enk")

                self._config = {
                    "phone_number": str(phone or ""),
                    "secret_key": str(key or ""),
                    "send2me_id": str(uid or ""),
                    "zpw_ws": zpw,
                }

                if self._config.get("secret_key"):
                    self._loggedin = True
                    self.cloud_id = self._config.get("send2me_id")
                    self.user_imei = imei
                else:
                    self._loggedin = False
                    raise zlapi._exception.ZaloLoginError("Không thể trích xuất secret_key từ Zalo. Vui lòng kiểm tra lại Cookie.")
            except zlapi._exception.ZaloLoginError:
                raise
            except Exception as e:
                raise zlapi._exception.ZaloLoginError(f"Lỗi phản hồi máy chủ Zalo: {str(e)}")
        else:
            raise zlapi._exception.LoginMethodNotSupport("Chưa cung cấp Cookie phiên làm việc hợp lệ")

    zlapi._state.State.login = _safe_state_login

except ImportError:
    ZALO_AVAILABLE = False

TOOL_COLOR_LIST = [
    "#DB342E",
    "#15A85F",
    "#F27806",
    "#F7B503",
    "#FFFFFF",
    "#000000"
]

def normalize_ttl_value(ttl):
    
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

def parse_cookies_input(cookie_raw: Any, imei: Optional[str] = None) -> Dict[str, str]:
    
    if not cookie_raw:
        return {}

    res = {}
    if isinstance(cookie_raw, dict):
        res = {str(k).strip(): str(v).strip() for k, v in cookie_raw.items()}
    elif isinstance(cookie_raw, list):
        res = {}
        for item in cookie_raw:
            if isinstance(item, dict) and "name" in item and "value" in item:
                res[str(item["name"]).strip()] = str(item["value"]).strip()
    else:
        cookie_str = str(cookie_raw).strip()
        if not cookie_str:
            return {}

        if (cookie_str.startswith("{") and cookie_str.endswith("}")) or (cookie_str.startswith("[") and cookie_str.endswith("]")):
            try:
                parsed = json.loads(cookie_str)
                res = parse_cookies_input(parsed, imei=imei)
            except Exception:
                pass

        if not res:

            for part in cookie_str.split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if k:
                        res[k] = v

            if not res and len(cookie_str) > 20 and "=" not in cookie_str:
                res["zpw_sek"] = cookie_str

    if "zpw_sek" not in res:
        for k, v in list(res.items()):
            val_str = str(v).strip()
            if val_str.startswith("tzao") or (len(res) == 1 and len(val_str) > 25):
                res["zpw_sek"] = val_str
                break

    if "zpw_sek" in res:
        res["zpw_sek"] = str(res["zpw_sek"]).strip('"\'')

    if imei and str(imei).strip() and "z_uuid" not in res:
        res["z_uuid"] = str(imei).strip()

    return res

def fetch_groups_from_acc(imei: str, cookie_raw: Any) -> List[Dict[str, str]]:
    
    if not ZALO_AVAILABLE:
        raise RuntimeError("Thư viện zlapi chưa được cài đặt. Vui lòng cài: pip install zlapi")

    imei = str(imei).strip()
    cookies = parse_cookies_input(cookie_raw, imei=imei)
    if not imei:
        raise ValueError("IMEI không được để trống")
    if not cookies:
        raise ValueError("Cookie không hợp lệ hoặc để trống")

    try:
        bot = ZaloAPI("api", "secret", imei, cookies)
    except Exception as e:
        err_msg = str(e)
        if "NoneType" in err_msg or "logging in" in err_msg or "secret key" in err_msg:
            raise RuntimeError(
                "Phiên đăng nhập Zalo không hợp lệ hoặc đã hết hạn!\n"
                "👉 Nguyên nhân: Cookie bị hết hạn (do đã đăng xuất hoặc đổi thiết bị), "
                "hoặc IMEI không khớp với phiên đăng nhập chat.zalo.me.\n"
                "👉 Khắc phục: Vào lại chat.zalo.me trên trình duyệt, lấy lại Cookie mới (token zpw_sek) và IMEI (z_uuid) tương ứng."
            )
        raise RuntimeError(f"Lỗi đăng nhập Zalo: {err_msg}")

    groups = []
    try:
        all_groups = bot.fetchAllGroups()
    except Exception as e:
        err_msg = str(e)
        if "NoneType" in err_msg:
            raise RuntimeError("Phiên đăng nhập Zalo đã hết hạn. Vui lòng lấy lại Cookie mới từ chat.zalo.me")
        raise RuntimeError(f"Lỗi kết nối Zalo khi lấy danh sách nhóm: {err_msg}")

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
            err_msg = str(e)
            if "NoneType" in err_msg or "logging in" in err_msg or "secret key" in err_msg:
                self.add_log(
                    f"[{acc_label}] Lỗi đăng nhập: Cookie/IMEI không hợp lệ hoặc phiên đăng nhập đã hết hạn! Vui lòng lấy lại Cookie (zpw_sek) mới trên chat.zalo.me",
                    "error"
                )
            else:
                self.add_log(f"[{acc_label}] Lỗi khởi tạo ZaloAPI: {err_msg}", "error")
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
            cookies = parse_cookies_input(acc.get("cookie", ""), imei=imei)
            if not imei or not cookies:
                self.add_log(f"[Acc #{idx+1}] Bỏ qua vì thiếu IMEI hoặc Cookie hợp lệ", "warning")
                continue

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

bot_manager = MultiTabBotManager()


class ZaloQRManager:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    def create_qr_session(self, acc_index=0):
        with self.lock:
            now_ts = time.time()
            self.sessions = {k: v for k, v in self.sessions.items() if now_ts - v.get('created_at', 0) < 600}
        session_id = secrets.token_hex(16)
        http_session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://id.zalo.me/account/login?continue=https%3A%2F%2Fchat.zalo.me%2F',
            'Origin': 'https://id.zalo.me',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        http_session.headers.update(headers)
        try:
            http_session.get('https://id.zalo.me/account/login', timeout=10)
        except Exception:
            pass
        res = http_session.post('https://id.zalo.me/account/authen/qr/generate', data={'cliGenQR': 0}, timeout=10)
        res_data = res.json()
        if res_data.get('error_code') != 0:
            raise Exception(res_data.get('error_message', 'Không thể tạo mã QR từ Zalo'))
        qr_data = res_data.get('data', {})
        code = qr_data.get('code')
        image = qr_data.get('image')
        session_obj = {
            'session_id': session_id,
            'acc_index': acc_index,
            'code': code,
            'image': image,
            'status': 'waiting-scan',
            'user_info': {},
            'credentials': {},
            'created_at': time.time(),
            'http_session': http_session
        }
        with self.lock:
            self.sessions[session_id] = session_obj
        worker = threading.Thread(target=self._poll_worker, args=(session_id,), daemon=True)
        worker.start()
        return {
            'session_id': session_id,
            'image': image,
            'code': code,
            'status': 'waiting-scan'
        }

    def _poll_worker(self, session_id):
        with self.lock:
            session_obj = self.sessions.get(session_id)
        if not session_obj:
            return
        http_session = session_obj['http_session']
        code = session_obj['code']
        scan_start = time.time()
        while time.time() - scan_start < 150:
            try:
                r_scan = http_session.post('https://id.zalo.me/account/authen/qr/waiting-scan', data={'code': code}, timeout=30)
                scan_res = r_scan.json()
                scan_err = scan_res.get('error_code')
                if scan_err == 0:
                    scan_data = scan_res.get('data') or {}
                    session_obj['status'] = 'scanned'
                    session_obj['user_info'] = {
                        'name': scan_data.get('display_name') or scan_data.get('name') or 'Tài khoản Zalo',
                        'avatar': scan_data.get('avatar') or ''
                    }
                    break
                elif scan_err == 8:
                    continue
                else:
                    session_obj['status'] = 'expired'
                    return
            except Exception:
                continue
        if session_obj.get('status') != 'scanned':
            session_obj['status'] = 'expired'
            return
        conf_start = time.time()
        while time.time() - conf_start < 120:
            try:
                r_conf = http_session.post('https://id.zalo.me/account/authen/qr/waiting-confirm', data={'code': code}, timeout=30)
                conf_res = r_conf.json()
                conf_err = conf_res.get('error_code')
                if conf_err == 0:
                    conf_data = conf_res.get('data') or {}
                    redirect_url = conf_data.get('url')
                    if redirect_url:
                        try:
                            http_session.get(redirect_url, allow_redirects=True, timeout=15)
                        except Exception:
                            pass
                    cookie_dict = http_session.cookies.get_dict()
                    cookie_json = json.dumps(cookie_dict)
                    imei = uuid.uuid4().hex
                    user_name = session_obj['user_info'].get('name') or 'Zalo User'
                    user_avatar = session_obj['user_info'].get('avatar') or ''
                    try:
                        ts = int(time.time() * 1000)
                        test_url = f'https://wpa.chat.zalo.me/api/login/getLoginInfo?imei={imei}&type=30&client_version=645&computer_name=Web&ts={ts}'
                        t_res = http_session.get(test_url, timeout=10)
                        t_data = t_res.json().get('data', {})
                        if t_data and isinstance(t_data, dict):
                            t_name = t_data.get('name') or t_data.get('display_name')
                            if t_name:
                                user_name = t_name
                    except Exception:
                        pass
                    session_obj['credentials'] = {
                        'imei': imei,
                        'cookie': cookie_json,
                        'name': user_name,
                        'avatar': user_avatar
                    }
                    session_obj['status'] = 'confirmed'
                    return
                elif conf_err == 8:
                    continue
                else:
                    session_obj['status'] = 'expired'
                    return
            except Exception:
                continue
        session_obj['status'] = 'expired'

    def get_status(self, session_id):
        with self.lock:
            session_obj = self.sessions.get(session_id)
            if not session_obj:
                return {'status': 'not_found', 'user_info': {}, 'credentials': {}}
            return {
                'session_id': session_id,
                'status': session_obj.get('status', 'unknown'),
                'user_info': session_obj.get('user_info', {}),
                'credentials': session_obj.get('credentials', {})
            }

qr_manager = ZaloQRManager()
