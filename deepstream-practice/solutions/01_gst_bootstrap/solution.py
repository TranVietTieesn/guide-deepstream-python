#!/usr/bin/env python3
"""
Lesson 01 solution: GStreamer bootstrap.

Hoan thanh cac TODO tu 03_starter.py
Tham khao 05_reference.py neu can
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
    if message_type == Gst.MessageType.EOS:
        print("EOS (End of Stream): Pipeline da doc het du lieu")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err.message}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    elif message_type == Gst.MessageType.STATE_CHANGED:
        src = message.src
        if src and src.get_name() == "lesson-01-pipeline":
            old_state, new_state, pending = message.parse_state_changed()
            print(f"PIPELINE STATE: {old_state.value_nick} -> {new_state.value_nick} (pending={pending.value_nick})")

    return True

def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-any-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)

    #TODO 2: Tao pipeline va 2 element toi thieu.
    pipeline = Gst.Pipeline.new("lesson-01-pipeline")
    if not pipeline:
        print("Khong tao duoc pipeline", file=sys.stderr)
        return 1

    source = Gst.ElementFactory.make("filesrc", "file-src")
    if not source:
        print("Khong tao duoc filesrc", file=sys.stderr)
        return 1

    sink = Gst.ElementFactory.make("fakesink", "fake-sink")
    if not sink:
        print("Khong tao duoc fakesink", file=sys.stderr)
        return 1
    
    print("Tao pipeline, filesrc, va fakesink thanh cong")

    # TODO 3: Set property `location` cho filesrc.
    source.set_property("location", input_path)
    # TODO 4: Add element vao pipeline.
    pipeline.add(source)
    pipeline.add(sink)
    # TODO 5: Link `filesrc -> fakesink`.
    if not source.link(sink):
        print("Khong link duoc filesrc -> fakesink", file=sys.stderr)
        return 1
    else:
        print("Link filesrc -> fakesink thanh cong")

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
