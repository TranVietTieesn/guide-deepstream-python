# Lesson 09 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/beginning/09_rtsp_source_walkthrough/03_starter.py rtsp://user:pass@host:554/path
```

Day la bai ma upstream source logic bat dau khac han cac bai file source truoc do.
Phan kho nhat khong nam o infer chain, ma nam o `uridecodebin`, dynamic pad, source bin,
va ghost pad.

Neu ban thay bai nay "khong con dung pipeline binh thuong", cam giac do la dung.
Nhung ly do khong phai vi GStreamer bo pipeline thang, ma vi source RTSP co mot phan
noi bo khong on dinh ngay tu dau:

- chua biet chac codec la gi
- chua biet khi nao pad output san sang
- co the sinh nhieu pad khac nhau
- can chon dung decode path phu hop voi DeepStream

## What Is Reused vs What Is New

Phan duoc dung lai:

- `on_message(...)`
- `make_element(...)`
- downstream infer chain
- link vao `nvstreammux.sink_0`

Phan moi:

- `cb_newpad(...)`
- `create_source_bin(...)`
- `Gst.Bin`
- `Gst.GhostPad`
- `live-source=True`

## Mental Model First

### Bai file source truoc do dang de hieu vi source chain co dinh

Neu input la file H264 tho, ban co the tu tin viet tay:

```text
filesrc -> h264parse -> nvv4l2decoder -> nvstreammux
```

Do la mot chain "co dinh":

- ban biet source la file
- ban biet codec la H264
- ban biet parser nao can dung
- ban biet decoder nao can noi tiep
- `src` pad cua cac element chinh thuong da ro rang

### RTSP khien phan source khong con co dinh nua

Voi RTSP, phan dau vao logic hon:

```text
rtsp://... -> rtspsrc -> depay -> parse -> decode -> nvstreammux
```

Nhung chain ben trong nay khong phai luc nao cung nen viet tay trong lesson:

- stream co the la H264 hoac H265
- ben trong RTSP con co network negotiation
- `rtspsrc` va `decodebin` tao pad dong
- DeepStream muon lay ra pad video decode dung memory path

Vi vay bai nay dung `uridecodebin` de "om" phan source phuc tap do.

## `uridecodebin` Dang Giai Quyet Gi?

Hay tam nghi `uridecodebin` nhu mot hop den:

```text
URI vao  ->  uridecodebin  ->  pad video da decode hop le
```

No khong chi "decode video". Trong bai RTSP, no dang giai quyet ca cum van de:

1. Mo URI
2. Xac dinh source phia sau la gi
3. Thuong luong media type
4. Chon demux/depay/parse/decode chain phu hop
5. Sinh output pad khi da san sang

Voi RTSP H264, neu viet tay thi mental model gan dung se la:

```text
rtspsrc -> rtph264depay -> h264parse -> decoder
```

Trong C samples cua DeepStream, ban se thay ho thuc su co luc viet tay doan nay.
Nhung trong Python lesson, muc tieu la hoc source bin va dynamic pad truoc, nen
`uridecodebin` duoc dung de giam bot khoi luong source plumbing.

## `uridecodebin` Khong Lam Bien Mat Pipeline

Dieu quan trong nhat can nho:

- bai nay van la pipeline
- chi la mot phan pipeline duoc tao dong
- va mot phan logic duoc giau ben trong source bin

Hay nhin theo 2 goc:

### Pipeline ma ban tuong tuong ben trong

```text
RTSP URI
  -> source internals
  -> depay
  -> parse
  -> decode
  -> video src pad
