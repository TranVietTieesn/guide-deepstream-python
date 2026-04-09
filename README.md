# DeepStream Learning Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![GStreamer](https://img.shields.io/badge/GStreamer-1.0-green.svg)](https://gstreamer.freedesktop.org/)
[![DeepStream](https://img.shields.io/badge/NVIDIA-DeepStream-orange.svg)](https://developer.nvidia.com/deepstream-sdk)

> Hệ thống học DeepStream từ cơ bản đến nâng cao - Tự tay xây dựng pipeline AI video analytics

## Giới thiệu

Project này là môi trường học tập toàn diện cho NVIDIA DeepStream SDK, thiết kế theo phương pháp **"guide-first"** - đọc hiểu trước khi code.

### Mục tiêu

- Hiểu toàn bộ pipeline DeepStream hoạt động như thế nào
- Nắm vững vai trò của từng plugin quan trọng (nvstreammux, nvinfer, nvdsosd...)
- Tự tay dựng lại từng đoạn pipeline thay vì chỉ sửa code có sẵn
- Hiểu cách `nvinfer` lấy cấu hình và ảnh hưởng đến kết quả inference
- Làm chủ metadata flow qua pipeline bằng `pyds`

## Cấu trúc Project

```
Deepstream-v2/
├── deepstream-practice/          # Môi trường học chính
│   ├── lessons/                  # Các bài học có cấu trúc
│   │   ├── 01_gst_bootstrap/     # GStreamer cơ bản
│   │   ├── 02_decode_chain/      # Decode pipeline
│   │   ├── 03_streammux_single_source/  # Streammux với 1 source
│   │   └── _template/            # Template tạo lesson mới
│   ├── exercises/                # 10 bài tập từ cơ bản đến nâng cao
│   │   ├── 01_gst_bootstrap.py
│   │   ├── 02_decode_chain.py
│   │   ├── 03_streammux_single_source.py
│   │   ├── 04_primary_infer.py
│   │   ├── 05_probe_batch_meta.py
│   │   ├── 06_osd_overlay_counts.py
│   │   ├── 07_config_variants/
│   │   ├── 08_multisource_batching.py
│   │   ├── 09_rtsp_source_walkthrough.py
│   │   └── 10_pipeline_debug_checklist.md
│   ├── notes/                    # Tài liệu bổ trợ
│   │   ├── 00_learning_path.md
│   │   ├── 01_pipeline_flow.md
│   │   ├── 02_infer_config_breakdown.md
│   │   └── 03_metadata_flow.md
│   └── README.md                 # Hướng dẫn chi tiết cho practice
├── deepstream-test1.py          # File tham chiếu gốc
└── dstest1_pgie_config.txt     # Cấu hình inference mẫu
```

## Format Bài Học

Mỗi lesson trong `lessons/` gồm 5 file theo thứ tự đọc/luyện:

| File | Mục đích |
|------|----------|
| `01_guide.md` | Dạy khái niệm, flow dữ liệu, mental model |
| `02_coding_guide.md` | Dạy syntax, thứ tự gọi hàm, cách check lỗi |
| `03_starter.py` | File bài tập - bạn tự điền code |
| `04_extensions.md` | Bài mở rộng để đào sâu |
| `05_reference.py` | Đáp án tham khảo sau khi tự làm |

## Lộ trình Học Đề Xuất

### Phase 1: Foundation (Lessons)
1. `notes/00_learning_path.md` - Lộ trình tổng quan
2. `lessons/01_gst_bootstrap/` - Hiểu GStreamer basics
3. `lessons/02_decode_chain/` - Xây dựng decode pipeline
4. `lessons/03_streammux_single_source/` - Làm việc với nvstreammux
5. `notes/01_pipeline_flow.md` - Hiểu flow tổng thể

### Phase 2: Inference (Exercises)
6. `exercises/04_primary_infer.py` - Thêm nvinfer
7. `notes/02_infer_config_breakdown.md` - Phân tích cấu hình inference
8. `exercises/05_probe_batch_meta.py` - Đọc metadata với pad probe

### Phase 3: Visualization & Advanced
9. `notes/03_metadata_flow.md` - Hiểu metadata flow sâu hơn
10. `exercises/06_osd_overlay_counts.py` - OSD và đếm objects
11. `exercises/07_config_variants/` - Thử nghiệm cấu hình khác nhau
12. `exercises/08_multisource_batching.py` - Nhiều nguồn cùng lúc
13. `exercises/09_rtsp_source_walkthrough.py` - RTSP streams
14. `exercises/10_pipeline_debug_checklist.md` - Kỹ năng debug

## Yêu Cầu Hệ Thống

- **OS**: Ubuntu 20.04/22.04 (Linux only - DeepStream yêu cầu GPU NVIDIA)
- **GPU**: NVIDIA GPU hỗ trợ CUDA (Turing/Ampere/Hopper trở lên khuyên dùng)
- **DeepStream SDK**: 6.x hoặc 7.x
- **Python**: 3.8+
- **GStreamer**: 1.0
- **CUDA**: 11.x hoặc 12.x

## Cách Học Hiệu Quả

1. **Đọc guide trước**: Mỗi lesson, đọc `01_guide.md` để hiểu khái niệm
2. **Nghiên cứu syntax**: Đọc `02_coding_guide.md` trước khi mở starter
3. **Tự code**: Viết `03_starter.py` theo checklist, không nhìn reference quá sớm
4. **Mở rộng**: Làm `04_extensions.md` để củng cố chiều sâu
5. **Đối chiếu**: Cuối cùng so sánh với `05_reference.py` và `deepstream-test1.py`
6. **Tham khảo notes**: Dùng notes như tài liệu bổ trợ, không là điểm vào chính

## Chạy Bài Tập

```bash
# Ví dụ chạy lesson decode_chain
python3 deepstream-practice/lessons/02_decode_chain/05_reference.py /path/to/sample_1080p_h264.h264

# Ví dụ chạy exercise
python3 deepstream-practice/exercises/04_primary_infer.py /path/to/video.h264
```

## Điều Cần Nhớ

- **DeepStream cần nvstreammux** - Dù chỉ có 1 nguồn cũng phải qua muxer
- **Metadata không tự sinh ra** - Plugin `nvinfer` gắn vào buffer, bạn đọc lại bằng pad probe
- **config-file-path là cầu nối** - Nối code GStreamer với model AI
- **Pad linking vs Element linking** - Từ streammux trở đi phải làm việc ở mức pad

## Tài Nguyên Tham Khảo

- [NVIDIA DeepStream Documentation](https://docs.nvidia.com/metropolis/deepstream/dev-guide/)
- [DeepStream Python API](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Python_Sample_Apps.html)
- [GStreamer Documentation](https://gstreamer.freedesktop.org/documentation/)
- File gốc: `deepstream-test1.py`

## Giấy Phép

Project phục vụ mục đích học tập DeepStream SDK.

---

**Happy Learning!** Chúc bạn chinh phục được DeepStream! 🚀
