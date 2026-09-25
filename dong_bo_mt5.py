# -*- coding: utf-8 -*-
"""
TRADING JOURNAL - HỆ THỐNG ĐỒNG BỘ MT5 ĐA TÀI KHOẢN (MULTI-ACCOUNT SYNC)
- Tự động nhận diện tài khoản MT5 đang hoạt động trên máy tính.
- Tự động đối soát và khớp với đúng tài khoản Web của từng người dùng riêng biệt.
- Chế độ 1-Chạm (Sync 1 lần) hoặc Chế độ Tự Động Liên Tục (Live Auto-Sync).
- Tự động chuyển đổi người dùng khi phát hiện đổi tài khoản trong MT5.
- Hoàn toàn chống trùng lặp, bảo toàn 100% dữ liệu lịch sử.
"""
import sys
import os
import time
import json
import traceback
from datetime import datetime, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import requests
except ImportError:
    print("[*] Đang cài đặt thư viện 'requests'...", flush=True)
    os.system("pip install requests -q")
    import requests

try:
    import MetaTrader5 as mt5
except ImportError:
    print("[*] Đang cài đặt thư viện 'MetaTrader5'...", flush=True)
    os.system("pip install MetaTrader5 -q")
    import MetaTrader5 as mt5

BASE_SERVER_URL = "https://crypto-journal-twhs.onrender.com"
CHECK_ACCOUNT_URL = f"{BASE_SERVER_URL}/api/mt5/check_account"
WEBHOOK_URL = f"{BASE_SERVER_URL}/api/mt5/webhook"


def verify_web_link(login_num: int, server_name: str):
    """
    Kiểm tra xem số tài khoản MT5 này đã được liên kết với nick Web nào chưa.
    """
    try:
        res = requests.post(CHECK_ACCOUNT_URL, json={
            "login": str(login_num),
            "server": server_name
        }, timeout=12)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 404:
            return {"status": "not_found", "message": res.json().get("message", "Chưa liên kết")}
        else:
            return {"status": "error", "message": f"Mã phản hồi HTTP {res.status_code}"}
    except Exception as ex:
        return {"status": "error", "message": f"Lỗi kết nối máy chủ: {ex}"}


def sync_account_trades(acc_info, web_info, days_back=90):
    """
    Thực hiện quét và đồng bộ các lệnh đóng từ MT5 lên Web.
    """
    login_num = acc_info.login
    server_name = acc_info.server
    current_balance = acc_info.balance
    current_equity = acc_info.equity
    currency = acc_info.currency or "USD"
    username = web_info.get("username", "Người dùng")
    account_label = web_info.get("account_name", "Tài khoản MT5")

    print(f"\n[*] Đang quét lịch sử lệnh đóng trong {days_back} ngày qua của #{login_num}...", flush=True)
    from_date = datetime.now() - timedelta(days=days_back)
    to_date = datetime.now() + timedelta(days=1)

    deals = mt5.history_deals_get(from_date, to_date)
    if deals is None or len(deals) == 0:
        print(f"[i] Không tìm thấy lệnh nào trong {days_back} ngày qua trên MT5.", flush=True)
        return 0, 0

    acc_new = 0
    acc_skipped = 0
    closed_deals = [d for d in deals if d.entry in (mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_INOUT) and d.symbol]
    print(f"[*] Tìm thấy {len(closed_deals)} lệnh đã đóng, đang đồng bộ vào tài khoản Web: '{username}'...", flush=True)

    for deal in closed_deals:
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

        # Tổng hợp toàn bộ Phí hoa hồng (Commission), Phí qua đêm (Swap) và Phí sàn (Fee) của toàn bộ vị thế
        gross_profit = float(deal.profit)
        total_comm = sum(float(getattr(d, "commission", 0.0) or 0.0) for d in pos_deals)
        total_swap = sum(float(getattr(d, "swap", 0.0) or 0.0) for d in pos_deals)
        total_fee = sum(float(getattr(d, "fee", 0.0) or 0.0) for d in pos_deals)
        
        total_fees = round(abs(total_comm) + abs(total_fee) + (abs(total_swap) if total_swap < 0 else 0.0), 2)
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
            res = requests.post(WEBHOOK_URL, json=payload, timeout=12)
            pnl_str = f"+${net_profit:.2f}" if net_profit >= 0 else f"-${abs(net_profit):.2f}"
            fee_info = f" (Phí: -${total_fees:.2f})" if total_fees > 0 else ""
            if res.status_code == 201:
                print(f"    [+] THÊM MỚI -> [{username}]: {deal.symbol} {trade_type} | Net: {pnl_str}{fee_info} | Vé #{deal.ticket}", flush=True)
                acc_new += 1
            elif res.status_code == 200:
                resp_json = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
                if resp_json.get("status") == "updated":
                    print(f"    [✔] CẬP NHẬT -> [{username}]: {deal.symbol} {trade_type} | Net: {pnl_str}{fee_info} | Vé #{deal.ticket}", flush=True)
                acc_skipped += 1
            elif res.status_code == 404:
                err_msg = res.json().get("error", "Tài khoản chưa được liên kết!")
                print(f"    [!] Lỗi: {err_msg}", flush=True)
                return acc_new, acc_skipped
            else:
                print(f"    [!] Máy chủ phản hồi mã {res.status_code} cho vé #{deal.ticket}", flush=True)
        except Exception as ex:
            print(f"    [!] Lỗi gửi vé #{deal.ticket}: {ex}", flush=True)

    return acc_new, acc_skipped


