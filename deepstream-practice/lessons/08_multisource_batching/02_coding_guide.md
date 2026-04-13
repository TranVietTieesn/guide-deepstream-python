# Lesson 08 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/08_multisource_batching/03_starter.py /path/to/a.h264 /path/to/b.h264
```

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `build_source_branch(...)`
4. Hoan thanh probe in `pad_index`
5. Tao downstream
6. Lap qua tung source branch va noi vao muxer
7. Chay pipeline

## Function-By-Function Walkthrough

### `build_source_branch(index, input_path)`

Ham nay nen:

- tao `filesrc`
- tao `h264parse`
- tao `nvv4l2decoder`
- set `location` cho source
- `return source, parser, decoder`

Loi ich:

- code multi-source khong lap lai qua nhieu
- de mo rong them source sau nay

### Probe `pad_index`

Trong probe, ban chi can:

- lay `gst_buffer`
- lay `batch_meta`
- lap qua `frame_meta_list`
- in `pad_index`, `frame_num`, `num_obj_meta`

Muc tieu probe bai nay la tracking source, khong phai in full object list.

### Lap qua tung source

Pattern:

```python
for index, input_path in enumerate(input_paths):
    source, parser, decoder = build_source_branch(index, input_path)
    ...
    sinkpad = streammux.request_pad_simple(f"sink_{index}")
    srcpad = decoder.get_static_pad("src")
```

## Starter Mapping

### TODO 1-2

- `on_message`, `make_element`

### TODO 3

- `build_source_branch(...)`

### TODO 4

- probe in `pad_index`

### TODO 5

- tao downstream elements

### TODO 6

- set property cho muxer, pgie, sink

### TODO 7

- add downstream vao pipeline

### TODO 8

- lap qua source branches
- add branch vao pipeline
- link toi decoder
- noi vao `sink_i`

### TODO 9

- link downstream

### TODO 10

- gan probe vao `nvosd.sink`

## Syntax Notes

- `enumerate(input_paths)` tra ve `(index, value)`
- `f"sink_{index}"` la f-string de tao ten request pad dong
- helper branch tra ve 3 element trong cung mot tuple

## Mini Checkpoints

- Sau TODO 3: ban co the tao mot source branch day du
- Sau TODO 8: moi source da co duong vao muxer rieng
- Sau TODO 10: ban doc duoc `pad_index` theo tung frame
