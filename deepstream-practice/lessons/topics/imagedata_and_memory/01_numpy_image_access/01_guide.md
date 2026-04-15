# Lesson 01: NumPy Image Access

Lesson nay la buoc dau de hieu cach doc image buffer tu batched frame bang
NumPy.

## What You Will Build

- Data path:
  `uridecodebin(source bins) -> nvstreammux -> nvinfer -> nvmultistreamtiler -> nvvideoconvert -> capsfilter(RGBA) -> nvdsosd -> sink`
- Input: nhieu URI H.264/H.265
- Output: frame buffer duoc truy cap bang NumPy, sau do co the save ra file

## Why It Matters

Day la buoc chuyen tu "metadata only" sang "pixel data + metadata":

- ban khong chi doc bbox va class
- ban bat dau truy cap anh thuc
- ban hieu vi sao phai convert sang RGBA truoc khi cham vao buffer trong Python

Neu lesson nay ro, ban se hieu:

- buffer access trong DeepStream khong giong image load thong thuong
- in-place modify va copy-and-save la hai kieu hoan toan khac nhau
- `nvstreammux` + `nvmultistreamtiler` van la backbone, nhung probe luc nay doc
  anh thay vi chi doc object count

## Compared to `multistream_and_batching`

Phan giu nguyen:

- multi-source source bin
- streammux batching
- nvinfer
- tiler
- probe on batched output

Phan moi:

- `pyds.get_nvds_buf_surface(...)`
- NumPy array thao tac tren frame
- RGBA requirement
- `cv2.imwrite(...)`

Lesson truoc day ban cach batch source.
Lesson nay day ban cach lay tung frame trong batch de xu ly anh.

## New Concepts In This Lesson

### `get_nvds_buf_surface(...)`

- Ham nay tra ve image buffer view cua mot frame trong batch.
- Tranh su dung no nhu mot `cv2.imread` thuong; no phu thuoc vao pipeline
  memory backend.

### RGBA path

- Python-side image access trong sample nay chi an toan khi buffer la RGBA.
- Do do pipeline co them `nvvideoconvert` va `capsfilter`.

### Copy mode

- Neu muon save anh, ban thuong se copy buffer sang numpy array `order='C'`.
- Copy mode giup ban dang doc/sua ma khong giu chat voi buffer goc lau hon can
  thiet.

### In-place vs copy

- In-place: thay doi buffer goc, downstream thay doi theo.
- Copy: thay doi ban copy, downstream khong thay doi.

## Mental Model

### Data flow

1. Multi-source vao streammux.
2. Pgie tao object metadata.
3. Tiler composite batch thanh mot canvas.
4. Probe tai tiler sink lay batched buffer.
5. `get_nvds_buf_surface(...)` tra ve image data cua frame.
6. NumPy/OpenCV xu ly va save file neu can.

### Memory model

- Buffer goc van nam trong DeepStream / GPU-oriented pipeline.
- Python chi dang map tung phan duoc expose ra.
- Neu buffer khong RGBA, access path co the khong hop le.

## Implementation Checklist

1. Parse URI list va output folder.
2. Tao source bins va streammux.
3. Tao pgie, tiler, nvvidconv, capsfilter, nvosd, sink.
4. Set streammux width/height/batch-size.
5. Set pgie config.
6. Dat probe tren tiler sink pad.
7. Trong probe, lay `NvDsFrameMeta`.
8. Lay image buffer bang `get_nvds_buf_surface(...)`.
9. Copy buffer sang numpy array neu can save.
10. Ghi file qua OpenCV.

## Common Failure Modes

- Quen RGBA caps truoc khi doc buffer.
- Doc nham batch_id vs pad_index.
- Khong copy buffer ma lai lam viec lau tren view goc.
- Khong canh non-CPU-safe on Jetson/unified memory path.
- Quen tao output folder cho tung source.

## Self-Check

- Tai sao phai co RGBA?
- `get_nvds_buf_surface(...)` tra ve gi?
- In-place va copy khac nhau o diem nao?
- Vi sao probe dat o tiler sink thay vi o source pad?

## Extensions

- Thu chi save frame moi N buffer.
- Ghi them frame number vao ten file.
- Doi confidence threshold va quan sat anh duoc save.
