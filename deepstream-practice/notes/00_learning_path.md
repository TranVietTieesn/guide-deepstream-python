# Learning Path

Tai lieu nay doi sang kieu hoc `guide-first`, nghia la moi chang se di theo thu tu:

1. Doc `01_guide.md` de hieu khai niem va mental model.
2. Doc `02_coding_guide.md` de hieu syntax, ham goi, va thu tu code that su.
3. Tu viet `03_starter.py` theo checklist va walkthrough.
4. Lam `04_extensions.md` de dao sau van trong boundary bai hoc.
5. Cuoi cung moi mo `05_reference.py` de doi chieu.

Tai sao can hoc theo lo trinh nay thay vi nhay thang vao file goc?

Vi `deepstream-test1.py` gop nhieu khai niem cung luc:

- Tao va quan ly pipeline GStreamer.
- Decode video bang plugin NVIDIA.
- Dua frame vao `nvstreammux`.
- Chay suy luan bang `nvinfer`.
- Doc metadata bang `pyds`.
- Ve overlay bang `nvdsosd`.

Neu tach tung lop va buoc ban tu code lai, ban se nho duoc:

- du lieu dang o dang nao tai moi moc
- plugin nao vua bien doi du lieu
- thu tu viet code tu file trong

## Ban do hoc

### Chang 1: Nhan dien bo khung GStreamer

Doc theo thu tu:

- `../lessons/01_gst_bootstrap/01_guide.md`
- `../lessons/01_gst_bootstrap/02_coding_guide.md`
- `../lessons/01_gst_bootstrap/03_starter.py`
- `../lessons/01_gst_bootstrap/04_extensions.md`
- `../lessons/01_gst_bootstrap/05_reference.py`

Muc tieu:

- Hieu `Gst.init()`.
- Hieu `Gst.Pipeline()`.
- Hieu bus message, `GLib.MainLoop()`, `set_state()`.
- Tu lap duoc app toi thieu `filesrc -> fakesink`.

Sau chang nay, ban phai tu tra loi duoc:

- App GStreamer toi thieu can nhung buoc nao?
- Tai sao bus watch va main loop di cung nhau?
- Vi sao cleanup ve `NULL` la mot buoc nghiêm tuc?

### Chang 2: Hieu chuoi input va decode

Doc theo thu tu:

- `../lessons/02_decode_chain/01_guide.md`
- `../lessons/02_decode_chain/02_coding_guide.md`
- `../lessons/02_decode_chain/03_starter.py`
- `../lessons/02_decode_chain/04_extensions.md`
- `../lessons/02_decode_chain/05_reference.py`

Muc tieu:

- Phan biet du lieu nen va frame sau decode.
- Hieu vi sao can `h264parse` truoc `nvv4l2decoder`.
- Tu lap duoc chuoi decode toi thieu.

Sau chang nay, ban phai tu tra loi duoc:

- `filesrc` co hieu H264 khong?
- Parser khac decoder o dau?
- Sau decoder, du lieu dang "giong cai gi"?

### Chang 3: Hieu `nvstreammux`

Doc theo thu tu:

- `../lessons/03_streammux_single_source/01_guide.md`
- `../lessons/03_streammux_single_source/02_coding_guide.md`
- `../lessons/03_streammux_single_source/03_starter.py`
- `../lessons/03_streammux_single_source/04_extensions.md`
- `../lessons/03_streammux_single_source/05_reference.py`
- `../notes/01_pipeline_flow.md`

Muc tieu:

- Hieu vi sao DeepStream van can mux du chi co 1 source.
- Hieu request pad `sink_0`.
- Hieu `batch-size`, `width`, `height`, `batched-push-timeout`.

Sau chang nay, ban phai tu tra loi duoc:

- Tai sao `decoder.get_static_pad("src")` lai link vao
  `streammux.request_pad_simple("sink_0")`?
- Tai sao `nvstreammux` khong chi danh cho multi-source?

### Chang 4: Hieu suy luan voi `nvinfer`

Day van la chang dang theo kieu exercise cu, nhung nen hoc voi tu duy moi:
doc note truoc, tu ve lai pipeline, roi moi mo file code.

Doc va chay:

- `../exercises/04_primary_infer.py`
- `../notes/02_infer_config_breakdown.md`

Muc tieu:

- Biet `config-file-path` noi code voi model.
- Doc duoc cac key chinh trong file config.

### Chang 5: Hieu metadata flow

Doc va chay:

- `../exercises/05_probe_batch_meta.py`
- `../notes/03_metadata_flow.md`

Muc tieu:

- Hieu `Gst.Buffer -> NvDsBatchMeta -> NvDsFrameMeta -> NvDsObjectMeta`.
- Biet ly do dung `hash(gst_buffer)`.
- Biet vi sao phai `.cast()`.

### Chang 6: Hieu overlay

Doc va chay:

- `../exercises/06_osd_overlay_counts.py`

Muc tieu:

- Biet cach cap nhat text overlay.
- Biet cach doi mau bbox theo class.

### Chang 7: Mo rong sang config, multi-source, RTSP

Doc va chay:

- `../exercises/07_config_variants/pgie_trafficcamnet.txt`
- `../exercises/08_multisource_batching.py`
- `../exercises/09_rtsp_source_walkthrough.py`
- `../exercises/10_pipeline_debug_checklist.md`

Muc tieu:

- Hieu batching that su khi co nhieu source.
- Hieu cach doi tu file source sang RTSP.
- Biet tu debug khi pipeline khong ra frame hoac khong co metadata.

## Cach hoc cho tung chang

- Chua mo `05_reference.py` truoc khi ban tu lam `03_starter.py`.
- Neu thay `03_starter.py` qua kho, quay lai `02_coding_guide.md` truoc khi xem dap an.
- Moi lan chi mo rong trong boundary chang dang hoc.
- Ghi lai bang loi cua ban:
  du lieu dang o dang nao, plugin vua lam gi, va neu bo plugin do thi pipeline hong o dau.
- Khi bi ket, quay lai `01_guide.md` va `02_coding_guide.md` thay vi xem dap an ngay.

## Tu hoc de sau hon

- Quay lai `../../deepstream-test1.py` va danh dau tung khoi theo 7 chang o tren.
- Neu ban giai thich duoc tung khoi lon trong file goc bang loi cua minh, luc do
  ban da bat dau "hieu DeepStream", khong chi la copy sample.
