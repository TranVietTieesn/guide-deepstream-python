# Lesson 02: NvDsAnalytics Rules

Lesson nay dua tracking len mot muc co rules analytics:

- roi
- line crossing
- overcrowding
- direction

## What You Will Build

- Data path:
  `multi-source source bins -> nvstreammux -> nvinfer -> nvtracker -> nvdsanalytics -> nvmultistreamtiler -> nvvideoconvert -> nvdsosd -> sink`
- Input: nhieu URI H.264/H.265
- Output: analytics meta in ra tu object va frame

## Why It Matters

Tracker cho ban identity va continuity.
`nvdsanalytics` cho ban rules va event semantics.

Day la buoc tu "tracking" sang "understanding motion and region behavior":

- object co vao ROI khong
- co cat line khong
- co di dung huong khong
- co crowded khong

## Compared to Lesson 01

Phan giu nguyen:

- detector
- tracker
- multi-source batching
- frame/object metadata

Phan moi:

- `nvdsanalytics`
- config rules file
- object analytics meta
- frame analytics meta

Lesson 01 tra loi "object nay la ai?".
Lesson 02 tra loi "object nay dang lam gi trong khong gian?".

## New Concepts In This Lesson

### ROI / Line Crossing / Direction / Overcrowding

- `nvdsanalytics` suy ra event tu tracker output va config rules.
- Khong phai detector meta, ma la analytics meta xay dung tren tracker state.

### Object analytics meta

- Duoc gan vao object meta list.
- Thuong mang trang thai per-object nhu direction, line crossing, roi status.

### Frame analytics meta

- Duoc gan vao frame user meta list.
- Thich hop cho count theo ROI, cumulative line crossing, overcrowding.

### Analytics config

- Rules file la timetable cua lesson nay.
- Doi config se doi hanh vi analytics, khong can doi code probe.

## Mental Model

### Data flow

1. Detector va tracker tao object identity.
2. `nvdsanalytics` doc object trajectory va positional rules.
3. Plugin attach analytics meta vao object va frame.
4. Probe cuoi pipeline doc va in analytics state.

### Control flow

- Config quyet dinh rules.
- Tracker quality quyet dinh analytics quality.
- Probe chi la noi doc event, khong tao event.

## Implementation Checklist

1. Parse URI list.
2. Tao source bins va streammux.
3. Tao pgie, tracker, nvanalytics, tiler, convert, osd, sink.
4. Doc tracker config.
5. Set analytics config file.
6. Link chain.
7. Dat probe tren nvanalytics src pad.
8. Doc object analytics meta va frame analytics meta.

## Common Failure Modes

- Quen tracker config truoc analytics.
- Khong check dung meta_type cho frame/object analytics meta.
- Doc nham object user meta va frame user meta.
- Rules file khong khop voi stream geometry.
- Quen `live-source` khi source la RTSP.

## Self-Check

- Analytics meta gắn vao object hay frame?
- `nvdsanalytics` dung tracker output cho gi?
- ROI status va line-crossing status khac nhau the nao?
- Tai sao probe dat o analytics src pad?

## Extensions

- Doi rules file va quan sat meta thay doi.
- Thu bat roi status va line crossing trong cung frame.
- Thay doi source count va xem count meta co doi khong.
