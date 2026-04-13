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

### `osd_sink_pad_buffer_probe(...)`

Phan nay giong lesson 05, nhung them 3 viec:

1. dem object theo class
2. goi `colorize_object(obj_meta)`
3. tao `display_meta`

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

## Mini Checkpoints

- Sau TODO 4: ban doi duoc mau bbox theo class
- Sau TODO 5: ban tao duoc text overlay theo frame
- Sau TODO 12: overlay da co duong de xuat hien tren frame
