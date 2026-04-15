# Lesson 03: RTSP Out

Lesson nay chuyen output tu local render sang RTSP stream. Day la level cuoi
trong baseline topic, vi no cho thay khong chi "hien ket qua", ma con "phat
ket qua" ra ngoai pipeline.

## What You Will Build

- Data path:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> nvvideoconvert -> capsfilter -> encoder -> rtppay -> udpsink`
- RTSP sidecar: `GstRtspServer` exposes the UDP stream via the media factory
- Input: mot file H.264
- Config: `apps/deepstream-test1-rtsp-out/dstest1_pgie_config.txt`
- Expected outcome: hieu cach DeepStream encode va publish output qua RTSP

## Why It Matters

RTSP out la buoc de dua inference result ra ngoai app local.

- `nvdsosd` van ve bbox/text vao frame
- `nvvideoconvert` va `capsfilter` chuan bi frame truoc encode
- `encoder` chuyen frame thanh bitstream
- `rtppay` dong goi RTP
- `GstRtspServer` expose stream ra network

Lesson nay cho ban thay mot phan rat quan trong trong DeepStream:

- inference khong phai endpoint cuoi cung
- overlay khong phai render cuoi cung
- ket qua co the duoc "ship" ra network nhu mot media service

## Compared to Lesson 01

Phan giu nguyen:

- `filesrc -> h264parse -> nvv4l2decoder`
- request pad vao `nvstreammux`
- `nvinfer` va `nvdsosd`
- bus watch va cleanup

Phan moi:

- them `nvvideoconvert -> capsfilter -> encoder -> rtppay -> udpsink`
- them `GstRtspServer`
- them tu duy egress: pipeline khong chi render, ma con serve stream

Lesson 01 day ban "detected frame de hien thi".
Lesson 03 day ban "detected frame de phat di".

## New Concepts In This Lesson

### `encoder`

- Bien frame thanh bitstream H.264.
- Neu khong co encoder, `rtppay` khong co gi de dong goi.

### `rtppay`

- Dong goi bitstream thanh RTP packets.
- RTSP server thuong serve RTP, khong serve raw frame.

### `udpsink`

- Dua RTP packets sang port ma RTSP server se lay vao.
- Trong sample nay, `udpsink` khong phat truc tiep cho end user;
  no cap du lieu cho `GstRtspServer` qua launch string.

### `GstRtspServer`

- Server layer, khong phai inference layer.
- No cho phep app cua ban tro thanh mot RTSP endpoint co the connect tu client.

### `capsfilter` truoc encoder

- Giup frame co dung format truoc khi encode.
- Neu format sai, encoder se fail hoac negotiate sai.

## Mental Model

### Data plane

1. Source -> decode -> mux -> infer -> OSD.
2. Frame sau OSD duoc chuyen sang format phu hop cho encoder.
3. Encoder -> RTP payloader -> UDP sink.
4. RTSP server expose stream da dong goi.

### Control plane

- Bus van theo doi `EOS` va `ERROR`.
- RTSP server la mot service object, khong thay the main loop.

### Kieu output

- Lesson 01/02: output local sink
- Lesson 03: output network stream

## Implementation Checklist

1. Parse input file.
2. Tao source, parser, decoder, mux, infer, OSD, encoder, payloader, sink.
3. Set `bitrate`, `codec`, `insert-sps-pps`, `sync`.
4. Add element vao pipeline va link theo thu tu.
5. Tao `GstRtspServer` va mount point.
6. Gan `udpsrc` launch string vao RTSP media factory.
7. Add pad probe neu can doc metadata.
8. Chay loop va cleanup.

## Common Failure Modes

- Encoder khong ton tai tren platform hien tai.
- `rtph264pay` / `rtph265pay` khong khop codec.
- Quen `insert-sps-pps` khi can H.264/H.265 stream on-the-fly.
- Quen `GstRtspServer` introspection package.
- RTSP port da bi dung boi process khac.
- Quen roi data vao `udpsink` port ma RTSP factory dang listen.

## Self-Check

- Output cua app da di vao network hay van chi render local?
- `rtppay` co nam sau encoder khong?
- `GstRtspServer` co can tham gia vao data plane khong?
- Neu client RTSP khong connect duoc, ban co biet nhin vao `encoder`,
  `payloader`, hay `server` de debug khong?

## Extensions

- Doi codec giua H.264 va H.265.
- Thu thay doi bitrate va quan sat output.
- Doi sink local thanh RTSP va ghi lai su khac nhau trong lifecycle.
- Thu dong thoi local render va RTSP out de so sanh hai output path.
