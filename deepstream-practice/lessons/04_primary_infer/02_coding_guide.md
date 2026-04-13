# Lesson 04 Coding Guide

Day la bai dau tien co `nvinfer`, nen ban hay doc theo dung thu tu va khong nhay
thang den cuoi file. So voi lesson 03, bai nay khong chi them 1 element moi, ma them
ca mot cach nghi moi: infer duoc cau hinh bang file config, khong hard-code trong
Python.

## Before You Code

Lenh chay:

```bash
python3 lessons/04_primary_infer/03_starter.py /path/to/sample.h264
```

Ban can:

- file H264 input
- `dstest1_pgie_config.txt` ton tai o root project
- DeepStream Python bindings hoat dong

## What Is Reused vs What Is New

Phan duoc dung lai tu lesson 03:

- helper `on_message(...)`
- helper `make_element(...)`
- static chain `filesrc -> h264parse -> nvv4l2decoder`
- link vao `nvstreammux` bang request pad `sink_0`

Phan moi trong bai nay:

- `nvinfer`
- `config-file-path`
- `PlatformInfo()` va `create_sink(...)`
- `nvvideoconvert` va `nvdsosd`

Neu ban thay bai 04 "dong nhieu thu cung luc", do la cam giac binh thuong. Hay chia bai
ra thanh 2 lop:

- lop 1: lap pipeline infer cho chay duoc
- lop 2: hieu vi sao config, OSD chain, va sink selection ton tai

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `create_sink(...)`
4. Parse input va kiem tra config
5. Tao pipeline + element
6. Set property cho source, streammux, pgie
7. Add element vao pipeline
8. Link toi decoder, roi link vao muxer bang pad-level
9. Link phan con lai den sink
10. Tao bus/main loop va chay pipeline

## Tao Element

Sau khi co `PlatformInfo()` va `pipeline`, ban nen tao element theo mot block ro rang, thay
vi tao tung cai roi nhay xuong duoi file.

Mau viet:

```python
platform_info = PlatformInfo()
pipeline = Gst.Pipeline.new("lesson-04-pipeline")
source = make_element("filesrc", "file-source")
parser = make_element("h264parse", "h264-parser")
decoder = make_element("nvv4l2decoder", "hw-decoder")
streammux = make_element("nvstreammux", "stream-muxer")
pgie = make_element("nvinfer", "primary-inference")
nvvidconv = make_element("nvvideoconvert", "video-convert")
nvosd = make_element("nvdsosd", "onscreendisplay")
sink = create_sink(platform_info)
```

Hay doc block nay theo 2 nhom:

- nhom source -> decode -> mux:
  `filesrc`, `h264parse`, `nvv4l2decoder`, `nvstreammux`
- nhom infer -> display:
  `nvinfer`, `nvvideoconvert`, `nvdsosd`, `sink`

### Factory name vs instance name

Moi dong `make_element("factory", "name")` co 2 phan:

- factory name:
  day la ten plugin GStreamer/DeepStream can tao
- instance name:
  day la ten ban dat cho object trong pipeline

Vi du:

- `make_element("nvinfer", "primary-inference")`
  - `"nvinfer"`: plugin can tao
  - `"primary-inference"`: ten object trong pipeline
- `make_element("nvvideoconvert", "video-convert")`
  - `"nvvideoconvert"`: plugin convert
  - `"video-convert"`: ten object
- `make_element("nvdsosd", "onscreendisplay")`
  - `"nvdsosd"`: plugin OSD
  - `"onscreendisplay"`: ten object

Neu ban nho duoc quy tac nay, ban se de doc hon rat nhieu sample DeepStream khac.

## Function-By-Function Walkthrough

### `on_message(bus, message, loop)`

Bai nay chi can `EOS` va `ERROR`, giong lesson 02-03.

### `make_element(factory_name, name)`

Dung lai helper cua lesson 02-03:

```python
element = Gst.ElementFactory.make(factory_name, name)
if not element:
    raise RuntimeError(...)
return element
```

Helper nay giup code phia duoi ngan gon hon, dac biet khi so element bat dau tang len.

### `create_sink(platform_info)`

Ham nay duoc dung de chon sink theo nen tang GPU.

- neu la integrated GPU hoac aarch64, dung `nv3dsink`
- con lai dung `nveglglessink`

Dieu quan trong o day:

- ham nay tra ve mot element da tao xong
- caller co the gan no vao pipeline nhu element binh thuong
- day la logic portability, khong phai infer logic

Day la cach nen nghi khi viet TODO nay:

1. Ban da co helper `make_element(...)`
2. Ban da co object `platform_info`
3. Viec con lai chi la hoi `platform_info` 1-2 cau hoi roi chon factory name phu hop
4. Moi nhanh phai `return` ngay element vua tao

Ban co the viet gan nhu sau:

```python
def create_sink(platform_info):
    if platform_info.is_integrated_gpu():
        return make_element("nv3dsink", "video-output")
    if platform_info.is_platform_aarch64():
        return make_element("nv3dsink", "video-output")
    return make_element("nveglglessink", "video-output")
```

Doc tung dong theo logic:

- dong 1: nhan helper object vao
- `is_integrated_gpu()`: neu may thuoc nhom nay, chon `nv3dsink`
- `is_platform_aarch64()`: neu roi vao nhom nay, van chon `nv3dsink`
- neu khong roi vao 2 case tren, dung default la `nveglglessink`

### Tai sao lai `return` ngay trong tung nhanh?

Vi muc tieu cua ham nay khong phai la "ghi nho xem da chon gi", ma la "chon xong va tra
ve ngay sink dung".

Kieu viet nay giup:

- ngan gon
- de doc
- khong can bien tam nhu `sink_factory`
- moi nhanh deu ro rang la ket qua cuoi cung cua ham

### Tai sao khong viet `pipeline.add(...)` trong ham nay?

Vi `create_sink(...)` chi lam mot viec: tao va tra ve sink.

Viec add vao pipeline van thuoc `main(...)`, giong cac element khac:

```python
sink = create_sink(platform_info)
pipeline.add(sink)
```

Tach nhu vay giup ham nay de test va de doc hon:

- `create_sink(...)`: quyet dinh dung sink nao
- `main(...)`: lap pipeline

### Gap TODO 3 thi nen lam theo thu tu nao?

Rat thuc dung:

1. Viet ban nhap bang pseudo-code:

```python
if integrated:
    return nv3dsink
if aarch64:
    return nv3dsink
return nveglglessink
```

2. Doi `integrated` thanh `platform_info.is_integrated_gpu()`
3. Doi `aarch64` thanh `platform_info.is_platform_aarch64()`
4. Doi ten sink thanh `make_element(...)`

Neu ban lam theo thu tu nay, TODO 3 se de hon nhieu so voi viec co gang nho cung luc ca
factory name, helper name, va platform API.

### Tao `PlatformInfo()`

Trong `main(args)`:

```python
platform_info = PlatformInfo()
```

Ham nay khong tao element pipeline. No chi giup ban quyet dinh nen dung sink nao.

Can nho ro:

- `PlatformInfo()` khong phai `Gst.Element`
- no khong doc buffer, khong sua frame, khong lam infer
- no chi giup code de chay tren nhieu may khac nhau de hon

Neu tam thoi ban chua nho ro `nv3dsink` va `nveglglessink` khac nhau the nao, khong sao.
O bai nay, chi can hieu vai tro cua `PlatformInfo()` la chon output phu hop cho may.

Moi quan he giua 2 phan nay la:

```python
platform_info = PlatformInfo()
sink = create_sink(platform_info)
```

Doc no bang tieng Viet thuong:

- tao mot object biet thong tin nen tang
- dua object do vao helper chon sink
- nhan lai mot `Gst.Element` ten la `sink`

## The Post-Infer Chain

Sau `nvinfer`, bai nay them:

- `nvvideoconvert`
- `nvdsosd`
- `sink`

Hay doc chuoi nay theo y nghia don gian:

- `nvinfer`: tao metadata object detection
- `nvvideoconvert`: chuan bi frame cho phan display/OSD phia sau
- `nvdsosd`: dung metadata de co the ve overlay
- `sink`: nhan output cuoi cung

Ban chua can hieu sau internal metadata o bai nay. Viec "doc metadata bang tay" se den o
bai 05. O bai 04, muc tieu chi la lap chuoi infer + display cho dung.

### Khoi tao cac element moi trong chain nay

Trong TODO tao element, ba dong moi can them so voi lesson 03 la:

```python
pgie = make_element("nvinfer", "primary-inference")
nvvidconv = make_element("nvvideoconvert", "video-convert")
nvosd = make_element("nvdsosd", "onscreendisplay")
```

Doc theo y nghia:

- `pgie`: element infer chinh cua bai
- `nvvidconv`: element chuyen doi video de chain display/OSD xu ly tiep
- `nvosd`: element dung metadata de ve thong tin len frame

Neu ban bi khop o TODO 4, hay tach rieng 3 dong nay ra va tu hoi:

- factory name cua infer la gi? `nvinfer`
- factory name cua video convert la gi? `nvvideoconvert`
- factory name cua OSD la gi? `nvdsosd`

Sau do moi dat ten instance cho de doc.

## How `config-file-path` Works

Dong quan trong nhat cua bai nay la:

```python
pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
```

Y nghia cua no:

- code Python khong tu truyen `onnx-file`, labels, threshold... vao `nvinfer`
- code dua cho `nvinfer` mot file config
- `nvinfer` tu doc file do de biet phai chay model nao va xu ly output ra sao

Noi ngan gon:

- Python noi voi config
- config noi voi model

Vi vay, khi infer loi, dung nghi den code truoc. Hay nghi den:

- sai duong dan config
- config tro toi model/engine/labels khong ton tai
- batch-size hay mode trong config khong hop

## What Lives In The Config File

Trong `dstest1_pgie_config.txt`, ban nen nhan ra it nhat:

```ini
[property]
onnx-file=...
model-engine-file=...
labelfile-path=...
batch-size=1
network-mode=2
interval=0
```

