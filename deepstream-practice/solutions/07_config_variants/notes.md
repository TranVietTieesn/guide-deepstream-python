# Lesson 07: Config Variants - Notes

## Trạng Thái

- Bài này không có code solution riêng.
- Sử dụng lại pipeline từ bài 04, 05, hoặc 06.
- Tập trung vào việc điều chỉnh file config.

## Config Checklist

| Parameter | Mặc định | Đã Thử | Kết Quả |
|-----------|----------|--------|---------|
| `pre-cluster-threshold` | 0.2 | | |
| `topk` | 20 | | |
| `nms-iou-threshold` | 0.5 | | |
| `batch-size` | 1 | | |
| `network-mode` | 2 (FP16) | | |
| `interval` | 0 | | |

## Ghi Chú Thực Nghiệm

### `pre-cluster-threshold`

- 0.2: Balance giữa precision và recall.
- 0.4: Output sạch hơn nhưng có thể miss object.
- 0.1: Nhiều false positives.

### `topk`

- 20: Đủ cho hầu hết scenes.
- 5: Quá ít cho crowded scenes.
- 50: Dư thừa, không cần thiết.

### `nms-iou-threshold`

- 0.5: Standard, cân bằng.
- 0.3: Gộp nhiều bbox hơn, ít overlap.
- 0.7: Giữ nhiều overlap hơn.

## Match với Code

```python
# Trong code, streammux batch-size phải match config
streammux.set_property("batch-size", 1)  # Match batch-size=1 trong config
```

## References

- DeepStream Plugin Guide: nvinfer config file format
- TensorRT documentation: FP16, INT8, FP32 modes
