# Lesson 06: OSD Overlay Counts

Neu ban chua quen syntax Python/GStreamer/DeepStream, doc them
`02_coding_guide.md` truoc khi mo `03_starter.py`.

## What You Will Build

- Pipeline:
`filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink`
- Expected outcome: dung metadata de doi mau bbox va tao text overlay theo frame

## Why It Matters

Day la bai hoc metadata duoc "visualize" ra sao.

- lesson 05 cho ban doc metadata
- lesson 06 cho ban bien metadata thanh thong tin nhin thay duoc tren frame

Khi lam duoc bai nay, ban hieu ro `nvdsosd` khong tu sinh ra text/bbox; no dua vao
metadata va display meta ma ban chuan bi.

## Compared to Lesson 05

Phan duoc giu nguyen tu lesson 05:

- van dung probe o `nvosd.sink`
- van di theo metadata flow `BatchMeta -> FrameMeta -> ObjectMeta`
- van dung `pyds` de cast va doc metadata

Phan moi trong lesson 06:

- khong chi doc metadata, ma sua metadata
- doi `rect_params.border_color` de bbox doi mau
- tao `NvDsDisplayMeta` de hien text overlay
- add display meta vao frame de `nvdsosd` co cai de ve

Neu lesson 05 day ban "doc metadata", thi lesson 06 day ban "bien metadata thanh thu nhin
thay duoc".

## New Concepts In This Lesson

### In-place metadata update

- `obj_meta` va `frame_meta` khong phai ban sao tam thoi.
- Neu ban sua `rect_params` tren `obj_meta`, `nvdsosd` se nhin thay thay doi do.

### `rect_params.border_color`

- Day la noi de doi mau vien bbox.
- Bai nay dung no de map mau theo `class_id`.

### `NvDsDisplayMeta`

- Day la metadata rieng cho overlay text/shape.
- Ban acquire no tu pool, dien `text_params`, roi gan vao frame.

### `text_params`

- Chua noi dung text, vi tri, font, mau chu, mau nen.
- Bai nay chi dung mot slot text dau tien, nen `num_labels = 1` la du.

## Must Understand Now vs Know For Later

Can hieu ngay o bai nay:

- probe dat truoc `nvdsosd` de ban sua metadata truoc khi OSD ve len frame
- doi mau bbox la sua `obj_meta.rect_params`
- overlay text la them `NvDsDisplayMeta` vao `frame_meta`
- `nvds_add_display_meta_to_frame(...)` la buoc bat buoc de text xuat hien

Chi can biet mat o bai nay, chua can hieu sau:

- nhieu slot `text_params` va `num_labels > 1`
- cac loai display primitives khac ngoai text
- chi tiet pool internals cua DeepStream

## Mental Model

- `NvDsObjectMeta` chua thong tin object va `rect_params`
- ban co the sua `rect_params.border_color` de doi mau bbox
- `NvDsDisplayMeta` dung de tao text overlay
- `nvds_add_display_meta_to_frame(...)` gan display meta vao frame

Hay nho theo thu tu:

- lesson 05: doc metadata
- lesson 06: sua metadata + them display meta
- `nvdsosd`: dung metadata da sua do de ve len frame

## Why Probe Stays On `nvosd.sink`

Day la diem hay bi hieu nham.

Ban dat probe o `nvosd.sink` vi:

- metadata da ton tai sau `nvinfer`
- ban van con o truoc OSD, nen thay doi cua ban con co tac dung
- neu dat sau OSD, phan ve overlay co the da xong roi

Noi ngan gon:

- `nvosd.sink` = diem cuoi cung de chuan bi metadata truoc khi OSD tieu thu no

## How To Think About The Probe

Probe bai nay thuc ra la probe cua lesson 05 cong them 3 khoi moi:

1. dem object theo `class_id`
2. goi `colorize_object(obj_meta)`
3. tao `display_meta` va attach vao frame

Pseudo-code:

```python
lay gst_buffer
lay batch_meta
lap qua frame
    tao bo dem
    lap qua object
        tang bo dem
        doi mau bbox
    tao display_meta
    dien text_params
    add display_meta vao frame
return OK
```

## Implementation Checklist

1. Tao pipeline giong lesson 04.
2. Dat probe o `nvosd.sink`.
3. Trong probe:
  - dem object theo class
  - doi mau bbox theo class
  - acquire `NvDsDisplayMeta`
  - dien `text_params`
  - add display meta vao frame
4. Chay pipeline va quan sat overlay.

## Common Failure Modes

- Chi doi mau bbox ma quen add display meta:
co bbox mau moi nhung khong co text.
- Tao display meta nhung quen `nvds_add_display_meta_to_frame(...)`:
text khong xuat hien.
- Dat probe sai diem:
co the metadata chua san sang.
- Map class sai:
bbox doi mau nham object.
- Quen `num_labels = 1` nhung van viet vao `text_params[0]`:
de doc code thi van co ve hop ly nhung metadata khong duoc dien dung y.
- Nghiem nhien cho rang `nvdsosd` tu tao text:
thuc te `nvdsosd` chi ve nhung gi metadata da chuan bi.

## Self-Check

1. Bbox color duoc doi o dau?
2. Text overlay duoc tao tu `NvDsDisplayMeta` nhu the nao?
3. Vi sao bai nay dat probe o `nvosd.sink` thay vi sau OSD?
4. Neu chi muon overlay cho `person`, ban se sua logic o dau?

## Extensions

- Them dong text moi hien tong so object theo frame.
- Doi mau bbox theo quy tac rieng cua ban.
- Chi hien overlay cho `person`.
- Them mau rieng cho tung class va ghi lai quy uoc mau.

