# Lesson 08 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/08_multisource_batching/03_starter.py /path/to/a.h264 /path/to/b.h264
```

Day la bai ma `nvstreammux` bat dau "song dung vai tro batching" that su.
Phan moi khong nam o downstream infer chain, ma nam o cach ban tao nhieu source branch va
noi chung vao muxer.

## What Is Reused vs What Is New

Phan duoc dung lai:

- `on_message(...)`
- `make_element(...)`
- infer pipeline sau muxer
- probe metadata pattern

Phan moi:

- `build_source_branch(...)`
- vong lap qua nhieu source
- `request_pad_simple(f"sink_{index}")`
- in `pad_index` thay vi full object list

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

Mau viet rat gan starter:

```python
source = make_element("filesrc", f"file-source-{index}")
parser = make_element("h264parse", f"h264-parser-{index}")
decoder = make_element("nvv4l2decoder", f"hw-decoder-{index}")
source.set_property("location", input_path)
return source, parser, decoder
```

Dieu can nho:

- branch helper chi tao branch upstream
- no chua add vao pipeline
- no chua noi vao muxer
- viec do xay ra trong `main(...)`

### Probe `pad_index`

Trong probe, ban chi can:

- lay `gst_buffer`
- lay `batch_meta`
- lap qua `frame_meta_list`
- in `pad_index`, `frame_num`, `num_obj_meta`

Muc tieu probe bai nay la tracking source, khong phai in full object list.

Hay code theo cac buoc toi thieu:

1. `gst_buffer = info.get_buffer()`
2. neu khong co buffer thi return
3. lay `batch_meta`
4. duyet `frame_meta_list`
5. in `pad_index`, `frame_num`, `num_obj_meta`

Pseudo-code:

```python
lay gst_buffer
lay batch_meta
lap qua frame list
    cast frame_meta
    print pad_index
return OK
```

### Lap qua tung source

Pattern:

```python
for index, input_path in enumerate(input_paths):
    source, parser, decoder = build_source_branch(index, input_path)
    ...
    sinkpad = streammux.request_pad_simple(f"sink_{index}")
    srcpad = decoder.get_static_pad("src")
```

Hay nghi theo thu tu:

1. tao branch
2. add 3 element cua branch vao pipeline
3. link `source -> parser -> decoder`
4. xin `sink_i`
5. lay `decoder.src`
6. link `decoder.src -> sink_i`

Do la mot "mini lesson 03" lap lai cho moi source.

### Link order khuyen nghi

De de debug, nen lam theo thu tu:

1. tao downstream va add vao pipeline
2. lap qua tung source branch
3. add branch vao pipeline
4. link branch den decoder
5. noi tung branch vao muxer
6. cuoi cung moi link downstream `streammux -> ... -> sink`

Lam theo thu tu nay de khi hong, ban biet loi nam o upstream branch hay downstream infer.

## Starter Mapping

### TODO 1-2

- `on_message`, `make_element`

### TODO 3

- `build_source_branch(...)`

### TODO 4

- probe in `pad_index`

### TODO 5

- tao downstream elements
- giong lesson 04/05, nhung khong co source branch trong block nay

### TODO 6

- set property cho muxer, pgie, sink

### TODO 7

- add downstream vao pipeline

### TODO 8

- lap qua source branches
- add branch vao pipeline
- link toi decoder
- noi vao `sink_i`
- day la phan moi va la trong tam that su cua bai

### TODO 9

- link downstream

### TODO 10

- gan probe vao `nvosd.sink`

## Syntax Notes

- `enumerate(input_paths)` tra ve `(index, value)`
- `f"sink_{index}"` la f-string de tao ten request pad dong
- helper branch tra ve 3 element trong cung mot tuple
- `pad_index` thuong doi chieu voi `index` cua branch da noi vao muxer

## Mini Checkpoints

- Sau TODO 3: ban co the tao mot source branch day du
- Sau TODO 8: moi source da co duong vao muxer rieng
- Sau TODO 10: ban doc duoc `pad_index` theo tung frame
