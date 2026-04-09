# Lesson 02 Coding Guide

File này dạy bạn cách viết `03_starter.py` theo từng block. Mục tiêu là sau khi đọc
xong, bạn biết cần gọi hàm nào, check lỗi ở đâu, và sau dòng này thường viết gì tiếp.

## Before You Code

Lệnh chạy:

```bash
python3 lessons/02_decode_chain/03_starter.py /path/to/sample_1080p_h264.h264
```

Input của bài này là file H264 elementary stream, không phải MP4 thông thường.

Imports giống lesson 01, nhưng từ lesson này bạn bắt đầu có thêm helper
`make_element(...)` để tránh lặp code.

## Build Order

1. Hoàn thành `on_message(...)`.
2. Hoàn thành helper `make_element(...)`.
3. Parse input và gọi `Gst.init(None)`.
4. Tạo pipeline và 4 element.
5. Set property cho `filesrc` và `fakesink`.
6. Add tất cả vào pipeline.
7. Link từng cặp theo thứ tự decode chain.
8. Đăng ký bus và `GLib.MainLoop()`.
9. `PLAYING -> loop.run() -> NULL`.

## Function-By-Function Walkthrough

### `on_message(bus, message, loop)`

Ở bài này bạn chỉ cần `EOS` và `ERROR`. Không bắt buộc phải thêm
`STATE_CHANGED` nữa vì bài học đang tập trung vào decode chain.

Mẫu viết:

```python
def on_message(bus, message, loop):
    _ = bus
    if message.type == Gst.MessageType.EOS:
        print("EOS: decode xong.")
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True
```

Việc đặt `_ = bus` là để nói rằng tham số này chưa được dùng trong lesson.

### `make_element(factory_name, name)`

Mẫu viết:

```python
def make_element(factory_name, name):
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Không tạo được element: {factory_name}")
    return element
```

Giải thích:

- `factory_name` là tên plugin factory, ví dụ `filesrc`, `h264parse`.
- `name` là tên instance trong pipeline.
- Helper này giúp bạn không phải lặp lại block check `if not element`.
- `return element` để bạn dùng lại object vừa tạo.

### `main(args)` phần tạo element

Sau `Gst.init(None)`, hãy viết:

```python
pipeline = Gst.Pipeline.new("lesson-02-pipeline")
source = make_element("filesrc", "file-source")
parser = make_element("h264parse", "h264-parser")
decoder = make_element("nvv4l2decoder", "hw-decoder")
sink = make_element("fakesink", "fake-sink")
```

Giải thích:

- `make_element(...)` đã gồm sẵn logic check lỗi.
- `pipeline` vẫn được tạo riêng vì nó không phải element factory thông thường.

### Set property

Hãy viết:

```python
source.set_property("location", input_path)
sink.set_property("sync", False)
```

Giải thích:

- `location` chỉ cho `filesrc` file nào cần đọc.
- `sync=False` với `fakesink` thường được dùng để sink không cố gắng đồng bộ với
  clock hiển thị. Ở bài học phân tích pipeline, điều này giúp sink "dễ tính" hơn.

### Add element vào pipeline

Mẫu viết:

```python
for element in (source, parser, decoder, sink):
    pipeline.add(element)
```

Giải thích:

- Python cho phép loop qua tuple để giảm lặp code.
- Sau block này, tất cả element đã nằm trong pipeline.

### Link từng bước

Mẫu viết:

```python
if not source.link(parser):
    raise RuntimeError("Không link được filesrc -> h264parse")
if not parser.link(decoder):
    raise RuntimeError("Không link được h264parse -> nvv4l2decoder")
if not decoder.link(sink):
    raise RuntimeError("Không link được nvv4l2decoder -> fakesink")
```

Giải thích:

- `link(...)` trả về bool.
- Ở bài này, link bằng element-level API là đủ vì các pad cần dùng đều là static
  và có thể nối trực tiếp.
- Thứ tự link cũng là thứ tự dữ liệu chạy trong pipeline.

## Starter Mapping

### TODO 1: Hoàn thành `on_message(...)`

- Giải quyết `EOS`
- Giải quyết `ERROR`
- `return True`

### TODO 2: Hoàn thành `make_element(...)`

- Tạo bằng `Gst.ElementFactory.make(...)`
- Check lỗi ngay
- `return element`

### TODO 3: Tạo 4 element cần thiết

- `filesrc`
- `h264parse`
- `nvv4l2decoder`
- `fakesink`

### TODO 4: Set property

- `source.location = input_path`
- `sink.sync = False`

### TODO 5: Add element vào pipeline

- Có thể dùng `for element in (...)`

### TODO 6: Link decode chain

- `filesrc -> parser -> decoder -> sink`

## Syntax Notes

- `raise RuntimeError(...)` là cách dùng để dừng ngay khi có lỗi logic/tạo element.
- `for element in (...)` là cách viết Python gọn để làm lặp lại cùng một thao tác.
- `False` trong Python là bool, dùng trực tiếp khi set property kiểu boolean.

## Mini Checkpoints

- Sau TODO 2: bạn đã có helper để tạo element nhanh và an toàn.
- Sau TODO 3: bạn phải có đủ 4 element của decode chain.
- Sau TODO 4: source đã biết đọc file nào, sink đã được config.
- Sau TODO 6: pipeline đã nối xong đến cuối bài học.
