# Metadata Flow

Đây là phần quan trọng nhất để bạn thật sự "đọc được DeepStream".

Nếu chỉ chạy pipeline và nhìn bbox trên màn hình, bạn mới thấy kết quả. Nếu bạn
đọc được metadata, bạn mới thật sự hiểu plugin nào đã đưa thông tin gì vào
buffer, và bạn có thể mở rộng sang analytics, đếm đối tượng, cảnh báo, lưu sự
kiện.

## Chuỗi metadata trong file gốc

Trong `../../deepstream-test1.py`, probe ở `nvosd.sink` đọc metadata theo chuỗi:

`Gst.Buffer -> NvDsBatchMeta -> NvDsFrameMeta -> NvDsObjectMeta`

## Metadata xuất hiện từ đâu?

Trong pipeline này, metadata detection xuất hiện sau `nvinfer`.

Nghĩa là:
- `filesrc`, `h264parse`, `nvv4l2decoder`, `nvstreammux` chủ yếu chuẩn bị data.
- `nvinfer` thêm thông tin object detection vào buffer.
- Probe của bạn đọc lại metadata đó.

## Tại sao dùng `hash(gst_buffer)`?

Theo mẫu Python DeepStream, `pyds.gst_buffer_get_nvds_batch_meta()` cần địa chỉ C
của `GstBuffer`. Trong binding Python, `hash(gst_buffer)` được dùng để lấy giá trị
địa chỉ phù hợp cho hàm này.

Hãy nhớ:
- Bạn không truyền "nội dung buffer".
- Bạn truyền handle / địa chỉ của buffer để `pyds` tìm metadata gắn kèm.

## Tại sao phải `.cast()`?

Metadata list được đưa về dưới dạng node tổng quát.

Vì vậy bạn phải:
- `pyds.NvDsFrameMeta.cast(l_frame.data)`
- `pyds.NvDsObjectMeta.cast(l_obj.data)`

Nếu không cast:
- Python không biết node đó phải được đọc như kiểu nào.
- Bạn không truy cập được field chuyên biệt như `frame_num`, `num_obj_meta`,
  `class_id`, `rect_params`.

## Memory ownership: chỗ này rất dễ "mơ hồ"

Trong sample DeepStream Python, comment nhấn mạnh rằng:
- Metadata object nằm ở phía C.
- Python binding chỉ wrap lại.
- Garbage collector Python không sở hữu bộ nhớ đó.

Ý nghĩa thực tế:
- Bạn không nên tự ý giải phóng.
- Bạn cần dùng các API `pyds` đúng cách.
- Khi tạo display meta, thường phải xin từ pool bằng
  `nvds_acquire_display_meta_from_pool(batch_meta)`.

## Duyệt metadata list như thế nào?

### Tầng batch

- Một buffer có thể chứa batch của nhiều frame.
- `batch_meta.frame_meta_list` là danh sách frame trong batch.

### Tầng frame

- Mỗi `NvDsFrameMeta` đại diện cho 1 frame.
- Trong đó có `frame_num`, `num_obj_meta`, `obj_meta_list`.

### Tầng object

- Mỗi `NvDsObjectMeta` đại diện cho 1 object detect được.
- Bạn có thể đọc:
  - `class_id`
  - `confidence`
  - `rect_params.left`
  - `rect_params.top`
  - `rect_params.width`
  - `rect_params.height`

## Từ metadata sang overlay

File gốc làm 2 việc trong cùng probe:

1. Đọc metadata object để đếm object.
2. Tạo `NvDsDisplayMeta` để đưa text overlay lên frame.

Đó là một pattern rất phổ biến:
- infer -> metadata
- probe -> business logic
- OSD -> visualize logic

## Những điểm hay nhầm lẫn

### Nhầm lẫn 1: Probe là nơi tao metadata

Sai. Probe không phải nơi tạo detection metadata.

Probe:
- đọc,
- sửa,
- thêm metadata / display meta mới nếu muốn.

Còn detection metadata ở bài này đến từ `nvinfer`.

### Nhầm lẫn 2: `num_obj_meta` là tổng object của cả pipeline

Sai. Nó là tổng object của frame hiện tại.

Muốn tổng theo thời gian:
- bạn phải tự tích lũy ở tầng app.

### Nhầm lẫn 3: Có bbox là chắc chắn có text overlay

Sai. Bbox / object meta và display text là 2 lớp khác nhau.

## `# TODO`

- In thêm `confidence` của từng object.
- In thêm bbox và map `class_id` sang tên class.
- Thử gắn probe sang điểm sớm hơn trong pipeline và quan sát metadata có khác
  không.
- Tự giải thích vì sao `nvosd.sink` là vị trí học tập tốt.

## SELF-CHECK

- Nếu batch-size = 2 thì `frame_meta_list` có thể chứa gì?
- Vì sao sample phải dùng `.cast()` thay vì đọc trực tiếp `l_frame.data`?
- Bạn sẽ đặt logic đếm object tổng theo 1 phút ở probe hay ở lớp app cao hơn?
