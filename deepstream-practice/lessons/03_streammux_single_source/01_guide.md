# Lesson 03: Single-Source Streammux

Nếu bạn chưa quen syntax Python/GStreamer, đọc thêm `02_coding_guide.md` của lesson
này trước khi mở `03_starter.py`.

## What You Will Build

- Pipeline: `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> fakesink`
- Input: một file H264 elementary stream
- Expected outcome: tự nối được `decoder.src` vào request pad `sink_0` của
  `nvstreammux`, sau đó cho muxer đẩy batched buffer xuống sink

## Why It Matters

Đây là bài học bản lề giữa GStreamer nền tảng và DeepStream "thật sự". Rất nhiều
người mới học hay hỏi: "Chỉ có 1 source thì cần gì `nvstreammux`?" Câu trả lời là:

- Trong DeepStream, `nvstreammux` la diem vao chuan cua nhieu plugin phia sau.
- No tao ra batched buffer, ke ca khi `batch-size=1`.
- No day ban vao mot kieu suy nghi moi: khong chi link element, ma con phai hieu
  request pad va config batching.

## Mental Model

### Trước `nvstreammux`

- Sau `nvv4l2decoder`, bạn đang có frame video đã giải mã.
- `decoder` co `src` static pad co the lay bang `get_static_pad("src")`.

### Tại `nvstreammux`

- `nvstreammux` là request-pad-based element.
- Bạn không link thẳng bằng `decoder.link(streammux)` được.
- Bạn phải xin một sink pad cụ thể, ví dụ `sink_0`, rồi mới `srcpad.link(sinkpad)`.

### Sau `nvstreammux`

- Dữ liệu được đóng gói theo kiểu batch.
- Khi `batch-size=1`, nó vẫn là batched buffer 1 frame.
- `width`, `height`, `batched-push-timeout` ảnh hưởng trực tiếp đến output của muxer.

## Implementation Checklist

1. Parse input và kiểm tra file tồn tại.
2. `Gst.init(None)`.
3. Tao `filesrc`, `h264parse`, `nvv4l2decoder`, `nvstreammux`, `fakesink`.
4. Set property:
   - `source.location`
   - `streammux.batch-size = 1`
   - `streammux.width`, `streammux.height`
   - `streammux.batched-push-timeout`
   - `sink.sync = False`
5. Add tất cả element vào pipeline.
6. Link static chain: `filesrc -> h264parse -> nvv4l2decoder`.
7. Xin request pad: `streammux.request_pad_simple("sink_0")`.
8. Lay `decoder.get_static_pad("src")`.
9. Link `decoder.src -> streammux.sink_0`.
10. Link `streammux -> fakesink`.
11. Tạo bus watch, `GLib.MainLoop()`, chờ pipeline `PLAYING`.
12. Cleanup về `NULL`.

## Common Failure Modes

- Quên request pad:
  `nvstreammux` không có một sink pad cố định duy nhất cho bạn link tự động.
- Dùng sai tên pad, ví dụ `sink0` thay vì `sink_0`:
  request pad sẽ thất bại.
- Chưa lấy được `decoder.src` static pad:
  có thể element chưa tạo đúng hoặc gọi sai tên pad.
- Hiểu nhầm `batch-size=1` là "không cần mux":
  trong DeepStream, mux vẫn là entry point quan trọng của phần sau.

## Self-Check

1. Tại sao `nvstreammux` dùng request pad thay vì chỉ có 1 sink pad cố định?
2. `decoder.get_static_pad("src")` và `streammux.request_pad_simple("sink_0")`
   khác nhau ở điểm nào?
3. Vì sao DeepStream vẫn cần mux dù chỉ có 1 source?
4. `width`, `height`, `batched-push-timeout` đang tác động lên output theo ý nghĩa
   khái niệm nào?

## Extensions

- Thử đổi `batch-size` thành 2 và ghi lại bạn nghĩ muxer sẽ chờ điều gì khi chỉ có 1 source.
- Thêm source thứ hai và request thêm `sink_1`.
- Thử đổi `width`/`height` và quan sát output của muxer thay đổi theo cách nào.
- Vẽ lại pipeline bằng tay, nhấn mạnh đoạn request pad và đoạn static pad.
