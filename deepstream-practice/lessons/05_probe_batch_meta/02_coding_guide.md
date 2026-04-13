# Lesson 05 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/05_probe_batch_meta/03_starter.py /path/to/sample.h264
```

Day la bai dau tien dung `pyds`, vi vay phan probe quan trong hon phan pipeline.

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `osd_sink_pad_buffer_probe(...)`
4. Tao pipeline giong lesson 04
5. Dat probe vao `nvosd.sink`
6. Chay pipeline

## Function-By-Function Walkthrough

### `osd_sink_pad_buffer_probe(pad, info, user_data)`

Thu tu nen viet:

1. `gst_buffer = info.get_buffer()`
2. neu khong co buffer thi `return Gst.PadProbeReturn.OK`
3. `batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))`
4. `l_frame = batch_meta.frame_meta_list`
5. lap qua frame bang `while l_frame is not None`
6. cast `frame_meta`
7. lap qua `obj_meta_list`
8. cast `obj_meta`
9. in thong tin frame/object
10. `return Gst.PadProbeReturn.OK`

### Vi sao can `.cast()`

`pyds` tra ve wrapper can duoc cast sang kieu DeepStream phu hop:

- `pyds.NvDsFrameMeta.cast(...)`
- `pyds.NvDsObjectMeta.cast(...)`

Neu khong cast, ban khong doc duoc field dung nhu `frame_num`, `class_id`, `rect_params`.

### Vi sao can `hash(gst_buffer)`

DeepStream helper can dia chi/handle cua buffer de lay metadata da gan vao no.
Trong Python, bai nay dung `hash(gst_buffer)` cho muc dich do.

### Dat probe

Dat nhu sau:

```python
osd_sink_pad = nvosd.get_static_pad("sink")
osd_sink_pad.add_probe(
    Gst.PadProbeType.BUFFER,
    osd_sink_pad_buffer_probe,
    None,
)
```

## Starter Mapping

### TODO 1-2

- giong lesson 04

### TODO 3

- hoan thanh probe de doc `gst_buffer`
- lay `batch_meta`
- lap qua frame/object list
- in thong tin ra console

### TODO 4

- tao pipeline va element

### TODO 5

- set property cho source, muxer, pgie, sink

### TODO 6

- add element vao pipeline

### TODO 7-8

- link static chain
- link vao muxer bang pad-level

### TODO 9

- link downstream

### TODO 10

- gan probe vao `nvosd.sink`

## Syntax Notes

- `while l_frame is not None` la pattern pho bien khi di qua DeepStream linked list
- `try/except StopIteration` duoc dung de an toan khi buoc sang node tiep theo
- `rect = obj_meta.rect_params` giup code de doc hon truoc khi in bbox

## Mini Checkpoints

- Sau TODO 3: ban da co probe co the doc metadata
- Sau TODO 8: duong vao muxer da noi xong
- Sau TODO 10: metadata se duoc doc moi khi buffer den `nvosd.sink`
