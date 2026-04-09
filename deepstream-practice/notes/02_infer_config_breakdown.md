# Infer Config Breakdown

File goc `../../dstest1_pgie_config.txt` la noi `nvinfer` doc de biet:
- model nao duoc dung,
- engine nao duoc nap,
- co bao nhieu class,
- cach loc va clustering bbox sau suy luan.

Trong code, diem noi giua pipeline va model la:

```python
pgie.set_property("config-file-path", "dstest1_pgie_config.txt")
```

Neu khong hieu file config nay, ban se thay `nvinfer` giong nhu hop den.

## Cac key chinh trong file hien tai

### `onnx-file`

Gia tri hien tai:
- `../../../../samples/models/Primary_Detector/resnet18_trafficcamnet_pruned.onnx`

Y nghia:
- Duong dan den model ONNX goc.
- Thuong duoc dung khi can build TensorRT engine lan dau.

### `model-engine-file`

Gia tri hien tai:
- `../../../../samples/models/Primary_Detector/resnet18_trafficcamnet_pruned.onnx_b1_gpu0_fp16.engine`

Y nghia:
- Engine TensorRT da toi uu san cho GPU / precision / batch-size cu the.
- Neu engine phu hop da ton tai, DeepStream co the nap nhanh hon so voi build lai
  tu model goc.

### `labelfile-path`

Gia tri hien tai:
- `../../../../samples/models/Primary_Detector/labels.txt`

Y nghia:
- Mapping `class_id -> ten class`.
- Gia tri nay rat quan trong khi ban muon in log de nguoi doc hieu duoc.

### `batch-size`

Gia tri hien tai:
- `1`

Y nghia:
- So frame duoc infer cung luc.
- Thuong can dong bo voi batch ma `nvstreammux` tao ra.

### `network-mode`

Gia tri hien tai:
- `2`

Theo docs DeepStream, cac gia tri pho bien:
- `0`: FP32
- `1`: INT8
- `2`: FP16

Y nghia:
- Chon precision cho suy luan.
- Precision anh huong den toc do, memory va do chinh xac.

### `num-detected-classes`

Gia tri hien tai:
- `4`

Y nghia:
- So class detector se output.
- Can phu hop voi model va labels.

### `interval`

Gia tri hien tai:
- `0`

Y nghia:
- Tan suat bo qua frame infer.
- `0` nghia la infer moi frame.

### `gie-unique-id`

Gia tri hien tai:
- `1`

Y nghia:
- ID de phan biet engine nay voi engine khac trong pipeline.
- Rat quan trong khi sau nay co them tracker, SGIE hoac custom metadata.

### `cluster-mode`

Gia tri hien tai:
- `2`

Theo docs DeepStream:
- `0`: GroupRectangles
- `1`: DBSCAN
- `2`: NMS
- `3`: Hybrid
- `4`: Khong clustering

Y nghia:
- Cac candidate bbox tu model can duoc gom / loc sau suy luan.
- `2` thuong la NMS, rat pho bien cho detector.

### `pre-cluster-threshold`

Gia tri hien tai:
- `0.2`

Y nghia:
- Loc bo bbox confidence thap truoc khi clustering / NMS.
- Tang gia tri nay thi output thuong sach hon nhung de miss object hon.

### `topk`

Gia tri hien tai:
- `20`

Y nghia:
- Giu lai toi da bao nhieu candidate truoc / trong buoc loc tiep theo.

### `nms-iou-threshold`

Gia tri hien tai:
- `0.5`

Y nghia:
- Nguong giao nhau de NMS quyet dinh giu hoac bo bbox trung lap.

## Moi lien he giua config va hanh vi runtime

- `deepstream-test1.py` tao `nvinfer`.
- `nvinfer` doc `config-file-path`.
- Config quyet dinh model va cach post-process.
- Sau do `nvinfer` gan `NvDsObjectMeta` vao buffer.
- Pad probe cua ban doc chinh metadata do.

Noi cach khac:
- Code xay duong ong.
- Config quyet dinh "bo nao" va "quy tac doc output".

## `# TODO`

- Ghi ra bang loi cua ban su khac nhau giua model goc va engine.
- Sua `pre-cluster-threshold` thanh `0.4`, chay lai va ghi nhan thay doi.
- Sua `topk` nho hon, quan sat xem output co gon lai khong.
- Giai thich tai sao `num-detected-classes` sai co the lam log / label roi loan.

## SELF-CHECK

- Khi nao DeepStream can build engine moi?
- Precision FP16 khac gi so voi INT8 va FP32 o muc y tuong?
- Neu `batch-size` cua muxer va infer khong an khop, ban nghi se co nhung kieu
  van de nao?
