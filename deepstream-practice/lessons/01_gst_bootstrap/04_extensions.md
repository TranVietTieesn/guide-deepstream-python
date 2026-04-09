# Lesson 01 Extensions

## Cơ bản

1. In ra tên từng element trong pipeline bằng `pipeline.iterate_elements()`.
  - Quan sát: pipeline của bạn đang chứa chính xác những element nào?
2. Log state transition của pipeline.
  - Quan sát: có nhìn thấy `NULL -> READY -> PAUSED -> PLAYING` không?
3. Đổi `fakesink` thành `filesink`.
  - Quan sát: byte có được ghi ra file không, và điều đó nói gì về vai trò của
   `filesrc` trong bài này?

## Nâng hơn nhưng vẫn trong boundary lesson

1. Bỏ bus watch và chạy lại.
  - Quan sát: app còn nhận `EOS`/`ERROR` theo callback nữa không?
  - Kết luận: `GLib.MainLoop()` và bus watch đang phối hợp như thế nào?
2. Cố ý truyền một đường dẫn không tồn tại.
  - Quan sát: lỗi xuất hiện ở đâu, và `ERROR` message cho bạn biết gì?
3. Đổi tên pipeline và in tên `message.src` khi có `STATE_CHANGED`.
  - Quan sát: không chỉ pipeline, các element bên trong cũng có thể phát state
   message.

