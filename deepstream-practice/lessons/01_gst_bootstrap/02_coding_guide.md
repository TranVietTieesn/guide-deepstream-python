# Lesson 01 Coding Guide

Guide nay khong thay the `01_guide.md`. `01_guide.md` giup ban hieu bai hoc, con file nay
giup ban biet can go dong nao, go theo thu tu nao, va tai sao.

## Before You Code

- File se duoc chay bang lenh:

```bash
python3 lessons/01_gst_bootstrap/03_starter.py /path/to/any-file
```

- `import os`: dung de kiem tra file co ton tai khong.
- `import sys`: dung de lay `sys.argv` va thoat voi ma loi.
- `import gi` va `from gi.repository import GLib, Gst`: day la cach PyGObject expose
  GStreamer va GLib vao Python.

Ban chua can hieu sau ve `gi` ngay lap tuc. Trong bai nay, chi can nho:

- `Gst` chua cac class/hang so/hang enum cua GStreamer.
- `GLib.MainLoop()` la vong lap su kien de app nhan callback.

## Build Order

Hay code theo thu tu nay:

1. Hoan thanh callback `on_message(...)`.
2. Xu ly input trong `main(args)`.
3. Goi `Gst.init(None)`.
4. Tao pipeline va element.
5. Set property cho `filesrc`.
6. Add va link element.
7. Tao `loop`, lay `bus`, dang ky callback.
8. Chuyen pipeline sang `PLAYING`.
9. Trong `finally`, dua ve `NULL`.

Neu ban di dung thu tu nay, ban se it bi "tao sai thu tu roi khong biet sua o dau".

## Function-By-Function Walkthrough

### `on_message(bus, message, loop)`

Ham nay la callback cho bus. Khi pipeline gui message len bus, GStreamer se goi ham
nay.

Ba tham so trong bai nay:

- `bus`: doi tuong bus da goi callback. O bai nay ban khong can dung nhieu.
- `message`: message vua duoc gui len bus. Day la tham so quan trong nhat.
- `loop`: `GLib.MainLoop()` ma ban truyen vao luc `bus.connect(...)`, dung de
  `loop.quit()` khi can dung app.

Thu tu viet hop ly:

1. Lay `message_type = message.type`
2. `if message_type == Gst.MessageType.EOS:`
3. `elif message_type == Gst.MessageType.ERROR:`
4. `elif message_type == Gst.MessageType.STATE_CHANGED:`
5. `return True`

### `EOS`

Ham can viet:

```python
if message_type == Gst.MessageType.EOS:
    print("EOS: pipeline da doc het du lieu.")
    loop.quit()
```

Giai thich:

- `message.type` la enum, nen ban so sanh voi `Gst.MessageType.EOS`.
- Khi gap `EOS`, bai nay khong con viec gi de lam nua, nen goi `loop.quit()`.

### `ERROR`

Ham can viet:

```python
elif message_type == Gst.MessageType.ERROR:
    err, debug = message.parse_error()
    print(f"ERROR: {err}")
    if debug:
        print(f"DEBUG: {debug}")
    loop.quit()
```

Giai thich:

- `message.parse_error()` tra ve 2 gia tri: loi chinh va debug string.
- Vi day la Python, ban co the unpack truc tiep bang `err, debug = ...`.
- Sau khi in loi, thuong se `loop.quit()` vi pipeline dang o trang thai loi.

### `STATE_CHANGED`

Ham can viet:

```python
elif message_type == Gst.MessageType.STATE_CHANGED:
    src = message.src
    if src and src.get_name() == "lesson-01-pipeline":
        old_state, new_state, pending = message.parse_state_changed()
        print(
            "PIPELINE STATE:",
            old_state.value_nick,
            "->",
            new_state.value_nick,
            f"(pending={pending.value_nick})",
        )
```

Giai thich:

