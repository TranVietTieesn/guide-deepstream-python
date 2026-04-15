# Lesson 03: Demux After Infer

Lesson nay day ban cach lay batch da infer va tach no ra thanh tung nhánh output
don le.

## What You Will Build

- Data path:
`multi-source source bins -> nvstreammux -> nvinfer -> nvstreamdemux -> per-source branches`
- Input: mot hoac nhieu URI
- Expected outcome: hieu vi sao can `nvstreamdemux` khi muon co output rieng cho
tung source sau khi batched infer xong

## Why It Matters

`nvstreammux` gom nhieu source vao batch.
`nvstreamdemux` lam dieu nguoc lai o phia output.

Lesson nay rat quan trong neu ban muon:

- render rieng tung stream
- xu ly sau theo tung source
- giu inference batched nhung output tach biet

## Compared to Lesson 01

Phan giu nguyen:

- multi-source source bin
- `nvstreammux`
- `nvinfer`
- bus/main loop

Phan moi:

- `nvstreamdemux`
- mot branch output cho moi source
- queue/convert/osd/sink lap lai theo source

Lesson 01 day ban "batch and tile".
Lesson 03 day ban "batch in, split out".

## New Concepts In This Lesson

### `nvstreamdemux`

- Tach batch thanh tung GstBuffer rieng theo source.
- Hay dung khi ban can per-stream postprocessing.

### Per-branch sink chain

- Moi source co mot nhánh queue -> convert -> OSD -> sink.
- Day la reason vi sao demux khong chi "out one buffer", ma out mot branch cho
tung source.

### Source index / pad index

- Demux branch thuong map theo `src_%u`.
- Ban can hieu source nao ung voi branch nao.

## Mental Model

### Data flow

1. Nhieu source vao muxer.
2. Infer chay tren batch.
3. Demux tach batch thanh tung stream.
4. Tung stream co own branch de ve/hien thi.

### Control flow

- Batch inference van giu throughput.
- Output branching cho ban flexibility.

## Implementation Checklist

1. Parse URI list.
2. Tao source bins va streammux.
3. Tao pgie.
4. Tao nvstreamdemux va per-source branch elements.
5. Set streammux batch size va live source.
6. Link mux -> pgie -> demux.
7. Xin demux src pad cho tung nhánh.
8. Link tung branch va sink.
9. Tao bus/main loop va run.

## Common Failure Modes

- Xin sai `src_%u` pad tren demux.
- Quen tao queue rieng cho tung branch.
- Branch khong doc lap nen backpressure loi.
- Demux va mux bi confound khi doc code.

## Self-Check

- `nvstreammux` va `nvstreamdemux` khac nhau nhu the nao?
- Output sau demux la 1 buffer hay nhieu branch?
- Ban co the map `src_0` ve source nao khong?
- Vi sao can queue cho moi branch?

## Extensions

- Them branch moi cho source 3.
- Doi sink branch thanh file sink hoac fakesink.
- Ghi log source-index tren tung branch.

