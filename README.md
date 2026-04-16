# DeepStream Learning Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![GStreamer](https://img.shields.io/badge/GStreamer-1.0-green.svg)](https://gstreamer.freedesktop.org/)
[![DeepStream](https://img.shields.io/badge/NVIDIA-DeepStream-orange.svg)](https://developer.nvidia.com/deepstream-sdk)

> Repo học NVIDIA DeepStream theo hướng guide-first: hiểu pipeline, metadata, batching, tracking và message flow bằng cách đọc, tự code, rồi mới đối chiếu reference.

## Tổng quan

Repo này được chia thành hai phần chính:

- `deepstream-practice/`: curriculum học tập đã được biên soạn lại, dùng để học theo lộ trình rõ ràng.
- `apps/`: kho sample app DeepStream Python để tham chiếu implementation và làm nguồn biên soạn lesson.

Mục tiêu của repo là giúp bạn:

- Hiểu cách một pipeline DeepStream được dựng từ GStreamer primitives đến AI video analytics hoàn chỉnh.
- Nắm vai trò của các thành phần quan trọng như `nvstreammux`, `nvinfer`, `nvtracker`, `nvdsanalytics`, `nvmsgconv`, `nvmsgbroker`.
- Làm chủ metadata flow bằng `pyds`, từ object/frame metadata đến custom user meta.
- Luyện tư duy đọc guide, tự triển khai `starter`, rồi mới so sánh với `reference`.

## Cấu trúc hiện tại

```text
Deepstream-v2/
├── apps/                               # Sample app DeepStream Python gốc
├── deepstream-practice/                # Khu vực học chính
│   ├── README.md
│   ├── archive/                        # Bài tập/lesson cũ để đối chiếu
│   ├── lessons/
│   │   ├── beginning/                  # Track nhập môn cốt lõi
│   │   ├── topics/                     # Track nâng cao theo chủ đề
│   │   └── _template/                  # Template tạo lesson mới
│   ├── notes/                          # Tài liệu bổ trợ và roadmap
│   └── solutions/                      # Scratch/solution hỗ trợ luyện tập
└── README.md
```

### `deepstream-practice/` dùng để làm gì?

- `lessons/beginning/`: đường học nền tảng từ GStreamer basics đến batching, metadata và RTSP.
- `lessons/topics/`: các track theo chủ đề để học sâu từng nhóm năng lực.
- `archive/`: nội dung cũ được giữ lại để tham chiếu, không phải entry point chính.
- `notes/`: tài liệu bổ trợ, mapping và roadmap biên soạn.

### `apps/` dùng để làm gì?

`apps/` không phải nơi nên bắt đầu học. Đây là kho sample app để:

- đối chiếu implementation thực tế,
- truy vết pattern pipeline,
- hoặc làm nguồn để tách bài học thành từng stage nhỏ trong `deepstream-practice/`.

## Mô hình bài học

Phần lớn lesson/stage trong curriculum dùng format 5 file:

| File | Vai trò |
| --- | --- |
| `01_guide.md` | Giải thích khái niệm, mental model, flow dữ liệu |
| `02_coding_guide.md` | Chỉ rõ các bước code, API cần dùng, thứ tự lắp pipeline |
| `03_starter.py` | File bạn tự hoàn thiện |
| `04_extensions.md` | Bài mở rộng để đào sâu hoặc biến thể hóa |
| `05_reference.py` | Bản tham chiếu để đối chiếu sau khi tự làm |

## Lộ trình bắt đầu

Nếu bạn mới vào repo, nên đi theo thứ tự này:

1. Đọc `deepstream-practice/README.md`.
2. Mở `deepstream-practice/notes/00_learning_path.md` nếu có trong nhánh làm việc của bạn.
3. Học tuần tự toàn bộ `deepstream-practice/lessons/beginning/`.
4. Sau khi xong phần nền tảng, chuyển sang `deepstream-practice/lessons/topics/00_path.md`.
5. Chọn một topic phù hợp rồi học theo `00_path.md` của topic đó.

Các topic hiện tại gồm:

- `baseline_pipeline`
- `multistream_and_batching`
- `imagedata_and_memory`
- `metadata_and_custom_user_meta`
- `tracking_and_analytics`
- `egress_and_brokering`
- `vision_extensions`

## Cách học hiệu quả

1. Đọc `01_guide.md` trước để hiểu bài toán và mental model.
2. Đọc `02_coding_guide.md` để nắm khung code và các API cần nối.
3. Tự hoàn thiện `03_starter.py` mà chưa nhìn `05_reference.py`.
4. Làm thêm `04_extensions.md` nếu muốn nhớ sâu hơn.
5. Chỉ mở `05_reference.py` sau khi đã tự chạy và tự debug.
6. Khi cần đối chiếu implementation gốc, mới quay sang `apps/`.

## Ví dụ chạy code

```bash
# Ví dụ chạy reference của track beginning
python3 deepstream-practice/lessons/beginning/08_multisource_batching/05_reference.py \
  /path/to/input1.h264 /path/to/input2.h264

# Ví dụ chạy reference ở topic tracking and analytics
python3 deepstream-practice/lessons/topics/tracking_and_analytics/01_tracker_and_sgie/05_reference.py \
  /path/to/video.h264

# Ví dụ mở sample app gốc để đối chiếu
python3 apps/deepstream-test2/deepstream_test_2.py /path/to/video.h264
```

## Yêu cầu hệ thống

- Linux Ubuntu 20.04/22.04 hoặc môi trường tương thích DeepStream.
- NVIDIA GPU hỗ trợ CUDA.
- NVIDIA DeepStream SDK 6.x hoặc 7.x.
- Python 3.8+.
- GStreamer 1.x.
- CUDA phù hợp với bản DeepStream đang dùng.

## Một vài nguyên tắc quan trọng khi học DeepStream

- `nvstreammux` gần như luôn là điểm hợp batch trung tâm, kể cả khi bạn chỉ có một nguồn.
- Metadata không tự xuất hiện trong code Python; nó được plugin DeepStream gắn vào buffer và bạn đọc lại bằng probe qua `pyds`.
- `config-file-path` là cầu nối giữa pipeline code và model/config inference.
- Sau `streammux`, nhiều thao tác sẽ cần làm việc ở mức pad chứ không chỉ `element.link(...)`.
- Đừng học bằng cách copy sample app nguyên khối; repo này được tổ chức để bạn tách nhỏ và hiểu từng bước.

## Tài liệu tham khảo

- [NVIDIA DeepStream Documentation](https://docs.nvidia.com/metropolis/deepstream/dev-guide/)
- [DeepStream Python Sample Apps](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Python_Sample_Apps.html)
- [GStreamer Documentation](https://gstreamer.freedesktop.org/documentation/)