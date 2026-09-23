"""
Script tạo đường link truy cập từ xa qua Cloudflare Tunnel
Cho phép điện thoại dùng 4G hoặc Wi-Fi ngoài quán cafe truy cập thẳng vào Web Journal trên máy tính
"""
import sys
import os
import time
import threading

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pycloudflared import try_cloudflare
from web_app import app

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    print("=" * 65)
    print("  ⚡ KHỞI ĐỘNG TRUY CẬP TỪ XA CHO ĐIỆN THOẠI (CLOUDFLARE TUNNEL)")
    print("=" * 65)
    print("\n[*] Đang khởi chạy máy chủ Web cục bộ...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    time.sleep(1.5)
    print("[*] Đang kết nối Cloudflare Tunnel để tạo link di động...")
    try:
        tunnel = try_cloudflare(port=5000, verbose=False)
        print("\n" + "=" * 65)
        print("  🎉 ĐƯỜNG LINK TRUY CẬP TRÊN ĐIỆN THOẠI (4G / KHÁC WI-FI):")
        print(f"  👉  {tunnel.tunnel}")
        print("=" * 65)
        print("\n[*] Bạn chỉ cần copy link trên và dán vào trình duyệt điện thoại là dùng được ngay!")
        print("[*] Giữ cửa sổ này mở trong khi sử dụng. Nhấn Ctrl + C để dừng.")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Đã dừng phiên làm việc.")
    except Exception as e:
        print(f"\n[!] Có lỗi xảy ra: {e}")