Y nghia o muc do bai nay:

- `onnx-file`: model goc
- `model-engine-file`: TensorRT engine da toi uu
- `labelfile-path`: ten class de map metadata
- `batch-size`: kich thuoc batch phia infer
- `network-mode`: FP32 / INT8 / FP16
- `interval`: co infer moi frame hay bo qua mot so frame

Ban chua can tune cac gia tri nay ngay. Bai 07 moi la bai cho viec thay doi co chu dich.

## Set Property

Phan can dat:

```python
source.set_property("location", input_path)
streammux.set_property("batch-size", 1)
pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
```

Va voi old `nvstreammux`:

```python
streammux.set_property("width", 1920)
streammux.set_property("height", 1080)
streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
```

Y nghia:

- `config-file-path` la diem noi code voi model config
- ban khong phai truyen threshold/labels truc tiep trong code bai nay
- `streammux.batch-size` va `batch-size` trong config nen duoc doi chieu voi nhau

### Old vs New `nvstreammux`

Trong code runnable, ban se thay:

```python
if os.environ.get("USE_NEW_NVSTREAMMUX") != "yes":
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
```

Dieu nay co nghia:

- course dang giu compatibility voi legacy mux path
- `width`, `height`, `batched-push-timeout` duoc set cho truong hop old mux
- neu moi truong cua ban dung new mux, khong phai luc nao cung set nhung property nay

Khong can di sau vao versioning o bai nay. Chi can nho rang doan `if` nay giai thich vi
sao code co them mot nhanh dieu kien.

## Batch-Size Relation: Muxer vs PGIE

Lesson 03 da gioi thieu `streammux.batch-size`.
Lesson 04 them `batch-size` ben trong file config cua `nvinfer`.

Mental anchor can nho:

- `nvstreammux` quyet dinh batch di vao infer
- `nvinfer` can config batch-size phu hop voi du lieu no nhan

Trong bai 1 source, ca hai thuong deu la `1`.
O bai 07 va bai multi-source, moi quan he nay se tro nen quan trong hon.

## Link vao muxer

Phan nay giong lesson 03:

```python
sinkpad = streammux.request_pad_simple("sink_0")
srcpad = decoder.get_static_pad("src")
if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
    raise RuntimeError(...)
```

Neu phan nay chua ro, hay quay lai lesson 03 truoc khi debug `nvinfer`.

## Link phan sau muxer

Hay link theo thu tu:

- `streammux -> pgie`
- `pgie -> nvvidconv`
- `nvvidconv -> nvosd`
- `nvosd -> sink`

Trong bai nay, thu tu do khong chi la "sample viet the". Moi link co vai tro:

- `streammux -> pgie`: dua batched frame vao infer
- `pgie -> nvvidconv`: dua output sau infer vao display-prep chain
- `nvvidconv -> nvosd`: chuan bi cho overlay
- `nvosd -> sink`: dua ket qua cuoi cung ra output

## Starter Mapping

### TODO 1

- `on_message(...)`
- xu ly `EOS`
- xu ly `ERROR`

### TODO 2

- `make_element(...)`
- giong lesson 02-03

### TODO 3

- `create_sink(platform_info)`
- nho rang ham nay tra ve `Gst.Element`, con `platform_info` chi la helper object

### TODO 4

- tao `PlatformInfo()`
- tao pipeline va 8 element
- nhan ra rang bai nay co them infer chain va display chain

### TODO 5

- set property cho source
- set property cho streammux
- set `config-file-path`
- doc doan old/new mux de hieu vi sao co nhanh `if`

### TODO 6

- add element vao pipeline

### TODO 7

- link `filesrc -> parser -> decoder`

### TODO 8

- xin `sink_0`
- lay `decoder.src`
- link pad-level

### TODO 9

- link downstream tu `streammux` den sink
- xem day la "infer + display chain", khong phai 4 link ngau nhien

### TODO 10

- doc block bus/main loop co san
- in `config-file-path` truoc khi `PLAYING` de thay code dang noi vao config nao

## Syntax Notes

- `PlatformInfo()` la object helper, khong phai `Gst.Element`
- `create_sink(...)` tra ve element, nen ban co the `pipeline.add(sink)`
- `set_property("config-file-path", ...)` dung string path
- `srcpad.link(sinkpad)` tra ve `Gst.PadLinkReturn`
- `pgie`, `nvvidconv`, `nvosd` van la `Gst.Element` binh thuong, du chuc nang cua chung
la DeepStream-specific

## Mini Checkpoints

- Sau TODO 4: ban phai co du element cua mot pipeline infer toi thieu, va phan moi so
voi lesson 03 phai nam o nua sau pipeline
- Sau TODO 5: `nvinfer` da biet doc config nao, va ban phai biet config dang dong vai tro
gi trong bai nay
- Sau TODO 8: duong vao muxer da noi xong, nghia la input cho infer da san sang
- Sau TODO 9: pipeline da noi xong tu source den sink, va ban co the chi ra vai tro cua
tung element sau `nvinfer`

