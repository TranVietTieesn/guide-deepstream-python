# Lesson 03 Coding Guide

Lesson nay day ban code theo chieu:

1. batched source side
2. branch split side

## Before You Code

- Input: URI list.
- Output: per-source branches.
- Imports:
  - `PERF_DATA`
  - `pyds`
  - `PlatformInfo`
  - `bus_call`

## Build Order

1. Source bin helper.
2. Batch side setup.
3. Create demux.
4. Create per-source branches.
5. Link batch -> demux.
6. Request demux src pads.
7. Link branch chains.
8. Bus/main loop.

## Function-By-Function Walkthrough

### `create_source_bin(...)`

- Giong lesson 01.
- Lesson nay tap trung vao output split, nen source side co the giu nguyen.

### `main(...)`

- Tao `nvstreamdemux` sau `nvinfer`.
- Moi source branch nen co queue rieng de demux khong bi block.

## Syntax Notes

- `nvstreamdemux.request_pad_simple("src_%u")` la diem then chot.
- Moi branch nen co queue truoc convert/OSD/sink.

## Starter Mapping

- `TODO 1`: source bin helper
- `TODO 2`: branch setup
- `TODO 3`: pad request/link
- `TODO 4`: main pipeline

## Mini Checkpoints

- Ban co phan biet source batching va output splitting khong?
- Branch nao la cho source nao?
- Queue co tac dung gi sau demux?
