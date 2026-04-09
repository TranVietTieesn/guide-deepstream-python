#!/usr/bin/env python3
"""
Lesson 01 starter: GStreamer bootstrap.

Muc tieu: tu lap bo khung toi thieu cua mot app GStreamer.
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
    message_type = message.type

    # TODO 1: Xu ly `EOS`, `ERROR`, `STATE_CHANGED`.
    # Xem `02_coding_guide.md` muc `on_message(bus, message, loop)`.
    # Goi y sau dong `message_type = message.type`:
    # - `EOS`: in log va `loop.quit()`
    # - `ERROR`: `parse_error()`, in debug string neu co, roi `loop.quit()`
    # - `STATE_CHANGED`: chi log khi `message.src` la pipeline chinh
    _ = bus
    _ = message_type
    _ = loop
    return True


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-any-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    # Buoc tiep theo trong walkthrough: khoi tao GStreamer truoc khi tao pipeline.
    Gst.init(None)

    # TODO 2: Tao pipeline va 2 element toi thieu.
    # Xem `02_coding_guide.md` muc `TODO 2`.
    pipeline = Gst.Pipeline.new("lesson-01-pipeline")
    source = None
    sink = None

    if not pipeline or not source or not sink:
        print("TODO: Tao pipeline, filesrc, va fakesink truoc.", file=sys.stderr)
        return 1

    # TODO 3: Set property `location` cho filesrc.
    # Sau khi tao element xong, buoc tiep theo thuong la config source.
    # source.set_property("location", input_path)

    # TODO 4: Add element vao pipeline.
    # Sau `set_property(...)`, hay dua element vao pipeline truoc khi link.
    # pipeline.add(source)
    # pipeline.add(sink)

    # TODO 5: Link `filesrc -> fakesink`.
    # Sau khi add xong, moi thuong link cac element lai voi nhau.

    # TODO 6: Doc block co san nay trong `02_coding_guide.md`.
    # Ban khong can viet moi, nhung can hieu:
    # - `GLib.MainLoop()` tao event loop
    # - `pipeline.get_bus()` lay bus cua pipeline
    # - `bus.connect("message", on_message, loop)` se goi callback cua ban
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Bat dau PLAYING")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Dung boi nguoi dung.")
    finally:
        print("Tra pipeline ve NULL")
        pipeline.set_state(Gst.State.NULL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
