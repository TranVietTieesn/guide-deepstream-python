#!/usr/bin/env python3
"""
Lesson 03 starter: single-source streammux.

Pipeline muc tieu:
    filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> fakesink

Hay doc theo thu tu:
1. `01_guide.md`
2. `02_coding_guide.md`
3. file nay
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


MUXER_BATCH_TIMEOUT_USEC = 33000


def on_message(bus, message, loop):
    _ = bus
    # TODO 1: Xu ly `EOS` va `ERROR`.
    # Xem `02_coding_guide.md` muc `on_message(bus, message, loop)`.
    _ = message
    _ = loop
    return True


def make_element(factory_name, name):
    # TODO 2: Viet helper tao element va raise `RuntimeError` neu that bai.
    # Xem `02_coding_guide.md` muc `make_element(factory_name, name)`.
    _ = factory_name
    _ = name
    raise NotImplementedError("TODO: implement make_element()")


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("lesson-03-pipeline")

    # TODO 3: Tao day du element.
    # Sau helper `make_element(...)`, ban se tao 5 element trong block nay.
    source = None
    parser = None
    decoder = None
    streammux = None
    sink = None

    if not pipeline or not source or not parser or not decoder or not streammux or not sink:
        print("TODO: Tao day du element truoc.", file=sys.stderr)
        return 1

    # TODO 4: Set property cho source, streammux, va sink.
    # Goi y:
    # - `streammux.batch-size = 1`
    # - `streammux.width = 1920`
    # - `streammux.height = 1080`
    # - `streammux.batched-push-timeout = MUXER_BATCH_TIMEOUT_USEC`
    # - `sink.sync = False`
    # Xem `02_coding_guide.md` muc `Set property`.

    # TODO 5: Add element vao pipeline.
    # Goi y: co the loop qua tuple cac element.

    # TODO 6: Link static chain `filesrc -> h264parse -> nvv4l2decoder`.
    # Phan nay van dung `element.link(...)`.

    # TODO 7: Xin request pad `sink_0` tu `nvstreammux`.
    # Phan nay bat dau chuyen sang pad-level API.
    sinkpad = None

    # TODO 8: Lay `decoder.src` static pad.
    # `get_static_pad("src")` tra ve pad object, khong phai element.
    srcpad = None

    if not sinkpad or not srcpad:
        print("TODO: Lay day du pad truoc khi link vao muxer.", file=sys.stderr)
        return 1

    # TODO 9: Link `decoder.src -> streammux.sink_0`.
    # Goi y: `srcpad.link(sinkpad)` tra ve `Gst.PadLinkReturn`, khong phai bool.
    # TODO 10: Link `nvstreammux -> fakesink`.
    # Sau khi noi xong vao muxer, ban quay lai `element.link(...)` cho doan cuoi.

    # TODO 11: Doc block co san nay trong `02_coding_guide.md`.
    # Ban khong can viet moi, nhung can hieu pipeline bat dau chay tu day.
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running streammux single-source exercise...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