def print_unlinked_warning(acc_info):
    """In cảnh báo và hướng dẫn cụ thể khi tài khoản MT5 chưa được liên kết trên Web."""
    login_num = acc_info.login
    server_name = acc_info.server
    acc_name = acc_info.name or "Trader"
    print("\n" + "=" * 65, flush=True)
    print(" [!] CẢNH BÁO: TÀI KHOẢN MT5 CHƯA ĐƯỢC LIÊN KẾT TRÊN WEB!", flush=True)
    print("=" * 65, flush=True)
    print(f"  * Tài khoản MT5 đang mở : #{login_num}", flush=True)
    print(f"  * Server MT5            : {server_name}", flush=True)
    print(f"  * Chủ tài khoản         : {acc_name}", flush=True)
    print("\n  LÝ DO: Hệ thống Web chưa biết tài khoản MT5 này thuộc về", flush=True)
    print("  người dùng nào (ví dụ: 'sinh123456' hay 'phattruong2128').", flush=True)
    print("\n  HƯỚNG DẪN LIÊN KẾT (Chỉ cần làm 1 lần):", flush=True)
    print("  1. Truy cập Website: https://crypto-journal-twhs.onrender.com/", flush=True)
    print("  2. Đăng nhập vào đúng tài khoản Web của bạn.", flush=True)
    print("  3. Bấm vào nút 'Quản Lý Tài Khoản MT5' -> Chọn 'Thêm Tài Khoản Mới':", flush=True)
    print("     - Tên gợi nhớ : (Ví dụ 'The5ers' hoặc 'Tài khoản Sinh')", flush=True)
    print(f"     - Server      : {server_name}", flush=True)
    print(f"     - Số login    : {login_num}", flush=True)
    print("  4. Bấm 'Lưu Tài Khoản'. Sau đó mở lại file này để đồng bộ!", flush=True)
    print("=" * 65 + "\n", flush=True)


