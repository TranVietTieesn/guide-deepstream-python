# Lesson 04: Primary Infer

Neu ban chua quen syntax Python/GStreamer/DeepStream, doc them
`02_coding_guide.md` truoc khi mo `03_starter.py`.

## What You Will Build

- Pipeline:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> nvinfer -> nvvideoconvert -> nvdsosd -> sink`
- Input: mot file H264 elementary stream
- Config: `dstest1_pgie_config.txt`
- Expected outcome: pipeline object detection toi thieu co the chay den sink, va ban
  thay ro `nvinfer` duoc noi vao code qua `config-file-path`

## Why It Matters

Day la bai hoc dau tien ban that su cham vao "AI plugin" cua DeepStream.

- `nvstreammux` chuan hoa input cho DeepStream
- `nvinfer` chay TensorRT theo file config
- `nvvideoconvert` va `nvdsosd` chuan bi de ket qua infer co the duoc dua den sink

Neu bai nay ro, ban se hieu pipeline lon hon khong hard-code model trong code Python,
ma noi code voi model qua config.

## Compared to Lesson 03

Phan duoc giu nguyen tu lesson 03:

- van doc file H264 bang `filesrc -> h264parse -> nvv4l2decoder`
- van dua decoder vao `nvstreammux` bang request pad `sink_0`
- van can bus watch, `GLib.MainLoop()`, va cleanup ve `NULL`

Phan moi o lesson 04:

- them `nvinfer` la plugin infer dau tien
- them file config PGIE va `config-file-path`
- them chuoi sau infer: `nvvideoconvert -> nvdsosd -> sink`
- them `PlatformInfo()` de chon sink hop voi nen tang

Neu lesson 03 day ban cach dua frame vao the gioi DeepStream, thi lesson 04 day ban
cach dua infer vao pipeline do.

## New Concepts In This Lesson

### `nvinfer`

- Day la plugin DeepStream de chay infer tren GPU/TensorRT.
- Bai nay dung no nhu primary detector dau tien trong pipeline.

### `config-file-path`

- Code Python khong truyen tung dong model setting vao `nvinfer`.
- Code chi noi `nvinfer` voi file config bang mot duong dan string.

### PGIE config file

- File `dstest1_pgie_config.txt` chua thong tin ve model, engine, labels, batch-size,
  threshold, cluster mode...
- Bai nay chi can biet no dong vai tro "hop cau hinh" cho `nvinfer`.
- Bai 07 moi di sau vao viec tune cac tham so trong file nay.

### `nvvideoconvert`

- Sau infer, pipeline can mot buoc chuyen doi phu hop de chuoi display/OSD xu ly.
- O muc do bai nay, ban chi can nho: no la buoc chuan bi truoc khi ve overlay.

### `nvdsosd`

- Plugin nay dung metadata object detection de ve overlay len frame.
- Bai nay chua bat buoc ban doc metadata bang tay, nhung no la cau noi giua infer va
  phan hien thi.

### Cac dong khoi tao moi se xuat hien trong code

So voi lesson 03, bai nay co them 3 dong khoi tao element ma ban nen nhan dien som:

- `pgie = make_element("nvinfer", "primary-inference")`
- `nvvidconv = make_element("nvvideoconvert", "video-convert")`
- `nvosd = make_element("nvdsosd", "onscreendisplay")`

Day la cach doc chung:

- chuoi thu nhat la factory name cua plugin
- chuoi thu hai la ten instance ban dat cho object

Neu ban thay nhung ten nay la moi, dung lo. O bai nay ban chua can nho het moi plugin cua
DeepStream. Ban chi can biet:

- `nvinfer` = infer
- `nvvideoconvert` = chuan bi video cho chain sau infer
- `nvdsosd` = ve overlay dua tren metadata

### `PlatformInfo`

- Day la helper object, khong phai `Gst.Element`.
- No khong xu ly du lieu video.
- No chi giup code chon sink phu hop voi may dang chay.

## How To Think About `create_sink(...)`

TODO `create_sink(platform_info)` de gay khung cho nguoi moi vi no khong giong cac TODO
tao element thong thuong. Ban khong chi "tao 1 sink", ma dang viet mot helper co logic:

- nhan vao `platform_info`
- kiem tra may dang thuoc nhom nao
- chon factory phu hop
- tra ve mot `Gst.Element` da tao xong

Hay nghi theo 3 buoc:

1. Hoi: "May nay co can dung `nv3dsink` khong?"
2. Neu co, return ngay `make_element("nv3dsink", "video-output")`
3. Neu khong, roi xuong case mac dinh va return `make_element("nveglglessink", "video-output")`

Co the doc ham nay nhu mot ham `if/elif/fallback`, khong phai mot noi de viet pipeline
logic moi.

Pseudo-code:

```python
def create_sink(platform_info):
    if ...:
        return make_element("nv3dsink", "video-output")
    if ...:
        return make_element("nv3dsink", "video-output")
    return make_element("nveglglessink", "video-output")