- Rat nhieu element cung phat `STATE_CHANGED`, nen ban loc chi lay pipeline chinh.
- `message.src` la object gui message.
- `get_name()` giup ban kiem tra co dung pipeline vua tao khong.
- `parse_state_changed()` tra ve 3 state.

### `main(args)`

`args` o day chinh la `sys.argv`, duoc truyen vao tu dong cuoi file:

```python
raise SystemExit(main(sys.argv))
```

Dieu nay co nghia:

- `args[0]` la ten file Python dang chay
- `args[1]` la input path nguoi dung truyen vao

## TODO Mapping

### TODO 1: Xu ly bus message trong `on_message(...)`

Ban viet ba nhanh `EOS`, `ERROR`, `STATE_CHANGED` nhu o tren.

Mini checkpoint:

- Ban da biet `message.type` dung de lam gi
- Ban da biet tai sao callback can `loop`

### TODO 2: Tao pipeline va element

Trong `main(args)`, sau `Gst.init(None)`, hay viet:

```python
pipeline = Gst.Pipeline.new("lesson-01-pipeline")
source = Gst.ElementFactory.make("filesrc", "file-source")
sink = Gst.ElementFactory.make("fakesink", "fake-sink")
```

Giai thich:

- `Gst.Pipeline.new(...)` tao mot pipeline moi.
- `Gst.ElementFactory.make(factory_name, name)` tao element tu plugin factory.
- Neu plugin khong ton tai hoac tao that bai, gia tri co the la `None`.

Vi vay ban can giu block check:

```python
if not pipeline or not source or not sink:
    ...
```

Dong tiep theo thuong la set property cho source.

### TODO 3: Set property cho `filesrc`

Hay viet:

```python
source.set_property("location", input_path)
```

Giai thich:

- `set_property(...)` la cach dat property cho GObject trong PyGObject.
- `"location"` la ten property cua `filesrc`.
- `input_path` la gia tri nguoi dung truyen vao.

Dong tiep theo thuong la add element vao pipeline.

### TODO 4: Add element vao pipeline

Hay viet:

```python
pipeline.add(source)
pipeline.add(sink)
```

Giai thich:

- Element phai nam trong pipeline thi moi co the link va chay cung pipeline.
- `add(...)` khong tra ve gia tri ma ban can dung tiep trong bai nay.

Dong tiep theo thuong la `link(...)`.

### TODO 5: Link `filesrc -> fakesink`

Hay viet:

```python
if not source.link(sink):
    print("Khong link duoc filesrc -> fakesink", file=sys.stderr)
    return 1
```

Giai thich:

- `link(...)` thuong tra ve bool cho bie t co noi thanh cong hay khong.
- O bai nay, hai element co the link truc tiep bang API element-level.

Sau do ban moi tao `GLib.MainLoop()` va bus.

### TODO 6: Bus va main loop

Block co san:

```python
loop = GLib.MainLoop()
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message", on_message, loop)
```

Giai thich:

- `GLib.MainLoop()` tao event loop.
- `pipeline.get_bus()` lay bus cua pipeline.
- `add_signal_watch()` bao voi GLib rang ban muon nhan message theo kieu signal/callback.
- `connect("message", on_message, loop)` noi signal `message` voi callback
  `on_message`, dong thoi truyen them `loop` vao callback.

## Syntax Notes

- `if not source`: trong Python, cach nay dung de check `None` hoac gia tri falsy.
- `err, debug = ...`: day la tuple unpacking.
- `f"...{value}..."`: day la f-string de noi chuoi.
- `return True` trong callback nghia la tiep tuc nhan message tiep.

## Mini Checkpoints

- Sau TODO 2: ban phai co `pipeline`, `source`, `sink`.
- Sau TODO 4: hai element da nam trong pipeline.
- Sau TODO 5: pipeline da noi xong tu source den sink.
- Sau TODO 6: app da san sang nhan `EOS` va `ERROR`.
