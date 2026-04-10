#!/usr/bin/env python3
"""
Lesson 02 solution: decode chain.

Pipeline muc tieu:
    filesrc -> h264parse -> nvv4l2decoder -> fakesink

Hoan thanh cac TODO tu 03_starter.py
Tham khao 05_reference.py neu can
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


def on_message(bus, message, loop):
    _ = bus
    # TODO 1: Xu ly `EOS` va `ERROR`.
    _ = message
    _ = loop
    return True


def make_element(factory_name, name):
    # TODO 2: Tao helper nay bang `Gst.ElementFactory.make(...)`.
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
    source = None
    parser = None
    decoder = None
    sink = None

    if not pipeline or not source or not parser or not decoder or not sink:
        print("TODO: Tao day du element truoc.", file=sys.stderr)
        return 1

    # TODO 4: Set property cho source va sink

    # TODO 5: Add element vao pipeline.

    # TODO 6: Link tung buoc:
    # - filesrc -> h264parse
    # - h264parse -> nvv4l2decoder
    # - nvv4l2decoder -> fakesink

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
