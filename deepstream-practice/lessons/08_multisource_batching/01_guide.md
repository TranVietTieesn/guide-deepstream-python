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

## Mental Model

- moi source can mot branch rieng: `filesrc -> parser -> decoder`
- moi branch xin mot request pad rieng tren `nvstreammux`
- `pad_index` trong frame meta giup truy vet frame thuoc source nao
- `batch-size` phai khop voi so source de pipeline batching hop ly

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
