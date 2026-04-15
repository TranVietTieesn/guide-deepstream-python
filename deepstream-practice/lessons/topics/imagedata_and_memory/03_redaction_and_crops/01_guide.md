# Lesson 03: Redaction and Crops

Lesson nay ket hop image access voi object filtering va crop output.

## What You Will Build

- Data path:
  `uridecodebin(source bins) -> nvstreammux -> nvinfer -> nvmultistreamtiler -> nvvideoconvert -> capsfilter(RGBA) -> nvdsosd -> sink`
- Input: nhieu URI
- Output: frame da redaction va cropped face images trong `out_crops/`

## Why It Matters

Day la lesson noi image access khong con chi de "doc anh", ma de:

- che mat / redaction
- crop object tu frame buffer
- save ROI ra file
- nhan biet object theo confidence/class va xu ly co dieu kien

Day la buoc gan voi production hon:

- khong phai object nao cung save
- khong phai frame nao cung xu ly nhu nhau
- ban phai biet khi nao can hide, khi nao can export

## Compared to Lessons 01 and 02

Phan giu nguyen:

- multi-source batching
- infer metadata
- RGBA image access
- output sink

Phan moi:

- face redaction
- crop object
- save to `out_crops/`
- class-aware overlay modification

Lesson 01 focus vao save frame.
Lesson 02 focus vao GPU access.
Lesson 03 focus vao object-driven post-processing.

## New Concepts In This Lesson

### Redaction

- Thay vi ve bbox, sample nay set background color / border width de che
  doi tuong.
- Day la mot kieu "privacy-aware visualization".

### Crop object

- Image buffer duoc cat theo rect params cua object meta.
- Crop chi capture region quan tam, khong can save toan frame.

### Confidence-based save

- Lesson nay co them logic "chi luu khi object meet dieu kien".
- Day giong mot filter layer truoc khi write to disk.

### Out crops directory

- Frame crop duoc chia theo stream va frame number.
- Structure output giup tracing sau nay de hon.

## Mental Model

### Data flow

1. Multi-source vao pipeline.
2. Infer tao object meta.
3. Probe duyet object list.
4. Face/person object duoc redaction in-place.
5. Khi dieu kien khop, crop face ra anh copy.
6. Crop duoc save vao folder theo stream.

### Control flow

- Object class quyet dinh cach xu ly.
- Confidence quyet dinh co save crop hay khong.
- `is_first_obj` tranh crop/convert nhieu lan trong cung frame.

## Implementation Checklist

1. Parse URI list.
2. Tao folder `out_crops/stream_<id>/`.
3. Tao multi-source pipeline.
4. Set RGBA path.
5. Dat probe tren tiler sink pad.
6. Trong probe, redaction face/person theo class.
7. Crop face khi meet confidence criteria.
8. Copy image sang numpy array va save bang OpenCV.

## Common Failure Modes

- Crop ngoai bounds cua image.
- Quen RGBA path cho `get_nvds_buf_surface(...)`.
- Save nhieu lan trong cung frame vi quên `is_first_obj`.
- Khong tao folder output theo stream.
- Lam redaction nhung khong quan tam memory unmap tren Jetson.

## Self-Check

- Redaction khac gi crop?
- Tai sao sample nay can class-aware logic?
- Vi sao chi save co dieu kien?
- `out_crops` phuc vu muc dich gi so voi lesson 01?

## Extensions

- Doi confidence threshold.
- Save person crop, khong chi face crop.
- Doi mau redaction theo class.
