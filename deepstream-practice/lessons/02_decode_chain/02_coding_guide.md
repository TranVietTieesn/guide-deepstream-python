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

Mau viet:

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

Mau viet:

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

Giai thich:

- `make_element(...)` da gom san logic check loi.
- `pipeline` van duoc tao rieng vi no khong phai element factory thong thuong.

### Set property

Hay viet:

```python
source.set_property("location", input_path)
sink.set_property("sync", False)
```

Giai thich:

- `location` chi cho `filesrc` file nao can doc.
- `sync=False` voi `fakesink` thuong duoc dung de sink khong co gang dong bo voi
  clock hien thi. O bai hoc phan tich pipeline, dieu nay giup sink "de tinh" hon.

### Add element vao pipeline

Mau viet:

```python
for element in (source, parser, decoder, sink):
    pipeline.add(element)
```

Giai thich:

- Python cho phep loop qua tuple de giam lap code.
- Sau block nay, tat ca element da nam trong pipeline.

### Link tung buoc

Mau viet:

```python
if not source.link(parser):
    raise RuntimeError("Khong link duoc filesrc -> h264parse")
if not parser.link(decoder):
    raise RuntimeError("Khong link duoc h264parse -> nvv4l2decoder")
if not decoder.link(sink):
    raise RuntimeError("Khong link duoc nvv4l2decoder -> fakesink")
```

Giai thich:

- `link(...)` tra ve bool.
- O bai nay, link bang element-level API la du vi cac pad can dung deu la static
  va co the noi truc tiep.
- Thu tu link cung la thu tu du lieu chay trong pipeline.

## Starter Mapping

### TODO 1: Hoan thanh `on_message(...)`

- Giai quyet `EOS`
- Giai quyet `ERROR`
- `return True`

### TODO 2: Hoan thanh `make_element(...)`

- Tao bang `Gst.ElementFactory.make(...)`
- Check loi ngay
- `return element`

### TODO 3: Tao 4 element can thiet

- `filesrc`
- `h264parse`
- `nvv4l2decoder`
- `fakesink`

### TODO 4: Set property

- `source.location = input_path`
- `sink.sync = False`

### TODO 5: Add element vao pipeline

- Co the dung `for element in (...)`

### TODO 6: Link decode chain

- `filesrc -> parser -> decoder -> sink`

## Syntax Notes

- `raise RuntimeError(...)` la cach dung de dung ngay khi co loi logic/tao element.
- `for element in (...)` la cach viet Python gon de lam lap lai cung mot thao tac.
- `False` trong Python la bool, dung truc tiep khi set property kieu boolean.

## Mini Checkpoints

- Sau TODO 2: ban da co helper de tao element nhanh va an toan.
- Sau TODO 3: ban phai co du 4 element cua decode chain.
- Sau TODO 4: source da biet doc file nao, sink da duoc config.
- Sau TODO 6: pipeline da noi xong den cuoi bai hoc.
