# Lesson 05: Probe Batch Meta

Neu ban chua quen syntax Python/GStreamer/DeepStream, doc them
`02_coding_guide.md` truoc khi mo `03_starter.py`.

## What You Will Build

- Pipeline:
`filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> fakesink`
- Expected outcome: dat probe o `nvosd.sink`, doc `NvDsBatchMeta`, di qua
`NvDsFrameMeta` va `NvDsObjectMeta`, in frame/object info ra console

## Why It Matters

Day la bai hoc "metadata xuat hien o dau va doc no the nao".

Day cung la bai noi tiep truc tiep cua lesson 04:

- lesson 04 dung infer pipeline dau tien va cho ban thay `nvinfer` noi voi config ra sao
- lesson 05 giu lai i nfer pipeline do, nhung chuyen trong tam sang viec doc metadata  
thay vi chi nhin output
- `nvinfer` khong chi tao bbox de ve
- no gan metadata vao buffer
- Python DeepStream doc lai metadata nay qua `pyds`

Neu bai nay ro, ban se biet metadata flow that su trong pipeline, thay vi nghi no
la "du lieu tu nhien co san".

## Compared to Lesson 04

Phan duoc giu nguyen tu lesson 04:

- van dung infer pipeline co `nvinfer`
- van can `config-file-path`
- van can `nvstreammux` va pad-level link vao `sink_0`
- van co chuoi `nvinfer -> nvvideoconvert -> nvdsosd`

Phan moi cua lesson 05:

- them `pyds`
- them pad probe callback
- them cach lay `gst_buffer` tu `info`
- them cach lay `NvDsBatchMeta`
- them cach di qua `frame_meta_list` va `obj_meta_list`

Neu lesson 04 day ban "metadata da ton tai sau infer", thi lesson 05 day ban "lam sao
lay no ra va doc no".

## New Concepts In This Lesson

### `pyds`

- Day la Python binding cho cac struct va helper cua DeepStream.
- Bai nay can no de doc `NvDsBatchMeta`, `NvDsFrameMeta`, `NvDsObjectMeta`.

### Pad probe

- Pad probe la callback duoc goi moi khi buffer di qua mot pad ma ban dang theo doi.
- Bai nay dat probe o `nvosd.sink` de doc metadata truoc khi OSD xu ly tiep.

### `gst_buffer`

- Day la buffer GStreamer dang chay trong pipeline.
- Metadata cua DeepStream duoc gan vao buffer nay.

### `NvDsBatchMeta`

- Day la metadata cap cao nhat gan vao buffer.
- Tu day ban di xuong tung frame trong batch.

### `NvDsFrameMeta`

- Chua thong tin tung frame, vi du `frame_num`, `pad_index`, `num_obj_meta`.

### `NvDsObjectMeta`

- Chua thong tin tung object detect duoc, vi du `class_id`, `confidence`, bbox.

### `.cast()`

- `pyds` can cast du lieu ve dung kieu DeepStream truoc khi ban doc field.
- Neu khong cast, ban thuong khong lay duoc `frame_num`, `class_id`, `rect_params`.

## Must Understand Now vs Know For Later

Can hieu ngay o bai nay:

- probe la mot callback chay khi buffer di qua mot pad
- `info.get_buffer()` la diem bat dau de doc metadata
- metadata flow la `BatchMeta -> FrameMeta -> ObjectMeta`
- vi sao probe dat o `nvosd.sink`
- vi sao can `.cast()` va `hash(gst_buffer)`

Chi can biet mat o bai nay, chua can hieu sau:

- toan bo cac loai metadata khac cua DeepStream
- cach OSD dung metadata ben trong
- toan bo API `pyds`

## Mental Model

- `gst_buffer` la buffer GStreamer dang di trong pipeline
- DeepStream gan `NvDsBatchMeta` vao buffer do
- tu `NvDsBatchMeta` ban di xuong `frame_meta_list`
- tu moi frame ban di xuong `obj_meta_list`

