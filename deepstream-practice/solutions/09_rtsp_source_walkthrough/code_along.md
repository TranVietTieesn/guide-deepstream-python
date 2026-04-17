# Lesson 09: RTSP Source Walkthrough - Code Along

File nay duoc viet de ban vua doc vua code trong
`deepstream-practice/solutions/09_rtsp_source_walkthrough/scratch.py`.

Muc tieu cua file nay khong phai la dua dap an ngay lap tuc.
Muc tieu la:

- chia bai thanh tung buoc nho
- moi buoc deu giai thich ro "tai sao phai code dong nay"
- doc den dau co the code den do
- xong moi di tiep

Neu ban dang hoc bai 09 lan dau, hay lam theo dung trinh tu trong file nay.
Dung nhay thang den cuoi roi paste toan bo solution.

## Cach hoc file nay

Moi section deu co cung mot nhiep:

1. Doc muc tieu cua buoc
2. Mo `scratch.py`
3. Code dung phan section yeu cau
4. Doc mini checkpoint
5. Chi khi da hieu thi moi qua section ke tiep

## Bai nay dang xay dung gi?

Pipeline y tuong:

```text
uridecodebin(source-bin) -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> fakesink
```

Nhung de code duoc bai nay, ban can giu 2 timeline rieng biet trong dau:

### Timeline A: Setup timeline

Day la nhung gi ta tao truoc khi pipeline chay:

- tao `source_bin`
- tao `uridecodebin`
- connect `pad-added`
- tao ghost pad `src`
- tao `streammux`, `pgie`, `nvvidconv`, `nvosd`, `sink`
- add vao pipeline
- link `source_bin.src` vao `nvstreammux.sink_0`

### Timeline B: Runtime timeline

Day la nhung gi chi xay ra sau khi pipeline chuyen sang `PLAYING`:

- `uridecodebin` mo RTSP URI
- no phan tich stream
- no sinh `decoder_src_pad`
- callback `cb_newpad(...)` duoc goi
- callback kiem tra `caps` va `memory:NVMM`
- neu hop le, ghost pad `src` cua `source_bin` moi duoc gan target that

Neu ban tron 2 timeline nay vao nhau, bai nay se rat roi.

## Truoc khi code: mo 3 file nay

Trong luc hoc, ban nen mo song song:

- `deepstream-practice/solutions/09_rtsp_source_walkthrough/scratch.py`
- `deepstream-practice/lessons/beginning/09_rtsp_source_walkthrough/03_starter.py`
- `deepstream-practice/lessons/beginning/09_rtsp_source_walkthrough/05_reference.py`

Tu duy de hoc:

- `starter.py` cho biet TODO va khung bai
- `scratch.py` la noi ban tu code
- `05_reference.py` chi dung khi can doi chieu

## Step 1: Hoan thanh `on_message(...)`

### Ban sap code gi?

Ban se hoan thanh ham xu ly bus message.
Buoc nay giong cac bai truoc, khong phai phan kho nhat cua RTSP.

### Vi sao buoc nay ton tai?

Pipeline GStreamer gui message len bus khi:

- het du lieu `EOS`
- co loi `ERROR`

Neu khong xu ly bus:

- ban kho biet pipeline dang fail o dau
- `loop.run()` se khong thoat dung cach khi loi xay ra

### Code actions

Trong `scratch.py`, hoan thanh:

```python
def on_message(bus, message, loop):
```

Viec can lam:

1. lay `message.type`
2. neu la `Gst.MessageType.EOS`:
   - in thong bao
   - `loop.quit()`
3. neu la `Gst.MessageType.ERROR`:
   - `message.parse_error()`
   - in `err`
   - neu co `debug` thi in them
   - `loop.quit()`
4. cuoi ham `return True`

### Truoc buoc nay da co gi?

- chi moi co khung file
- chua co helper nao hoan chinh

### Sau buoc nay co gi moi?

- pipeline co the thoat dep khi `EOS`
- pipeline co the bao loi ro hon khi `ERROR`

### Mini checkpoint

Ban nen tu tra loi duoc:

- bus message khac gi voi du lieu video?
- tai sao `loop.quit()` lai nam trong `EOS` va `ERROR`?

Dung tai day va code xong Step 1.

## Step 2: Hoan thanh `make_element(...)`

### Ban sap code gi?

Ban se viet helper tao GStreamer element.

### Vi sao buoc nay ton tai?

Bai nay tao nhieu element:

