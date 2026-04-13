# Lesson 01: GStreamer Bootstrap - Notes

## Danh gia Solution

**Trang thai: HOAN THANH**

### Diem tot

| STT | Noi dung |
|-----|----------|
| 1 | Xu ly dung 3 loai message: EOS, ERROR, STATE_CHANGED |
| 2 | STATE_CHANGED co loc theo pipeline name |
| 3 | Pipeline cleanup dung cach (NULL trong finally) |
| 4 | Xu ly KeyboardInterrupt (Ctrl+C) |
| 5 | Error handling cho moi khoi tao element |
| 6 | Dung `get_name()` API chuan thay vi `.name` |

### Van de can sua

| STT | Van de | Muc do | Cach sua |
|-----|--------|--------|----------|
| 1 | `source.link(sink)` khong check return value | Warning | Them `if not source.link(sink): return 1` |

### Tong diem: 9/10

## Key Learnings

### 1. GStreamer States (4 states)

```
NULL -> READY -> PAUSED -> PLAYING
```

- **NULL**: Khoi dau, chua chiem tai nguyen
- **READY**: Da cau hinh, san sang
- **PAUSED**: Chuan bi xu ly, clock dung
- **PLAYING**: Dang chay thuc te

### 2. Pending State

- `pending=playing`: Dang trong qua trinh chuyen den PLAYING
- `pending=void-pending`: Da dat state cuoi, pipeline on dinh

### 3. Main Loop Flow

```python
# 1. Tao loop va bus
loop = GLib.MainLoop()
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message", on_message, loop)

# 2. Chay pipeline
pipeline.set_state(Gst.State.PLAYING)
loop.run()  # Blocking, doi callback

# 3. Cleanup trong finally
pipeline.set_state(Gst.State.NULL)
```

### 4. Bus Messages xu ly

| Message | Khi nao | Hanh dong |
|---------|---------|-----------|
| EOS | Doc het file/stream | `loop.quit()` |
| ERROR | Loi element/pipeline | `loop.quit()` + in loi |
| STATE_CHANGED | Pipeline/element doi state | Log de debug |

## Common Mistakes & Solutions

### 1. Quen `loop.run()`

**Loi**: Pipeline tao xong nhung khong chay, khong thay output.

**Sua**: Them `loop.run()` sau `set_state(PLAYING)`.

### 2. Khong cleanup pipeline

**Loi**: Warning "Trying to dispose element... but it is in PLAYING"

**Sua**: Dung `try/finally` hoac dam bao goi `pipeline.set_state(Gst.State.NULL)`.

### 3. Element chua add vao pipeline

**Loi**: `get_by_name()` tra ve `None`.

**Sua**: `pipeline.add(element)` truoc khi tim kiem.

### 4. Khong set location cho filesrc

**Loi**: Pipeline chay nhung khong doc duoc file, treo mai khong co EOS.

**Sua**: `source.set_property("location", input_path)`.

## Kien thuc bo sung

### Exit Code

- `return 0`: Success
- `return 1`: Loi chung (KHONG dung -1)
- `return 2`: Sai cach dung (thieu argument)

### Naming Convention

| Type | Vi du | Mo ta |
|------|-------|-------|
| Pipeline | `lesson-01-pipeline` | Chuc nang + so bai |
| Source | `file-source`, `camera-source` | Loai + chuc nang |
| Sink | `fake-sink`, `display-sink` | Loai + chuc nang |

## References

- GStreamer docs: https://gstreamer.freedesktop.org/documentation/
- GstElement API: `get_name()`, `set_state()`, `get_bus()`
- GstMessage API: `parse_error()`, `parse_state_changed()`
