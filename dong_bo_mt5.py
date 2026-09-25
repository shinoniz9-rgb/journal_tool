# -*- coding: utf-8 -*-
"""
Script Đồng Bộ Lệnh MT5 1-Chạm (1-Click Sync) vào Trading Journal.
Tự động quét các lệnh đã đóng từ MT5 trên máy tính và đẩy lên Website.
Hoàn toàn chống trùng lặp, bảo toàn 100% dữ liệu lịch sử.
"""
import sys
import os
import json
from datetime import datetime, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import requests
except ImportError:
    print("[*] Đang cài đặt thư viện 'requests'...")
    os.system("pip install requests -q")
    import requests

try:
    import MetaTrader5 as mt5
except ImportError:
    print("[*] Đang cài đặt thư viện 'MetaTrader5'...")
    os.system("pip install MetaTrader5 -q")
    import MetaTrader5 as mt5

WEBHOOK_URL = "https://crypto-journal-twhs.onrender.com/api/mt5/webhook"

def main():
    print("=" * 65)
    print("          TRADING JOURNAL - ĐỒNG BỘ LỆNH MT5 1-CHẠM")
    print("=" * 65)

    # 1. Khởi tạo kết nối MetaTrader 5
    if not mt5.initialize():
        print("\n[-] Không thể kết nối với phần mềm MetaTrader 5 trên máy tính!")
        print("    Vui lòng kiểm tra:")
        print("    1. Phần mềm MetaTrader 5 (MT5) đã được mở và đã đăng nhập tài khoản.")
        print("    2. Kiểm tra biểu tượng kết nối mạng góc dưới bên phải MT5 đã có vạch sóng xanh.")
        print(f"    Mã lỗi MT5: {mt5.last_error()}\n")
        return

    # 2. Lấy thông tin tài khoản MT5 đang hoạt động trên máy
    acc_info = mt5.account_info()
    if not acc_info:
        print("\n[-] Không lấy được thông tin tài khoản MT5. Vui lòng đăng nhập vào MT5 trước.")
        mt5.shutdown()
        return

    login_num = acc_info.login
    server_name = acc_info.server
    current_balance = acc_info.balance
    current_equity = acc_info.equity
    currency = acc_info.currency or "USD"

    print(f"\n[+] Kết nối MT5 thành công!")
    print(f"    - Tài khoản : #{login_num}")
    print(f"    - Server    : {server_name}")
    print(f"    - Số dư     : ${current_balance:,.2f} {currency}")
    print(f"    - Vốn Equity: ${current_equity:,.2f} {currency}")

    # 3. Quét lịch sử lệnh trong 90 ngày gần nhất
    days_back = 90
    from_date = datetime.now() - timedelta(days=days_back)
    to_date = datetime.now() + timedelta(days=1)
    print(f"\n[*] Đang quét lịch sử lệnh đóng trong {days_back} ngày qua...")

    deals = mt5.history_deals_get(from_date, to_date)
    if deals is None or len(deals) == 0:
        print("[i] Không tìm thấy lệnh nào trong 90 ngày qua.")
        mt5.shutdown()
        return

    acc_new = 0
    acc_skipped = 0

    print(f"[*] Tìm thấy {len(deals)} bản ghi lịch sử, đang đối soát với Web Journal...")

    for deal in deals:
        # Chỉ lấy các lệnh đóng (DEAL_ENTRY_OUT hoặc DEAL_ENTRY_INOUT) có mã giao dịch
        if deal.entry in (mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_INOUT) and deal.symbol:
            pos_id = getattr(deal, "position_id", None)
            pos_deals = [d for d in deals if d.position_id == pos_id] if pos_id else [deal]
            in_deals = [d for d in pos_deals if d.entry == mt5.DEAL_ENTRY_IN]
            in_deal = in_deals[0] if in_deals else None
            
            close_time = datetime.fromtimestamp(deal.time).strftime("%Y-%m-%d %H:%M:%S")
            exit_price = float(deal.price)

            if in_deal:
                trade_type = "Long" if in_deal.type == mt5.DEAL_TYPE_BUY else "Short"
                entry_price = float(in_deal.price)
                open_time = datetime.fromtimestamp(in_deal.time).strftime("%Y-%m-%d %H:%M:%S")
            else:
                trade_type = "Long" if deal.type == mt5.DEAL_TYPE_SELL else "Short"
                entry_price = exit_price
                open_time = close_time

            # Tổng hợp toàn bộ Phí hoa hồng (Commission), Phí qua đêm (Swap) và Phí sàn (Fee) của toàn bộ vị thế này (cả chiều mở và đóng)
            gross_profit = float(deal.profit)
            total_comm = sum(float(getattr(d, "commission", 0.0) or 0.0) for d in pos_deals)
            total_swap = sum(float(getattr(d, "swap", 0.0) or 0.0) for d in pos_deals)
            total_fee = sum(float(getattr(d, "fee", 0.0) or 0.0) for d in pos_deals)
            
            # Tổng phí giao dịch của lệnh
            total_fees = round(abs(total_comm) + abs(total_fee) + (abs(total_swap) if total_swap < 0 else 0.0), 2)
            # Lợi nhuận ròng thực nhận/mất vào tài khoản
            net_profit = round(gross_profit + total_comm + total_swap + total_fee, 2)

            payload = {
                "login": str(login_num),
                "server": server_name,
                "ticket": str(deal.ticket),
                "deal_id": str(deal.ticket),
                "type": trade_type,
                "symbol": deal.symbol,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "profit": float(gross_profit),
                "commission": float(total_comm),
                "swap": float(total_swap),
                "fees": float(total_fees),
                "net_profit": float(net_profit),
                "volume": float(deal.volume),
                "balance": float(current_balance),
                "equity": float(current_equity),
                "close_time": close_time,
                "open_time": open_time
            }

            try:
                res = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                pnl_str = f"+${net_profit:.2f}" if net_profit >= 0 else f"-${abs(net_profit):.2f}"
                fee_info = f" (Phí: -${total_fees:.2f})" if total_fees > 0 else ""
                if res.status_code == 201:
                    print(f"    [+] THÊM MỚI: {deal.symbol} {trade_type} | Net PnL: {pnl_str}{fee_info} | Vé #{deal.ticket} lúc {close_time}")
                    acc_new += 1
                elif res.status_code == 200:
                    try:
                        resp_json = res.json()
                    except Exception:
                        resp_json = {}
                    if resp_json.get("status") == "updated":
                        print(f"    [✔] CẬP NHẬT: {deal.symbol} {trade_type} | Net PnL: {pnl_str}{fee_info} | Vé #{deal.ticket}")
                    acc_skipped += 1
                else:
                    print(f"    [!] Máy chủ phản hồi mã {res.status_code} cho vé #{deal.ticket}")
            except Exception as ex:
                print(f"    [!] Lỗi gửi vé #{deal.ticket}: {ex}")

    mt5.shutdown()

    print("\n" + "=" * 65)
    print("                    TỔNG KẾT ĐỒNG BỘ MT5")
    print("=" * 65)
    print(f"  [✔] Lệnh mới được nạp vào sổ nhật ký : {acc_new} lệnh")
    print(f"  [✔] Lệnh cũ đã có sẵn (chống trùng lặp): {acc_skipped} lệnh")
    print(f"  [✔] Cập nhật số dư Balance & Equity   : ${current_balance:,.2f} {currency}")
    print("=" * 65)
    print(">>> ĐỒNG BỘ THÀNH CÔNG! Bạn có thể mở web để xem thống kê mới nhất.")
    print("    Link Website: https://crypto-journal-twhs.onrender.com/\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[!] Lỗi xảy ra: {e}")
    finally:
        input("Nhấn Enter để thoát...")