- `uridecodebin`
- `nvstreammux`
- `nvinfer`
- `nvvideoconvert`
- `nvdsosd`
- `fakesink`

Neu lap lai `Gst.ElementFactory.make(...)` moi noi:

- code dai
- khi tao fail se kho debug hon

### Code actions

Trong `scratch.py`, hoan thanh:

```python
def make_element(factory_name, name):
```

Viec can lam:

1. goi `Gst.ElementFactory.make(factory_name, name)`
2. neu tao that bai, `raise RuntimeError(...)`
3. neu thanh cong, `return element`

### Truoc buoc nay da co gi?

- bus watch da xu ly duoc `EOS` va `ERROR`

### Sau buoc nay co gi moi?

- moi noi can tao element deu co the goi mot helper chung

### Mini checkpoint

Ban nen tu tra loi duoc:

- `factory_name` la ten plugin hay ten bien?
- tai sao fail khi tao element nen `raise` som?

Dung tai day va code xong Step 2.

## Step 3: Hoan thanh `cb_newpad(...)`

Day la phan kho nhat cua bai.
Neu ban thay phan nay kho hon cac bai truoc, do la binh thuong.

### Ban sap code gi?

Ban se viet callback duoc goi khi `uridecodebin` sinh mot pad moi.

Signature:

```python
def cb_newpad(decodebin, decoder_src_pad, source_bin):
```

### Vi sao buoc nay ton tai?

`uridecodebin` khong lo output pad hop le ngay luc vua duoc tao.

No phai:

1. mo URI
2. phan tich stream
3. xac dinh media type
4. chon decode path
5. roi moi sinh pad

Vi vay, ban khong the trong `main(...)` ma lay ngay pad that de link.
Ban phai nghe signal `pad-added`.

### 3 khoi nho can nho truoc khi code

#### `pad`

Ban co the hieu gan dung `pad` la cong cua element:

- `src pad` la cong ra
- `sink pad` la cong vao

Trong callback nay, `decoder_src_pad` la cong output moi sinh ra tu `uridecodebin`.

#### `caps`

`caps` la mo ta ve loai du lieu dang di qua pad.

No tra loi nhung cau hoi nhu:

- day la video hay audio?
- la raw hay compressed?
- format dang la gi?

Noi gon:

- `caps` = pad nay dang mang du lieu gi

#### `caps_features`

`caps_features` la dac tinh bo sung gan voi mot muc caps cu the.

Trong bai nay, feature quan trong nhat la:

- `memory:NVMM`

Noi gon:

- `caps_features` = du lieu do dang o kieu memory/path nao

### Reference skeleton can tu viet lai

Khi code callback, flow logic can giong nhu sau:

```python
lay caps
neu chua co thi query_caps(None)
neu van khong co thi bo qua

lay caps_features cua muc caps dau tien
neu khong co memory:NVMM thi bo qua

lay ghost pad src tu source_bin
gan ghost pad target = decoder_src_pad
```

### Vi sao co 2 lan check `caps`?

Ban se code logic kieu:

```python
caps = decoder_src_pad.get_current_caps()
if not caps:
    caps = decoder_src_pad.query_caps(None)
if not caps:
    return
```

Y nghia:

1. thu lay `current caps` da duoc negotiate
2. neu chua co, fallback sang `query_caps(None)`
3. neu ca hai deu khong co, khong du thong tin de xu ly tiep

`None` trong `query_caps(None)` nghia la:

- khong dat bo loc caps bo sung
- tuc la dang hoi pad: "neu khong rang buoc gi them, m co the support nhung caps nao?"

### `caps.get_features(0)` la sao?

`GstCaps` co the chua 1 hoac nhieu muc caps.
Moi muc caps co the co `features` rieng.

Index `0` o day nghia la:

- lay feature cua muc caps dau tien

Trong bai nay, current caps thuong da la fixed/negotiated caps, nen thuong chi co 1 muc,
va `0` la index hop ly.

Mental model:

```text
caps
  structure[0] = video/x-raw
  features[0] = memory:NVMM
```

### `memory:NVMM` la gi?

Day la caps feature bao rang buffer dang nam tren memory path cua NVIDIA.

No khong phai:

- codec
- media type

No la thong tin ve cach buffer duoc bieu dien trong bo nho.

Vi DeepStream downstream plugins thuong muon du lieu di theo memory path nay, nen callback
chi nhan pad co `memory:NVMM`.

### Code actions

Trong `scratch.py`, hoan thanh:

```python
def cb_newpad(decodebin, decoder_src_pad, source_bin):
```