def main():
    print("=" * 65, flush=True)
    print("       TRADING JOURNAL - HỆ THỐNG ĐỒNG BỘ MT5 ĐA TÀI KHOẢN", flush=True)
    print("=" * 65, flush=True)

    # 1. Khởi tạo kết nối MT5
    if not mt5.initialize():
        print("\n[-] Không thể kết nối với phần mềm MetaTrader 5 trên máy tính!", flush=True)
        print("    Vui lòng kiểm tra:", flush=True)
        print("    1. Phần mềm MetaTrader 5 (MT5) đã được mở và đã đăng nhập tài khoản.", flush=True)
        print("    2. Biểu tượng kết nối mạng góc dưới bên phải MT5 đã có vạch sóng xanh.", flush=True)
        print(f"    Mã lỗi MT5: {mt5.last_error()}\n", flush=True)
        return

    # 2. Lấy thông tin tài khoản MT5 đang active
    acc_info = mt5.account_info()
    if not acc_info:
        print("\n[-] Không lấy được thông tin tài khoản MT5. Vui lòng đăng nhập vào MT5 trước.", flush=True)
        mt5.shutdown()
        return

    login_num = acc_info.login
    server_name = acc_info.server
    current_balance = acc_info.balance
    currency = acc_info.currency or "USD"

    print(f"\n[+] Đã kết nối phần mềm MT5:", flush=True)
    print(f"    - Số tài khoản : #{login_num}", flush=True)
    print(f"    - Server       : {server_name}", flush=True)
    print(f"    - Tên MT5      : {acc_info.name}", flush=True)
    print(f"    - Số dư        : ${current_balance:,.2f} {currency}", flush=True)

    # 3. Kiểm tra xem tài khoản này thuộc về user Web nào
    print(f"[*] Đang xác thực liên kết với Web Journal...", flush=True)
    web_check = verify_web_link(login_num, server_name)
    if web_check.get("status") != "ok":
        print_unlinked_warning(acc_info)
        mt5.shutdown()
        return

    target_user = web_check.get("username", "Người dùng")
    account_label = web_check.get("account_name", "Tài khoản MT5")
    print(f"[✔] LIÊN KẾT HỢP LỆ!", flush=True)
    print(f"    -> Tài khoản Web nhận lệnh: '{target_user}' (Hồ sơ: {account_label})\n", flush=True)

    # 4. Cho người dùng chọn chế độ: Sync 1 lần hoặc Chạy Tự Động Liên Tục
    print("-" * 65, flush=True)
    print("CHỌN CHẾ ĐỘ HOẠT ĐỘNG:", flush=True)
    print("  [1] Đồng bộ 1 lần rồi kết thúc (Mặc định - Nhấn Enter)")
    print("  [2] Tự động đồng bộ liên tục (Live Auto-Sync: quét mỗi 15 giây,")
    print("      tự động phát hiện khi bạn chuyển sang tài khoản MT5 khác)")
    print("-" * 65, flush=True)
    
    choice = input("Lựa chọn của bạn [1 hoặc 2, Enter = 1]: ").strip()
    is_continuous = (choice == "2")

    if not is_continuous:
        # Chế độ 1 lần
        new_cnt, skip_cnt = sync_account_trades(acc_info, web_check)
        mt5.shutdown()
        print("\n" + "=" * 65, flush=True)
        print("                    TỔNG KẾT ĐỒNG BỘ MT5", flush=True)
        print("=" * 65, flush=True)
        print(f"  [✔] Đã đồng bộ vào nick Web : {target_user}", flush=True)
        print(f"  [✔] Lệnh mới được nạp vào sổ: {new_cnt} lệnh", flush=True)
        print(f"  [✔] Lệnh đã có sẵn (đối soát): {skip_cnt} lệnh", flush=True)
        print(f"  [✔] Cập nhật số dư Balance  : ${acc_info.balance:,.2f} {currency}", flush=True)
        print("=" * 65, flush=True)
        print(">>> ĐỒNG BỘ HOÀN TẤT! Bạn có thể vào Web để xem nhật ký.")
        print(f"    Link Website: {BASE_SERVER_URL}\n", flush=True)
    else:
        # Chế độ Tự Động Liên Tục
        print("\n" + "=" * 65, flush=True)
        print("   ĐÃ BẬT CHẾ ĐỘ TỰ ĐỘNG ĐỒNG BỘ LIÊN TỤC (LIVE AUTO-SYNC)", flush=True)
        print("   * Tool sẽ kiểm tra lệnh mới mỗi 15 giây.", flush=True)
        print("   * Khi bạn đổi tài khoản trong MT5, tool sẽ tự động nhận diện", flush=True)
        print("     và chuyển sang nạp vào nick Web tương ứng!", flush=True)
        print("   * Nhấn Ctrl + C để dừng bất cứ lúc nào.", flush=True)
        print("=" * 65 + "\n", flush=True)

        current_active_login = login_num
        current_web_user = target_user

        # Lần đồng bộ đầu tiên
        sync_account_trades(acc_info, web_check)

        try:
            while True:
                time.sleep(15)
                # Kiểm tra kết nối MT5
                latest_acc = mt5.account_info()
                if not latest_acc:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [!] Không kết nối được MT5, đang thử lại...", flush=True)
                    continue

                # Phát hiện nếu người dùng đổi tài khoản trong MT5
                if latest_acc.login != current_active_login:
                    print(f"\n[🔄] PHÁT HIỆN ĐỔI TÀI KHOẢN MT5!", flush=True)
                    print(f"    Từ #{current_active_login} -> #{latest_acc.login} ({latest_acc.server})", flush=True)
                    
                    check = verify_web_link(latest_acc.login, latest_acc.server)
                    if check.get("status") != "ok":
                        print_unlinked_warning(latest_acc)
                        current_active_login = latest_acc.login
                        continue

                    current_active_login = latest_acc.login
                    web_check = check
                    current_web_user = check.get("username", "Người dùng")
                    print(f"[✔] ĐÃ CHUYỂN SANG NICK WEB: '{current_web_user}' (Hồ sơ: {check.get('account_name')})\n", flush=True)
                    sync_account_trades(latest_acc, web_check)
                else:
                    # Cùng tài khoản, quét lệnh đóng mới trong 2 ngày gần nhất
                    sync_account_trades(latest_acc, web_check, days_back=2)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Đang giám sát lệnh cho '{current_web_user}' (#{current_active_login})...", flush=True)

        except KeyboardInterrupt:
            print("\n[*] Đã dừng chế độ tự động.", flush=True)
        finally:
            mt5.shutdown()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n" + "!" * 65, flush=True)
        print(f"[-] ĐÃ XẢY RA LỖI: {e}", flush=True)
        traceback.print_exc()
        print("!" * 65, flush=True)
    finally:
        input("\nNhấn Enter để thoát...")
