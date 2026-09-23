"""
Export and Backup Utilities
"""
import csv
import shutil
import os
from typing import List, Dict, Any
from config import DB_PATH


def export_trades_to_csv(trades: List[Dict[str, Any]], filepath: str) -> bool:
    """Xuất danh sách lệnh ra file CSV với tiêu đề tiếng Việt và chi tiết rõ ràng"""
    fieldnames = [
        "ID", "Cặp tiền", "Vị thế", "Thị trường", "Trạng thái", "Khung giờ",
        "Ngày vào", "Ngày ra", "Giá vào", "Giá thoát", "Stop Loss", "Take Profit",
        "Đòn bẩy", "Ký quỹ ($)", "Phí ($)", "PnL ($)", "ROI (%)", "R:R Dự tính", "R:R Thực tế",
        "Chiến lược", "Tâm lý", "Ghi chú", "Bài học"
    ]

    key_mapping = [
        ("id", "ID"),
        ("symbol", "Cặp tiền"),
        ("trade_type", "Vị thế"),
        ("market_type", "Thị trường"),
        ("status", "Trạng thái"),
        ("timeframe", "Khung giờ"),
        ("entry_date", "Ngày vào"),
        ("exit_date", "Ngày ra"),
        ("entry_price", "Giá vào"),
        ("exit_price", "Giá thoát"),
        ("stop_loss", "Stop Loss"),
        ("take_profit", "Take Profit"),
        ("leverage", "Đòn bẩy"),
        ("position_size", "Ký quỹ ($)"),
        ("fees", "Phí ($)"),
        ("pnl", "PnL ($)"),
        ("pnl_percent", "ROI (%)"),
        ("planned_rr", "R:R Dự tính"),
        ("realized_rr", "R:R Thực tế"),
        ("strategy", "Chiến lược"),
        ("emotion", "Tâm lý"),
        ("notes", "Ghi chú"),
        ("lessons", "Bài học"),
    ]

    try:
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in trades:
                row = {}
                for key, col_name in key_mapping:
                    val = t.get(key)
                    if val is None:
                        val = ""
                    row[col_name] = val
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
