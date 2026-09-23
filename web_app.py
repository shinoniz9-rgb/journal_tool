"""
Crypto Trading Journal - Web Application Backend (Flask)
Phục vụ API và Giao diện Web Dark Mode phong cách TradingView
"""
import os
import sys
import io
import base64
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, Response

# Thêm thư mục gốc vào sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import (
    DATA_DIR, CHARTS_DIR, DB_PATH, DEFAULT_PAIRS,
    TIMEFRAMES, TRADE_TYPES, MARKET_TYPES, TRADE_STATUSES,
    DEFAULT_STRATEGIES, DEFAULT_EMOTIONS
)
from database.db_manager import DatabaseManager
from utils.calculations import calculate_trade_metrics, calculate_portfolio_statistics
from utils.export_import import export_trades_to_csv

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "crypto-journal-secret-2026")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Tối đa 16MB ảnh

# Đảm bảo thư mục cần thiết luôn tồn tại
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# Khởi tạo Database Manager
db = DatabaseManager()
db.insert_sample_trades_if_empty()


# ==========================================
# CÁC ROUTE PHỤC VỤ GIAO DIỆN & TÀI NGUYÊN
# ==========================================

@app.route("/")
def index():
    """Trang chủ ứng dụng Web"""
    return render_template("index.html")


@app.route("/charts/<path:filename>")
def serve_chart(filename):
    """Phục vụ ảnh chụp màn hình biểu đồ lưu trong data/charts/"""
    return send_from_directory(CHARTS_DIR, filename)


@app.route("/api/health")
def health_check():
    """Endpoint kiểm tra trạng thái hoạt động (Dành cho Render / UptimeRobot)"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "trades_count": db.count_trades()
    })


# ==========================================
# CÁC API DỮ LIỆU CẤU HÌNH & GỢI Ý
# ==========================================

@app.route("/api/config", methods=["GET"])
def get_config():
    """Lấy danh sách các cặp tiền, khung giờ, chiến lược, tâm lý gợi ý"""
    return jsonify({
        "pairs": DEFAULT_PAIRS,
        "timeframes": TIMEFRAMES,
        "trade_types": TRADE_TYPES,
        "market_types": MARKET_TYPES,
        "statuses": TRADE_STATUSES,
        "strategies": DEFAULT_STRATEGIES,
        "emotions": DEFAULT_EMOTIONS
    })


# ==========================================
# CÁC API THỐNG KÊ & BÁO CÁO (ANALYTICS)
# ==========================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Lấy dữ liệu thống kê KPI, biểu đồ Equity Curve và phân tích chiến lược/tâm lý"""
    trades = db.get_all_trades(order_desc=False)
    stats = calculate_portfolio_statistics(trades)
    return jsonify(stats)


# ==========================================
# CÁC API QUẢN LÝ LỆNH GIAO DỊCH (CRUD)
# ==========================================

@app.route("/api/trades", methods=["GET"])
def get_trades():
    """Lấy danh sách lệnh có hỗ trợ lọc và tìm kiếm"""
    symbol = request.args.get("symbol")
    status = request.args.get("status")
    result = request.args.get("result")
    strategy = request.args.get("strategy")
    search = request.args.get("search")

    trades = db.filter_trades(
        symbol=symbol,
        status=status,
        result=result,
        strategy=strategy,
        search_query=search
    )
    return jsonify(trades)


@app.route("/api/trades/<int:trade_id>", methods=["GET"])
def get_trade(trade_id):
    """Xem chi tiết 1 lệnh"""
    trade = db.get_trade(trade_id)
    if not trade:
        return jsonify({"error": "Không tìm thấy lệnh này"}), 404
    return jsonify(trade)


@app.route("/api/trades", methods=["POST"])
def add_trade():
    """Thêm một lệnh giao dịch mới vào nhật ký"""
    data = request.json or {}
    
    # Tính toán lại các chỉ số tự động để đảm bảo độ chính xác
    try:
        entry_price = float(data.get("entry_price", 0))
        exit_price = float(data["exit_price"]) if data.get("exit_price") not in (None, "") else None
        stop_loss = float(data["stop_loss"]) if data.get("stop_loss") not in (None, "") else None
        take_profit = float(data["take_profit"]) if data.get("take_profit") not in (None, "") else None
        pos_size = float(data.get("position_size", 0))
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
            fees=fees
        )

        # Cập nhật kết quả tính toán vào payload
        data["planned_rr"] = metrics["planned_rr"]
        data["realized_rr"] = metrics["realized_rr"]
        if exit_price is not None:
            data["pnl"] = metrics["pnl"]
            data["pnl_percent"] = metrics["pnl_percent"]

        trade_id = db.add_trade(data)
        return jsonify({"success": True, "trade_id": trade_id, "message": "Thêm lệnh thành công"}), 201

    except Exception as e:
        return jsonify({"error": f"Lỗi xử lý dữ liệu: {str(e)}"}), 400


