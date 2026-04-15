# Lesson 03 Coding Guide

Lesson nay co hai truc code chinh:

1. redaction in-place tren object meta
2. crop and save object image

## Before You Code

- Input: URI list.
- Output: redacted live preview va cropped face images.
- Imports:
  - `numpy`
  - `cv2`
  - `pyds`
  - `PERF_DATA`

## Build Order

1. Viet `tiler_sink_pad_buffer_probe(...)`.
2. Viet `crop_object(...)`.
3. Viet source bin helpers.
4. Parse args va tao output folder.
5. Build pipeline va set mux/infer properties.
6. Dat probe tren tiler sink pad.
7. Tao bus watch va perf callback.

## Function-By-Function Walkthrough

### `tiler_sink_pad_buffer_probe(...)`

- Day la noi:
  - duyet frame meta
  - duyet obj meta
  - classify theo object id
  - set rect params de redaction
  - lay image buffer
  - crop face
  - copy sang numpy array
  - save file

### `crop_object(...)`

- Helper cat image theo `rect_params`.
- Vi crop dua tren bbox, can canh bounds va frame format.

### `main(...)`

- Tao `out_crops/stream_<i>`.
- Sample nay khac lesson 01 o cho no co folder I/O workflow.
- `nveglglessink`/`nv3dsink` van giu preview trong khi crop save ra disk.

## Syntax Notes

- `obj_meta.rect_params.has_bg_color = 1`
  - bat che background.
- `pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)`
  - lay image view cua frame.
- `cv2.imwrite(img_path, frame_copy)`
  - save crop/annotated copy.
- `pyds.unmap_nvds_buf_surface(...)`
  - can nho tren Jetson khi buffer duoc map ra CPU.

## Starter Mapping

- `TODO 1`: object/image probe
- `TODO 2`: crop helper
- `TODO 3`: source bin helpers
- `TODO 4`: output folder setup
- `TODO 5`: pipeline creation
- `TODO 6`: link and probe setup

## Mini Checkpoints

- Redaction xay ra tren object meta hay image copy?
- Crop co dung frame goc hay ban copy?
- Tai sao phai co `is_first_obj`?
- Khi nao can `unmap_nvds_buf_surface(...)`?
