# Lesson 02: Decode Chain - Solution Notes

## Score: 8.5/10

Completed: 2026-04-13

---

## What Went Well

- Pipeline structure correct: `filesrc → h264parse → nvv4l2decoder → fakesink`
- All 6 TODOs from starter implemented
- Proper bus message handling (EOS, ERROR with debug parsing)
- Clean state transitions: `PLAYING → loop → NULL`
- KeyboardInterrupt handling with proper cleanup

---

## Issues Found

### 1. Error handling in `make_element()` - MEDIUM

**Current:**
```python
if not element:
    print(f"khong tao duoc element {factory_name}")
    return None
```

**Should be (per coding guide):**
```python
if not element:
    raise RuntimeError(f"Khong tao duoc element: {factory_name}")
```

**Why it matters:** Using `raise` stops execution immediately with clear error. Returning `None` requires caller to check everywhere.

### 2. Error handling during link - MEDIUM

**Current:**
```python
if not source.link(parser):
    print("khong the link duoc source -> parser")
    return 1
```

**Should be:**
```python
if not source.link(parser):
    raise RuntimeError("Khong link duoc filesrc -> h264parse")
```

### 3. Add element style - LOW

**Current:** 4 separate `pipeline.add()` calls

**Better (more Pythonic):**
```python
for element in (source, parser, decoder, sink):
    pipeline.add(element)
```

### 4. Missing docstrings - LOW

No function documentation. Should add:
```python
def make_element(factory_name, name):
    """Create a GStreamer element with error checking.
    
    Args:
        factory_name: Element factory name (e.g., 'filesrc')
        name: Instance name for the element
    
    Returns:
        The created Gst.Element
    
    Raises:
        RuntimeError: If element creation fails
    """
```

---

## Key Learnings

1. **filesrc** chỉ đọc byte - không hiểu gì về video format
2. **h264parse** chuẩn hóa stream H264, không decode
3. **nvv4l2decoder** biến elementary stream thành decoded frames
4. **fakesink** với `sync=False` cho phép chạy không đồng bộ với clock

## Common Mistakes to Avoid

- Đưa file MP4 vào pipeline H264 elementary → sẽ fail
- Bỏ `h264parse` → decoder không nhận diện được stream
- Quên `sink.set_property("sync", False)` → có thể bị delay không cần thiết

## References

- `05_reference.py` - Implementation mẫu đúng chuẩn
- `02_coding_guide.md` - Best practices cho GStreamer Python
- `01_guide.md` - Mental model và self-check questions

---

## Follow-up Actions

- [ ] Refactor error handling to use `raise RuntimeError()` pattern
- [ ] Add docstrings to all functions
- [ ] Test with different H264 files to verify robustness
