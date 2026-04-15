# Lesson 02: USB Camera

Lesson nay bat dau khi source khong con la file H.264 nua. Ban phai xu ly raw
camera frames va day chung qua NVMM truoc khi vao DeepStream core.

## What You Will Build

- Pipeline:
  `v4l2src -> capsfilter -> videoconvert -> nvvideoconvert -> capsfilter -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink`
- Input: mot thiet bi `/dev/video*`
- Config: `apps/deepstream-test1-usbcam/dstest1_pgie_config.txt`
- Expected outcome: hieu vi sao raw camera source can them converter va caps
  filter truoc khi vao NVMM

## Why It Matters

USB camera khong di vao DeepStream giong file H.264.

- Source la raw video, khong phai compressed bitstream
- Mot so camera tra ra format ma `nvvideoconvert` khong an thang duoc
- `videoconvert` giup "trung gian" negotiation
- `capsfilter` buoc stream vao dung shape truoc khi vao NVMM

Lesson nay day ban mot pattern rat thuc te:

1. raw input khong phai luc nao cung "ve la xong"
2. thi truong DeepStream can NVMM vao dung cho
3. neu source khac file, skeleton van giong, nhung bridge se khac

## Compared to Lesson 01

Phan giu nguyen:

- van co `nvstreammux`
- van co `nvinfer`
- van co `nvdsosd`
- van co bus watch va cleanup lifecycle

Phan moi:

- source la `v4l2src`
- co them `videoconvert`
- co them 2 `capsfilter`
- phai nghien nghi ro hon ve raw caps va NVMM caps

Lesson 01 day ban "file -> DeepStream".
Lesson 02 day ban "camera raw -> DeepStream".

## New Concepts In This Lesson

### `v4l2src`

- Element doc tu USB camera hoac thiet bi V4L2.
- No tra frame raw, khong phai H.264 bitstream.

### `capsfilter`

- Dung de ep media type va format.
- Trong bai nay no co 2 vai tro:
  - giu raw input o dung framerate/caps
  - buoc dong du lieu sau `nvvideoconvert` vao `video/x-raw(memory:NVMM)`

### `videoconvert`

- Trung gian cho format raw.
- Khong lam DeepStream magic; no chi giup camera raw negotiate de dang hon.

### `nvvideoconvert`

- Buoc dich sang NVMM.
- Day la cuoc doi tu "raw CPU-friendly buffer" sang buffer phu hop voi
  DeepStream/GPU pipeline.

### `sync = False`

- Camera feed va sink hien thi co the bi am thanh/late frame neu sync cham.
- Lesson nay giup ban de thich nghiem hanh vi live source hon.

## Mental Model

### Data plane

1. `v4l2src` lay frame tu camera.
2. `capsfilter` siem soat raw format.
3. `videoconvert` chuyen doi format raw neu can.
4. `nvvideoconvert` day buffer vao NVMM.
5. `nvstreammux` nhan buffer da san sang theo kieu DeepStream.
6. `nvinfer` gan metadata.
7. `nvdsosd` ve overlay.

### Control plane

- Bus va main loop khong doi theo loai source.
- Van can `EOS`, `ERROR`, va cleanup.

### Key transition

- Lesson 01: compressed file -> decoder -> frame
- Lesson 02: raw camera frame -> raw converter -> NVMM -> DeepStream

## Implementation Checklist

1. Parse `/dev/video*`.
2. `Gst.init(None)` va tao `PlatformInfo()`.
3. Tao source, 2 capsfilter, 2 converter, mux, infer, OSD, sink.
4. Set caps cho raw input va NVMM output.
5. Set `device`, `batch-size`, `width`, `height`, `sync = False`.
6. Add tat ca element vao pipeline.
7. Link source -> caps -> videoconvert -> nvvideoconvert -> caps.
8. Xin request pad tu muxer va link pad-level vao `sink_0`.
9. Link phan downstream con lai.
10. Chay bus/main loop va cleanup.

## Common Failure Modes

- Device path khong dung.
- Camera tra ve raw format khong duoc `videoconvert` ho tro tot.
- Quen NVMM caps sau `nvvideoconvert`.
- Quen `sync=False` lam output live cam bi giat/tre.
- Quen set `config-file-path` cho `nvinfer`.

## Self-Check

- Vi sao lesson nay khong can `h264parse`?
- Vi sao `videoconvert` va `nvvideoconvert` khong trung nhau?
- Dau nao cho ban biet buffer da vao NVMM?
- Neu bo `capsfilter` sau `nvvideoconvert`, sao pipeline co the fail o muc
  negotiation?

## Extensions

- Thu doi camera resolution va quan sat negotiation.
- Bo `videoconvert` va ghi lai format nao bi fail.
- In them caps chain truoc va sau NVMM bridge.
- Thu `sync=True` va ghi lai cam giac ve live frame.
