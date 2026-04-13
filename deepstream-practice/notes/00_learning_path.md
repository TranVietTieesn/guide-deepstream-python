# Learning Path

Tài liệu này đổi sang kiểu học `guide-first`, nghĩa là mỗi chặng sẽ đi theo thứ tự:

1. Đọc `01_guide.md` để hiểu khái niệm và mental model.
2. Đọc `02_coding_guide.md` để hiểu syntax, hàm gọi, và thứ tự code thật sự.
3. Tự viết `03_starter.py` theo checklist và walkthrough.
4. Làm `04_extensions.md` để đào sâu vấn trong boundary bài học.
5. Cuối cùng mới mở `05_reference.py` để đối chiếu.

Tại sao cần học theo lộ trình này thay vì nhảy thẳng vào file gốc?

Vì `deepstream-test1.py` gộp nhiều khái niệm cùng lúc:

- Tạo và quản lý pipeline GStreamer.
- Decode video bằng plugin NVIDIA.
- Đưa frame vào `nvstreammux`.
- Chạy suy luận bằng `nvinfer`.
- Đọc metadata bằng `pyds`.
- Vẽ overlay bằng `nvdsosd`.

Nếu tách từng lớp và bước bạn tự code lại, bạn sẽ nhớ được:

- dữ liệu đang ở dạng nào tại mỗi mốc
- plugin nào vừa biến đổi dữ liệu
- thứ tự viết code từ file trong

## Bản đồ học

### Chặng 1: Nhận diện bộ khung GStreamer

Đọc theo thứ tự:

- `../lessons/01_gst_bootstrap/01_guide.md`
- `../lessons/01_gst_bootstrap/02_coding_guide.md`
- `../lessons/01_gst_bootstrap/03_starter.py`
- `../lessons/01_gst_bootstrap/04_extensions.md`
- `../lessons/01_gst_bootstrap/05_reference.py`

Mục tiêu:

- Hiểu `Gst.init()`.
- Hiểu `Gst.Pipeline()`.
- Hiểu bus message, `GLib.MainLoop()`, `set_state()`.
- Tự lập được app tối thiểu `filesrc -> fakesink`.

Sau chặng này, bạn phải tự trả lời được:

- App GStreamer tối thiểu cần những bước nào?
- Tại sao bus watch và main loop đi cùng nhau?
- Vì sao cleanup về `NULL` là một bước nghiêm túc?

### Chặng 2: Hiểu chuỗi input và decode

Đọc theo thứ tự:

- `../lessons/02_decode_chain/01_guide.md`
- `../lessons/02_decode_chain/02_coding_guide.md`
- `../lessons/02_decode_chain/03_starter.py`
- `../lessons/02_decode_chain/04_extensions.md`
- `../lessons/02_decode_chain/05_reference.py`

Mục tiêu:

- Phân biệt dữ liệu nén và frame sau decode.
- Hiểu vì sao cần `h264parse` trước `nvv4l2decoder`.
- Tự lập được chuỗi decode tối thiểu.

Sau chặng này, bạn phải tự trả lời được:

- `filesrc` có hiểu H264 không?
- Parser khác decoder ở đâu?
- Sau decoder, dữ liệu đang "giống cái gì"?

### Chặng 3: Hiểu `nvstreammux`

Đọc theo thứ tự:

- `../lessons/03_streammux_single_source/01_guide.md`
- `../lessons/03_streammux_single_source/02_coding_guide.md`
- `../lessons/03_streammux_single_source/03_starter.py`
- `../lessons/03_streammux_single_source/04_extensions.md`
- `../lessons/03_streammux_single_source/05_reference.py`
- `../notes/01_pipeline_flow.md`

Mục tiêu:

- Hiểu vì sao DeepStream vẫn cần mux dù chỉ có 1 source.
- Hiểu request pad `sink_0`.
- Hiểu `batch-size`, `width`, `height`, `batched-push-timeout`.

Sau chặng này, bạn phải tự trả lời được:

- Tại sao `decoder.get_static_pad("src")` lại link vào
  `streammux.request_pad_simple("sink_0")`?
- Tại sao `nvstreammux` không chỉ dành cho multi-source?

### Chặng 4: Hiểu suy luận với `nvinfer`

Đọc theo thứ tự:

- `../lessons/04_primary_infer/01_guide.md`
- `../lessons/04_primary_infer/02_coding_guide.md`
- `../lessons/04_primary_infer/03_starter.py`
- `../lessons/04_primary_infer/04_extensions.md`
- `../lessons/04_primary_infer/05_reference.py`
- `../notes/02_infer_config_breakdown.md`

