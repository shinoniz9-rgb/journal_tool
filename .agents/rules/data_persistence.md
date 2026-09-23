# Quy Tắc Bảo Toàn Dữ Liệu Lệnh Giao Dịch

## Yêu Cầu Cốt Lõi Của Dự Án
Tất cả các thông tin về lệnh được thêm vào sau này ở bảng Dashboard, Nhật Ký Lệnh và Lịch PnL phải được ghi nhớ và giữ lại nguyên vẹn cho mỗi lần thay đổi hay sửa code.

## Chỉ Thị Dành Cho AI & Lập Trình Viên:
1. **Dữ liệu lệnh trong DB**: Tuyệt đối không xóa bảng `trades`, không xóa các bản ghi hiện có, không ghi đè cơ sở dữ liệu `data/trading_journal.db` khi commit hoặc build.
2. **Migrations**: Luôn dùng `ALTER TABLE ADD COLUMN` sau khi kiểm tra cột tồn tại, tuyệt đối không dùng `DROP TABLE` hoặc tạo mới ghi đè.
3. **Bộ đếm tự tăng (ID)**: Chỉ reset `sqlite_sequence` khi và chỉ khi bảng lệnh thực sự có 0 bản ghi. Khi đã có lệnh của người dùng, không can thiệp ID của họ.
4. **Trạng thái tài khoản & số vốn**: Số vốn thiết lập (`initial_capital`) và phiên làm việc phải được bảo toàn vĩnh viễn trên thiết bị của người dùng.
