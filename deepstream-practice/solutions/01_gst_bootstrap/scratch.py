#!/usr/bin/env python3
"""
Lesson 01 - SCRATCH FILE

File nay de test, thu nghiem, debug thoai mai.
Sau khi chay on, chuyen code sach sang solution.py
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

# TODO: Test your code here. Add print debug, comment thoai mai.

Gst.init(None)

def on_message(bus, message, loop):
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("EOS: Pipeline đã đọc hết dữ liệu")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err.message}")
        loop.quit()
    elif message_type == Gst.MessageType.STATE_CHANGED:
        src = message.src
        if src and src.get_name() == "scratch-01-pipeline":
            old_state, new_state, pending = message.parse_state_changed()
            print(f"PIPELINE STATE: {old_state.value_nick} -> {new_state.value_nick} (pending={pending.value_nick})")
            
    return True

def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-any-file>", file=sys.stderr)
        return 0

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 0
    else:
        print(f"Input found: {input_path}")
        print("Creating pipeline...")

    pipeline = Gst.Pipeline.new("scratch-01-pipeline")

    if pipeline:
        print("Pipeline created successfully")
    else:
        print("Pipeline creation failed")
        return 0

    source = Gst.ElementFactory.make("filesrc", "file-source")
    if source:
        print("File source created successfully")
    else:
        print("File source creation failed")
        return 0

    sink = Gst.ElementFactory.make("fakesink", "fake-sink")
    if sink:
        print("Fake sink created successfully")
    else:
        print("Fake sink creation failed")
        return 0

    source.set_property("location", input_path)

    pipeline.add(source)
    pipeline.add(sink)

    if not source.link(sink):
        print("Failed to link source to sink")
        return 0
    else:
        print("Source linked to sink successfully")

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Starting pipeline...")
    pipeline.set_state(Gst.State.PLAYING)
    loop.run()
    pipeline.set_state(Gst.State.NULL)
    print("Pipeline stopped and cleaned up")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
