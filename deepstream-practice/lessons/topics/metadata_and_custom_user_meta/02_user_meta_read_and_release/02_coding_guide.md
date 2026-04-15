# Lesson 02 Coding Guide

Lesson nay co mot truc code chinh:

1. read back custom meta o downstream probe va release no dung cach

## Before You Code

- Input: mot H.264 file giong lesson 01.
- Output: payload duoc doc o sink pad.
- Imports:
  - `pyds`
  - `Gst`, `GLib`
  - `sys`

## Build Order

1. Viet `bus_call(...)`.
2. Viet `streammux_src_pad_buffer_probe(...)` neu can attach nhu lesson 01.
3. Viet `fakesink_sink_pad_buffer_probe(...)`.
4. Build pipeline file decode -> mux -> queue -> queue -> sink.
5. Add both probes.
6. Tao bus watch va main loop.

## Function-By-Function Walkthrough

### `fakesink_sink_pad_buffer_probe(...)`

- Day la noi doc `frame_user_meta_list`.
- Moi user meta can:
  - check type
  - cast ve `NvDsUserMeta`
  - cast `user_meta_data` ve custom payload
  - doc field values
  - release payload neu sample yeu cau

### `streammux_src_pad_buffer_probe(...)`

- Co the giu lai logic attach nhu lesson 01.
- Khi hoc lesson 02, tot nhat la doc attach + readback trong cung mot sample
  de thay full vong doi.

### `main(args)`

- Pipeline giu nguyen vi sample nay khong doi data path.
- Khac biet nam o noi dat probe va cach xu ly meta sau sink.

## Syntax Notes

- `frame_meta.frame_user_meta_list`
  - danh sach user meta cua frame.
- `pyds.NvDsUserMeta.cast(l_usr.data)`
  - cast object trong list.
- `pyds.CustomDataStruct.cast(user_meta.user_meta_data)`
  - cast custom payload ve binding struct.
- `pyds.release_custom_struct(custom_msg_meta)`
  - thu hoi memory cua payload custom.

## Starter Mapping

- `TODO 1`: bus handler
- `TODO 2`: downstream probe readback
- `TODO 3`: build file pipeline
- `TODO 4`: add probe and loop

## Mini Checkpoints

- Ban co duyet dung user meta list khong?
- Ban co check `meta_type` truoc khi cast khong?
- Tai sao release phai di kem readback?
- `fakesink` co phai noi cuoi cho custom meta verification khong?
