# -*- coding: utf-8 -*-
"""
Script Đồng Bộ Lệnh MT5 1-Chạm (1-Click Sync) vào Trading Journal.
Tự động quét các lệnh đóng từ MT5 và đẩy lên Website Render.
Hoàn toàn chống trùng lặp, bảo toàn dữ liệu.
"""
import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests

try:
    import MetaTrader5 as mt5
except ImportError:
    os.system("pip install MetaTrader5 -q")
    import MetaTrader5 as mt5

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "trading_journal.db")
WEBHOOK_URL = "https://crypto-journal-twhs.onrender.com/api/mt5/webhook"

def get_accounts():
    """Lấy danh sách tài khoản MT5 đã lưu trong web"""
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mt5_accounts WHERE is_active = 1")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"[!] Lỗi đọc dữ liệu tài khoản: {e}")
        return []

def main():
    print("=" * 60)
    print("          TRADING JOURNAL - ĐỒNG BỘ LỆNH MT5 1-CHẠM")
    print("=" * 60)

    # 1. Khởi động MT5
    if not mt5.initialize():
        print("[-] Không thể kết nối với phần mềm MT5 trên máy tính!")
        print("    Vui lòng kiểm tra xem bạn đã cài đặt MetaTrader 5 chưa.")
        print(f"    Mã lỗi MT5: {mt5.last_error()}")
        return

    accounts = get_accounts()
    if not accounts:
        # Nếu chưa lưu trong DB, lấy thông tin tài khoản MT5 đang đăng nhập sẵn trên máy
        acc_info = mt5.account_info()
        if acc_info:
            accounts = [{
                "id": 1,
                "user_id": 1,
                "account_name": f"MT5 #{acc_info.login}",
                "server": acc_info.server,
                "login": str(acc_info.login),
                "password": "",
                "balance": acc_info.balance
            }]
        else:
            print("[!] Chưa có tài khoản MT5 nào được cấu hình trên web!")
            print("    Vui lòng mở web -> Chọn [Quản lý MT5] -> Thêm tài khoản trước.")
            mt5.shutdown()
            return

    total_new = 0
    total_skipped = 0

    for acc in accounts:
        login_num = int(acc["login"])
        server_name = acc["server"]
        password = acc["password"]

        print(f"\n[*] Đang kết nối tài khoản: {acc['account_name']} (#{login_num})")
        print(f"    Server: {server_name}")

        # Đăng nhập vào MT5
        logged_in = False
        if password:
            logged_in = mt5.login(login=login_num, password=password, server=server_name)
        else:
            logged_in = True

        acc_info = mt5.account_info()
        if not acc_info or (acc_info.login != login_num and not logged_in):
            print(f"[-] Đăng nhập tài khoản MT5 #{login_num} thất bại! Kiểm tra mật khẩu hoặc server.")
            continue

        current_balance = acc_info.balance
        current_equity = acc_info.equity
        print(f"[+] Kết nối thành công! Số dư hiện tại: ${current_balance:,.2f} USD")

        # Quét lịch sử 90 ngày gần nhất
        from_date = datetime.now() - timedelta(days=90)
        to_date = datetime.now() + timedelta(days=1)
        deals = mt5.history_deals_get(from_date, to_date)

        if not deals:
            print("[i] Không có lệnh nào trong 90 ngày qua.")
            continue

        acc_new = 0
        acc_skipped = 0

        for deal in deals:
            # Chỉ lấy các lệnh đóng (DEAL_ENTRY_OUT hoặc DEAL_ENTRY_INOUT) có symbol
            if deal.entry in (mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_INOUT) and deal.symbol:
                deal_time = datetime.fromtimestamp(deal.time).strftime("%Y-%m-%d %H:%M:%S")
                trade_type = "BUY" if deal.type == mt5.DEAL_TYPE_BUY else "SELL"
                
                payload = {
                    "login": str(login_num),
                    "server": server_name,
                    "ticket": str(deal.ticket),
                    "deal_id": str(deal.ticket),
                    "type": trade_type,
                    "symbol": deal.symbol,
                    "entry_price": deal.price,
                    "exit_price": deal.price,
                    "profit": float(deal.profit),
                    "volume": float(deal.volume),
                    "balance": float(current_balance),
                    "close_time": deal_time,
                    "open_time": deal_time
                }

                try:
                    res = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                    if res.status_code == 201:
                        data = res.json()
                        pnl_str = f"+${deal.profit:.2f}" if deal.profit >= 0 else f"-${abs(deal.profit):.2f}"
                        print(f"    [+] MỚI: {deal.symbol} {trade_type} | Lãi/Lỗ: {pnl_str} | Vé #{deal.ticket}")
                        acc_new += 1
                    elif res.status_code == 200:
                        acc_skipped += 1
                except Exception as ex:
                    print(f"    [!] Lỗi gửi lệnh #{deal.ticket}: {ex}")

        print(f"    -> Đã thêm mới: {acc_new} lệnh.")
        print(f"    -> Đã bỏ qua: {acc_skipped} lệnh (Đã có sẵn trên web, không trùng lặp).")
        total_new += acc_new
        total_skipped += acc_skipped

    mt5.shutdown()

    print("\n" + "=" * 60)
    print("                    TỔNG KẾT ĐỒNG BỘ")
    print("=" * 60)
    print(f"[✔] Tổng lệnh mới đã thêm vào Web : {total_new} lệnh")
    print(f"[✔] Tổng lệnh cũ đã có sẵn       : {total_skipped} lệnh")
    print("=" * 60)
    print(">>> ĐỒNG BỘ HOÀN TẤT! Hãy mở website để xem nhật ký.")
    print("    Website: https://crypto-journal-twhs.onrender.com/")

if __name__ == "__main__":
    main()
