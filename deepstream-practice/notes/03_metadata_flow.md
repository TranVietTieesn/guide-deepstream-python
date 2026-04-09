# Metadata Flow

Day la phan quan trong nhat de ban that su "doc duoc DeepStream".

Neu chi chay pipeline va nhin bbox tren man hinh, ban moi thay ket qua. Neu ban
doc duoc metadata, ban moi that su hieu plugin nao da dua thong tin gi vao
buffer, va ban co the mo rong sang analytics, dem doi tuong, canh bao, luu su
kien.

## Chuoi metadata trong file goc

Trong `../../deepstream-test1.py`, probe o `nvosd.sink` doc metadata theo chuoi:

`Gst.Buffer -> NvDsBatchMeta -> NvDsFrameMeta -> NvDsObjectMeta`

## Metadata xuat hien tu dau?

Trong pipeline nay, metadata detection xuat hien sau `nvinfer`.

Nghia la:
- `filesrc`, `h264parse`, `nvv4l2decoder`, `nvstreammux` chu yeu chuan bi data.
- `nvinfer` them thong tin object detection vao buffer.
- Probe cua ban doc lai metadata do.

## Tai sao dung `hash(gst_buffer)`?

Theo mau Python DeepStream, `pyds.gst_buffer_get_nvds_batch_meta()` can dia chi C
cua `GstBuffer`. Trong binding Python, `hash(gst_buffer)` duoc dung de lay gia tri
dia chi phu hop cho ham nay.

Hay nho:
- Ban khong truyen "noi dung buffer".
- Ban truyen handle / dia chi cua buffer de `pyds` tim metadata gan kem.

## Tai sao phai `.cast()`?

Metadata list duoc dua ve duoi dang node tong quat.

Vi vay ban phai:
- `pyds.NvDsFrameMeta.cast(l_frame.data)`
- `pyds.NvDsObjectMeta.cast(l_obj.data)`

Neu khong cast:
- Python khong biet node do phai duoc doc nhu kieu nao.
- Ban khong truy cap duoc field chuyen biet nhu `frame_num`, `num_obj_meta`,
  `class_id`, `rect_params`.

## Memory ownership: cho nay rat de "mo ho"

Trong sample DeepStream Python, comment nhan manh rang:
- Metadata object nam o phia C.
- Python binding chi wrap lai.
- Garbage collector Python khong so huu bo nho do.

Y nghia thuc te:
- Ban khong nen tu y giai phong.
- Ban can dung cac API `pyds` dung cach.
- Khi tao display meta, thuong phai xin tu pool bang
  `nvds_acquire_display_meta_from_pool(batch_meta)`.

## Duyet metadata list nhu the nao?

### Tang batch

- Mot buffer co the chua batch cua nhieu frame.
- `batch_meta.frame_meta_list` la danh sach frame trong batch.

### Tang frame

- Moi `NvDsFrameMeta` dai dien cho 1 frame.
- Trong do co `frame_num`, `num_obj_meta`, `obj_meta_list`.

### Tang object

- Moi `NvDsObjectMeta` dai dien cho 1 object detect duoc.
- Ban co the doc:
  - `class_id`
  - `confidence`
  - `rect_params.left`
  - `rect_params.top`
  - `rect_params.width`
  - `rect_params.height`

## Tu metadata sang overlay

File goc lam 2 viec trong cung probe:

1. Doc metadata object de dem object.
2. Tao `NvDsDisplayMeta` de dua text overlay len frame.

Do la mot pattern rat pho bien:
- infer -> metadata
- probe -> business logic
- OSD -> visualize logic

## Nhung diem hay nham lan

### Nham lan 1: Probe la noi tao metadata

Sai. Probe khong phai noi tao detection metadata.

Probe:
- doc,
- sua,
- them metadata / display meta moi neu muon.

Con detection metadata o bai nay den tu `nvinfer`.

### Nham lan 2: `num_obj_meta` la tong object cua ca pipeline

Sai. No la tong object cua frame hien tai.

Muon tong theo thoi gian:
- ban phai tu tich luy o tang app.

### Nham lan 3: Co bbox la chac chan co text overlay

Sai. Bbox / object meta va display text la 2 lop khac nhau.

## `# TODO`

- In them `confidence` cua tung object.
- In them bbox va map `class_id` sang ten class.
- Thu gan probe sang diem som hon trong pipeline va quan sat metadata co khac
  khong.
- Tu giai thich vi sao `nvosd.sink` la vi tri hoc tap tot.

## SELF-CHECK

- Neu batch-size = 2 thi `frame_meta_list` co the chua gi?
- Vi sao sample phai dung `.cast()` thay vi doc truc tiep `l_frame.data`?
- Ban se dat logic dem object tong theo 1 phut o probe hay o lop app cao hon?
