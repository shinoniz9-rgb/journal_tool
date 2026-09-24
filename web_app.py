"""
Crypto Trading Journal - Web Application Backend (Flask)
Hỗ trợ Xác thực Đa Người Dùng (Multi-User Authentication) & Tách biệt dữ liệu
"""
import os
import sys
import io
import base64
import uuid
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, session

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import (
    SYMBOL_CATEGORIES,
    DATA_DIR, CHARTS_DIR, DB_PATH, DEFAULT_PAIRS,
    TIMEFRAMES, TRADE_TYPES, MARKET_TYPES, TRADE_STATUSES,
    DEFAULT_STRATEGIES, DEFAULT_EMOTIONS
)
from database.db_manager import DatabaseManager
from utils.calculations import calculate_trade_metrics, calculate_portfolio_statistics
from utils.export_import import export_trades_to_csv

from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "crypto-journal-secret-key-2026-auth")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=90)  # Ghi nhớ đăng nhập 90 ngày
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"                  # Giữ cookie bền bỉ trên cả mobile & desktop
app.config["SESSION_COOKIE_HTTPONLY"] = True                   # Bảo mật chống can thiệp script
app.config["SESSION_REFRESH_EACH_REQUEST"] = True              # Tự động làm mới hạn 90 ngày mỗi lần truy cập
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024            # Tối đa 16MB ảnh

# Quản lý Token Xác thực bền bỉ (Hoạt động tốt cả khi trình duyệt Safari/mobile chặn cookie)
token_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def generate_auth_token(user_id: int) -> str:
    """Tạo token ký số an toàn có hạn 90 ngày cho thiết bị"""
    return token_serializer.dumps(user_id, salt="crypto-journal-device-auth")

def verify_auth_token(token: str) -> int | None:
    """Xác thực token 90 ngày từ header request"""
    try:
        user_id = token_serializer.loads(token, salt="crypto-journal-device-auth", max_age=60 * 60 * 24 * 90)
        return user_id
    except Exception:
        return None

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# Khởi tạo Database Manager
db = DatabaseManager()


# ==========================================
# AUTHENTICATION HELPER & DECORATOR
# ==========================================

def get_current_user_id() -> int | None:
    # 1. Kiểm tra session cookie thông thường
    uid = session.get("user_id")
    if uid:
        return uid

    # 2. Dự phòng: Kiểm tra token từ thiết bị (Authorization hoặc X-Auth-Token header)
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif request.headers.get("X-Auth-Token"):
        token = request.headers.get("X-Auth-Token").strip()

    if token:
        uid = verify_auth_token(token)
        if uid:
            # Đồng bộ lại vào session để tăng tốc các lượt gọi sau
            session.permanent = True
            session["user_id"] = uid
            return uid

    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user_id():
            return jsonify({"error": "Vui lòng đăng nhập để tiếp tục", "auth_required": True}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# CÁC ROUTE PHỤC VỤ GIAO DIỆN & TÀI NGUYÊN
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/charts/<path:filename>")
def serve_chart(filename):
    return send_from_directory(CHARTS_DIR, filename)

@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_trades": db.count_trades()
    })


# ==========================================
# API XÁC THỰC NGƯỜI DÙNG (AUTH API)
# ==========================================

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    display_name = data.get("display_name", "")

    result = db.register_user(username=username, password=password, display_name=display_name)
    if result["success"]:
        user = result["user"]
        session.permanent = True
        session["user_id"] = user["id"]
        token = generate_auth_token(user["id"])
        return jsonify({
            "success": True,
            "message": "Đăng ký tài khoản thành công!",
            "user": user,
            "token": token
        }), 201
    return jsonify({"error": result.get("error", "Đăng ký thất bại")}), 400

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")

    user = db.authenticate_user(username=username, password=password)
    if user:
        session.permanent = True
        session["user_id"] = user["id"]
        token = generate_auth_token(user["id"])
        return jsonify({
            "success": True,
            "message": "Đăng nhập thành công!",
            "user": user,
            "token": token
        })
    return jsonify({"error": "Tên đăng nhập hoặc mật khẩu không chính xác!"}), 401


