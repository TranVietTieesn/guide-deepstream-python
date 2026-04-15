# Lesson 01: Attach Custom User Meta Upstream

Lesson nay day ban cach gan custom data cua Python vao frame meta tai upstream
probe.

## What You Will Build

- Data path:
  `filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> queue -> queue -> fakesink`
- Input: mot file H.264 elementary stream
- Expected outcome: moi frame di qua `streammux` se duoc attach them
  `NvDsUserMeta` co custom payload

## Why It Matters

Day la buoc khoi dau cua custom metadata trong DeepStream:

- ban khong chi doc metadata co san
- ban tu tao payload rieng cho ung dung cua minh
- payload do di theo buffer trong pipeline, khong can global state

Neu ban hieu buoc nay, ban se hieu duoc:

- attach custom business data vao frame
- bat meta o dung vi tri trong pipeline
- vi sao phai quan tam den copy function va memory ownership ngay tu dau

## Compared to `beginning`

Phan giu nguyen:

- file source
- decode chain
- `nvstreammux`
- bus/main loop
- thinking theo frame/batch meta

Phan moi:

- `NvDsUserMeta`
- `pyds.alloc_custom_struct`
- `pyds.copy_custom_struct`
- `pyds.nvds_add_user_meta_to_frame`
- meta lock/unlock quanh frame list

Lesson `beginning` day ban doc batch meta.
Lesson nay day ban gan payload moi vao batch/frame meta.

## New Concepts In This Lesson

### `NvDsUserMeta`

- Loai meta de attach data tuy y vao frame.
- Duoc luu chung voi metadata DeepStream, khong can global dict.

### Custom struct

- Python data khong the giu nguyen nhu object thuong trong meta path.
- Ban phai cap phat struct bang binding helper va copy du lieu can thiet
  sang do.

### Upstream pad probe

- Probe dat o `nvstreammux.src`.
- Day la cho phu hop de frame da co batch meta hoan chinh, truoc khi di
  xuong sink side.

### Memory ownership

- Khi ban cap phat payload, ban cung phai biet no se duoc release o dau.
- Day la ly do sample co hai probe: mot probe attach, mot probe readback.

## Mental Model

### Data flow

1. Video file vao decoder.
2. `nvstreammux` nhan frame va tao batch meta.
3. Upstream probe chay tren buffer sau mux.
4. Probe cap phat custom struct.
5. Probe attach struct vao `NvDsUserMeta`.
6. Buffer tiep tuc xuong pipeline.

### Control flow

- Meta attach khong phai la "tang them field" vao object Python.
- No la mot vong doi gan buffer.
- Probe can acquire/release meta lock khi duyet frame list.

### Ownership model

- `alloc_custom_struct(...)` tao payload.
- `copy_custom_struct(...)` giup chuyen du lieu vao binding memory.
- `release_custom_struct(...)` se quan trong o lesson sau khi meta di xuong
  downstream.

## Implementation Checklist

1. Tao pipeline file decode -> mux -> queue -> queue -> sink.
2. Set streammux batch-size = 1.
3. Dat probe tai `streammux.src`.
4. Trong probe, lay batch meta va frame meta.
5. Cap phat custom struct cho moi frame.
6. Gan message, structId, sampleInt.
7. Tao user meta va attach vao frame.
8. Tao bus watch va main loop.

## Common Failure Modes

- Quen acquire/release meta lock.
- Gan custom payload nhung khong set `meta_type` dung.
- Doc nham buffer chua co batch meta.
- Quen canh bao ve memory ownership khi copy string.
- Dat probe sai pad nen meta khong bao gio duoc attach.

## Self-Check

- Vi sao probe dat o `streammux.src`?
- `NvDsUserMeta` gan vao frame hay gan vao buffer thuong?
- Tai sao payload phai co helper `alloc_custom_struct(...)`?
- Neu khong release payload thi dieu gi co the xay ra?

## Extensions

- Doi `message` theo frame number.
- Gan them mot field so roi doc lai o lesson sau.
- Thu ghi log frame number va source index neu ban mo rong sang multi-source.