@app.route("/api/trades/<int:trade_id>", methods=["PUT"])
def update_trade(trade_id):
    """Cập nhật thông tin một lệnh giao dịch"""
    data = request.json or {}
    existing = db.get_trade(trade_id)
    if not existing:
        return jsonify({"error": "Không tìm thấy lệnh"}), 404

    try:
        entry_price = float(data.get("entry_price", existing.get("entry_price", 0)))
        exit_price = float(data["exit_price"]) if data.get("exit_price") not in (None, "") else None
        stop_loss = float(data["stop_loss"]) if data.get("stop_loss") not in (None, "") else None
        take_profit = float(data["take_profit"]) if data.get("take_profit") not in (None, "") else None
        pos_size = float(data.get("position_size", existing.get("position_size", 0)))
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
            fees=fees
        )

        data["planned_rr"] = metrics["planned_rr"]
        data["realized_rr"] = metrics["realized_rr"]
        if exit_price is not None:
            data["pnl"] = metrics["pnl"]
            data["pnl_percent"] = metrics["pnl_percent"]
        elif data.get("status") == "Open":
            data["pnl"] = 0.0
            data["pnl_percent"] = 0.0

        success = db.update_trade(trade_id, data)
        if success:
            return jsonify({"success": True, "message": "Cập nhật lệnh thành công"})
        return jsonify({"error": "Không thể cập nhật"}), 500

    except Exception as e:
        return jsonify({"error": f"Lỗi cập nhật: {str(e)}"}), 400


@app.route("/api/trades/<int:trade_id>", methods=["DELETE"])
def delete_trade(trade_id):
    """Xóa một lệnh giao dịch"""
    existing = db.get_trade(trade_id)
    if not existing:
        return jsonify({"error": "Lệnh không tồn tại"}), 404

    # Xóa file ảnh liên quan nếu có
    chart_path = existing.get("chart_image_path")
    if chart_path and os.path.exists(chart_path):
        try:
            os.remove(chart_path)
        except Exception:
            pass

    success = db.delete_trade(trade_id)
    if success:
        return jsonify({"success": True, "message": "Đã xóa lệnh thành công"})
    return jsonify({"error": "Không thể xóa lệnh"}), 500


# ==========================================
# API DÁN ẢNH / TẢI ẢNH BIỂU ĐỒ (CLIPBOARD & UPLOAD)
# ==========================================

@app.route("/api/upload-chart", methods=["POST"])
def upload_chart():
    """
    Xử lý tải ảnh biểu đồ lên máy chủ:
    - Hỗ trợ dán ảnh trực tiếp từ Clipboard (Base64)
    - Hỗ trợ tải file thông thường (Multipart FormData)
    """
    try:
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
        filepath = os.path.join(CHARTS_DIR, filename)

        # Trường hợp 1: Dán ảnh Clipboard (Base64)
        if request.is_json:
            data = request.json or {}
            base64_data = data.get("image_base64", "")
            if not base64_data:
                return jsonify({"error": "Không có dữ liệu ảnh"}), 400

            # Bỏ header data:image/png;base64, nếu có
            if "," in base64_data:
                base64_data = base64_data.split(",")[1]

            image_bytes = base64.b64decode(base64_data)
            with open(filepath, "wb") as f:
                f.write(image_bytes)

        # Trường hợp 2: Upload file từ ô chọn file (FormData)
        elif "file" in request.files:
            uploaded_file = request.files["file"]
            if uploaded_file.filename == "":
                return jsonify({"error": "Chưa chọn file"}), 400
            uploaded_file.save(filepath)

        else:
            return jsonify({"error": "Dữ liệu ảnh không hợp lệ"}), 400

        # Trả về URL để hiển thị và đường dẫn lưu trữ
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
# API XUẤT CSV (EXPORT DATA)
# ==========================================

@app.route("/api/export-csv", methods=["GET"])
def export_csv():
    """Xuất toàn bộ nhật ký giao dịch ra file CSV có dấu UTF-8 (mở tốt trên Excel)"""
    trades = db.get_all_trades(order_desc=True)
    temp_csv_path = os.path.join(DATA_DIR, "temp_export.csv")
    
    if export_trades_to_csv(trades, temp_csv_path):
        return send_file(
            temp_csv_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"crypto_trading_journal_{datetime.now().strftime('%Y%m%d')}.csv"
        )
    return jsonify({"error": "Không thể xuất file CSV"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Web Crypto Trading Journal đang khởi động tại: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