Hay lien he voi lesson 04 nhu sau:

- lesson 04 da noi rang metadata bat dau xuat hien sau `nvinfer`
- bai nay la luc ban dung tay doc metadata do thay vi chi biet no "co ton tai"

Pad probe o bai nay dat tai `nvosd.sink` vi:

- frame da qua `nvinfer`
- metadata da ton tai
- nhung chua qua OSD

Ban co the nho theo mot cau don gian:

- infer gan metadata vao buffer
- probe dung lai o mot diem hop ly de doc metadata do

## Metadata Flow In Plain Language

Khi probe duoc goi, hay nghi theo 4 lop:

1. Lay `gst_buffer` tu `info`
2. Lay `batch_meta` tu buffer do
3. Di qua tung `frame_meta` trong batch
4. Di qua tung `obj_meta` trong moi frame

Neu ban thay linked-list la kho, dung co gang nho tat ca mot luc. Hay chi nho:

- 1 buffer
- 1 batch meta
- nhieu frame
- moi frame co nhieu object

## How To Think About The Probe Function

TODO `osd_sink_pad_buffer_probe(...)` la phan de gay ngop nhat bai nay. Hay chia no
thanh cac khoi nho:

### Khoi 1: Lay buffer

- `gst_buffer = info.get_buffer()`
- neu khong co buffer, return ngay

### Khoi 2: Lay batch metadata

- goi `pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))`
- ket qua la diem vao cua metadata tree

### Khoi 3: Di qua frame list

- bat dau tu `batch_meta.frame_meta_list`
- dung `while l_frame is not None`
- cast thanh `NvDsFrameMeta`

### Khoi 4: Di qua object list

- lay `frame_meta.obj_meta_list`
- dung `while l_obj is not None`
- cast thanh `NvDsObjectMeta`

### Khoi 5: In thong tin

- in `frame_num`, `pad_index`, `num_obj_meta`
- in `class_id`, `confidence`, va bbox

### Khoi 6: Return

- ket thuc probe bang `Gst.PadProbeReturn.OK`

Pseudo-code:

```python
lay buffer
neu khong co buffer: return OK

lay batch_meta
lap qua frame list
    cast frame_meta
    in thong tin frame
    lap qua object list
        cast obj_meta
        in thong tin object

return OK
```

## Implementation Checklist

1. Tao pipeline giong lesson 04 nhung dung `fakesink`.
2. Dat `config-file-path` cho `nvinfer`.
3. Dat probe vao `nvosd.get_static_pad("sink")`.
4. Trong probe:
  - lay `gst_buffer`
  - lay `batch_meta` qua `hash(gst_buffer)`
  - lap qua frame list
  - lap qua object list
  - in `frame_num`, `pad_index`, `class_id`, `confidence`, bbox
5. Chay pipeline va quan sat console output.

## Common Failure Modes

- Dat probe qua som:
  co the chua co object metadata.
- `info.get_buffer()` tra ve `None`:
  probe khong co buffer hop le o luc do.
- Quen `.cast()`:
  khong doc duoc Python wrapper dung cho DeepStream struct.
- Quen `hash(gst_buffer)`:
  khong lay dung metadata tu buffer.
- Di nham `frame_meta_list` va `obj_meta_list`:
  ban de loai linked-list nao dang duyet.
- Coi probe nhu mot ham "chay 1 lan":
  thuc te no duoc goi moi khi buffer di qua pad.

## Self-Check

1. Metadata object detection bat dau xuat hien sau plugin nao?
2. Vi sao `gst_buffer_get_nvds_batch_meta(...)` can `hash(gst_buffer)`?
3. Vi sao probe dat o `nvosd.sink` hop ly hon `filesrc.src`?
4. `frame_meta.pad_index` giup ich gi trong bai sau multi-source?

## Extensions

- Dem object theo `class_id`.
- Map `class_id` sang ten label bang labels file.
- Chuyen probe sang diem khac va so sanh metadata co con ton tai khong.
- In them tong object theo moi frame.

