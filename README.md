# NEO Robot – Hướng dẫn sử dụng

Tài liệu này dành cho phụ huynh, giáo viên hoặc người hỗ trợ cài đặt ứng dụng cho trẻ em sử dụng. Nội dung giải thích mục đích, cách mở ứng dụng và các thao tác cơ bản.

## Ứng dụng dùng để làm gì

NEO Robot là ứng dụng học lập trình qua terminal, nơi trẻ viết các lệnh Python đơn giản để điều khiển một cánh tay robot. Ứng dụng chạy trên Raspberry Pi và không cần giao diện desktop.

Trẻ sẽ gõ mã ở khung bên trái và xem kết quả ở khung bên phải. Ứng dụng có chế độ tương tác để thử từng dòng lệnh.

## Bắt đầu nhanh (khuyến nghị)

1. Cài Python 3.11+.
2. Cài ứng dụng (xem phần Cài đặt).
3. Lần đầu nên chạy chế độ mô phỏng.
4. Vào phần application, mở `Terminal Emulator` và chạy:

```bash
neo-robot --mock
```

Nếu đã kết nối robot thật và muốn điều khiển trực tiếp:

```bash
neo-robot
```

Nếu không tìm thấy phần cứng, ứng dụng tự chuyển sang chế độ mô phỏng.

## Cài đặt

Từ thư mục dự án:

```bash
pip install -e .
```

Nếu cần bộ công cụ phát triển (không bắt buộc):

```bash
pip install -e ".[dev]"
```

## Mở ứng dụng

Từ terminal:

```bash
neo-robot
```

Hoặc chạy bằng Python:

```bash
python -m neo_robot
```

Chạy chế độ mô phỏng (không cần robot):

```bash
neo-robot --mock
```

## Cách dùng cơ bản

Màn hình có hai chế độ:

- Chế độ kịch bản (mặc định): trình soạn mã bên trái, bảng điều khiển bên phải.
- Chế độ tương tác: REPL toàn màn hình để thử từng lệnh.

### Chế độ kịch bản (khuyến nghị cho trẻ)

1. Gõ mã ở khung bên trái.
2. Nhấn **F5** để chạy.
3. Kết quả hiển thị ở khung bên phải.

Ví dụ:

```python
arm.turn_right(90)
delay(1)
arm.grab()
arm.turn_left(90)
arm.release()
```

### Chế độ tương tác (thử từng dòng)

Nhấn **F2** để chuyển chế độ tương tác.
Gõ một lệnh rồi nhấn **Enter**.

Ví dụ:

```python
arm.turn_left(45)
```

## Phím tắt

- `F5` – Chạy mã (chế độ kịch bản)
- `F2` – Chuyển kịch bản / tương tác
- `Ctrl+X` – Dừng thực thi
- `Ctrl+L` – Xóa bảng điều khiển
- `Ctrl+E` – Xóa trình soạn mã
- `Ctrl+Q` – Thoát

## Các lệnh trẻ có thể dùng

Ứng dụng chạy trong môi trường an toàn. Trẻ có thể dùng các lệnh sau:

```python
arm.turn_left(angle)
arm.turn_right(angle)
arm.set_angle(angle)
arm.lift_up(angle)
arm.lower_down(angle)
arm.grab()
arm.release()
arm.delay(seconds)

delay(seconds)  # bí danh của arm.delay
print(...)      # in ra bảng điều khiển
```

Góc quay nằm trong khoảng 0 đến 180 độ.

## Lưu ý an toàn

- Không để tay gần robot khi đang chạy chương trình.
- Bắt đầu với góc nhỏ và chuyển động chậm.
- Nên thử ý tưởng mới trong chế độ mô phỏng trước.

## Khắc phục sự cố

- **“Không thể kết nối phần cứng”**: ứng dụng sẽ chuyển sang mô phỏng. Kiểm tra dây, nguồn rồi khởi động lại. Hãy chắc chắn kết nối robot trước khi khởi động ứng dụng nếu muốn dùng chế độ phần cứng.
- **Không thấy robot chuyển động**: đảm bảo robot đã cấp nguồn và đúng chân kết nối.
- **Không mở được ứng dụng**: kiểm tra Python 3.11+ và cài lại phụ thuộc.

## Bản quyền

AGPL-3.0 (xem file LICENSE)
