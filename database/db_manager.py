"""
Database Manager for SQLite Storage
"""
import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import DB_PATH


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Khởi tạo cấu trúc bảng nếu chưa có"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL,         -- 'Long' / 'Short'
                market_type TEXT NOT NULL,        -- 'Futures' / 'Spot'
                status TEXT NOT NULL,             -- 'Open' / 'Closed' / 'Cancelled'
                timeframe TEXT,                   -- 'M5', 'H1', 'H4'...
                entry_date TEXT NOT NULL,         -- 'YYYY-MM-DD HH:MM:SS'
                exit_date TEXT,                   -- 'YYYY-MM-DD HH:MM:SS'
                entry_price REAL NOT NULL,
                exit_price REAL,
                stop_loss REAL,
                take_profit REAL,
                leverage INTEGER DEFAULT 1,
                position_size REAL NOT NULL,      -- Margin ($) hoặc Vị thế
                fees REAL DEFAULT 0.0,
                pnl REAL DEFAULT 0.0,             -- Lợi nhuận ròng ($)
                pnl_percent REAL DEFAULT 0.0,     -- ROI (%)
                planned_rr REAL DEFAULT 0.0,      -- Tỷ lệ R:R dự kiến
                realized_rr REAL DEFAULT 0.0,     -- Tỷ lệ R:R thực tế
                strategy TEXT,                    -- Chiến lược vào lệnh
                emotion TEXT,                     -- Tâm lý giao dịch
                notes TEXT,                       -- Phân tích / Lý do vào lệnh
                lessons TEXT,                     -- Bài học / Sai lầm
                chart_image_path TEXT,            -- Đường dẫn ảnh chart
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """)
            conn.commit()

    def add_trade(self, data: Dict[str, Any]) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO trades (
                symbol, trade_type, market_type, status, timeframe,
                entry_date, exit_date, entry_price, exit_price,
                stop_loss, take_profit, leverage, position_size, fees,
                pnl, pnl_percent, planned_rr, realized_rr,
                strategy, emotion, notes, lessons, chart_image_path,
                created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?
            )
            """, (
                data.get("symbol", "").upper(),
                data.get("trade_type", "Long"),
                data.get("market_type", "Futures"),
                data.get("status", "Open"),
                data.get("timeframe", "H1"),
                data.get("entry_date", now),
                data.get("exit_date"),
                float(data.get("entry_price", 0.0)),
                float(data.get("exit_price")) if data.get("exit_price") is not None else None,
                float(data.get("stop_loss")) if data.get("stop_loss") is not None else None,
                float(data.get("take_profit")) if data.get("take_profit") is not None else None,
                int(data.get("leverage", 1)),
                float(data.get("position_size", 0.0)),
                float(data.get("fees", 0.0)),
                float(data.get("pnl", 0.0)),
                float(data.get("pnl_percent", 0.0)),
                float(data.get("planned_rr", 0.0)),
                float(data.get("realized_rr", 0.0)),
                data.get("strategy", ""),
                data.get("emotion", ""),
                data.get("notes", ""),
                data.get("lessons", ""),
                data.get("chart_image_path", ""),
                now,
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def update_trade(self, trade_id: int, data: Dict[str, Any]) -> bool:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE trades SET
                symbol = ?, trade_type = ?, market_type = ?, status = ?, timeframe = ?,
                entry_date = ?, exit_date = ?, entry_price = ?, exit_price = ?,
                stop_loss = ?, take_profit = ?, leverage = ?, position_size = ?, fees = ?,
                pnl = ?, pnl_percent = ?, planned_rr = ?, realized_rr = ?,
                strategy = ?, emotion = ?, notes = ?, lessons = ?, chart_image_path = ?,
                updated_at = ?
            WHERE id = ?
            """, (
                data.get("symbol", "").upper(),
                data.get("trade_type", "Long"),
                data.get("market_type", "Futures"),
                data.get("status", "Open"),
                data.get("timeframe", "H1"),
                data.get("entry_date"),
                data.get("exit_date"),
                float(data.get("entry_price", 0.0)),
                float(data.get("exit_price")) if data.get("exit_price") is not None else None,
                float(data.get("stop_loss")) if data.get("stop_loss") is not None else None,
                float(data.get("take_profit")) if data.get("take_profit") is not None else None,
                int(data.get("leverage", 1)),
                float(data.get("position_size", 0.0)),
                float(data.get("fees", 0.0)),
                float(data.get("pnl", 0.0)),
                float(data.get("pnl_percent", 0.0)),
                float(data.get("planned_rr", 0.0)),
                float(data.get("realized_rr", 0.0)),
                data.get("strategy", ""),
                data.get("emotion", ""),
                data.get("notes", ""),
                data.get("lessons", ""),
                data.get("chart_image_path", ""),
                now,
                trade_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_trade(self, trade_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_trade(self, trade_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_trades(self, order_desc: bool = True) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            order = "DESC" if order_desc else "ASC"
            cursor.execute(f"SELECT * FROM trades ORDER BY id {order}")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def filter_trades(
        self,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        result: Optional[str] = None,  # 'All', 'Win', 'Loss', 'Breakeven'
        strategy: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM trades WHERE 1=1"
        params = []

        if symbol and symbol != "Tất cả":
            query += " AND symbol LIKE ?"
            params.append(f"%{symbol.strip()}%")

        if status and status != "Tất cả":
            query += " AND status = ?"
            params.append(status)

        if result and result != "Tất cả":
            if result == "Thắng (Win)":
                query += " AND status = 'Closed' AND pnl > 0"
            elif result == "Thua (Loss)":
                query += " AND status = 'Closed' AND pnl < 0"
            elif result == "Hòa (Breakeven)":
                query += " AND status = 'Closed' AND pnl = 0"

        if strategy and strategy != "Tất cả":
            query += " AND strategy = ?"
            params.append(strategy)

        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += " AND (symbol LIKE ? OR notes LIKE ? OR lessons LIKE ? OR strategy LIKE ?)"
            params.extend([sq, sq, sq, sq])

        query += " ORDER BY id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    def count_trades(self) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trades")
            return cursor.fetchone()[0]

    def insert_sample_trades_if_empty(self):
        """Thêm dữ liệu mẫu nếu database đang trống để người dùng trải nghiệm ngay"""
        if self.count_trades() > 0:
            return

        sample_data = [
            {
                "symbol": "BTC/USDT",
                "trade_type": "Long",
                "market_type": "Futures",
                "status": "Closed",
                "timeframe": "H1",
                "entry_date": "2026-09-15 08:30:00",
                "exit_date": "2026-09-15 14:45:00",
                "entry_price": 58200.0,
                "exit_price": 60500.0,
                "stop_loss": 57400.0,
                "take_profit": 60600.0,
                "leverage": 10,
                "position_size": 200.0,
                "fees": 4.5,
                "pnl": 74.56,
                "pnl_percent": 37.28,
                "planned_rr": 3.0,
                "realized_rr": 2.88,
                "strategy": "SMC / Order Block",
                "emotion": "Kỷ luật (Disciplined)",
                "notes": "Bắt sóng hồi tại vùng Order Block H1 sau khi quét thanh khoản đáy cũ.",
                "lessons": "Kiên nhẫn chờ retest là yếu tố sống còn.",
                "chart_image_path": ""
            },
            {
                "symbol": "ETH/USDT",
                "trade_type": "Short",
                "market_type": "Futures",
                "status": "Closed",
                "timeframe": "M15",
                "entry_date": "2026-09-16 10:15:00",
                "exit_date": "2026-09-16 11:30:00",
                "entry_price": 2420.0,
                "exit_price": 2360.0,
                "stop_loss": 2445.0,
                "take_profit": 2350.0,
                "leverage": 10,
                "position_size": 150.0,
                "fees": 3.2,
                "pnl": 34.0,
                "pnl_percent": 22.67,
                "planned_rr": 2.8,
                "realized_rr": 2.4,
                "strategy": "Breakout / Phá vỡ đỉnh đáy",
                "emotion": "Tự tin (Confident)",
                "notes": "Phá vỡ cản hỗ trợ M15 với volume lớn.",
                "lessons": "Chốt lời từng phần khi chạm cản tâm lý.",
                "chart_image_path": ""
            },
            {
                "symbol": "SOL/USDT",
                "trade_type": "Long",
                "market_type": "Futures",
                "status": "Closed",
                "timeframe": "H4",
                "entry_date": "2026-09-17 19:00:00",
                "exit_date": "2026-09-18 03:20:00",
                "entry_price": 142.5,
                "exit_price": 139.0,
                "stop_loss": 139.0,
                "take_profit": 152.0,
                "leverage": 5,
                "position_size": 250.0,
                "fees": 2.8,
                "pnl": -33.5,
                "pnl_percent": -13.4,
                "planned_rr": 2.71,
                "realized_rr": -1.0,
                "strategy": "Trend Following / Bám xu hướng",
                "emotion": "FOMO (Sợ bỏ lỡ)",
                "notes": "Vào lệnh quá sớm khi nến H4 chưa đóng, bị quét râu dính Stop Loss.",
                "lessons": "Không FOMO khi nến chưa đóng cửa xác nhận!",
                "chart_image_path": ""
            },
            {
                "symbol": "BTC/USDT",
                "trade_type": "Short",
                "market_type": "Futures",
                "status": "Open",
                "timeframe": "H4",
                "entry_date": "2026-09-21 16:00:00",
                "exit_date": None,
                "entry_price": 63800.0,
                "exit_price": None,
                "stop_loss": 64600.0,
                "take_profit": 61500.0,
                "leverage": 10,
                "position_size": 300.0,
                "fees": 3.0,
                "pnl": 0.0,
                "pnl_percent": 0.0,
                "planned_rr": 2.88,
                "realized_rr": 0.0,
                "strategy": "RSI Phân kỳ",
                "emotion": "Kỷ luật (Disciplined)",
                "notes": "Phân kỳ đỉnh RSI trên khung H4 chạm vùng kháng cự cứng.",
                "lessons": "",
                "chart_image_path": ""
            }
        ]

        for item in sample_data:
            self.add_trade(item)
