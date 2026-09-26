"""
Export and Backup Utilities
"""
import csv
import shutil
import os
from typing import List, Dict, Any
from config import DB_PATH


def export_trades_to_csv(trades: List[Dict[str, Any]], filepath: str) -> bool:
    """
    Xuất danh sách lệnh ra file CSV với tiêu đề tiếng Việt và thứ tự cột
    đồng bộ 100% với giao diện Bảng Nhật Ký Lệnh trên Web.
    """
    fieldnames = [
        "#",
        "Cặp Tiền",
        "Vị Thế",
        "Trạng Thái",
        "Giá Vào",
        "SL",
        "Giá Thoát",
        "Phí ($)",
        "Net PnL ($)",
        "ROI (%)",
        "R:R",
        "Biểu Đồ",
        "Thời Gian",
        "Thời Gian Ra",
        "Khung Giờ",
        "Take Profit",
        "Rủi Ro ($)",
        "Ký Quỹ ($)",
        "Đòn Bẩy",
        "Thị Trường",
        "Chiến Lược",
        "Tâm Lý",
        "Ghi Chú",
        "Bài Học",
        "ID Hệ Thống"
    ]

    try:
        total_trades = len(trades)
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for idx, t in enumerate(trades):
                # 1. Số thứ tự hiển thị đồng bộ tuyệt đối với bảng web (#24, #23...)
                stt = f"#{total_trades - idx}"

                # 2. R:R đồng bộ định dạng 1:X.XX như trên web
                rr_val = t.get("realized_rr") if t.get("status") == "Closed" else t.get("planned_rr")
                if rr_val is not None and float(rr_val or 0) > 0:
                    rr_str = f"1:{float(rr_val):.2f}"
                else:
                    rr_str = "-"

                # 3. ROI (%) đồng bộ dấu + / -
                roi_val = t.get("pnl_percent")
                roi_str = f"{float(roi_val):+.2f}%" if roi_val is not None else "-"

                # 4. Biểu đồ
                chart_str = t.get("chart_image_path") or "Không"

                row = {
                    "#": stt,
                    "Cặp Tiền": t.get("symbol") or "",
                    "Vị Thế": t.get("trade_type") or "",
                    "Trạng Thái": t.get("status") or "",
                    "Giá Vào": t.get("entry_price") if t.get("entry_price") is not None else "",
                    "SL": t.get("stop_loss") if t.get("stop_loss") is not None else "",
                    "Giá Thoát": t.get("exit_price") if t.get("exit_price") is not None else "",
                    "Phí ($)": round(float(t.get("fees") or 0.0), 2),
                    "Net PnL ($)": round(float(t.get("pnl") or 0.0), 2),
                    "ROI (%)": roi_str,
                    "R:R": rr_str,
                    "Biểu Đồ": chart_str,
                    "Thời Gian": t.get("entry_date") or "",
                    "Thời Gian Ra": t.get("exit_date") or "",
                    "Khung Giờ": t.get("timeframe") or "",
                    "Take Profit": t.get("take_profit") if t.get("take_profit") is not None else "",
                    "Rủi Ro ($)": t.get("risk_amount") if t.get("risk_amount") is not None else "",
                    "Ký Quỹ ($)": t.get("position_size") if t.get("position_size") is not None else "",
                    "Đòn Bẩy": t.get("leverage") if t.get("leverage") is not None else 1,
                    "Thị Trường": t.get("market_type") or "",
                    "Chiến Lược": t.get("strategy") or "",
                    "Tâm Lý": t.get("emotion") or "",
                    "Ghi Chú": t.get("notes") or "",
                    "Bài Học": t.get("lessons") or "",
                    "ID Hệ Thống": t.get("id") or ""
                }
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"Lỗi khi xuất CSV: {e}")
        return False


def backup_database(destination_path: str) -> bool:
    """Sao lưu file SQLite sang vị trí khác"""
    try:
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, destination_path)
            return True
        return False
    except Exception as e:
        print(f"Lỗi khi sao lưu: {e}")
        return False


def restore_database(source_path: str) -> bool:
    """Khôi phục file SQLite từ bản sao lưu"""
    try:
        if os.path.exists(source_path):
            shutil.copy2(source_path, DB_PATH)
            return True
        return False
    except Exception as e:
        print(f"Lỗi khi phục hồi: {e}")
        return False
