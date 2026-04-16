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

Mot diem de bi roi la: bai nay khong "bo pipeline binh thuong".
No van la pipeline, nhung phan source RTSP khong con la mot chain co dinh de viet tay
ngay tu dau.

## Compared to Lesson 08

Phan duoc giu nguyen:

- downstream infer chain
- `nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink`
- request pad vao `nvstreammux`

Phan moi trong lesson 09:

- source khong con la `filesrc`
- pad co the xuat hien dong
- can `source bin` va `ghost pad`
- can callback `pad-added`
- can nghi theo tu duy live source

Neu lesson 08 day ban "nhieu file source vao muxer", thi lesson 09 day ban "mot live
source dong vao muxer" the nao.

## New Concepts In This Lesson

### `uridecodebin`

- Element nay tu tim decode chain phu hop dua tren URI.
- RTSP thuong can cach tiep can nay thay vi hard-code `filesrc -> h264parse`.
- Hay tam nghi no la mot lop abstraction cho phan source:
  mo URI, xac dinh media, chon depay/parse/decode path, roi moi lo output pad ra ngoai.

### Pipeline viet tay vs pipeline duoc goi gon

Neu viet tay source RTSP H264, ban thuong hinh dung:

```text
rtspsrc -> rtph264depay -> h264parse -> decoder -> nvstreammux
```

Trong lesson nay, phan do duoc goi gon thanh:

```text
uridecodebin(source-bin) -> nvstreammux -> ...
```

Dieu nay khong co nghia la nhung plugin o giua "khong ton tai".
No chi co nghia la bai hoc muon tap trung vao:

- dynamic pad
- source bin
- ghost pad
- live source mental model

### Dynamic pad

- Pad khong co san tu dau.
- No xuat hien khi `uridecodebin` da biet media type va da tao decode path.

### Source bin

- Day la mot `Gst.Bin` boc logic source thanh mot khoi rieng.
- De ben ngoai, ban chi can coi no nhu mot element co `src` pad.

### Ghost pad

- Ghost pad la pad "lo ra ben ngoai" cua bin.
- No giup pipeline chinh khong can biet chi tiet ben trong source bin.

### `live-source=True`

- Bao cho muxer rang day la source live.
- Bai nay chi can hieu o muc khai niem: timestamp va batching voi live source can xu ly
khac file source.

## Must Understand Now vs Know For Later

Can hieu ngay o bai nay:

- RTSP thuong can `uridecodebin`
- pad-added callback la noi ban quyet dinh co noi pad vao pipeline chinh hay khong
- source bin + ghost pad giup rest of pipeline don gian hon
- `live-source=True` la mot phan cua mental model cho live stream

Chi can biet mat o bai nay, chua can hieu sau:

- latency tuning sau hon cua RTSP
- reconnect logic
- tat ca bien the caps/features co the gap

## Mental Model

- `uridecodebin` tao pad dong khi no biet media type
- source bin dung de boc logic source thanh mot khoi co `src` ghost pad
- `cb_newpad(...)` la noi ra quyet dinh pad nao hop le de noi vao pipeline chinh
- `streammux.live-source=True` giup muxer xu ly source live dung hon

Hay nho theo mot cau:

- decode bin tao pad dong
- callback quyet dinh co nhan pad do hay khong
- ghost pad lo pad hop le ra ngoai source bin
- pipeline chinh chi viec noi source bin vao muxer

Neu muon nho theo timeline, hay doc bai theo thu tu nay:

1. Tao `uridecodebin`
2. Set `uri`
3. Pipeline chuyen sang PLAYING
4. `uridecodebin` moi phan tich stream
5. Pad video hop le moi xuat hien
6. Callback noi pad do vao ghost pad cua source bin
7. Tu ben ngoai, `source_bin.src` tro thanh output de noi vao muxer

## Why Source Bin Exists

Neu khong co source bin, `main(...)` se phai xu ly truc tiep logic dynamic pad cua
`uridecodebin`, khien pipeline chinh roi hon nhieu.

Source bin giai quyet bai toan do:

- ben trong bin: xu ly source RTSP, callback, ghost pad
- ben ngoai bin: chi thay mot `src` pad de noi vao muxer

Day la cach lesson bien "source RTSP dong" thanh "mot source nhin tu ngoai kha on dinh".

## Live-Source Mental Model

Khac voi file source:

- RTSP co the khong co EOS "dep" nhu file
- timing phu thuoc vao stream live
- muxer can biet day la live source de xu ly hop ly hon

Ban chua can hoc sau ve clocking o bai nay. Chi can nho `live-source=True` khong phai
mot property ngau nhien.

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
- pad-added callback chay nhung ban noi nham pad audio:
pipeline van roi va kho nhan ra vi sao downstream khong nhan duoc frame video

## Common Confusions

### "Tai sao khong thay `rtph264depay` trong lesson?"

Vi lesson nay khong day source chain bang cach viet tay tung plugin.
No dung `uridecodebin` de gop phan source internals lai, nham day ban abstraction ma
DeepStream dung rat nhieu trong cac source phuc tap hon file source.

### "Neu da co `uridecodebin`, tai sao van can `pad-added`?"

Vi `uridecodebin` khong dua san cho ban mot `src` pad on dinh ngay khi vua tao element.
Ban van phai doi den luc no xac dinh duoc output phu hop.

### "Ghost pad dang giai quyet bai toan gi?"

No cho phep `main(...)` lam viec voi source bin nhu voi mot source binh thuong,
thay vi phai biet het chi tiet source internals ben trong.

## Self-Check

1. Tai sao RTSP khong con dung `filesrc -> h264parse` truc tiep?
2. Ghost pad cua source bin giai quyet bai toan gi?
3. Vi sao phai nghe `pad-added`?
4. `live-source=True` co y nghia gi o muc khai niem?

## Extensions

- Thu bo `live-source=True` va ghi lai hanh vi.
- Doi `fakesink` thanh sink hien thi neu muon xem live output.
- Nghien cuu them latency qua `rtspsrc` neu can truy cap sau hon vao source.

Neu can giai thich chi tiet hon tung callback va tung dong code trong starter,
chuyen sang `02_coding_guide.md`.

