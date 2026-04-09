# Lesson Title

## What You Will Build

- Pipeline:
- Input:
- Expected outcome:

## Why It Matters

- Lesson này nằm ở đâu trong chuỗi DeepStream lớn hơn?
- Sau bài này, người học sẽ tự viết được phần nào?

## Mental Model

- Dữ liệu đang ở dạng nào trước plugin chính?
- Plugin này biến đổi dữ liệu hay chỉ điều phối?
- Control-plane message nào cần theo dõi trên bus?

## Implementation Checklist

1. Kiểm tra input.
2. `Gst.init(None)`.
3. Tạo pipeline và element cần thiết.
4. Set property cần thiết.
5. `pipeline.add(...)`.
6. Link static pads và request pads nếu cần.
7. Tạo bus watch và `GLib.MainLoop()`.
8. `pipeline.set_state(Gst.State.PLAYING)`.
9. Cleanup bằng `Gst.State.NULL`.

## Common Failure Modes

- Input hoặc config không tồn tại.
- `Gst.ElementFactory.make(...)` trả về `None`.
- Link thất bại vì dùng sai pad, sai caps, hoặc thiếu parser.
- Bus không được watch nên app không xử lý `EOS`/`ERROR`.

## Self-Check

- Bạn có thể tự vẽ lại pipeline không?
- Dữ liệu đang ở dạng nào trước/sau plugin chính?
- Nếu bỏ một bước, điều gì sẽ hỏng đầu tiên?

## Extensions

- Extension cơ bản:
- Extension nâng hơn nhưng vẫn trong boundary:
