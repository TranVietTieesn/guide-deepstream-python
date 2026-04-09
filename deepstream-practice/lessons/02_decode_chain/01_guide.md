# Lesson 02: Decode Chain

Nếu bạn chưa quen syntax Python/GStreamer, đọc thêm `02_coding_guide.md` của lesson
này trước khi mở `03_starter.py`.

## What You Will Build

- Pipeline: `filesrc -> h264parse -> nvv4l2decoder -> fakesink`
- Input: một file H264 elementary stream, ví dụ `sample_1080p_h264.h264`
- Expected outcome: tự lập được chuỗi parser + decoder có thể chạy đến `EOS`

## Why It Matters

Trong pipeline DeepStream cổ điển, video không đi thẳng từ file vào `nvstreammux`.
Nó thường phải:

1. được đọc lên như một luồng byte
2. được parser chuẩn hóa
3. được decoder đổi thành frame video

Nếu bạn không nắm bài này, bạn rất dễ nhầm lẫn giữa:

- dữ liệu nén và dữ liệu đã decode
- parser và decoder
- "file video" và "dòng frame" trong pipeline

## Mental Model

### Trước parser

- `filesrc` chỉ đọc byte từ file.
- Nó không biết đây có phải H264 hợp lệ không.

### Sau parser

- `h264parse` không decode.
- Vai trò của nó là chuẩn hóa và tổ chức lại luồng H264 để decoder dễ tiêu thụ hơn.
- Theo GStreamer docs, parser thường nằm trước decoder để giúp bước giải mã nhận
  đúng format/cấu trúc dữ liệu.

### Sau decoder

- `nvv4l2decoder` biến elementary stream thành frame video đã giải mã.
- Ở mức khái niệm, đây là lúc dữ liệu bắt đầu giống "ảnh/video frame", không còn là
  luồng H264 nén nữa.
- Đây là mốc cực kỳ quan trọng trước khi học `nvstreammux`.

## Implementation Checklist

1. Parse argument và đảm bảo input là file H264 hợp lệ.
2. `Gst.init(None)`.
3. Tạo `pipeline`, `filesrc`, `h264parse`, `nvv4l2decoder`, `fakesink`.
4. Set `location` cho `filesrc`.
5. Nếu cần, set `sync=False` cho `fakesink`.
6. Add tất cả element vào pipeline.
7. Link từng cặp:
   - `filesrc -> h264parse`
   - `h264parse -> nvv4l2decoder`
   - `nvv4l2decoder -> fakesink`
8. Tạo bus watch và `GLib.MainLoop()`.
9. `PLAYING -> run loop -> NULL`.

## Common Failure Modes

- Truyền file MP4 thay vì H264 elementary stream:
  pipeline này không còn đúng nguyên xi.
- Bỏ `h264parse`:
  decoder có thể không ăn được luồng vào như mong đợi.
- `nvv4l2decoder` không tạo được:
  môi trường NVIDIA/DeepStream chưa sẵn sàng.
- Hiểu nhầm `fakesink` là "không có gì xảy ra":
  thực ra decode vẫn có thể đang diễn ra, chỉ là bạn không hiển thị frame.

## Self-Check

1. `filesrc` có hiểu "video H264" không hay chỉ đọc byte?
2. `h264parse` và `nvv4l2decoder` khác nhau ở vai trò nào?
3. Sau `nvv4l2decoder`, bạn mong caps sẽ nghiêng về kiểu dữ liệu nào?
4. Nếu đổi input sang codec khác, pipeline này hỏng ở đâu tiên?

## Extensions

- Bỏ `h264parse` và ghi lại lỗi hoặc hành vi pipeline.
- Gắn pad probe hoặc in caps ở `decoder.src` để tự xác nhận dữ liệu sau decode khác
  trước decode.
- Đổi `fakesink` thành một sink hiển thị nếu bạn muốn nhìn kết quả decode.
- Thử với một file khác để phân biệt "pipeline sai vì input sai" và "pipeline sai vì
  code sai".
