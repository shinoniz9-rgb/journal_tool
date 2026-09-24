"""
Database Manager supporting both Cloud PostgreSQL (Neon) and Local SQLite
Bảo toàn dữ liệu vĩnh viễn, chống mất dữ liệu khi deploy lại hệ thống.
"""
import os
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_PATH, DATABASE_URL

try:
    import psycopg2
    from psycopg2.pool import ThreadedConnectionPool
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


class PgCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = None

    def execute(self, query, params=None):
        q = query.replace("?", "%s")
        # Tự động thêm RETURNING id nếu là lệnh INSERT để lấy lastrowid
        if "INSERT INTO" in q.upper() and "RETURNING" not in q.upper():
            q = q.rstrip(";\n\t ") + " RETURNING id;"
            if params is not None:
                self.cursor.execute(q, params)
            else:
                self.cursor.execute(q)
            row = self.cursor.fetchone()
            if row:
                self.lastrowid = row["id"] if isinstance(row, dict) else row[0]
            return self
        if params is not None:
            self.cursor.execute(q, params)
        else:
            self.cursor.execute(q)
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    @property
    def rowcount(self):
        return self.cursor.rowcount


class PgConnectionWrapper:
    def __init__(self, conn, pool=None):
        self.conn = conn
        self.pool = pool

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        is_broken = False
        try:
            if exc_type is not None:
                self.conn.rollback()
                if issubclass(exc_type, (psycopg2.OperationalError, psycopg2.InterfaceError)):
                    is_broken = True
            else:
                self.conn.commit()
        except Exception:
            is_broken = True
        finally:
            if self.pool:
                try:
                    self.pool.putconn(self.conn, close=is_broken)
                except Exception:
                    pass
            else:
                try:
                    self.conn.close()
                except Exception:
                    pass

    def cursor(self):
        return PgCursorWrapper(self.conn.cursor(cursor_factory=RealDictCursor))

    def commit(self):
        self.conn.commit()

    def rollback(self):
        try:
            self.conn.rollback()
        except Exception:
            pass

    def close(self):
        if self.pool:
            try:
                self.pool.putconn(self.conn)
            except Exception:
                pass
        else:
            try:
                self.conn.close()
            except Exception:
                pass


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH, db_url: Optional[str] = DATABASE_URL):
        self.db_path = db_path
        self.db_url = db_url
        self.is_postgres = False
        self.pool = None

        if self.db_url and HAS_POSTGRES:
            try:
                self.pool = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=self.db_url)
                self.is_postgres = True
                print("[+] Connected successfully to Neon PostgreSQL connection pool (1-10 conns)!")
            except Exception as e:
                print(f"[!] Cannot initialize PostgreSQL pool: {e}")
                self.is_postgres = False
                self.pool = None

        self.init_db()

    def get_connection(self):
        if self.is_postgres and self.pool:
            for _ in range(2):
                try:
                    conn = self.pool.getconn()
                    # Kiểm tra kết nối sống trước khi cấp phát (đặc biệt khi Neon tự động ngủ sau 5 phút không hoạt động)
                    if conn.closed == 0:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("SELECT 1;")
                            return PgConnectionWrapper(conn, pool=self.pool)
                        except (psycopg2.OperationalError, psycopg2.InterfaceError):
                            # Socket cũ bị đóng bởi cloud, loại bỏ và lấy kết nối mới
                            self.pool.putconn(conn, close=True)
                            continue
                    else:
                        self.pool.putconn(conn, close=True)
                except Exception as e:
                    print(f"[!] PostgreSQL pool error: {e}")
                    break

            if self.db_url:
                try:
                    return PgConnectionWrapper(psycopg2.connect(self.db_url))
                except Exception as e2:
                    print(f"[!] Direct connect failed: {e2}")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Khởi tạo cấu trúc các bảng"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if self.is_postgres:
                # 1. Bảng Users (PostgreSQL)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    display_name VARCHAR(100),
                    initial_capital DOUBLE PRECISION DEFAULT 1000.0,
                    created_at VARCHAR(50) NOT NULL
                );
                """)

                # 2. Bảng MT5 Accounts (PostgreSQL)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS mt5_accounts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    account_name VARCHAR(100) NOT NULL,
                    server VARCHAR(100) NOT NULL,
                    login VARCHAR(100) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    metaapi_account_id VARCHAR(100),
                    balance DOUBLE PRECISION DEFAULT 0.0,
                    equity DOUBLE PRECISION DEFAULT 0.0,
                    currency VARCHAR(20) DEFAULT 'USD',
                    is_active INTEGER DEFAULT 1,
                    created_at VARCHAR(50) NOT NULL,
                    updated_at VARCHAR(50) NOT NULL
                );
                """)

                # 3. Bảng Trades (PostgreSQL)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER DEFAULT 1 REFERENCES users(id) ON DELETE CASCADE,
                    mt5_account_id INTEGER,
                    symbol VARCHAR(50) NOT NULL,
                    trade_type VARCHAR(20) NOT NULL,
                    market_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    timeframe VARCHAR(20),
                    entry_date VARCHAR(50) NOT NULL,
                    exit_date VARCHAR(50),
                    entry_price DOUBLE PRECISION NOT NULL,
                    exit_price DOUBLE PRECISION,
                    stop_loss DOUBLE PRECISION,
                    take_profit DOUBLE PRECISION,
                    leverage INTEGER DEFAULT 1,
                    position_size DOUBLE PRECISION NOT NULL,
                    risk_amount DOUBLE PRECISION DEFAULT 0.0,
                    fees DOUBLE PRECISION DEFAULT 0.0,
                    pnl DOUBLE PRECISION DEFAULT 0.0,
                    pnl_percent DOUBLE PRECISION DEFAULT 0.0,
                    planned_rr DOUBLE PRECISION DEFAULT 0.0,
                    realized_rr DOUBLE PRECISION DEFAULT 0.0,
                    strategy VARCHAR(100),
                    emotion VARCHAR(100),
                    notes TEXT,
                    lessons TEXT,
                    chart_image_path TEXT,
                    created_at VARCHAR(50) NOT NULL,
                    updated_at VARCHAR(50) NOT NULL
                );
                """)
            else:
                # 1. Bảng Users (SQLite)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    display_name TEXT,
                    initial_capital REAL DEFAULT 1000.0,
                    created_at TEXT NOT NULL
                );
                """)

                # 2. Bảng Trades (SQLite)
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
                    risk_amount REAL DEFAULT 0.0,
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

                # Bảng MT5 Accounts (SQLite)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS mt5_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    account_name TEXT NOT NULL,
                    server TEXT NOT NULL,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL,
                    metaapi_account_id TEXT,
                    balance REAL DEFAULT 0.0,
                    equity REAL DEFAULT 0.0,
                    currency TEXT DEFAULT 'USD',
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """)

                cursor.execute("PRAGMA table_info(trades)")
                trade_columns = [col[1] for col in cursor.fetchall()]
                if "mt5_account_id" not in trade_columns:
                    try:
                        cursor.execute("ALTER TABLE trades ADD COLUMN mt5_account_id INTEGER DEFAULT NULL;")
                    except Exception:
                        pass

            conn.commit()

        self._ensure_default_user()

    def _ensure_default_user(self):
        """Đảm bảo luôn có ít nhất 1 tài khoản mặc định"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
            row = cursor.fetchone()
            if not row:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pwd_hash = generate_password_hash("admin123")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, display_name, initial_capital, created_at) VALUES (?, ?, ?, ?, ?)",
                    ("admin", pwd_hash, "Admin Trader", 1000.0, now)
                )
                conn.commit()
            # Tối ưu hóa hiệu năng truy vấn siêu tốc bằng Database Index
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_entry_date ON trades(entry_date DESC);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_mt5_acc ON trades(mt5_account_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_mt5_ticket ON trades(mt5_ticket);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_mt5_accounts_user_id ON mt5_accounts(user_id);")
                conn.commit()
            except Exception as e:
                print(f"[!] Warning creating indexes: {e}")


    def register_user(self, username: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        username = username.strip().lower()
        if not username or not password:
            return {"success": False, "error": "Tên đăng nhập và mật khẩu không được để trống"}
        if len(username) < 3:
            return {"success": False, "error": "Tên đăng nhập tối thiểu 3 ký tự"}
        if len(password) < 4:
            return {"success": False, "error": "Mật khẩu tối thiểu 4 ký tự"}

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return {"success": False, "error": "Tên đăng nhập đã tồn tại, vui lòng chọn tên khác"}

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pwd_hash = generate_password_hash(password)
            display = (display_name or "").strip() or username.capitalize()
            cursor.execute(
                "INSERT INTO users (username, password_hash, display_name, initial_capital, created_at) VALUES (?, ?, ?, ?, ?)",
                (username, pwd_hash, display, 1000.0, now)
            )
            user_id = cursor.lastrowid
            conn.commit()
            user_obj = {"id": user_id, "username": username, "display_name": display, "initial_capital": 1000.0}
            return {"success": True, "user": user_obj, "user_id": user_id, "username": username, "display_name": display}

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = username.strip().lower()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if not user:
                return None
            stored_hash = user.get("password_hash")
            if stored_hash and check_password_hash(stored_hash, password):
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "display_name": user.get("display_name") or user["username"],
                    "initial_capital": float(user.get("initial_capital", 1000.0))
                }
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, display_name, initial_capital, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_capital(self, user_id: int) -> float:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT initial_capital FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                val = row.get("initial_capital")
                return float(val) if val is not None else 1000.0
            return 1000.0

    def update_user_capital(self, user_id: int, capital: float) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET initial_capital = ? WHERE id = ?", (float(capital), user_id))
            conn.commit()
            return cursor.rowcount > 0

    def reset_user_password(self, username: str, new_password: str) -> Dict[str, Any]:
        username = username.strip().lower()
        if not username or not new_password:
            return {"success": False, "error": "Tên đăng nhập và mật khẩu mới không được để trống"}
        if len(new_password) < 4:
            return {"success": False, "error": "Mật khẩu mới phải từ 4 ký tự trở lên"}

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if not user:
                return {"success": False, "error": "Không tìm thấy tài khoản với tên đăng nhập này"}

            new_hash = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
            conn.commit()
            return {"success": True, "message": "Đặt lại mật khẩu thành công!"}

    # ==========================================
    # CÁC HÀM QUẢN LÝ LỆNH GIAO DỊCH (TRADES)
    # ==========================================
    def add_trade(self, user_id: int, data: Dict[str, Any]) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            mt5_acc_id = data.get("mt5_account_id")
            if mt5_acc_id in (None, "", "all", "none"):
                mt5_acc_id = None
            else:
                try:
                    mt5_acc_id = int(mt5_acc_id)
                except Exception:
                    mt5_acc_id = None

            cursor.execute("""
            INSERT INTO trades (
                user_id, mt5_account_id, symbol, trade_type, market_type, status, timeframe,
                entry_date, exit_date, entry_price, exit_price,
                stop_loss, take_profit, leverage, position_size, risk_amount, fees,
                pnl, pnl_percent, planned_rr, realized_rr,
                strategy, emotion, notes, lessons, chart_image_path,
                created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?
            )
            """, (
                user_id,
                mt5_acc_id,
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
                float(data.get("risk_amount", 0.0)),
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
            cursor.execute("SELECT id FROM trades WHERE id = ? AND user_id = ?", (trade_id, user_id))
            if not cursor.fetchone():
                return False

            fields = ["updated_at = ?"]
            values = [now]

            mapping = {
                "symbol": lambda v: v.upper(),
                "trade_type": str,
                "market_type": str,
                "status": str,
                "timeframe": str,
                "entry_date": str,
                "exit_date": lambda v: v if v not in (None, "") else None,
                "entry_price": float,
                "exit_price": lambda v: float(v) if v not in (None, "") else None,
                "stop_loss": lambda v: float(v) if v not in (None, "") else None,
                "take_profit": lambda v: float(v) if v not in (None, "") else None,
                "leverage": int,
                "position_size": float,
                "risk_amount": float,
                "fees": float,
                "pnl": float,
                "pnl_percent": float,
                "planned_rr": float,
                "realized_rr": float,
                "strategy": str,
                "emotion": str,
                "notes": str,
                "lessons": str,
                "chart_image_path": str
            }

            for key, func in mapping.items():
                if key in data:
                    fields.append(f"{key} = ?")
                    val = data[key]
                    values.append(func(val) if val is not None else None)

            if "mt5_account_id" in data:
                fields.append("mt5_account_id = ?")
                acc_val = data["mt5_account_id"]
                values.append(int(acc_val) if acc_val not in (None, "", "all") else None)

            values.extend([trade_id, user_id])
            cursor.execute(f"UPDATE trades SET {', '.join(fields)} WHERE id = ? AND user_id = ?", values)
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

    def get_all_trades(self, user_id: int, order_desc: bool = True, mt5_account_id: Any = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            order = "DESC" if order_desc else "ASC"
            if mt5_account_id is not None and str(mt5_account_id).lower() not in ("all", "", "none"):
                try:
                    acc_id = int(mt5_account_id)
                    cursor.execute(f"SELECT * FROM trades WHERE user_id = ? AND mt5_account_id = ? ORDER BY id {order}", (user_id, acc_id))
                except Exception:
                    cursor.execute(f"SELECT * FROM trades WHERE user_id = ? ORDER BY id {order}", (user_id,))
            else:
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
        search_query: Optional[str] = None,
        mt5_account_id: Any = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM trades WHERE user_id = ?"
        params = [user_id]

        if mt5_account_id is not None and str(mt5_account_id).lower() not in ("all", "", "none"):
            try:
                acc_id = int(mt5_account_id)
                query += " AND mt5_account_id = ?"
                params.append(acc_id)
            except Exception:
                pass

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
            row = cursor.fetchone()
            return list(row.values())[0] if isinstance(row, dict) else row[0]

    # ==========================================
    # CÁC HÀM QUẢN LÝ TÀI KHOẢN MT5 (MULTI-ACCOUNT)
    # ==========================================
    def add_mt5_account(self, user_id: int, account_name: str, server: str, login: str, password: str, balance: float = 0.0, metaapi_account_id: Optional[str] = None) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO mt5_accounts (
                user_id, account_name, server, login, password,
                metaapi_account_id, balance, equity, currency, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'USD', 1, ?, ?)
            """, (
                user_id,
                account_name.strip() if account_name else f"MT5 #{login}",
                server.strip(),
                str(login).strip(),
                password.strip(),
                metaapi_account_id,
                float(balance or 0.0),
                float(balance or 0.0),
                now,
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def get_mt5_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mt5_accounts WHERE user_id = ? ORDER BY id ASC", (user_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_mt5_account(self, account_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT * FROM mt5_accounts WHERE id = ? AND user_id = ?", (account_id, user_id))
            else:
                cursor.execute("SELECT * FROM mt5_accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_mt5_account_by_login(self, server: str, login: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mt5_accounts WHERE login = ? AND (server LIKE ? OR ? LIKE '%' || server || '%') LIMIT 1", (str(login).strip(), f"%{server.strip()}%", server.strip()))
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT * FROM mt5_accounts WHERE login = ? LIMIT 1", (str(login).strip(),))
                row = cursor.fetchone()
            return dict(row) if row else None

    def update_mt5_balance(self, account_id: int, balance: float, equity: Optional[float] = None) -> bool:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if equity is not None:
                cursor.execute("UPDATE mt5_accounts SET balance = ?, equity = ?, updated_at = ? WHERE id = ?", (float(balance), float(equity), now, account_id))
            else:
                cursor.execute("UPDATE mt5_accounts SET balance = ?, updated_at = ? WHERE id = ?", (float(balance), now, account_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_mt5_account(self, account_id: int, user_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM mt5_accounts WHERE id = ? AND user_id = ?", (account_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
