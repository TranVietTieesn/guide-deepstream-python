# Lesson 01: Multi-Source Baseline

Neu ban da hoc `beginning` va `baseline_pipeline`, lesson nay la buoc chuyen quan
trong sang multi-source DeepStream.

## What You Will Build

- Data path:
  `uridecodebin(source bin) -> nvstreammux -> queue -> nvinfer -> queue -> nvmultistreamtiler -> queue -> nvvideoconvert -> queue -> nvdsosd -> queue -> sink`
- Input: mot hoac nhieu URI H.264/H.265, co the la file hoac RTSP
- Expected outcome: hieu cach DeepStream ghep nhieu source vao batch va composite
  chung thanh mot tiled output

## Why It Matters

Day la lesson quan trong nhat trong topic nay vi no chuyen ban tu "single stream"
sang "multiple streams batched".

- `nvstreammux` khong con chi la mot hop ky thuat nhu lesson baseline
- Ban phai nghi theo source bin, ghost pad, batch size, live source, va tiler
- Multi-source DeepStream khong con la "moi source noi truc tiep vao pipeline"

Neu lesson nay ro, cac lesson sau chi la cac bien the cua cung tu duy:

- preprocess chen vao truoc infer
- demux tach batch ra thanh tung nhánh
- RTSP in/out thay input/output layer

## Compared to `baseline_pipeline`

Phan giu nguyen:

- `nvinfer`
- `nvdsosd`
- bus watch va cleanup
- tu duy pipeline + metadata

Phan moi:

- `uridecodebin`
- source bin
- dynamic pad callback
- ghost pad
- `nvstreammux` voi nhieu source
- `nvmultistreamtiler`
- queue chain de dam bao throughput va stream isolation

Lesson baseline day ban cach đi từ 1 source sang sink.
Lesson nay day ban cach đi từ N source sang 1 batch va quay lai 1 tile grid.

## New Concepts In This Lesson

### `uridecodebin`

- Decodebin tu dong tim demux/decode chain phu hop.
- It can plug file hoac RTSP source, container format va codec khac nhau.

### Source bin

- Mot `Gst.Bin` boc logic source thanh 1 khung.
- Ben ngoai, pipeline chi thay mot `src` pad.

### Dynamic pad

- `uridecodebin` tao pad dong khi no da biet media type.
- Callback `pad-added` quyet dinh co cho pad nay di vao source bin hay khong.

### Ghost pad

- Ghost pad la "cong ra ben ngoai" cua source bin.
- No giup `main(...)` khong phai biet chi tiet ben trong source bin.

### `nvstreammux`

- Gom frame tu nhieu source thanh batch.
- Moi source can mot request pad rieng `sink_0`, `sink_1`, ...

### `nvmultistreamtiler`

- Sau infer, tiler sap xep frame batched thanh mot man hinh nhieu o.
- Day la phan giup nguoi hoc "nhin thay" batched processing.

## Mental Model

### Data flow

1. Moi URI di vao mot source bin rieng.
2. `uridecodebin` sinh pad dong.
3. Callback bat pad video NVMM hop le va gan vao ghost pad.
4. Ghost pad noi vao `nvstreammux`.
5. `nvstreammux` bat frame tu nhieu source thanh batch.
6. `nvinfer` chay theo batch.
7. `nvmultistreamtiler` lay frame tu batch va xep thanh grid.
8. `nvdsosd` ve overlay.

### Control flow

- Neu source la RTSP, muxer can hieu day la live source.
- Bus va main loop van giong cac lesson truoc.
- Difference chi nam o phan source handling va batch orchestration.

### Batch thinking

- Lesson nay khong con lam viec voi "mot frame = mot output" nua.
- Ban phai nghi theo:
  - source index
  - pad index
  - batch size
  - tile position

## Implementation Checklist

1. Parse input URI list.
2. Tao `PERF_DATA`.
3. Tao pipeline va `nvstreammux`.
4. Tao source bin cho tung URI.
5. Gan `pad-added` va `child-added` callback.
6. Xin request pad tu muxer va link source bin vao muxer.
7. Tao queue chain, pgie, tiler, nvvidconv, nvosd, sink.
8. Set `live-source=True` neu co it nhat 1 RTSP source.
9. Set batch size theo so source.
10. Add probe vao `pgie.src` neu khong disable probe.
11. Tao bus watch, main loop, PLAYING, cleanup.

## Common Failure Modes

- Decodebin sinh pad audio ma ban link nham.
- Decodebin khong chon NVMM decoder.
- Ghost pad khong duoc set target.
- `nvstreammux` batch-size khong khop so source.
- Quen set `live-source=True` khi co RTSP source.
- Tiler grid size khong phu hop so source.

## Self-Check

- Ban co the giai thich vi sao source bin can ghost pad khong?
- Ban co biet khi nao phai dung `request_pad_simple("sink_%u")` khong?
- `nvstreammux` co nhan mot source hay nhieu source trong lesson nay?
- `nvmultistreamtiler` đang lam gi khac voi `nvdsosd`?

## Extensions

- Thu them 1 RTSP source vao danh sach input.
- Thu `--file-loop` va quan sat hanh vi live/file.
- Doi `batch-size` va xem tiler grid thay doi nhu the nao.
- Bo probe va so sanh khoi luong log.
