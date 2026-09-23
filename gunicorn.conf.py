import os

# Tự động lấy biến PORT từ Render (mặc định 10000 trên Render)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

workers = 2
threads = 2
timeout = 120
accesslog = "-"
errorlog = "-"