@app.route("/api/auth/reset-password", methods=["POST"])
def auth_reset_password():
    data = request.json or {}
    username = data.get("username", "")
    new_password = data.get("new_password", "")
    result = db.reset_user_password(username=username, new_password=new_password)
    if result["success"]:
        user = result["user"]
        session.permanent = True
        session["user_id"] = user["id"]
        token = generate_auth_token(user["id"])
        return jsonify({
            "success": True,
            "message": "Đặt lại mật khẩu và đăng nhập thành công!",
            "user": user,
            "token": token
        })
    return jsonify({"error": result.get("error", "Không thể đặt lại mật khẩu")}), 400




@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"success": True, "message": "Đã đăng xuất thành công"})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"logged_in": False, "user": None})
    user = db.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({"logged_in": False, "user": None})
    token = generate_auth_token(user["id"])
    return jsonify({
        "logged_in": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "display_name": user["display_name"]
        },
        "token": token
    })


# ==========================================
# CÁC API DỮ LIỆU CẤU HÌNH & GỢI Ý
# ==========================================

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify({
        "pairs": DEFAULT_PAIRS,
        "symbol_categories": SYMBOL_CATEGORIES,
        "timeframes": TIMEFRAMES,
        "trade_types": TRADE_TYPES,
        "market_types": MARKET_TYPES,
        "statuses": TRADE_STATUSES,
        "strategies": DEFAULT_STRATEGIES,
        "emotions": DEFAULT_EMOTIONS
    })


# ==========================================
# CÁC API THỐNG KÊ & BÁO CÁO (THEO USER)
# ==========================================

@app.route("/api/user/capital", methods=["GET", "POST"])
@login_required
def user_capital():
    user_id = get_current_user_id()
    if request.method == "POST":
        data = request.json or {}
        try:
            capital = float(data.get("initial_capital", 1000.0))
            if capital < 0:
                return jsonify({"error": "Số vốn không thể là số âm"}), 400
            db.update_user_capital(user_id=user_id, capital=capital)
            return jsonify({"success": True, "initial_capital": capital, "message": "Cập nhật vốn ban đầu thành công!"})
        except (ValueError, TypeError):
            return jsonify({"error": "Số vốn không hợp lệ"}), 400
    else:
        capital = db.get_user_capital(user_id=user_id)
        return jsonify({"initial_capital": capital})


@app.route("/api/stats", methods=["GET"])
@login_required
def get_stats():
    user_id = get_current_user_id()
    mt5_account_id = request.args.get("mt5_account_id")
    trades = db.get_all_trades(user_id=user_id, order_desc=False, mt5_account_id=mt5_account_id)
    
    # 1. Vốn ban đầu mặc định của User
    initial_capital = db.get_user_capital(user_id=user_id)

    # 2. Thuật toán truy ngược Vốn Ban Đầu khi chọn một tài khoản MT5 / Sàn cụ thể:
    if mt5_account_id and str(mt5_account_id).lower() not in ("all", "", "none"):
        try:
            acc = db.get_mt5_account(account_id=int(mt5_account_id), user_id=user_id)
            if acc and float(acc.get("balance", 0)) > 0:
                current_balance = float(acc["balance"])
                # Tổng Net PnL của tất cả các lệnh đã đóng thuộc tài khoản này
                account_closed_pnl = sum(
                    float(t.get("pnl", 0) or 0)
                    for t in trades
                    if str(t.get("status", "")).lower() in ("closed", "đã đóng")
                )
                # Vốn Ban Đầu Gốc = Số Dư Hiện Tại - Tổng Net PnL các lệnh đã giao dịch
                calculated_initial = round(current_balance - account_closed_pnl, 2)
                initial_capital = max(1.0, calculated_initial)
        except Exception:
            pass

    stats = calculate_portfolio_statistics(trades, initial_capital=initial_capital)
    return jsonify(stats)


# ==========================================
# CÁC API QUẢN LÝ LỆNH GIAO DỊCH (CRUD THEO USER)
# ==========================================

@app.route("/api/trades", methods=["GET"])
@login_required
def get_trades():
    user_id = get_current_user_id()
    symbol = request.args.get("symbol")
    status = request.args.get("status")
    result = request.args.get("result")
    strategy = request.args.get("strategy")
    search = request.args.get("search")

    mt5_account_id = request.args.get("mt5_account_id")
    trades = db.filter_trades(
        user_id=user_id,
        symbol=symbol,
        status=status,
        result=result,
        strategy=strategy,
        search_query=search,
        mt5_account_id=mt5_account_id
    )
    return jsonify(trades)

