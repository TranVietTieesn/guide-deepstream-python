# Lesson 03 Coding Guide

Từ bài này, bạn không chỉ link bằng `element.link(...)` nữa. Bạn sẽ phải xử lý ở
mức pad, vì `nvstreammux` dùng request pad.

## Before You Code

Lệnh chạy:

```bash
python3 lessons/03_streammux_single_source/03_starter.py /path/to/sample_1080p_h264.h264
```

Input vẫn là file H264 elementary stream.

Phần khác lesson 02:

- bạn có thêm `nvstreammux`
- bạn có thêm constant `MUXER_BATCH_TIMEOUT_USEC`
- bạn phải làm việc với `Gst.Pad`

## Build Order

1. Hoàn thành `on_message(...)`.
2. Hoàn thành `make_element(...)`.
3. Parse input và `Gst.init(None)`.
4. Tạo pipeline và 5 element.
5. Set property cho source, streammux, sink.
6. Add element vào pipeline.
7. Link static chain đến `decoder`.
8. Xin request pad từ `streammux`.
9. Lấy static pad từ `decoder`.
10. Link pad-level.
11. Link `streammux -> fakesink`.
12. Tạo bus, main loop, chạy pipeline.

## Function-By-Function Walkthrough

### `on_message(bus, message, loop)`

Giống lesson 02, bài này chỉ cần `EOS` và `ERROR`.

### `make_element(factory_name, name)`

Giong lesson 02. Bạn nên hoàn thành helper này trước để phần dưới ngắn gọn hơn.

### Tao element

Sau `Gst.init(None)`, hay viet:

```python
pipeline = Gst.Pipeline.new("lesson-03-pipeline")
source = make_element("filesrc", "file-source")
parser = make_element("h264parse", "h264-parser")
decoder = make_element("nvv4l2decoder", "hw-decoder")
streammux = make_element("nvstreammux", "stream-muxer")
sink = make_element("fakesink", "fake-sink")
```

Sau block này, bạn mới set property.

### Set property

Mau viet:

```python
source.set_property("location", input_path)
streammux.set_property("batch-size", 1)
streammux.set_property("width", 1920)
streammux.set_property("height", 1080)
streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
sink.set_property("sync", False)
```

Giải thích:

- `batch-size` là kích thước batch tối đa.
- `width` và `height` là output size mà muxer sẽ tạo.
- `batched-push-timeout` giúp muxer không chờ mãi khi tạo batch.
- `sync=False` vẫn là config nhẹ cho `fakesink`.

### Link static chain

Phần này vẫn giống lesson 02:

```python
if not source.link(parser):
    raise RuntimeError("Khong link duoc filesrc -> h264parse")
if not parser.link(decoder):
    raise RuntimeError("Khong link duoc h264parse -> nvv4l2decoder")
```

Bạn dùng lại `element.link(...)` vì đây vẫn là phần static chain.

### Xin request pad tu `nvstreammux`

Mau viet:

```python
sinkpad = streammux.request_pad_simple("sink_0")
if not sinkpad:
    raise RuntimeError("Khong xin duoc request pad sink_0 tu nvstreammux")
```

Giải thích:

- Hàm này trả về một `Gst.Pad`, không phải một element.
- `sink_0` là tên pad cụ thể bạn muốn xin.
- Khác với `element.link(...)`, ở đây bạn đang thao tác trực tiếp ở mức pad.

### Lay static pad tu `decoder`

Mau viet:

```python
srcpad = decoder.get_static_pad("src")
if not srcpad:
    raise RuntimeError("Khong lay duoc src pad tu decoder")
```

Giải thích:

- `get_static_pad("src")` lấy pad có sẵn của decoder.
- Hàm này cũng trả về `Gst.Pad`.

### Link pad-level

Mau viet:

```python
if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
    raise RuntimeError("Khong link duoc decoder.src -> streammux.sink_0")
```

Giải thích:

- `srcpad.link(sinkpad)` không trả về bool như `element.link(...)`.
- Nó trả về một giá trị enum `Gst.PadLinkReturn`.
- Bài học ở đây là: khi làm việc ở mức pad, bạn phải check kết quả theo kiểu pad API.

### Link phan cuoi pipeline

Mau viet:

```python
if not streammux.link(sink):
    raise RuntimeError("Khong link duoc nvstreammux -> fakesink")
```

Lúc này bạn quay lại element-level API, vì `streammux` đã có src pad phù hợp để nối
với sink.

## Starter Mapping

### TODO 1: Hoan thanh `on_message(...)`

- `EOS`
- `ERROR`
- `return True`

### TODO 2: Hoan thanh `make_element(...)`

- Giong lesson 02

### TODO 3: Tao day du element

- `filesrc`
- `h264parse`
- `nvv4l2decoder`
- `nvstreammux`
- `fakesink`

### TODO 4: Set property cho source, streammux, sink

- `location`
- `batch-size`
- `width`
- `height`
- `batched-push-timeout`
- `sync`

### TODO 5: Add element vao pipeline

- Dung loop `for element in (...)`

### TODO 6: Link static chain

- `filesrc -> h264parse -> nvv4l2decoder`

### TODO 7: Xin `sink_0` tu `streammux`

- Dung `request_pad_simple(...)`
- Check loi ngay

### TODO 8: Lay `decoder.src`

- Dung `get_static_pad("src")`
- Check loi ngay

### TODO 9: Link pad-level va link phan cuoi

- `srcpad.link(sinkpad)`
- `streammux.link(sink)`

## Syntax Notes

- `srcpad` va `sinkpad` la `Gst.Pad`, khong phai `Gst.Element`.
- `element.link(...)` va `pad.link(...)` la hai muc API khac nhau.
- `!= Gst.PadLinkReturn.OK` la cach check thanh cong cho pad-level link.

## Mini Checkpoints

- Sau TODO 4: muxer da duoc cau hinh, khong chi moi duoc tao ra.
- Sau TODO 6: pipeline da chay den `decoder`.
- Sau TODO 8: ban da co 2 pad object trong tay.
- Sau TODO 9: pipeline da noi xong qua `nvstreammux`.
