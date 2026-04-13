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