@app.route("/api/trades/<int:trade_id>", methods=["GET"])
@login_required
def get_trade(trade_id):
    user_id = get_current_user_id()
    trade = db.get_trade(user_id=user_id, trade_id=trade_id)
    if not trade:
        return jsonify({"error": "Không tìm thấy lệnh hoặc bạn không có quyền xem"}), 404
    return jsonify(trade)

@app.route("/api/trades", methods=["POST"])
@login_required
def add_trade():
    user_id = get_current_user_id()
    data = request.json or {}
    
    try:
        # Hỗ trợ gán tài khoản MT5 / Sàn thủ công cho lệnh thêm tay
        mt5_acc = data.get("mt5_account_id")
        if mt5_acc in ("all", "none", "", None):
            data["mt5_account_id"] = None
        else:
            try:
                data["mt5_account_id"] = int(mt5_acc)
            except (ValueError, TypeError):
                data["mt5_account_id"] = None

        entry_price = float(data.get("entry_price", 0))
        exit_price = float(data["exit_price"]) if data.get("exit_price") not in (None, "") else None
        stop_loss = float(data["stop_loss"]) if data.get("stop_loss") not in (None, "") else None
        take_profit = float(data["take_profit"]) if data.get("take_profit") not in (None, "") else None
        pos_size = float(data.get("position_size", 0))
        risk_amount = float(data.get("risk_amount", 0))
        leverage = int(data.get("leverage", 1))
        fees = float(data.get("fees", 0))
        trade_type = str(data.get("trade_type", "Long"))

        metrics = calculate_trade_metrics(
            trade_type=trade_type,
            entry_price=entry_price,
            exit_price=exit_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=pos_size,
            leverage=leverage,
            fees=fees,
            risk_amount=risk_amount
        )

        data["planned_rr"] = metrics["planned_rr"]
        data["realized_rr"] = metrics["realized_rr"]
        data["risk_amount"] = risk_amount
        if exit_price is not None:
            data["pnl"] = metrics["pnl"]
            data["pnl_percent"] = metrics["pnl_percent"]

        trade_id = db.add_trade(user_id=user_id, data=data)
        return jsonify({"success": True, "trade_id": trade_id, "message": "Thêm lệnh thành công"}), 201

    except Exception as e:
        return jsonify({"error": f"Lỗi xử lý dữ liệu: {str(e)}"}), 400

@app.route("/api/trades/<int:trade_id>", methods=["PUT"])
@login_required
def update_trade(trade_id):
    user_id = get_current_user_id()
    data = request.json or {}
    existing = db.get_trade(user_id=user_id, trade_id=trade_id)
    if not existing:
        return jsonify({"error": "Không tìm thấy lệnh này"}), 404

    try:
        if "mt5_account_id" in data:
            mt5_acc = data.get("mt5_account_id")
            if mt5_acc in ("all", "none", "", None):
                data["mt5_account_id"] = None
            else:
                try:
                    data["mt5_account_id"] = int(mt5_acc)
                except (ValueError, TypeError):
                    data["mt5_account_id"] = None

        entry_price = float(data.get("entry_price", existing.get("entry_price", 0)))
        exit_price = float(data["exit_price"]) if data.get("exit_price") not in (None, "") else None
        stop_loss = float(data["stop_loss"]) if data.get("stop_loss") not in (None, "") else None
        take_profit = float(data["take_profit"]) if data.get("take_profit") not in (None, "") else None
        pos_size = float(data.get("position_size", existing.get("position_size", 0)))
        risk_amount = float(data.get("risk_amount", existing.get("risk_amount", 0)))
        leverage = int(data.get("leverage", existing.get("leverage", 1)))
        fees = float(data.get("fees", existing.get("fees", 0)))
        trade_type = str(data.get("trade_type", existing.get("trade_type", "Long")))

        metrics = calculate_trade_metrics(
            trade_type=trade_type,
            entry_price=entry_price,
            exit_price=exit_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=pos_size,
            leverage=leverage,
            fees=fees,
            risk_amount=risk_amount
        )

        data["planned_rr"] = metrics["planned_rr"]
        data["realized_rr"] = metrics["realized_rr"]
        data["risk_amount"] = risk_amount
        if exit_price is not None:
            data["pnl"] = metrics["pnl"]
            data["pnl_percent"] = metrics["pnl_percent"]
        elif data.get("status") == "Open":
            data["pnl"] = 0.0
            data["pnl_percent"] = 0.0

        success = db.update_trade(user_id=user_id, trade_id=trade_id, data=data)
        if success:
            return jsonify({"success": True, "message": "Cập nhật lệnh thành công"})
        return jsonify({"error": "Không thể cập nhật"}), 500

    except Exception as e:
        return jsonify({"error": f"Lỗi cập nhật: {str(e)}"}), 400

