# Lesson 02 Coding Guide

Lesson nay chuyen trong tam tu "batched infer" sang "batched preprocess + infer".

## Before You Code

- Input: URI list.
- Config: preprocess config file.
- Imports:
  - `configparser`
  - `argparse`
  - `pyds`
  - `PERF_DATA`

## Build Order

1. Viet probe doc ROI/tensor meta.
2. Viet source bin helper.
3. Parse args va config.
4. Tao pipeline, muxer, preprocess, pgie, tiler, sink.
5. Set preprocess config va batch related properties.
6. Link pipeline.
7. Tao bus watch va run.

## Function-By-Function Walkthrough

### `pgie_src_pad_buffer_probe(...)`

- Day la noi doc metadata sau preprocess va sau infer.
- O lesson nay, ban can theo doi `NVDS_PREPROCESS_BATCH_META`.
- Neu co ROI meta, ban co the label/display ROI va frame index.

### `cb_newpad(...)` va `create_source_bin(...)`

- Giong lesson 01.
- Khong thay doi ban chat: van la dynamic source bin + ghost pad.

### `main(...)`

- Them preprocess config.
- Mot so sample co the cho phep `nvinfer` / `nvinferserver`.
- Lesson nay trung thanh voi concept: preprocess tao meta, infer doc meta do.

## Syntax Notes

- `pyds.GstNvDsPreProcessBatchMeta.cast(...)`
  - dung khi muon doc ROI vector.
- `roi_meta.roi.left/top`
  - dung de dat text display len tung ROI.
- `streammux.set_property("batch-size", number_sources)`
  - van la batch cua source plane.
- `nvdspreprocess` co config file rieng, khong phai config cua `nvinfer`.

## Starter Mapping

- `TODO 1`: doc preprocess batch meta
- `TODO 2`: source bin helper
- `TODO 3`: parse args/config
- `TODO 4`: pipeline construct
- `TODO 5`: set preprocess and mux properties
- `TODO 6`: link pipeline
- `TODO 7`: bus/main loop

## Mini Checkpoints

- Ban co phan biet source batch va tensor batch khong?
- ROI count nam o config nao?
- `nvinfer` co preprocess lai sau khi da co tensor meta khong?
- `nvdspreprocess` tao user meta o batch level hay frame level?
