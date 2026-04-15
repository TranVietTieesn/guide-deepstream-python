# Lesson 03 Coding Guide

Lesson nay co them 2 block code moi ma lesson 01 va 02 khong co:

- encoder chain
- RTSP server helper

Neu ban muon code lam chut nao cung duoc, hay chia thanh 2 pha:

1. lam xong pipeline media
2. moi lam xong RTSP server wiring

## Before You Code

- Input: H.264 file.
- Output: RTSP stream qua `GstRtspServer`.
- Imports can nho:
  - `Gst`, `GLib`
  - `GstRtspServer`
  - `PlatformInfo`
  - `bus_call`
  - khong can `pyds` trong starter nay vi probe/metadata chua duoc khai thac
    trong doc nay

## Build Order

1. Viet `on_message(...)`.
2. Viet `make_element(...)`.
3. Viet `create_sink(...)`.
4. Viet `create_rtsp_server(...)`.
5. Trong `main(args)`, parse input va check config.
6. Tao pipeline va cac element tu source den UDP sink.
7. Set property cho source, mux, infer, encoder, sink.
8. Add tat ca element vao pipeline.
9. Link decode chain va request pad vao muxer.
10. Link downstream encoder chain.
11. Tao RTSP server va attach mount point.
12. Tao bus/main loop va chay pipeline.

## Function-By-Function Walkthrough

### `main(args)`

- `main(...)` van bat dau bang input validation nhu cac lesson truoc.
- Diem khac la sau khi pipeline da link xong, ban con phai khoi tao server.
- Neu ban tao server truoc khi pipeline san sang, debug se bi roi:
  - khong ro stream fail o data plane hay server plane

### `create_rtsp_server(port, codec)`

- Day la helper setup output layer.
- No khong tao media frames.
- No chi:
  - tao server
  - set service port
  - tao media factory
  - gan launch string
  - add mount point

Hieu ham nay nhu "web server wiring for media", khong phai "video processing".

### `create_sink(platform_info)`

- Van giu chan trong baseline: logic chon sink phu thuoc platform.
- Trong RTSP lesson, sink nay khong phai final UX, nhung van can co vi app co the
  muon local render khi debug.

## Syntax Notes

- `caps.set_property("caps", Gst.Caps.from_string(...))`
  - dung de dat format truoc encoder.
- `encoder.set_property("insert-sps-pps", 1)`
  - rat quan trong voi stream live.
- `factory.set_launch("...")`
  - chuoi launch cua RTSP factory khong phai pipeline Python.
- `server.get_mount_points().add_factory("/ds-test", factory)`
  - day la noi server public endpoint.

## Starter Mapping

### TODO 1: `on_message(...)`

- `EOS`
- `ERROR`

### TODO 2: `make_element(...)`

- Tao element va fail som neu khong co plugin.

### TODO 3: `create_sink(...)`

- Chon sink theo platform.

### TODO 4: `create_rtsp_server(...)`

- Tao server, media factory, launch string, mount point.

### TODO 5: Set property

- `source.location`
- `streammux.batch-size`
- `pgie.config-file-path`
- `encoder.bitrate`
- `encoder.insert-sps-pps`
- `sink.host/port/async/sync`

### TODO 6: Add elements

- Tu source den sink.

### TODO 7: Link decode chain va request pad

- `filesrc -> h264parse -> nvv4l2decoder`
- `decoder.src -> streammux.sink_0`

### TODO 8: Link encoder chain

- `streammux -> pgie -> nvvidconv -> nvosd -> nvvidconv_postosd -> caps -> encoder -> rtppay -> sink`

### TODO 9: Tao RTSP server

- `create_rtsp_server(8554, "H264")`

## Mini Checkpoints

- Sau TODO 8, ban da co RTP packets chua?
- Sau TODO 9, ban da co endpoint `/ds-test` chua?
- Neu bo server helper, pipeline co con output duoc ra network khong?
- Ban co biet phan nao la data plane va phan nao la service plane khong?
