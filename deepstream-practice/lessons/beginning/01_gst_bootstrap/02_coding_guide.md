# Lesson 01 Coding Guide

Guide này không thay thế `01_guide.md`. `01_guide.md` giúp bạn hiểu bài học, còn file này
giúp bạn biết cần gõ dòng nào, gõ theo thứ tự nào, và tại sao.

## Before You Code

- File sẽ được chạy bằng lệnh:

```bash
python3 lessons/beginning/01_gst_bootstrap/03_starter.py /path/to/any-file
```

- `import os`: dùng để kiểm tra file có tồn tại không.
- `import sys`: dùng để lấy `sys.argv` và thoát với mã lỗi.
- `import gi` và `from gi.repository import GLib, Gst`: đây là cách PyGObject expose
  GStreamer và GLib vào Python.

Bạn chưa cần hiểu sâu về `gi` ngay lập tức. Trong bài này, chỉ cần nhớ:

- `Gst` chứa các class/hằng số/hằng enum của GStreamer.
- `GLib.MainLoop()` là vòng lặp sự kiện để app nhận callback.

## Build Order

Hãy code theo thứ tự này:

1. Hoàn thành callback `on_message(...)`.
2. Xử lý input trong `main(args)`.
3. Gọi `Gst.init(None)`.
4. Tạo pipeline và element.
5. Set property cho `filesrc`.
6. Add và link element.
7. Tạo `loop`, lấy `bus`, đăng ký callback.
8. Chuyển pipeline sang `PLAYING`.
9. Trong `finally`, đưa về `NULL`.

Nếu bạn đi đúng thứ tự này, bạn sẽ ít bị "tạo sai thứ tự rồi không biết sửa ở đâu".

## Function-By-Function Walkthrough

### `on_message(bus, message, loop)`

Hàm này là callback cho bus. Khi pipeline gửi message lên bus, GStreamer sẽ gọi hàm
này.

Ba tham số trong bài này:

- `bus`: đối tượng bus đã gọi callback. Ở bài này bạn không cần dùng nhiều.
- `message`: message vừa được gửi lên bus. Đây là tham số quan trọng nhất.
- `loop`: `GLib.MainLoop()` mà bạn truyền vào lúc `bus.connect(...)`, dùng để
  `loop.quit()` khi cần dừng app.

Thứ tự viết hợp lý:

1. Lấy `message_type = message.type`
2. `if message_type == Gst.MessageType.EOS:`
3. `elif message_type == Gst.MessageType.ERROR:`
4. `elif message_type == Gst.MessageType.STATE_CHANGED:`
5. `return True`

### `EOS`

Ham can viet:

```python
if message_type == Gst.MessageType.EOS:
    print("EOS: pipeline da doc het du lieu.")
    loop.quit()
```

Giải thích:

- `message.type` là enum, nên bạn so sánh với `Gst.MessageType.EOS`.
- Khi gặp `EOS`, bài này không còn việc gì để làm nữa, nên gọi `loop.quit()`.

### `ERROR`

Ham can viet:

```python
elif message_type == Gst.MessageType.ERROR:
    err, debug = message.parse_error()
    print(f"ERROR: {err}")
    if debug:
        print(f"DEBUG: {debug}")
    loop.quit()
```

Giải thích:

- `message.parse_error()` trả về 2 giá trị: lỗi chính và debug string.
- Vì đây là Python, bạn có thể unpack trực tiếp bằng `err, debug = ...`.
- Sau khi in lỗi, thường sẽ `loop.quit()` vì pipeline đang ở trạng thái lỗi.

### `STATE_CHANGED`

Ham can viet:

```python
elif message_type == Gst.MessageType.STATE_CHANGED:
    src = message.src
    if src and src.get_name() == "lesson-01-pipeline":
        old_state, new_state, pending = message.parse_state_changed()
        print(
            "PIPELINE STATE:",
            old_state.value_nick,
            "->",
            new_state.value_nick,
            f"(pending={pending.value_nick})",
        )
```

Giải thích:

