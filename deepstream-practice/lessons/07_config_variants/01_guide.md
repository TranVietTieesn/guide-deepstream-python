# Lesson 07: Config Variants

## What You Will Build

- Không viết code mới. Sử dụng lại các bài 04, 05, hoặc 06.
- Input: File config `pgie_trafficcamnet.txt` đã được chú thích.
- Expected outcome: Hiểu cách điều chỉnh config ảnh hưởng đến inference và output visualization.

Day khong phai la noi dau tien ban gap file config.
Lesson 04 da gioi thieu `config-file-path` va vai tro cua `dstest1_pgie_config.txt`.
Bai nay la luc ban quay lai config de tune co chu dich.

## What Is New In This Lesson

Phan khong moi:

- infer pipeline code
- `config-file-path`
- `streammux`
- `nvinfer`

Phan moi:

- doi truc tiep tham so trong file config
- chay lai cung mot pipeline voi config khac nhau
- hoc trade-off giua recall, precision, overlap handling, va batching

Neu lesson 04 day ban "config duoc noi vao code the nao", thi lesson 07 day ban "thay doi
config thi output doi ra sao".

## Suggested Workflow

Hay lam bai nay theo dung thu tu, thay vi sua ngau nhien nhieu dong cung luc:

1. Chon mot pipeline da chay on tu lesson 04, 05, hoac 06.
2. Chay voi config mac dinh truoc.
3. Chon duy nhat 1 tham so de doi.
4. Chay lai va ghi nhan thay doi.
5. Mới chuyen sang tham so tiep theo.

Neu ban sua 3-4 tham so cung luc, bai nay se mat y nghia "config lab".

## Why It Matters

- DeepStream pipeline không chỉ là code Python - phần lớn behavior nằm trong config.
- Sau bài này, bạn sẽ biết cách tune inference mà không cần động vào code.
- Hiểu `batch-size` trong config phải match với `streammux batch-size`.
- Noi cach khac: lesson 04 day ban "config duoc noi vao code the nao", con lesson 07 day
  ban "doi config thi output thay doi ra sao".

## Mental Model

### Trước khi đọc config

- Bạn chạy pipeline với config mặc định.
- Bạn không biết tại sao lại detect được/miss object.
- Bạn da biet `config-file-path` duoc set trong lesson 04, nhung chua khai thac het y
  nghia cua tung tham so.

### Tại file config

- Mỗi tham số control một khía cạnh của inference.
- `pre-cluster-threshold`: Lọc detection yếu trước khi cluster.
- `nms-iou-threshold`: Xử lý bbox overlap.
- `topk`: Giới hạn candidate trước khi xuất output.

### Sau khi tune config

- Cùng một pipeline code, nhưng output khác biệt rõ rệt.
- Hiểu trade-off giữa precision và recall.

Hay nho theo mot cau:

- code pipeline la khung
- config quyet dinh infer behavior
- lesson 07 la bai de nhin ro anh huong cua config len ket qua

## Config Parameters Walkthrough

### `[property]` Section

| Parameter | Giá trị | Ý nghĩa |
|-----------|---------|----------|
| `gpu-id` | 0 | Chạy trên GPU 0 |
| `net-scale-factor` | 0.0039... | 1/255.0 cho normalization |
| `onnx-file` | path | Model gốc dạng ONNX |
| `model-engine-file` | path | Engine TensorRT đã optimize |
| `batch-size` | 1 | Match với streammux batch-size |
| `network-mode` | 2 | 0=FP32, 1=INT8, 2=FP16 |
| `interval` | 0 | Infer mọi frame (0 = không skip) |
| `gie-unique-id` | 1 | ID cho primary GIE |
| `cluster-mode` | 2 | 2 = NMS algorithm |

### `[class-attrs-all]` Section

| Parameter | Giá trị | Ý nghĩa |
|-----------|---------|----------|
| `pre-cluster-threshold` | 0.2 | Confidence threshold (càng cao = càng strict) |
| `topk` | 20 | Số detection candidate tối đa |
| `nms-iou-threshold` | 0.5 | IoU threshold cho NMS (càng cao = giữ nhiều overlap) |

## Implementation Checklist

1. Copy `pgie_trafficcamnet.txt` vào thư mục bài tập.
2. Chọn một pipeline từ bài 04, 05, hoặc 06.
3. Chạy pipeline với config mặc định, ghi nhận output.
4. Thay đổi từng parameter theo TODO trong file.
5. Quan sát và so sánh kết quả.

Nho rang anchor quan trong nhat tu lesson 04 van giu nguyen:

- code set `config-file-path`
- `streammux` co `batch-size` ben phia pipeline
- PGIE config cung co `batch-size` ben phia infer

## How To Read The TODOs In The Config

Trong file `pgie_trafficcamnet.txt`, TODO khong bat ban viet code moi.
No dang goi y cho ban cac thuc nghiem:

- doi `pre-cluster-threshold` de xem output sach hon hay bi miss object
- doi `topk` de xem candidate bi cat bot nhu the nao
- doi `nms-iou-threshold` de xem overlap handling thay doi ra sao
- doi `batch-size` khi hoc multi-source de doi chieu voi muxer

## Common Failure Modes

- `batch-size` không match với streammux: Pipeline vẫn chạy nhưng không optimal.
- Đổi `pre-cluster-threshold` quá cao: Miss nhiều object, đặc biệt object nhỏ/xa.
- Đổi `topk` quá thấp: Mất detection khi có nhiều object trong frame.
- Sai `network-mode`: Model chạy chậm hoặc không chính xác.

## Self-Check

1. `batch-size=1` trong config phải match với gì trong code?
2. `pre-cluster-threshold=0.2` nghĩa là gì? Thử đổi thành 0.4 sẽ thấy gì?
3. `nms-iou-threshold` cao hơn sẽ giữ lại nhiều bbox hơn hay ít hơn?
4. `topk=20` ảnh hưởng khi nào? (gợi ý: crowded scenes)

## Extensions

### Cơ bản

1. Thử `pre-cluster-threshold` các giá trị: 0.1, 0.2, 0.4, 0.6.
   - Quan sát: số lượng detection và độ chính xác.
2. Thử `topk`: 5, 10, 20, 50.
   - Quan sát: crowded scene vs sparse scene.
3. Thử `nms-iou-threshold`: 0.3, 0.5, 0.7.
   - Quan sát: overlap handling.

### Nâng hơn

1. Chuyển `network-mode` từ FP16 sang INT8 (nếu có calib file).
   - Quan sát: speed vs accuracy trade-off.
2. Thay đổi `interval` thành 2 (infer mỗi 3 frame).
   - Quan sát: FPS tăng nhưng tracking có thể giật.
3. Tìm hiểu thêm `scaling-filter` và `scaling-compute-hw`.
