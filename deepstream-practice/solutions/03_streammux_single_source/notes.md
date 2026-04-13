# Lesson 03: Streammux Single Source - Notes

## Đánh Giá Solution

### ✅ Hoàn Thành Tốt

| TODO | Nội dung | Trạng thái |
|------|----------|------------|
| 1 | Xử lý `EOS` và `ERROR` trong `on_message()` | ✅ Hoàn thành nhưng có lỗi logic |
| 2 | Helper `make_element()` | ✅ Đúng mẫu lesson 02 |
| 3 | Tạo đủ 5 element | ✅ filesrc, h264parse, nvv4l2decoder, nvstreammux, fakesink |
| 4 | Set property | ✅ source.location, streammux config, sink.sync |
| 5 | Add element vào pipeline | ✅ pipeline.add() cho tất cả |
| 6 | Link static chain | ✅ filesrc → h264parse → nvv4l2decoder |
| 7 | Request pad `sink_0` | ✅ Dùng `request_pad_simple()` |
| 8 | Lấy `decoder.src` | ✅ Dùng `get_static_pad("src")` |
| 9 | Link pad-level | ✅ `srcpad.link(sinkpad)` với check `Gst.PadLinkReturn.OK` |
| 10 | Link `streammux → fakesink` | ✅ Dùng `element.link()` |

### 🔴 Lỗi Tìm Thấy

**File:** `solution.py` line 31

```python
elif message == Gst.MessageType.ERROR:  # ❌ SAI
```

Sửa thành:

```python
elif message.type == Gst.MessageType.ERROR:  # ✅ ĐÚNG
```

**Mức độ:** Nghiêm trọng - Error handling không hoạt động, pipeline treo khi có lỗi.

### 📚 Key Learnings

1. **Request Pad vs Static Pad**
   - `nvstreammux` dùng request pad: `streammux.request_pad_simple("sink_0")`
   - `nvv4l2decoder` có static pad: `decoder.get_static_pad("src")`
   - Không thể dùng `decoder.link(streammux)` vì muxer không có sẵn sink pad

2. **API Khác Nhau Ở Mức Pad**
   - Element-level: `element.link(other)` trả về `bool`
   - Pad-level: `srcpad.link(sinkpad)` trả về `Gst.PadLinkReturn`
   - Check thành công: `!= Gst.PadLinkReturn.OK` (khác với `not link`)

3. **Vì Sao Cần `nvstreammux` Dù Chỉ 1 Source**
   - Là entry point chuẩn cho các plugin DeepStream phía sau
   - Tạo batched buffer ngay cả khi `batch-size=1`
   - Chuẩn hóa metadata format cho downstream elements (nvinfer, nvosd...)

### 🎯 Self-Check Answers

1. **Tại sao `nvstreammux` dùng request pad?**
   - Cho phép linh hoạt số lượng source động. Mỗi source cần 1 sink pad riêng (`sink_0`, `sink_1`...).

2. **`get_static_pad` vs `request_pad_simple` khác nhau?**
   - `get_static_pad`: Lấy pad có sẵn của element (decoder.src luôn tồn tại)
   - `request_pad_simple`: Tạo pad mới theo yêu cầu (nvstreammux tạo sink_0 khi được gọi)

3. **Vì sao DeepStream cần mux dù 1 source?**
   - DeepStream SDK thiết kế xung quanh batch processing
   - Muxer chuẩn hóa buffer format, kích thước, timestamp cho toàn bộ pipeline

4. **`width`, `height`, `batched-push-timeout` ý nghĩa gì?**
   - `width/height`: Kích thước output frame sau khi mux (thường resize về 1920x1080)
   - `batched-push-timeout`: Giới hạn thời gian chờ batch đầy trước khi push anyway

### 📖 References

- GStreamer Pad API: https://gstreamer.freedesktop.org/documentation/gstreamer/gstpad.html
- DeepStream Plugin Guide: nvstreammux configuration