Viec can lam theo dung thu tu:

1. lay `caps = decoder_src_pad.get_current_caps()`
2. neu `caps` rong, fallback sang `decoder_src_pad.query_caps(None)`
3. neu van khong co `caps`, in thong bao va `return`
4. lay `caps_features = caps.get_features(0)`
5. neu `not caps_features.contains("memory:NVMM")`, in thong bao va `return`
6. lay `ghost_pad = source_bin.get_static_pad("src")`
7. neu lay duoc `ghost_pad` ma `set_target(decoder_src_pad)` that bai, in thong bao

### Truoc buoc nay da co gi?

- callback da ton tai tren file, nhung chua co logic
- chua co `source_bin` that, chua co `ghost pad` that

### Sau buoc nay co gi moi?

- ban da co bo loc xac dinh pad nao duoc phep tro thanh output cua `source_bin`

### Mini checkpoint

Ban nen tu tra loi duoc:

- tai sao callback nay khong link thang vao `nvstreammux`?
- tai sao chi biet `video/x-raw` van chua du, ma con phai check `memory:NVMM`?
- sau `set_target(...)`, `source_bin.src` dang tro den ai?

Dung tai day va code xong Step 3.

## Step 4: Hoan thanh `create_source_bin(...)`

### Ban sap code gi?

Ban se tao mot `Gst.Bin` gom toan bo source logic.

### Vi sao buoc nay ton tai?

Ban muon:

- ben trong: callback + `uridecodebin` + dynamic pad
- ben ngoai: mot `src` pad gon de noi vao muxer

Do chinh la ly do can `source_bin`.

### Thu tu khoi tao quan trong

Day la thu tu ban nen nho:

1. tao `source_bin`
2. tao `uridecodebin`
3. set `uri`
4. connect `pad-added`
5. add `uridecodebin` vao `source_bin`
6. tao ghost pad `src` bang `new_no_target(...)`
7. add ghost pad vao `source_bin`
8. `return source_bin`

### Tai sao ghost pad duoc tao truoc khi co pad that?

Vi pad that cua `uridecodebin` chua xuat hien ngay.

Nho 2 timeline:

- setup timeline: tao ghost pad truoc
- runtime timeline: callback moi gan target that vao ghost pad sau

Hay hinh dung:

```text
luc setup:
source_bin.src -> rong

sau callback:
source_bin.src -> decoder_src_pad hop le
```

### Code actions

Trong `scratch.py`, hoan thanh:

```python
def create_source_bin(index, uri):
```

Viec can lam:

1. dat ten bin theo `index`
2. tao `source_bin = Gst.Bin.new(...)`
3. neu tao fail, `raise RuntimeError(...)`
4. tao `uri_decode_bin = make_element("uridecodebin", ...)`
5. `uri_decode_bin.set_property("uri", uri)`
6. `uri_decode_bin.connect("pad-added", cb_newpad, source_bin)`
7. `source_bin.add(uri_decode_bin)`
8. tao `ghost_pad = Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC)`
9. neu fail, `raise RuntimeError(...)`
10. `source_bin.add_pad(ghost_pad)`
11. `return source_bin`

### Truoc buoc nay da co gi?

- callback `cb_newpad(...)` da biet cach chon pad hop le

### Sau buoc nay co gi moi?

- ban da co mot source module ma ben ngoai nhin nhu mot element co `src` pad

### Mini checkpoint

Ban nen tu tra loi duoc:

- tai sao `source_bin` la `Gst.Bin` chu khong phai mot element don?
- tai sao `connect("pad-added", ...)` dat o day, khong dat trong `main(...)`?
- tai sao dung `new_no_target(...)` thay vi tao ghost pad tu pad that ngay lap tuc?

Dung tai day va code xong Step 4.

## Step 5: Tao pipeline va downstream elements

### Ban sap code gi?

Ban se hoan thanh phan khoi tao chinh trong `main(...)`.

### Vi sao buoc nay ton tai?

Sau khi da co source logic, bai nay quay tro lai dang pipeline quen thuoc:

- `source_bin`
- `nvstreammux`
- `nvinfer`
- `nvvideoconvert`
- `nvdsosd`
- `fakesink`

### Code actions

Trong `main(args)`, sau `Gst.init(None)`, tao day du:

