# Lesson 01 Coding Guide

Lesson nay co ba truc code chinh:

1. event message meta generation
2. tee split pipeline
3. broker setup

## Before You Code

- Input: H.264 file + broker connection params.
- Output: local preview + broker publish.
- Imports:
  - `OptionParser`
  - `common.utils.long_to_uint64`
  - `pyds`
  - `PlatformInfo`

## Build Order

1. Viet `generate_vehicle_meta(...)` va `generate_person_meta(...)`.
2. Viet `generate_event_msg_meta(...)`.
3. Viet `osd_sink_pad_buffer_probe(...)`.
4. Parse CLI args.
5. Tao source, parser, decoder, mux, pgie, convert, osd.
6. Tao `msgconv`, `msgbroker`, `tee`, `queue1`, `queue2`, sink.
7. Set config/schema/proto/broker props.
8. Link main chain va tee branches.
9. Dat probe o nvosd sink pad.
10. Tao bus watch va run.

## Function-By-Function Walkthrough

### `generate_event_msg_meta(...)`

- Tao `NvDsEventMsgMeta`.
- Gan bbox, trackingId, confidence.
- Tao custom ext object cho vehicle/person.
- Set `meta.type`, `objType`, `objClassId`.

### `osd_sink_pad_buffer_probe(...)`

- Day la noi attach event meta vao frame.
- `is_first_object` va `frame_number % 30` giup dieu chinh tan suat gui.
- `nvds_acquire_user_meta_from_pool(...)` cap user meta.

### `main(args)`

- `tee` chia sang broker va preview.
- `msgconv.payload-type` quyet dinh schema.
- `msgbroker.proto-lib` va `conn-str` quyet dinh backend.

## Syntax Notes

- `pyds.alloc_nvds_event_msg_meta(user_event_meta)`
  - cap phat event msg meta.
- `user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META`
  - bat buoc truoc khi add vao frame.
- `tee.request_pad_simple('src_%u')`
  - tee pad request de split nhánh.
- `msgconv.set_property('config', MSCONV_CONFIG_FILE)`
  - doc schema config.
- `msgbroker.set_property('sync', False)`
  - tranh block render path.

## Starter Mapping

- `TODO 1`: event meta generator
- `TODO 2`: OSD probe attach
- `TODO 3`: parse CLI args
- `TODO 4`: build pipeline elements
- `TODO 5`: tee split and link

## Mini Checkpoints

- Event msg meta duoc tao o dau?
- `msgconv` co lay thang tu object meta khong?
- `tee` can may request pads?
- `proto-lib` va `conn-str` khac nhau nhu the nao?