```

Dieu can nho:

- moi nhanh deu `return` mot element that
- khong can `pipeline.add(...)` trong ham nay
- khong set `PLAYING`, khong link gi trong ham nay
- ham nay chi co nhiem vu "chon dung sink roi tra no ra"

## Must Understand Now vs Know For Later

Can hieu ngay o bai nay:

- `nvstreammux` van dung truoc `nvinfer`, du chi co 1 source
- `nvinfer` doc model qua `config-file-path`
- `nvinfer` se gan metadata vao buffer
- chuoi sau infer duoc link theo thu tu `nvinfer -> nvvideoconvert -> nvdsosd -> sink`

Chi can biet mat o bai nay, chua can hieu sau:

- chi tiet ben trong `dstest1_pgie_config.txt`
- metadata struct cua DeepStream duoc doc the nao trong Python
- khac nhau sau ve render giua `nv3dsink` va `nveglglessink`

Nhung phan tren se duoc quay lai o bai 05 va bai 07.

## Config Primer

Day la lan dau file config tro thanh mot phan bat buoc cua pipeline.

Trong `dstest1_pgie_config.txt`, ban nen nhan ra it nhat cac dong sau:

- `onnx-file=...`: duong dan model goc
- `model-engine-file=...`: duong dan TensorRT engine
- `labelfile-path=...`: ten class de map `class_id` sang label
- `batch-size=1`: kich thuoc batch phia infer, can doi chieu voi muxer
- `network-mode=2`: che do tinh toan, o day la FP16
- `interval=0`: infer moi frame

Dieu quan trong nhat can nho:

- o bai 04, ban hoc cach code noi voi config
- o bai 07, ban hoc cach thay doi config de quan sat output doi theo y minh

## Mental Model

### Truoc `nvinfer`

- `filesrc -> parser -> decoder -> streammux` dua du lieu ve dang frame batched
- luc nay frame da san sang cho infer

### Tai `nvinfer`

- `nvinfer` khong can ban truyen chi tiet model tung dong
- code chi can `config-file-path`
- file config quyet dinh model, engine, labels, threshold, clustering...

### Sau `nvinfer`

- metadata object detection duoc gan vao buffer
- `nvvideoconvert` chuan bi frame cho chuoi phia sau
- `nvdsosd` dung metadata de co the ve thong tin len frame
- sink nhan output cuoi cung de hien thi hoac xuat ket qua

## Why `PlatformInfo` Exists

Trong sample va reference, sink khong duoc chon co dinh.

Ly do:

- mot so may hop voi `nv3dsink`
- mot so may hop voi `nveglglessink`
- code muon chay de dang hon tren nhieu nen tang DeepStream khac nhau

Vi vay, `PlatformInfo()` khong phai la mot phan cua data path. No la helper phuc vu
portability.

Noi cach khac:

- `main(...)` khong muon biet qua nhieu chi tiet ve tung loai sink
- `create_sink(...)` gom logic lua chon do vao mot cho
- sau khi goi xong, `main(...)` chi viec dung bien `sink` nhu cac element khac

## Implementation Checklist

1. Parse input file va kiem tra `dstest1_pgie_config.txt`.
2. `Gst.init(None)` va tao `PlatformInfo()`.
3. Tao pipeline va cac element tu source den sink.
4. Set property cho source, streammux, pgie.
5. Add element vao pipeline.
6. Link den decoder, roi noi vao `nvstreammux.sink_0`.
7. Link `streammux -> pgie -> nvvideoconvert -> nvdsosd -> sink`.
8. Tao bus va `GLib.MainLoop()`.
9. In `config-file-path` truoc khi `PLAYING`.
10. Cleanup ve `NULL`.

## Common Failure Modes

- Sai `config-file-path`:
  pipeline co the chay den `nvinfer` roi bao loi.
- Model/engine/labels trong config khong ton tai:
  can nghi ngo config truoc khi nghi ngo pipeline.
- Quen `nvstreammux`:
  `nvinfer` trong DeepStream thuong khong duoc day truc tiep bang decoder thuan.
- `batch-size` cua muxer va config khong khop:
  pipeline co the van chay, nhung day la dau hieu cau hinh infer chua chat.
- Chon sink khong hop voi nen tang:
  co the processing dung nhung hien thi loi.

## Self-Check

1. Tai sao code chi set `config-file-path` ma `nvinfer` van biet model nao de chay?
2. Vi sao `nvstreammux` van nam truoc `nvinfer` du chi co 1 source?
3. Metadata object detection bat dau xuat hien sau plugin nao?
4. Trong bai nay, doi threshold thi thuong sua o code hay o config? Vi sao?
5. `PlatformInfo()` dang giai quyet bai toan portability nao, va tai sao no khong nam
   trong data path?

## Looking Ahead

- Bài 05 se dung lai infer pipeline nay, nhung dat probe de doc metadata that su.
- Bai 07 se quay lai file config va di sau vao threshold, topk, NMS, va batch-size.

## Extensions

- Doi sang config variant trong `archive/exercises/07_config_variants/`.
- Thay `pre-cluster-threshold` va ghi lai bbox thay doi ra sao.
- In them `pgie.get_property("batch-size")` va doi chieu voi muxer.
- In them mot vai dong quan trong trong file config truoc khi `PLAYING`.
- Doi sink neu ban muon quan sat output tren man hinh that.