```

### Pipeline ma `main(...)` nhin thay

```text
source_bin(src) -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink
```

Source bin chinh la lop vo giup ban khong phai de `main(...)` biet het phan ben trong.

## Vi Sao Phai Co Dynamic Pad?

RTSP va decodebin khong phai luc nao cung co `src` pad san ngay khi element duoc tao.

Thu tu thuc te thuong la:

1. Ban tao `uridecodebin`
2. Ban set `uri`
3. Pipeline bat dau PLAYING
4. `uridecodebin` moi mo source va phan tich media
5. Khi no da co output hop le, no moi phat signal `pad-added`

Noi cach khac:

- voi file source co dinh, ban thuong link ngay
- voi `uridecodebin`, ban phai doi pad xuat hien roi moi quyet dinh link

Do la ly do bai nay co `cb_newpad(...)`.

## Vi Sao Phai Loc `memory:NVMM`?

Khong phai pad nao tu `uridecodebin` cung nen noi vao DeepStream pipeline chinh.

Bai nay muon output pad:

- la video
- da qua decode path phu hop
- nam tren memory path ma DeepStream mong doi

Vi vay callback se kiem tra `caps_features.contains("memory:NVMM")`.

Mental model:

- neu thay NVMM: day la output hop le de dua vao `nvstreammux`
- neu khong thay NVMM: bo qua, vi day khong phai decode path bai nay muon

Neu ban bo buoc loc nay, bai co the van co pad, nhung khong chac la pad dung cho
chuoi DeepStream phia sau.

## Vai Tro Cua Source Bin

`create_source_bin(...)` khong tao "mot pipeline thu hai".
No tao mot **container** cho logic source.

Ban muon phan source RTSP duoc gom thanh 1 khoi:

- ben trong: `uridecodebin`, callback, dynamic pad
- ben ngoai: 1 cong ra don gian ten `src`

Do la vai tro cua `Gst.Bin`.

Neu khong co source bin, `main(...)` se phai:

- canh signal `pad-added`
- giu tham chieu pad trung gian
- biet chi tiet source internals
- link truc tiep phan dong vao muxer

Nhung bai nay co y day ban cach dong goi phan do vao helper.

## Vai Tro Cua Ghost Pad

Ghost pad la "cong noi ra ben ngoai" cua mot `Gst.Bin`.

Trong bai nay:

- source bin duoc tao voi ghost pad `src`
- luc moi tao, ghost pad chua tro vao pad that nao
- khi `uridecodebin` sinh duoc pad video hop le, callback moi `set_target(...)`

Hay nghien theo hinh anh nay:

```text
source_bin.src (ghost pad)
    -> luc dau: chua noi dau ca
    -> sau callback: tro vao decoder_src_pad that ben trong uridecodebin
```

Sau khi `set_target(...)`, tu goc nhin cua pipeline chinh:

- source bin da co `src` pad de noi vao `nvstreammux`
- ben trong source bin co gi, `main(...)` khong can biet nua

## Function-By-Function Walkthrough

### `cb_newpad(decodebin, decoder_src_pad, source_bin)`

Day la noi "bat" dynamic pad va quyet dinh co cho no di tiep hay khong.

Reference code:

```python
caps = decoder_src_pad.get_current_caps()
if not caps:
    caps = decoder_src_pad.query_caps(None)
if not caps:
    return

caps_features = caps.get_features(0)
if not caps_features.contains("memory:NVMM"):
    return

ghost_pad = source_bin.get_static_pad("src")
ghost_pad.set_target(decoder_src_pad)
```

Thu tu nen viet:

1. lay `caps`
2. neu can thi `query_caps(None)`
3. lay `caps_features`
4. check `memory:NVMM`
5. lay ghost pad `src` tu `source_bin`
6. `ghost_pad.set_target(decoder_src_pad)`

Muc tieu callback:

- chi noi nhung pad decode hop le vao pipeline chinh

### Truoc khi di vao 4 khoi: `pad`, `caps`, `caps_features` la gi?

Neu phan nay lam ban roi, hay dung lai va tach 3 khái niệm:

#### `pad`

- co the hieu gan dung la "cong" cua mot element
- `src pad` la cong ra
- `sink pad` la cong vao
- trong callback nay, `decoder_src_pad` la cong output moi sinh ra tu `uridecodebin`

#### `caps`

- la mo ta ve loai du lieu dang chay qua pad
- no tra loi cac cau hoi nhu:
  - day la `video` hay `audio`
  - la `raw` hay compressed
  - format/kich thuoc/framerate hien tai la gi
- noi ngan gon: `caps` tra loi cau hoi "pad nay dang mang du lieu gi?"

#### `caps_features`

- la tap dac tinh bo sung gan voi mot muc caps cu the
- no khong phai field du lieu chinh nhu `width=1920` hay `format=NV12`
- no dung de bieu dien cac yeu cau/representation dac biet, thuong gap nhat o bai nay la
  memory type
- noi ngan gon: `caps_features` tra loi cau hoi "du lieu nay dang nam tren kieu memory/path nao?"

Hay nho mot cap doi:

- `caps` = du lieu gi
- `caps_features` = du lieu do dang o dau / dang o representation nao

### Luong suy nghi cua callback

Callback nay thuc chat dang lam 3 viec:

1. co mot `pad` moi vua xuat hien
2. xac minh pad do co phai output video hop le cho DeepStream hay khong
3. neu hop le, bien no thanh output that cua `source_bin`

Neu viet thanh 1 cau:

- callback khong phai de "lay thong tin cho vui"
- callback dang lam buoc kiem dinh truoc khi cho pad di ra khoi `source_bin`

Hay chia callback nay thanh 4 khoi:

#### Khoi A: Lay caps

- `caps = decoder_src_pad.get_current_caps()`
- neu can, fallback sang `decoder_src_pad.query_caps(None)`

Y nghia:

- ban dang hoi `decoder_src_pad` hien tai dang mang loai du lieu gi
- o muc thuc te, day thuong la:
  - co phai video khong
  - video do dang o dang nao
  - pad nay da negotiated du thong tin de minh xet tiep chua
- neu khong lay duoc thong tin nay, ban chua the quyet dinh co nen noi hay khong

#### Vi sao co 2 lan `if not caps`?

Do day la 2 buoc fallback khac nhau:

1. `get_current_caps()`
   - hoi caps hien tai da duoc negotiate xong chua
2. neu chua co, dung `query_caps(None)`
   - hoi pad nay co the support nhung caps nao, khong dat bo loc bo sung
3. neu thu ca 2 cach van khong lay duoc
   - luc do moi bo qua pad

Hay doc no nhu pseudo-code:

```python
caps = current_caps
neu chua co:
    caps = query_caps_khong_filter