Mục tiêu:

- Biết `config-file-path` nối code với model.
- Hiểu `nvinfer` bắt đầu thêm metadata vào buffer từ đâu.
- Phân biệt phần nào nên sửa trong code, phần nào nên sửa trong config.

### Chặng 5: Hiểu metadata flow

Đọc theo thứ tự:

- `../lessons/05_probe_batch_meta/01_guide.md`
- `../lessons/05_probe_batch_meta/02_coding_guide.md`
- `../lessons/05_probe_batch_meta/03_starter.py`
- `../lessons/05_probe_batch_meta/04_extensions.md`
- `../lessons/05_probe_batch_meta/05_reference.py`
- `../notes/03_metadata_flow.md`

Mục tiêu:

- Hiểu `Gst.Buffer -> NvDsBatchMeta -> NvDsFrameMeta -> NvDsObjectMeta`.
- Biết lý do dùng `hash(gst_buffer)`.
- Biết vì sao phải `.cast()`.

### Chặng 6: Hiểu overlay

Đọc theo thứ tự:

- `../lessons/06_osd_overlay_counts/01_guide.md`
- `../lessons/06_osd_overlay_counts/02_coding_guide.md`
- `../lessons/06_osd_overlay_counts/03_starter.py`
- `../lessons/06_osd_overlay_counts/04_extensions.md`
- `../lessons/06_osd_overlay_counts/05_reference.py`

Mục tiêu:

- Biết cách cập nhật text overlay.
- Biết cách đổi màu bbox theo class.
- Hiểu vai trò của `NvDsDisplayMeta`.

### Chặng 7: Học config như một phần của pipeline

Đọc và thực hành:

- `../exercises/07_config_variants/pgie_trafficcamnet.txt`
- quay lại `../lessons/04_primary_infer/` va thử đổi config

Mục tiêu:

- Hiểu config variant không phải file rời, mà là phần nối trực tiếp với `nvinfer`.
- Biết những key nào nên chỉnh khi test batching và threshold.

### Chặng 8: Hiểu batching thật sự khi có nhiều source

Đọc theo thứ tự:

- `../lessons/08_multisource_batching/01_guide.md`
- `../lessons/08_multisource_batching/02_coding_guide.md`
- `../lessons/08_multisource_batching/03_starter.py`
- `../lessons/08_multisource_batching/04_extensions.md`
- `../lessons/08_multisource_batching/05_reference.py`

Mục tiêu:

- Hiểu batching thật sự khi có nhiều source.
- Đọc `pad_index` để biết frame đến từ source nào.

### Chặng 9: Chuyển từ file source sang RTSP

Đọc theo thứ tự:

- `../lessons/09_rtsp_source_walkthrough/01_guide.md`
- `../lessons/09_rtsp_source_walkthrough/02_coding_guide.md`
- `../lessons/09_rtsp_source_walkthrough/03_starter.py`
- `../lessons/09_rtsp_source_walkthrough/04_extensions.md`
- `../lessons/09_rtsp_source_walkthrough/05_reference.py`

Mục tiêu:

- Hiểu vì sao RTSP thường dùng `uridecodebin` / source bin.
- Hiểu ghost pad và dynamic pad callback.
- Hiểu vì sao `live-source=True` quan trọng.

### Chặng 10: Dùng checklist để debug có hệ thống

Đọc và dùng:

- `../exercises/10_pipeline_debug_checklist.md`

Mục tiêu:

- Biết tự debug khi pipeline không ra frame hoặc không có metadata.
- Có một checklist cố định để quay lại khi bài học khó hơn bắt đầu fail.

## Cách học cho từng chặng

- Chưa mở `05_reference.py` trước khi bạn tự làm `03_starter.py`.
- Nếu thấy `03_starter.py` quá khó, quay lại `02_coding_guide.md` trước khi xem đáp án.
- Mỗi lần chỉ mở rộng trong boundary chặng đang học.
- Ghi lại bằng lời của bạn:
  dữ liệu đang ở dạng nào, plugin vừa làm gì, và nếu bỏ plugin đó thì pipeline hỏng ở đâu.
- Khi bị kẹt, quay lại `01_guide.md` và `02_coding_guide.md` thay vì xem đáp án ngay.

## Tự học để sâu hơn

- Quay lai `../../deepstream-test1.py` và đánh dấu từng khối theo 10 chặng ở trên.
- Nếu bạn giải thích được tung khối lớn trong file gốc bằng lời của mình, lúc đó
  bạn đã bắt đầu "hiểu DeepStream", không chỉ là copy sample.
