# Multistream And Batching Topic

Day la topic ve nhieu source, batching, demux, preprocess, va RTSP flow:

- `apps/deepstream-test3`
- `apps/deepstream-preprocess-test`
- `apps/deepstream-demux-multi-in-multi-out`
- `apps/deepstream-rtsp-in-rtsp-out`

## What this topic teaches

- `uridecodebin` cho multi-source
- `nvstreammux` batch formation
- `nvmultistreamtiler`
- `nvstreamdemux`
- `nvdspreprocess` truoc infer
- Source live va RTSP in/out flow

## Suggested lesson order

1. `01_test3_multi_source_baseline`
2. `02_preprocess_before_infer`
3. `03_demux_after_infer`
4. `04_rtsp_in_rtsp_out`

## Boundary

- Giu focus o source, mux, batch, demux, preprocess, va networking.
- Chua day sang redaction, analytics, hay vision-specialized post-processing.
- Neu can probe metadata, chi dung phan toi thieu de giai thich batch flow va
  source index.
- Lesson 01 va 02 can nghi theo "batch formation".
- Lesson 03 can nghi theo "split batched output".
- Lesson 04 can nghi theo "live input -> live output".
