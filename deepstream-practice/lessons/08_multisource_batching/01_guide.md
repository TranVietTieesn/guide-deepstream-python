# Lesson 08: Multi-Source Batching

Neu ban chua quen syntax Python/GStreamer/DeepStream, doc them
`02_coding_guide.md` truoc khi mo `03_starter.py`.

## What You Will Build

- Pipeline:
  `source0 -> parser0 -> decoder0 -> nvstreammux.sink_0`
  `source1 -> parser1 -> decoder1 -> nvstreammux.sink_1`
  `nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> fakesink`
- Expected outcome: thay batching that su khi co nhieu source, va doc
  `frame_meta.pad_index` de biet frame den tu source nao

## Why It Matters

Lesson 03 moi cho ban thay single-source muxing. Bai nay mo rong sang truong hop
DeepStream thuong gap hon: nhieu source vao cung mot muxer.

## Compared to Earlier Lessons

Phan duoc giu nguyen:

- request pad tren `nvstreammux`
- infer pipeline sau muxer
- metadata probe o `nvosd.sink`

Phan moi cua lesson 08:

- co nhieu source branch cung luc
- moi branch can `sink_i` rieng tren muxer
- `batch-size` bay gio that su mang y nghia batching
- `pad_index` tro thanh cach de truy vet frame den tu source nao

Neu lesson 03 day ban "1 source vao muxer the nao", thi lesson 08 day ban "nhieu source
vao cung 1 muxer the nao".

## New Concepts In This Lesson

### Source branch

- Moi source can mot nhanh rieng: `filesrc -> h264parse -> nvv4l2decoder`.
- Moi nhanh duoc tao rieng roi moi noi vao muxer.

### `build_source_branch(...)`

- Day la helper de tranh lap lai code.
- Bai nay dung helper vi logic source bi lap lai nhieu lan.

### `sink_i`

- `nvstreammux` khong tu co san vo han sink pad.
- Ban phai request tung pad cu the nhu `sink_0`, `sink_1`.

### `pad_index`

- Sau khi frame di qua infer, `frame_meta.pad_index` giup biet frame do thuoc source nao.
- Thuong no phan anh index cua branch da duoc noi vao `sink_i`.

### `batch-size`

- O bai 03, `batch-size=1` chi la mot gia tri can set.
- O bai 08, `batch-size` phai doi chieu voi so source de batching hop ly.

## Must Understand Now vs Know For Later

Can hieu ngay o bai nay:

- moi source can branch rieng
- moi branch can request pad rieng tren muxer
- `batch-size` nen bang so source dang dua vao muxer
- `pad_index` la cach de theo doi frame thuoc source nao

Chi can biet mat o bai nay, chua can hieu sau:

- cac chien luoc scheduler phuc tap cua muxer
- partial batch behavior chi tiet
- toi uu hieu nang khi so source tang cao

## Mental Model

- moi source can mot branch rieng: `filesrc -> parser -> decoder`
- moi branch xin mot request pad rieng tren `nvstreammux`
- `pad_index` trong frame meta giup truy vet frame thuoc source nao
- `batch-size` phai khop voi so source de pipeline batching hop ly

Hay nho theo mot cau:

- nhieu source vao nhieu `sink_i`
- muxer gom chung thanh batch
- metadata giu lai dau vet source qua `pad_index`

## Why `pad_index` Matters

Neu khong in `pad_index`, ban biet pipeline dang detect object, nhung khong biet frame do
den tu nhanh nao.

O bai nay, probe khong can in full object list nhu lesson 05. Muc tieu moi la:

- kiem tra batching da xay ra that
- thay moi frame trong batch thuoc source nao

## Config Reminder

Starter cua bai nay dung config trong:

- `exercises/07_config_variants/pgie_trafficcamnet.txt`

Dieu do co nghia:

- bai 07 da tro thanh config anchor cho infer
- lesson 08 tiep tuc dung no khi chuyen sang multi-source
- ban nen nho `batch-size` trong config va `streammux.batch-size` trong code can doi chieu

## Implementation Checklist

1. Parse 2 input path.
2. Tao helper build source branch.
3. Tao muxer + downstream.
4. Dat `batch-size = len(input_paths)`.
5. Add downstream vao pipeline.
6. Lap qua tung source:
   - tao branch
   - add vao pipeline
   - link den decoder
   - xin `sink_i`
   - noi `decoder_i.src -> muxer.sink_i`
7. Dat probe o `nvosd.sink` de in `pad_index`.
8. Chay pipeline.

## Common Failure Modes

- `batch-size` khong khop so source
- request sai ten pad `sink_0`, `sink_1`, ...
- co 1 source hong nhung source con lai lam ban nham la muxer co van de
- khong in `pad_index` nen kho biet frame den tu nhanh nao
- add branch vao pipeline qua muon:
link order bi roi va kho debug source nao chua vao muxer

## Self-Check

1. `pad_index` giup ban biet dieu gi?
2. Vi sao multi-source can request nhieu sink pad tren muxer?
3. Neu co 2 source ma `batch-size=1`, ban se nghi ngo dieu gi truoc?
4. Build source branch thanh helper co loi ich gi?

## Extensions

- Dung cung 1 file cho ca hai source va xem `pad_index` thay doi the nao.
- Doi `batch-size` sai khac voi so source va doc log.
- In tong object theo tung `pad_index`.
- Mo rong thanh 3 source neu may ban du kha nang chay.
