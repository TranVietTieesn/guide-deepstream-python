# Coding Guide Template

Dùng file này để dạy người học "code bài này như thế nào" theo trình tự thực hành.

## Before You Code

- File này nhận input gì?
- Chạy bằng lệnh nào?
- Cần import gì và import đó dùng để làm gì?

## Build Order

1. Viết callback và helper nào trước?
2. Trong `main(args)`, parse input thế nào?
3. Tạo pipeline/element ở đâu?
4. Set property ở đâu?
5. Add/link ở đâu?
6. Bus/main loop/state transition ở đâu?

## Function-By-Function Walkthrough

### `on_message(...)`

- Hàm này được gọi khi nào?
- Tham số nào quan trọng trong lesson này?
- Bạn cần xử lý những `MessageType` nào?

### `main(args)`

- `args` đến từ đâu?
- Thứ tự viết từng block là gì?
- Sau mỗi block, bạn nên kiểm tra điều gì?

### Helper functions

- Nếu có `make_element(...)`, giải thích vì sao nên tách ra.
- Nếu có helper pad/probe, giải thích nó trả về gì và được gọi ở đâu.

## Syntax Notes

- Hàm nào trả về element?
- Hàm nào trả về pad?
- Hàm nào trả về bool?
- Hàm nào không trả về giá trị bạn cần dùng tiếp?

## Starter Mapping

- `TODO 1`:
- `TODO 2`:
- `TODO 3`:

Mặc định, hãy map trực tiếp sang `03_starter.py`.

## Mini Checkpoints

- Sau block tạo element, bạn phải có gì trong tay?
- Sau block link, pipeline đã nối xong đến đâu?
- Sau block bus/main loop, app đã sẵn sàng `PLAYING` chưa?
