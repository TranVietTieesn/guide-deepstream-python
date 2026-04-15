# Lesson 09 Coding Guide

## Before You Code

Lenh chay:

```bash
python3 lessons/beginning/09_rtsp_source_walkthrough/03_starter.py rtsp://user:pass@host:554/path
```

Day la bai ma upstream source logic bat dau khac han cac bai file source truoc do.
Phan kho nhat khong nam o infer chain, ma nam o `uridecodebin`, dynamic pad, source bin,
va ghost pad.

## What Is Reused vs What Is New

Phan duoc dung lai:

- `on_message(...)`
- `make_element(...)`
- downstream infer chain
- link vao `nvstreammux.sink_0`

Phan moi:

- `cb_newpad(...)`
- `create_source_bin(...)`
- `Gst.Bin`
- `Gst.GhostPad`
- `live-source=True`

## Build Order

1. Hoan thanh `on_message(...)`
2. Hoan thanh `make_element(...)`
3. Hoan thanh `cb_newpad(...)`
4. Hoan thanh `create_source_bin(...)`
5. Tao downstream
6. Link source bin vao muxer
7. Chay pipeline

## Function-By-Function Walkthrough

### `cb_newpad(decodebin, decoder_src_pad, source_bin)`

Thu tu nen viet:

1. lay `caps`
2. neu can thi `query_caps(None)`
3. lay `caps_features`
4. check `memory:NVMM`
5. lay ghost pad `src` tu `source_bin`
6. `ghost_pad.set_target(decoder_src_pad)`

Muc tieu callback:

- chi noi nhung pad decode hop le vao pipeline chinh

Hay chia callback nay thanh 4 khoi:

#### Khoi A: Lay caps

- `caps = decoder_src_pad.get_current_caps()`
- neu can, fallback sang `decoder_src_pad.query_caps(None)`

#### Khoi B: Lay features

- doc `caps_features`
- check `memory:NVMM`

Y nghia:

- bai nay muon decode path phu hop voi DeepStream/NVIDIA memory
- khong phai pad nao tu `uridecodebin` cung hop le de di tiep

#### Khoi C: Lay ghost pad

- lay `src` ghost pad tu `source_bin`

#### Khoi D: Set target

- `ghost_pad.set_target(decoder_src_pad)`

Noi ngan gon:

- callback nhan pad dong
- neu pad do hop le thi noi no vao ghost pad

Pseudo-code:

```python
lay caps
lay features
neu khong phai NVMM: bo qua
lay ghost pad src cua source_bin
set target cua ghost pad = decoder_src_pad
```

### `create_source_bin(index, uri)`

Ham nay nen:

- tao `Gst.Bin`
- tao `uridecodebin`
- set `uri`
- connect `pad-added`
- add `uridecodebin` vao bin
- tao ghost pad `src`
- add ghost pad vao bin
- `return source_bin`

Hay doc ham nay theo 3 lop:

1. Tao mot `Gst.Bin` de gom logic source
2. Tao `uridecodebin`, set `uri`, connect callback
3. Tao ghost pad `src` de lo pad hop le ra ngoai

Mau tu duy:

```python
source_bin = Gst.Bin.new(...)
uri_decode_bin = make_element("uridecodebin", ...)
uri_decode_bin.set_property("uri", uri)
uri_decode_bin.connect("pad-added", cb_newpad, source_bin)
source_bin.add(uri_decode_bin)
ghost_pad = Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC)
source_bin.add_pad(ghost_pad)
return source_bin
```

### Vi sao can `Gst.Bin` va `Gst.GhostPad`?

Vi `main(...)` khong muon biet chi tiet ben trong source RTSP.

Ban muon:

- ben trong: callback + uridecodebin + dynamic pad
- ben ngoai: 1 `src` pad de noi vao muxer

Day chinh la vai tro cua source bin.

## Main Flow: Nen nghi the nao

Sau khi xong 2 helper tren, `main(...)` nen de doc theo thu tu:

1. tao `source_bin`
2. tao downstream elements
3. set property cho muxer, pgie, sink
4. add tat ca vao pipeline
5. xin `sink_0`
6. lay `source_bin.src`
7. link vao muxer
8. link downstream

Neu callback lam ban roi, hay nho `main(...)` van kha don gian. Doan kho nhat da duoc
gom vao `cb_newpad(...)` va `create_source_bin(...)`.

## Why `live-source=True` Matters Here

Trong bai nay, `streammux` can biet source la live:

- de xu ly timing hop ly hon
- de mental model cua pipeline khop voi RTSP source

Ban chua can hoc sau ve timestamp, nhung dung bo qua property nay nhu mot dong "de co".

## Starter Mapping

### TODO 1-2

- `on_message`, `make_element`

### TODO 3

- `cb_newpad(...)`
- phan kho nhat cua bai, nen lam theo thu tu caps -> features -> ghost pad -> set target

### TODO 4

- `create_source_bin(...)`
- coi day la helper de main gọn hon, khong phai mot pipeline rieng thu hai

### TODO 5

- tao downstream elements

### TODO 6

- set property cho muxer, pgie, sink

### TODO 7

- add element vao pipeline

### TODO 8

- xin `sink_0`
- lay `source_bin.src`
- link vao muxer
- day la luc source bin tro thanh "mot source binh thuong" tu goc nhin cua pipeline chinh

### TODO 9

- link downstream

## Syntax Notes

- `Gst.Bin.new(name)` tao mot container element
- `Gst.GhostPad.new_no_target(...)` tao ghost pad chua noi den pad that
- `ghost_pad.set_target(...)` la luc source bin "loi src ra ngoai"
- `caps_features.contains("memory:NVMM")` dung de loc decode path phu hop
- `pad-added` callback co the duoc goi nhieu lan; bai nay chi noi pad hop le

## Mini Checkpoints

- Sau TODO 3: ban biet pad dong nao se duoc phep di tiep
- Sau TODO 4: source bin da co `src` ghost pad
- Sau TODO 8: source RTSP da noi vao muxer thanh cong
