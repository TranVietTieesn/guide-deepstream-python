# Lesson 05 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/05_probe_batch_meta/03_starter.py /path/to/sample.h264
```

Day la bai dau tien dung `pyds`, vi vay phan probe quan trong hon phan pipeline.
Neu lesson 04 lam ban thay "infer da phuc tap", thi lesson 05 se la bai dau tien bat ban
lam quen voi metadata API cua DeepStream trong Python.

## What Is Reused vs What Is New

Phan duoc dung lai tu lesson 04:

- `on_message(...)`
- `make_element(...)`
- toan bo infer pipeline tu source den `nvosd`
- pad-level link vao `nvstreammux`

Phan moi trong bai nay:

- import `pyds`
- viet `osd_sink_pad_buffer_probe(...)`
- doc `gst_buffer`
- lay `NvDsBatchMeta`
- duyet linked-list `frame_meta_list` va `obj_meta_list`

Hay tu tach bai nay thanh 2 lop:

- lop 1: pipeline van giong lesson 04
- lop 2: phan moi that su la probe va metadata traversal

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `osd_sink_pad_buffer_probe(...)`
4. Tao pipeline giong lesson 04
5. Dat probe vao `nvosd.sink`
6. Chay pipeline

## Tao Element

Pipeline bai nay gan nhu giong lesson 04, chi doi sink thanh `fakesink` de tap trung vao
console output cua probe.

Mau viet:

```python
pipeline = Gst.Pipeline.new("lesson-05-pipeline")
source = make_element("filesrc", "file-source")
parser = make_element("h264parse", "h264-parser")
decoder = make_element("nvv4l2decoder", "hw-decoder")
streammux = make_element("nvstreammux", "stream-muxer")
pgie = make_element("nvinfer", "primary-inference")
nvvidconv = make_element("nvvideoconvert", "video-convert")
nvosd = make_element("nvdsosd", "onscreendisplay")
sink = make_element("fakesink", "fake-sink")
```

Dieu can nho:

- phan tao element khong phai khoi moi hoan toan
- cai moi thuc su la ban se "doc" du lieu tren `nvosd.sink`
- vi bai nay tap trung vao metadata, `fakesink` la du

## Function-By-Function Walkthrough

### `osd_sink_pad_buffer_probe(pad, info, user_data)`

Thu tu nen viet:

1. `gst_buffer = info.get_buffer()`
2. neu khong co buffer thi `return Gst.PadProbeReturn.OK`
3. `batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))`
4. `l_frame = batch_meta.frame_meta_list`
5. lap qua frame bang `while l_frame is not None`
6. cast `frame_meta`
7. lap qua `obj_meta_list`
8. cast `obj_meta`
9. in thong tin frame/object
10. `return Gst.PadProbeReturn.OK`

Hay chia function nay thanh 4 phan de de code hon:

#### Phan A: Lay `gst_buffer`

```python
gst_buffer = info.get_buffer()
if not gst_buffer:
    print("Unable to get GstBuffer")
    return Gst.PadProbeReturn.OK
```

Y nghia:

- `info` la object pad probe dua cho callback
- buffer that su nam trong `info`
- neu khong lay duoc buffer, callback ket thuc an toan

#### Phan B: Lay `batch_meta`

```python
batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
l_frame = batch_meta.frame_meta_list
```

Y nghia:

- `hash(gst_buffer)` dong vai tro handle de `pyds` tim metadata da gan vao buffer
- `batch_meta.frame_meta_list` la diem bat dau de di qua cac frame trong batch

#### Phan C: Duyet frame list

```python
while l_frame is not None:
    try:
        frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
    except StopIteration:
        break
```

Hay doc nhu sau:

- `l_frame` la node hien tai trong linked-list
- `l_frame.data` chua payload
- can cast ve `NvDsFrameMeta` de doc field

Sau khi cast xong, ban co the in thong tin frame:

```python
print(
    f"Frame={frame_meta.frame_num} "
    f"pad_index={frame_meta.pad_index} "
    f"objects={frame_meta.num_obj_meta}"
)
```

#### Phan D: Duyet object list

```python
l_obj = frame_meta.obj_meta_list
while l_obj is not None:
    try:
        obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
    except StopIteration:
        break
