# NGUYÊN TẮC BẢO TOÀN DỮ LIỆU GIAO DỊCH (DATA PERSISTENCE & INTEGRITY)

> **QUY TẮC BẮT BUỘC TỪ NGƯỜI DÙNG**:
> Tất cả các thông tin về lệnh được thêm vào ở Bảng Dashboard, Nhật Ký Lệnh và Lịch PnL **PHẢI ĐƯỢC GHI NHỚ VÀ GIỮ LẠI NGUYÊN VẸN** cho mỗi lần thay đổi hay sửa code, cập nhật tính năng hoặc triển khai lại hệ thống.

---

## 1. Không Bao Giờ Xóa Hoặc Ghi Đè Dữ Liệu Lệnh (Trades)
- Tuyệt đối **KHÔNG ĐƯỢC CHẠY** các lệnh `DROP TABLE`, `TRUNCATE`, hoặc `DELETE FROM trades` trừ khi người dùng chủ động yêu cầu xóa một lệnh cụ thể qua giao diện.
- Không được ghi đè file cơ sở dữ liệu `data/trading_journal.db` bằng file rỗng hoặc dữ liệu mẫu khi cập nhật code hay commit Git.
- Dữ liệu lệnh của người dùng thực tế phải luôn được bảo toàn 100%.

## 2. Nâng Cấp Schema Không Gây Mất Dữ Liệu (Non-Destructive Migrations)
- Mọi thay đổi bảng cơ sở dữ liệu phải được thực hiện bằng cơ chế kiểm tra và bổ sung cột an toàn:
  ```python
  cursor.execute("PRAGMA table_info(trades)")
  columns = [col[1] for col in cursor.fetchall()]
  if "new_column" not in columns:
      cursor.execute("ALTER TABLE trades ADD COLUMN new_column ...")
  ```
- Không tạo lại bảng mới làm mất các bản ghi hiện có.

## 3. Bảo Toàn Dữ Liệu Cài Đặt Người Dùng
- Số vốn ban đầu (`initial_capital`), vốn hiện tại, thông tin tài khoản và cấu hình cá nhân phải luôn được duy trì xuyên suốt các bản cập nhật.
- Token xác thực và phiên đăng nhập trên thiết bị (`localStorage` / `session`) phải được duy trì để người dùng không bị mất đăng nhập sau khi đóng trình duyệt.

## 4. Kiểm Tra Trước Khi Triển Khai
- Trước mỗi lần commit và deploy lên Render/Production, phải kiểm tra chắc chắn rằng cơ sở dữ liệu đang có không bị reset, bộ đếm lệnh không bị lỗi và mọi lệnh trước đó của người dùng vẫn hiển thị đầy đủ trên Dashboard, Nhật Ký và Lịch PnL.
