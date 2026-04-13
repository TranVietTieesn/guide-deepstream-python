# Infer Config Breakdown

File gốc `../../dstest1_pgie_config.txt` là nơi `nvinfer` đọc để biết:
- model nào được dùng,
- engine nào được nạp,
- có bao nhiều class,
- cách lọc và clustering bbox sau suy luận.

Trong code, điểm nối giữa pipeline và model là:

```python
pgie.set_property("config-file-path", "dstest1_pgie_config.txt")
```

Nếu không hiểu file config nay, bạn sẽ thấy `nvinfer` giống như hộp đen.

## Các key chính trong file hiện tại

### `onnx-file`

Giá trị hiện tại:
- `../../../../samples/models/Primary_Detector/resnet18_trafficcamnet_pruned.onnx`

Ý nghĩa:
- Đường dẫn đến model ONNX gốc.
- Thường được dùng khi cần build TensorRT engine lần đầu.

### `model-engine-file`

Giá trị hiện tại:
- `../../../../samples/models/Primary_Detector/resnet18_trafficcamnet_pruned.onnx_b1_gpu0_fp16.engine`

Ý nghĩa:
- Engine TensorRT đã tối ưu sẵn cho GPU / precision / batch-size cụ thể.
- Nếu engine phù hợp đã tồn tại, DeepStream có thể nạp nhanh hơn so với build lại
  từ model gốc.

### `labelfile-path`

Giá trị hiện tại:
- `../../../../samples/models/Primary_Detector/labels.txt`

Ý nghĩa:
- Mapping `class_id -> tên class`.
- Giá trị này rất quan trọng khi bạn muốn in log để người đọc hiểu được.

### `batch-size`

Giá trị hiện tại:
- `1`

Ý nghĩa:
- Số frame được infer cùng lúc.
- Thuong cần đồng bộ voi batch mà `nvstreammux` tạo ra.

### `network-mode`

Giá trị hiện tại:
- `2`

Theo docs DeepStream, các giá trị phổ biến:
- `0`: FP32
- `1`: INT8
- `2`: FP16

Ý nghĩa:
- Chọn precision cho suy luận.
- Precision ảnh hưởng đến tốc độ, memory và độ chính xác.

### `num-detected-classes`

Giá trị hiện tại:
- `4`

Ý nghĩa:
- Số class detector sẽ output.
- Cần phù hợp với model và labels.

### `interval`

Giá trị hiện tại:
- `0`

Ý nghĩa:
- Tần suất bỏ qua frame infer.
- `0` nghĩa là infer mỗi frame.

### `gie-unique-id`

Giá trị hiện tại:
- `1`

Ý nghĩa:
- ID để phân biệt engine này với engine khác trong pipeline.
- Rat quan trọng khi sau này có thêm tracker, SGIE hoặc custom metadata.

### `cluster-mode`

Giá trị hiện tại:
- `2`

Theo docs DeepStream:
- `0`: GroupRectangles
- `1`: DBSCAN
- `2`: NMS
- `3`: Hybrid
- `4`: Khong clustering

Ý nghĩa:
- Cac candidate bbox từ model cần được gom / lọc sau suy luận.
- `2` thường là NMS, rất phổ biến cho detector.

### `pre-cluster-threshold`

Giá trị hiện tại:
- `0.2`

Ý nghĩa:
- Lọc bỏ bbox confidence thấp trước khi clustering / NMS.
- Tăng giá trị này thì output thường sạch hơn nhưng dễ miss object hơn.

### `topk`

Giá trị hiện tại:
- `20`

Ý nghĩa:
- Giữ lại tối đa bao nhiêu candidate trước / trong bước lọc tiếp theo.

### `nms-iou-threshold`

Giá trị hiện tại:
- `0.5`

Ý nghĩa:
- Ngưỡng giao nhau để NMS quyết định giữ hoặc bỏ bbox trùng lặp.

## Mối liên hệ giữa config và hành vi runtime

- `deepstream-test1.py` tạo `nvinfer`.
- `nvinfer` đọc `config-file-path`.
- Config quyet dinh model và cách post-process.
- Sau đó `nvinfer` gắn `NvDsObjectMeta` vào buffer.
- Pad probe cua ban đọc chính metadata đó.

Nói cách khác:
- Code xây đường ống.
- Config quyết định "bộ não" và "quy tắc đọc output".

## `# TODO`

- Ghi ra bằng lời của bạn sự khác nhau giữa model gốc va engine.
- Sua `pre-cluster-threshold` thành `0.4`, chạy lại và ghi nhận thay đổi.
- Sửa `topk` nhỏ hơn, quan sát xem output có gọn lại không.
- Giải thích tại sao `num-detected-classes` sai có thể làm log / label rối loạn.

## SELF-CHECK

- Khi nào DeepStream cần build engine mới?
- Precision FP16 khác gì so với INT8 và FP32 ở mức ý tưởng?
- Neu `batch-size` cua muxer va infer khong an khop, bạn nghĩ sẽ có những kiểu
  vấn đề nào?
