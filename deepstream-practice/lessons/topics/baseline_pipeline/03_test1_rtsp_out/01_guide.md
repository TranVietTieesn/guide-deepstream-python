# Lesson 03: RTSP Out

Lesson nay nang cap output tu local display sang network streaming. Muc tieu
khong con la "nhin thay frame tren may local", ma la "publish stream da infer
ra RTSP endpoint de app khac co the subscribe".

## Learning Objectives

Sau bai nay, ban can lam duoc:

1. Giai thich duoc 2 lop trong he thong:
   - **Data plane**: xu ly media frame trong pipeline.
   - **Service plane**: publish stream qua `GstRtspServer`.
2. Dung duoc chain RTSP out:
   `... -> nvvideoconvert -> capsfilter -> encoder -> rtppay -> udpsink`.
3. Tao duoc RTSP endpoint `/ds-test` va mo bang client.
4. Khoanh vung bug dung cho tung nhom: encode bug, RTP bug, RTSP server bug.

## What You Will Build

- Input: 1 file H.264.
- Inference config: `apps/deepstream-test1-rtsp-out/dstest1_pgie_config.txt`.
- Pipeline:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> nvvideoconvert -> capsfilter -> encoder -> rtppay -> udpsink`
- RTSP sidecar: `GstRtspServer` doc RTP tu UDP port va expose endpoint.
- Output mong doi: stream truy cap duoc qua `rtsp://<host>:8554/ds-test`.

## Why This Lesson Is Important

Trong project thuc te, inference khong ket thuc o local render. Ban thuong can:

- gui stream toi dashboard monitoring,
- feed stream cho recorder hoac analytics service khac,
- cho phep client tu xa xem ket qua detect.

Lesson nay day tu duy **egress**: inference la mot stage trong media service,
khong phai output cuoi cung.

## Architecture: Data Plane vs Service Plane

### 1) Data Plane (video processing)

1. `filesrc -> h264parse -> nvv4l2decoder`: doc va decode stream.
2. `decoder -> nvstreammux`: dua frame vao batch DeepStream.
3. `nvinfer -> nvdsosd`: detect va ve overlay.
4. `nvvideoconvert + capsfilter`: dua frame ve format encoder chap nhan.
5. `encoder -> rtppay -> udpsink`: bien frame thanh RTP packet va day ra UDP.

### 2) Service Plane (stream publishing)

1. `GstRtspServer` mo service port (mac dinh 8554).
2. `RTSPMediaFactory` khai bao `udpsrc` launch string.
3. Mount endpoint `/ds-test` de client connect.

Luu y: `GstRtspServer` khong thay the pipeline processing; no chi la lop serve.

## New Components (Practical View)

### `capsfilter` truoc encoder

- Ep format dung truoc khi encode (vi du I420, NVMM).
- Sai format -> pipeline co the fail khi negotiate caps.

### `encoder` (`nvv4l2h264enc` / `nvv4l2h265enc`)

- Chuyen raw frame sau OSD thanh compressed bitstream.
- Khong co encoder -> `rtppay` khong co du lieu de dong goi.

### `rtppay` (`rtph264pay` / `rtph265pay`)

- Dong goi bitstream thanh RTP packet.
- Phai khop voi codec encoder.

### `udpsink`

- Day RTP packet den port ma RTSP factory doc vao.
- Day la "noi trung gian" giua pipeline va RTSP server.

### `GstRtspServer`

- Expose stream ra network duoi dang RTSP URL.
- Quan ly session client, mount point, va protocol handling.

## End-to-End Flow You Should Memorize

1. Media processing tao RTP packet va gui vao UDP port.
2. RTSP server lay du lieu tu `udpsrc` tuong ung port do.
3. Client ket noi `rtsp://host:8554/ds-test`.
4. Client nhan stream inference output (da co OSD overlay).

## Run And Validate

### Chay app

- Truyen duong dan file H.264 hop le.
- Dam bao ton tai `dstest1_pgie_config.txt`.

### Mo stream bang client

- VLC/GStreamer/ffplay ket noi:
  `rtsp://<host>:8554/ds-test`

### Dau hieu thanh cong

- App khong crash khi PLAYING.
- Co client ket noi duoc endpoint.
- Client thay stream co overlay detect.

## Debug Playbook (When Things Break)

### Khong tao duoc element

- Kiem tra plugin ton tai (`nvv4l2h264enc`, `rtph264pay`, ...).
- Xac dinh dung factory name theo platform.

### Client mo RTSP nhung khong co hinh

- Kiem tra `udpsink.port` co khop launch string `udpsrc port=...` khong.
- Kiem tra `rtppay` co khop codec (`H264` vs `H265`) khong.

### Client connect fail ngay tu dau

- Kiem tra RTSP port da bi chiem chua.
- Kiem tra mount point co dung `/ds-test`.

### Hinh co giat / kho mo

- Thu tang `encoder.bitrate`.
- Kiem tra `insert-sps-pps=1` da bat chua.
- Thu doi `sync` tuy use-case realtime hay playback.

## Common Failure Modes

- Quen `insert-sps-pps` cho stream live.
- Dung sai cap `encoder` va `rtppay`.
- Port UDP trong pipeline khong khop port trong RTSP factory.
- Chua cai introspection package cho `GstRtspServer`.
- Cau hinh mux/encoder khong phu hop platform.

## Self-Check Questions

1. Neu bo `GstRtspServer`, pipeline con xu ly frame duoc khong?
2. Neu bo `encoder`, sao `rtppay` khong hoat dong dung?
3. Ban co biet phan nao debug trong data plane, phan nao debug trong service plane?
4. Ban co the doi H.264 sang H.265 va cap nhat dung tat ca diem lien quan khong?

## Suggested Extensions

1. Chuyen qua H.265 (`encoder + payloader + encoding-name`).
2. Thu 3 muc bitrate va so sanh quality/latency.
3. Doi RTSP port va xac minh endpoint moi.
4. Thu vua local render vua RTSP out de so sanh hai output path.
