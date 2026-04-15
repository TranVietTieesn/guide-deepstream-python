# Lesson 04 Coding Guide

Lesson nay co 2 sidecar logics:

- source bin cho RTSP live input
- RTSP server cho output

## Before You Code

- Input: RTSP URI list.
- Output: RTSP stream.
- Imports:
  - `GstRtspServer`
  - `PlatformInfo`
  - `bus_call`
  - `pyds`

## Build Order

1. Source bin helpers.
2. RTSP source sync logic.
3. Live source muxer config.
4. Infer and OSD chain.
5. Encoder chain.
6. RTSP server helper.
7. Bus/main loop.

## Function-By-Function Walkthrough

### `cb_newpad(...)`

- Same dynamic pad logic, but live RTSP source can be more timing-sensitive.

### `decodebin_child_added(...)`

- Đây la noi source-specific timing properties co the duoc set.

### `create_rtsp_server(...)`

- Tao server, set launch string, add mount point.
- Giay phut nay rat nho: giu object server o mot bien local trong `main(...)`
  de lifecycle cua no ro rang khi doc code.

### `main(...)`

- `ts_from_rtsp` and `live-source` are the new thinking here.
- The rest still follows the same GStreamer lifecycle.

## Syntax Notes

- `server.props.service = "8554"`
- `factory.set_launch('( udpsrc name=pay0 ... )')`
- `source_bin.get_static_pad("src")`
- `rtsp_server = create_rtsp_server(...)` nen duoc giu lai trong `main(...)`,
  khong nen goi xong bo qua hoan toan.

## Starter Mapping

- `TODO 1`: dynamic pad handling
- `TODO 2`: RTSP source child-added
- `TODO 3`: source bin
- `TODO 4`: RTSP server helper

## Mini Checkpoints

- Ban co phan biet source RTSP va server RTSP khong?
- `drop-on-latency` nam o input hay output?
- `udpsink` co phai la client-facing endpoint khong?
