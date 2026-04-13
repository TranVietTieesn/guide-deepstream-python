# Lesson 09: RTSP Source Walkthrough

Neu ban chua quen syntax Python/GStreamer/DeepStream, doc them
`02_coding_guide.md` truoc khi mo `03_starter.py`.

## What You Will Build

- Pipeline y tuong:
  `uridecodebin(source-bin) -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> fakesink`
- Expected outcome: hieu tai sao RTSP thuong can `uridecodebin`, source bin,
  ghost pad, va `live-source=True`

## Why It Matters

RTSP khac file source o 3 diem lon:

- source la live
- pad thuong xuat hien dong
- decode path co the phuc tap hon `filesrc -> h264parse`

Neu ban hieu bai nay, ban se biet vi sao sample RTSP trong DeepStream thuong khong
viet theo kieu source file don gian.

## Mental Model

- `uridecodebin` tao pad dong khi no biet media type
- source bin dung de boc logic source thanh mot khoi co `src` ghost pad
- `cb_newpad(...)` la noi ra quyet dinh pad nao hop le de noi vao pipeline chinh
- `streammux.live-source=True` giup muxer xu ly source live dung hon

## Implementation Checklist

1. Parse RTSP URI.
2. Tao helper `create_source_bin(...)`.
3. Trong source bin:
   - tao `uridecodebin`
   - set `uri`
   - connect `pad-added`
   - tao ghost pad `src`
4. Trong callback `cb_newpad(...)`:
   - lay caps
   - check NVMM
   - set target cho ghost pad
5. Tao downstream pipeline va link vao muxer.
6. Set `live-source=True`.
7. Chay pipeline.

## Common Failure Modes

- URI khong bat dau bang `rtsp://`
- pad moi tao khong phai NVMM
- ghost pad khong duoc set target
- bo `live-source=True` lam timestamp/batching co van de

## Self-Check

1. Tai sao RTSP khong con dung `filesrc -> h264parse` truc tiep?
2. Ghost pad cua source bin giai quyet bai toan gi?
3. Vi sao phai nghe `pad-added`?
4. `live-source=True` co y nghia gi o muc khai niem?

## Extensions

- Thu bo `live-source=True` va ghi lai hanh vi.
- Doi `fakesink` thanh sink hien thi neu muon xem live output.
- Nghien cuu them latency qua `rtspsrc` neu can truy cap sau hon vao source.
