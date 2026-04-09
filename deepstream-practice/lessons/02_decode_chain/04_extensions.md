# Lesson 02 Extensions

## Cơ bản

1. Bỏ `h264parse` và chạy lại.
   - Quan sát: decoder báo lỗi gì, hoặc pipeline hỏng theo cách nào?
2. Đổi `fakesink` thành sink hiển thị.
   - Quan sát: bạn có nhìn thấy kết quả decode không?
3. In thêm tên từng element trước khi link.
   - Quan sát: mỗi cặp link đang nối 2 đầu nào?

## Nâng hơn nhưng vẫn trong boundary lesson

1. Gắn probe vào `decoder.src`.
   - Quan sát: dữ liệu sau decoder còn là H264 elementary stream nữa không?
2. Thử với input không phải H264 elementary stream.
   - Quan sát: lỗi bắt đầu xuất hiện ở parser, decoder, hay sớm hơn?
3. In caps ở `decoder.src` nếu bạn muốn tự kiểm chứng mental model của bài này.