- Rất nhiều element cũng phát `STATE_CHANGED`, nên bạn lọc chỉ lấy pipeline chính.
- `message.src` là object gửi message.
- `get_name()` giúp bạn kiểm tra có đúng pipeline vừa tạo không.
- `parse_state_changed()` trả về 3 state.

### `main(args)`

`args` ở đây chính là `sys.argv`, được truyền vào tự động cuối file:

```python
raise SystemExit(main(sys.argv))
```

Điều này có nghĩa:

- `args[0]` là tên file Python đang chạy
- `args[1]` là input path người dùng truyền vào

## TODO Mapping

### TODO 1: Xu ly bus message trong `on_message(...)`

Bạn viết ba nhánh `EOS`, `ERROR`, `STATE_CHANGED` như ở trên.

Mini checkpoint:

- Bạn đã biết `message.type` dùng để làm gì
- Bạn đã biết tại sao callback cần `loop`

### TODO 2: Tao pipeline va element

Trong `main(args)`, sau `Gst.init(None)`, hãy viết:

```python
pipeline = Gst.Pipeline.new("lesson-01-pipeline")
source = Gst.ElementFactory.make("filesrc", "file-source")
sink = Gst.ElementFactory.make("fakesink", "fake-sink")
```

Giải thích:

- `Gst.Pipeline.new(...)` tạo một pipeline mới.
- `Gst.ElementFactory.make(factory_name, name)` tạo element từ plugin factory.
- Nếu plugin không tồn tại hoặc tạo thất bại, giá trị có thể là `None`.

Vì vậy bạn cần giữ block check:

```python
if not pipeline or not source or not sink:
    ...
```

Dòng tiếp theo thường là set property cho source.

### TODO 3: Set property cho `filesrc`

Hãy viết:

```python
source.set_property("location", input_path)
```

Giải thích:

- `set_property(...)` là cách đặt property cho GObject trong PyGObject.
- `"location"` là tên property của `filesrc`.
- `input_path` là giá trị người dùng truyền vào.

Dòng tiếp theo thường là add element vào pipeline.

### TODO 4: Add element vao pipeline

Hãy viết:

```python
pipeline.add(source)
pipeline.add(sink)
```

Giải thích:

- Element phải nằm trong pipeline thì mới có thể link và chạy cùng pipeline.
- `add(...)` không trả về giá trị mà bạn cần dùng tiếp trong bài này.

Dòng tiếp theo thường là `link(...)`.

### TODO 5: Link `filesrc -> fakesink`

Hãy viết:

```python
if not source.link(sink):
    print("Không link được filesrc -> fakesink", file=sys.stderr)
    return 1
```

Giải thích:

- `link(...)` thường trả về bool cho biết có nối thành công hay không.
- Ở bài này, hai element có thể link trực tiếp bằng API element-level.

Sau đó bạn mới tạo `GLib.MainLoop()` và bus.

### TODO 6: Bus va main loop

Block có sẵn:

```python
loop = GLib.MainLoop()
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message", on_message, loop)
```

Giải thích:

- `GLib.MainLoop()` tạo event loop.
- `pipeline.get_bus()` lấy bus của pipeline.
- `add_signal_watch()` bảo với GLib rằng bạn muốn nhận message theo kiểu signal/callback.
- `connect("message", on_message, loop)` nối signal `message` với callback
  `on_message`, đồng thời truyền thêm `loop` vào callback.

## Syntax Notes

- `if not source`: trong Python, cách này dùng để check `None` hoặc giá trị falsy.
- `err, debug = ...`: đây là tuple unpacking.
- `f"...{value}..."`: đây là f-string để nối chuỗi.
- `return True` trong callback nghĩa là tiếp tục nhận message tiếp.

## Mini Checkpoints

- Sau TODO 2: bạn phải có `pipeline`, `source`, `sink`.
- Sau TODO 4: hai element đã nằm trong pipeline.
- Sau TODO 5: pipeline đã nối xong từ source đến sink.
- Sau TODO 6: app đã sẵn sàng nhận `EOS` và `ERROR`.
