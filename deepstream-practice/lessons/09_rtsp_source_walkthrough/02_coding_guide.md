# Lesson 09 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/09_rtsp_source_walkthrough/03_starter.py rtsp://user:pass@host:554/path
```

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `cb_newpad(...)`
4. Hoan thanh `create_source_bin(...)`
5. Tao downstream
6. Link source bin vao muxer
7. Chay pipeline

## Function-By-Function Walkthrough

### `cb_newpad(decodebin, decoder_src_pad, source_bin)`

Thu tu nen viet:

1. lay `caps`
2. neu can thi `query_caps(None)`
3. lay `caps_features`
4. check `memory:NVMM`
5. lay ghost pad `src` tu `source_bin`
6. `ghost_pad.set_target(decoder_src_pad)`

Muc tieu callback:

- chi noi nhung pad decode hop le vao pipeline chinh

### `create_source_bin(index, uri)`

Ham nay nen:

- tao `Gst.Bin`
- tao `uridecodebin`
- set `uri`
- connect `pad-added`
- add `uridecodebin` vao bin
- tao ghost pad `src`
- add ghost pad vao bin
- `return source_bin`

## Starter Mapping

### TODO 1-2

- `on_message`, `make_element`

### TODO 3

- `cb_newpad(...)`

### TODO 4

- `create_source_bin(...)`

### TODO 5

- tao downstream elements

### TODO 6

- set property cho muxer, pgie, sink

### TODO 7

- add element vao pipeline

### TODO 8

- xin `sink_0`
- lay `source_bin.src`
- link vao muxer

### TODO 9

- link downstream

## Syntax Notes

- `Gst.Bin.new(name)` tao mot container element
- `Gst.GhostPad.new_no_target(...)` tao ghost pad chua noi den pad that
- `ghost_pad.set_target(...)` la luc source bin "loi src ra ngoai"
- `caps_features.contains("memory:NVMM")` dung de loc decode path phu hop

## Mini Checkpoints

- Sau TODO 3: ban biet pad dong nao se duoc phep di tiep
- Sau TODO 4: source bin da co `src` ghost pad
- Sau TODO 8: source RTSP da noi vao muxer thanh cong
