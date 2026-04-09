#!/usr/bin/env python3
"""
Lesson 02 reference: decode chain.

Pipeline:
    filesrc -> h264parse -> nvv4l2decoder -> fakesink
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


def on_message(bus, message, loop):
    _ = bus
    if message.type == Gst.MessageType.EOS:
        print("EOS: decode xong.")
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True


def make_element(factory_name, name):
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Khong tao duoc element: {factory_name}")
    return element


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
    source = make_element("filesrc", "file-source")
    parser = make_element("h264parse", "h264-parser")
    decoder = make_element("nvv4l2decoder", "hw-decoder")
    sink = make_element("fakesink", "fake-sink")

    source.set_property("location", input_path)
    sink.set_property("sync", False)

    for element in (source, parser, decoder, sink):
        pipeline.add(element)

    if not source.link(parser):
        raise RuntimeError("Khong link duoc filesrc -> h264parse")
    if not parser.link(decoder):
        raise RuntimeError("Khong link duoc h264parse -> nvv4l2decoder")
    if not decoder.link(sink):
        raise RuntimeError("Khong link duoc nvv4l2decoder -> fakesink")

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
