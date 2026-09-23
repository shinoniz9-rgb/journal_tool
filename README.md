# ⚡ Crypto Trading Journal - Web Application Pro

Ứng dụng Web chuyên nghiệp dành cho Trader Crypto để theo dõi lệnh, ghi nhật ký, kiểm soát tâm lý, phân tích tăng trưởng vốn và xem lịch PnL xanh/đỏ.

Giao diện **Dark Mode** cao cấp lấy cảm hứng từ TradingView & Binance, hỗ trợ dán ảnh biểu đồ trực tiếp từ Clipboard (`Ctrl + V`), sử dụng mượt mà trên cả máy tính và điện thoại.

---

## 🌟 Các Tính Năng Nổi Bật

1. **Ghi Nhận & Quản Lý Lệnh Đầy Đủ**:
   - Hỗ trợ **Futures** và **Spot**, vị thế **Long** và **Short**, đòn bẩy tùy chỉnh từ 1x - 125x.
   - Nhập Entry, Stop Loss, Take Profit, Margin ($), Phí giao dịch.
   - **Tự động tính toán tức thời (Live Calculations)**: Lợi nhuận ròng PnL ($), ROI (%), Tỷ lệ Planned R:R và Realized R:R ngay khi vừa gõ số.
2. **Quản Lý Kỷ Luật & Tâm Lý Giao Dịch**:
   - Ghi nhận chiến lược (Setup): SMC / Order Block, Breakout, Trend Following, Cản/Hỗ trợ, RSI Phân kỳ, Scalp...
   - Ghi nhận tâm lý: Kỷ luật, Tự tin, FOMO, Nóng vội, Sợ hãi, Trả thù thị trường...
   - Phân tích và thống kê tác động của tâm lý đến kết quả giao dịch.
3. **Đính Kèm Ảnh Biểu Đồ TradingView Cực Nhanh**:
   - Khi đang phân tích trên TradingView, chỉ cần nhấn `Alt + S` để sao chép ảnh biểu đồ.
   - Mở form lệnh và bấm `Ctrl + V` hoặc kéo thả ảnh để lưu trữ ngay.
   - Tích hợp trình xem ảnh phóng to (Lightbox) độ phân giải cao.
4. **Dashboard & Thống Kê Hiệu Suất (Analytics)**:
   - Các chỉ số KPI: **Net PnL ($)**, **Win Rate (%)**, **Profit Factor (PF)**, **Average Win / Loss**, **Average R:R**, **Max Streaks**.
   - **Biểu đồ Tăng Trưởng Vốn (Equity Curve)** tương tác mượt mà với Chart.js.
   - Bảng phân tích chi tiết hiệu quả theo từng Chiến lược và Cặp coin.
5. **Lịch PnL (Trading Calendar)**:
   - Hiển thị lịch ngày xanh / ngày đỏ trực quan tương tự các quỹ cấp vốn chuyên nghiệp.
6. **Lưu Trữ An Toàn & Xuất Báo Cáo**:
   - Cơ sở dữ liệu SQLite cục bộ (`data/trading_journal.db`).
   - Chức năng xuất toàn bộ nhật ký ra file **CSV** để mở trên Excel.

---

## 🚀 Hướng Dẫn Khởi Chạy

### Cách 1: Chạy trên máy tính cá nhân
- Nhấp đúp vào file **`start.bat`** (hoặc **`start_web.bat`**).
- Trình duyệt sẽ tự động mở trang web tại địa chỉ: `http://localhost:5000`.

### Cách 2: Mở trên điện thoại (Khác Wi-Fi / 4G)
- Nhấp đúp vào file **`start_tunnel.bat`**.
- Màn hình sẽ hiển thị đường link HTTPS miễn phí để truy cập từ xa trên điện thoại.

### Cách 3: Triển khai lên Cloud (Render.com) dùng 24/7
- Đẩy thư mục mã nguồn lên GitHub cá nhân (chế độ Private).
- Kết nối GitHub với Render.com để nhận đường link cố định `https://...onrender.com`.

---

## 📦 Cấu Trúc Thư Mục

```
journal_tool/
│
├── web_app.py               # Backend Flask xử lý API và phục vụ Web
├── start.bat                # Phím tắt click đúp chạy Web trên Windows
├── start_web.bat            # Phím tắt click đúp chạy Web
├── start_tunnel.bat         # Phím tắt tạo link truy cập điện thoại 4G
├── run_tunnel.py            # Script khởi chạy Cloudflare Tunnel
├── config.py                # Cấu hình danh sách coin, khung giờ, màu sắc
├── requirements.txt         # Khai báo thư viện (Flask, Gunicorn)
├── Procfile                 # File cấu hình deploy Render / Cloud
├── render.yaml              # Cấu hình tự động triển khai Render.com
│
├── templates/
│   └── index.html           # Giao diện chính của Web App
│
├── static/
│   ├── css/
│   │   └── style.css        # Giao diện Dark Theme chuẩn TradingView
│   └── js/
│       └── app.js           # Xử lý tương tác, biểu đồ Chart.js, dán ảnh
│
├── database/
│   └── db_manager.py        # Quản lý cơ sở dữ liệu SQLite
│
├── utils/
│   ├── calculations.py      # Thuật toán tính PnL, ROI, R:R, KPIs
│   └── export_import.py     # Xuất CSV và backup dữ liệu
│
└── data/
    ├── trading_journal.db   # File cơ sở dữ liệu
    └── charts/              # Thư mục lưu ảnh biểu đồ chụp màn hình
```
