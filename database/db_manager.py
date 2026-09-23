"""
Database Manager for SQLite Storage with Multi-User Authentication
"""
import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
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
        """Khởi tạo cấu trúc các bảng và tự động bổ sung cột mới nếu cần"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Bảng Users (Hệ thống xác thực đa người dùng)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT,
                created_at TEXT NOT NULL
            );
            """)

            # 2. Bảng Trades (Lưu trữ các lệnh giao dịch)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                market_type TEXT NOT NULL,
                status TEXT NOT NULL,
                timeframe TEXT,
                entry_date TEXT NOT NULL,
                exit_date TEXT,
                entry_price REAL NOT NULL,
                exit_price REAL,
                stop_loss REAL,
                take_profit REAL,
                leverage INTEGER DEFAULT 1,
                position_size REAL NOT NULL,
                fees REAL DEFAULT 0.0,
                pnl REAL DEFAULT 0.0,
                pnl_percent REAL DEFAULT 0.0,
                planned_rr REAL DEFAULT 0.0,
                realized_rr REAL DEFAULT 0.0,
                strategy TEXT,
                emotion TEXT,
                notes TEXT,
                lessons TEXT,
                chart_image_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """)

            # 3. Migration: Kiểm tra và bổ sung cột user_id nếu bảng trades đã tồn tại từ trước
            cursor.execute("PRAGMA table_info(trades)")
            columns = [col[1] for col in cursor.fetchall()]
            if "user_id" not in columns:
                try:
                    cursor.execute("ALTER TABLE trades ADD COLUMN user_id INTEGER DEFAULT 1;")
                except Exception:
                    pass

            conn.commit()

        self._ensure_default_user()

    def _ensure_default_user(self):
        """Đảm bảo luôn có ít nhất 1 tài khoản ban đầu"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                INSERT INTO users (username, password_hash, display_name, created_at)
                VALUES (?, ?, ?, ?)
                """, (
                    "admin",
                    generate_password_hash("123456"),
                    "Admin Trader",
                    now
                ))
                conn.commit()

    # =========================================================================
    # QUẢN LÝ TÀI KHOẢN NGƯỜI DÙNG (USER AUTHENTICATION)
    # =========================================================================

    def register_user(self, username: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        clean_user = username.strip().lower()
        if not clean_user or len(clean_user) < 3:
            return {"success": False, "error": "Tên đăng nhập phải có ít nhất 3 ký tự"}
        if not password or len(password) < 4:
            return {"success": False, "error": "Mật khẩu phải có ít nhất 4 ký tự"}

        disp_name = (display_name.strip() if display_name else "") or clean_user.capitalize()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pwd_hash = generate_password_hash(password)

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (username, password_hash, display_name, created_at)
                VALUES (?, ?, ?, ?)
                """, (clean_user, pwd_hash, disp_name, now))
                conn.commit()
                user_id = cursor.lastrowid
                return {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "username": clean_user,
                        "display_name": disp_name
                    }
                }
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Tên đăng nhập này đã được sử dụng, vui lòng chọn tên khác"}
        except Exception as e:
            return {"success": False, "error": f"Lỗi tạo tài khoản: {str(e)}"}

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        clean_user = username.strip().lower()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (clean_user,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                if check_password_hash(user["password_hash"], password):
                    return {
                        "id": user["id"],
                        "username": user["username"],
                        "display_name": user["display_name"]
                    }
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, display_name, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None


    def reset_user_password(self, username: str, new_password: str) -> Dict[str, Any]:
        """Đặt lại mật khẩu cho tài khoản"""
        clean_user = username.strip().lower()
        if not clean_user or not new_password or len(new_password) < 4:
            return {"success": False, "error": "Mật khẩu mới phải có ít nhất 4 ký tự"}
        pwd_hash = generate_password_hash(new_password)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (pwd_hash, clean_user))
            conn.commit()
            if cursor.rowcount > 0:
                cursor.execute("SELECT id, username, display_name FROM users WHERE username = ?", (clean_user,))
                row = cursor.fetchone()
                return {"success": True, "message": "Đặt lại mật khẩu thành công!", "user": dict(row)}
            return {"success": False, "error": "Không tìm thấy tên đăng nhập này"}

    # =========================================================================
    # QUẢN LÝ LỆNH GIAO DỊCH (TRADES) THEO TỪNG USER
    # =========================================================================

    def add_trade(self, user_id: int, data: Dict[str, Any]) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO trades (
                user_id, symbol, trade_type, market_type, status, timeframe,
                entry_date, exit_date, entry_price, exit_price,
                stop_loss, take_profit, leverage, position_size, fees,
                pnl, pnl_percent, planned_rr, realized_rr,
                strategy, emotion, notes, lessons, chart_image_path,
                created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?
            )
            """, (
                user_id,
                data.get("symbol", "").upper(),
                data.get("trade_type", "Long"),
                data.get("market_type", "Futures"),
                data.get("status", "Open"),
                data.get("timeframe", "H1"),
                data.get("entry_date", now),
                data.get("exit_date"),
                float(data.get("entry_price", 0.0)),
                float(data.get("exit_price")) if data.get("exit_price") not in (None, "") else None,
                float(data.get("stop_loss")) if data.get("stop_loss") not in (None, "") else None,
                float(data.get("take_profit")) if data.get("take_profit") not in (None, "") else None,
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

    def update_trade(self, user_id: int, trade_id: int, data: Dict[str, Any]) -> bool:
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
            WHERE id = ? AND user_id = ?
            """, (
                data.get("symbol", "").upper(),
                data.get("trade_type", "Long"),
                data.get("market_type", "Futures"),
                data.get("status", "Open"),
                data.get("timeframe", "H1"),
                data.get("entry_date"),
                data.get("exit_date"),
                float(data.get("entry_price", 0.0)),
                float(data.get("exit_price")) if data.get("exit_price") not in (None, "") else None,
                float(data.get("stop_loss")) if data.get("stop_loss") not in (None, "") else None,
                float(data.get("take_profit")) if data.get("take_profit") not in (None, "") else None,
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
                trade_id,
                user_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_trade(self, user_id: int, trade_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trades WHERE id = ? AND user_id = ?", (trade_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_trade(self, user_id: int, trade_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades WHERE id = ? AND user_id = ?", (trade_id, user_id))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_trades(self, user_id: int, order_desc: bool = True) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            order = "DESC" if order_desc else "ASC"
            cursor.execute(f"SELECT * FROM trades WHERE user_id = ? ORDER BY id {order}", (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def filter_trades(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        result: Optional[str] = None,
        strategy: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM trades WHERE user_id = ?"
        params = [user_id]

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

    def count_trades(self, user_id: Optional[int] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT COUNT(*) FROM trades WHERE user_id = ?", (user_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM trades")
            return cursor.fetchone()[0]

    def insert_sample_trades_if_empty(self, user_id: int = 1):
        if self.count_trades(user_id) > 0:
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
            }
        ]

        for trade in sample_data:
            self.add_trade(user_id, trade)
