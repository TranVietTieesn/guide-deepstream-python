# Lesson 03 Coding Guide

Tai lieu nay la guide thuc thi theo tung buoc de hoan thanh `03_starter.py`.
Muc tieu la giup ban code co thu tu, de debug, va de review.

## Scope Of This Guide

Ban se hoan thanh 9 TODO trong starter:

- TODO 1-4: viet helper function.
- TODO 5-8: wiring pipeline media.
- TODO 9: wiring RTSP server.

Tu duy chinh:

1. Dung pipeline tao RTP packet.
2. Dung RTSP server expose RTP thanh URL cho client.

## Prerequisites

Truoc khi code, kiem tra:

- Input la file H.264 hop le.
- Ton tai file config infer:
  `apps/deepstream-test1-rtsp-out/dstest1_pgie_config.txt`.
- Imports:
  - `Gst`, `GLib`
  - `GstRtspServer`
  - `PlatformInfo`
  - helper bus message (`bus_call` hoac custom handler)

## Implementation Strategy (Recommended)

Thuc hien theo 2 pha:

### Phase A - Media Pipeline First

- Tao va link xong chain den `udpsink`.
- Dam bao pipeline PLAYING khong fail.

### Phase B - RTSP Service Second

- Tao `GstRtspServer`.
- Tao `RTSPMediaFactory` va mount `/ds-test`.
- Verify client mo duoc stream.

Lam theo thu tu nay giup debug nhanh hon vi tach ro data plane va service plane.

## Build Order (One-pass)

1. Implement `on_message(...)`.
2. Implement `make_element(...)`.
3. Implement `create_sink(...)`.
4. Implement `create_rtsp_server(...)`.
5. Trong `main(args)`: validate input + config.
6. Tao day du element.
7. Set property cho source/mux/infer/encoder/sink.
8. Add tat ca vao pipeline.
9. Link source decode chain.
10. Link request pad: `decoder.src -> streammux.sink_0`.
11. Link downstream encode chain den `udpsink`.
12. Khoi tao RTSP server.
13. Main loop + bus watch + cleanup.

## Function Guide

### `on_message(bus, message, loop)`

Bat buoc handle:

- `EOS`: in log, `loop.quit()`.
- `ERROR`: parse error + debug string, in log, `loop.quit()`.

Muc tieu: app thoat sach thay vi treo.

### `make_element(factory_name, name)`

Pattern dung:

1. `Gst.ElementFactory.make(...)`.
2. Neu fail, raise `RuntimeError` ngay.

Tai sao quan trong: fail som de biet thieu plugin nao.

### `create_sink(platform_info)`

Guide co ban:

- Integrated GPU / aarch64: uu tien `nv3dsink`.
- Con lai: `nveglglessink`.

Luu y: bai nay output chinh la RTSP, local sink chi ho tro debug.

### `create_rtsp_server(port, codec)`

Can lam du:

1. Tao `RTSPServer`, set `service = str(port)`.
2. Tao `RTSPMediaFactory`.
3. `set_launch(...)` voi `udpsrc name=pay0 port=5400 ... encoding-name=<codec>`.
4. `factory.set_shared(True)`.
5. Mount vao `/ds-test`.
6. `server.attach(None)`.

Nho: launch string nay la mini pipeline cua RTSP factory, khong phai pipeline Python.

## Property Checklist (TODO 5)

Property toi thieu nen set:

- `source.location = input_path`
- `streammux.batch-size = 1`
- `streammux.width/height/batched-push-timeout` (neu pipeline can)
- `pgie.config-file-path = PGIE_CONFIG_PATH`
- `caps.caps = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")`
- `encoder.bitrate = 4000000` (tham khao)
- `encoder.insert-sps-pps = 1`
- `sink.host = "224.224.255.255"` (hoac host mong muon)
- `sink.port = 5400`
- `sink.async = False`
- `sink.sync = 1`

## Linking Checklist

### TODO 7: Decode + Mux

- Link:
  `filesrc -> h264parse -> nvv4l2decoder`
- Xin request pad:
  `streammux.request_pad_simple("sink_0")`
- Link:
  `decoder.get_static_pad("src") -> streammux.sink_0`

### TODO 8: Downstream Encode Chain

Link dung thu tu:

`streammux -> pgie -> nvvidconv -> nvosd -> nvvidconv_postosd -> caps -> encoder -> rtppay -> udpsink`

Bat buoc check tung `link()` va raise neu fail.

## TODO-by-TODO Mapping

### TODO 1

- Hoan thanh message handler cho `EOS` va `ERROR`.

### TODO 2

- Hoan thanh helper tao element + fail-fast.

### TODO 3

- Hoan thanh sink selection theo platform.

### TODO 4

- Hoan thanh RTSP server helper + `/ds-test`.

### TODO 5

- Dat property cho source/mux/infer/encoder/sink/caps.

### TODO 6

- `pipeline.add(...)` day du tat ca element.

### TODO 7

- Link decode chain + request pad vao mux.

### TODO 8

- Link toan bo chain sau mux den UDP sink.

### TODO 9

- Goi `create_rtsp_server(8554, "H264")`.

## Verification Workflow

### Step 1: Runtime logs

- App vao PLAYING khong loi link/property.
- Khong co message ERROR tu bus.

### Step 2: Endpoint check

- Co mount point `/ds-test`.
- Mo stream:
  `rtsp://<host>:8554/ds-test`

### Step 3: Functional check

- Client hien stream.
- Overlay detect xuat hien (neu OSD/probe da bat).

## Quick Troubleshooting Matrix

- **No element**: sai factory name hoac thieu plugin.
- **No stream in client**: sai `udpsink.port` vs `udpsrc port` trong factory.
- **Client cannot connect**: RTSP port da bi chiem hoac sai URL.
- **Pipeline links fail**: sai thu tu chain hoac thieu caps hop le.
- **Stream unstable**: thu dieu chinh bitrate/sync va bat `insert-sps-pps`.

## Completion Rubric

Ban co the xem la "xong bai" neu:

1. Code het TODO, khong con `NotImplementedError`.
2. Pipeline PLAYING on dinh.
3. Client mo duoc `rtsp://.../ds-test`.
4. Ban giai thich duoc tai sao `udpsink` va `GstRtspServer` phai khop port.
