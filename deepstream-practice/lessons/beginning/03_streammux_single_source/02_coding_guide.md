# Lesson 03 Coding Guide

Từ bài này, bạn không chỉ link bằng `element.link(...)` nữa. Bạn sẽ phải xử lý ở
mức pad, vì `nvstreammux` dùng request pad.

## Before You Code

Lệnh chạy:

```bash
python3 lessons/beginning/03_streammux_single_source/03_starter.py /path/to/sample_1080p_h264.h264
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

Giống lesson 02. Bạn nên hoàn thành helper này trước để phần dưới ngắn gọn hơn.

### Tạo element

Sau `Gst.init(None)`, hãy viết:

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

Mẫu viết:

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
    raise RuntimeError("Không link được filesrc -> h264parse")
if not parser.link(decoder):
    raise RuntimeError("Không link được h264parse -> nvv4l2decoder")
```

Bạn dùng lại `element.link(...)` vì đây vẫn là phần static chain.

### Xin request pad từ `nvstreammux`

Mẫu viết:

```python
sinkpad = streammux.request_pad_simple("sink_0")
if not sinkpad:
    raise RuntimeError("Không xin được request pad sink_0 từ nvstreammux")
```

Giải thích:

- Hàm này trả về một `Gst.Pad`, không phải một element.
- `sink_0` là tên pad cụ thể bạn muốn xin.
- Khác với `element.link(...)`, ở đây bạn đang thao tác trực tiếp ở mức pad.

### Lấy static pad từ `decoder`

Mẫu viết:

```python
srcpad = decoder.get_static_pad("src")
if not srcpad:
    raise RuntimeError("Không lấy được src pad từ decoder")
```

Giải thích:

- `get_static_pad("src")` lấy pad có sẵn của decoder.
- Hàm này cũng trả về `Gst.Pad`.

### Link pad-level

Mẫu viết:

```python
if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
    raise RuntimeError("Không link được decoder.src -> streammux.sink_0")
```

Giải thích:

- `srcpad.link(sinkpad)` không trả về bool như `element.link(...)`.
- Nó trả về một giá trị enum `Gst.PadLinkReturn`.
- Bài học ở đây là: khi làm việc ở mức pad, bạn phải check kết quả theo kiểu pad API.

### Link phần cuối pipeline

Mẫu viết:

```python
if not streammux.link(sink):
    raise RuntimeError("Không link được nvstreammux -> fakesink")
```

Lúc này bạn quay lại element-level API, vì `streammux` đã có src pad phù hợp để nối
với sink.

## Starter Mapping

### TODO 1: Hoàn thành `on_message(...)`

- `EOS`
- `ERROR`
- `return True`

### TODO 2: Hoàn thành `make_element(...)`

- Giống lesson 02

### TODO 3: Tạo đầy đủ element

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

### TODO 5: Add element vào pipeline

- Dùng loop `for element in (...)`

### TODO 6: Link static chain

- `filesrc -> h264parse -> nvv4l2decoder`

### TODO 7: Xin `sink_0` từ `streammux`

- Dùng `request_pad_simple(...)`
- Check lỗi ngay

### TODO 8: Lấy `decoder.src`

- Dùng `get_static_pad("src")`
- Check lỗi ngay

### TODO 9: Link pad-level và link phần cuối

- `srcpad.link(sinkpad)`
- `streammux.link(sink)`

## Syntax Notes

- `srcpad` và `sinkpad` là `Gst.Pad`, không phải `Gst.Element`.
- `element.link(...)` và `pad.link(...)` là hai mức API khác nhau.
- `!= Gst.PadLinkReturn.OK` là cách check thành công cho pad-level link.

## Mini Checkpoints

- Sau TODO 4: muxer đã được cấu hình, không chỉ mới được tạo ra.
- Sau TODO 6: pipeline đã chạy đến `decoder`.
- Sau TODO 8: bạn đã có 2 pad object trong tay.
- Sau TODO 9: pipeline đã nối xong qua `nvstreammux`.
