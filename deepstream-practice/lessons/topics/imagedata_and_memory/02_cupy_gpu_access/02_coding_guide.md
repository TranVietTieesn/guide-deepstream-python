# Lesson 02 Coding Guide

Lesson nay co hai truc code chinh:

1. lay GPU buffer view tren tiler sink
2. thao tac CuPy in-place

## Before You Code

- Input: URI list.
- Output: GUI sink va frame da duoc modify tren GPU.
- Imports:
  - `cupy as cp`
  - `ctypes`
  - `pyds`
  - `PERF_DATA`

## Build Order

1. Viet `tiler_sink_pad_buffer_probe(...)`.
2. Viet `cb_newpad(...)`, `decodebin_child_added(...)`, `create_source_bin(...)`.
3. Parse args va tao pipeline.
4. Tao streammux, pgie, nvvidconv1, capsfilter, tiler, nvvidconv, nvosd, sink.
5. Set RGBA caps.
6. Dat probe tren tiler sink pad.
7. Tao bus watch va perf callback.
8. Chay main loop.

## Function-By-Function Walkthrough

### `tiler_sink_pad_buffer_probe(...)`

- Lay `batch_meta` nhu lesson 01.
- Chon tung frame trong batch.
- Goi `pyds.get_nvds_buf_surface_gpu(...)`.
- Extract pointer bang `ctypes.pythonapi.PyCapsule_GetPointer`.
- Tao `cp.cuda.UnownedMemory`.
- Tao `cp.cuda.MemoryPointer`.
- Tao `cp.ndarray`.
- Dung CUDA null stream de modify data.

### `main(...)`

- `filter1` ep buffer ve `video/x-raw(memory:NVMM), format=RGBA`.
- `nveglglessink`/`nv3dsink` giu output preview.
- `pgie.batch-size` nen khop so source.

## Syntax Notes

- `ctypes.pythonapi.PyCapsule_GetPointer`
  - can khi `dataptr` la PyCapsule.
- `cp.cuda.stream.Stream(null=True)`
  - null stream, dung de synchronize operations tren buffer.
- `cp.ndarray(shape=..., dtype=..., memptr=..., strides=...)`
  - tao view tren GPU memory.

## Starter Mapping

- `TODO 1`: GPU buffer probe
- `TODO 2`: source bin helper
- `TODO 3`: pipeline creation
- `TODO 4`: link and probe

## Mini Checkpoints

- Tai sao khong convert sang numpy trong lesson nay?
- `UnownedMemory` co vai tro gi?
- Vi sao null stream quan trong?
- Ban co the modify buffer ma khong copy ra CPU khong?
