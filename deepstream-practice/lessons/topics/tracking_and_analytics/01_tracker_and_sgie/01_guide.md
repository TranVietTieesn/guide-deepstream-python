# Lesson 01: Tracker and SGIE

Lesson nay la buoc tiep theo sau `baseline_pipeline`: ban khong chi infer,
ma con track object va chay secondary inference theo object.

## What You Will Build

- Data path:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvtracker -> nvinfer(sgie1) -> nvinfer(sgie2) -> nvvideoconvert -> nvdsosd -> sink`
- Input: mot H.264 elementary stream
- Output: frame co bbox, text overlay, tracker state, va secondary classifier meta

## Why It Matters

Day la mau hinh production co ban cua object intelligence:

- detector tim object
- tracker giu object identity qua frames
- secondary inference them thuoc tinh chi tiet

Neu ban hieu lesson nay, ban se hieu:

- object_id khac class_id
- tracker khong phai detector
- SGIE khong phai detector moi, ma la classifier theo object roi
- meta co the tiep tuc di xuong pipeline va duoc doc o probe cuoi

## Compared to `baseline_pipeline`

Phan giu nguyen:

- file source decode chain
- `nvstreammux`
- primary inference
- `nvdsosd`
- bus/main loop

Phan moi:

- `nvtracker`
- multiple `nvinfer` instances
- config file reading
- past-frame tracker meta
- object-level and frame-level metadata together

Lesson baseline day ban infer 1 lan.
Lesson nay day ban infer + track + refine object properties.

## New Concepts In This Lesson

### `nvtracker`

- Giu object identity qua frames.
- Cho phep ban giam sat object theo thoi gian, khong chi theo frame hien tai.

### SGIE

- Secondary inference chay sau detector/tracker.
- Thuong dung de phan loai make/type, attribute, subtype, va similar.

### Past-frame meta

- Tracker co the emit meta ve qua khu cua object.
- Day la data rich hon object list co ban.

### Metadata fan-out

- Mot frame co the mang:
  - frame meta
  - object meta
  - tracker past-frame meta
  - SGIE meta

## Mental Model

### Data flow

1. Detector tao object meta.
2. Tracker gan object_id va state.
3. SGIE1 doc object roi de phan loai make.
4. SGIE2 doc object roi de phan loai type.
5. OSD in text/count len frame.
6. Sink hien thi ket qua tong hop.

### Control flow

- Tracker config quyet dinh tracker algorithm va memory model.
- SGIE config quyet dinh model/labels/classifier operation.
- Probe dat o nvosd sink de doc duoc tat ca metadata da hoan chinh.

## Implementation Checklist

1. Parse input file path.
2. Tao pipeline source -> parser -> decoder -> mux.
3. Tao pgie, tracker, sgie1, sgie2, nvvidconv, nvosd, sink.
4. Doc tracker config bang `configparser`.
5. Set pgie/sgie config-file-path.
6. Link chain theo thu tu sample.
7. Dat probe tren nvosd sink pad.
8. Trong probe, doc frame/object/tracker meta.

## Common Failure Modes

- Quen set tracker config properties tu file.
- SGIE batch-size khong khop voi input object batch.
- Doc nham object_id va class_id.
- Quen probe dat cuoi pipeline nen meta chua day du.
- Doc tracker past-frame meta ma khong check meta_type.

## Self-Check

- Tracker lam gi khac detector?
- SGIE dat truoc hay sau tracker?
- Object_id va class_id khac nhau nhu the nao?
- Vi sao probe cuoi pipeline lai doc duoc nhieu loai meta hon?

## Extensions

- Doi tracker config va quan sat object_id.
- Thay doi sgie config de thay labels khac.
- Thu phan tich past-frame meta.
