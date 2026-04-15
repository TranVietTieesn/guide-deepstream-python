# Lesson 01 Coding Guide

Lesson nay co hai truc code chinh:

1. build pipeline file decode -> mux -> sink
2. attach custom payload tai upstream probe

## Before You Code

- Input: mot H.264 elementary stream.
- Output: pipeline chay va moi frame co custom user meta.
- Imports:
  - `sys`, `os`
  - `gi`, `Gst`, `GLib`
  - `pyds`

## Build Order

1. Viet `bus_call(...)`.
2. Viet `streammux_src_pad_buffer_probe(...)`.
3. Parse input path.
4. Tao pipeline, source, parser, decoder, muxer, queue, sink.
5. Set mux properties.
6. Link source -> parser -> decoder.
7. Request mux sink pad va link decoder src pad.
8. Link mux -> queue -> queue -> sink.
9. Dat probe tren mux src pad.
10. Chay main loop.

## Function-By-Function Walkthrough

### `streammux_src_pad_buffer_probe(...)`

- Day la noi attach custom meta.
- Logic chinh:
  - lay `GstBuffer`
  - lay `NvDsBatchMeta`
  - acquire meta lock
  - duyet `frame_meta_list`
  - cap phat custom struct
  - fill field
  - wrap struct trong `NvDsUserMeta`
  - add meta vao frame
  - release lock

### `bus_call(...)`

- Giu cho lesson van co full pipeline lifecycle.
- EOS, WARNING, ERROR xu ly theo thoi quen DeepStream co ban.

### `main(args)`

- `streammux.batch-size = 1` phu hop voi file input sample.
- `queue` giu pipeline de khong block khi meta probe chiem thoi gian.
- `fakesink` giup lesson tap trung vao metadata, khong bi phan tam boi
rendering.

## Syntax Notes

- `pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))`
  - day la cach lay batch meta tu buffer.
- `pyds.nvds_acquire_meta_lock(batch_meta)` / `release`
  - dung khi duyet frame meta.
- `pyds.nvds_acquire_user_meta_from_pool(batch_meta)`
  - lay `NvDsUserMeta` object tu pool.
- `pyds.alloc_custom_struct(user_meta)`
  - cap phat memory cho custom payload binding.
- `user_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_USER_META`
  - bat buoc de downstream nhan ra day la user meta.

## Starter Mapping

- `TODO 1`: bus handler
- `TODO 2`: probe attach user meta
- `TODO 3`: build file pipeline
- `TODO 4`: request pad and link mux
- `TODO 5`: add probe and main loop

## Mini Checkpoints

- `NvDsUserMeta` duoc tao o dau trong pipeline?
- Tai sao can meta lock khi duyet frame list?
- `fakesink` o day co vai tro gi trong lesson?
- `alloc_custom_struct` khac gi object Python thuong?

