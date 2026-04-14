# Lesson 06 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/06_osd_overlay_counts/03_starter.py /path/to/sample.h264
```

Day la bai mo rong truc tiep tu lesson 05, nen phan probe se co them:

- bo dem object
- doi mau bbox
- tao `NvDsDisplayMeta`

## What Is Reused vs What Is New

Phan duoc dung lai tu lesson 05:

- infer pipeline
- pad probe o `nvosd.sink`
- `gst_buffer -> batch_meta -> frame_meta -> obj_meta`

Phan moi trong bai nay:

- helper `colorize_object(...)`
- bo dem object theo class
- `NvDsDisplayMeta`
- `text_params`
- `nvds_add_display_meta_to_frame(...)`

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `create_sink(...)`
4. Hoan thanh `colorize_object(...)`
5. Hoan thanh probe
6. Tao pipeline va link giong lesson 04
7. Gan probe vao `nvosd.sink`

## Function-By-Function Walkthrough

### `colorize_object(obj_meta)`

Ham nay nhan `NvDsObjectMeta` va sua truc tiep:

```python
obj_meta.rect_params.border_color.set(r, g, b, a)
```

No khong tra ve gia tri. No thay doi metadata ngay tren object.

Hay coi ham nay la "quy uoc mau theo class".
Nhiem vu cua no la:

1. doc `obj_meta.class_id`
2. chon mau phu hop
3. sua `border_color` ngay tren object

Khong can return vi `obj_meta` da bi sua truc tiep.

### `osd_sink_pad_buffer_probe(...)`

Phan nay giong lesson 05, nhung them 3 viec:

1. dem object theo class
2. goi `colorize_object(obj_meta)`
3. tao `display_meta`

Hay chia probe thanh 5 khoi:

#### Khoi A: Lay buffer va batch meta

Giong lesson 05:

- `gst_buffer = info.get_buffer()`
- `batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))`

#### Khoi B: Duyet frame

Giong lesson 05:

- di qua `frame_meta_list`
- cast `NvDsFrameMeta`

#### Khoi C: Duyet object va dem

Moi khi gap `obj_meta`, ban lam 2 viec:

- tang counter theo `class_id`
- goi `colorize_object(obj_meta)`

Pattern:

```python
obj_counter[obj_meta.class_id] = obj_counter.get(obj_meta.class_id, 0) + 1
colorize_object(obj_meta)
```

#### Khoi D: Tao `display_meta`

Sau khi duyet xong object trong mot frame, moi tao text overlay cho frame do.

### Tao `display_meta`

Mau viet:

```python
display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
display_meta.num_labels = 1
text_params = display_meta.text_params[0]
```

Sau do dien:

- `display_text`
- `x_offset`, `y_offset`
- `font_params.font_name`
- `font_params.font_size`
- `font_params.font_color`
- `set_bg_clr`
- `text_bg_clr`

Va cuoi cung:

```python
pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
```

Hay doc phan nay theo logic:

- acquire meta tu pool
- chon se dung 1 dong text
- lay slot text dau tien
- dien noi dung va style
- gan vao frame

#### Khoi E: Return

Probe van ket thuc bang:

```python
return Gst.PadProbeReturn.OK
```

Vi callback nay khong chan buffer. No chi doc/sua metadata roi cho buffer di tiep.

### Vi sao tao `display_meta` sau khi dem xong object?

Vi text overlay o bai nay phu thuoc vao tong so object cua frame.
Ban phai dem xong truoc, roi moi biet can ghi gi vao `display_text`.

### Vi sao bai nay van dat probe o `nvosd.sink`?

Vi ban muon sua metadata truoc khi `nvdsosd` tieu thu no.
Neu doi mau bbox hoac add text meta sau OSD, frame hien thi co the da bo qua thay doi do.

## How To Debug Overlay Logic

Neu overlay khong dung, debug theo thu tu:

1. Truoc tien, chi in counter ra console
2. Khi counter dung, moi goi `colorize_object(...)`
3. Khi bbox da doi mau, moi tao `display_meta`
4. Khi text da dung, moi dieu chinh font, mau, background

Lam theo thu tu nay de tach bug "logic dem" khoi bug "overlay style".

## Starter Mapping

### TODO 1-3

- `on_message`, `make_element`, `create_sink`

### TODO 4

- doi mau bbox theo class

### TODO 5

- dem object
- colorize object
- tao display meta
- add display meta vao frame
- nen lam theo thu tu: dem -> doi mau -> tao text -> add vao frame

### TODO 6-11

- tao pipeline
- set property
- add element
- link toi decoder
- link vao muxer
- link downstream

### TODO 12

- gan probe vao `nvosd.sink`

## Syntax Notes

- `obj_counter.get(obj_meta.class_id, 0) + 1` la cach Python an toan de dem key
- `text_params = display_meta.text_params[0]` lay slot text dau tien
- `pyds.get_string(...)` co the dung de in display text ra console
- `display_meta.num_labels = 1` can khop voi viec bai nay chi dung 1 dong text

## Mini Checkpoints

- Sau TODO 4: ban doi duoc mau bbox theo class
- Sau TODO 5: ban tao duoc text overlay theo frame
- Sau TODO 12: overlay da co duong de xuat hien tren frame
