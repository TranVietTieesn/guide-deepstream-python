# Lesson 01 Coding Guide

Lesson nay co hai truc code chinh:

1. multi-source pipeline + RGBA image access
2. save frame copy bang OpenCV

## Before You Code

- Input: list URI va output folder.
- Output: frame anh duoc save theo stream.
- Imports:
  - `numpy`
  - `cv2`
  - `pyds`
  - `PERF_DATA`
  - `PlatformInfo`

## Build Order

1. Viet `tiler_sink_pad_buffer_probe(...)`.
2. Viet `draw_bounding_boxes(...)` neu sample can annotate.
3. Viet `cb_newpad(...)`, `decodebin_child_added(...)`, `create_source_bin(...)`.
4. Parse args va tao folder output.
5. Tao pipeline, streammux, pgie, nvvidconv1, capsfilter, tiler, nvvidconv, nvosd, sink.
6. Set streammux properties va pgie config.
7. Link source bins vao mux.
8. Dat probe tren tiler sink pad.
9. Tao bus watch, main loop va run.

## Function-By-Function Walkthrough

### `tiler_sink_pad_buffer_probe(...)`

- Day la noi lay frame buffer de xu ly anh.
- Logic:
  - lay batch meta
  - duyet frame meta
  - lay obj meta
  - dem class
  - neu can, lay `nvbufsurface`
  - convert sang numpy copy
  - convert sang format OpenCV
  - save ra file

### `draw_bounding_boxes(...)`

- Helper nay ve mark len image copy.
- Day khong phai bat buoc cho image access, nhung giup nguoi hoc thay ro
  frame nao da duoc annotate.

### `main(...)`

- `nvvidconv1 + capsfilter RGBA` la nut quan trong nhat.
- `platform_info` quyet dinh sink phu hop theo GPU/OS.
- `batched-push-timeout` va `batch-size` van la phan co ban cua multi-source.

## Syntax Notes

- `pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)`
  - lay image data cua tung frame.
- `np.array(n_frame, copy=True, order='C')`
  - copy buffer sang numpy de save.
- `cv2.cvtColor(..., cv2.COLOR_RGBA2BGRA)`
  - chuyen format sang thu cv2 hieu tot hon.
- `saved_count["stream_{}".format(frame_meta.pad_index)]`
  - dem theo stream index, khong phai theo frame number.

## Starter Mapping

- `TODO 1`: frame/image probe
- `TODO 2`: annotation helper
- `TODO 3`: source bin helpers
- `TODO 4`: output folder setup
- `TODO 5`: pipeline creation
- `TODO 6`: link and probe setup

## Mini Checkpoints

- Vi sao phai copy truoc khi save?
- `pad_index` dung de map stream nao?
- Tai sao capsfilter phai yeu cau RGBA?
- `tiler_sink_pad_buffer_probe` co la noi phu hop nhat de access image khong?
