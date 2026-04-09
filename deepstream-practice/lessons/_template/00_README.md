# Lesson Template

Dùng template này khi tạo một lesson mới trong `deepstream-practice/lessons/`.

## Mục tiêu

Mỗi lesson phải dạy theo thứ tự:

1. Hiểu khái niệm và mental model.
2. Đọc hướng dẫn thực hành để biết cần gọi gì và vì sao.
3. Tự code lại từ file khung.
4. Làm thêm bài mở rộng vẫn nằm trong cùng phạm vi bài học.
5. Chỉ đối chiếu đáp án sau khi đã tự thử.

## Cấu trúc bắt buộc

- `01_guide.md`: dạy khái niệm, flow dữ liệu, implementation checklist, failure modes,
  self-check, extensions.
- `02_coding_guide.md`: dạy cách code theo thứ tự viết file, giải thích syntax, hàm
  gọi, giá trị trả về, và bước tiếp theo.
- `03_starter.py`: file khung có `TODO` mang tính triển khai. Người học phải tự viết
  phần vừa học.
- `04_extensions.md`: các bài mở rộng trong cùng boundary của lesson.
- `05_reference.py`: bản chạy được, sạch sẽ, dùng để đối chiếu sau cùng.

## Nguyên tắc viết `01_guide.md`

- Phải có các section: `What you will build`, `Why it matters`, `Mental model`,
  `Implementation checklist`, `Common failure modes`, `Self-check`, `Extensions`.
- Giải thích theo dòng chảy dữ liệu và lifecycle của pipeline, không mô tả mơ hồ.
- Nếu có thể, đối chiếu khái niệm GStreamer nền tảng với docs đã cross-check.
- Dùng ví dụ nhỏ và ngọn; guide không nên biến thành một sample code dài.

## Nguyên tắc viết `03_starter.py`

- Giữ imports và bộ khung app để người học tập trung vào bài học.
- `TODO` phải buộc người học tự lập trình phần vừa học, không chỉ đợi 1-2 dòng.
- `TODO` nên được đánh số hoặc gán nhãn theo `02_coding_guide.md` để người học biết
  mình đang ở bước nào.
- Mỗi `TODO` nên tương ứng với một mốc kỹ thuật rõ ràng:
  tạo element, add/link, bus callback, request pad, probe, overlay...
- File phải hợp lệ về mặt cú pháp để người học có điểm bắt đầu rõ ràng.

## Nguyên tắc viết `02_coding_guide.md`

- Phải dạy theo trình tự code thật sự, không chỉ nhắc lại khái niệm.
- Mỗi block nên trả lời được 5 câu hỏi:
  gọi hàm nào, dùng để làm gì, trả về cái gì ở mức khái niệm, khi nào cần check lỗi,
  và sau dòng đó thường viết gì tiếp.
- Nếu callback có tham số là, phải nói rõ tham số nào được dùng trong lesson.
- Phải có phần map trực tiếp sang từng `TODO` trong `03_starter.py`.
- Người chưa quen syntax Python/GStreamer vẫn phải lần theo được.

## Nguyên tắc viết `04_extensions.md`

- Bắt đầu bằng 2-3 bài mở rộng cơ bản, sau đó mới tới bài nâng hơn.
- Không nhảy sang chủ đề của lesson sau.
- Mỗi extension phải nói rõ: thay đổi gì, quan sát gì, rút ra kết luận gì.

## Nguyên tắc viết `05_reference.py`

- Đây là bản đối chiếu sau cùng, không phải điểm vào chính.
- Code nên sạch hơn bản starter: argument parsing rõ, log tối thiểu, cleanup đầy đủ.
- Không nhét thêm nhiều "mẹo" ngoài phạm vi lesson.
