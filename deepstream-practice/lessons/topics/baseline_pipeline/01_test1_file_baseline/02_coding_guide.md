# Lesson 01 Coding Guide

Lesson nay khong chi day "goi ham nao", ma day cach chia pipeline thanh cac block
co logic ro rang:

1. tao object
2. set property
3. add vao pipeline
4. link static pad
5. xin request pad
6. dat pad probe
7. chay loop

## Before You Code

- Input: 1 file H.264 elementary stream.
- Output logic: display/render local, khong phai RTSP.
- Config that: `apps/deepstream-test1/dstest1_pgie_config.txt`.
- Imports can nho:
  - `Gst`, `GLib` cho pipeline va main loop
  - `PlatformInfo` cho sink selection
  - `pyds` cho metadata probe

## Build Order

1. Viet `on_message(...)`.
2. Viet `make_element(...)`.
3. Viet `create_sink(...)`.
4. Trong `main(args)`, parse input va kiem tra config.
5. Tao pipeline va cac element.
6. Set property cho source, streammux, pgie, sink.
7. Add all element vao pipeline.
8. Link static chain `filesrc -> h264parse -> nvv4l2decoder`.
9. Xin request pad `sink_0` tu `nvstreammux`.
10. Lay `decoder.src` va link pad-level.
11. Link phan downstream.
12. Gan probe vao `nvdsosd.sink`.
13. Tao bus/main loop va chuyen sang `PLAYING`.

## Function-By-Function Walkthrough

### `on_message(bus, message, loop)`

- Chuc nang: nghe bus de biet pipeline da dung hay gap loi.
- Can xu ly toi thieu:
  - `EOS`: thoat loop
  - `ERROR`: parse va thoat loop
- Trong lesson nay, ham nay nen nho va ro: no khong lam data processing.

### `make_element(factory_name, name)`

- Day la helper de giam lap code.
- Neu `Gst.ElementFactory.make(...)` fail, raise ngay.
- Logic nay quan trong vi lesson co nhieu element; neu khong co helper, phan `main`
  se bi loang va kho doc.

### `create_sink(platform_info)`

- Nhiem vu: chon sink phu hop platform.
- `PlatformInfo` chi tra loi "may nay la gi", khong tao sink thay ban.
- `main(...)` se dong y tuong cua ham nay bang cach coi `sink` nhu mot element
  binh thuong sau khi tao xong.

### `main(args)`

Thu tu code nen di theo dung skeleton:

1. Validate input.
2. `Gst.init(None)`.
3. Tao `PlatformInfo()`.
4. Tao pipeline va element.
5. Set property.
6. Add/link.
7. Dat probe.
8. Tao bus watch.
9. `PLAYING`.
10. Cleanup.

Neu ban viec tu TODO 5 tro di truoc TODO 4, lesson se rat de bi roi.

## Syntax Notes

- `element.link(...)` tra ve `bool`.
- `pad.link(...)` tra ve `Gst.PadLinkReturn`.
- `request_pad_simple("sink_0")` tra ve `Gst.Pad`.
- `get_static_pad("src")` cung tra ve `Gst.Pad`.
- `osdsinkpad.add_probe(...)` khong phai la link; no la gan callback vao duong
  di cua buffer.

## Starter Mapping

### TODO 0: `osd_sink_pad_buffer_probe(...)`

- Day la cho doc metadata sau infer.
- O level nay, ban chi can biet probe duoc gan vao sink pad cua `nvdsosd`.

### TODO 1: `on_message(...)`

- `EOS`
- `ERROR`
- `return True`

### TODO 2: `make_element(...)`

- Tao element va check `None` ngay.

### TODO 3: `create_sink(...)`

- Chon `nv3dsink` hoac `nveglglessink` theo platform.

### TODO 4: Tao pipeline va element

- `filesrc`
- `h264parse`
- `nvv4l2decoder`
- `nvstreammux`
- `nvinfer`
- `nvvideoconvert`
- `nvdsosd`
- sink

### TODO 5: Set property

- `source.location`
- `streammux.batch-size`
- `streammux.width`
- `streammux.height`
- `streammux.batched-push-timeout`
- `pgie.config-file-path`
- `sink.sync = False`

### TODO 6: Add elements vao pipeline

- Dung loop qua tuple.

### TODO 7: Link static chain

- `filesrc -> h264parse -> nvv4l2decoder`

### TODO 8: Xin request pad va lay `decoder.src`

- `streammux.request_pad_simple("sink_0")`
- `decoder.get_static_pad("src")`

### TODO 9: Link pad-level va downstream

- `srcpad.link(sinkpad)`
- `streammux -> pgie -> nvvidconv -> nvosd -> sink`

### TODO 10: Dat probe

- `nvosd.get_static_pad("sink")`
- `add_probe(Gst.PadProbeType.BUFFER, ...)`

## Mini Checkpoints

- Sau TODO 5, ban da co day du thong tin de pipeline co the chay chua?
- Sau TODO 8, ban co 2 pad object va biet pad nao la source/target chua?
- Sau TODO 9, data da co duong di den sink chua?
- Sau TODO 10, ban co the doc object metadata ngay tai sink pad cua OSD chua?
