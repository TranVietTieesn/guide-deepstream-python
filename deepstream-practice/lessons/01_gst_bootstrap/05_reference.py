#!/usr/bin/env python3
"""
Lesson 01 reference: GStreamer bootstrap.

Pipeline:
    filesrc -> fakesink
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


def on_message(bus, message, loop):
    _ = bus
    message_type = message.type

    if message_type == Gst.MessageType.EOS:
        print("EOS: pipeline da doc het du lieu.")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    elif message_type == Gst.MessageType.STATE_CHANGED:
        src = message.src
        if src and src.get_name() == "lesson-01-pipeline":
            old_state, new_state, pending = message.parse_state_changed()
            print(
                "PIPELINE STATE:",
                old_state.value_nick,
                "->",
                new_state.value_nick,
                f"(pending={pending.value_nick})",
            )

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

    pipeline = Gst.Pipeline.new("lesson-01-pipeline")
    source = Gst.ElementFactory.make("filesrc", "file-source")
    sink = Gst.ElementFactory.make("fakesink", "fake-sink")
    if not pipeline or not source or not sink:
        print("Khong tao duoc pipeline hoac element.", file=sys.stderr)
        return 1

    source.set_property("location", input_path)
    pipeline.add(source)
    pipeline.add(sink)

    if not source.link(sink):
        print("Khong link duoc filesrc -> fakesink", file=sys.stderr)
        return 1

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