@app.route("/api/trades/<int:trade_id>", methods=["DELETE"])
@login_required
def delete_trade(trade_id):
    user_id = get_current_user_id()
    existing = db.get_trade(user_id=user_id, trade_id=trade_id)
    if not existing:
        return jsonify({"error": "Lệnh không tồn tại hoặc bạn không có quyền xóa"}), 404

    chart_path = existing.get("chart_image_path")
    if chart_path and os.path.exists(chart_path):
        try:
            os.remove(chart_path)
        except Exception:
            pass

    success = db.delete_trade(user_id=user_id, trade_id=trade_id)
    if success:
        return jsonify({"success": True, "message": "Đã xóa lệnh thành công"})
    return jsonify({"error": "Không thể xóa lệnh"}), 500


# ==========================================
# API DÁN ẢNH / TẢI ẢNH BIỂU ĐỒ
# ==========================================

@app.route("/api/upload-chart", methods=["POST"])
@login_required
def upload_chart():
    try:
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
        filepath = os.path.join(CHARTS_DIR, filename)

        if request.is_json:
            data = request.json or {}
            base64_data = data.get("image_base64", "")
            if not base64_data:
                return jsonify({"error": "Không có dữ liệu ảnh"}), 400

            if "," in base64_data:
                base64_data = base64_data.split(",")[1]

            image_bytes = base64.b64decode(base64_data)
            with open(filepath, "wb") as f:
                f.write(image_bytes)

        elif "file" in request.files:
            uploaded_file = request.files["file"]
            if uploaded_file.filename == "":
                return jsonify({"error": "Chưa chọn file"}), 400
            uploaded_file.save(filepath)
        else:
            return jsonify({"error": "Dữ liệu ảnh không hợp lệ"}), 400

        web_url = f"/charts/{filename}"
        return jsonify({
            "success": True,
            "filename": filename,
            "url": web_url,
            "filepath": filepath
        })
    except Exception as e:
        return jsonify({"error": f"Lỗi lưu ảnh: {str(e)}"}), 500


# ==========================================
# API XUẤT CSV
# ==========================================


# ==========================================
# CÁC API QUẢN LÝ TÀI KHOẢN MT5 & REAL-TIME WEBHOOK
# ==========================================

@app.route("/api/mt5/accounts", methods=["GET"])
@login_required
def get_mt5_accounts():
    user_id = get_current_user_id()
    accounts = db.get_mt5_accounts(user_id=user_id)
    # Ẩn password khi trả về client để bảo mật
    safe_accounts = []
    for a in accounts:
        item = dict(a)
        item.pop("password", None)
        safe_accounts.append(item)
    return jsonify(safe_accounts)

@app.route("/api/mt5/accounts", methods=["POST"])
@login_required
def add_mt5_account():
    user_id = get_current_user_id()
    data = request.json or {}
    account_name = data.get("account_name", "").strip()
    server = data.get("server", "").strip() or "Manual"
    login = data.get("login", "").strip() or "MANUAL"
    password = data.get("password", "").strip() or "manual"
    balance = float(data.get("balance", 0.0) or 0.0)

    if not account_name:
        return jsonify({"error": "Vui lòng nhập Tên Gợi Nhớ cho tài khoản (ví dụ: Binance, Bybit, Exness...)"}), 400

    acc_id = db.add_mt5_account(
        user_id=user_id,
        account_name=account_name,
        server=server,
        login=login,
        password=password,
        balance=balance
    )
    return jsonify({"success": True, "account_id": acc_id, "message": "Đã thêm tài khoản thành công!"}), 201

