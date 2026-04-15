# Lesson 01: GStreamer Bootstrap

Nếu bạn chưa quen syntax Python/GStreamer, đọc thêm `02_coding_guide.md` của lesson
này trước khi mở `03_starter.py`.

## What You Will Build

- Pipeline: `filesrc -> fakesink`
- Input: một file bất kỳ tồn tại trên máy của bạn
- Expected outcome: một app GStreamer tối thiểu có thể tạo pipeline, nhận bus
message, chạy `GLib.MainLoop()`, vào `PLAYING`, nhận `EOS`, và cleanup về `NULL`

## Why It Matters

DeepStream không phải một thế giới tách riêng khỏi GStreamer. Trước khi học
`nvstreammux`, `nvinfer`, metadata hay overlay, bạn cần nắm bộ khung tối thiểu của
một app GStreamer:

- `Gst.init(None)` để khởi tạo framework
- `Gst.Pipeline` để giữ graph các element
- bus message để nhận `EOS`, `ERROR`, `STATE_CHANGED`
- `GLib.MainLoop()` để app tiếp tục xử lý sự kiện
- `set_state(...)` để điều khiển lifecycle của pipeline

Nếu bài này rõ, các bài sau sẽ chỉ là "thêm plugin mới vào bộ khung cũ", thay vì
cảm giác như có phép màu.

## Mental Model

### Data plane

- `filesrc` chỉ đọc byte từ file trên đĩa.
- `fakesink` nhận dữ liệu rồi bỏ đi.
- Ở bài này, pipeline chưa "hiểu video" và chưa decode gì cả.

### Control plane

- Pipeline gửi message lên bus để thông báo `EOS`, `ERROR`, `STATE_CHANGED`.
- Theo GStreamer docs, bus watch kiểu callback chỉ thực sự có ý nghĩa khi có
`GLib.MainLoop()` đang chạy.
- `MainLoop` không chạy data plane thay bạn; nó giúp app tiếp tục xử lý event và
callback trong lúc pipeline đang hoạt động.

### Lifecycle

1. Khởi tạo GStreamer.
2. Tạo pipeline và element.
3. Add và link.
4. Đăng ký bus callback.
5. Chuyển sang `PLAYING`.
6. Chờ đến khi nhận `EOS` hoặc `ERROR`.
7. Đưa pipeline về `NULL`.

## Implementation Checklist

1. Parse `sys.argv` và kiểm tra file input có tồn tại.
2. Gọi `Gst.init(None)`.
3. Tạo `pipeline`, `filesrc`, `fakesink`.
4. Set `location` cho `filesrc`.
5. `pipeline.add(source)` và `pipeline.add(sink)`.
6. `source.link(sink)`.
7. Tạo `GLib.MainLoop()`.
8. Lấy `bus`, gọi `bus.add_signal_watch()`, rồi `bus.connect("message", ...)`.
9. Trong callback:
  - `EOS` thì in log và `loop.quit()`
  - `ERROR` thì parse lỗi, in debug string nếu có, rồi `loop.quit()`
  - `STATE_CHANGED` thì chỉ theo dõi pipeline chính
10. `pipeline.set_state(Gst.State.PLAYING)`.
11. Trong `finally`, gọi `pipeline.set_state(Gst.State.NULL)`.

## Common Failure Modes

- Nhập sai đường dẫn file:
`filesrc` không đọc được gì, pipeline sẽ dừng với lỗi.
- `Gst.ElementFactory.make(...)` trả về `None`:
thường là plugin không tồn tại hoặc môi trường GStreamer chưa sẵn sàng.
- Quên `bus.add_signal_watch()` hoặc không chạy `GLib.MainLoop()`:
app sẽ khó quan sát `EOS`/`ERROR` theo kiểu callback.
- Hiểu nhầm `filesrc` là "source video":
thực ra nó chỉ đọc byte. Việc "hiểu đây là H264 hay raw frame" thuộc bài sau.

## Self-Check

1. Tại sao bài này vẫn cần `GLib.MainLoop()` dù pipeline rất nhỏ?
2. Tại sao `pipeline.set_state(Gst.State.NULL)` là một bước cleanup, không chỉ là
  "tắt đi cho xong"?
3. Khác nhau giữa data đi trong pipeline và message đi trên bus là gì?
4. Nếu bỏ phần xử lý `ERROR`, bạn sẽ gặp khó khăn gì khi học bài sau?

## Extensions

- Thêm đoạn in tên từng element bằng `pipeline.iterate_elements()`.
- Thêm log state transition của pipeline và ghi lại chuỗi `NULL -> READY -> PAUSED -> PLAYING`.
- Thử bỏ bus watch và quan sát xem app còn nhận `EOS`/`ERROR` theo kiểu callback
nữa không.
- Đổi `fakesink` thành `filesink` hoặc một sink khác để cảm nhận rõ hơn luồng dữ
liệu đang đi qua pipeline.