```

Sau do in thong tin object:

```python
rect = obj_meta.rect_params
print(
    "  "
    f"class_id={obj_meta.class_id} "
    f"confidence={obj_meta.confidence:.3f} "
    f"bbox=({rect.left:.1f},{rect.top:.1f},{rect.width:.1f},{rect.height:.1f})"
)
```

Va cuoi cung, buoc sang node tiep theo:

```python
try:
    l_obj = l_obj.next
except StopIteration:
    break
```

Khi xong object list cua frame hien tai, ban moi nhay sang frame tiep theo:

```python
try:
    l_frame = l_frame.next
except StopIteration:
    break
```

Neu ban bi roi, hay nho probe nay chi lam 1 viec:

- buffer -> batch -> frames -> objects -> print

### Vi sao can `.cast()`

`pyds` tra ve wrapper can duoc cast sang kieu DeepStream phu hop:

- `pyds.NvDsFrameMeta.cast(...)`
- `pyds.NvDsObjectMeta.cast(...)`

Neu khong cast, ban khong doc duoc field dung nhu `frame_num`, `class_id`, `rect_params`.

Hay coi `.cast()` la buoc "noi voi Python rang toi muon doc node nay nhu loai struct nao".

### Vi sao can `hash(gst_buffer)`

DeepStream helper can dia chi/handle cua buffer de lay metadata da gan vao no.
Trong Python, bai nay dung `hash(gst_buffer)` cho muc dich do.

Ban khong can dao sau vao CPython internals. O bai nay chi can nho:

- `gst_buffer` la object Python
- helper cua `pyds` can mot handle de tim metadata
- `hash(gst_buffer)` duoc dung lam handle do

### Dat probe

Dat nhu sau:

```python
osd_sink_pad = nvosd.get_static_pad("sink")
osd_sink_pad.add_probe(
    Gst.PadProbeType.BUFFER,
    osd_sink_pad_buffer_probe,
    None,
)
```

Can hieu 3 dong chinh:

- `nvosd.get_static_pad("sink")`: lay pad ma ban muon theo doi
- `Gst.PadProbeType.BUFFER`: callback se chay khi buffer di qua
- `osd_sink_pad_buffer_probe`: ten ham callback cua ban

### Vi sao dat o `nvosd.sink`?

Vi do la diem can bang nhat cho bai hoc nay:

- du muon metadata thi phai sau `nvinfer`
- du chua muon quan tam OSD internals thi dung truoc khi vao `nvosd`

Neu dat som hon, metadata co the chua ton tai.
Neu dat muon hon, ban khong con hoc dung "metadata vua sau infer" nua.

## How To Debug The Probe

Neu probe lam ban roi, hay debug theo thu tu sau:

1. In xem callback co duoc goi khong
2. Kiem tra `gst_buffer` co lay duoc khong
3. Kiem tra `batch_meta` co lay duoc khong
4. Chi in frame truoc, chua in object
5. Khi frame ok, moi xuong object list

Lam theo cach nay de tranh bi ngop boi qua nhieu linked-list cung mot luc.

## Starter Mapping

### TODO 1-2

- giong lesson 04

### TODO 3

- hoan thanh probe de doc `gst_buffer`
- lay `batch_meta`
- lap qua frame/object list
- in thong tin ra console
- neu can, lam tung lop: buffer -> batch -> frame -> object

### TODO 4

- tao pipeline va element
- phan nay gan giong lesson 04, chi doi sink thanh `fakesink`

### TODO 5

- set property cho source, muxer, pgie, sink

### TODO 6

- add element vao pipeline

### TODO 7-8

- link static chain
- link vao muxer bang pad-level

### TODO 9

- link downstream

### TODO 10

- gan probe vao `nvosd.sink`
- check `osd_sink_pad` khong phai `None` truoc khi `add_probe(...)`

## Syntax Notes

- `while l_frame is not None` la pattern pho bien khi di qua DeepStream linked list
- `try/except StopIteration` duoc dung de an toan khi buoc sang node tiep theo
- `rect = obj_meta.rect_params` giup code de doc hon truoc khi in bbox
- `pad`, `info`, `user_data` la signature pad probe quen thuoc; bai nay chu yeu dung `info`

## Mini Checkpoints

- Sau TODO 3: ban da co probe co the doc metadata
- Sau TODO 8: duong vao muxer da noi xong
- Sau TODO 10: metadata se duoc doc moi khi buffer den `nvosd.sink`
