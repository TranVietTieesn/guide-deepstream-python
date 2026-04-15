# Lesson 02 Coding Guide

Lesson nay lam sang mot query rat thuc te: khi source la USB camera, ban code
pipeline nhu the nao de raw frame di vao DeepStream ma khong bi "sai format".

## Before You Code

- Input: `v4l2-device-path`.
- Config: `apps/deepstream-test1-usbcam/dstest1_pgie_config.txt`.
- Imports can nho:
  - `Gst`, `GLib`
  - `PlatformInfo`
  - khong can `pyds` trong file starter nay vi guide tap trung vao pipeline, khong
    doc metadata.

## Build Order

1. Viet `on_message(...)`.
2. Viet `make_element(...)`.
3. Viet `create_sink(...)`.
4. Parse device path va kiem tra config.
5. Tao pipeline va tung element.
6. Set caps cho raw input va NVMM bridge.
7. Set property cho source, mux, infer, sink.
8. Add tat ca element vao pipeline.
9. Link source chain qua 2 converter.
10. Xin request pad va link vao `nvstreammux`.
11. Link downstream.
12. Tao bus/main loop va chay pipeline.

## Function-By-Function Walkthrough

### `main(args)`

- `args[1]` la duong dan device.
- Can check file ton tai truoc khi tao pipeline.
- Khac lesson 01 o cho source khong con la file compressed.
- Khi viet `main`, hay chia thanh 3 khoi:
  1. validate
  2. construct
  3. run

### Helper functions

- `make_element(...)` van giup code gon va bat loi som.
- `create_sink(...)` tach logic platform de `main(...)` khong phai biet may chi tiet
  cua render backend.

## Syntax Notes

- `caps_v4l2src.set_property("caps", Gst.Caps.from_string(...))`
  - dung khi ban muon lock raw format.
- `caps_vidconvsrc.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM)"))`
  - day la cuoc doi sang NVMM.
- `source.link(caps_v4l2src)` van la element-level link.
- `srcpad.link(sinkpad)` van la pad-level link nhu lesson 03.

## Starter Mapping

### TODO 1: `on_message(...)`

- `EOS`
- `ERROR`

### TODO 2: `make_element(...)`

- Tao element va raise neu fail.

### TODO 3: `create_sink(...)`

- Chon `nv3dsink` hoac `nveglglessink`.

### TODO 4: Set property

- `source.device`
- raw caps cho `caps_v4l2src`
- NVMM caps cho `caps_vidconvsrc`
- `streammux.width/height/batch-size/batched-push-timeout`
- `pgie.config-file-path`
- `sink.sync = False`

### TODO 5: Add elements

- Dung tuple va loop.

### TODO 6: Link source bridge

- `v4l2src -> capsfilter -> videoconvert -> nvvideoconvert -> capsfilter`

### TODO 7: Request pad va pad link

- `streammux.request_pad_simple("sink_0")`
- `caps_vidconvsrc.get_static_pad("src")`
- link vao muxer

### TODO 8: Link downstream

- `streammux -> pgie -> nvvidconv -> nvosd -> sink`

## Mini Checkpoints

- Sau TODO 4, ban co lock raw input va NVMM output chua?
- Sau TODO 6, buffer da co duong di vao NVMM chua?
- Sau TODO 7, ban co hieu vi sao `nvstreammux` khong link bang `element.link(...)`
  khong?
- Sau TODO 8, pipeline da quay lai "DeepStream mode" chua?
