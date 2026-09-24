"""
Application Configuration and Constants for Crypto Trading Journal
"""
import os
import sys

# Đường dẫn thư mục gốc của ứng dụng (Tương thích cả khi chạy python hoặc chạy file .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.abspath(os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Thư mục dữ liệu & hình ảnh
DATA_DIR = os.path.join(BASE_DIR, "data")
CHARTS_DIR = os.path.join(DATA_DIR, "charts")
DB_PATH = os.path.join(DATA_DIR, "trading_journal.db")

# Đảm bảo các thư mục luôn tồn tại
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# Thông tin ứng dụng
APP_NAME = "Crypto Trading Journal"
APP_VERSION = "1.0.0"
AUTHOR = "Antigravity & Trader"

# Danh sách gợi ý mặc định

# Danh sách mã giao dịch (Chỉ giữ BTC/USDT và XAU/USD)
SYMBOL_CATEGORIES = {
    "⚡ Tiền Mã Hóa (Crypto)": ["BTC/USDT"],
    "🟡 Vàng (Gold)": ["XAU/USD"]
}

DEFAULT_PAIRS = ["BTC/USDT", "XAU/USD"]

TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"]

TRADE_TYPES = ["Long", "Short"]
MARKET_TYPES = ["Futures", "Spot", "Forex / CFD"]
TRADE_STATUSES = ["Open", "Closed", "Cancelled"]

DEFAULT_STRATEGIES = [
    "SMC / Order Block",
    "Breakout / Phá vỡ đỉnh đáy",
    "Trend Following / Bám xu hướng",
    "Support & Resistance / Hỗ trợ & Kháng cự",
    "Reversal / Đảo chiều",
    "Scalp nhanh",
    "EMA Crossover",
    "RSI Phân kỳ",
    "Khác"
]

DEFAULT_EMOTIONS = [
    "Kỷ luật (Disciplined)",
    "Tự tin (Confident)",
    "FOMO (Sợ bỏ lỡ)",
    "Nóng vội (Impatient)",
    "Sợ hãi (Fearful)",
    "Trả thù thị trường (Revenge)",
    "Tham lam (Greedy)",
    "Mệt mỏi / Mất tập trung"
]

# Bảng màu Dark Mode phong cách TradingView / Binance
COLORS = {
    # Nền
    "bg_main": "#0D1117",        # Nền chính tối sẫm
    "bg_card": "#161B22",        # Thẻ card / Container
    "bg_card_hover": "#1F242C",  # Hover thẻ
    "bg_input": "#21262D",       # Ô nhập liệu
    "bg_input_focus": "#30363D", # Focus ô nhập liệu
    "border": "#30363D",         # Viền vi mô
    "border_highlight": "#388BFD",# Viền khi active

    # Màu giao dịch (Crypto standard)
    "profit": "#00F59B",         # Xanh neon rực rỡ (Win / Long)
    "profit_bg": "#0D2E24",      # Nền mờ cho nhãn Win/Long
    "loss": "#FF4757",           # Đỏ cam rực rỡ (Loss / Short)
    "loss_bg": "#33181C",        # Nền mờ cho nhãn Loss/Short
    "breakeven": "#A0AEC0",      # Xám hòa vốn

    # Màu nhấn & bổ trợ
    "accent_blue": "#00B4D8",    # Xanh dương cyan
    "accent_yellow": "#FFD166",  # Vàng cảnh báo / Pending
    "accent_purple": "#7209B7",  # Tím hiện đại

    # Văn bản
    "text_primary": "#F0F6FC",   # Chữ chính trắng sáng
    "text_secondary": "#8B949E", # Chữ phụ xám mờ
    "text_muted": "#6E7681",     # Chữ gợi ý / mờ
}

# Cấu hình Cơ sở dữ liệu Đám mây vĩnh viễn (Neon PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_Htl5RSerw0In@ep-falling-poetry-b5um855v-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require")
