# Lesson 02: Read and Release Custom User Meta

Lesson nay tiep tuc buoc truoc, nhung tap trung vao downstream side:

- doc custom meta
- xac nhan payload
- release memory dung cach

## What You Will Build

- Data path:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> queue -> queue -> fakesink`
- Input: cung sample file nhu lesson 01
- Expected outcome: custom payload duoc doc o sink-side probe va bo nho
  duoc release an toan

## Why It Matters

Van de lon nhat cua custom meta khong phai attach, ma la lifecycle:

- ai cap phat payload
- ai doc payload
- ai release payload

Lesson nay day ban phan biet "metadata da co trong buffer" voi
"metadata con hop le de dung".

## Compared to Lesson 01

Phan giu nguyen:

- source decode chain
- `nvstreammux`
- custom struct layout
- batch/frame traversal

Phan moi:

- sink-side probe
- `frame_user_meta_list`
- `NvDsUserMeta.cast(...)`
- `release_custom_struct(...)`
- deallocation discipline

Lesson 01 noi ve "attach".
Lesson 02 noi ve "consume and clean up".

## New Concepts In This Lesson

### Downstream pad probe

- Probe dat o sink pad de doc meta sau khi pipeline da chay qua cac stage
  trung gian.
- Day la noi phu hop de validate payload da di duoc den cuoi pipeline.

### `frame_user_meta_list`

- Frame meta co mot danh sach user meta rieng.
- Ban phai duyet danh sach nay de tim custom payload cua minh.

### Release function

- Custom payload khong nen nam lai trong memory sau khi da doc xong.
- `pyds.release_custom_struct(...)` giup thu hoi memory binding.

### Verification mindset

- Lesson nay khong chi "in ra string".
- Ban can biet payload nay co dung field, dung source, dung frame hay khong.

## Mental Model

### Data flow

1. Upstream probe attach payload.
2. Buffer tiep tuc di xuong pipeline.
3. Sink probe doc frame user meta list.
4. Probe cast payload ve custom struct.
5. Probe in field value.
6. Probe release payload neu sample yeu cau.

### Control flow

- Neu khong doc duoc payload, van de co the nam o attach step.
- Neu doc duoc payload nhung release sai, van de la memory ownership.

### Ownership model

- Lesson 01: producer side.
- Lesson 02: consumer side.
- Cac ben phai khop nhau ve format va release contract.

## Implementation Checklist

1. Dung pipeline giong lesson 01.
2. Dat probe o sink pad cua `fakesink`.
3. Duyet `frame_user_meta_list`.
4. Cast `NvDsUserMeta`.
5. Cast custom payload.
6. In field values.
7. Release custom struct dung thu tu.

## Common Failure Modes

- Doc nham `frame_meta_list` thay vi `frame_user_meta_list`.
- Quen check `meta_type`.
- Release payload trong khi con dang su dung.
- Gan custom meta nhung sink probe khong tim ra vi sai pad.
- Khong co meta lock khi duyet list.

## Self-Check

- `frame_user_meta_list` khac gi `frame_meta_list`?
- Khi nao nen release custom struct?
- Vi sao phai check `meta_type` truoc khi cast?
- Lesson nay khac lesson 01 o diem lifecycle nao?

## Extensions

- Ghi ra `structId` va `sampleInt`.
- Thu them field string dai hon.
- Bo release de xem co log canh bao hoac memory leak thuong thay khong.