1. `pipeline = Gst.Pipeline.new(...)`
2. `source_bin = create_source_bin(0, uri)`
3. `streammux = make_element("nvstreammux", ...)`
4. `pgie = make_element("nvinfer", ...)`
5. `nvvidconv = make_element("nvvideoconvert", ...)`
6. `nvosd = make_element("nvdsosd", ...)`
7. `sink = make_element("fakesink", ...)`

### Truoc buoc nay da co gi?

- source helper da xong
- callback da xong

### Sau buoc nay co gi moi?

- da co day du cac khoi lon cua pipeline

### Mini checkpoint

Ban nen tu tra loi duoc:

- tai sao bai nay van can `nvstreammux` du chi co 1 source?
- tai sao `source_bin` duoc tao truoc ca `streammux`?

Dung tai day va code xong Step 5.

## Step 6: Set properties, dac biet `live-source=True`

### Ban sap code gi?

Ban se dat property cho:

- `streammux`
- `pgie`
- `sink`

### Vi sao buoc nay ton tai?

Khong phai tao element xong la chay duoc.
`nvstreammux` can duoc noi cho biet:

- kich thuoc batch
- width/height
- timeout
- source nay la live hay khong

### Code actions

Trong `main(...)`, set:

1. `streammux.batch-size = 1`
2. `streammux.width = 1920`
3. `streammux.height = 1080`
4. `streammux.batched-push-timeout = MUXER_BATCH_TIMEOUT_USEC`
5. `streammux.live-source = True`
6. `pgie.config-file-path = PGIE_CONFIG_PATH`
7. `sink.sync = False`

### `live-source=True` can nho gi?

RTSP la source live.
Day khong phai property "trang tri".

No giup muxer hieu rang:

- source khong phai dang doc file offline
- timing va batching phai duoc xu ly theo kieu live stream

### Truoc buoc nay da co gi?

- pipeline va downstream elements da ton tai

### Sau buoc nay co gi moi?

- moi element quan trong da duoc cau hinh toi thieu de chay dung logic bai hoc

### Mini checkpoint

Ban nen tu tra loi duoc:

- neu bo `live-source=True` thi bai nay co the gap van de gi o muc khai niem?
- tai sao `sink.sync=False` thuong duoc bat trong bai hoc demo?

Dung tai day va code xong Step 6.

## Step 7: Add tat ca vao pipeline

### Ban sap code gi?

Ban se add:

- `source_bin`
- `streammux`
- `pgie`
- `nvvidconv`
- `nvosd`
- `sink`

vao `pipeline`.

### Vi sao buoc nay ton tai?

Element phai nam trong cung mot pipeline/bin thi moi link va chay cung state duoc.

### Code actions

Trong `main(...)`, add tat ca vao `pipeline`.

Ban co the:

- goi `pipeline.add(...)` tung element
- hoac lap qua tuple cac element

### Truoc buoc nay da co gi?

- tat ca element da ton tai
- chua element nao thuoc pipeline chinh

### Sau buoc nay co gi moi?

- ca source lẫn downstream da nam trong cung mot container runtime

### Mini checkpoint

Ban nen tu tra loi duoc:

- `source_bin` co nam trong pipeline nhu mot element binh thuong duoc khong?
- tai sao phai add truoc khi link?

Dung tai day va code xong Step 7.

## Step 8: Link `source_bin.src` vao `nvstreammux.sink_0`

Day la diem ma rat nhieu nguoi moi hoc thay "nguoc doi":

- `source_bin.src` duoc link tu som
- trong khi pad that cua `uridecodebin` chi xuat hien sau

Nhung day khong mau thuan, vi:

- `source_bin.src` la ghost pad da duoc tao tu setup phase
- callback se gan target that cho no sau

### Ban sap code gi?

Ban se noi source bin vao muxer.

### Code actions

Trong `main(...)`, lam dung thu tu:

1. `sinkpad = streammux.request_pad_simple("sink_0")`
2. `srcpad = source_bin.get_static_pad("src")`
3. neu khong lay duoc pad nao, `raise RuntimeError(...)`
4. `srcpad.link(sinkpad)`
5. neu link fail, `raise RuntimeError(...)`

### Vi sao `nvstreammux` can `request pad`?

Vi `nvstreammux` nhan nhieu source.
Moi source can mot sink pad rieng:

- `sink_0`
- `sink_1`
- ...

Trong bai nay chi co 1 source, nen ta dung `sink_0`.

### Vi sao `source_bin.src` lai la `static pad`?

Vi ghost pad do chinh tay ta tao ra tu truoc:

- ten la `src`
- direction la `SRC`
- du target that chua duoc gan ngay luc khoi tao

