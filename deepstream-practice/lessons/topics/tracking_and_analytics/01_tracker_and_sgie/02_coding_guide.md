# Lesson 01 Coding Guide

Lesson nay co ba truc code chinh:

1. file decode pipeline
2. tracker + SGIE chain
3. OSD probe doc all meta

## Before You Code

- Input: mot H.264 elementary stream.
- Output: preview co overlay va tracker/SGIE metadata.
- Imports:
  - `configparser`
  - `pyds`
  - `PlatformInfo`
  - `bus_call`
  - `GLib`, `Gst`

## Build Order

1. Viet `osd_sink_pad_buffer_probe(...)`.
2. Parse input args.
3. Tao source, parser, decoder, mux.
4. Tao pgie, tracker, sgie1, sgie2, nvvidconv, nvosd, sink.
5. Read tracker config file.
6. Set pgie/sgie config paths.
7. Link chain.
8. Dat probe o nvosd sink.
9. Tao bus watch va main loop.

## Function-By-Function Walkthrough

### `osd_sink_pad_buffer_probe(...)`

- Day la noi inspect buffer sau khi metadata da day du.
- Ban can:
  - dem object theo class
  - ve display text
  - duyet batch user meta
  - cast past-frame tracking meta neu co

### `main(args)`

- `tracker` khong chay truc tiep neu khong co config dung.
- `sgie1` va `sgie2` duoc dat sau tracker, khong phai sau sink.
- `nvosd` la diem hop ly de probe vi tat ca meta da duoc gom.

## Syntax Notes

- `config = configparser.ConfigParser(); config.read(...)`
  - doc tracker properties tu file.
- `tracker.set_property('ll-lib-file', ...)`
  - low-level tracker library.
- `user_meta.base_meta.meta_type == pyds.NvDsMetaType.NVDS_TRACKER_PAST_FRAME_META`
  - check past-frame meta.
- `pyds.NvDsTargetMiscDataBatch.cast(...)`
  - cast batch past-frame meta.

## Starter Mapping

- `TODO 1`: probe metadata walkthrough
- `TODO 2`: source/decode helper setup
- `TODO 3`: tracker config reading
- `TODO 4`: pipeline construction
- `TODO 5`: link chain and probe attach

## Mini Checkpoints

- Vi sao probe dat o nvosd sink?
- Tracker config doc tu file nao?
- SGIE1 va SGIE2 co vai tro gi trong lesson?
- Past-frame meta nam o batch level hay frame level?
