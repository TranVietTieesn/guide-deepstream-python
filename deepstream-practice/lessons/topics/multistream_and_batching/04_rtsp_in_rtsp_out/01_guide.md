# Lesson 04: RTSP In, RTSP Out

Lesson nay la ket hop cua live source handling va streaming egress.

## What You Will Build

- Data path:
  `rtsp://... source bin -> nvstreammux -> nvinfer or nvinferserver -> nvdsosd -> encoder -> rtppay -> udpsink -> GstRtspServer`
- Input: mot hoac nhieu RTSP URI
- Expected outcome: hieu cach live source di vao pipeline va output cung duoc
  expose nhu RTSP

## Why It Matters

Day la lesson cho ban thay DeepStream co the song o ca hai dau:

- dau vao la live
- dau ra cung la live

No can:

- source bin va ghost pad
- live-source / NTP sync thinking
- encoder/payloader/server sidecar

## Compared to Lesson 01 and 03

Lesson 01:
- live multi-source in

Lesson 03:
- batched infer split out

Lesson 04:
- live input + live output
- con co RTSP timestamping / source sync concerns

## New Concepts In This Lesson

### `rtsp://` source

- Source live khong co EOS "dep" nhu file.
- `drop-on-latency` va NTP sync co the quan trong hon file input.

### `ts_from_rtsp`

- RTSP timestamp co the duoc lay tu stream thay vi system time.
- Lesson nay chi can hieu concept, khong can goi het tat ca latency tuning chi tiet.

### `GstRtspServer`

- Day la server layer cho output.
- `udpsink` day RTP stream vao factory launch string.

### `nvinferserver`

- Sample nay co the dung `nvinfer` hoac `nvinferserver`.
- lesson guide chi can hieu both are inference engines, vi output path khong doi.

## Mental Model

### Data flow

1. RTSP source vao source bin.
2. Source bin nho callback dynamic pad.
3. `nvstreammux` batch live sources.
4. `nvinfer` / `nvinferserver` gan metadata.
5. `nvdsosd` ve overlay.
6. encoder -> rtppay -> udpsink -> RTSP server.

### Control flow

- Live input can sync logic.
- Live output can server logic.
- Lesson nay cho ban phan biet hai lop nay ro hon.

## Implementation Checklist

1. Parse RTSP URI list va output codec/bitrate.
2. Tao source bin, muxer, inference engine, OSD, encoder chain.
3. Set live-source.
4. Set RTSP server mount point.
5. Link pipeline.
6. Attach bus/main loop.
7. Run and cleanup.

## Common Failure Modes

- RTSP source khong bao gio tao pad video hop le.
- Quen `live-source`.
- Encoder/codec khong khop.
- Server mount point khong dung.
- Timestamping confuse system-ts va stream-ts.

## Self-Check

- `rtsp://` source va RTSP output co gi khac nhau ve lifecycle?
- `drop-on-latency` co vai tro gi trong live source?
- RTSP server co nam trong data path khong?
- Ban co the vi sao lesson nay can nhieu than phan hon baseline khong?

## Extensions

- Thu 2 RTSP sources va 1 output.
- Doi codec output.
- Bat/tat stream timestamping va ghi lai output thay doi the nao.
