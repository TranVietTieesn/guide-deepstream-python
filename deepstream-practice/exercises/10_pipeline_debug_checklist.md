# Pipeline Debug Checklist

Dung file nay moi khi pipeline DeepStream "khong chay nhu mong doi". Muc tieu
khong phai la doan mo phong chung chung, ma la mot checklist de ban debug co he
thong.

## 1. Source co vao that khong?

- Duong dan file / RTSP URI co dung khong?
- Neu dung file H264, co can `h264parse` khong?
- Neu dung RTSP, source co dang live va can `uridecodebin` khong?

`# TODO`
- In log ngay sau khi set `source.set_property("location", ...)`.
- Thu doi input bang mot file chac chan chay duoc.

## 2. Element co tao duoc khong?

- `Gst.ElementFactory.make(...)` co tra ve `None` khong?
- Plugin co ton tai tren may khong?

`# TODO`
- In ten tung element sau khi tao.
- Neu mot plugin khong tao duoc, kiem tra lai moi truong DeepStream.

## 3. Add va link co thanh cong khong?

- Da `pipeline.add(...)` day du chua?
- Moi `link(...)` co thanh cong khong?
- Neu dung `nvstreammux`, da request dung `sink_0`, `sink_1`, ... chua?

`# TODO`
- Check tung buoc link, khong gom tat ca vao 1 doan "hy vong no dung".
- In ro ten 2 element truoc khi link.

## 4. `nvstreammux` co duoc cau hinh hop ly khong?

- `batch-size` co khop so source khong?
- `width`, `height` co duoc set hop ly khong?
- Neu la source live, da set `live-source=True` chua?

`# TODO`
- In gia tri `batch-size`, `width`, `height`, `batched-push-timeout`.
- Giai thich bang loi cua ban batch dang duoc tao o dau.

## 5. `nvinfer` co doc duoc config khong?

- `config-file-path` co dung khong?
- Duong dan model / engine / labels trong config co ton tai khong?
- `batch-size` cua infer co hop ly khong?

`# TODO`
- In duong dan config ra truoc khi PLAYING.
- Neu khong co bbox / metadata, nghi ngo `nvinfer` truoc.

## 6. Metadata co xuat hien khong?

- Probe dang dat o dau?
- Tai diem do buffer da qua `nvinfer` chua?
- `gst_buffer_get_nvds_batch_meta(hash(gst_buffer))` co tra ve hop ly khong?

`# TODO`
- Dat probe o `nvosd.sink` truoc.
- In `frame_num`, `num_obj_meta`, `class_id` de xac nhan metadata ton tai.

## 7. OSD co ve dung khong?

- Da tao `NvDsDisplayMeta` tu pool chua?
- Da `nvds_add_display_meta_to_frame(...)` chua?
- Da doi mau bbox / text o dung cho chua?

`# TODO`
- In `display_text` truoc khi add vao frame.
- Thu mot text overlay co dinh truoc, roi moi lam dong.

## 8. Sink co phu hop khong?

- Dang dung `fakesink` hay sink hien thi?
- Neu muon xem ket qua, sink co dung nen tang GPU khong?

`# TODO`
- Doi giua `fakesink` va sink hien thi de xac dinh loi nam o processing hay render.

## 9. Bus message noi gi?

- Co `ERROR` message khong?
- Co `EOS` khong?
- Co can in them state transition khong?

`# TODO`
- Ghi lai nguyen van loi va debug string.
- Khong debug bang cach "doan mo"; doc bus message truoc.

## 10. Cach nghi khi debug

- Tach nho pipeline.
- Xac nhan tung moc.
- Moi lan chi sua 1 bien.
- Ghi lai gia thuyet truoc khi thu.

## SELF-CHECK

- Neu pipeline chay nhung khong co bbox, ban nghi 3 diem nao dau tien?
- Neu multi-source khong batching dung, ban se check `pad_index` va `batch-size`
  nhu the nao?
- Neu RTSP chay bat on, ban se nghi ngay den `live-source`, latency, hay source
  bin? Vi sao?
