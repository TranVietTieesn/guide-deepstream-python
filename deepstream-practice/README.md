# DeepStream Practice

Workspace này được tổ chức lại theo hướng `guide-first`:

1. Đọc `01_guide.md` để hiểu khái niệm và mental model.
2. Đọc `02_coding_guide.md` để biết cần gọi hàm nào, theo thứ tự nào, và vì sao.
3. Tự code lại từ `03_starter.py`.
4. Làm thêm bài mở rộng trong `04_extensions.md`.
5. Chỉ đối chiếu `05_reference.py` sau khi đã tự làm.

Mục tiêu là không chỉ "đọc hiểu một file chạy được", mà là tự tay dựng lại từng
lớp của pipeline DeepStream.

Tham chiếu gốc của bộ bài tập:

- `../deepstream-test1.py`
- `../dstest1_pgie_config.txt`

## Mục tiêu

- Nhìn được toàn bộ pipeline chạy như thế nào.
- Hiểu vai trò của từng plugin DeepStream quan trọng.
- Tự tay dựng lại từng đoạn pipeline thay vì chỉ sửa code có sẵn.
- Hiểu `nvinfer` lấy cấu hình từ đâu và ảnh hưởng ra sao.
- Hiểu metadata đi qua pipeline bằng `pyds`.

## Cấu trúc

- `lessons/`: lesson khép kín theo format `01_guide.md`, `02_coding_guide.md`,
  `03_starter.py`, `04_extensions.md`, `05_reference.py`.
- `notes/`: note bổ trợ giải thích flow, config, metadata bằng tiếng Việt.
- `exercises/`: các file bài tập cũ, giữ lại làm tham chiếu và để đối chiếu trong
  giai đoạn chuyển đổi.

## Lesson Format

Mỗi lesson mới đều có 5 file được đánh số theo thứ tự đọc/luyện:

- `01_guide.md`: dạy khái niệm, flow dữ liệu, implementation checklist, failure modes,
  self-check.
- `02_coding_guide.md`: dạy phần thực hành, syntax, hàm gọi, giá trị trả về, và thứ tự
  viết code trong `03_starter.py`.
- `03_starter.py`: file khung, người học phải tự điền các `TODO` mang tính triển khai.
- `04_extensions.md`: bài mở rộng cơ bản và nâng hơn, nhưng vẫn nằm trong boundary của lesson.
- `05_reference.py`: bản hoàn chỉnh để đối chiếu sau khi đã tự thử.

Nếu bạn muốn tạo lesson mới, tham khảo `lessons/_template/00_README.md`.

## Thứ tự học đề xuất

1. `notes/00_learning_path.md`
2. `lessons/01_gst_bootstrap/01_guide.md`
3. `lessons/01_gst_bootstrap/02_coding_guide.md`
4. `lessons/01_gst_bootstrap/03_starter.py`
5. `lessons/01_gst_bootstrap/04_extensions.md`
6. `lessons/01_gst_bootstrap/05_reference.py`
7. `lessons/02_decode_chain/01_guide.md`
8. `lessons/02_decode_chain/02_coding_guide.md`
9. `lessons/02_decode_chain/03_starter.py`
10. `lessons/02_decode_chain/04_extensions.md`
11. `lessons/02_decode_chain/05_reference.py`
12. `lessons/03_streammux_single_source/01_guide.md`
13. `lessons/03_streammux_single_source/02_coding_guide.md`
14. `lessons/03_streammux_single_source/03_starter.py`
15. `lessons/03_streammux_single_source/04_extensions.md`
16. `lessons/03_streammux_single_source/05_reference.py`
17. `notes/01_pipeline_flow.md`
18. `lessons/04_primary_infer/01_guide.md`
19. `lessons/04_primary_infer/02_coding_guide.md`
20. `lessons/04_primary_infer/03_starter.py`
21. `lessons/04_primary_infer/04_extensions.md`
22. `lessons/04_primary_infer/05_reference.py`
23. `notes/02_infer_config_breakdown.md`
24. `lessons/05_probe_batch_meta/01_guide.md`
25. `lessons/05_probe_batch_meta/02_coding_guide.md`
26. `lessons/05_probe_batch_meta/03_starter.py`
27. `lessons/05_probe_batch_meta/04_extensions.md`
28. `lessons/05_probe_batch_meta/05_reference.py`
29. `notes/03_metadata_flow.md`
30. `lessons/06_osd_overlay_counts/01_guide.md`
31. `lessons/06_osd_overlay_counts/02_coding_guide.md`
32. `lessons/06_osd_overlay_counts/03_starter.py`
33. `lessons/06_osd_overlay_counts/04_extensions.md`
34. `lessons/06_osd_overlay_counts/05_reference.py`
35. `exercises/07_config_variants/pgie_trafficcamnet.txt`
36. `lessons/08_multisource_batching/01_guide.md`
37. `lessons/08_multisource_batching/02_coding_guide.md`
38. `lessons/08_multisource_batching/03_starter.py`
39. `lessons/08_multisource_batching/04_extensions.md`
40. `lessons/08_multisource_batching/05_reference.py`
41. `lessons/09_rtsp_source_walkthrough/01_guide.md`
42. `lessons/09_rtsp_source_walkthrough/02_coding_guide.md`
43. `lessons/09_rtsp_source_walkthrough/03_starter.py`
44. `lessons/09_rtsp_source_walkthrough/04_extensions.md`
45. `lessons/09_rtsp_source_walkthrough/05_reference.py`
46. `exercises/10_pipeline_debug_checklist.md`

## Cách học hiệu quả

- Mỗi lesson, hãy đọc `01_guide.md` trước để hiểu bài học.
- Nếu chưa quen syntax, đọc tiếp `02_coding_guide.md` trước khi mở `03_starter.py`.
- Tự viết `03_starter.py` theo walkthrough và implementation checklist, không nhìn
  `05_reference.py` quá sớm.
- Sau khi chạy được, làm thêm `04_extensions.md` để củng cố bài học đó theo chiều sâu.
- Cuối cùng mới đối chiếu `05_reference.py` và so sánh với `deepstream-test1.py`.
- Dùng `notes/` như tài liệu bổ trợ, không biến nó thành điểm vào chính.

## Gợi ý input

Nhiều lesson và exercise ở đây nhận một đường dẫn đến luồng H264:

```bash
python3 lessons/02_decode_chain/05_reference.py /path/to/sample_1080p_h264.h264
```

Nếu bạn muốn dùng RTSP, học đến `lessons/09_rtsp_source_walkthrough/05_reference.py` trước
khi đổi source.

## Quy ước

- `01_guide.md`: dạy "tại sao" và "nghĩ như thế nào".
- `02_coding_guide.md`: dạy "gọi hàm nào, check gì, dòng tiếp theo là gì".
- `03_starter.py`: file để bạn tự code theo lesson.
- `04_extensions.md`: dạy "đào sâu trong cùng bài học".
- `05_reference.py`: dạy "một đáp án sách để đối chiếu".

## Điều cần nhớ

- DeepStream thường cần `nvstreammux` dù chỉ có 1 nguồn.
- Metadata object detection không "từ dưới đất chui lên"; nó được plugin như
  `nvinfer` gắn vào buffer, và bạn đọc lại bằng pad probe.
- `config-file-path` là điểm nối quan trọng giữa code GStreamer và model AI.
