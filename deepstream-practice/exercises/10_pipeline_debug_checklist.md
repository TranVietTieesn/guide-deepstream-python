# Pipeline Debug Checklist

Dùng file này mỗi khi pipeline DeepStream "không chạy như mong đợi". Mục tiêu
không phải là đoán mò phỏng chung chung, mà là một checklist để bạn debug có hệ
thống.

## 1. Source có vào thật không?

- Đường dẫn file / RTSP URI có đúng không?
- Nếu dùng file H264, có cần `h264parse` không?
- Nếu dùng RTSP, source có đang live và cần `uridecodebin` không?

`# TODO`
- In log ngay sau khi set `source.set_property("location", ...)`.
- Thử đổi input bằng một file chắc chắn chạy được.

## 2. Element có tạo được không?

- `Gst.ElementFactory.make(...)` có trả về `None` không?
- Plugin có tồn tại trên máy không?

`# TODO`
- In tên từng element sau khi tạo.
- Nếu một plugin không tạo được, kiểm tra lại môi trường DeepStream.

## 3. Add và link có thành công không?

- Đã `pipeline.add(...)` đầy đủ chưa?
- Mọi `link(...)` có thành công không?
- Nếu dùng `nvstreammux`, đã request đúng `sink_0`, `sink_1`, ... chưa?

`# TODO`
- Check từng bước link, không gộp tất cả vào 1 đoạn "hy vọng nó đúng".
- In rõ tên 2 element trước khi link.

## 4. `nvstreammux` có được cấu hình hợp lý không?

- `batch-size` có khớp số source không?
- `width`, `height` có được set hợp lý không?
- Nếu là source live, đã set `live-source=True` chưa?

`# TODO`
- In giá trị `batch-size`, `width`, `height`, `batched-push-timeout`.
- Giải thích bằng lời của bạn batch đang được tạo ở đâu.

## 5. `nvinfer` có đọc được config không?

- `config-file-path` có đúng không?
- Đường dẫn model / engine / labels trong config có tồn tại không?
- `batch-size` của infer có hợp lý không?

`# TODO`
- In đường dẫn config ra trước khi PLAYING.
- Nếu không có bbox / metadata, nghi ngờ `nvinfer` trước.

## 6. Metadata có xuất hiện không?

- Probe đang đặt ở đâu?
- Tại điểm đó buffer đã qua `nvinfer` chưa?
- `gst_buffer_get_nvds_batch_meta(hash(gst_buffer))` có trả về hợp lý không?

`# TODO`
- Đặt probe ở `nvosd.sink` trước.
- In `frame_num`, `num_obj_meta`, `class_id` để xác nhận metadata tồn tại.

## 7. OSD có vẽ đúng không?

- Đã tạo `NvDsDisplayMeta` từ pool chưa?
- Đã `nvds_add_display_meta_to_frame(...)` chưa?
- Đã đổi màu bbox / text ở đúng chỗ chưa?

`# TODO`
- In `display_text` trước khi add vào frame.
- Thử một text overlay cố định trước, rồi mới làm động.

## 8. Sink có phù hợp không?

- Đang dùng `fakesink` hay sink hiển thị?
- Nếu muốn xem kết quả, sink có đúng nền tảng GPU không?

`# TODO`
- Đổi giữa `fakesink` và sink hiển thị để xác định lỗi nằm ở processing hay render.

## 9. Bus message nói gì?

- Có `ERROR` message không?
- Có `EOS` không?
- Có cần in thêm state transition không?

`# TODO`
- Ghi lại nguyên văn lỗi và debug string.
- Không debug bằng cách "đoán mò"; đọc bus message trước.

## 10. Cách nghĩ khi debug

- Tách nhỏ pipeline.
- Xác nhận từng mốc.
- Mỗi lần chỉ sửa 1 biến.
- Ghi lại giả thuyết trước khi thử.

## SELF-CHECK

- Nếu pipeline chạy nhưng không có bbox, bạn nghĩ 3 điểm nào đầu tiên?
- Nếu multi-source không batching đúng, bạn sẽ check `pad_index` và `batch-size`
  như thế nào?
- Nếu RTSP chạy bất ổn, bạn sẽ nghĩ ngay đến `live-source`, latency, hay source
  bin? Vì sao?