### Truoc buoc nay da co gi?

- `source_bin` da ton tai
- ghost pad `src` da ton tai
- `streammux` da ton tai

### Sau buoc nay co gi moi?

- pipeline chinh da biet source bin se di vao muxer o cong nao

### Mini checkpoint

Ban nen tu tra loi duoc:

- cai gi la request pad o bai nay?
- tai sao `source_bin.src` co the lay som, con `decoder_src_pad` thi khong?

Dung tai day va code xong Step 8.

## Step 9: Link downstream chain va chay main loop

### Ban sap code gi?

Ban se noi phan con lai:

```text
nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink
```

va de pipeline chay trong `GLib.MainLoop()`.

### Code actions

Trong `main(...)`, lam:

1. link `streammux -> pgie`
2. link `pgie -> nvvidconv`
3. link `nvvidconv -> nvosd`
4. link `nvosd -> sink`
5. tao `loop = GLib.MainLoop()`
6. lay `bus = pipeline.get_bus()`
7. `bus.add_signal_watch()`
8. `bus.connect("message", on_message, loop)`
9. in thong bao start
10. `pipeline.set_state(Gst.State.PLAYING)`
11. `loop.run()`
12. trong `finally`, `pipeline.set_state(Gst.State.NULL)`

### Truoc buoc nay da co gi?

- source da duoc noi vao muxer
- tat ca elements da o trong pipeline

### Sau buoc nay co gi moi?

- pipeline da thanh mot chuoi chay duoc

### Mini checkpoint

Ban nen tu tra loi duoc:

- tai sao clean up bang `Gst.State.NULL` nam trong `finally`?
- callback `cb_newpad(...)` duoc goi truoc hay sau `pipeline.set_state(PLAYING)`?

Dung tai day va code xong Step 9.

## Deep Dive: Toan bo `cb_newpad(...)` theo mot mach duy nhat

Day la cach doc callback tu tren xuong ma khong bi roi:

1. `uridecodebin` vua sinh ra mot pad moi
2. callback nhan `decoder_src_pad`
3. callback lay `caps`
4. callback lay `caps_features`
5. callback check `memory:NVMM`
6. neu khong hop le, bo qua pad nay
7. neu hop le, lay ghost pad `src` cua `source_bin`
8. gan ghost pad target = `decoder_src_pad`
9. tu luc nay, `source_bin.src` moi tro thanh output that de di vao `nvstreammux`

Neu can mot cau tong ket:

- callback nay la bo phan "kiem dinh va chon output pad" cho `source_bin`

## Tong ket thu tu khoi tao truoc, runtime sau

### Setup timeline

1. tao `source_bin`
2. tao `uridecodebin`
3. set `uri`
4. connect `pad-added`
5. tao ghost pad `src` khong co target
6. tao downstream elements
7. add tat ca vao pipeline
8. link `source_bin.src -> nvstreammux.sink_0`
9. link downstream chain

### Runtime timeline

1. `pipeline.set_state(PLAYING)`
2. `uridecodebin` mo URI va phan tich stream
3. `uridecodebin` sinh pad moi
4. `cb_newpad(...)` duoc goi
5. callback check `caps`
6. callback check `memory:NVMM`
7. callback gan ghost pad target
8. du lieu video that bat dau di ra tu `source_bin.src`

## Checklist tu kiem tra sau khi code xong

- [ ] Toi da tu viet `on_message(...)`
- [ ] Toi da tu viet `make_element(...)`
- [ ] Toi da hieu vi sao `cb_newpad(...)` phai check `caps`
- [ ] Toi da hieu `memory:NVMM` la memory path, khong phai codec
- [ ] Toi da hieu ghost pad duoc tao truoc, target gan sau
- [ ] Toi da tu tay noi `source_bin.src -> nvstreammux.sink_0`
- [ ] Toi da hieu callback xay ra sau `PLAYING`, khong phai luc moi tao object

## Cach dung file nay sau lan dau

Sau khi ban code xong bai 09 mot lan, lan sau co the dung file nay nhu cheat sheet:

- xem lai thu tu setup
- xem lai callback flow
- xem lai cho nao la dynamic pad
- xem lai cho nao la ghost pad

Neu ban muon hoc sau hon nua, buoc tiep theo nen lam la:

1. tu giai thich lai bang loi cua minh vi sao `source_bin` ton tai
2. tu ve lai 2 timeline: setup va runtime
3. thu doc `05_reference.py` ma khong mo guide, xem ban co theo duoc nua khong
