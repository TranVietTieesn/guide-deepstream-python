# Lesson 03 Extensions

## Cơ bản

1. Đổi `batch-size` thành 2 trong khi vẫn chỉ có 1 source.
   - Quan sát: bạn nghĩ muxer sẽ chờ điều gì, và log cho bạn dấu hiệu nào?
2. In ra `batch-size`, `width`, `height`, `batched-push-timeout` trước khi PLAYING.
   - Quan sát: bạn đã cấu hình muxer đúng theo ý định chưa?
3. Thử đổi `width` và `height`.
   - Quan sát: muxer đang chuẩn bị output frame size theo cách nào?

## Nâng hơn nhưng vẫn trong boundary lesson

1. Thêm source thứ hai và request thêm `sink_1`.
   - Quan sát: workflow request pad thay đổi như thế nào khi số source tăng lên?
2. Cố ý request sai tên pad.
   - Quan sát: lỗi xuất hiện ở lúc nào, và bài học ở đây là gì?
3. Giải thích bằng lời của bạn vì sao `nvstreammux` vẫn cần mặt trong bài 1 source,
   thay vì trả lời theo kiểu "sample của NVIDIA viết thế".
