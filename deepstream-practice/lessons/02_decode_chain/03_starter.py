#!/usr/bin/env python3
"""
Lesson 02 starter: decode chain.

Pipeline muc tieu:
    filesrc -> h264parse -> nvv4l2decoder -> fakesink

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


def on_message(bus, message, loop):
    _ = bus
    # TODO 1: Xu ly `EOS` va `ERROR`.
    # Xem `02_coding_guide.md` muc `on_message(bus, message, loop)`.
    _ = message
    _ = loop
    return True


def make_element(factory_name, name):
    # TODO 2: Tao helper nay bang `Gst.ElementFactory.make(...)`.
    # Xem `02_coding_guide.md` muc `make_element(factory_name, name)`.
    # Sau khi tao element, neu that bai thi raise `RuntimeError`.
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

    pipeline = Gst.Pipeline.new("lesson-02-pipeline")

    # TODO 3: Tao 4 element can thiet.
    # Sau helper `make_element(...)`, ban se goi no 4 lan trong block nay.
    source = None
    parser = None
    decoder = None
    sink = None

    if not pipeline or not source or not parser or not decoder or not sink:
        print("TODO: Tao day du element truoc.", file=sys.stderr)
        return 1

    # TODO 4: Set property:
    # - `source.location`
    # - `sink.sync = False` neu ban muon
    # Sau block tao element, day la noi hop ly de config source/sink.

    # TODO 5: Add element vao pipeline.
    # Goi y: co the loop qua tuple `(source, parser, decoder, sink)`.

    # TODO 6: Link tung buoc:
    # - filesrc -> h264parse
    # - h264parse -> nvv4l2decoder
    # - nvv4l2decoder -> fakesink
    # Xem `02_coding_guide.md` muc `Link tung buoc`.

    # TODO 7: Doc block co san nay trong `02_coding_guide.md`.
    # Ban khong can viet moi, nhung can hieu app se nhan `EOS`/`ERROR` o day.
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running decode chain...")
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
