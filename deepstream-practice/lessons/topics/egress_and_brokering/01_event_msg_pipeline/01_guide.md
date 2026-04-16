# Lesson 01: Event Message Pipeline

Lesson nay day ban cach tao event message meta va day no sang `nvmsgconv`
va `nvmsgbroker`.

## What You Will Build

- Data path:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> tee -> [nvmsgconv -> nvmsgbroker] + [preview sink]`
- Input: mot H.264 file
- Output: 1 nhánh preview va 1 nhánh broker message

## Why It Matters

Day la mau hinh egress co ban trong DeepStream:

- mot pipeline co the phuc vu ca visualization va telemetry
- message payload duoc sinh ra tu metadata, khong phai tu raw frame
- `tee` cho phep tach data plane va control/egress plane

Neu lesson nay ro, ban se hieu:

- `nvmsgconv` khong "detect" gi ca, no convert meta sang payload
- `nvmsgbroker` chi gui payload ra ngoai
- event message meta phai duoc gan truoc khi convert

## Compared to `baseline_pipeline`

Phan giu nguyen:

- file source decode chain
- `nvstreammux`
- `nvinfer`
- `nvdsosd`
- bus/main loop

Phan moi:

- `tee`
- `queue` sau tee
- `nvmsgconv`
- `nvmsgbroker`
- `NVDS_META_EVENT_MSG` flow

Lesson baseline day ban ve bbox.
Lesson nay day ban ve data o ngoai pipeline.

## New Concepts In This Lesson

### `tee`

- Tach 1 buffer path thanh nhieu nhánh.
- Mot nhánh co the render local, nhánh kia co the de lam egress.

### Event message meta

- Dang meta dung cho telemetry.
- Co the mang bbox, object id, class, va custom payload.

### `nvmsgconv`

- Convert `NVDS_META_EVENT_MSG` sang payload JSON.
- Doc schema config tu file.

### `nvmsgbroker`

- Gui payload qua protocol adaptor.
- Backend co the la Kafka, MQTT, AMQP, Redis, Azure.

## Mental Model

### Data flow

1. Detector tao object meta.
2. OSD probe attach event message meta.
3. `tee` split buffer.
4. Mot nhánh vao `nvmsgconv`.
5. `nvmsgconv` sinh payload.
6. `nvmsgbroker` gui payload ra backend.
7. Nhánh con lai tiep tuc preview.

### Control flow

- Message frequency do app quyet dinh.
- Schema do config file quyet dinh.
- Broker adaptor va connection string do CLI/config quyet dinh.

## Implementation Checklist

1. Parse input file, proto lib, conn string, schema type, topic, no-display.
2. Tao source -> decode -> mux -> pgie -> convert -> osd.
3. Tao tee va hai queue.
4. Tao msgconv, msgbroker, preview sink.
5. Set config file path va payload type.
6. Set broker adaptor params.
7. Dat probe tren OSD sink de attach event msg meta.
8. Request tee pads va link hai nhánh.

## Common Failure Modes

- Quen set `proto-lib`.
- Quen set `conn-str` hoac `cfg-file`.
- Sai schema type lam payload khong khop.
- Quen request pad tu tee.
- Attach event meta nhung khong set `NVDS_EVENT_MSG_META`.

## Self-Check

- `nvmsgconv` va `nvmsgbroker` khac nhau the nao?
- `tee` co vai tro gi trong sample nay?
- Event message meta duoc attach o dau?
- Preview sink co can broker khong?

## Extensions

- Doi tan suat gui message.
- Chay voi `--no-display`.
- Thu comment out nhánh broker va chi preview local.
