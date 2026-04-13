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

## Mental Model

- `NvDsObjectMeta` chua thong tin object va `rect_params`
- ban co the sua `rect_params.border_color` de doi mau bbox
- `NvDsDisplayMeta` dung de tao text overlay
- `nvds_add_display_meta_to_frame(...)` gan display meta vao frame

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
