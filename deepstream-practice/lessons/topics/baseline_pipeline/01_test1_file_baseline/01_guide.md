# Lesson 01: File Baseline

Neu ban chua quen syntax Python/GStreamer, doc them `02_coding_guide.md` truoc
khi mo `03_starter.py`.

## What You Will Build

- Pipeline:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink`
- Input: mot file H.264 elementary stream
- Config: `apps/deepstream-test1/dstest1_pgie_config.txt`
- Expected outcome: hieu baseline DeepStream sample theo duong di tu file source
  cho toi infer + OSD + render

## Why It Matters

Day la level dau tien trong topic `baseline_pipeline`, nhung no khong con la "GStreamer
toy example" nua.

- Ban van dung khung GStreamer co ban tu `beginning`
- Nhung lan nay khung do da gan voi sample DeepStream that su
- `nvinfer` vao pipeline qua config, khong phai hard-code model trong code
- `nvdsosd` su dung metadata sinh ra boi infer de ve ket qua len frame

Neu lesson nay ro, cac lesson sau chi la thay source, thay output, hoac chen them
mot bridge hop ly vao cung skeleton.

## Compared to `beginning`

Phan duoc giu nguyen tu cac bai dau:

- `Gst.init(None)`
- tao pipeline, add/link element
- bus watch, `GLib.MainLoop()`
- cleanup ve `NULL`

Phan moi cua topic nay:

- co `nvinfer` va file config that
- co `nvdsosd` thay vi chi dung sink "trong"
- co use case hoc thuc te, khong chi hoc syntax thuoc long

Neu `beginning` day ban cach "lap pipeline", thi lesson nay day ban "pipeline do
phuc vu mot app DeepStream co y nghia gi".

## New Concepts In This Lesson

### `nvinfer`

- Plugin chay inference tren GPU/TensorRT.
- Day la noi object detection metadata duoc gan vao buffer.
- Trong lesson nay, ban chua can tune model, chi can hieu no la "AI step"
  trong chuoi.

### `config-file-path`

- Python code khong can hard-code model details.
- `nvinfer` doc config file va tu do biet model, labels, batch-size, threshold,
  engine file...
- Day la mot trong nhung y tuong quan trong nhat cua DeepStream: code mo ta luong,
  config mo ta model.

### `nvdsosd`

- OSD la noi metadata object detection duoc bien thanh overlay.
- No khong tao detection moi.
- No chi "doc" metadata san co va ve len frame.

### `nvstreammux` voi 1 source

- Du chi co 1 source, `nvstreammux` van can co mat vi DeepStream lam viec theo
  batch-centric model.
- Bui hoc o day la: single source khong co nghia la bo qua muxer.

### `PlatformInfo`

- Helper nay chi chon sink phu hop platform.
- No khong tham gia data plane.
- Nghia la ban khong hoc them AI o day, ban hoc cach viec render phu thuoc
  vao platform.

## Mental Model

### Data plane

1. `filesrc` doc byte.
2. `h264parse` lam stream de decoder hieu ro hon.
3. `nvv4l2decoder` bien H.264 thanh frame.
4. `nvstreammux` chuyen frame don le thanh duong di DeepStream co batch semantics.
5. `nvinfer` gan object metadata len buffer.
6. `nvvideoconvert -> nvdsosd` chuan bi frame va ve overlay.
7. `sink` hien thi ket qua cuoi cung.

### Control plane

- Bus message van la noi app biet pipeline co `EOS` hay `ERROR`.
- `GLib.MainLoop()` khong xu ly video, no giup app song du de nghe message.
- `PLAYING` va `NULL` la lifecycle cua pipeline, khong phai cua model.

### Data shape theo chieu doc

- Truoc decoder: byte stream
- Sau decoder: frame
- Sau muxer: batched frame
- Sau infer: frame + metadata
- Sau OSD: frame da ve overlay

## Implementation Checklist

1. Parse input file va kiem tra ton tai.
2. `Gst.init(None)` va tao `PlatformInfo()`.
3. Tao pipeline, source, parser, decoder, mux, pgie, `nvvideoconvert`, `nvdsosd`, sink.
4. Set `location`, `batch-size`, `width`, `height`, `batched-push-timeout`,
   va `config-file-path`.
5. `pipeline.add(...)` tat ca element.
6. Link static chain `filesrc -> h264parse -> nvv4l2decoder`.
7. Xin `sink_0` tu `nvstreammux` va lay `decoder.src`.
8. Link pad-level `decoder.src -> streammux.sink_0`.
9. Link downstream `streammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink`.
10. Gan pad probe vao sink pad cua `nvdsosd` de doc object metadata.
11. Tao bus watch va `GLib.MainLoop()`.
12. Dua pipeline sang `PLAYING` va cleanup ve `NULL`.

## Common Failure Modes

- File khong phai H.264 elementary stream.
- Quen set `config-file-path` cho `nvinfer`.
- Quen xin request pad tu `nvstreammux`.
- Link sai cap do element vs pad.
- Quen gan probe vao `nvdsosd` neu muon doc metadata.
- Bus khong co watch nen app khong dung dung khi co `ERROR`.

## Self-Check

- Ban co the ve lai pipeline va chi ro doi tuong nao la frame, doi tuong nao la
  metadata khong?
- Neu bo `nvinfer`, `nvdsosd` con co gi de ve khong?
- Neu bo `nvstreammux`, viec noi sang `nvinfer` co con theo tu duy DeepStream
  khong?
- Sau `nvinfer`, metadata xuat hien o pad nao neu ban dat probe?

## Extensions

- Doi input sang file khac va quan sat thay doi object count.
- In them `STATE_CHANGED` cua pipeline.
- Thay `sink` bang `fakesink` de tap trung vao data/control flow.
- Thu bo `nvdsosd` va ghi lai vi sao lesson mat mat nguon su dung metadata.