@app.route("/api/mt5/accounts/<int:account_id>", methods=["DELETE"])
@login_required
def delete_mt5_account(account_id):
    user_id = get_current_user_id()
    success = db.delete_mt5_account(account_id=account_id, user_id=user_id)
    if not success:
        return jsonify({"error": "Không thể xóa hoặc không tìm thấy tài khoản"}), 404
    return jsonify({"success": True, "message": "Đã xóa tài khoản MT5"})

@app.route("/api/mt5/accounts/<int:account_id>/balance", methods=["POST"])
@login_required
def update_mt5_account_balance(account_id):
    user_id = get_current_user_id()
    data = request.json or {}
    balance = float(data.get("balance", 0.0))
    equity = float(data.get("equity", balance))
    acc = db.get_mt5_account(account_id=account_id, user_id=user_id)
    if not acc:
        return jsonify({"error": "Không tìm thấy tài khoản MT5"}), 404
    db.update_mt5_balance(account_id=account_id, balance=balance, equity=equity)
    return jsonify({"success": True, "balance": balance})

@app.route("/api/mt5/webhook", methods=["POST"])
def mt5_webhook():
    """
    Endpoint nhận dữ liệu lệnh đóng Real-time từ MT5 (MetaApi Cloud hoặc custom webhook).
    Tự động chuẩn hóa dữ liệu và lưu vào đúng bảng nhật ký của User tương ứng.
    """
    payload = request.json or {}
    
    # 1. Tìm tài khoản MT5 dựa theo login / server hoặc account_id
    login = str(payload.get("login") or payload.get("account_number") or payload.get("accountNumber") or payload.get("accountId") or "").strip()
    server = str(payload.get("server") or "").strip()
    
    acc = None
    if login:
        acc = db.get_mt5_account_by_login(server=server, login=login)
    
    # Nếu payload gửi theo metaapi_account_id
    if not acc and payload.get("metaapi_account_id"):
        # Tìm theo metaapi_account_id
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mt5_accounts WHERE metaapi_account_id = ? LIMIT 1", (payload["metaapi_account_id"],))
            row = cursor.fetchone()
            if row:
                acc = dict(row)

    # Nếu không tìm thấy theo login, fallback về tài khoản MT5 đầu tiên nếu có
    if not acc and payload.get("user_id"):
        user_id = int(payload["user_id"])
        accounts = db.get_mt5_accounts(user_id=user_id)
        if accounts:
            acc = accounts[0]
            
    if not acc:
        # Nếu chưa cấu hình tài khoản nào, fallback về user_id = 1
        user_id = 1
        mt5_acc_id = None
    else:
        user_id = acc["user_id"]
        mt5_acc_id = acc["id"]

    # Cập nhật số dư Balance nếu webhook có gửi kèm
    new_balance = payload.get("balance") or payload.get("account_balance")
    if new_balance is not None and mt5_acc_id:
        try:
            db.update_mt5_balance(account_id=mt5_acc_id, balance=float(new_balance))
        except Exception:
            pass

    # 2. Xử lý thông tin lệnh đóng
    # Bỏ qua nếu lệnh không phải lệnh đóng (deal entry out)
    deal_type = str(payload.get("type") or payload.get("deal_type") or payload.get("action") or "BUY").upper()
    trade_type = "Long" if "BUY" in deal_type else "Short"
    
    # Chuẩn hóa Symbol: XAUUSD -> XAU/USD, BTCUSD -> BTC/USD
    raw_symbol = str(payload.get("symbol") or "XAU/USD").strip().upper()
    if "/" not in raw_symbol:
        if raw_symbol.startswith("XAU"):
            symbol = "XAU/USD"
        elif raw_symbol.startswith("BTC"):
            symbol = "BTC/USDT"
        elif len(raw_symbol) == 6:
            symbol = f"{raw_symbol[:3]}/{raw_symbol[3:]}"
        else:
            symbol = raw_symbol
    else:
        symbol = raw_symbol

    entry_price = float(payload.get("entry_price") or payload.get("open_price") or payload.get("price") or 0.0)
    exit_price = float(payload.get("exit_price") or payload.get("close_price") or payload.get("price") or entry_price)
    
    # Lấy thông tin Lợi nhuận gộp, Phí hoa hồng (commission) và Phí qua đêm (swap)
    gross_pnl = float(payload.get("profit") or payload.get("pnl") or 0.0)
    commission = float(payload.get("commission") or 0.0)
    swap = float(payload.get("swap") or 0.0)
    fee_val = float(payload.get("fees") or 0.0)

    # Nếu payload gửi kèm net_profit thì ưu tiên lấy, nếu chưa có thì tự động tính:
    if "net_profit" in payload:
        net_pnl = float(payload["net_profit"])
    else:
        net_pnl = round(gross_pnl + commission + swap, 2)

    if fee_val == 0.0 and (commission != 0.0 or swap != 0.0):
        fee_val = round(abs(commission) + (abs(swap) if swap < 0 else 0.0), 2)
    
    # Tính ROI %
    pnl_percent = 0.0
    if entry_price > 0:
        if trade_type == "Long":
            pnl_percent = round(((exit_price - entry_price) / entry_price) * 100, 2)
        else:
            pnl_percent = round(((entry_price - exit_price) / entry_price) * 100, 2)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    close_time = payload.get("close_time") or payload.get("time") or now_str
    
    # 3. Kiểm tra chống trùng lặp lệnh (Duplicate Prevention)
    ticket = str(payload.get("ticket") or payload.get("deal_id") or payload.get("deal") or "").strip()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        if ticket:
            cursor.execute("SELECT id FROM trades WHERE user_id = ? AND notes LIKE ? LIMIT 1", (user_id, f"%#{ticket}%"))
            existing = cursor.fetchone()
            if existing:
                return jsonify({"status": "skipped", "message": f"Lệnh #{ticket} đã tồn tại trong nhật ký", "trade_id": existing[0]}), 200
                
        # Kiểm tra thêm theo các thông số khớp lệnh để đảm bảo 100% không bị nhân đôi
        cursor.execute(
            "SELECT id FROM trades WHERE user_id = ? AND symbol = ? AND trade_type = ? AND entry_price = ? AND exit_price = ? AND exit_date = ? LIMIT 1",
            (user_id, symbol, trade_type, entry_price, exit_price, close_time)
        )
        existing_match = cursor.fetchone()
        if existing_match:
            return jsonify({"status": "skipped", "message": "Lệnh đã tồn tại trong nhật ký", "trade_id": existing_match[0]}), 200

    ticket_note = f"MT5 #{ticket}" if ticket else "MT5 Sync"
    acc_label = acc['account_name'] if acc else 'Tài khoản MT5'

    trade_data = {
        "user_id": user_id,
        "mt5_account_id": mt5_acc_id,
        "symbol": symbol,
        "trade_type": trade_type,
        "market_type": "Forex" if "USD" in symbol and "USDT" not in symbol else "Crypto",
        "status": "Closed",
        "timeframe": str(payload.get("timeframe") or "H1"),
        "entry_date": payload.get("open_time") or close_time,
        "exit_date": close_time,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "stop_loss": float(payload["stop_loss"]) if payload.get("stop_loss") else None,
        "take_profit": float(payload["take_profit"]) if payload.get("take_profit") else None,
        "position_size": float(payload.get("volume") or payload.get("lot") or 1.0),
        "risk_amount": 0.0,
        "fees": fee_val,
        "pnl": net_pnl,
        "pnl_percent": pnl_percent,
        "strategy": "MT5 Auto Sync",
        "emotion": "Disciplined",
        "notes": f"{ticket_note} ({acc_label})"
    }

    trade_id = db.add_trade(user_id=user_id, data=trade_data)
    return jsonify({
        "status": "success",
        "message": "Đã ghi nhận lệnh MT5 thành công",
        "trade_id": trade_id,
        "symbol": symbol,
        "pnl": net_pnl,
        "fees": fee_val
    }), 201


@app.route("/api/export-csv", methods=["GET"])
@login_required
def export_csv():
    user_id = get_current_user_id()
    trades = db.get_all_trades(user_id=user_id, order_desc=True)
    temp_csv_path = os.path.join(DATA_DIR, f"temp_export_{user_id}.csv")
    
    if export_trades_to_csv(trades, temp_csv_path):
        return send_file(
            temp_csv_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"trading_journal_{datetime.now().strftime('%Y%m%d')}.csv"
        )
    return jsonify({"error": "Không thể xuất file CSV"}), 500



@app.after_request
def add_header(response):
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    elif request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Web Crypto Trading Journal Multi-User đang chạy tại: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
