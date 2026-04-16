# Lesson 02 Coding Guide

Lesson nay co hai truc code chinh:

1. tracker/analytics pipeline setup
2. analytics metadata probe

## Before You Code

- Input: URI list.
- Output: analytics meta duoc in ra tai probe.
- Imports:
  - `configparser`
  - `pyds`
  - `PlatformInfo`
  - `bus_call`

## Build Order

1. Viet `nvanalytics_src_pad_buffer_probe(...)`.
2. Viet `cb_newpad(...)`, `decodebin_child_added(...)`, `create_source_bin(...)`.
3. Parse args.
4. Tao pipeline va source bins.
5. Tao pgie, tracker, nvanalytics, tiler, nvvidconv, nvosd, sink.
6. Doc tracker config va set nvanalytics config.
7. Link chain co queue.
8. Dat probe o nvanalytics src pad.
9. Tao bus watch va main loop.

## Function-By-Function Walkthrough

### `nvanalytics_src_pad_buffer_probe(...)`

- Day la noi nhan object va frame analytics meta.
- Ban can:
  - duyet frame_meta_list
  - duyet obj_meta_list
  - duyet obj_user_meta_list cho object-level analytics
  - duyet frame_user_meta_list cho frame-level analytics

### `main(args)`

- `nvdsanalytics` can tracker state truoc.
- `config-file` cua plugin analytics quyet dinh roi/line/direction rules.
- Queue giup pipeline co backbone ro rang va han backpressure.

## Syntax Notes

- `user_meta.base_meta.meta_type == pyds.NvDsMetaType.NVDS_OBJ_META_NVDSANALYTICS`
  - object analytics meta.
- `user_meta.base_meta.meta_type == pyds.NvDsMetaType.NVDS_FRAME_META_NVDSANALYTICS`
  - frame analytics meta.
- `pyds.NvDsAnalyticsObjInfo.cast(...)`
  - object analytics payload.
- `pyds.NvDsAnalyticsFrameMeta.cast(...)`
  - frame analytics payload.
- `nvanalytics.set_property("config-file", "config_nvdsanalytics.txt")`
  - load rules.

## Starter Mapping

- `TODO 1`: analytics probe
- `TODO 2`: source/decode helper setup
- `TODO 3`: tracker config reading
- `TODO 4`: pipeline construction
- `TODO 5`: analytics config and link chain

## Mini Checkpoints

- Object analytics meta va frame analytics meta khac nhau o dau?
- `nvtracker` co vai tro gi trong analytics pipeline?
- Rules file nam o dau trong sample?
- Vi sao probe dat o `nvdsanalytics` src pad?
