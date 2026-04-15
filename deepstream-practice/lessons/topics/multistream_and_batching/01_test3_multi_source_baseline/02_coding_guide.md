# Lesson 01 Coding Guide

Lesson nay co 2 truc code quan trong:

1. source bin + dynamic pad handling
2. batch pipeline + tiler

## Before You Code

- Input: mot danh sach URI.
- Output: tiled multi-source display.
- Imports:
  - `Path`, `argparse`, `configparser`
  - `Gst`, `GLib`
  - `PlatformInfo`, `bus_call`, `PERF_DATA`
  - `pyds`

## Build Order

1. Viet `cb_newpad(...)`.
2. Viet `decodebin_child_added(...)`.
3. Viet `create_source_bin(...)`.
4. Viet `pgie_src_pad_buffer_probe(...)`.
5. Trong `main(...)`, parse args va khoi tao perf tracker.
6. Tao pipeline va `nvstreammux`.
7. Tao source bins va link vao muxer.
8. Tao pgie, tiler, queues, nvosd, sink.
9. Set `live-source`, `batch-size`, `width`, `height`, tiler rows/columns.
10. Add elements va link pipeline.
11. Gan probe va perf callback.
12. Chay loop.

## Function-By-Function Walkthrough

### `cb_newpad(...)`

- Callback nay bat khi decodebin tao pad moi.
- Ban phai check:
  - pad name co phai video khong
  - caps co `memory:NVMM` khong
- Neu khong co NVMM, source bin khong nen noi vao DeepStream core.

### `decodebin_child_added(...)`

- Hook nay theo doi child ben trong decodebin.
- Trong sample, no giup xu ly source-specific properties nhu `drop-on-latency`.

### `create_source_bin(...)`

- Tao `Gst.Bin`.
- Ganh `uridecodebin`.
- Dat `uri`.
- Nhan `pad-added` va `child-added`.
- Tao ghost pad `src` chua co target.

### `pgie_src_pad_buffer_probe(...)`

- Probe doc metadata de in frame/object count.
- Trong lesson nay, ban can hieu `frame_meta.pad_index` de map frame ve source nao.
- Perf update cung nam o probe nay.

### `main(args, requested_pgie, config, disable_probe)`

- `requested_pgie` va `config` cho phep thay doi inference engine.
- Neu khong truyen gi, sample mac dinh dung `nvinfer` + config co san.
- `streammux` luon di truoc pgie.
- `tiler` di sau pgie.
- `queue` giu pipeline song tot hon.

## Syntax Notes

- `Gst.Bin.new(...)` tao container, khong phai element thong thuong.
- `Gst.GhostPad.new_no_target(...)` tao ghost pad chua co target.
- `set_target(...)` chi xay ra khi callback pad-added bat video NVMM hop le.
- `streammux.request_pad_simple("sink_%u" % i)` tra ve `Gst.Pad`.
- `tiler.set_property("rows", ...)` va `columns` quyet dinh layout output.

## Starter Mapping

### TODO 1: `cb_newpad(...)`

- Check video pad
- Check NVMM
- Gan target vao ghost pad

### TODO 2: `decodebin_child_added(...)`

- Connect child-added cho nested decodebin
- Dat `drop-on-latency` neu co

### TODO 3: `create_source_bin(...)`

- Tao bin
- Tao `uridecodebin`
- Connect signal
- Tao ghost pad

### TODO 4: `pgie_src_pad_buffer_probe(...)`

- Doc batch meta
- In frame/object count
- Update FPS

### TODO 5: `main(...)` setup

- Parse input list
- Khoi tao perf data
- Tao pipeline va source bins

### TODO 6: Batch configuration

- `live-source`
- `batch-size`
- `width`
- `height`
- `batched-push-timeout`

### TODO 7: Layout configuration

- `tiler.rows`
- `tiler.columns`
- `tiler.width`
- `tiler.height`

### TODO 8: Link chain

- `streammux -> queue1 -> pgie -> queue2 -> tiler -> queue3 -> nvvidconv -> queue4 -> nvosd -> queue5 -> sink`

## Mini Checkpoints

- Ban co noi ro dynamic pad khac gi static pad khong?
- Ban co the vi sao source bin phai co ghost pad khong?
- Ban co biet `pad_index` dung de lam gi trong probe khong?
- `tiler` o day la output visualization, khong phai inference, dung khong?