neu van chua co:
    dung lai
```

#### `query_caps(None)` nghia la gi?

- `None` o day nghia la khong dua them bo loc caps nao
- tuc la dang hoi: "neu khong rang buoc gi them, pad nay co the bao nhung caps nao?"
- neu truyen mot `Gst.Caps` cu the vao thay vi `None`, nghia se la:
  "trong so cac caps nay, pad co phu hop voi cai nao?"

#### Khoi B: Lay features

- doc `caps_features`
- check `memory:NVMM`

Y nghia:

- bai nay muon decode path phu hop voi DeepStream/NVIDIA memory
- khong phai pad nao tu `uridecodebin` cung hop le de di tiep

#### `caps.get_features(0)` la gi?

- `GstCaps` co the chua 1 hoac nhieu muc caps
- moi muc caps co the co `features` rieng
- `0` la index cua muc caps dau tien
- trong bai nay, ta dang lam viec voi current caps da duoc negotiate, thuong chi co 1 muc,
  nen index `0` la thu hop ly nhat

Mental model don gian:

```text
caps
  structure[0] = video/x-raw
  features[0] = memory:NVMM
```

Hay tach ro:

- `video/x-raw` la media type / structure
- `memory:NVMM` la feature gan voi structure do

#### `memory:NVMM` la gi?

- day la caps feature bao rang buffer dang nam tren memory path cua NVIDIA
- no khong phai codec
- no khong phai media type
- no la thong tin ve cach buffer duoc bieu dien trong bo nho

Trong DeepStream, dieu nay quan trong vi:

- downstream nhu `nvstreammux`, `nvinfer`, `nvvideoconvert` thuong mong doi du lieu di theo
  duong memory NVIDIA
- neu pad khong co `memory:NVMM`, do co the la software/system-memory path
- bai nay muon nhan dung output pad cho chuoi GPU pipeline, nen phai loc

Mot cap so sanh de de nho:

- `video/x-raw, format=NV12`
  - la video raw, nhung chua noi gi ve memory path NVIDIA
- `video/x-raw(memory:NVMM), format=NV12`
  - van la video raw, nhung dang o dung memory path ma DeepStream thich

Neu viet gon:

- `caps` cho ban biet "day la video raw"
- `caps_features` cho ban biet "video raw nay co dang o NVMM khong"

#### Khoi C: Lay ghost pad

- lay `src` ghost pad tu `source_bin`

Y nghia:

- day la cong ra co dinh ma `main(...)` se dung
- callback khong link thang vao muxer, callback chi "day" pad hop le ra cong do

#### Vi sao callback khong link truc tiep vao `nvstreammux`?

Vi callback chi phu trach source internals.

Kien truc bai nay tach lam 2 lop:

- `create_source_bin(...)` + `cb_newpad(...)`
  - chon pad that ben trong source
- `main(...)`
  - coi `source_bin` nhu mot source co `src` pad de link vao muxer

Dieu nay giup `main(...)` khong phai biet chi tiet ben trong `uridecodebin`.

#### Khoi D: Set target

- `ghost_pad.set_target(decoder_src_pad)`

Y nghia:

- day la khoanh khac source bin chinh thuc co output that
- tu luc nay `source_bin.src` da dan den pad decode hop le

#### `set_target(...)` dang lam gi?

- ghost pad duoc tao tu truoc bang `new_no_target(...)`
- luc dau no la mot cong ra "rong"
- `set_target(decoder_src_pad)` gan cong ra rong do voi pad that vua qua buoc kiem dinh

Hay hinh dung:

```text
truoc callback:
source_bin.src -> chua tro vao dau ca

sau callback:
source_bin.src -> decoder_src_pad hop le
```

Day la ly do `main(...)` co the lay `source_bin.get_static_pad("src")` tu ben ngoai,
du ben trong source bin moi vua quyet dinh xong pad that nao se duoc lo ra ngoai.

Noi ngan gon:

- callback nhan pad dong
- neu pad do hop le thi noi no vao ghost pad

Pseudo-code:

```python
lay caps
lay features
neu khong phai NVMM: bo qua
lay ghost pad src cua source_bin
set target cua ghost pad = decoder_src_pad
```

### Toan bo doan `47-62` dang lam gi?

Neu doc mot mach tu tren xuong, doan code nay co the duoc dien giai thanh:

1. `uridecodebin` vua sinh ra mot `src pad` moi
2. ta xem pad do dang mang du lieu gi qua `caps`
3. ta xem du lieu do co dang o dung memory path cho DeepStream khong qua `caps_features`
4. neu khong dat, bo qua pad
5. neu dat, lay ghost pad `src` cua `source_bin`
6. gan ghost pad nay tro vao `decoder_src_pad`
7. tu luc nay, `source_bin` da co output that de `main(...)` noi vao `nvstreammux`

Neu can mot cau tong ket duy nhat:

- `caps` va `caps_features` khong phai de log cho vui
- chung la buoc kiem dinh de quyet dinh pad nao duoc phep tro thanh output cua `source_bin`

### `create_source_bin(index, uri)`

Ham nay nen:

- tao `Gst.Bin`
- tao `uridecodebin`
- set `uri`
- connect `pad-added`
- add `uridecodebin` vao bin
- tao ghost pad `src`
- add ghost pad vao bin
- `return source_bin`

Hay doc ham nay theo 3 lop:

1. Tao mot `Gst.Bin` de gom logic source
2. Tao `uridecodebin`, set `uri`, connect callback
3. Tao ghost pad `src` de lo pad hop le ra ngoai

Mau tu duy:

```python
source_bin = Gst.Bin.new(...)
uri_decode_bin = make_element("uridecodebin", ...)
uri_decode_bin.set_property("uri", uri)
uri_decode_bin.connect("pad-added", cb_newpad, source_bin)
source_bin.add(uri_decode_bin)
ghost_pad = Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC)
source_bin.add_pad(ghost_pad)
return source_bin
```

Y nghia kien truc:

- `create_source_bin(...)` la noi "lap rap source"
- `main(...)` la noi "lap rap pipeline chinh"

Tach 2 vai tro nay ra se giup bai de doc hon rat nhieu.

## Vi Sao Khong Link Truc Tiep Trong `main(...)`?

Vi tai thoi diem `main(...)` dang tao pipeline:

- ban chua co `decoder_src_pad` that
- `uridecodebin` chua phat sinh pad
- ban chua biet pad nao la pad cuoi cung hop le

Nen `main(...)` chi lam phan on dinh:

1. tao `source_bin`
2. xin `sink_0` tu `nvstreammux`
3. lay `source_bin.src`
4. link `source_bin.src -> nvstreammux.sink_0`

Con phan noi bo ben trong source bin se tu hoan tat sau, khi `pad-added` xay ra.

## Main Flow: Nen Nghi The Nao

Sau khi xong 2 helper tren, `main(...)` nen de doc theo thu tu:

1. tao `source_bin`
2. tao downstream elements
3. set property cho muxer, pgie, sink
4. add tat ca vao pipeline
5. xin `sink_0`
6. lay `source_bin.src`
7. link vao muxer
8. link downstream

Neu callback lam ban roi, hay nho `main(...)` van kha don gian. Doan kho nhat da duoc
gom vao `cb_newpad(...)` va `create_source_bin(...)`.

## Why `live-source=True` Matters Here

Trong bai nay, `streammux` can biet source la live:

- de xu ly timing hop ly hon
- de mental model cua pipeline khop voi RTSP source
- de batching khong bi nghi nhu dang doc file offline

Ban chua can hoc sau ve timestamp, nhung dung bo qua property nay nhu mot dong "de co".
Trong RTSP, day la mot phan khai bao y nghia cua source.

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `cb_newpad(...)`
4. Hoan thanh `create_source_bin(...)`
5. Tao downstream
6. Link source bin vao muxer
7. Chay pipeline

Thu tu nay khong chi de de code.
No con phan anh dung luong tu duy cua bai:

- xong source internals truoc
- roi moi noi source vao pipeline chinh

## Starter Mapping

### TODO 1-2

- `on_message`, `make_element`

### TODO 3

- `cb_newpad(...)`
- phan kho nhat cua bai, nen lam theo thu tu caps -> features -> ghost pad -> set target
- neu ban khong ro callback nay, hay tam bo qua `main(...)` va chi tap trung vao 1 cau hoi:
"pad dong nao duoc phep tro thanh output cua source bin?"

### TODO 4

- `create_source_bin(...)`
- coi day la helper de main gon hon, khong phai mot pipeline rieng thu hai
- sau TODO nay, ban da co mot source "nhin tu ngoai thi binh thuong", du ben trong no van dong

### TODO 5

- tao downstream elements

### TODO 6

- set property cho muxer, pgie, sink
- nho `live-source=True`

### TODO 7

- add element vao pipeline

### TODO 8

- xin `sink_0`
- lay `source_bin.src`
- link vao muxer
- day la luc source bin tro thanh "mot source binh thuong" tu goc nhin cua pipeline chinh

### TODO 9

- link downstream

## Syntax Notes

- `Gst.Bin.new(name)` tao mot container element
- `Gst.GhostPad.new_no_target(...)` tao ghost pad chua noi den pad that
- `ghost_pad.set_target(...)` la luc source bin "loi src ra ngoai"
- `caps_features.contains("memory:NVMM")` dung de loc decode path phu hop
- `pad-added` callback co the duoc goi nhieu lan; bai nay chi noi pad hop le

## Comparison With A Handwritten RTSP Chain

Neu ban muon doi chieu voi cach "pipeline thuong", hay nghi nhu sau:

### Cach viet tay de hieu y tuong

```text
rtspsrc -> rtph264depay -> h264parse -> decoder -> nvstreammux
```

### Cach lesson nay day

```text
uridecodebin inside source_bin -> ghost pad src -> nvstreammux
```

Khac nhau o cho:

- cach viet tay lo ro tung plugin
- cach cua lesson giau source internals de day ban dynamic pad va source bin

Ban khong mat di hieu biet ve pipeline.
Ban dang hoc mot abstraction ma DeepStream dung rat nhieu khi lam source da dinh dang.

## Common Confusions

### "Sao khong thay `rtph264depay` trong code?"

Vi bai nay khong day source chain bang cach viet tay.
No day cach de `uridecodebin` lo phan nay, con ban tap trung vao:

- pad-added
- source bin
- ghost pad

### "Neu da co `uridecodebin`, sao van can callback?"

Vi `uridecodebin` khong dua san cho ban mot `src` pad co dinh tu dau.
Ban van phai bat luc output pad xuat hien va quyet dinh co dung no hay khong.

### "Ghost pad co phai la pad that khong?"

Khong. No la pad dai dien cho pad that ben trong bin.
No giup ben ngoai thay mot interface on dinh.

## Mini Checkpoints

- Sau TODO 3: ban biet pad dong nao se duoc phep di tiep
- Sau TODO 4: source bin da co `src` ghost pad
- Sau TODO 8: source RTSP da noi vao muxer thanh cong

## Self-Check

- Neu viet tay source chain RTSP H264, ban se mong doi nhung plugin nao xuat hien?
- Tai sao `main(...)` khong the lay ngay `decoder_src_pad` de link vao muxer?
- Tai sao bai nay can ghost pad thay vi cho `main(...)` biet het source internals?
- `memory:NVMM` dang loc theo "media type" hay dang loc theo "memory/decode path"?

