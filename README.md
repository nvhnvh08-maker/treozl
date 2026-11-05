# ZALO TREO TEXT PRO - WEB MULTI-TAB 3D

Hệ thống Web điều khiển và treo text Zalo đa luồng, hỗ trợ đa tài khoản và quản lý nhiều tab độc lập.

## 🚀 Tính năng nổi bật

- **Giao diện 3D Cyberpunk hiện đại**: Tích hợp Three.js Particle 3D, hiệu ứng thẻ 3D Tilt perspective phản chiếu ánh sáng và GSAP ScrollTrigger siêu mượt mà.
- **Cơ sở dữ liệu SQLite**: Quản lý tài khoản đăng ký người dùng an toàn, lưu trữ cấu hình từng tab vĩnh viễn.
- **Menu 3 gạch bên phải**:
  - 📑 **Quản lý tab**: Hiển thị danh sách các tab dạng thẻ ngang. **Full viền xanh lá khi tab đang chạy, full viền đỏ khi tab đã dừng**.
  - ➕ **Tạo tab**: Tạo tab mới và tự động chuyển về Quản lý tab.
  - 📞 **Liên hệ**: Các nút button kết nối trực tiếp Telegram, Zalo, Discord.
- **Cơ chế Treo Text chuẩn xác**:
  - Nhập số lượng tài khoản (IMEI + Cookie).
  - Lấy danh sách nhóm từ Acc #1, chọn nhóm trực quan qua Dropdown.
  - Tải file ngôn `.txt` (gửi toàn bộ nội dung ngôn trong 1 tin nhắn mỗi lượt lặp, không gửi từng dòng).
  - Delay gửi tùy chỉnh.
  - Bảng mã màu chuẩn từ tool (`#DB342E`, `#15A85F`, `#F27806`, `#F7B503`, `#FFFFFF`, `#000000`) cùng chế độ Rainbow (mỗi dòng 1 màu) và Color Picker.
  - Đồng hồ đếm thời gian chạy thực tế và màn hình Console Logs thời gian thực cho từng tab.

## 📦 Cài đặt & Khởi động

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

2. Khởi động máy chủ Web:
- Trên Windows: Nhấp đúp vào file `run_web.bat` hoặc gõ:
```bash
python app.py
```

3. Truy cập vào trình duyệt web:
```
http://localhost:8080
```

## 📞 Liên hệ
- **Telegram**: https://t.me/ngbaodev
- **Zalo**: zalo.me/84988467271
- **Discord**: _5p40
