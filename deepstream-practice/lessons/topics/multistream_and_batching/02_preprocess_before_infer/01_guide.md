# Lesson 02: Preprocess Before Infer

Lesson nay chuyen tu "multi-source infer" sang "multi-source + custom ROI preprocess".

## What You Will Build

- Data path:
  `uridecodebin(source bin) -> nvstreammux -> nvdspreprocess -> nvinfer -> nvmultistreamtiler -> sink`
- Input: mot hoac nhieu URI H.264/H.265
- Expected outcome: hieu nvdspreprocess gan raw tensor meta vao batch va nvinfer
  doc tensor meta do thay vi preprocess lai

## Why It Matters

Day la lesson day ban mot pattern rat quan trong:

- preprocessing khong nhat thiet phai nam ben trong `nvinfer`
- ban co the tach custom ROI transformation ra mot plugin rieng
- `nvinfer` co the doc input tensor meta co san

Day la buoc nhin pipeline theo kieu "feature extraction -> tensor prep -> infer".

## Compared to Lesson 01

Phan giu nguyen:

- source bin + `nvstreammux`
- tiler + sink
- bus/main loop
- batch-oriented thinking

Phan moi:

- `nvdspreprocess`
- ROI grouping
- tensor meta
- config preprocess
- gioi han network input shape va ROI count

Lesson 01 day ban batch tu source.
Lesson 02 day ban batch sau do duoc "bien doi" truoc khi vao infer.

## New Concepts In This Lesson

### `nvdspreprocess`

- Preprocess batched frames va tao raw tensor meta.
- Co the dung custom library de xu ly group ROI.

### Tensor meta

- `nvinfer` doc tensor meta thay vi preprocess lai tu dau.
- Day la co che tach preprocessing ra khoi inference.

### ROI budget

- `network-input-shape[0]` quyet dinh so sample/tensor slot.
- ROI cua tat ca source khong duoc vuot qua gioi han nay.

### `GST_CAPS_FEATURES_NVMM`

- Lesson nay van can NVMM flow truoc khi preprocessing.
- GPU path van la "xuong song" chung.

## Mental Model

### Data flow

1. Source bin -> muxer.
2. Muxer bat frame theo batch.
3. Preprocess cat/transform ROI theo config.
4. Preprocess gan user meta tensor vao batch.
5. `nvinfer` doc tensor meta do.
6. Tiler va sink hien thi.

### Control flow

- ROI config khong phai chi la "add more data".
- No quyet dinh tensor count, batch size, va memory budget.
- Sai cau hinh preprocess co the lam fail ngay truoc infer.

## Implementation Checklist

1. Parse input URI list va preprocess config.
2. Tao pipeline, streammux, preprocess, pgie, tiler, sink.
3. Set streammux batch size va tile size.
4. Set preprocess config file.
5. Add and link pipeline.
6. Dat probe de doc ROI/tensor meta neu can.
7. Run bus/main loop.

## Common Failure Modes

- ROI count vuot qua network input shape.
- Config preprocess khong khop voi source count.
- `nvinfer` batch-size khong khop preprocess batch-size.
- Quen giong multi-source source bin va streammux setup.
- GPU memory backend khong duoc chuan bi dung.

## Self-Check

- ROI preprocessing nam truoc hay sau `nvinfer`?
- `nvinfer` co can tu preprocess lai khi da co tensor meta khong?
- Gioi han ROI duoc quyet dinh boi cai gi?
- Lesson nay khac gi lesson 01 ve vai tro cua `nvstreammux`?

## Extensions

- Doi so ROI trong config va ghi lai tac dong.
- Thay custom preprocess config va quan sat tensor count.
- So sanh co/khong co preprocess tren cung input.
