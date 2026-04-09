# Lesson Title

## What You Will Build

- Pipeline:
- Input:
- Expected outcome:

## Why It Matters

- Lesson nay nam o dau trong chuoi DeepStream lon hon?
- Sau bai nay, nguoi hoc se tu viet duoc phan nao?

## Mental Model

- Du lieu dang o dang nao truoc plugin chinh?
- Plugin nay bien doi du lieu hay chi dieu phoi?
- Control-plane message nao can theo doi tren bus?

## Implementation Checklist

1. Kiem tra input.
2. `Gst.init(None)`.
3. Tao pipeline va element can thiet.
4. Set property can thiet.
5. `pipeline.add(...)`.
6. Link static pads va request pads neu can.
7. Tao bus watch va `GLib.MainLoop()`.
8. `pipeline.set_state(Gst.State.PLAYING)`.
9. Cleanup bang `Gst.State.NULL`.

## Common Failure Modes

- Input hoac config khong ton tai.
- `Gst.ElementFactory.make(...)` tra ve `None`.
- Link that bai vi dung sai pad, sai caps, hoac thieu parser.
- Bus khong duoc watch nen app khong xu ly `EOS`/`ERROR`.

## Self-Check

- Ban co the tu ve lai pipeline khong?
- Du lieu dang o dang nao truoc/sau plugin chinh?
- Neu bo mot buoc, dieu gi se hong dau tien?

## Extensions

- Extension co ban:
- Extension nang hon nhung van trong boundary:
