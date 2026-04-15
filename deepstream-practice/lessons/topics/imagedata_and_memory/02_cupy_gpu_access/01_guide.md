# Lesson 02: CuPy GPU Access

Lesson nay chuyen tu CPU/unified-memory access sang GPU direct access bang
CuPy.

## What You Will Build

- Data path:
  `uridecodebin(source bins) -> nvstreammux -> nvinfer -> nvmultistreamtiler -> nvvideoconvert -> capsfilter(RGBA) -> nvdsosd -> sink`
- Input: nhieu URI
- Output: buffer duoc xu ly tren GPU memory, khong convert sang NumPy view

## Why It Matters

Day la nấc thang tiep theo cua image access:

- ban khong phai map buffer ve CPU nua
- ban doc va thao tac GPU memory truc tiep
- ban hieu duoc vi sao buffer ownership va CUDA stream synchronization quan trong

Neu lesson nay ro, ban se thay su khac biet giua:

- data view tren CPU
- data pointer tren GPU
- math / ndarray semantics cua CuPy

## Compared to Lesson 01

Phan giu nguyen:

- multi-source pipeline
- batching
- infer
- tiler
- RGBA path
- probe tai output

Phan moi:

- `pyds.get_nvds_buf_surface_gpu(...)`
- `cupy.cuda.UnownedMemory`
- `cupy.cuda.MemoryPointer`
- `cupy.ndarray(...)`
- CUDA null stream synchronization

Lesson 01 la "doc anh bang NumPy".
Lesson 02 la "doc va modify anh bang GPU memory".

## New Concepts In This Lesson

### `get_nvds_buf_surface_gpu(...)`

- Tra ve thong tin buffer tren GPU: dtype, shape, strides, pointer, size.
- Tu day ban xay CuPy array thay vi numpy copy.

### `UnownedMemory`

- CuPy can biet day la memory no khong own.
- Day giup avoid double free va giu connection toi DeepStream buffer.

### CUDA null stream

- When modifying shared buffer memory, null stream giup don gian hoa
  synchronization.

### In-place GPU modification

- Thay doi truoc khi downstream dung buffer.
- Day la khac biet chinh so voi lesson 01, noi ban thuong save copy.

## Mental Model

### Data flow

1. Buffer di qua tiler sink probe.
2. Probe lay GPU surface info.
3. Probe tao CuPy view tren device memory.
4. Probe modify channel data in-place.
5. Buffer tiep tuc di xuong pipeline trong trang thai da doi.

### Memory model

- Khong co CPU copy o giua.
- `UnownedMemory` giu lien ket voi buffer goc.
- Dang lam viec voi GPU pointer nen sai sync co the gay corruption hoac
  race condition.

## Implementation Checklist

1. Parse URI list.
2. Tao source bins, mux, pgie, tiler, nvvidconv, capsfilter, nvosd, sink.
3. Set RGBA path va streammux properties.
4. Dat probe tren tiler sink.
5. Trong probe, lay GPU buffer info.
6. Tao CuPy memory view.
7. Modify mot channel.
8. Sync stream.

## Common Failure Modes

- Quen `cupy` dependency.
- Dang dung sai memory backend cho platform.
- Khong dung null stream khi modify buffer dang share.
- Lam viec nhu NumPy array binh thuong trong khi day la device memory.
- Quen RGBA path truoc khi access.

## Self-Check

- `get_nvds_buf_surface_gpu(...)` khac gi `get_nvds_buf_surface(...)`?
- Tai sao can `UnownedMemory`?
- Vi sao phai co stream synchronization?
- Lesson nay khac lesson 01 o memory ownership nao?

## Extensions

- Thu modify channel khac.
- Doi scale factor trong GPU operation.
- So sanh ket qua voi NumPy copy path.
